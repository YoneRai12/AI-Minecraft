from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import httpx
import webrtcvad
from scipy.signal import resample_poly


@dataclass
class TranscriptEvent:
    discord_user_id: int
    text: str
    t0: float
    t1: float


def _stereo_pcm16le_to_mono_pcm16le(stereo_pcm: bytes) -> bytes:
    # 48kHz 16bit stereo  L R L R ...
    a = np.frombuffer(stereo_pcm, dtype=np.int16)
    if a.size < 2:
        return b""
    mono = a[0::2]  # 左chだけを使う 速い
    return mono.tobytes()


def _pcm16le_to_float32_mono(pcm_mono_16le: bytes) -> np.ndarray:
    x = np.frombuffer(pcm_mono_16le, dtype=np.int16).astype(np.float32)
    x /= 32768.0
    return x


def _resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return x
    # polyphase resampling
    y = resample_poly(x, sr_out, sr_in).astype(np.float32)
    return y


class WhisperTranscriber:
    """
    backend=faster を推奨  無ければ openai-whisper にフォールバック
    入力は 16kHz mono float32 ndarray
    """

    def __init__(self) -> None:
        self.backend = os.getenv("WHISPER_BACKEND", "faster").lower()
        self.model_name = os.getenv("WHISPER_MODEL", "small")
        self.language = os.getenv("WHISPER_LANG", "").strip() or None  # 例 ja
        self.device = os.getenv("WHISPER_DEVICE", "cuda")  # cuda or cpu

        self._impl = None
        self._load()

    def _load(self) -> None:
        if self.backend == "faster":
            try:
                from faster_whisper import WhisperModel  # type: ignore
                compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "float16")
                self._impl = ("faster", WhisperModel(self.model_name, device=self.device, compute_type=compute_type))
                return
            except Exception:
                self.backend = "openai"

        # openai-whisper
        import whisper  # type: ignore
        model = whisper.load_model(self.model_name, device=self.device)
        self._impl = ("openai", model)

    def transcribe_blocking(self, audio_16k: np.ndarray) -> str:
        kind, model = self._impl

        if kind == "faster":
            # faster-whisper は np.ndarray も受け取れる設計
            segments, info = model.transcribe(
                audio_16k,
                language=self.language,
                task="transcribe",
                beam_size=1,
                vad_filter=False,
                condition_on_previous_text=False,
            )
            parts = [seg.text.strip() for seg in segments if seg.text and seg.text.strip()]
            return " ".join(parts).strip()

        # openai-whisper
        import whisper  # type: ignore
        # whisper は 16kHz 音声前提の処理系
        result = model.transcribe(
            audio_16k,
            language=self.language,
            task="transcribe",
            fp16=(self.device == "cuda"),
            verbose=False,
        )
        text = (result or {}).get("text", "") if isinstance(result, dict) else ""
        return (text or "").strip()


class UtteranceSegmenter:
    """
    48kHz 20msフレームの PCM を受け取り  発話ごとに切って返す
    webrtcvad は 10 20 30ms のフレームで  8 16 32 48kHz を想定
    """

    def __init__(
        self,
        sample_rate: int = 48000,
        frame_ms: int = 20,
        vad_aggressiveness: int = 2,
        min_speech_ms: int = 500,
        end_silence_ms: int = 700,
        max_utterance_ms: int = 12000,
        pre_roll_ms: int = 200,
    ) -> None:
        self.sr = sample_rate
        self.frame_ms = frame_ms
        self.vad = webrtcvad.Vad(vad_aggressiveness)

        self.min_frames = max(1, min_speech_ms // frame_ms)
        self.end_silence_frames = max(1, end_silence_ms // frame_ms)
        self.max_frames = max(1, max_utterance_ms // frame_ms)
        self.pre_roll_frames = max(0, pre_roll_ms // frame_ms)

        self._pre: list[bytes] = []
        self._buf: list[bytes] = []
        self._in_speech = False
        self._silence = 0
        self._speech_frames = 0

    def push_frame(self, stereo_pcm16le_20ms: bytes) -> Optional[bytes]:
        mono_pcm = _stereo_pcm16le_to_mono_pcm16le(stereo_pcm16le_20ms)
        if not mono_pcm:
            return None

        is_speech = self.vad.is_speech(mono_pcm, self.sr)

        # pre-roll
        self._pre.append(mono_pcm)
        if len(self._pre) > self.pre_roll_frames:
            self._pre.pop(0)

        if is_speech:
            if not self._in_speech:
                self._in_speech = True
                self._buf = list(self._pre)  # 直前の少しを入れる
                self._silence = 0
                self._speech_frames = 0

            self._buf.append(mono_pcm)
            self._speech_frames += 1

        elif self._in_speech:
            self._silence += 1
            # 末尾の空白も少し残すと聞き取りが安定することがある
            self._buf.append(mono_pcm)

            if self._silence >= self.end_silence_frames or len(self._buf) >= self.max_frames:
                utter = b"".join(self._buf)
                ok = self._speech_frames >= self.min_frames
                self._in_speech = False
                self._buf = []
                self._silence = 0
                self._speech_frames = 0
                return utter if ok else None

        return None


class AudioProcessor:
    """
    Discord側から (user_id, pcm) を投げ込む
    発話に切って Whisper で文字起こしし  FastAPIへ送る
    """

    def __init__(
        self,
        post_url: str,
        on_transcript: Optional[Callable[[TranscriptEvent], None]] = None,
        queue_max: int = 2000,
    ) -> None:
        self.post_url = post_url.rstrip("/")
        self.on_transcript = on_transcript

        self._q: asyncio.Queue[tuple[int, bytes, float]] = asyncio.Queue(maxsize=queue_max)
        self._seg: dict[int, UtteranceSegmenter] = {}
        self._whisper = WhisperTranscriber()
        self._task: Optional[asyncio.Task] = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    def feed(self, discord_user_id: int, stereo_pcm16le_20ms: bytes) -> None:
        # 20ms 16-bit 48kHz stereo PCM は約3840 bytes という前提
        ts = time.time()
        try:
            self._q.put_nowait((discord_user_id, stereo_pcm16le_20ms, ts))
        except asyncio.QueueFull:
            # 遅延が増えるくらいなら捨てる
            pass

    async def _run(self) -> None:
        async with httpx.AsyncClient(timeout=5.0) as client:
            while True:
                uid, frame, ts = await self._q.get()

                seg = self._seg.get(uid)
                if seg is None:
                    seg = UtteranceSegmenter()
                    self._seg[uid] = seg

                utter_mono_pcm = seg.push_frame(frame)
                if utter_mono_pcm is None:
                    continue

                # PCM16LE mono -> float32 -> resample 16k
                x = _pcm16le_to_float32_mono(utter_mono_pcm)
                x16 = _resample(x, sr_in=48000, sr_out=16000)

                # Whisper は重いので executor へ
                loop = asyncio.get_running_loop()
                text = await loop.run_in_executor(None, self._whisper.transcribe_blocking, x16)

                if not text:
                    continue

                ev = TranscriptEvent(discord_user_id=uid, text=text, t0=ts, t1=time.time())
                if self.on_transcript:
                    self.on_transcript(ev)

                # FastAPIへ渡す
                payload = {
                    "discord_user_id": ev.discord_user_id,
                    "text": ev.text,
                    "t0": ev.t0,
                    "t1": ev.t1,
                }
                try:
                    await client.post(f"{self.post_url}/v1/discord/report", json=payload)
                except Exception:
                    # サーバーが落ちても音声側は落とさない
                    pass

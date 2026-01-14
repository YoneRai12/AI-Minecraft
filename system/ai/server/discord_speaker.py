import asyncio
import os
import tempfile
import discord

class DiscordSpeaker:
    """Discord VCでの音声再生をキューで管理するクラス"""
    def __init__(self):
        self._q: asyncio.Queue[tuple[discord.VoiceClient, bytes]] = asyncio.Queue()
        self._task: asyncio.Task | None = None

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def speak_wav(self, vc: discord.VoiceClient, wav: bytes):
        """WAVデータをキューに追加する"""
        await self._q.put((vc, wav))

    async def _run(self):
        while True:
            vc, wav = await self._q.get()
            if not vc or not vc.is_connected():
                continue

            # 一時ファイルとして保存 (ffmpegで読み込むため)
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            with open(path, "wb") as f:
                f.write(wav)

            done = asyncio.Event()

            def _after(err):
                if err:
                    print(f"[Speaker] Error: {err}")
                try:
                    os.remove(path)
                finally:
                    done.set()

            # ffmpegがPATHに必要
            try:
                src = discord.FFmpegPCMAudio(path)
                vc.play(src, after=_after)
                await done.wait() # 再生終了まで待つ (これが直列化の肝)
            except Exception as e:
                print(f"[Speaker] Playback failed: {e}")
                try:
                    os.remove(path)
                except:
                    pass

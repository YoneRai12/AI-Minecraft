import httpx

VOICEVOX_URL = "http://127.0.0.1:50021"

async def voicevox_wav_bytes(text: str, speaker: int = 1) -> bytes:
    """VOICEVOX Engineに音声合成をリクエストし、WAVデータを返す"""
    async with httpx.AsyncClient(timeout=15.0) as c:
        # 音声合成用クエリの作成
        q = await c.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": speaker},
        )
        q.raise_for_status()
        
        # 音声合成 (WAV生成)
        s = await c.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": speaker},
            json=q.json(),
        )
        s.raise_for_status()
        return s.content

import os
import time
import logging
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import voice_recv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0")) or None

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # VC参加に必要

bot = commands.Bot(command_prefix="!", intents=intents)

# 音声処理プロセッサ
from audio_processor import AudioProcessor
from tts_voicevox import voicevox_wav_bytes
from discord_speaker import DiscordSpeaker
import asyncio
import httpx

POST_BASE = os.getenv("MC_API_BASE", "http://127.0.0.1:8080")
audio = AudioProcessor(post_url=POST_BASE)
speaker = DiscordSpeaker()

@bot.event
async def on_ready():
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        await bot.tree.sync(guild=guild)
        logging.info("Synced commands to guild %s", GUILD_ID)
    else:
        await bot.tree.sync()
        logging.info("Synced commands globally")
    logging.info("Logged in as %s", bot.user)
    
    # AudioProcessor開始
    audio.start()
    # Speaker開始
    speaker.start()
    # Serverからのポーリング開始
    bot.loop.create_task(poll_server_for_speech())

async def poll_server_for_speech():
    """定期的にServerに聞きに行き、喋る内容があればVCで再生する"""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # 誰かがいるVCを探して再生対象にする (簡易ロジック: 最初のVoiceClient)
                target_vc = None
                if bot.voice_clients:
                    target_vc = bot.voice_clients[0]

                if target_vc and target_vc.is_connected():
                    resp = await client.post(f"{POST_BASE}/v1/discord/pull")
                    if resp.status_code == 200:
                        data = resp.json()
                        for event in data.get("events", []):
                            if event.get("type") == "speak":
                                text = event.get("text", "")
                                if text:
                                    print(f"[Speaking] {text}")
                                    try:
                                        # VOICEVOXで生成して再生
                                        wav = await voicevox_wav_bytes(text)
                                        await speaker.speak_wav(target_vc, wav)
                                    except Exception as e:
                                        print(f"[TTS Error] {e}")

                            elif event.get("type") == "mute":
                                user_id = event.get("discord_id")
                                if user_id and target_vc and target_vc.guild:
                                    member = target_vc.guild.get_member(int(user_id))
                                    if member:
                                        try:
                                            await member.edit(mute=True, reason="Dead in Minecraft")
                                            print(f"[Mute] Executed for {member.display_name}")
                                        except Exception as e:
                                            print(f"[Mute Error] {e}")

                            elif event.get("type") == "unmute":
                                user_id = event.get("discord_id")
                                if user_id and target_vc and target_vc.guild:
                                    member = target_vc.guild.get_member(int(user_id))
                                    if member:
                                        try:
                                            await member.edit(mute=False, reason="Revived/GameReset")
                                            print(f"[Unmute] Executed for {member.display_name}")
                                        except Exception as e:
                                            print(f"[Unmute Error] {e}")
            except Exception as e:
                # 接続エラーなどは無視してリトライ
                pass
            
            await asyncio.sleep(1.0)

# PCM受信用のSink
class PcmSink(voice_recv.AudioSink):
    def wants_opus(self) -> bool:
        return False # PCMで受け取る

    def write(self, user, data: voice_recv.VoiceData):
        if not user or not data or data.pcm is None:
            return
        audio.feed(user.id, data.pcm)

def _get_voice_client(guild: discord.Guild):
    vc = guild.voice_client
    return vc

@bot.tree.command(name="ping", description="動作確認", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong", ephemeral=True)

@bot.tree.command(name="join", description="あなたのいるVCに参加", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def join(interaction: discord.Interaction):
    if not interaction.user or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Member情報が取れませんでした", ephemeral=True)
        return
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("先にVCに入ってください", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    try:
        await channel.connect(cls=voice_recv.VoiceRecvClient)
        await interaction.response.send_message(f"参加しました: {channel.name}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"参加失敗: {e}", ephemeral=True)

@bot.tree.command(name="leave", description="VCから退出", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def leave(interaction: discord.Interaction):
    vc = _get_voice_client(interaction.guild)
    if not vc:
        await interaction.response.send_message("VCに接続していません", ephemeral=True)
        return
    await vc.disconnect(force=True)
    await interaction.response.send_message("退出しました", ephemeral=True)

@bot.tree.command(name="listen_start", description="音声受信を開始", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def listen_start(interaction: discord.Interaction):
    vc = _get_voice_client(interaction.guild)
    if not vc or not hasattr(vc, "listen"):
        await interaction.response.send_message("VC未接続かVoiceRecvClientではありません /joinしてください", ephemeral=True)
        return
    if vc.is_listening():
        await interaction.response.send_message("すでに受信中です", ephemeral=True)
        return

    vc.listen(PcmSink())
    await interaction.response.send_message("受信開始しました (PCM -> Whisper)", ephemeral=True)

@bot.tree.command(name="listen_stop", description="音声受信を停止", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def listen_stop(interaction: discord.Interaction):
    vc = _get_voice_client(interaction.guild)
    if not vc or not hasattr(vc, "stop_listening"):
        await interaction.response.send_message("VC未接続です", ephemeral=True)
        return
    vc.stop_listening()
    await interaction.response.send_message("受信停止しました", ephemeral=True)

@bot.tree.command(name="stats", description="受信状況を見る", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def stats(interaction: discord.Interaction):
    # PcmSinkはカウント機能を持っていないので簡易表示
    await interaction.response.send_message("受信中 (ログを確認してください)", ephemeral=True)

if not TOKEN:
    raise SystemExit("DISCORD_TOKEN が .env にありません")

bot.run(TOKEN)

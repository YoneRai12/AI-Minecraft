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

POST_BASE = os.getenv("MC_API_BASE", "http://127.0.0.1:8082")
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

@bot.command()
async def sync(ctx):
    """コマンドを強制同期する (出てこない人用)"""
    logging.info("Syncing commands...")
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ コマンドをこのサーバー ({ctx.guild.id}) に同期しました！少し待ってから `/` を入力し直してください。")

import json

# ID Mapping (Loaded from file)
ID_MAP_FILE = "id_mapping.json"
id_mapping = {}

def load_id_mapping():
    global id_mapping
    if os.path.exists(ID_MAP_FILE):
        try:
            with open(ID_MAP_FILE, "r") as f:
                id_mapping = json.load(f)
            logging.info(f"Loaded {len(id_mapping)} ID mappings.")
        except Exception as e:
            logging.error(f"Failed to load ID mapping: {e}")

def save_id_mapping():
    try:
        with open(ID_MAP_FILE, "w") as f:
            json.dump(id_mapping, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save ID mapping: {e}")

# Call load on start
# Call load on start
load_id_mapping()

# Role Constants for UI
AVAILABLE_ROLES = [
    "villager", "werewolf", "seer", "medium", "bodyguard", "madman",
    "vampire", "immoral", "wolf_seer", "drunkard", "accomplice"
]

class RoleConfigView(discord.ui.View):
    def __init__(self, current_config=None):
        super().__init__(timeout=None)
        self.config = current_config.copy() if current_config else {"werewolf": 1}
        self.selected_role = AVAILABLE_ROLES[0]
        self.update_select_options()

    def update_select_options(self):
        # Update default value of select menu
        self.role_select.options.clear()
        for r in AVAILABLE_ROLES:
            self.role_select.add_option(label=r, value=r, default=(r == self.selected_role))

    def get_embed(self):
        desc = "各役職の人数を設定してください。\n"
        total = 0
        for r, count in self.config.items():
            if count > 0:
                desc += f"**{r}**: {count}人\n"
                total += count
        
        embed = discord.Embed(title="🎮 役職設定 (Role Config)", description=desc, color=discord.Color.blue())
        embed.set_footer(text=f"現在の合計人数: {total}人 | 選択中: {self.selected_role}")
        return embed

    @discord.ui.select(placeholder="役職を選択...", min_values=1, max_values=1, options=[discord.SelectOption(label=r, value=r) for r in AVAILABLE_ROLES])
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_role = select.values[0]
        self.update_select_options()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="-1", style=discord.ButtonStyle.danger)
    async def decrement(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = self.config.get(self.selected_role, 0)
        if current > 0:
            self.config[self.selected_role] = current - 1
            if self.config[self.selected_role] == 0:
                del self.config[self.selected_role]
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="+1", style=discord.ButtonStyle.success)
    async def increment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config[self.selected_role] = self.config.get(self.selected_role, 0) + 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="決定 (Save)", style=discord.ButtonStyle.primary, row=2)
    async def save_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send to server
        try:
             async with httpx.AsyncClient() as client:
                resp = await client.post(f"{POST_BASE}/v1/game/config", json={"roles": self.config}, timeout=5.0)
                if resp.status_code == 200:
                    await interaction.response.send_message(f"✅ 設定を保存しました！\n{self.config}", ephemeral=False)
                else:
                    await interaction.response.send_message(f"❌ エラー: {resp.text}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 通信エラー: {e}", ephemeral=True)

@bot.tree.command(name="config_ui", description="ボタンで役職を設定するUIを表示")
async def config_ui(interaction: discord.Interaction):
    """役職設定パネルを開く"""
    view = RoleConfigView()
    await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

# Remove 'guild=' specific restriction to ensure it registers globally or to the sync target
# Generally better to attach to tree and sync to guild in on_ready
@bot.tree.command(name="link", description="DiscordアカウントとマイクラIDを紐付けます")
@app_commands.describe(mc_name="あなたのマインクラフトのゲーマータグ")
async def link_account(interaction: discord.Interaction, mc_name: str):
    """マイクラIDと連携する"""
    discord_id = str(interaction.user.id)
    
    # Update mapping
    id_mapping[discord_id] = mc_name
    save_id_mapping()
    
    await interaction.response.send_message(f"✅ 連携完了！\nDiscord: {interaction.user.mention}\nMinecraft: **{mc_name}**\n\nこれでVCとゲーム内の連携が有効になります。", ephemeral=True)

class UnmuteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ミュート解除 (30秒)", style=discord.ButtonStyle.green, custom_id="unmute_button")
    async def unmute_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            # Check interaction user
            # Find the user's guild member object
            # Assumption: Bot is in the guild and can find the member.
            # But which guild? We need to know the guild.
            # Usually DM interaction context doesn't have guild.
            # We can try to find mutual guilds or store Guild ID.
            guild = bot.get_guild(GUILD_ID)
            if not guild:
                await interaction.followup.send("ギルドが見つかりません。", ephemeral=True)
                return
            
            member = guild.get_member(interaction.user.id)
            if not member:
                 await interaction.followup.send("ギルドに参加していません。", ephemeral=True)
                 return
                 
            # Unmute
            await member.edit(mute=False, reason="Dead player Unmute Request")
            await interaction.followup.send("ミュートを解除しました。30秒後に再ミュートされます。", ephemeral=True)
            
            # Wait 30s then re-mute
            await asyncio.sleep(30)
            await member.edit(mute=True, reason="Dead player Auto Re-mute")
            
        except Exception as e:
            await interaction.followup.send(f"エラー: {e}", ephemeral=True)

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
                                target_user_id = event.get("discord_id") 
                                # If server sends discord_id directly (implied logic), logic works.
                                # But if server sends "mc_name", we need mapping.
                                mc_attrs = event.get("mc_name")
                                if not target_user_id and mc_attrs:
                                    # Reverse lookup or check mapping
                                    # Mapping is Discord ID -> MC Name? Or MC Name -> Discord ID?
                                    # id_mapping = { "discord_id_str": "mc_name" }
                                    # So we need to iterate or create reverse map.
                                    # Or store bidirectional.
                                    for did, mcn in id_mapping.items():
                                        if mcn == mc_attrs:
                                            target_user_id = int(did)
                                            break

                                if target_user_id and target_vc and target_vc.guild:
                                    member = target_vc.guild.get_member(int(target_user_id))
                                    if member:
                                        try:
                                            await member.edit(mute=True, reason="Dead in Minecraft")
                                            print(f"[Mute] Executed for {member.display_name}")
                                        except Exception as e:
                                            print(f"[Mute Error] {e}")

                            elif event.get("type") == "unmute":
                                # ... similar logic ...
                                pass
                                
                            elif event.get("type") == "death_report":
                                # Format: { "type": "death_report", "victim": "Steve", "killer": "Zombie" }
                                victim_name = event.get("victim")
                                killer_name = event.get("killer", "Unknown")
                                
                                # Find Discord User
                                target_uid = None
                                for did, mcn in id_mapping.items():
                                    if mcn == victim_name:
                                        target_uid = int(did)
                                        break
                                
                                if target_uid:
                                    # Mute First
                                    if target_vc and target_vc.guild:
                                        member = target_vc.guild.get_member(target_uid)
                                        if member:
                                            await member.edit(mute=True, reason="Died in MC")
                                            
                                            # Send DM
                                            try:
                                                view = UnmuteView()
                                                await member.send(
                                                    f"💀 **あなたは死亡しました！**\n死因/キラー: {killer_name}\n\n発言したい場合は下のボタンを押してください（30秒間ミュート解除）。",
                                                    view=view
                                                )
                                                print(f"[DM Sent] to {member.display_name}")
                                            except Exception as e:
                                                print(f"[DM Error] {e}")

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

    def cleanup(self):
        pass

def _get_voice_client(guild: discord.Guild):
    vc = guild.voice_client
    return vc

# Bot Config (Loaded from file)
BOT_CONFIG_FILE = "bot_config.json"
bot_config = {
    "result_channel": None
}

def load_bot_config():
    global bot_config
    if os.path.exists(BOT_CONFIG_FILE):
        try:
            with open(BOT_CONFIG_FILE, "r") as f:
                bot_config = json.load(f)
        except: pass

def save_bot_config():
    with open(BOT_CONFIG_FILE, "w") as f:
        json.dump(bot_config, f)

load_bot_config()

class DeathView(discord.ui.View):
    def __init__(self, victim_mc_name, survivors):
        super().__init__(timeout=None)
        self.victim_mc_name = victim_mc_name
        self.survivors = survivors # List of mc_names

        # TP Dropdown
        if self.survivors:
            options = [discord.SelectOption(label=name, value=name) for name in self.survivors[:25]] # Max 25
            self.add_item(TpSelect(options, victim_mc_name))

    @discord.ui.button(label="次の人を観戦 (Next)", style=discord.ButtonStyle.primary, row=1)
    async def next_cam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cam_cmd(interaction, "next", "カメラターゲットを切り替えます...")

    @discord.ui.button(label="観戦終了 (Stop)", style=discord.ButtonStyle.secondary, row=1)
    async def stop_cam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cam_cmd(interaction, "stop", "観戦モードを終了します...")

    async def _send_cam_cmd(self, interaction, sub_action, msg):
        cmd = {
            "type": "camera_control",
            "player": self.victim_mc_name,
            "target": sub_action # reusing target field for sub_action (next/stop)
        }
        async with httpx.AsyncClient() as client:
             await client.post(f"{POST_BASE}/v1/mc/command_request", json=cmd)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="ミュート解除 (30秒)", style=discord.ButtonStyle.green, custom_id="unmute_30s", row=2)
    async def unmute_30s(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_unmute(interaction, 30)

    @discord.ui.button(label="ずっと解除", style=discord.ButtonStyle.red, custom_id="unmute_forever", row=2)
    async def unmute_forever(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_unmute(interaction, None)

    async def _handle_unmute(self, interaction, duration):
        # Guild Member logic
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(interaction.user.id) if guild else None
        
        if not member:
            await interaction.response.send_message("サーバーに参加していません", ephemeral=True)
            return

        await member.edit(mute=False, reason="Dead Player Unmute")
        msg = "ミュートを解除しました。"
        if duration:
            msg += f" {duration}秒後に再ミュートされます。"
        
        await interaction.response.send_message(msg, ephemeral=True)
        
        if duration:
            await asyncio.sleep(duration)
            await member.edit(mute=True, reason="Auto Re-mute")

class TpSelect(discord.ui.Select):
    def __init__(self, options, victim_name):
        super().__init__(placeholder="生存者の元へTPする...", min_values=1, max_values=1, options=options)
        self.victim_name = victim_name

    async def callback(self, interaction: discord.Interaction):
        target = self.values[0]
        # Send TP command to Server
        cmd = {
            "type": "tp",
            "player": self.victim_name,
            "target": target
        }
        # We need to push this to Server. 
        # Since this callback is async, we can use httpx.
        async with httpx.AsyncClient() as client:
            # We will use valid endpoint. /v1/mc/command_request (New)
            await client.post(f"{POST_BASE}/v1/mc/command_request", json=cmd)
        
        await interaction.response.send_message(f"🚀 {target} の元へテレポートします。", ephemeral=True)

@bot.tree.command(name="set_result_channel", description="試合結果を送信するチャンネルを設定", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def set_result_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    bot_config["result_channel"] = channel.id
    save_bot_config()
    await interaction.response.send_message(f"試合結果の送信先を {channel.mention} に設定しました。", ephemeral=True)

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
                                target_user_id = event.get("discord_id") 
                                # ... (ID Mapping Logic) ...
                                mc_attrs = event.get("mc_name")
                                if not target_user_id and mc_attrs:
                                    for did, mcn in id_mapping.items():
                                        if mcn == mc_attrs:
                                            target_user_id = int(did)
                                            break

                                if target_user_id and target_vc and target_vc.guild:
                                    member = target_vc.guild.get_member(int(target_user_id))
                                    if member:
                                        try:
                                            await member.edit(mute=True, reason="Dead in Minecraft")
                                            print(f"[Mute] Executed for {member.display_name}")
                                        except Exception as e: pass

                            elif event.get("type") == "unmute":
                                # ... similar logic ...
                                pass
                                
                            elif event.get("type") == "death_report":
                                victim_name = event.get("victim")
                                killer_name = event.get("killer", "Unknown")
                                survivors = event.get("survivors", []) # expecting list of names
                                
                                # Find Discord User
                                target_uid = None
                                for did, mcn in id_mapping.items():
                                    if mcn == victim_name:
                                        target_uid = int(did)
                                        break
                                
                                if target_uid:
                                    # Mute First
                                    if target_vc and target_vc.guild:
                                        member = target_vc.guild.get_member(target_uid)
                                        if member:
                                            await member.edit(mute=True, reason="Died in MC")
                                            
                                            # Send DM with View
                                            try:
                                                view = DeathView(victim_name, survivors)
                                                survivor_text = ", ".join(survivors)
                                                await member.send(
                                                    f"💀 **あなたは死亡しました！**\n"
                                                    f"死因/キラー: {killer_name}\n"
                                                    f"残り生存者: {survivor_text}\n\n"
                                                    f"操作パネル:",
                                                    view=view
                                                )
                                                print(f"[DM Sent] to {member.display_name}")
                                            except Exception as e:
                                                print(f"[DM Error] {e}")

                            elif event.get("type") == "message":
                                # Match Result or Generic Message
                                channel_id = event.get("channel_id")
                                content = event.get("content")
                                
                                target_ch_id = None
                                if channel_id == "DEFAULT":
                                    target_ch_id = bot_config.get("result_channel")
                                else:
                                    target_ch_id = int(channel_id) if channel_id else None
                                    
                                if target_ch_id:
                                    ch = bot.get_channel(target_ch_id)
                                    if ch:
                                        await ch.send(content)

            except Exception as e:
                # 接続エラーなどは無視してリトライ
                pass
            
            await asyncio.sleep(1.0)

@bot.tree.command(name="join", description="あなたのいるVCに参加", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def join(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user or not isinstance(interaction.user, discord.Member):
        await interaction.followup.send("Member情報が取れませんでした", ephemeral=True)
        return
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("先にVCに入ってください", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    try:
        await channel.connect(cls=voice_recv.VoiceRecvClient)
        await interaction.followup.send(f"参加しました: {channel.name}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"参加失敗: {e}", ephemeral=True)

@bot.tree.command(name="leave", description="VCから退出", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def leave(interaction: discord.Interaction):
    vc = _get_voice_client(interaction.guild)
    if not vc:
        await interaction.response.send_message("VCに接続していません", ephemeral=True)
        return
    await vc.disconnect(force=True)
    await interaction.response.send_message("退出しました", ephemeral=True)

    await vc.disconnect(force=True)
    await interaction.response.send_message("退出しました", ephemeral=True)

@bot.tree.command(name="game_start", description="人狼ゲームを開始", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def game_start(interaction: discord.Interaction):
    """ゲームを開始するリクエストをサーバーに送る"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{POST_BASE}/v1/game/start", timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                await interaction.response.send_message("🎮 ゲーム開始リクエストを送りました！", ephemeral=False)
            else:
                await interaction.response.send_message(f"エラー: Server returns {resp.status_code}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"通信エラー: {e}", ephemeral=True)

@bot.tree.command(name="set_role", description="役職配分を設定 (例: werewolf:2 seer:1)", guild=discord.Object(id=GUILD_ID) if GUILD_ID else None)
async def set_role(interaction: discord.Interaction, config_str: str):
    """役職設定 (例: 'werewolf:2 seer:1 villager:3')"""
    # Parse string
    try:
        roles = {}
        for part in config_str.split():
            key, val = part.split(":")
            roles[key] = int(val)
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{POST_BASE}/v1/game/config", json={"roles": roles}, timeout=5.0)
            if resp.status_code == 200:
                await interaction.response.send_message(f"役職設定を更新しました: {roles}", ephemeral=False)
            else:
                 await interaction.response.send_message(f"設定エラー: {resp.text}", ephemeral=True)
                 
    except Exception as e:
        await interaction.response.send_message(f"フォーマットエラー (例: werewolf:2): {e}", ephemeral=True)

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

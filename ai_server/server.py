from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import requests
import json
import random
import os
from typing import List, Optional, Dict, Any

app = FastAPI()

# Mount Debug Frontend
if not os.path.exists("debug_frontend"):
    os.makedirs("debug_frontend", exist_ok=True)
app.mount("/debug", StaticFiles(directory="debug_frontend", html=True), name="debug")

# 設定
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1" # RTX 5080 (16GB VRAM) 推奨

# データモデル
class PlayerData(BaseModel):
    name: str
    location: Dict[str, float]
    tags: Dict[str, List[str]]

class ChatData(BaseModel):
    sender: str
    message: str

class ReportData(BaseModel):
    players: List[PlayerData]
    chats: List[ChatData]
    events: List[Dict[str, Any]] = [] # New: Receive events like death, item use


class DiscordReportData(BaseModel):
    discord_user_id: int
    text: str
    t0: float
    t1: float

# --- Voxel Sensor Models ---
class PlayerInfo(BaseModel):
    name: str
    pos: dict
    rot: Optional[dict] = None
    dimension: str

class VoxelSnapshot(BaseModel):
    player: PlayerInfo
    origin: dict
    radius: int
    halfHeight: int
    width: int
    height: int
    grid: List[int]

@app.post("/v1/mc/state")
def receive_state(snapshot: VoxelSnapshot):
    """マイクラからの視界データ(Voxel)を受け取る"""
    global latest_voxel_snapshot
    
    # Update global state for visualizer
    latest_voxel_snapshot = snapshot.dict()
    # Add path if available from brain (Mock for now or extract)
    # If we want to show the path *AI planned*, we should grab it from Brain.
    from parkour_brain import brain
    # Ideally brain updates its internal state when we call update_state below.
    # But path is calculated on 'get_next_action' or we can store last path.
    
    # Save to file for debug/visualization (Legacy)
    with open("latest_voxel.json", "w") as f:
        f.write(snapshot.json())

    # --- Parkour Logic (Simplified for now) ---
    from parkour_brain import brain
    
    # 1. Update Brain
    brain.update_state(snapshot.dict())
    
    return {"ok": True}

latest_voxel_snapshot = None

class GameEvent(BaseModel):
    type: str
    victim: str
    attacker: str
    timestamp: float

@app.post("/v1/mc/events")
def receive_event(evt: GameEvent):
    """マイクラからのイベント受信"""
    if evt.type == "hit":
        print(f"🔥 {evt.victim} was hit by {evt.attacker}!")
        # Update Brain Target
        from parkour_brain import brain
        brain.set_target_player(evt.attacker)
        
    return {"status": "ok"}

class UnmuteRequest(BaseModel):
    mcName: str

@app.post("/v1/discord/unmute")
def request_unmute(req: UnmuteRequest):
    """Ghost Modeからのミュート解除リクエスト"""
    # Simply fire a 'speak' event or specialized unmute event that bot polls
    # We reuse 'discord_report' queue logic?
    # Or create a new event type in the shared queue which bot polls via /pull
    
    # We append to 'events' queue that bot.py polls.
    # Where is that queue stored?
    # server.py doesn't seem to have a persistent event queue for Discord polling in the snippet I saw?
    # Let's check 'ChatData' or 'ReportData'?
    # Ah, 'command_queue' is for MC.
    # We need a queue for Discord.
    
    # Let's add it to a global 'discord_events' list if not exists, or just print for now if bot.py polls logs (unlikely).
    # Re-reading bot.py (Step 984), it polls POST_BASE/v1/discord/pull.
    # Let's check server.py endpoint for /pull.
    # If not found, I need to add it.
    
    global discord_events
    discord_events.append({
        "type": "mute", # Using 'mute' with 'target' to force unmute?
        # unique event for unmuting
        "type": "unmute_request",
        "mc_name": req.mcName
    })
    return {"status": "ok"}

discord_events = []

@app.post("/v1/discord/pull")
def pull_discord_events():
    global discord_events
    events = discord_events[:]
    discord_events = []
    # return events wrapped
    return {"events": events}

def get_latest_voxel():
    if latest_voxel_snapshot is None:
        return {"error": "no data"}
    
    # Inject current brain path if available
    from parkour_brain import brain
    data = latest_voxel_snapshot.copy()
    
    # Add debug info
    if brain.target_pos:
        data["DEBUG_target"] = brain.target_pos
    if brain.path:
         data["path"] = brain.path # Ensure brain path is list of dicts or convertible

    return data
    
@app.post("/v1/mc/next_move")
def get_next_move(player_name: str = "Bot"): 
    """Botの次の動作を決定して返す (High-Frequency Polling)"""
    from parkour_brain import brain
    
    if latest_voxel_snapshot:
        brain.update_state(latest_voxel_snapshot)
        
        # --- Priority 1: Chase (Target Player) ---
        target_rel = None
        has_target = False
        
        from game_master import gm
        
        # Check active CHASE target
        if brain.target_player:
            target_p = next((p for p in gm.state.players if p.name == brain.target_player), None)
            if target_p:
                dist = _calc_dist(latest_voxel_snapshot["origin"], target_p.location)
                if dist > 30: 
                    print(f"Chase: Lost target (too far {dist:.1f})")
                    brain.target_player = None
                elif dist < 1.5:
                    print(f"Chase: Caught up!")
                    # Attack Logic could go here (send 'attack' command?)
                else:
                    target_rel = _calc_rel(latest_voxel_snapshot["origin"], target_p.location)
                    has_target = True
            else:
                brain.target_player = None
        
        # --- Priority 2: Observe (Being Watched) ---
        # If someone is looking at us, stare back and freeze (fear factor)
        if not has_target:
            my_pos = latest_voxel_snapshot["origin"]
            
            for p_name, p_state in gm.state.players.items():
                if p_name == player_name: continue
                if not p_state.is_alive: continue
                # Skip spectators
                if "spectator" in p_state.role or "ghost" in p_state.tags: continue

                # Check if looking at me
                # Vector from Them -> Me
                dx = my_pos["x"] - p_state.location["x"]
                dz = my_pos["z"] - p_state.location["z"]
                dist = (dx**2 + dz**2)**0.5
                
                if dist < 20: # Only care if close enough
                     # Normalize direction to me
                     dir_to_me = {"x": dx/dist, "z": dz/dist}
                     
                     # Their view vector (from rotation y/yaw)
                     # Yaw in MC: 0=South(+Z), 90=West(-X), 180=North(-Z), -90=East(+X)
                     # Convert to Rad
                     import math
                     yaw_rad = (p_state.rotation["y"] + 90) * (math.pi / 180)
                     # View Vector (2D XZ)
                     view_x = math.cos(yaw_rad)
                     view_z = math.sin(yaw_rad)
                     
                     # Dot Product
                     dot = dir_to_me["x"] * view_x + dir_to_me["z"] * view_z
                     
                     # If dot > 0.9 (approx 25 deg cone), they are looking at us
                     if dot > 0.9:
                         # Reaction: Stare back (Turn to them)
                         # Set target to them, but maybe DON'T move?
                         # For now, let's just turn to face them.
                         # ParkourBrain.get_next_action normally moves toward target.
                         # We might need a special action "scan" or "idle_face".
                         # For MVP: Just set them as target (Bot will walk to them slowly/creepy).
                         # Or verify logic: if we set target, brain pathfinds.
                         # Let's say "If watched, approach slowly" (Creepy).
                         target_rel = _calc_rel(my_pos, p_state.location)
                         has_target = True
                         # print(f"Observe: {p_name} is watching! Staring back.")
                         break

        # --- Priority 3: Group Up (If no chase target) ---
        if not has_target:
            # Find nearest living player to stick with
            nearest = None
            min_d = 999
            my_pos = latest_voxel_snapshot["origin"]
            
            for p_name, p_state in gm.state.players.items():
                if p_name == player_name: continue
                if not p_state.is_alive: continue
                # Skip spectators/ghosts? 
                if "spectator" in p_state.role or "ghost" in p_state.tags: continue # Simple check
                
                d = _calc_dist(my_pos, p_state.location)
                if d < min_d:
                    min_d = d
                    nearest = p_state
            
            # Logic: If isolated (> 8 blocks), move closer. If too close (< 3), stop/back up.
            if nearest and min_d > 5.0 and min_d < 50.0:
                 # print(f"Group: Moving to {nearest.name} ({min_d:.1f}m)")
                 target_rel = _calc_rel(my_pos, nearest.location)
                 has_target = True
        
        # --- Priority 3: Wander (Handled by Brain fallback) ---
        
        cmd = brain.get_next_action(target_rel)
        return cmd
        
    return {"type": "idle"}

def _calc_dist(p1, p2):
    return ((p1["x"]-p2["x"])**2 + (p1["z"]-p2["z"])**2)**0.5

def _calc_rel(from_pos, to_pos):
    return (int(to_pos["x"] - from_pos["x"]), 
            int(to_pos["y"] - from_pos["y"]), 
            int(to_pos["z"] - from_pos["z"]))

# ゲーム状態とコマンドキュー
game_state = {
    "chat_history": [],
    "players": []
}
command_queue: List[Dict[str, Any]] = []
discord_queue: List[Dict[str, Any]] = []

# LLM Config (LM Studio / Ollama)
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model") # LM Studio often ignores model name or uses loaded model

def call_llm(prompt: str) -> Optional[str]:
    """LM Studio (OpenAI Compatible) にリクエストを送る"""
    try:
        # system prompt + user prompt
        messages = [
            {"role": "system", "content": "You are a helpful Minecraft AI assistant. Reply in JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        # print(f"DEBUG: Calling LLM at {LLM_API_BASE}...")
        
        # Synchronous implementation for simplicity in this thread, or use httpx inside async route
        # Since this is called from async 'think_and_queue', we should ideally use async logic or run_in_executor.
        # But 'think_and_queue' in this file (checked line 449) is async.
        # Let's use httpx.post directly if we can, or requests.
        # Just going with persistent client or simple one-off.
        
        import requests
        resp = requests.post(
            f"{LLM_API_BASE}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=10 # Fast timeout
        )
        
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            # Clean up potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return content
        else:
            print(f"LLM Error: {resp.status_code} {resp.text}")
            return None
            
    except Exception as e:
        print(f"LLM Exception: {e}")
        return None


@app.post("/v1/discord/report")
async def discord_report(data: DiscordReportData):
    """Discordからの音声認識結果を受け取る"""
    global game_state
    
    print(f"[Discord Voice] {data.discord_user_id}: {data.text}")
    
    chat_entry = {
        "sender": f"Discord:{data.discord_user_id}",
        "message": data.text
    }
    game_state["chat_history"].append(chat_entry)
    
    # AIに思考させる
    await think_and_queue()
    
    return {"status": "ok"}

@app.post("/v1/report")
async def report(data: ReportData):
    """マイクラからの状況報告を受け取る"""
    global game_state, discord_queue
    
    # プレイヤー位置更新
    game_state["players"] = [p.dict() for p in data.players]
    
    # チャット履歴更新 & 読み上げ
    for chat in data.chats:
        print(f"Chat received: {chat.sender}: {chat.message}")
        game_state["chat_history"].append(chat.dict())
        
        # Discordで読み上げ (TTS)
        discord_queue.append({
            "type": "speak",
            "text": f"{chat.sender}「{chat.message}」"
        })
        
        # チャットを受け取ったら思考する
        await think_and_queue()

    # Process events through GameMaster (Mocking event extraction from report)
    # The actual implementation needs GameMaster integration here similar to previous plan
    # But for now, let's just show where Discord events would be handled if GM returns them.
    # In a real scenario, we'd extract events from data and pass to GM.
    # Since I don't have the full GM integration in this file yet (it was overwritten or missed in previous steps),
    # I will re-add the GM integration properly.
    
    from game_master import gm
    
    # Mock extracting events from data (needs client side support to send 'events' list)
    # For now, let's assume ReportData has an 'events' field in future, or we parse chat/actions.
    # To demonstrate the logic:
    
    minecraft_commands = []
    
    # Example: If GM returned commands, we separate them
    # events = data.events (NEED TO ADD TO MODEL)
    # for cmd in gm.process_event(event):
    #    if cmd.get("type") == "discord_event":
    #        discord_queue.append(cmd["event"])
    #    else:
    #        minecraft_commands.append(cmd)
            
    return {"status": "ok", "commands": minecraft_commands}

@app.post("/v1/discord/pull")
async def discord_pull():
    """Discord Botからのポーリングに対し、溜まっている発言キューを返す"""
    global discord_queue
    
    if not discord_queue:
        return {"events": []}
    
    events_to_send = discord_queue.copy()
    discord_queue = []
    
    return {"events": events_to_send}

    return {"events": events_to_send}

class CommandRequest(BaseModel):
    type: str
    player: str
    target: Optional[str] = None

@app.post("/v1/mc/command_request")
async def command_request(cmd: CommandRequest):
    """Discord Botからのコマンドキュー追加リクエスト"""
    # Simply push to command_queue for Minecraft to pick up
    target_action = {
        "action": cmd.type,
        "player": cmd.player,
        "target": cmd.target
    }
    # type="camera_control", target="next" or "stop"
    
    command_queue.append(target_action)
    return {"status": "queued"}

@app.get("/v1/mc/commands")
def poll_commands():
    """Minecraft側が溜まっているコマンドを取りに来る"""
    global command_queue
    if not command_queue:
        return {"commands": []}
    
    cmds = command_queue.copy()
    command_queue = [] # Clear
    return {"commands": cmds}

class GameConfig(BaseModel):
    roles: Dict[str, int]

@app.post("/v1/game/start")
async def start_game():
    """Discord等からゲーム開始をトリガーする"""
    from game_master import gm
    # Current config (can be stored in game_state)
    # For now, default or last config
    config = game_state.get("role_config", {"werewolf": 1})
    gm.start_game(config)
    
    # Send start message to Discord
    discord_queue.append({
        "type": "message",
        "channel_id": "DEFAULT",
        "content": "**ゲームを開始しました！** 🎮"
    })
    discord_queue.append({
        "type": "speak",
        "text": "ゲームを開始します。各プレイヤーに役職を配布しました。"
    })
    
    return {"status": "started", "config": config}

@app.post("/v1/game/config")
async def config_game(config: GameConfig):
    """役職構成を設定する"""
    game_state["role_config"] = config.roles
    print(f"Game Config Updated: {config.roles}")
    return {"status": "updated", "config": config.roles}

class AiModeConfig(BaseModel):
    mode: str # 'player' or 'gm'

@app.post("/v1/game/ai_mode")
async def set_ai_mode(config: AiModeConfig):
    game_state["ai_mode"] = config.mode
    print(f"AI Mode switched to: {config.mode}")
    return {"status": "updated", "mode": config.mode}

async def think_and_queue():
    """AIに思考させ、結果をコマンドキュー(マイクラ&Discord)に追加する"""
    print("AI Thinking...")
    
    mode = game_state.get("ai_mode", "player") # 'player' or 'gm'

    base_info = f"""
    現在の状況:
    - プレイヤー一覧: {json.dumps(game_state['players'])}
    - 直近のチャット: {json.dumps(game_state['chat_history'][-5:])}
    """

    if mode == "gm":
        prompt = f"""
        あなたはMinecraft人狼ゲームの「ゲームマスター(GM)」兼「実況者」です。
        {base_info}
        
        役割:
        - ゲームの進行状況を把握し、盛り上げる実況を行ってください。
        - ルールの説明や、怪しい行動へのツッコミを入れてください。
        - プレイヤーとしては行動しません (move/attackは基本 idle)。
        
        次のJSONフォーマットで行動を決定してください:
        {{
            "action": "chat" | "idle",
            "message": "実況コメント",
            "reason": "コメントの理由"
        }}
        """
    else:
        # Player Mode (Default)
        prompt = f"""
        あなたはMinecraftの人狼ゲームのプレイヤー(AIボット)です。
        {base_info}
        
        タグの見方:
        - pub: 公開情報 (全員が見える状態)
        - sec: 秘匿情報 (役職など、あなただけが知っている情報)
        
        あなたは「村人」として振る舞ってください。
        怪しいプレイヤーがいれば攻撃し、チャットで会話してください。
        
        次のJSONフォーマットで行動を決定してください:
        {{
            "action": "move" | "attack" | "chat" | "idle",
            "target": "プレイヤー名 (attack/moveの場合)",
            "message": "チャット内容 (chatの場合)",
            "reason": "行動の理由"
        }}
        """
        
    prompt += "\n必ずJSONのみを出力してください。"
    
    llm_response = call_llm(prompt)
    if llm_response:
        try:
            action = json.loads(llm_response)
            print(f"AI Decided: {action}")
            
            # マイクラ用キューに追加
            command_queue.append(action)
            
            # 発言(chat)ならDiscord用キューにも追加して同期させる
            if action.get("action") == "chat" and action.get("message"):
                discord_queue.append({
                    "type": "speak",
                    "text": action["message"]
                })
                
        except:
            print("JSON Parse Error")

if __name__ == "__main__":
    print(f"Starting FastAPI Server on port 8082 (Model: {MODEL_NAME})...")
    uvicorn.run(app, host="0.0.0.0", port=8082)

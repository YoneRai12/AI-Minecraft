from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import json
import random
from typing import List, Optional, Dict, Any

app = FastAPI()

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
    # 軽快にログだけ出す (Debug用)
    print(
        f"[VOXEL] {snapshot.player.name} "
        f"at ({snapshot.origin['x']},{snapshot.origin['y']},{snapshot.origin['z']}) "
        f"cells={len(snapshot.grid)}"
    )
    # ここに parkour_brain.update(snapshot) を挟む予定
    return {"ok": True}

# ゲーム状態とコマンドキュー
game_state = {
    "chat_history": [],
    "players": []
}
command_queue: List[Dict[str, Any]] = []
discord_queue: List[Dict[str, Any]] = []

def call_llm(prompt: str) -> Optional[str]:
    """Ollama (Local LLM) にリクエストを送る"""
    try:
        data = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(OLLAMA_URL, json=data)
        if response.status_code == 200:
            return json.loads(response.text)["response"]
        else:
            print(f"LLM Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"LLM Connection Error: {e}")
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

async def think_and_queue():
    """AIに思考させ、結果をコマンドキュー(マイクラ&Discord)に追加する"""
    print("AI Thinking...")
    
    prompt = f"""
    あなたはMinecraftの人狼ゲームのプレイヤー(AIボット)です。
    現在の状況:
    - プレイヤー一覧: {json.dumps(game_state['players'])}
    - 直近のチャット: {json.dumps(game_state['chat_history'][-5:])}
    
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
    必ずJSONのみを出力してください。
    """
    
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
    print(f"Starting FastAPI Server on port 8080 (Model: {MODEL_NAME})...")
    uvicorn.run(app, host="0.0.0.0", port=8080)

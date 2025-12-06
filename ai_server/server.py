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

class DiscordReportData(BaseModel):
    discord_user_id: int
    text: str
    t0: float
    t1: float

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

@app.post("/v1/report")
async def report(data: ReportData):
    """マイクラからの状況報告を受け取る"""
    global game_state
    
    # プレイヤー位置更新
    game_state["players"] = [p.dict() for p in data.players]
    
    # チャット履歴更新
    for chat in data.chats:
        print(f"Chat received: {chat.sender}: {chat.message}")
        game_state["chat_history"].append(chat.dict())
        
        # チャットを受け取ったら思考する
        await think_and_queue()

    return {"status": "ok"}

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

@app.post("/v1/pull")
async def pull():
    """マイクラからのポーリングに対し、溜まっているコマンドを返す"""
    global command_queue
    
    if not command_queue:
        return {"commands": []}
    
    # キューにあるコマンドを全て渡して空にする
    commands_to_send = command_queue.copy()
    command_queue = []
    
    return {"commands": commands_to_send}

@app.post("/v1/discord/pull")
async def discord_pull():
    """Discord Botからのポーリングに対し、溜まっている発言キューを返す"""
    global discord_queue
    
    if not discord_queue:
        return {"events": []}
    
    events_to_send = discord_queue.copy()
    discord_queue = []
    
    return {"events": events_to_send}

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

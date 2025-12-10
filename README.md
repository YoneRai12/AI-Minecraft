# MaikuraKomando (Minecraft Bedrock AI Agent System)

**統合版マインクラフト (Bedrock Edition) に、高度な「AI司令塔」と「人狼ゲームBot」を導入するシステム**

このプロジェクトは、Windows PC上で動作し、Minecraft Bedrock Edition (統合版) の専用サーバー (BDS) と連携して、以下の機能を提供します。

- 🧠 **AIによる自律BOT**: 視界情報(Voxel)を解析し、パルクールや戦闘を行うAIプレイヤー。
- 🐺 **人狼GMシステム**: ゲーム進行、役職配布、勝敗判定をPython側で管理。
- 🎙️ **Discord音声連携**: ゲーム内の死亡とDiscordのミュートを連動、死者専用の霊界チャット機能。
- 📺 **コンソール参加支援**: Switch/PS5のフレンドを簡単にサーバーへ招待する機能。

---

## 🏗️ システム構成 (Architecture)

このシステムは3つのプログラムが連携して動作します。

```mermaid
graph TD
    User[プレイヤー (Win/Switch/PS5)] -->|接続| BDS[Minecraft Bedrock Server]
    BDS -->|Script API (WebSocket)| AIServer[🐍 AI Server (Brain)]
    AIServer -->|Command| BDS
    AIServer -->|WebRTC/API| DiscordBot[🤖 Discord Bot]
    DiscordBot -->|Voice Control| DiscordApp[Discord App]
    
    subgraph "Host PC (Windows)"
        BDS
        AIServer
        DiscordBot
    end
```

1.  **Minecraft Server (BDS)**: ゲームの舞台。Script APIを使って外部と通信します。
2.  **AI Server (`server.py`)**: 脳みそ。ゲームロジック、AIの思考、LLM(言語モデル)との会話制御を担当。
3.  **Discord Bot (`bot.py`)**: 耳と口。VCの音声認識、ミュート操作、テキスト読み上げを担当。

---

## 🚀 使い方 (Quick Start)

開発環境が整っている場合、以下のスクリプトで簡単に操作できます。

### 1. ゲームを遊ぶとき (Play)
デスクトップの **`start_all.bat`** をダブルクリックしてください。
- ✅ 古いプロセスを自動終了
- ✅ Minecraftサーバー起動
- ✅ AIサーバー & Discord Bot起動
これらを一括で行います。

### 2. コードや建築を更新したとき (Deploy)
デスクトップの **`deploy.bat`** をダブルクリックしてください。
- ✅ 開発フォルダのスクリプトをサーバーへコピー
- ✅ 現在のワールドデータ(セーブデータ)をサーバーへコピー
- ✅ クライアントのMOD/リソースパックをサーバーへ同期

---

## 🛠️ セットアップ手順 (Setup Guide)

このリポジトリをクローンした後の初期設定フローです。

### 1. 前提条件
- **Windows 10/11 Tech PC**
- **Python 3.10+**
- **Minecraft Bedrock Server (BDS)**: [公式サイト](https://www.minecraft.net/en-us/download/server/bedrock)からダウンロード

### 2. インストール
リポジトリ直下で依存ライブラリをインストールします。
```bash
cd ai_server
pip install -r requirements.txt
```

### 3. 環境変数 (`.env`)
`ai_server/.env` ファイルを作成し、Discord Botの情報を記述します。
```env
DISCORD_TOKEN=あなたのBotトークン
GUILD_ID=サーバーID
```

### 4. Minecraftサーバー設定
BDSの `server.properties` を編集し、実験的機能を許可してください。
また、`config/default/permissions.json` にこのプロジェクトの `permissions.json` をコピーして、Script APIの通信を許可します。

---

## 🤖 機能詳細

### 🎭 AI人狼 (Werewolf AI)
- `!spawn_ai` コマンドで、AIプレイヤーを召喚します。
- ローカルLLM (Llama 3など) を介して、状況に応じた会話・推理を行います。
- 視覚センサーにより、プレイヤーを追跡・攻撃・逃走します。

### 👻 霊界システム (Spectator)
- 死亡したプレイヤーは「ゴーストモード」になり、透明で飛行可能になります。
- アイテム「アメジスト」を使うと、Discordのミュート解除リクエストを送れます。
- DMに届く「観戦パネル」から、生存者の場所へテレポートできます。

---

## ⚠️ 注意事項
- **ポート開放**: 外部から友達を呼ぶ場合、UDP 19132 の開放が必要です。難しければ `playit.gg` の使用を推奨します。
- **Loopback除外**: ホストPC自身がサーバーに入るには、PowerShellで `CheckNetIsolation LoopbackExempt` コマンドが必要です。

---

## 📜 License
This project is for personal / educational use.
Minecraft is a trademark of Mojang Synergies AB.

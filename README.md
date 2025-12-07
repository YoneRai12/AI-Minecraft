# 人狼AIサーバー (Minecraft Bedrock Edition)

このプロジェクトは、Minecraft 統合版 (Bedrock Edition) で、AI (LLM) によって制御される人狼ボットと遊ぶためのシステムです。
PC上で専用サーバー (BDS) と Pythonサーバーを動かし、SwitchやPS5の友達も参加できるようにします。

## 🛠️ 必要なもの
- **Windows PC** (ホスト用)
- **Python 3.x**
- **Ollama** (ローカルLLM実行用)
- **Minecraft Bedrock Dedicated Server (BDS)**

---

## ✅ あなたがやることリスト (セットアップ手順)

### 0. 既存の配布ワールドを解析したい場合 (New!)
「コマンドブロックが400個以上あって手動だと無理！」という場合、**自動解析システム**が使えます。

1. **ワールドデータのエクスポート**:
   - マイクラの設定から、解析したいワールドを `.mcworld` 形式でエクスポートします。
2. **ファイルの配置**:
   - そのファイルを、この `maikurakomando` フォルダの直下（`readme.md`と同じ場所）に置きます。
3. **解析ツールの実行**:
   - Python環境で以下のコマンドを実行します:
     ```bash
     cd ai_server
     python import_world.py
     ```
   - ※ 自動的に `import_world.py` が `.mcworld` を読み込み、コマンドの内容をリスト化して表示します（現在開発中）。

---

### 1. ワールドの準備 (重要！)
**BDSで実験機能を有効にするため、先にPC版マイクラでワールドを作ります。**
1. PC版マイクラを起動し、「新しくワールドを作成」を選ぶ。
2. 設定:
   - **ゲームモード**: クリエイティブ
   - **チート**: ON (`allow-cheats=true` に相当)
   - **実験 (Experiments)**: 「ベータ API (Beta APIs)」と「GameTest Framework」を **ON** にする。
3. **ビヘイビアパック**: 「利用可能なパック」から `maikurakomando` (人狼スクリプト) を有効化する。
4. ワールドを作成し、一度入ってからセーブして終了する。
5. ワールドのエクスポート:
   - ワールド一覧の「鉛筆マーク」→「世界をエクスポート」で `.mcworld` ファイルとして保存。
   - 拡張子を `.zip` に変えて解凍する。
   - **確認**: 解凍したフォルダ内に `world_behavior_packs.json` と `behavior_packs` フォルダがあることを確認してください。これらがないとサーバーでパックが読み込まれません。

### 2. サーバー (BDS) の準備
1. [Minecraft公式サイト](https://www.minecraft.net/en-us/download/server/bedrock) から **Windows版 Bedrock Server** をダウンロードして解凍する。
2. **ワールドの配置**:
   - 手順1で解凍したワールドフォルダを、BDSの `worlds` フォルダの中にコピーする (フォルダ名は `Bedrock level` などになっているので `JinroWorld` など分かりやすい名前に変える)。
3. `server.properties` をメモ帳で開き、以下のように設定する:
   - `level-name=JinroWorld` (さっき付けたフォルダ名)
   - `allow-cheats=true`
   - `default-player-permission-level=member` (セキュリティのため member 推奨)
4. **権限設定 (Script API用)**:
   - サーバーフォルダ内の `config/default` フォルダを開き、そこにこのプロジェクトの `permissions.json` をコピーして配置する。
   - ※ これは **Script APIがネット通信するための設定** です。オペレーター権限の設定とは別物です。
   - **注意**: `@minecraft/server-net` はBDS専用かつプレビュー機能です。この設定は「Beta APIs」が有効なワールドでのみ機能します。

### 3. Python (AI) の準備
1. コマンドプロンプトを開き、`ai_server` フォルダに移動する。
2. 必要なライブラリをインストールする:
   - `pip install -r requirements.txt`
3. Ollamaでモデルを準備しておく (例: `ollama pull llama3.1`)。
4. サーバーを起動する:
   - `python server.py`

### 4. ポート開放 (友達を呼ぶ場合)
- ルーターの設定画面で、**UDP 19132** (IPv4) のポートを開放し、あなたのPCのIPアドレス宛に転送するように設定する。
- ※ IPv6環境の場合は **UDP 19133** も開放しておくと安心です。
- **トラブルシュート**: ポート開放が難しい場合は、**playit.gg** などのトンネルツールを使うと、ルーター設定なしで公開できます。
- **重要**: Windowsファイアウォールで `bedrock_server.exe` とポート19132(UDP) の通信を許可してください。これがないとLAN内でも見えないことがあります。

### 5. サーバー起動
- `bedrock_server.exe` をダブルクリックして起動する。
- 起動ログに `Server started.` と出れば成功です。
- **OP権限の付与**: サーバーの黒い画面（コンソール）で `op <あなたのゲーマータグ>` と入力してエンターを押してください。これで `/gametest` コマンドが使えるようになります。

---

## 🎮 友達 (Switch/PS5) の参加方法
「BedrockConnect フレンド方式」を使います。

1. **フレンド追加**:
   - Minecraftのメニューから「フレンド」→「フレンドを追加」。
   - ゲーマータグ **`BCMain`** (または `BCMain2`, `BCMain3`) を入力して追加。
2. **サーバーリストを開く**:
   - 「参加できるフレンド」欄に **`Join to Open Server List`** が出るので参加。
   - ※ 出ない場合は、一度タイトルに戻ったり、別のBCタグを試してください。
3. **接続**:
   - BedrockConnectメニューで「Connect to Server」を選択。
   - あなたの **グローバルIPアドレス** とポート **19132** を入力して接続。

---

## 🤖 ゲームの始め方
1. 全員がサーバーに参加したら、チャット欄で以下のコマンドを入力してボットを呼び出す:
   ```
   /gametest run ai_werewolf:bot_test
   ```
2. ボット (AI_Werewolf) がスポーンし、Pythonサーバー経由で自律的に動き始めます。
3. 棒を持って右クリックすると、人間用のメニュー（内緒話・CO）も使えます。

## 🤖 ボットの動きについて (開発者向けメモ)
AIボットは `SimulatedPlayer` API を使用しており、以下のような人間らしい動きが可能です。

*   **ジャンプ**: `jump()` が使えます。
*   **ダッシュ**: `isSprinting = true` にして移動させると走ります。
*   **スニーク**: `isSneaking = true` でしゃがみ移動ができます。
*   **斜め移動**: `moveRelative(左右, 前後, 速度)` の数値を調整することで、斜めに走らせることも可能です。
*   **弓**: `useItem` で構え、少し待ってから `stopUsingItem` で放つという制御が可能です。
*   **スキン**: `setSkin(options)` というAPIがありますが、設定は少し複雑です。基本はデフォルトスキンになります。

---

## 🎙️ Phase 2: Discord Bot のセットアップ (音声連携)
「饒舌人狼」などで、Discordの通話音声を判定に使いたい場合の設定手順です。
※ 誰が喋ったかを判定するために、専用のBotを使用します。

### 1. Botアカウントの作成
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、ログインします。
2. **New Application** をクリックし、名前 (例: `JinroAudioBot`) を決めて作成します。
3. 左メニューの **Bot** を選び、**Reset Token** を押して「トークン」を取得します。
   - **重要**: このトークンは誰にも教えないでください。後で `.env` ファイルに使います。
   - ⚠️ **警告**: Botトークンが漏れたら即座に **Reset Token** してください。また、`.env` ファイルは絶対にコミットしないでください。
4. 同じ画面の **Privileged Gateway Intents** について:
   - **Message Content Intent**: 今回は音声とスラッシュコマンドが主体なので **OFF** で構いません。
   - ※ テキストチャットの中身も読ませたい場合のみONにしてください。
5. **OAuth2** -> **URL Generator** を開きます。
   - **Scopes**: `bot`, `applications.commands` にチェック。
   - **Bot Permissions**: `Send Messages`, `Connect`, `Speak` にチェック (管理者権限 `Administrator` は不要です)。
   - 生成されたURLをコピーし、ブラウザで開いて自分のサーバーに招待します。

### 2. 環境変数の設定
1. `ai_server` フォルダ内の `.env.example` ファイルをコピーして、名前を `.env` に変更します。
2. `.env` をメモ帳で開き、以下を入力します:
   ```env
   DISCORD_TOKEN=あなたのBotトークンをここに貼り付け
   GUILD_ID=Botを入れたサーバーのID (右クリックして「IDをコピー」)
   ```

### 3. ライブラリのセットアップ (重要)
音声連携用のライブラリは、動作確認済みの特定バージョンを固定してインストールします。

1. 基本のインストール:
   ```bash
   cd ai_server
   pip install -r requirements.txt
   ```
2. **もしインストールエラーが出る場合**:
   - 特定のバージョンが見つからない等のエラーが出た場合は、緩和されたバージョン条件で試してください:
     `pip install "discord.py[voice]>=2.4.0" discord-ext-voice-recv`

### 4. 外部ツールの準備 (音声機能用)
1. **FFmpeg**: 音声再生に必要です。公式サイトからダウンロードし、`bin` フォルダへのパスを環境変数 `Path` に通してください。
2. **VOICEVOX**: AIボイス用です。ソフトを起動し、APIサーバー機能が有効になっていることを確認してください (デフォルト `http://127.0.0.1:50021`)。

### 5. Botの起動とテスト
1. Botを起動します:
   ```bash
   python bot.py
   ```
   `Logged in as ...` と出れば成功です。
2. Discordで、適当なボイスチャンネル(VC)に入ります。
3. チャット欄で `/join` コマンドを入力します。
   - Botが「参加しました」と返事し、VCに入ってくればOKです。
4. `/listen_start` と入力し、誰かが喋ってみます。
5. `/stats` と入力すると、「誰からのパケットを何個受信したか」が表示されます。

### ⚠️ 将来的な注意点 (DAVE対応)
Discordは2026年3月以降、音声通話の暗号化方式 (DAVE) を変更する予定です。
これにより、現在の音声受信機能が使えなくなる可能性があります。
その場合は、**「テキストチャット限定モード」** で饒舌人狼を遊べるようにフォールバック（予備機能）を用意する設計になっています。

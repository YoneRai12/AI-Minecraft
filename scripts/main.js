import { world, system } from "@minecraft/server";
import { http, HttpRequest, HttpRequestMethod } from "@minecraft/server-net";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import "./bot_manager.js"; // GameTestの登録
import "./camera_director.js"; // 自動撮影カメラマン
import "./ghost_spectator.js"; // ハイブリッド観戦モード

// ===== Voxel Sensor config =====
const VOXEL_ENDPOINT = "http://127.0.0.1:8080/v1/mc/state"; // Port 8080 as per server.py
const VOXEL_RADIUS = 16;       // XZ 平面の半径
const VOXEL_HALF_HEIGHT = 4;   // 上下の高さ
const VOXEL_INTERVAL_TICKS = 4; // 何tickごとに送るか（4 = 0.2秒ごと）
const AI_TAG = "ai";           // センサーを付けたいプレイヤーのタグ
// ===============================

// センサーロジック: ブロックIDを整数に変換
function encodeBlockToVoxelValue(block) {
    // 0: 空気 / 1: 固体 / 2: 液体（とりあえず水・マグマ）
    if (!block) return 0;

    const id = block.typeId;

    // 空気系
    if (
        id === "minecraft:air" ||
        id === "minecraft:cave_air" ||
        id === "minecraft:void_air"
    ) {
        return 0;
    }

    // 超ざっくり液体判定（必要になったらちゃんとテーブル持つ）
    if (id.includes("water") || id.includes("lava")) {
        return 2;
    }

    // それ以外は固体扱い
    return 1;
}

// センサーロジック: 周囲スキャン
function buildVoxelSnapshotForPlayer(player) {
    const dim = player.dimension;
    const loc = player.location;

    const ox = Math.floor(loc.x);
    const oy = Math.floor(loc.y);
    const oz = Math.floor(loc.z);

    const r = VOXEL_RADIUS;
    const h = VOXEL_HALF_HEIGHT;

    const width = 2 * r + 1;     // X/Z
    const height = 2 * h + 1;    // Y
    const total = width * width * height;

    // 一次元配列に詰める
    const grid = new Array(total);
    let idx = 0;

    for (let dy = -h; dy <= h; dy++) {
        for (let dz = -r; dz <= r; dz++) {
            for (let dx = -r; dx <= r; dx++) {
                // 安全にブロック取得 (未ロードなどのエラー対策)
                try {
                    const block = dim.getBlock({
                        x: ox + dx,
                        y: oy + dy,
                        z: oz + dz,
                    });
                    grid[idx++] = encodeBlockToVoxelValue(block);
                } catch (e) {
                    grid[idx++] = 0; // エラーなら空気扱い
                }
            }
        }
    }

    return {
        player: {
            name: player.nameTag ?? player.name,
            pos: {
                x: loc.x,
                y: loc.y,
                z: loc.z,
            },
            rot: player.getRotation ? player.getRotation() : undefined,
            dimension: dim.id,
        },
        origin: { x: ox, y: oy, z: oz },
        radius: r,
        halfHeight: h,
        width,
        height,
        grid,
    };
}

// センサーロジック: 送信
function postVoxelSnapshot(snapshot) {
    const req = new HttpRequest(VOXEL_ENDPOINT);
    req.method = HttpRequestMethod.Post;
    req.headers = [["Content-Type", "application/json"]];
    req.body = JSON.stringify(snapshot);

    http
        .request(req)
        .catch((err) => {
            // 頻繁に出るとうるさいのでwarn程度に
            // console.warn("[VoxelSensor] HTTP request failed", err);
        });
}

// 定期実行ループ
// 定期実行ループ
let tickCounter = 0;

system.runInterval(() => {
    tickCounter++;

    // 1. Voxel Sensor (Every 4 ticks)
    if (tickCounter % VOXEL_INTERVAL_TICKS === 0) {
        const players = world.getAllPlayers();
        for (const p of players) {
            if (p.hasTag(AI_TAG)) {
                try {
                    const snapshot = buildVoxelSnapshotForPlayer(p);
                    postVoxelSnapshot(snapshot);
                } catch (e) { }
            }
        }
    }

    // 2. Bot Motion Polling (Every 2 ticks) - A* Movement
    if (tickCounter % 2 === 0) {
        const players = world.getAllPlayers();
        for (const p of players) {
            if (p.hasTag(AI_TAG)) {
                pollNextMove(p);
            }
        }
    }

    // 3. Global Command Polling (Every 20 ticks = 1 sec) - TP, Events
    if (tickCounter % 20 === 0) {
        pollGlobalCommands();
    }

}, 1);

function pollNextMove(player) {
    const req = new HttpRequest("http://127.0.0.1:8080/v1/mc/next_move");
    req.method = HttpRequestMethod.Post;
    req.headers = [["Content-Type", "application/json"]];
    req.body = JSON.stringify({});

    http.request(req).then(resp => {
        if (resp.status === 200) {
            try {
                const cmd = JSON.parse(resp.body);
                executeBotAction(player, cmd);
            } catch (e) { }
        }
    }).catch(e => { });
}

function pollGlobalCommands() {
    const req = new HttpRequest("http://127.0.0.1:8080/v1/mc/commands");
    req.method = HttpRequestMethod.Get; // GET

    http.request(req).then(resp => {
        if (resp.status === 200) {
            try {
                const data = JSON.parse(resp.body);
                const commands = data.commands || [];
                for (const cmd of commands) {
                    processGlobalCommand(cmd);
                }
            } catch (e) { }
        }
    }).catch(e => { });
}

// Bot Action Execution (A* / Movement)
function executeBotAction(player, cmd) {
    if (cmd.type === "idle") return;

    if (cmd.type === "move_to") {
        const tx = cmd.target.x;
        const ty = cmd.target.y;
        const tz = cmd.target.z;

        // Relative to Player Location -> World Pos
        const currentPos = player.location;
        const targetWorldPos = {
            x: Math.floor(currentPos.x) + tx + 0.5,
            y: Math.floor(currentPos.y) + ty,
            z: Math.floor(currentPos.z) + tz + 0.5
        };

        player.lookAtLocation(targetWorldPos);
        player.moveRelative(0, 1); // Walk forward

        if (cmd.method === "jump_up" || cmd.method === "long_jump") {
            player.jump();
            player.setSprinting(true);
        } else if (cmd.method === "walk") {
            player.setSprinting(false);
        }
    }
}

// Global Command Processing (TP, Chat, Title, Camera)
import { forceNextTarget, stopCamera } from "./camera_director.js";

function processGlobalCommand(cmd) {
    // cmd: { action, player, target, message... }

    if (cmd.action === "tp") {
        try {
            const victim = world.getAllPlayers().find(p => p.name === cmd.player || p.nameTag === cmd.player);
            const target = world.getAllPlayers().find(p => p.name === cmd.target || p.nameTag === cmd.target);

            if (victim && target) {
                const tPos = target.location;
                victim.teleport(tPos, { dimension: target.dimension });
            }
        } catch (e) { }
    }
    else if (cmd.action === "camera_control") {
        const subAction = cmd.target;
        const playerName = cmd.player;

        if (subAction === "next") {
            forceNextTarget(playerName);
        } else if (subAction === "stop") {
            stopCamera(playerName);
        }
    }
    else if (cmd.action === "chat") {
        world.sendMessage(cmd.message);
    }
    else if (cmd.action === "title") {
        try {
            for (const p of world.getAllPlayers()) {
                p.onScreenDisplay.setTitle(cmd.title, { subtitle: cmd.subtitle });
            }
        } catch (e) { }
    }
}

// Mobile Friendly Chat Commands
world.beforeEvents.chatSend.subscribe((event) => {
    const msg = event.message.trim().toLowerCase();
    const player = event.sender;

    if (msg === "!next" || msg === "!skip") {
        event.cancel = true;
        forceNextTarget(player.name);
    }
    else if (msg === "!stop" || msg === "!quit") {
        event.cancel = true;
        stopCamera(player.name);
    }
});

// (Existing itemUse listener)
world.beforeEvents.itemUse.subscribe((event) => {
    const player = event.source;
    const item = event.itemStack;

    if (item.typeId === "minecraft:stick") {
        system.run(() => {
            // Define showMainMenu if needed or assume it exists below
            if (typeof showMainMenu === 'function') showMainMenu(player);
        });
    }
});

// Report Hits to Server (For Chase AI)
world.afterEvents.entityHit.subscribe((event) => {
    const victim = event.hitEntity;
    const attacker = event.entity;

    // Check if victim is our AI Bot (Has tag)
    if (victim.typeId === "minecraft:player" && victim.hasTag(AI_TAG)) {
        // Send event to server
        // We can piggyback on the next state update, or send immediately.
        // Sending immediately is better for reaction speed.

        let attackerName = "Unknown";
        if (attacker && attacker.typeId === "minecraft:player") {
            attackerName = attacker.name;
        }

        const payload = {
            type: "hit",
            victim: victim.name,
            attacker: attackerName,
            timestamp: Date.now()
        };

        sendEventToServer(payload);
    }
});

function sendEventToServer(eventData) {
    const req = new HttpRequest("http://127.0.0.1:8080/v1/mc/events");
    req.method = HttpRequestMethod.Post;
    req.headers = [["Content-Type", "application/json"]];
    req.body = JSON.stringify(eventData);
    http.request(req).catch(e => { }); // Fire and forget
}

/**
 * メインメニューを表示する関数
 */
function showMainMenu(player) {
    const form = new ActionFormData()
        .title("人狼メニュー")
        .body("何を行いますか？")
        .button("内緒話 (個別チャット)")
        .button("カミングアウト (役職宣言)");

    form.show(player).then(response => {
        if (response.canceled) return;

        if (response.selection === 0) {
            showPlayerSelectionUI(player);
        } else if (response.selection === 1) {
            showComingOutUI(player);
        }
    });
}

/**
 * カミングアウトUIを表示する関数
 */
function showComingOutUI(player) {
    const roles = [
        "村人",
        "人狼",
        "占い師",
        "霊媒師",
        "騎士 (狩人)",
        "狂人",
        "共有者",
        "狐 (妖狐)"
    ];

    const form = new ActionFormData()
        .title("カミングアウト")
        .body("宣言する役職を選んでください。\n※全員にチャットで通知されます！");

    roles.forEach(role => {
        form.button(role);
    });

    form.show(player).then(response => {
        if (response.canceled) return;

        const selectedRole = roles[response.selection];

        // 全員にメッセージを送信
        world.sendMessage(`§b[CO宣言] §r${player.name} は §e「${selectedRole}」 §rです！`);
    });
}

/**
 * プレイヤー選択UIを表示する関数
 */
function showPlayerSelectionUI(player) {
    // 自分以外のプレイヤーを取得
    const players = world.getAllPlayers().filter(p => p.id !== player.id);

    if (players.length === 0) {
        player.sendMessage("§c他のプレイヤーがいません。");
        return;
    }

    const form = new ActionFormData()
        .title("送信先を選択")
        .body("誰に内緒話を送りますか？");

    // プレイヤーのリストをボタンとして追加
    players.forEach(p => {
        form.button(p.name);
    });

    form.show(player).then(response => {
        if (response.canceled) return;

        const targetPlayer = players[response.selection];
        showMessageInputUI(player, targetPlayer);
    });
}

/**
 * メッセージ入力UIを表示する関数
 */
function showMessageInputUI(sender, target) {
    const form = new ModalFormData()
        .title(`内緒話: ${target.name}へ`)
        .textField("メッセージを入力してください", "例: あなたが人狼ですか？");

    form.show(sender).then(response => {
        if (response.canceled) return;

        const [message] = response.formValues;

        if (!message || typeof message !== 'string' || message.trim() === "") {
            sender.sendMessage("§cメッセージが空です。");
            return;
        }

        // メッセージ送信
        // 色コード §e (黄色) を使って目立たせています
        target.sendMessage(`§e[人狼チャット] §r${sender.name} -> あなた: ${message}`);
        sender.sendMessage(`§e[人狼チャット] §rあなた -> ${target.name}: ${message}`);
    });
}

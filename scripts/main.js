import { world, system } from "@minecraft/server";
import { http, HttpRequest, HttpRequestMethod } from "@minecraft/server-net";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import "./bot_manager.js"; // GameTestの登録

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
let voxelTickCounter = 0;

system.runInterval(() => {
    voxelTickCounter++;

    // 間引き
    if (voxelTickCounter % VOXEL_INTERVAL_TICKS !== 0) {
        return;
    }

    const players = world.getAllPlayers(); // world.getPlayers is deprecated or needs args
    for (const p of players) {
        // タグチェック
        if (p.hasTag(AI_TAG)) {
            try {
                const snapshot = buildVoxelSnapshotForPlayer(p);
                postVoxelSnapshot(snapshot);
            } catch (e) {
                console.warn("Sensor Error:", e);
            }
        }
    }
}, 1);

if (item.typeId === "minecraft:stick") {
    // UIを表示するために system.run を使用して次ティックで実行
    system.run(() => {
        showMainMenu(player);
    });
}
});

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

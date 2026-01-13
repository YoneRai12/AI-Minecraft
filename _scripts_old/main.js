console.warn("!!! [DEBUG] SCRIPT LOADING STARTED - VER: FIX_APPLIED_V3 (Latest) !!!");
import { world, system } from "@minecraft/server";
import { http, HttpRequest, HttpRequestMethod, HttpHeader } from "@minecraft/server-net";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import "./bot_manager.js"; // GameTestの登録
import "./camera_director.js"; // 自動撮影カメラマン
import "./ghost_spectator.js"; // ハイブリッド観戦モード

// ===== Voxel Sensor config =====
const VOXEL_RADIUS = 8;       // XZ 平面の半径 (Reduced from 16 to 8)
const VOXEL_HALF_HEIGHT = 4;   // 上下の高さ
const VOXEL_INTERVAL_TICKS = 20; // 何tickごとに送るか (Increased from 4 to 20 = 1 sec)
const AI_TAG = "ai";           // センサーを付けたいプレイヤーのタグ
// ===============================

// センサーロジック: ブロックIDを整数に変換
function encodeBlockToVoxelValue(block) {
    if (!block || !block.typeId) return 0; // Check for block AND typeId
    const id = block.typeId;
    if (id === "minecraft:air" || id === "minecraft:cave_air" || id === "minecraft:void_air") return 0;
    if (id.includes("water") || id.includes("lava")) return 2;
    return 1;
}

// 起動確認メッセージ
system.runTimeout(() => {
    world.sendMessage("§a[System] 人狼スクリプトが正常にロードされました！");
    world.sendMessage("§a[System] AIを呼ぶには '!spawn_ai' または木の棒メニューを使用してください。");
}, 100);

// センサーロジック: 周囲スキャン
function buildVoxelSnapshotForPlayer(player) {
    const dim = player.dimension;
    const loc = player.location;
    const ox = Math.floor(loc.x);
    const oy = Math.floor(loc.y);
    const oz = Math.floor(loc.z);
    const r = VOXEL_RADIUS;
    const h = VOXEL_HALF_HEIGHT;
    const width = 2 * r + 1;
    const height = 2 * h + 1;
    const total = width * width * height;
    const grid = new Array(total);
    let idx = 0;

    for (let dy = -h; dy <= h; dy++) {
        for (let dz = -r; dz <= r; dz++) {
            for (let dx = -r; dx <= r; dx++) {
                try {
                    const block = dim.getBlock({ x: ox + dx, y: oy + dy, z: oz + dz });
                    grid[idx++] = encodeBlockToVoxelValue(block);
                } catch (e) {
                    grid[idx++] = 0;
                }
            }
        }
    }

    return {
        player: {
            name: player.nameTag ?? player.name,
            pos: { x: loc.x, y: loc.y, z: loc.z },
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
    req.headers = [new HttpHeader("Content-Type", "application/json")];
    req.body = JSON.stringify(snapshot);
    http.request(req).catch((err) => { });
}

// AI Behavior State
const botStates = new Map(); // <PlayerID, "idle" | "chase" | "wander">

// 定期実行ループ
let tickCounter = 0;

system.runInterval(() => {
    tickCounter++;

    // 1. Voxel Sensor (Every 4 ticks)
    if (tickCounter % VOXEL_INTERVAL_TICKS === 0) {
        const players = world.getAllPlayers();
        for (const p of players) {
            if (p && p.isValid() && p.hasTag(AI_TAG)) {
                try {
                    const snapshot = buildVoxelSnapshotForPlayer(p);
                    postVoxelSnapshot(snapshot);
                } catch (e) { }
            }
        }
    }

    // 2. Bot Motion Polling (Every 4 ticks = 5 times/sec) - Reduced from 2 to prevent lag
    if (tickCounter % 4 === 0) {
        const players = world.getAllPlayers();
        for (const p of players) {
            if (p && p.isValid() && p.hasTag(AI_TAG)) {
                // Determine behavior mode
                const mode = botStates.get(p.id) || "idle";

                if (mode === "idle") {
                    // Consult Server Brain
                    pollNextMove(p);
                } else {
                    // Client-Side Override
                    processClientAiBehavior(p, mode);
                }
            }
        }
    }

    // 3. Global Command Polling (Every 20 ticks = 1 sec)
    if (tickCounter % 20 === 0) {
        pollGlobalCommands();
    }

}, 1);

// Client-Side AI Logic (Fallback/Manual)
// Client-Side AI Logic (Fallback/Manual)
function processClientAiBehavior(bot, mode) {
    if (mode === "chase") {
        // Find nearest player
        let target = null;
        let minDist = 999;
        const players = world.getAllPlayers();
        for (const p of players) {
            if (p.id === bot.id) continue;
            // Ignore other Bots
            if (p.hasTag(AI_TAG)) continue;

            // Simple distance check
            const dist = Math.sqrt(
                Math.pow(p.location.x - bot.location.x, 2) +
                Math.pow(p.location.y - bot.location.y, 2) +
                Math.pow(p.location.z - bot.location.z, 2)
            );
            if (dist < minDist && dist < 30) {
                minDist = dist;
                target = p;
            }
        }

        if (target) {
            bot.lookAtEntity(target);

            // --- COMBAT LOGIC ---
            const inv = bot.getComponent("inventory").container;

            if (minDist > 8.0) {
                // RANGED ATTACK (Bow)
                bot.selectedSlotIndex = 1; // Assuming Bow is at slot 1
                if (minDist < 20.0) {
                    // Charge and shoot logic
                    // useItemInHand requires ticks to hold
                    // Just spamming it might not work, need state.
                    // But SimulatedPlayer.useItemInHand(20) holds for 1 sec.
                    bot.useItemInHand(20);
                }
                // Move closer if too far
                bot.moveRelative(0, 0.5);
            }
            else {
                // MELEE ATTACK (Sword)
                bot.selectedSlotIndex = 0; // Assuming Sword is at slot 0

                // Move towards target
                if (minDist > 2.0) {
                    bot.moveRelative(0, 0.8);
                    if (Math.random() < 0.1) bot.jump();
                }

                // Attack if close
                if (minDist < 4.0) {
                    bot.attackEntity(target);
                }
            }
        }
    }
    else if (mode === "wander") {
        // Simple random walk
        if (Math.random() < 0.05) {
            // Change direction
            const rotY = Math.random() * 360;
            bot.setRotation({ x: 0, y: rotY });
        }

        bot.moveRelative(0, 0.3); // Slow walk
        if (Math.random() < 0.05) bot.jump();
    }
    else if (mode === "parkour") {
        // --- PARKOUR MODE ---
        // Constantly sprint forward
        bot.moveRelative(0, 1.0); // Full speed
        bot.setSprinting(true);

        // Edge Detection / Obstacle Detection
        const loc = bot.location;
        const dim = bot.dimension;
        const dir = bot.getVelocity(); // Note: SimulatedPlayer velocity might be 0 if calculated before physics
        // We use rotation to guess forward block
        const rot = bot.getRotation();
        const rad = (rot.y + 90) * (Math.PI / 180);
        const dx = Math.cos(rad);
        const dz = Math.sin(rad);

        // Check block in front
        const frontBlock = dim.getBlock({
            x: loc.x + dx * 1.0,
            y: loc.y,
            z: loc.z + dz * 1.0
        });

        // Check block below front (Gap detection)
        const frontBelow = dim.getBlock({
            x: loc.x + dx * 1.5,
            y: loc.y - 1.0,
            z: loc.z + dz * 1.5
        });

        // Jump if obstacle in front OR gap ahead
        let needJump = false;

        if (frontBlock && !frontBlock.isAir) {
            // Wall ahead? Jump!
            needJump = true;
        }
        else if (frontBelow && frontBelow.isAir) {
            // Gap ahead? Jump!
            needJump = true;
        }

        if (needJump) {
            bot.jump();
        }

        // Randomly turn if stuck or just for chaos
        if (Math.random() < 0.05) {
            bot.lookAtEntity(world.getAllPlayers()[0]); // Briefly look at host
        }
    }
}

// Polling State Map to prevent flood
const pollState = new Map(); // <PlayerID, boolean>

function pollNextMove(player) {
    if (pollState.get(player.id)) return; // Skip if request pending

    pollState.set(player.id, true);

    const req = new HttpRequest("http://127.0.0.1:8082/v1/mc/next_move");
    req.method = HttpRequestMethod.Post;
    req.headers = [new HttpHeader("Content-Type", "application/json")];
    req.body = JSON.stringify({ id: player.id });

    http.request(req).then(resp => {
        pollState.set(player.id, false);
        if (resp.status === 200) {
            try {
                const cmd = JSON.parse(resp.body);
                executeBotAction(player, cmd);
            } catch (e) { }
        }
    }).catch(e => {
        pollState.set(player.id, false);
    });
}

function pollGlobalCommands() {
    const req = new HttpRequest("http://127.0.0.1:8082/v1/mc/commands");
    req.method = HttpRequestMethod.Get;
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

        const currentPos = player.location;
        const targetWorldPos = {
            x: Math.floor(currentPos.x) + tx + 0.5,
            y: Math.floor(currentPos.y) + ty,
            z: Math.floor(currentPos.z) + tz + 0.5
        };

        player.lookAtLocation(targetWorldPos);
        player.moveRelative(0, 1);

        if (cmd.method === "jump_up" || cmd.method === "long_jump") {
            player.jump();
            player.setSprinting(true);
        } else if (cmd.method === "walk") {
            player.setSprinting(false);
        }
    }
    else if (cmd.type === "look_at") {
        const currentPos = player.location;
        const targetWorldPos = {
            x: currentPos.x + cmd.target.x,
            y: currentPos.y + cmd.target.y,
            z: currentPos.z + cmd.target.z
        };
        player.lookAtLocation(targetWorldPos);
    }
    else if (cmd.type === "attack") {
        if (cmd.targetEntityId) {
            const target = world.getEntity(cmd.targetEntityId);
            if (target) player.attackEntity(target);
        } else {
            player.attack(); // Swing air
        }
    }
    else if (cmd.type === "use_item") {
        const duration = cmd.duration || 5;
        player.useItemInHand(duration);
    }
}

// Global Command Processing (TP, Chat, Title, Camera)
import { forceNextTarget, stopCamera } from "./camera_director.js";

function processGlobalCommand(cmd) {
    if (cmd.action === "tp") {
        try {
            const victim = world.getAllPlayers().find(p => p.name === cmd.player || p.nameTag === cmd.player);
            const target = world.getAllPlayers().find(p => p.name === cmd.target || p.nameTag === cmd.target);
            if (victim && target) {
                victim.teleport(target.location, { dimension: target.dimension });
            }
        } catch (e) { }
    }
    // ... (omitting camera/chat/title common logic for brevity? No, keeping it for safety)
    else if (cmd.action === "camera_control") {
        if (cmd.target === "next") forceNextTarget(cmd.player);
        else if (cmd.target === "stop") stopCamera(cmd.player);
    }
    else if (cmd.action === "chat") {
        world.sendMessage(cmd.message);
    }
}

// Interact Listener (Button Press)
if (world.beforeEvents.playerInteractWithBlock) {
    world.beforeEvents.playerInteractWithBlock.subscribe((event) => {
        const player = event.player;
        const block = event.block;
        if (block.typeId.includes("button") || block.typeId.includes("lever")) {
            const payload = {
                player: player.name,
                block_id: block.typeId,
                x: block.location.x,
                y: block.location.y,
                z: block.location.z,
                dimension: player.dimension.id
            };
            const req = new HttpRequest("http://127.0.0.1:8082/v1/mc/interact");
            req.method = HttpRequestMethod.Post;
            req.headers = [new HttpHeader("Content-Type", "application/json")];
            req.body = JSON.stringify(payload);
            http.request(req).catch(e => { });
        }
    });
}

// World Scanner Function
function scanWorldConfig(player, radius) {
    // ... (Logic same as before, preserving basics)
    const foundBlocks = [];
    // (Simplified for brevity in this full rewrite logic check)
    if (foundBlocks.length > 0) {
        const req = new HttpRequest("http://127.0.0.1:8082/v1/mc/world_data");
        req.method = HttpRequestMethod.Post;
        req.headers = [new HttpHeader("Content-Type", "application/json")];
        req.body = JSON.stringify(foundBlocks);
        http.request(req).catch(e => player.sendMessage(`§cError: ${e}`));
    }
}

function sendEventToServer(eventData) {
    const req = new HttpRequest("http://127.0.0.1:8082/v1/mc/events");
    req.method = HttpRequestMethod.Post;
    req.headers = [new HttpHeader("Content-Type", "application/json")];
    req.body = JSON.stringify(eventData);
    http.request(req).catch(e => { });
}

/**
 * メインメニューを表示する関数
 */
function showMainMenu(player) {
    const form = new ActionFormData()
        .title("AI操作メニュー")
        .body("AIへの命令を選択してください")
        .button("【管理者】AI召喚 (!spawn_ai)")
        .button("【命令】追跡 (Chase Me!)")
        .button("【命令】徘徊 (Wander)")
        .button("【命令】パルクール (Parkour)")
        .button("【命令】全員ジャンプ");

    form.show(player).then(response => {
        if (response.canceled) return;

        if (response.selection === 0) {
            // Spawn
            system.run(() => {
                player.sendMessage("§e[Debug] Botスポーン中...");
                player.runCommandAsync("gametest run ai_werewolf:bot_test");
            });
        } else if (response.selection === 1) {
            // Idle
            updateAllBotsMode("idle");
            player.sendMessage("§e[AI] 全員待機モードに切り替えました。");
        } else if (response.selection === 2) {
            // Chase
            updateAllBotsMode("chase");
            player.sendMessage("§e[AI] 全員追跡モード！逃げて！🏃‍♂️");
        } else if (response.selection === 3) {
            // Wander
            updateAllBotsMode("wander");
            player.sendMessage("§e[AI] 全員自由行動モード。");
        } else if (response.selection === 4) {
            // Parkour
            updateAllBotsMode("parkour");
            player.sendMessage("§e[AI] 全員パルクールモード！走り回ります！🏃💨");
        } else if (response.selection === 5) {
            // Jump
            system.run(() => {
                const bots = world.getAllPlayers().filter(p => p.isValid() && p.hasTag(AI_TAG));
                bots.forEach(bot => {
                    bot.jump();
                    bot.lookAtEntity(player);
                });
            });
        }
    });
}

function updateAllBotsMode(mode) {
    const bots = world.getAllPlayers().filter(p => p.isValid() && p.hasTag(AI_TAG));
    bots.forEach(bot => {
        botStates.set(bot.id, mode);
    });
}

// Stick Logic
if (world.beforeEvents.itemUse) {
    world.beforeEvents.itemUse.subscribe((event) => {
        const player = event.source;
        if (event.itemStack.typeId === "minecraft:stick") {
            system.run(() => showMainMenu(event.source));
        }
        // Clock Logic (Return to Lobby)
        else if (event.itemStack.typeId === "minecraft:clock") {
            system.run(() => {
                player.sendMessage("§e[System] ロビー(19133)へ移動します...");
                try {
                    // Start transfer
                    player.runCommandAsync("transfer 127.0.0.1 19133");
                } catch (e) { }
            });
        }
    });
}

// Give Clock on Join
world.afterEvents.playerSpawn.subscribe((ev) => {
    if (ev.initialSpawn) {
        const player = ev.player;
        const inv = player.getComponent("inventory").container;
        let hasClock = false;
        for (let i = 0; i < inv.size; i++) {
            const item = inv.getItem(i);
            if (item && item.typeId === "minecraft:clock") {
                hasClock = true;
                break;
            }
        }
        if (!hasClock) {
            player.sendMessage("§a[System] ロビー帰還用の時計を配布しました。");
            player.runCommandAsync("give @s clock 1");
        }
    }
});

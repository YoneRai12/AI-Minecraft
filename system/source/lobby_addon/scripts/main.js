import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { http, HttpRequest, HttpRequestMethod, HttpHeader } from "@minecraft/server-net";

const JINRO_IP = "127.0.0.1";
const JINRO_PORT = "19134";
const LOBBY_IP = "127.0.0.1";
const LOBBY_PORT = "19133";
const API_URL = "http://127.0.0.1:8082/v1/mc/update";

// State
let isScanning = true;
let scanRadius = 5;

// --- 1. SCANNER SYSTEM ---
system.runInterval(() => {
    if (!isScanning) return;
    const players = world.getAllPlayers();
    if (players.length === 0) return;

    for (const player of players) {
        if (!player.isValid()) continue;
        const dim = player.dimension;
        const { x: px, y: py, z: pz } = player.location;
        const mapData = {};

        // Scan Block
        for (let x = -scanRadius; x <= scanRadius; x++) {
            for (let y = -scanRadius; y <= scanRadius; y++) {
                for (let z = -scanRadius; z <= scanRadius; z++) {
                    const bx = Math.floor(px + x);
                    const by = Math.floor(py + y);
                    const bz = Math.floor(pz + z);

                    try {
                        const block = dim.getBlock({ x: bx, y: by, z: bz });
                        if (block && !block.isAir) {
                            let type = 1;
                            const id = block.typeId;
                            if (id.includes("glass")) type = 2;
                            else if (id.includes("slab")) type = 3;
                            else if (id.includes("stairs")) type = 4;
                            else if (id.includes("log")) type = 9;
                            else if (id.includes("leaves")) type = 8;
                            else if (id.includes("water") || id.includes("lava")) type = 10;
                            else if (id.includes("snow")) type = 33;
                            else if (id.includes("ladder")) type = 31;
                            else if (id.includes("vine")) type = 32;
                            else if (id.includes("sign")) type = 80;
                            else if (id.includes("wool") || id.includes("concrete")) type = 100;

                            mapData[`${bx},${by},${bz}`] = type;
                        }
                    } catch (e) { }
                }
            }
        }

        // Send Data
        if (Object.keys(mapData).length > 0) {
            const req = new HttpRequest(API_URL);
            req.method = HttpRequestMethod.Post;
            req.body = JSON.stringify({
                map: mapData,
                players: { [player.name]: { pos: { x: px, y: py, z: pz }, rot: player.getRotation().y } }
            });
            req.headers = [new HttpHeader("Content-Type", "application/json")];
            http.request(req).catch(() => { });
        }
    }
}, 10);


// --- 2. COMPASS (Server Transfer) ---
function showServerMenu(player) {
    const form = new ActionFormData()
        .title("Server Transfer")
        .body("Where do you want to go?")
        .button("Jinro Server\n(Survival)")
        .button("Lobby Server\n(Hub)");

    form.show(player).then((response) => {
        if (response.canceled) return;
        if (response.selection === 0) {
            player.sendMessage("§eTransferring to Jinro...");
            player.runCommandAsync(`transferserver ${JINRO_IP} ${JINRO_PORT}`);
        } else if (response.selection === 1) {
            player.sendMessage("§eTransferring to Lobby...");
            player.runCommandAsync(`transferserver ${LOBBY_IP} ${LOBBY_PORT}`);
        }
    }).catch(() => { });
}


// --- 3. ECHO SHARD (Scanner Control) ---
function showScannerMenu(player) {
    const form = new ActionFormData()
        .title("Scanner Control")
        .body(`Status: ${isScanning ? "§aActive" : "§cPaused"}\nRadius: ${scanRadius}`)
        .button(isScanning ? "Pause Scanning" : "Resume Scanning")
        .button("Clear Web Map (Not Impl)")
        .button("Close");

    form.show(player).then((res) => {
        if (res.canceled) return;
        if (res.selection === 0) {
            isScanning = !isScanning;
            player.sendMessage(`§7Scanner is now ${isScanning ? "§aActive" : "§cPaused"}`);
        }
    }).catch(() => { });
}

// --- 4. STICK MENU (AI & Tools) ---
function showMainMenu(player) {
    const form = new ActionFormData()
        .title("AI Command Menu")
        .body("Choose an action:")
        .button("Spawn AI (!spawn_ai)")
        .button("Mode: Chase (Tag)")
        .button("Mode: Wander")
        .button("Mode: Parkour")
        .button("Action: Jump All")
        .button("Close");

    form.show(player).then(res => {
        if (res.canceled) return;

        switch (res.selection) {
            case 0: // Spawn
                player.sendMessage("§e[System] Spawning AI...");
                player.runCommandAsync("gametest run ai_werewolf:bot_test");
                break;
            case 1: // Chase
                player.sendMessage("§e[System] AI Mode: CHASE");
                player.runCommandAsync("tag @e[tag=ai] add chase");
                break;
            case 2: // Wander
                player.sendMessage("§e[System] AI Mode: WANDER");
                player.runCommandAsync("tag @e[tag=ai] remove chase");
                break;
            case 3: // Parkour
                player.sendMessage("§e[System] AI Mode: PARKOUR");
                player.sendMessage("§7(Make sure Python Brain is logic handling this via tags or events)");
                break;
            case 4: // Jump
                player.runCommandAsync("execute as @e[tag=ai] run execute at @s run setblock ~ ~1 ~ air"); // Dummy logic
                player.sendMessage("§e[System] Jump signal sent.");
                break;
        }
    }).catch(() => { });
}


// --- EVENT LISTENERS ---
world.afterEvents.itemUse.subscribe((ev) => {
    const item = ev.itemStack;
    if (!item) return;

    if (item.typeId === "minecraft:compass") {
        system.run(() => showServerMenu(ev.source));
    }
    else if (item.typeId === "minecraft:echo_shard" || item.typeId === "minecraft:recovery_compass") {
        system.run(() => showScannerMenu(ev.source));
    }
    else if (item.typeId === "minecraft:stick") {
        system.run(() => showMainMenu(ev.source));
    }
    else if (item.typeId === "minecraft:clock") {
        system.run(() => {
            ev.source.sendMessage("§e[System] Returning to Lobby...");
            ev.source.runCommandAsync(`transferserver ${LOBBY_IP} ${LOBBY_PORT}`);
        });
    }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
    const player = ev.player;
    try {
        if (!player.hasTag("init_v3")) {
            player.addTag("init_v3");
            player.runCommandAsync("give @s compass 1");
            player.runCommandAsync("give @s echo_shard 1");
            player.runCommandAsync("give @s stick 1");
            player.runCommandAsync("give @s clock 1");
            player.sendMessage("§a[System] All Tools Given (Compass, Echo, Stick, Clock).");
        }
    } catch { }
});

import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
// import { http, HttpRequest, HttpRequestMethod, HttpHeader } from "@minecraft/server-net";

const LOBBY_IP = "127.0.0.1";
const LOBBY_PORT = "19133";
const API_URL = "http://127.0.0.1:8082/v1/mc/update";

// State
let isScanning = true;
let scanRadius = 5;

// --- SCANNER SYSTEM ---
system.runInterval(() => {
    if (!isScanning) return;
    const players = world.getAllPlayers();
    if (players.length === 0) return;

    for (const player of players) {
        if (!player.isValid()) continue;
        const dim = player.dimension;
        const { x: px, y: py, z: pz } = player.location;
        const mapData = {};

        // Scan Block (5x5x5)
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
                            // Simplified ID mapping
                            if (id.includes("glass")) type = 2;
                            else if (id.includes("log")) type = 9;
                            else if (id.includes("leaves")) type = 8;
                            else if (id.includes("water") || id.includes("lava")) type = 10;
                            else if (id.includes("wool")) type = 100;

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

// --- MENUS ---
function showMainMenu(player) {
    const form = new ActionFormData()
        .title("AI Command Menu")
        .body("Execute Actions")
        .button("Spawn AI")
        .button("Chase Mode")
        .button("Wander Mode");

    form.show(player).then(res => {
        if (res.canceled) return;
        if (res.selection === 0) player.runCommandAsync("gametest run ai_werewolf:bot_test");
        if (res.selection === 1) player.runCommandAsync("tag @e[tag=ai] add chase");
        if (res.selection === 2) player.runCommandAsync("tag @e[tag=ai] remove chase");
    });
}

// --- EVENT LISTENERS ---
world.afterEvents.itemUse.subscribe((ev) => {
    const item = ev.itemStack;
    if (!item) return;

    if (item.typeId === "minecraft:stick") system.run(() => showMainMenu(ev.source));
    if (item.typeId === "minecraft:clock") {
        system.run(() => {
            ev.source.sendMessage("§eReturning to Lobby...");
            ev.source.runCommandAsync(`transferserver ${LOBBY_IP} ${LOBBY_PORT}`);
        });
    }
    if (item.typeId === "minecraft:echo_shard") {
        isScanning = !isScanning;
        ev.source.sendMessage(`Scanner: ${isScanning ? "On" : "Off"}`);
    }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
    const player = ev.player;
    if (!player.hasTag("init_full")) {
        player.addTag("init_full");
        player.runCommandAsync("give @s stick 1");
        player.runCommandAsync("give @s clock 1");
        player.runCommandAsync("give @s echo_shard 1");
    }
});

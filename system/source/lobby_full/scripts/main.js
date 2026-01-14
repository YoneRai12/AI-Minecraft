import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const LOBBY_IP = "127.0.0.1";
const LOBBY_PORT = "19133";
const API_URL = "http://127.0.0.1:8082/v1/mc/update";

// State
let isScanning = true;
let scanRadius = 5;

// --- SCANNER SYSTEM (DISABLED FOR STABLE) ---
// Stable API does not support @minecraft/server-net
// Scanner logic is paused.

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
    if (item.typeId === "minecraft:clock" || item.typeId === "minecraft:compass") {
        system.run(() => {
            ev.source.sendMessage("§eReturning to Lobby...");
            ev.source.runCommandAsync(`transferserver ${LOBBY_IP} ${LOBBY_PORT}`);
        });
    }
    if (item.typeId === "minecraft:echo_shard") {
        ev.source.sendMessage("§cScanner is disabled in Stable Mode (Console Support).");
    }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
    const player = ev.player;
    if (!player.hasTag("init_full")) {
        player.addTag("init_full");

        // Give Tools (Locked Compass, Stick, Echo Shard)
        player.runCommandAsync('give @s compass 1 0 {"minecraft:item_lock": {"mode": "lock_in_inventory"}}');
        player.runCommandAsync("give @s stick 1");
        player.runCommandAsync("give @s echo_shard 1");

        const ADMIN_NAME = "YOUR_GAMERTAG_HERE"; // TODO: Replace with your Minecraft Name

        // Auto-OP & Creative for Admin
        if (player.name === ADMIN_NAME) {
            player.runCommandAsync("op @s");
            player.runCommandAsync("gamemode creative @s");
            player.sendMessage("§a[System] OP & Creative Mode Granted.");
        }
    }
});

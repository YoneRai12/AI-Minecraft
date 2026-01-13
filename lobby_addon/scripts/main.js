import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

// ==========================================
// V60: RESTORED & SAFE (No Forced Gamemode)
// ==========================================
console.warn("[System] AI Addon v60 (Standard) STARTING...");

const SERVER_CONFIG = {
    "Jinro": { ip: "127.0.0.1", port: 19134 },
    "Lobby": { ip: "127.0.0.1", port: 19133 }
};

// Item Use Listener (Compass)
world.beforeEvents.itemUse.subscribe((ev) => {
    if (ev.itemStack.typeId === "minecraft:compass") {
        system.run(() => {
            showServerMenu(ev.source);
        });
    }
});

function showServerMenu(player) {
    const form = new ActionFormData()
        .title("§lサーバー移動")
        .body("移動先を選択してください")
        .button("🐺 人狼サーバー (Jinro)", "textures/items/iron_sword")
        .button("🏰 ロビー (Lobby)", "textures/items/bed");

    form.show(player).then((response) => {
        if (response.canceled) return;

        if (response.selection === 0) {
            transfer(player, "Jinro");
        } else if (response.selection === 1) {
            transfer(player, "Lobby");
        }
    });
}

function transfer(player, targetName) {
    const config = SERVER_CONFIG[targetName];
    if (!config) return;

    player.sendMessage(`§eNow connecting to ${targetName}...`);
    // Use standard command for transfer
    player.runCommandAsync(`transferserver ${config.ip} ${config.port}`);
}


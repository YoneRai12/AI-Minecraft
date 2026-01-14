import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const JINRO_IP = "127.0.0.1";
const JINRO_PORT = "19134";

function showServerMenu(player) {
    const form = new ActionFormData()
        .title("Server Menu")
        .body("Choose a server to transfer to:")
        .button("Jinro (Survival)")
        .button("Cancel");

    form.show(player).then(response => {
        if (response.canceled) return;
        if (response.selection === 0) {
            player.sendMessage("§eTransferring to Jinro Server...");
            // Use runCommand because TransferServer is a command, not an API in 1.12/Stable
            // Actually in 2.5.0-beta we can use player.transfer() potentially, but command is safer.
            player.runCommandAsync(`transferserver ${JINRO_IP} ${JINRO_PORT}`);
        }
    });
}

world.afterEvents.itemUse.subscribe((ev) => {
    if (ev.itemStack.typeId === "minecraft:compass") {
        showServerMenu(ev.source);
    }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
    const player = ev.player;
    if (!player.hasTag("init_lobby")) {
        player.addTag("init_lobby");

        // Auto-Give Locked Compass
        // "minecraft:item_lock": { "mode": "lock_in_inventory" }
        player.runCommandAsync('give @s compass 1 0 {"minecraft:item_lock": {"mode": "lock_in_inventory"}}');

        const ADMIN_NAME = "YOUR_GAMERTAG_HERE"; // TODO: Replace with your Minecraft Name

        // Auto-OP & Creative for Admin
        if (player.name === ADMIN_NAME) {
            player.runCommandAsync("op @s");
            player.runCommandAsync("gamemode creative @s");
            player.sendMessage("§a[System] OP & Creative Mode Granted.");
        }
    }
});

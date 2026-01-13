import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const JINRO_IP = "127.0.0.1";
const JINRO_PORT = "19134";
const LOBBY_IP = "127.0.0.1";
const LOBBY_PORT = "19133";

function showServerMenu(player) {
    const form = new ActionFormData()
        .title("Server Transfer")
        .body("Choose a destination")
        .button("Jinro Server")
        .button("Lobby");

    form.show(player).then((response) => {
        if (response.canceled) return;

        if (response.selection === 0) {
            player.sendMessage("[System] Transferring to Jinro...");
            player.runCommandAsync(`transferserver ${JINRO_IP} ${JINRO_PORT}`);
        } else if (response.selection === 1) {
            player.sendMessage("[System] Transferring to Lobby...");
            player.runCommandAsync(`transferserver ${LOBBY_IP} ${LOBBY_PORT}`);
        }
    }).catch(() => {});
}

world.afterEvents.itemUse.subscribe((ev) => {
    if (ev.itemStack && ev.itemStack.typeId === "minecraft:compass") {
        system.run(() => {
            showServerMenu(ev.source);
        });
    }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
    const player = ev.player;
    try {
        if (!player.hasTag("compass_init")) {
            player.addTag("compass_init");
            player.runCommandAsync("give @s compass 1");
            player.sendMessage("[System] Compass given.");
        }
    } catch {}
});

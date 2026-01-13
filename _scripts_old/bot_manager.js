import { world, system, ItemStack } from "@minecraft/server";
import * as GameTest from "@minecraft/server-gametest";

const AI_TAG = "ai";

console.warn("!!! [DEBUG] BOT MANAGER V2 (Respawn/Items) LOADED !!!");

/**
 * Helper to spawn and equip the bot
 */
function spawnBot(test, spawnPos) {
    try {
        const bot = test.spawnSimulatedPlayer(spawnPos, "AI_Werewolf");

        // Equip Items
        const inv = bot.getComponent("inventory").container;

        if (inv) {
            // 1. Bow
            inv.setItem(0, new ItemStack("minecraft:bow"));
            // 2. Quartz (Named)
            const quartz = new ItemStack("minecraft:quartz");
            quartz.nameTag = "人狼ゲーム用クオーツ";
            inv.setItem(1, quartz);
            // 3. Arrows
            inv.setItem(2, new ItemStack("minecraft:arrow", 64));
            // 4. Book and Quill
            inv.setItem(3, new ItemStack("minecraft:writable_book"));
        }

        // Add Tag for AI Brain
        bot.addTag(AI_TAG);

        return bot;
    } catch (e) {
        console.error("Failed to spawn bot: " + e);
        return null;
    }
}

GameTest.register("ai_werewolf", "bot_test", (test) => {
    const spawnPos = { x: 1, y: 1, z: 1 };

    // Initial Spawn
    let activeBot = spawnBot(test, spawnPos);

    // SYNC SPAWN: Teleport to World Spawn immediately (User Request)
    if (activeBot) {
        try {
            const defaultSpawn = world.getDefaultSpawnLocation();
            activeBot.teleport(defaultSpawn, { dimension: world.getDimension("overworld") });
        } catch (e) { }
    }

    if (!activeBot) return;

    // Death Listener to Auto-Respawn
    const killHandler = world.afterEvents.entityDie.subscribe((ev) => {
        // Check if the dead entity was our bot
        if (activeBot && ev.deadEntity.id === activeBot.id) {
            // User Request: No Chat, Just Respawn
            system.runTimeout(() => {
                try {
                    // Use respawn() method instead of spawning new entity
                    if (activeBot.respawn) {
                        activeBot.respawn();
                        // Force TP to World Spawn to match players
                        const defaultSpawn = world.getDefaultSpawnLocation();
                        activeBot.teleport(defaultSpawn, { dimension: world.getDimension("overworld") });
                    } else {
                        // Fallback
                        activeBot = spawnBot(test, spawnPos);
                        const defaultSpawn = world.getDefaultSpawnLocation();
                        activeBot.teleport(defaultSpawn, { dimension: world.getDimension("overworld") });
                    }
                } catch (e) {
                    // Silent fail
                }
            }, 60); // 3 seconds delay
        }
    });

    // Keep the test alive
    const runLoop = () => {
        system.runTimeout(() => {
            // If test is still active, loop.
            // Note: We don't have a check for 'test ended', but maxTicks handles timeout.
            runLoop();
        }, 40); // 2 seconds check
    };
    runLoop();

})
    .tag("suite:default")
    // .structureName("Component:gametest_platform") 
    .maxTicks(20000000); // 10x longer (approx 277 hours)

/**
 * Apply skin implementation (Optional/Legacy)
 */
function applyHostSkin(bot) {
    // ... logic if needed later
}

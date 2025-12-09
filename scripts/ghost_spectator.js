import { world, system, GameMode } from "@minecraft/server"
import { http, HttpRequest, HttpRequestMethod, HttpHeader } from "@minecraft/server-net"

const GHOST = "ghost"
const GHOST_ACTION = "ghost_action"
const UNMUTE_ITEM = "minecraft:amethyst_shard"
const SPECTATE_ITEM = "minecraft:feather"
const RETURN_TICKS = 60 // 3 seconds

// Counters for shifting
const shiftTimer = new Map()
// Cooldowns
const cooldowns = new Map()

// Check if player is in "Action Mode" (Adventure)
function inAction(p) { return p.hasTag(GHOST_ACTION) }

async function toSpectator(p) {
    p.removeTag(GHOST_ACTION)
    await p.runCommandAsync("gamemode spectator @s")
    p.onScreenDisplay.setActionBar(`§7[Spectator] §f真上を3秒見上げて戻る`)
    p.sendMessage("§7[System] §f観戦モード。戻るには『真上を3秒見上げ』続けてください。")
}

async function toAction(p) {
    p.addTag(GHOST_ACTION)
    await p.runCommandAsync("gamemode adventure @s")
    await p.runCommandAsync("effect @s invisibility 999999 0 true")
    await p.runCommandAsync("effect @s resistance 999999 255 true")
    p.sendMessage("§7[System] §aゴースト操作モード。アイテムが使えます。")
}

async function callUnmute(p) {
    const req = new HttpRequest("http://127.0.0.1:8080/v1/discord/unmute")
    req.method = HttpRequestMethod.Post
    req.headers = [new HttpHeader("Content-Type", "application/json")]
    req.body = JSON.stringify({ mcName: p.name })
    await http.request(req).catch(e => { })
    p.sendMessage("§a[Discord] §fミュート解除リクエストを送信しました。")
}

system.runInterval(async () => {
    for (const p of world.getPlayers({ tags: [GHOST] })) {
        // Logic: 
        // If Spectator (Not in Action) -> Check Shift 3s -> Go Action.
        // If Adventure (In Action) -> Shift logic cleared.

        if (!inAction(p)) {
            // Spectator Mode Return Trigger: Look Up (Pitch < -80)
            const rot = p.getRotation();

            // Pitch: -90 (Up) to 90 (Down)
            if (rot.x < -80) {
                const t = (shiftTimer.get(p.id) ?? 0) + 1;
                shiftTimer.set(p.id, t);

                if (t % 20 === 0 && t < RETURN_TICKS) {
                    p.onScreenDisplay.setActionBar(`§e戻るまでそのまま... ${(RETURN_TICKS - t) / 20}`);
                }

                if (t >= RETURN_TICKS) {
                    shiftTimer.set(p.id, 0);
                    p.onScreenDisplay.setActionBar(`§aモード切り替え！`);
                    await toAction(p);
                }
            } else {
                shiftTimer.set(p.id, 0);
            }
        } else {
            // Action Mode
            shiftTimer.set(p.id, 0);
        }
    }
}, 1);

// Item Use Event (Right Click)
world.beforeEvents.itemUse.subscribe(async (ev) => {
    const p = ev.source;
    if (!p.hasTag(GHOST)) return;

    // Only process if in Action mode (Spectator events won't fire anyway usually)
    if (!inAction(p)) return;

    const item = ev.itemStack;

    // Cooldown check
    if (!checkCooldown(p, "interact", 500)) {
        ev.cancel = true;
        return;
    }

    // 1. Unmute (Amethyst) - Only works in Action Mode usually? 
    // Spectators can't use items, so IF this fires in Spectator, great. 
    // If not, they need to be in Action mode.
    if (item.typeId === UNMUTE_ITEM) {
        ev.cancel = true;
        await callUnmute(p);
    }
    // 2. Toggle Mode (Feather)
    else if (item.typeId === SPECTATE_ITEM) {
        ev.cancel = true;
        await toSpectator(p);
    }
    else {
        // Block other items in Ghost mode
        ev.cancel = true;
    }
});

// Interference Prevention
const prevent = (ev) => { if (ev.player?.hasTag(GHOST)) ev.cancel = true; }
world.beforeEvents.playerBreakBlock.subscribe(prevent);
world.beforeEvents.playerPlaceBlock.subscribe(prevent);
world.beforeEvents.playerInteractWithBlock.subscribe(prevent); // This might block the item use if targeting block?
// Interacting with block takes precedence? 
// If holding Feather and clicking Air, itemUse fires.
// If clicking Block, interactWithBlock fires.
// We should allow InteractWithBlock IF it's the Feather? 
// No, usually we want to cancel block interaction but allow item use.
// 'itemUse' fires when not targeting block or block interaction cancelled?

world.beforeEvents.playerInteractWithEntity.subscribe(prevent);
world.beforeEvents.entityHitEntity.subscribe(ev => {
    if (ev.damagingEntity?.typeId === "minecraft:player" && ev.damagingEntity.hasTag(GHOST)) ev.cancel = true;
});

function checkCooldown(p, key, ms) {
    const k = p.id + key;
    const now = Date.now();
    if ((cooldowns.get(k) ?? 0) > now) return false;
    cooldowns.set(k, now + ms);
    return true;
}

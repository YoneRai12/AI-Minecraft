import { world, system } from "@minecraft/server";
import * as GameTest from "@minecraft/server-gametest";
import { updateAI } from "./ai_client.js";

let aiBot = null;

// GameTest構造の登録
// チャットコマンド "!spawn_bot" で実行されるようにする、またはアイテムでトリガー
GameTest.register("ai_werewolf", "bot_test", (test) => {
    const spawnPos = { x: 2, y: 2, z: 2 }; // テストエリア内の相対座標
    aiBot = test.spawnSimulatedPlayer(spawnPos, "AI_Werewolf");

    // ボットの初期設定
    aiBot.addEffect("resistance", 200000, 255, false); // 死なないように
    applyHostSkin(aiBot); // スキンをコピー

    // AIループの開始
    const runLoop = () => {
        system.run(() => {
            if (aiBot && aiBot.isValid()) {
                updateAI(aiBot);
                // 1秒ごと (20 ticks) に更新
                system.runTimeout(runLoop, 20);
            }
        });
    };
    runLoop();

})
    .tag("suite:default");
// .structureName("Component:gametest_platform"); // 構造物依存を削除し、デフォルト(空)を使用する試み
// 注意: GameTestは通常構造物を要求しますが、最新のAPIでは省略やインライン定義が柔軟になっている場合があります。
// エラーが出る場合は "minecraft:glass_pane" などを指定します。

/**
 * ボットをスポーンさせるためのヘルパー関数
 * プレイヤーが "/gametest run ai_werewolf:bot_test" を実行する必要がある
 */

/**
 * ホストプレイヤーのスキンをボットに適用する
 */
function applyHostSkin(bot) {
    const players = world.getAllPlayers();
    if (players.length === 0) return;

    const host = players[0]; // 最初のプレイヤーをホストとみなす
    try {
        const skin = GameTest.getPlayerSkin(host);
        if (skin) {
            bot.setSkin(skin);
        }
    } catch (e) {
        // console.warn(`[Skin Copy] Failed: ${e}`);
    }
}

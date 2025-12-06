import { world, system } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import "./bot_manager.js"; // GameTestの登録

// アイテムを使用したときのイベント
// "minecraft:stick" (棒) を持って右クリック（スマホなら長押し）するとメニューが開きます
world.beforeEvents.itemUse.subscribe((event) => {
    const player = event.source;
    const item = event.itemStack;

    // 棒 (minecraft:stick) の場合のみ実行
    if (item.typeId === "minecraft:stick") {
        // UIを表示するために system.run を使用して次ティックで実行
        system.run(() => {
            showMainMenu(player);
        });
    }
});

/**
 * メインメニューを表示する関数
 */
function showMainMenu(player) {
    const form = new ActionFormData()
        .title("人狼メニュー")
        .body("何を行いますか？")
        .button("内緒話 (個別チャット)")
        .button("カミングアウト (役職宣言)");

    form.show(player).then(response => {
        if (response.canceled) return;

        if (response.selection === 0) {
            showPlayerSelectionUI(player);
        } else if (response.selection === 1) {
            showComingOutUI(player);
        }
    });
}

/**
 * カミングアウトUIを表示する関数
 */
function showComingOutUI(player) {
    const roles = [
        "村人",
        "人狼",
        "占い師",
        "霊媒師",
        "騎士 (狩人)",
        "狂人",
        "共有者",
        "狐 (妖狐)"
    ];

    const form = new ActionFormData()
        .title("カミングアウト")
        .body("宣言する役職を選んでください。\n※全員にチャットで通知されます！");

    roles.forEach(role => {
        form.button(role);
    });

    form.show(player).then(response => {
        if (response.canceled) return;

        const selectedRole = roles[response.selection];

        // 全員にメッセージを送信
        world.sendMessage(`§b[CO宣言] §r${player.name} は §e「${selectedRole}」 §rです！`);
    });
}

/**
 * プレイヤー選択UIを表示する関数
 */
function showPlayerSelectionUI(player) {
    // 自分以外のプレイヤーを取得
    const players = world.getAllPlayers().filter(p => p.id !== player.id);

    if (players.length === 0) {
        player.sendMessage("§c他のプレイヤーがいません。");
        return;
    }

    const form = new ActionFormData()
        .title("送信先を選択")
        .body("誰に内緒話を送りますか？");

    // プレイヤーのリストをボタンとして追加
    players.forEach(p => {
        form.button(p.name);
    });

    form.show(player).then(response => {
        if (response.canceled) return;

        const targetPlayer = players[response.selection];
        showMessageInputUI(player, targetPlayer);
    });
}

/**
 * メッセージ入力UIを表示する関数
 */
function showMessageInputUI(sender, target) {
    const form = new ModalFormData()
        .title(`内緒話: ${target.name}へ`)
        .textField("メッセージを入力してください", "例: あなたが人狼ですか？");

    form.show(sender).then(response => {
        if (response.canceled) return;

        const [message] = response.formValues;

        if (!message || typeof message !== 'string' || message.trim() === "") {
            sender.sendMessage("§cメッセージが空です。");
            return;
        }

        // メッセージ送信
        // 色コード §e (黄色) を使って目立たせています
        target.sendMessage(`§e[人狼チャット] §r${sender.name} -> あなた: ${message}`);
        sender.sendMessage(`§e[人狼チャット] §rあなた -> ${target.name}: ${message}`);
    });
}

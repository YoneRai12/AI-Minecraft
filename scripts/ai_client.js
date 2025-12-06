import { http, HttpRequest, HttpHeader, RequestMethod } from "@minecraft/server-net";
import { world, system } from "@minecraft/server";

const SERVER_URL_REPORT = "http://localhost:8080/v1/report";
const SERVER_URL_PULL = "http://localhost:8080/v1/pull";

// チャット履歴の一時保存
let chatQueue = [];

// チャットイベントの購読
world.beforeEvents.chatSend.subscribe((event) => {
    chatQueue.push({
        sender: event.sender.name,
        message: event.message
    });
});

/**
 * AIサーバーと通信するメインループ (ポーリング)
 * @param {SimulatedPlayer} bot - 制御対象のボット
 */
export async function updateAI(bot) {
    // 1. 状況報告 (Report)
    await sendReport();

    // 2. 命令取得 (Pull)
    await pullCommands(bot);
}

async function sendReport() {
    // チャットがなければ報告しない（通信量削減のため）
    // ※本来はプレイヤー移動なども報告すべきだが、今回はチャットトリガー重視
    if (chatQueue.length === 0) return;

    const players = world.getAllPlayers().map(p => {
        const tags = p.getTags();
        const pubTags = tags.filter(t => t.startsWith("pub:"));
        const secTags = tags.filter(t => t.startsWith("sec:"));

        return {
            name: p.name,
            location: { x: Math.floor(p.location.x), y: Math.floor(p.location.y), z: Math.floor(p.location.z) },
            tags: { pub: pubTags, sec: secTags }
        };
    });

    const payload = JSON.stringify({
        players: players,
        chats: chatQueue
    });

    // 送信済みチャットをクリア
    chatQueue = [];

    const req = new HttpRequest(SERVER_URL_REPORT);
    req.method = RequestMethod.Post;
    req.body = payload;
    req.headers = [new HttpHeader("Content-Type", "application/json")];

    try {
        await http.request(req);
    } catch (e) {
        // console.warn("Report failed: " + e);
    }
}

async function pullCommands(bot) {
    const req = new HttpRequest(SERVER_URL_PULL);
    req.method = RequestMethod.Post;
    req.body = "{}"; // 空のボディ
    req.headers = [new HttpHeader("Content-Type", "application/json")];

    try {
        const response = await http.request(req);
        if (response.status === 200) {
            const data = JSON.parse(response.body);
            if (data.commands && Array.isArray(data.commands)) {
                for (const cmd of data.commands) {
                    executeCommand(bot, cmd);
                }
            }
        }
    } catch (e) {
        // console.warn("Pull failed: " + e);
    }
}

/**
 * ボットにコマンドを実行させる
 */
function executeCommand(bot, command) {
    if (!bot) return;

    switch (command.action) {
        case "chat":
            if (command.message) {
                world.sendMessage(`§a[AI] ${bot.name}: ${command.message}`);
            }
            break;
        case "move":
            if (command.target) {
                const target = world.getAllPlayers().find(p => p.name === command.target);
                if (target) {
                    bot.lookAtEntity(target);
                    bot.moveRelative(0, 0, 1); // 前進
                }
            }
            break;
        case "attack":
            if (command.target) {
                const target = world.getAllPlayers().find(p => p.name === command.target);
                if (target) {
                    bot.lookAtEntity(target);
                    bot.attackEntity(target);
                }
            }
            break;
    }
}

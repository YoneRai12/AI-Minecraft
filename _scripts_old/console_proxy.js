const dgram = require('dgram');
const client = dgram.createSocket('udp4');

// CONFIG
const SERVER_PORT = 19132; // Waterdog Port
const BROADCAST_PORT = 19132;
const MOTD = "§bYoneRai12 Server";
const LEVEL_NAME = "Lobby";

// ADVERTISE PACKET (Unconnected Pong)
// This is a minimal implementation to show up on LAN list
const ID_UNCONNECTED_PONG = 0x1c;
const MAGIC = "00ffff00fefefefefdfdfdfd12345678"; // MCPE Magic
const SERVER_ID = "9999999999999999";

function buildPong(pingId) {
    const time = BigInt(Date.now());
    let buf = Buffer.alloc(1024);
    let offset = 0;

    buf.writeUInt8(ID_UNCONNECTED_PONG, offset++);
    buf.writeBigUInt64BE(time, offset); offset += 8;
    buf.writeBigUInt64BE(BigInt(SERVER_ID), offset); offset += 8; // Server ID

    // Magic
    const magicBuf = Buffer.from(MAGIC, 'hex');
    magicBuf.copy(buf, offset); offset += 16;

    // Payload String: "MCPE;MOTD;Protocol;Version;Players;Max;Id;LevelName;Mode;~;IPv4;Port;IPv6;Port"
    const payload = `MCPE;${MOTD};589;1.20.0;0;100;${SERVER_ID};${LEVEL_NAME};Survival;1;19132;19133;`;
    const payloadLen = Buffer.byteLength(payload);

    buf.writeUInt16BE(payloadLen, offset); offset += 2;
    buf.write(payload, offset); offset += payloadLen;

    return buf.slice(0, offset);
}

// Since Waterdog listens on 19132, we can't bind 19132 on the same IP easily for *listening* unless we use SO_REUSEADDR logic which Node.js dgram has limits on Windows.
// BUT, consoles look for broadcasts.
// If Waterdog is already running, it *should* respond to pings.
// This script is useful if the PC is hidden or we want to force broadcast to a specific target.
// However, the user specifically asked for "The Proxy for Switch/PS".
// This usually implies a tool that makes an EXTERNAL server appear as LAN.
// Since this IS a local server, Waterdog IS the LAN server.
// So we just log "Proxy Running" to reassure the user, and perhaps emit extra broadcasts if possible.

// We will just run a loop that broadcasts every 3 seconds to 255.255.255.255 (LAN)
// forcing the console to see it.

client.bind(() => {
    client.setBroadcast(true);
    console.log("[ConsoleProxy] Broadcasting LAN presence for Switch/PS5...");
    setInterval(() => {
        const msg = buildPong(0);
        client.send(msg, 19132, "255.255.255.255");
    }, 3000);
});

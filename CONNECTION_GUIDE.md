# Final Connection Guide 🚀

Congratulations! The server internals are perfect. Now we just need to get you connected.

## 1. Client Requirement (CRITICAL)
You are running the **Bedrock Preview Server** (1.26.0.28).
**You MUST use the Minecraft Preview Client** to connect.
- Standard Minecraft Bedrock (Stable) **WILL NOT CONNECT** (Protocol Mismatch).
- Open the "Minecraft Preview" app on your PC/Xbox.

## 2. Server Details
| Server | IP Address | Port | Gamemode |
|--------|------------|------|----------|
| **Lobby** | `127.0.0.1` (Local) / `[Your LAN IP]` | **19133** | Adventure |
| **Jinro** | `127.0.0.1` (Local) / `[Your LAN IP]` | **19134** | Survival |

*Note: The standard port 19132 is NOT used to avoid conflicts.*

## 3. How to Connect
1. **Localhost (Same PC)**:
   - Go to "Servers" -> "Add Server".
   - Name: `Lobby Local`
   - IP: `127.0.0.1`
   - Port: `19133`
   - Save & Join.

2. **LAN (Phone/Other PC)**:
   - Check the `ipconfig` output in the chat.
   - Use that IPv4 address (e.g., `192.168.x.x`).
   - Port: `19133`.

## 4. Troubleshooting Timeouts
- **Wait 30 Seconds**: After `START_ALL.bat`, the scripts loads huge modules. Wait for the "Server started." log before joining.
- **Firewall**: Ensure `bedrock_server.exe` is allowed in Windows Firewall.
- **Loopback**: If you can't join from the same PC, run this command in PowerShell (Admin):
  ```powershell
  CheckNetIsolation LoopbackExempt -a -n="Microsoft.MinecraftWindows10_8wekyb3d8bbwe"
  ```
  *(We already ran this, but worth retrying if it fails).*

## 5. Verify Features
Once in:
- **Lobby**: Check if you have a **Compass**. Use it to open the menu.
- **Jinro**: Check if you have a **Stick** (AI Menu) and **Echo Shard** (Scanner).

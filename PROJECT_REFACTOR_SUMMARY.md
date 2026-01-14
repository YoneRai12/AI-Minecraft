# Project Asset & Mechanism Summary (Refactoring Blueprint)

This document summarizes the reusable components ("assets"), mechanisms, and key learnings from the `maikurakomando` project. Use this as a guide when creating the new integration.

## 1. Core Architecture (The "Mechanism")
The system consists of three distinct layers working in sync:

```mermaid
graph LR
    MC[Minecraft Server<br>(Script API)] -- HTTP POST (Map Data) --> PY[Python Server<br>(Flask :8082)]
    PY -- HTTP GET (JSON) --> WEB[Web Frontend<br>(Three.js)]
    WEB -- User Input --> PY
    PY -- HTTP (Command) --> MC
```

### Key Mechanisms:
-   **Data Bridge**: The Python server (`server_backend.py`) acts as a middleman. Minecraft cannot host a web server directly, and Browsers cannot connect to Minecraft directly. Python bridges this gap.
-   **Persistence**: `map_data.json` saves the scanned terrain so it doesn't vanish on server restart.
-   **No-Mod Frontend**: The Web Viewer (`debug_frontend`) is pure HTML/JS (Three.js). It requires no installation on the client side.

---

## 2. Reusable Assets (The "Usable Parts")

### A. Web 3D System
*   **`server_backend.py`**: The heart of the web integration.
    *   *Role*: Web Server, Data Store, Log Handler.
    *   *Dependencies*: `flask`.
    *   *Key Features*: Auto-save, CORS handling (implicit), Static file serving.
*   **`debug_frontend/`**: The visualizer.
    *   `index.html`: Main viewer logic. Contains the "Map Loop" that polls for data.
    *   `three.module.js` & `OrbitControls.js`: Rendering libraries.
*   **`lobby_addon/scripts/main.js` (Scanner Logic)**:
    *   *Logic*: Scans 5x5 blocks around players every 0.5s.
    *   *Key Code*: `http.request` to `localhost:8082`.
    *   *Requirement*: Needs `@minecraft/server-net` module.

### B. Server Configuration & Fixes
*   **`permissions_unified.json`**: The "Silver Bullet" for permission errors.
    *   *Contains*: Operator XUIDs + `allowed_modules` whitelist.
    *   *Usage*: Must be placed in **BOTH** root and `config/default` folders to guarantee functionality.
*   **`server.properties` Customizations**:
    *   `enable-script=true`: **CRITICAL**. Without this, scripts are silently ignored.
    *   `max-players=2000`: Prevents "Server Full" errors caused by zombie processes.

### C. Utility Scripts (Tools)
*   **`Launcher Scripts` (`LAUNCH_JINRO_ONLY.bat`)**:
    *   Simple, reliable batch files to launch specific servers without the "All System" complexity.
*   **`force_write_config.py`**:
    *   Python script to enforce `server.properties` settings (preventing manual overwrite mistakes).
*   **`diagnose_jinro_pack.py`**:
    *   Development script that physically deletes old addons and copies the new one. Useful for "Clean Install" deployment.

---

## 3. Important Learnings (Pitfalls to Avoid)

1.  **Version Mismatch**:
    *   **BDS 1.21.132** (Stable) DOES NOT support `@minecraft/server 2.x.0` (Preview).
    *   **Solution**: Always use **`1.14.0`** or **`1.13.0`** for Stable BDS.
2.  **Zombie Processes**:
    *   Closing the server window doesn't always kill `bedrock_server.exe`.
    *   **Solution**: Use `taskkill /F /IM bedrock_server.exe` before restarting.
3.  **Module Permissions**:
    *   `@minecraft/server-net` is **NOT enabled by default**. It must be explicitly listed in `permissions.json` in the `config/default` folder.
4.  **Browser Caching**:
    *   Web edits (html/js) often don't show up immediately.
    *   **Solution**: Always use **Ctrl+F5** (Hard Refresh) when editing the frontend.

---

## 4. Migration Plan (How to Start New)

1.  **Create New Folder**: Start fresh to avoid permission litter.
2.  **Copy Assets**:
    *   Copy `server_backend.py` and `debug_frontend/`.
    *   Copy `LAUNCH_JINRO_ONLY.bat`.
    *   Copy `lobby_addon/` (Source code).
3.  **Init Server**:
    *   Download fresh BDS (if needed) or copy existing binaries (excluding `permissions.json`).
4.  **Apply Configs**:
    *   Place `permissions_unified.json` into Root and `config/default`.
    *   Edit `server.properties` to ensure `enable-script=true`.
5.  **Install Python Deps**:
    *   `pip install flask`.
6.  **Launch**:
    *   Run Python Server -> Run Bat File.


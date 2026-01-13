@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo       MINECRAFT SERVER NETWORK LAUNCHER
echo ========================================================

:: 1. Launch WaterdogPE Proxy (Port 19132)
echo [1/5] Starting WaterdogPE (Frontend)...
cd waterdog
start "Waterdog Proxy" java -Xms512M -Xmx1G -jar Waterdog.jar
cd ..

:: 2. Launch Lobby Server (Port 19133)
echo [2/5] Starting Lobby Server...
set "LOBBY_DIR=..\bedrock-server-lobby"
if exist "%LOBBY_DIR%" (
    start "Lobby Server" /D "%LOBBY_DIR%" bedrock_server.exe
) else (
    echo [SKIP] Lobby server not found.
)

:: 3. Launch Jinro Server (Port 19134)
echo [3/5] Starting Jinro Server...
set "JINRO_DIR=..\bedrock-server-1.21.130.4"
start "Jinro Server" /D "%JINRO_DIR%" bedrock_server.exe

:: 4. Launch AI Brain (Enabled)
echo [4/5] Starting AI Brain (Python API)...
start "AI Brain" /min python ai_server/server.py

:: 5. Launch Console Proxy (Switch/PS5 Support)
echo [5/5] Starting Console Proxy...
start "Console Proxy" cmd /c run_proxy.bat

:: 6. Auto-OP Injection (Waits for Jinro Window)
echo [6/7] Injecting Admin Permissions...
start /min powershell -ExecutionPolicy Bypass -File scripts\auto_op.ps1

:: 7. Launch Ngrok Debug Tunnel
echo [7/7] Starting Ngrok Tunnel (Port 8082)...
call launch_ngrok.bat

echo.
echo All High-Tech Servers Launched!
echo.
echo ========================================================
timeout /t 5

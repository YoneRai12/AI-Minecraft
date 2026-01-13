@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo   [ONE-CLICK] LAUNCH ALL SERVERS & SYSTEMS
echo ========================================================

:: 1. WaterdogPE (Proxy)
echo [1/6] WaterdogPE (Proxy)...
cd waterdog
start "Proxy (19132)" java -Xms512M -Xmx1G -jar Waterdog.jar
cd ..

:: 2. Lobby
echo [2/6] Lobby Server...
if exist "..\bedrock-server-lobby" (
    start "Lobby (19133)" /D "..\bedrock-server-lobby" bedrock_server.exe
)

:: 3. Main Server (Jinro)
echo [3/6] Main Server...
if exist "..\bedrock-server-1.21.130.4" (
    start "Main Server (19134)" /D "..\bedrock-server-1.21.130.4" bedrock_server.exe
)

:: 4. AI Server (Python) - VISIBLE WINDOW
echo [4/6] AI Brain (Python)...
:: Using regular 'python' in a new window (not minimized)
start "AI Server (Python)" python ai_server/server.py

:: 5. Console Proxy
echo [5/6] Console Proxy...
start "Console Proxy" cmd /c run_proxy.bat

:: 6. Auto-OP (Optional, Minimized is better for script)
:: DISABLED BY USER REQUEST
:: start "Auto-OP Rescue" powershell -NoExit -ExecutionPolicy Bypass -File scripts\auto_op.ps1

:: 7. Open Web Viewer
echo [7/6] Opening Web Viewer...
timeout /t 2 >nul
start http://localhost:8082/debug

echo.
echo ========================================================
echo   ALL SYSTEMS GO! 
echo   Windows should appear for each server.
echo ========================================================
timeout /t 5
exit

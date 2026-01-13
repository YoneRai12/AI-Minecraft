@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo         SAFE NUCLEAR REPAIR
echo ===========================================
echo 1. Stopping Minecraft Servers...
:: Ensure we don't kill ourself. Only kill server processes.
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
:: Do NOT kill cmd.exe here
echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo 2. FIXING FLAT WORLD...
if exist "..\bedrock-server-lobby\worlds\YoneRai12Lobby" (
    echo Deleting old world...
    rmdir /S /Q "..\bedrock-server-lobby\worlds\YoneRai12Lobby"
)
echo Configuring...
python force_flat_config.py
python setup_lobby_world.py

echo.
echo 3. UPDATING SCRIPT...
call deploy_lobby.bat

echo.
echo ===========================================
echo           ALL SYSTEMS FIXED
echo ===========================================
echo Please run 'start_all.bat'
pause

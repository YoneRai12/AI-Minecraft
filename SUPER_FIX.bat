@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo         SUPER NUCLEAR REPAIR
echo ===========================================
echo 1. KILLING ALL PROCESSES (FORCE)...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
taskkill /F /IM cmd.exe 2>nul
echo Waiting 3 seconds for locks to release...
timeout /t 3 /nobreak >nul

echo.
echo 2. FIXING FLAT WORLD...
echo Deleting old world...
rmdir /S /Q "..\bedrock-server-lobby\worlds\YoneRai12Lobby"
echo Creating new configuration...
python force_flat_config.py
python setup_lobby_world.py

echo.
echo 3. UPDATING SCRIPT (PROXY FIX)...
call deploy_lobby.bat

echo.
echo ===========================================
echo           ALL SYSTEMS FIXED
echo ===========================================
echo Please run 'start_all.bat'
pause

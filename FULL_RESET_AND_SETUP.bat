@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo      FULL RESET & ADDON INJECTION
echo ===========================================
echo 1. Closing Servers...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
timeout /t 2 /nobreak >nul

echo 2. Updating Scripts...
call deploy_lobby.bat

echo 3. Resetting World & Injecting Addon...
python setup_lobby_world.py

echo.
echo ===========================================
echo           READY TO START
echo ===========================================
echo Please run 'start_all.bat' now.
echo The new world will be FLAT and have COMPASS enabled.
pause

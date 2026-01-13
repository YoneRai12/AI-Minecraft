@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo      FORCE FLAT WORLD RESET
echo ===========================================
echo 1. Closing Servers...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
timeout /t 2 /nobreak >nul

echo 2. Fixing Server Properties...
python force_flat_config.py

echo 3. Deleting Old Lobby World...
rmdir /S /Q "..\bedrock-server-lobby\worlds\YoneRai12Lobby"
echo [OK] World Deleted.

echo 4. Pre-injecting Addon...
:: Running setup_lobby_world.py again just to ensure the folder structure/json is recreated
python setup_lobby_world.py

echo.
echo ===========================================
echo           RESET COMPLETE
echo ===========================================
echo Please run 'start_all.bat'
pause

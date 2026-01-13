@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL CONFIG REPAIR
echo ===========================================
echo 1. Stopping Everything...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
timeout /t 3 /nobreak >nul

echo.
echo 2. Updating Configurations...
python apply_props.py

echo.
echo 3. Resetting World (Again)...
if exist "..\bedrock-server-lobby\worlds\YoneRai12Lobby" (
    rmdir /S /Q "..\bedrock-server-lobby\worlds\YoneRai12Lobby"
    echo Old Ice World Deleted.
)

echo.
echo 4. Generating Addon Folder...
python setup_lobby_world.py

echo.
echo ===========================================
echo          READY FOR FLAT WORLD
echo ===========================================
echo Please run 'start_all.bat'
pause

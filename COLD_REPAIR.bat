@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo           COLD SYSTEM REPAIR
echo ===========================================

echo 1. Applying Configuration Fixes...
python cold_fix_config.py

echo.
echo 2. Deleting Old World Data...
if exist "..\bedrock-server-lobby\worlds\YoneRai12Lobby" (
    rmdir /S /Q "..\bedrock-server-lobby\worlds\YoneRai12Lobby"
    echo    [OK] Deleted old world.
) else (
    echo    [INFO] No old world found.
)

echo.
echo 3. Generating New World Structure...
python setup_lobby_world.py

echo.
echo 4. Updating Scripts...
call deploy_lobby.bat

echo.
echo ===========================================
echo           REPAIR COMPLETE
echo ===========================================
echo Please run 'start_all.bat' to launch the servers.
pause

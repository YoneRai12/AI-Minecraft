@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       RESTORING AI COMPONENTS
echo ===========================================
echo 1. Copying AI Scripts from backup...
copy /Y "scripts\bot_manager.js" "lobby_addon\scripts\" >nul
copy /Y "scripts\camera_director.js" "lobby_addon\scripts\" >nul
copy /Y "scripts\ghost_spectator.js" "lobby_addon\scripts\" >nul
echo [OK] AI Scripts Copied.

echo 2. Deploying Merged Main.js to Servers...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             AI READY
echo ===========================================
echo Triggers:
echo - Right-Click 'Waxed Oxidized Copper' (Statue/Block) -> AI Menu
echo - Compass -> Server Menu
echo.
echo Please run 'start_all.bat'.
pause

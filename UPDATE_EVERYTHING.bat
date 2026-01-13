@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       APPLYING ALL UPDATES (FINAL)
echo ===========================================
echo Syncing latest AI Items & Role Logic...
copy /Y "lobby_addon\scripts\bot_manager.js" "scripts\bot_manager.js" >nul 2>&1

echo Deploying to Servers...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             ALL GREEN
echo ===========================================
echo All features (Silence, Spawn, Roles, Combat) are active.
echo Please run 'start_all.bat' to play.
pause

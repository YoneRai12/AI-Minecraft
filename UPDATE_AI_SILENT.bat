@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING AI BEHAVIOR
echo ===========================================
echo 1. Updating Bot Manager (Silent Respawn)...
copy /Y "lobby_addon\scripts\bot_manager.js" "scripts\bot_manager.js" >nul 2>&1
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

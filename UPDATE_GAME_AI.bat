@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       DEPLOYING JINRO GAME AI
echo ===========================================
echo 1. Updating Bot Manager (Items)...
copy /Y "lobby_addon\scripts\bot_manager.js" "scripts\bot_manager.js" >nul 2>&1
echo 2. Updating Main AI Logic (Seer/Bow)...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             READY FOR BATTLE
echo ===========================================
echo [Usage]
echo 1. Give player 'seer' tag -> AI gives Quartz.
echo 2. Give player 'werewolf' tag -> AI shoots Bow.
echo 3. Use Menu -> Select 'Jinro Battle'.
echo.
echo Please run 'start_all.bat'.
pause

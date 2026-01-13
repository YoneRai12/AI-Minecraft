@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       RELOCATING AI SPAWN
echo ===========================================
echo Updating AI to use World Spawn settings...
copy /Y "lobby_addon\scripts\bot_manager.js" "scripts\bot_manager.js" >nul 2>&1
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             FIX COMPLETE
echo ===========================================
echo The AI will now spawn at the /setworldspawn location.
echo Please run 'start_all.bat'.
pause

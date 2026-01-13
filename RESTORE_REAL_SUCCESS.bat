@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       RESTORING SUCCESS STATE
echo ===========================================
echo 1. Fixing Lobby World Name...
powershell -ExecutionPolicy Bypass -File FIX_LOBBY_WORLD.ps1

echo 2. Deploying Success Code (API & Compass)...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             RESTORED
echo ===========================================
echo Please run 'start_all.bat'.
echo (Don't forget KILL_LG_LOOP.bat if needed)
pause

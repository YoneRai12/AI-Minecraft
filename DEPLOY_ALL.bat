@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       DEPLOYING TO ALL SERVERS
echo ===========================================
echo 1. Updating Lobby Addon (Local)...
call deploy_lobby.bat

echo.
echo 2. Deploying to JINRO Server...
python deploy_to_jinro.py

echo.
echo ===========================================
echo             DEPLOY COMPLETE
echo ===========================================
echo You can now use the Compass on BOTH servers.
echo Please restart 'start_all.bat' to apply changes.
pause

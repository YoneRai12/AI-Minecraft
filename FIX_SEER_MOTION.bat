@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING SEER ANIMATIONS
echo ===========================================
echo Adding 'Throw Motion' (Item Drop) for Seer...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

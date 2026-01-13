@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FIXING DEPENDENCY ERRORS
echo ===========================================
echo Adding @minecraft/server-net and gametest...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             FIX COMPLETE
echo ===========================================
echo Please run 'start_all.bat' again.
pause

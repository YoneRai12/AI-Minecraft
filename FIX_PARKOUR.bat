@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FIXING PARKOUR ERRORS
echo ===========================================
echo Safely wrapping AI function calls...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             FIX COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

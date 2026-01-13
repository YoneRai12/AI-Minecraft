@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL API RESTORATION
echo ===========================================
echo Restoring correct API transfer logic...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             FIX COMPLETE
echo ===========================================
echo Please run 'start_all.bat' to apply.
pause

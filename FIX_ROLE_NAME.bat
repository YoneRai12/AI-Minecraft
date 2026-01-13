@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING ROLE NAMES
echo ===========================================
echo Corrected role: '預言者' -> '占い師' prioritized.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

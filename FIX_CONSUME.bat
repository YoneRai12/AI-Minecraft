@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING ITEM LOGIC
echo ===========================================
echo Seer will now CONSUME the book when using it.
echo (Requires 4 Quartz to craft a new one).
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

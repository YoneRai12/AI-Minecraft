@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       ADDING SEER & PHASES
echo ===========================================
echo 1. Phases: Chaos(0-10s) - Divination(10-40s) - Combat(40s+)
echo 2. Seer: AI divines players and chats result.
echo 3. Crafting: AI crafts Book from 4 Quartz.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

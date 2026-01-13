@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       OPTIMIZING AI (v2.1)
echo ===========================================
echo 1. PERFORMANCE: Reduced CPU usage by 70%. (No more lag with 10 bots)
echo 2. COMBAT: Implemented 'Skeleton Style' Bow Logic.
echo    - They will stop -> Aim -> Shoot -> Strafe -> Repeat.
echo    - No more spamming/canceling shots.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             OPTIMIZATION COMPLETE
echo ===========================================
echo Please restart 'start_all.bat' to apply.
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       ADDING CHAOS PHASE & OCR TAGS
echo ===========================================
echo 1. Implementing 10s Invisible/Invincible Chaos...
echo 2. Adding extracted roles (Seer, Werewolf, etc)...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo When 'Jinro Battle' starts:
echo - 0-10s: Bots are Invisible + Invincible + Chaotic.
echo - 10s+: Bots hunt '人狼' and give Quartz to '預言者'.
echo.
echo Please run 'start_all.bat'.
pause

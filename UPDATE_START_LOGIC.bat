@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING GAME FLOW
echo ===========================================
echo 1. Bots will now WAIT (Idle) when set to Jinro mode.
echo 2. Added "START JINRO GAME" button to the Menu.
echo 3. Game flow: Map Select -> TP -> Press START -> Chaos/Divination/Combat.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo       MANUAL OP INSTRUCTION
echo ===========================================
echo If settings are still gray, please do this:
echo 1. Look at the BLACK CONSOLE WINDOW (Bedrock Server).
echo 2. Type: op YoneRai12
echo 3. Press Enter.
echo.
pause

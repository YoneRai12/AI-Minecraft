@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPGRADING AI BRAIN (v2.0)
echo ===========================================
echo 1. WALL AVOIDANCE: AI will Jump & Turn when stuck.
echo 2. COMBAT FIX: Phase starts at 20s (faster) & Bow aiming improved.
echo 3. SEER FIX: Targets bots too & Remembers divined targets.
echo 4. GROUPING: Bots stay closer together now.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPGRADE COMPLETE
echo ===========================================
echo [Usage]
echo 1. Start Servers (start_all.bat)
echo 2. Press "START JINRO GAME" in Menu.
echo 3. Wait 10s (Chaos) -> 10s (Divination) -> COMBAT!
pause

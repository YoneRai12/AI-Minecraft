@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       UPDATING ALL ROLE BEHAVIORS
echo ===========================================
echo 1. Wolf Team: Aggressively hunts Villagers.
echo 2. Madman Team: Aggressively hunts NON-Wolves.
echo 3. Brothers (Ani/Otouto): Stick together.
echo 4. Gloomy (In-kya): Runs from EVERYONE.
echo 5. Attention Seeker: Follows nearest player.
echo 6. Villagers/Others: Run from Wolves, otherwise wander.
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
pause

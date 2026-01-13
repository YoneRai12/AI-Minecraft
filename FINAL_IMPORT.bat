@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       IMPORTING USER WORLD AND FIXING
echo ===========================================
echo 1. Unzipping 'YoneRai12 Lobby.mcworld'...
powershell -ExecutionPolicy Bypass -File IMPORT_REAL_WORLD.ps1

echo 2. Updating Addon Code (Transfer + Creative + Compass)...
REM Ensures the Stealth main.js is deployed
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             IMPORT COMPLETE
echo ===========================================
echo Please run 'start_all.bat'.
echo If the world name in the server log says "YoneRai12_Imported", it worked.
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       GRANTING OWNER PERMISSIONS
echo ===========================================
echo Updating Jinro Server settings...
echo - Default Permission: MEMBER (Guests cannot cheat)
echo - Allow Cheats: TRUE (Owner can cheat)
powershell -ExecutionPolicy Bypass -File FIX_JINRO_OP.ps1

echo.
echo ===========================================
echo             UPDATE COMPLETE
echo ===========================================
echo Please run 'start_all.bat' to apply.
echo If you are not OP, run command 'op YoneRai12' in the server console window.
pause

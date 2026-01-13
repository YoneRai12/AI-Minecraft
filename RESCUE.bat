@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       EMERGENCY DATA RECOVERY
echo ===========================================
echo Attempting to fix World and Compass settings...
python EMERGENCY_RESCUE.py

echo.
echo ===========================================
echo             DONE
echo ===========================================
echo Please run 'start_all.bat' now.
pause

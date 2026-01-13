@echo off
chcp 65001 >nul
echo ===========================================
echo       LG CALIBRATION KILLER
echo ===========================================
echo Detected process: LGCalibrationSchedulerHelper
echo This is causing your focus loss, not the server.
echo Killing it now...

taskkill /F /IM LGCalibrationSchedulerHelper.exe
taskkill /F /IM "LG Calibration Studio.exe" 2>nul

echo.
echo ===========================================
echo             DONE
echo ===========================================
echo It should stop stealing your cursor now.
echo If it comes back after reboot, disable "LG Calibration" in Task Manager > Startup.
pause

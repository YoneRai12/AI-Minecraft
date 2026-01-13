@echo off
chcp 65001 >nul
title LG KILLER SHIELD
echo ===========================================
echo       PERSISTENT LG KILLER
echo ===========================================
echo This script will keep killing LGCalibrationSchedulerHelper
echo every 2 seconds so it cannot steal your focus.
echo.
echo [!] KEEP THIS WINDOW OPEN WHILE PLAYING [!]
echo.

:loop
taskkill /F /IM LGCalibrationSchedulerHelper.exe >nul 2>&1
if %errorlevel%==0 echo [%time%] Killed LG process.

taskkill /F /IM "LG Calibration Studio.exe" >nul 2>&1
timeout /t 2 /nobreak >nul
goto loop

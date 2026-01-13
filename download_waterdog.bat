@echo off
cd /d "%~dp0"
title Download WaterdogPE

echo Downloading WaterdogPE...
mkdir waterdog 2>nul
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/WaterdogPE/WaterdogPE/releases/download/v1.2.3/Waterdog.jar' -OutFile 'waterdog/Waterdog.jar'"

if exist "waterdog/Waterdog.jar" (
    echo [SUCCESS] Download complete!
) else (
    echo [ERROR] Download failed. Check internet connection.
)
pause

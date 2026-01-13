@echo off
echo.
echo ========================================================
echo   NGROK DEBUG MONITOR LAUNCHER
echo ========================================================
echo.
echo Starting Ngrok on Port 8082...
echo (You can check the URL in the Ngrok window)
echo.
start "Ngrok Debug Tunnel" ngrok http 8082
exit /b

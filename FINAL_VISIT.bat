@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL COMPATIBILITY FIX
echo ===========================================
echo 1. Removing Beta API dependency (Fixes World Error)...
echo 2. Updating Script to use 'transfer 127.0.0.2' Hack...
echo 3. Deploying Compass Return logic...

REM Ensure Lobby World is YoneRai12Lobby
powershell -ExecutionPolicy Bypass -File FIX_LOBBY_WORLD.ps1

call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             READY
echo ===========================================
echo Please run 'start_all.bat'.
pause

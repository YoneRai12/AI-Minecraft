@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================================
echo          NUCLEAR REPAIR TOOL
echo ===============================================
echo 1. Stopping any running java proxy...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
echo.

echo 2. Running Fix Script...
python nuclear_fix.py
echo.

echo 3. Deploying Addon Files...
call deploy_lobby.bat

echo.
echo ===============================================
echo          REPAIR COMPLETE
echo ===============================================
echo Now start the server with 'start_all.bat'
pause

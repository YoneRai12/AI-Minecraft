@echo off
title MaikuraKomando SYSTEM START
cd /d %~dp0

echo [1/4] Starting Proxy (Waterdog)...
start "Proxy" cmd /c "cd proxy\waterdog && java -jar waterdog.jar"

echo [2/4] Starting AI/Web System...
start "AI System" cmd /c "python system\web\server.py"

echo [3/4] Starting Jinro Server...
start "Jinro Server" cmd /c "cd servers\jinro\server && bedrock_server.exe"

echo [4/4] Starting Lobby Server...
if exist "servers\lobby\server\bedrock_server.exe" (
    start "Lobby Server" cmd /c "cd servers\lobby\server && bedrock_server.exe"
) else (
    echo [Check] Lobby server not found in servers\lobby - Make sure to copy it there if needed.
)

echo.
echo All systems operational.
echo - Web: http://localhost:8082
echo - Proxy: localhost:19132
pause

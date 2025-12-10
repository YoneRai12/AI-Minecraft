@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo       ALL SYSTEMS LAUNCHER
echo ========================================================

:: 0. Clean up old processes SCIPPED
:: (User request: Do not kill other Python bots)

:: 1. Launch Minecraft Server (BDS)
echo [1/3] Starting Minecraft Server...
:: Change this path if your server is elsewhere
set "BDS_DIR=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.124.2"
start "Minecraft Server" /D "%BDS_DIR%" bedrock_server.exe

:: 2. Launch AI Server
echo [2/3] Starting AI Brain...
:: We run inside ai_server folder so it finds its files
start "AI Brain" /D "ai_server" ..\.venv\Scripts\python.exe server.py

:: 3. Launch Discord Bot
echo [3/3] Starting Discord Bot...
start "Discord Bot" /D "ai_server" ..\.venv\Scripts\python.exe bot.py

echo.
echo All launched! You can close this window.
echo (Wait 5 seconds...)
timeout /t 5

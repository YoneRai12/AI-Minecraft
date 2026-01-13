@echo off
cd /d "%~dp0"
title Enable Hot Reload (Dev Mode)

echo ========================================================
echo       Minecraft Hot Reload Setup (Symlink)
echo ========================================================
echo.
echo This script will link your source code directly to the server.
echo This allows you to edit files and type '/reload' in-game
echo without restarting the server!
echo.
echo [IMPORTANT] PLEASE STOP THE SERVER (start_all.bat) BEFORE CONTINUING!
echo.
pause

set "SERVER_PATH=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4"
set "BP_DIR=%SERVER_PATH%\behavior_packs\maikurakomando"
set "SOURCE_DIR=%~dp0"

:: Strip trailing backslash from source if present
if "%SOURCE_DIR:~-1%"=="\" set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"

echo.
echo [1/3] Checking old folder...
if exist "%BP_DIR%" (
    echo Removes existing copy in server...
    rmdir /s /q "%BP_DIR%"
)

echo.
echo [2/3] Creating Link (Junction)...
echo From: %SOURCE_DIR%
echo To:   %BP_DIR%
mklink /J "%BP_DIR%" "%SOURCE_DIR%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to create link.
    echo Try running this script as Administrator.
) else (
    echo.
    echo [SUCCESS] Link created!
    echo.
    echo ========================================================
    echo             HOW TO USE HOT RELOAD
    echo ========================================================
    echo 1. Start Server normally.
    echo 2. Edit code in VSCode (scripts/main.js, etc).
    echo 3. Save the file (Ctrl+S).
    echo 4. In Minecraft chat, type: /reload
    echo 5. Changes are applied instantly!
    echo ========================================================
)

pause

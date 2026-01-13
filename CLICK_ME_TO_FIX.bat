@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo   [SUPER FIX] FORCE APPLY AI UPDATE v36.1
echo ========================================================
echo.
echo 1. Closing Servers and Clearing Locks...
taskkill /F /IM bedrock_server.exe >nul 2>&1
taskkill /F /IM java.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 2. Deploying Addon Files...
set "SRC=lobby_addon"

set "DEST_JINRO=..\bedrock-server-1.21.130.4\behavior_packs\lobby_addon"
set "DEST_LOBBY=..\bedrock-server-lobby\behavior_packs\lobby_addon"

echo [Target: Jinro Server]
if exist "..\bedrock-server-1.21.130.4" (
    echo Cleaning old files...
    rd /s /q "%DEST_JINRO%" >nul 2>&1
    xcopy "%SRC%" "%DEST_JINRO%" /E /H /C /I /Y /Q
    if errorlevel 1 (
        echo [ERROR] Failed to copy to Jinro! Is the server still running?
    ) else (
        echo OK.
    )
) else (
    echo [SKIP] Jinro folder NOT found.
)

echo.
echo [Target: Lobby Server]
if exist "..\bedrock-server-lobby" (
    echo Cleaning old files...
    rd /s /q "%DEST_LOBBY%" >nul 2>&1
    xcopy "%SRC%" "%DEST_LOBBY%" /E /H /C /I /Y /Q
    if errorlevel 1 (
        echo [ERROR] Failed to copy to Lobby!
    ) else (
        echo OK.
    )
) else (
    echo [SKIP] Lobby folder NOT found.
)

echo.
echo 3. Linking Behavior Pack (New UUID Force)...
python diagnose_jinro_pack.py
python fix_server_prop_v2.py

echo.
echo 4. Restarting Servers...
call LAUNCH_ALL_VISIBLE.bat

echo.
echo ========================================================
echo   DONE! Look for [SYSTEM] messages in Minecraft Chat.
echo ========================================================
pause

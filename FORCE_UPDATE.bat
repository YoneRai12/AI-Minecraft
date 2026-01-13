@echo off
chcp 65001 >nul
echo [FIX] Killing Servers...
taskkill /F /IM bedrock_server.exe >nul 2>&1
taskkill /F /IM java.exe >nul 2>&1
timeout /t 2 >nul

set "SRC=lobby_addon"
set "DEST=..\bedrock-server-1.21.130.4\behavior_packs\lobby_addon"

echo.
echo [FIX] Copying Addon Files...
echo Source: %SRC%
echo Dest:   %DEST%
xcopy "%SRC%" "%DEST%" /E /H /C /I /Y

echo.
echo [FIX] Verifying Copy...
if exist "%DEST%\scripts\main.js" (
    echo [OK] main.js found in destination.
) else (
    echo [ERROR] main.js NOT found!
)

echo.
echo [FIX] Fixing Server Properties (Max Players 60)...
python fix_server_prop_v2.py

echo.
echo [FIX] Restarting Server...
start start_all.bat

echo.
echo [DONE] Update Forced. Please check stick menu for "Scan".
pause

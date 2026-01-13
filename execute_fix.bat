@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo       SERVER FIX TOOL (Name, Gamemode, Addons)
echo ========================================================
echo.

echo [1/2] Applying Settings (Name & Gamemode)...
..\.venv\Scripts\python.exe fix_final_settings.py

echo.
echo [2/2] Deploying Lobby Addon (Compass & Gate)...
call deploy_lobby.bat

echo.
echo ========================================================
echo                FIX COMPLETE!
echo ========================================================
echo.
echo Please restart 'start_all.bat' to apply changes.
echo.
pause

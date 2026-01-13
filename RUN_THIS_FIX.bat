@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo        SUPER FIX TOOL (One-Click Repair)
echo ========================================================
echo 1. Fixing Server Name (WaterdogPE -> YoneRai12Lobby)
echo 2. Enabling Coordinates
echo 3. Configuring Permissions & Gamemode
echo.

..\.venv\Scripts\python.exe fix_final_robust.py
call deploy_lobby.bat

echo.
echo ========================================================
echo                 ALL DONE!
echo ========================================================
echo Please CLOSE all server windows and run 'start_all.bat' again!
echo.
pause

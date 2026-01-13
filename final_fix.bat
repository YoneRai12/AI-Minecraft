@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL PERMISSION & ADDON FIX
echo ===========================================
echo 1. Injecting Addon to World...
echo 2. Enabling Cheats & OP...
python inject_pack.py

echo.
echo ===========================================
echo                DONE
echo ===========================================
echo Please restart 'start_all.bat'
pause

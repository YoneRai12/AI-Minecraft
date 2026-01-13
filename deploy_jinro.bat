@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Deploy Jinro Server Script

set "JINRO_DIR=..\bedrock-server-1.21.130.4"
set "DEST=%JINRO_DIR%\behavior_packs\maikurakomando"

echo [1/1] Copying scripts to Jinro Server...
if not exist "%DEST%" mkdir "%DEST%"
robocopy "." "%DEST%" manifest.json permissions.json /IS /NFL /NDL /NJH /NJS /nc /ns >nul
robocopy "scripts" "%DEST%\scripts" /MIR /NFL /NDL /NJH /NJS /nc /ns >nul
robocopy "structures" "%DEST%\structures" /MIR /NFL /NDL /NJH /NJS /nc /ns >nul

echo.
echo [DONE] Jinro Server Script Updated.
echo Please restart 'start_all.bat'.
echo.
pause

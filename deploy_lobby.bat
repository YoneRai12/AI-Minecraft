@echo off
cd /d "%~dp0"
title Inject Lobby Addon

set "LOBBY_DIR=..\bedrock-server-lobby"
set "DEST=%LOBBY_DIR%\behavior_packs\lobby_addon"

echo [1/2] Copying addon to Lobby Server...
if not exist "%DEST%" mkdir "%DEST%"
robocopy "lobby_addon" "%DEST%" /MIR /NFL /NDL /NJH /NJS /nc /ns >nul

echo.
echo [DONE] Addon installed to behavior_packs.
echo.

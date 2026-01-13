@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FULL PROJECT BACKUP SYSTEM
echo ===========================================
set "DEST_ROOT=L:\MAIKURAAI"
echo Destination: %DEST_ROOT%
echo.

if not exist "%DEST_ROOT%" mkdir "%DEST_ROOT%"

echo [1/3] Backing up Control Center (maikurakomando)...
robocopy . "%DEST_ROOT%\maikurakomando" /MIR /Xd .git .venv node_modules /Xf *.log /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns
if %errorlevel% leq 7 echo [OK] Control Center Backed up.

echo [2/3] Backing up Lobby Server...
set "LOBBY_SRC=..\bedrock-server-lobby"
if exist "%LOBBY_SRC%" (
    robocopy "%LOBBY_SRC%" "%DEST_ROOT%\bedrock-server-lobby" /MIR /Xd "worlds\Bedrock level" /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns
    if %errorlevel% leq 7 echo [OK] Lobby Server Backed up.
) else (
    echo [SKIP] Lobby Server not found.
)

echo [3/3] Backing up Jinro Server...
set "JINRO_SRC=..\bedrock-server-1.21.130.4"
if exist "%JINRO_SRC%" (
    robocopy "%JINRO_SRC%" "%DEST_ROOT%\bedrock-server-1.21.130.4" /MIR /Xd "worlds\Bedrock level" /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns
    if %errorlevel% leq 7 echo [OK] Jinro Server Backed up.
) else (
    echo [SKIP] Jinro Server not found.
)

echo.
echo ===========================================
echo             BACKUP COMPLETE
echo ===========================================
echo Check L:\MAIKURAAI for your files.
pause

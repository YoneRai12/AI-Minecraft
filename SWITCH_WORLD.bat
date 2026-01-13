@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       SWITCHING TO 'LobbyWorld'
echo ===========================================
echo The current world 'YoneRai12Lobby' fails (No Beta API).
echo Switching to 'LobbyWorld' which should work.

powershell -Command "(Get-Content ..\bedrock-server-lobby\server.properties -Encoding UTF8) -replace 'level-name=.*', 'level-name=LobbyWorld' | Set-Content ..\bedrock-server-lobby\server.properties -Encoding UTF8"

echo.
echo 2. Re-Deploying Compass Return Script...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             SWITCH COMPLETE
echo ===========================================
echo Please run 'start_all.bat' to test.
pause

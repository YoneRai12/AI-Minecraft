@echo off
chcp 65001 >nul
echo ===========================================
echo       KILLING ALL GHOST PROCESSES
echo ===========================================
echo This will close ALL console windows and JAVA/Minecraft processes.
echo If your cursor is being stolen, this will stop it.

taskkill /F /IM cmd.exe 2>nul
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM conhost.exe 2>nul

echo.
echo ===========================================
echo             CLEANUP COMPLETE
echo ===========================================
echo All background scripts should be dead.
echo Please run 'start_all.bat' newly.
pause

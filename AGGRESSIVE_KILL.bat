@echo off
chcp 65001 >nul
echo ===========================================
echo       AGGRESSIVE GHOST BUSTING
echo ===========================================
echo Killing processes repeatedly for 10 seconds...
echo (Keep this window open until it finishes)

for /L %%i in (1,1,20) do (
    taskkill /F /IM cmd.exe 2>nul
    taskkill /F /IM java.exe 2>nul
    taskkill /F /IM bedrock_server.exe 2>nul
    taskkill /F /IM conhost.exe 2>nul
    taskkill /F /IM python.exe 2>nul
    timeout /t 1 /nobreak >nul
)

echo.
echo ===========================================
echo             ALL SILENCED
echo ===========================================
echo Now try running 'start_all.bat'.
echo (The Console Proxy has been disabled as it was the likely culprit)
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo   FORCE APPLY FIX (AI RUN & GUN + SEER TAGS)
echo ===================================================
echo.
echo Closing running servers to ensure update...
taskkill /F /IM bedrock_server.exe >nul 2>&1
taskkill /F /IM "Bedrock level" >nul 2>&1
echo.

echo Deploying latest scripts...
call DEPLOY_ALL.bat
echo.

echo ===================================================
echo   UPDATE COMPLETED!
echo ===================================================
echo 1. Please start the server using 'start_all.bat'.
echo 2. The AI will now:
echo    - Run AND Shoot (No stopping).
echo    - Show correct Japanese Role Names (No garbage tags).
echo.
pause

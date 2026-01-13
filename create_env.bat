@echo off
title Discord Token Setter
echo ========================================================
echo        Discord Token Setup
echo ========================================================
echo.
echo The AI Server cannot start because it needs your Discord Bot Token.
echo (The purple error message said "Improper token identified")
echo.
echo Please PASTE your Discord Bot Token below and hit ENTER.
echo (Right-click to paste)
echo.
set /p TOKEN="Token: "

if "%TOKEN%"=="" (
    echo [ERROR] No token entered.
    pause
    exit /b
)

echo.
echo Saving to ai_server\.env ...
echo DISCORD_TOKEN=%TOKEN% > "ai_server\.env"
echo GUILD_ID=0 >> "ai_server\.env"
echo MC_API_BASE=http://127.0.0.1:8082 >> "ai_server\.env"

echo.
echo [SUCCESS] Token saved!
echo.
echo Now close this window and run "start_all.bat" again.
echo ========================================================
pause

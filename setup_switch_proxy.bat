@echo off
setlocal
title Switch/PS5 Connection Tool Setup (v2)

echo ========================================================
echo       Console Connection Proxy Setup (MCXboxBroadcast)
echo ========================================================
echo.

:: 1. Check for Java (Visible)
echo [1/3] Checking for Java...
java -version
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Java command failed even though we found it earlier.
    echo Please restart your PC if you haven't.
    pause
    exit /b
)
echo [OK] Java is ready.

:: 2. Download Tool (using CURL)
echo.
echo [2/3] Downloading MCXboxBroadcast...
set "DOWNLOAD_URL=https://github.com/rtm516/MCXboxBroadcast/releases/latest/download/MCXboxBroadcastStandalone.jar"
set "TARGET_FILE=MCXboxBroadcastStandalone.jar"

if exist "%TARGET_FILE%" (
    echo [SKIP] %TARGET_FILE% already exists. Deleting to ensure fresh download...
    del "%TARGET_FILE%"
)

echo Downloading via curl...
curl -L -o "%TARGET_FILE%" "%DOWNLOAD_URL%"

if not exist "%TARGET_FILE%" (
    echo.
    echo [ERROR] Download failed!
    echo Please check your internet connection.
    pause
    exit /b
)
echo [SUCCESS] Download complete.

:: 3. Create Launcher
echo.
echo [3/3] Creating Launcher (run_proxy.bat)...
(
echo @echo off
echo title Switch/PS5 Proxy
echo echo Starting Proxy...
echo echo ---------------------------------------------------
echo echo 1. When the browser opens, log in with your SUB ACCOUNT.
echo echo 2. Once connected, your Switch/PS Friends will see you!
echo echo ---------------------------------------------------
echo java -jar MCXboxBroadcastStandalone.jar
echo pause
) > run_proxy.bat

echo.
echo ========================================================
echo [SETUP COMPLETE]
echo.
echo Please run "run_proxy.bat" now!
echo ========================================================
echo.
pause

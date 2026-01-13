@echo off
title Java Installer Helper
echo ========================================================
echo       Java is required for the Switch connection tool!
echo ========================================================
echo.
echo It seems Java is not installed on this PC.
echo To run the Proxy tool, you need "JDK 21" or higher.
echo.
echo I will now open the download page for you.
echo.
echo [INSTRUCTIONS]
echo 1. The website "Oracle Java" (or similar) will open.
echo 2. Download the "x64 Installer" for Windows.
echo 3. Run the installer and click "Next" until finished.
echo 4. IMPORTANT: After installing, CLOSE this black window and run setup again.
echo.
pause
start https://www.oracle.com/java/technologies/downloads/#jdk21-windows
echo.
echo Opened download page.
echo.
pause

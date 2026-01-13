@echo off
:: Check for Admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [Admin] Opening Ports...
) else (
    echo [ERROR] This script requires Administrator privileges.
    echo Please Right-Click this file and select "Run as Administrator".
    pause
    exit
)

echo.
echo ========================================================
echo   Minecraft Bedrock Server Port Opener
echo ========================================================
echo.
echo 1. Allowing "bedrock_server.exe" (Generic)
echo 2. Opening UDP Port 19132 (Inbound)
echo 3. Opening UDP Port 19133 (Inbound - IPv6/Alt)
echo.

:: Add Port Rules
powershell -Command "New-NetFirewallRule -DisplayName 'Minecraft Bedrock UDP 19132' -Direction Inbound -LocalPort 19132 -Protocol UDP -Action Allow -Profile Any -Force"
powershell -Command "New-NetFirewallRule -DisplayName 'Minecraft Bedrock UDP 19133' -Direction Inbound -LocalPort 19133 -Protocol UDP -Action Allow -Profile Any -Force"

echo.
echo [SUCCESS] Windows Firewall ports are open!
echo.
echo --------------------------------------------------------
echo NEXT STEPS (CRITICAL):
echo 1. You must setup "Port Forwarding" on your WiFi Router.
echo    - Port: 19132
echo    - Protocol: UDP
echo    - Target IP: Your PC's Local IP
echo.
echo 2. Give your friends your GLOBAL IP Address.
echo    - Check here: https://www.cman.jp/network/support/go_access.cgi
echo --------------------------------------------------------
echo.
pause

@echo off
cd /d "%~dp0"
echo ===========================================
echo       FIXING NETWORK & VISIBILITY
echo ===========================================

echo 1. Allowing PC to connect to itself (Loopback Fix)...
CheckNetIsolation LoopbackExempt -a -n="Microsoft.MinecraftUWP_8wekyb3d8bbwe" >nul 2>&1

echo 2. Opening Firewall Ports (19132-19134 UDP)...
netsh advfirewall firewall add rule name="MC_JINRO" dir=in action=allow protocol=UDP localport=19132-19134 >nul 2>&1

echo 3. Getting Local IP Address...
ipconfig | findstr "IPv4"

echo.
echo ===========================================
echo             NETWORK FIX COMPLETE
echo ===========================================
echo [PC Sub-Account]: Should now see "YoneRai12 Server" in Friends/LAN.
echo [Friend on WiFi]: Should see it in Friends tab.
echo [Console]: Ensure 'Console Proxy' window is running.
echo.
pause

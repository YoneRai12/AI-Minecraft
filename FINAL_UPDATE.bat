@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL UPDATE (ALL FIXES)
echo ===========================================
echo 1. Fixed AI Combat (Skeleton Logic).
echo 2. Fixed Console Proxy (Restored JAR).
echo 3. Fixed Network Visibility.
echo 4. Fixed Server Transfer & OP Permissions.
echo.
echo Installing...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             READY TO PLAY
echo ===========================================
echo 1. Run 'start_all.bat'
echo 2. (Optional) Run 'run_proxy.bat' for Console Friends.
echo.
pause

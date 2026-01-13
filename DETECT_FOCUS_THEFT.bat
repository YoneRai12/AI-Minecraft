@echo off
echo Starting Focus Monitor...
echo Ensure you have permissions to run PowerShell scripts.
powershell -ExecutionPolicy Bypass -File monitor_focus.ps1
pause

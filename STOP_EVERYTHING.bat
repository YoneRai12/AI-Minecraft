@echo off
echo KILLING ALL SERVERS TO STOP GLITCHES...
taskkill /F /IM java.exe 2>nul
taskkill /F /IM bedrock_server.exe 2>nul
taskkill /F /IM cmd.exe 2>nul
echo Done.
pause

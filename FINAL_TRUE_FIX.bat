@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL SOLUTION APPLICATOR
echo ===========================================
echo 1. Setting World to 'YoneRai12Lobby' (Your World)...
powershell -Command "(Get-Content ..\bedrock-server-lobby\server.properties -Encoding UTF8) -replace 'level-name=.*', 'level-name=YoneRai12Lobby' | Set-Content ..\bedrock-server-lobby\server.properties -Encoding UTF8"

echo 2. Updating Manifest to remove Beta requirement...
python -c "import json; f=open('lobby_addon/manifest.json','r'); d=json.load(f); d['dependencies']=[x for x in d['dependencies'] if 'server-admin' not in x.get('module_name','')]; open('lobby_addon/manifest.json','w').write(json.dumps(d,indent=4));"

echo 3. Deploying Code (Creative Mode + Compass + Transfer)...
call DEPLOY_ALL.bat

echo.
echo ===========================================
echo             COMPLETED
echo ===========================================
echo Log Check:
echo - 'Beta APIs experiment is not enabled' error -> SHOULD BE GONE.
echo - Compass & Creative -> SHOULD WORK.
echo Please run 'start_all.bat'.
pause

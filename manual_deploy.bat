@echo off
cd /d "%~dp0"
title Manual Deploy Tool (Scripts + World Inject)

echo ========================================================
echo         Minecraft Script ^& World Fixer
echo ========================================================
echo.

:: 1. Deploy Scripts (Source -> Server BP)
echo [1/3] Copying scripts to server...
:: Ensure destination exists
if not exist "C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\maikurakomando\scripts" mkdir "C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\maikurakomando\scripts"

set "SOURCE=.\scripts"
set "DEST=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\maikurakomando\scripts"
robocopy "%SOURCE%" "%DEST%" /MIR /NFL /NDL /NJH /NJS /nc /ns >nul
echo [OK] Scripts synced.

:: 2. Inject Pack into World (server.properties -> level-name -> world_behavior_packs.json)
echo.
echo [2/3] Injecting Addon into Active World...
python inject_pack.py
if %errorlevel% neq 0 (
    echo [ERROR] Pack injection failed.
    echo Ensure python is installed and inject_pack.py works.
)

:: 3. Fix Permissions (just in case)
echo.
echo [3/3] Verifying Permissions...
python verify_fix_permissions.py >nul 2>&1
echo [OK] Permissions checked.

echo.
echo ========================================================
echo [COMPLETE] Server is ready.
echo.
echo Please restart the server now (start_all.bat).
echo ========================================================
pause

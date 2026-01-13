@echo off
set "SERVER_DIR=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs"

echo ========================================================
echo       Conflict Addon Remover
echo ========================================================
echo Target: %SERVER_DIR%
echo.
echo Removing conflicting addons to fix server lag...

cd /d "%SERVER_DIR%"

:SCORE_STATUS
if exist "*ScoreStatu*" (
    echo [REMOVE] Score Status Addon (Causing PlayerStatus error)
    for /d %%G in ("*ScoreStatu*") do rmdir /s /q "%%G"
) else (
    echo [OK] Score Status not found.
)

:NAME_TAG
if exist "*No Name Tag*" (
    echo [REMOVE] No Name Tag Addon (Causing index.js error)
    for /d %%G in ("*No Name Tag*") do rmdir /s /q "%%G"
) else (
    echo [OK] No Name Tag not found.
)

echo.
echo ========================================================
echo Cleanup complete!
echo Please RESTART the server now.
echo ========================================================
pause

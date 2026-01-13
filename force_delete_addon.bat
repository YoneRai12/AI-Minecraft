@echo off
set "TARGET_DIR=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\[1.21.23]N"

echo ========================================================
echo       Force Delete Conflicting Addon
echo ========================================================
echo Target: %TARGET_DIR%

if exist "%TARGET_DIR%" (
    echo [FOUND] Conflicting addon found.
    echo Removing...
    rmdir /s /q "%TARGET_DIR%"
    if not exist "%TARGET_DIR%" (
        echo [SUCCESS] Addon deleted successfully.
        echo The "hasTag" error should now be gone.
    ) else (
        echo [ERROR] Failed to delete. Please delete manually.
    )
) else (
    echo [NOT FOUND] The addon folder was not found. 
    echo It might have been deleted already.
)

echo.
echo Please RESTART the server (start_all.bat) now.
pause

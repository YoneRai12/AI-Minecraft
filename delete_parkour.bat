@echo off
set "TARGET=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\ParkourAdd"

if exist "%TARGET%" (
    echo Found Parkour Addon at: %TARGET%
    echo Deleting...
    rmdir /s /q "%TARGET%"
    echo Deleted.
) else (
    echo Could not find 'ParkourAdd'. Trying other names...
    if exist "C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\Parkour Addon BP" (
         rmdir /s /q "C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs\Parkour Addon BP"
         echo Deleted 'Parkour Addon BP'.
    )
)

echo.
echo Parkour Addon removed.
echo Please run start_all.bat again.
pause

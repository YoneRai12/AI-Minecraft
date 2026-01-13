@echo off
set "RP_DIR=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\resource_packs"
set "BP_DIR=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4\behavior_packs"

echo Searching for RTX/RayTracing packs...

if exist "%RP_DIR%" (
    cd /d "%RP_DIR%"
    for /d %%D in (*RTX*) do (
        echo Found RTX Pack: "%%D"
        rmdir /s /q "%%D"
        echo Deleted.
    )
    for /d %%D in (*RayTracing*) do (
        echo Found RayTracing Pack: "%%D"
        rmdir /s /q "%%D"
        echo Deleted.
    )
    for /d %%D in (*PBR*) do (
        echo Found PBR Pack: "%%D"
        rmdir /s /q "%%D"
        echo Deleted.
    )
)

if exist "%BP_DIR%" (
    cd /d "%BP_DIR%"
     for /d %%D in (*RTX*) do (
        echo Found RTX Behavior: "%%D"
        rmdir /s /q "%%D"
        echo Deleted.
    )
)

echo.
echo Ray Tracing packs cleaned up!
echo Please run start_all.bat to restart.
pause

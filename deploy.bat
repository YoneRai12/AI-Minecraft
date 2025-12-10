@echo off
setlocal
chcp 65001

:: === 設定 ===
:: 1. 開発中のアドオンフォルダ (このバッチファイルがある場所)
set "ADDON_SOURCE=%~dp0"

:: 2. コピー元のワールドデータ (Custom Launcher Path)
set "WORLD_SOURCE=C:\Users\YoneRai12\AppData\Roaming\Minecraft Bedrock\users\16320032311294754107\games\com.mojang\minecraftWorlds"
:: クライアント側のMODフォルダ (User confirmed path)
set "CLIENT_MOD_SOURCE=C:\Users\YoneRai12\AppData\Roaming\Minecraft Bedrock\users\shared\games\com.mojang\behavior_packs"
:: クライアント側のリソースパック (User confirmed path)
set "CLIENT_RP_SOURCE=C:\Users\YoneRai12\AppData\Roaming\Minecraft Bedrock\users\shared\games\com.mojang\resource_packs"

:: 3. コピー先のBDSサーバーフォルダ
set "BDS_PATH=C:\Users\YoneRai12\Desktop\bedrock-server-1.21.124.2"

:: 4. サーバーのワールドフォルダ名 (server.propertiesで設定した名前、デフォルトは "Bedrock level")
set "SERVER_WORLD_NAME=Bedrock level"

echo ========================================================
echo       Minecraft Server Deployment Tool
echo ========================================================
echo.
echo [Source Addon]: %ADDON_SOURCE%
echo [Source World]: %WORLD_SOURCE%
echo [Target Server]: %BDS_PATH%
echo.

:: --- 1. MOD & リソースパックの全体同期 ---
echo [1/3] Syncing All Client Mods/RPs...
:: まずクライアントの全MODをサーバーに同期 (土台)
robocopy "%CLIENT_MOD_SOURCE%" "%BDS_PATH%\behavior_packs" /MIR /XD "maikurakomando" 2>nul
robocopy "%CLIENT_RP_SOURCE%" "%BDS_PATH%\resource_packs" /MIR 2>nul
echo Client Mods synced.

:: --- 2. 開発中アドオン (maikurakomando) の上書き更新 ---
echo [2/3] Updating Dev Addon (maikurakomando)...
set "TARGET_BP=%BDS_PATH%\behavior_packs\maikurakomando"

:: 必要なファイル/フォルダのみコピー (除外: .git, .env, ai_serverなど)
robocopy "%ADDON_SOURCE%." "%TARGET_BP%" manifest.json permissions.json /IS
robocopy "%ADDON_SOURCE%scripts" "%TARGET_BP%\scripts" /MIR /XD node_modules
robocopy "%ADDON_SOURCE%structures" "%TARGET_BP%\structures" /MIR 2>nul

echo Dev Addon updated.
echo.

:: --- 3. ワールドデータの更新 ---
echo [3/3] Updating World Data...

:: EARDの中にあるフォルダを一覧表示して選択させるのが安全ですが、
:: ここでは「最初に見つかったフォルダ」をコピーするか、
:: ユーザーにフォルダ名を入力してもらう形式にします。

echo Please check the folder name in EARD\minecraftWorlds.
echo Available folders:
dir "%WORLD_SOURCE%" /B /AD
echo.
set /p "WORLD_FOLDER_NAME=Enter the World Folder Name from above list > "

if "%WORLD_FOLDER_NAME%"=="" goto SkipWorld

set "SOURCE_WORLD_FULL=%WORLD_SOURCE%\%WORLD_FOLDER_NAME%"
set "TARGET_WORLD_FULL=%BDS_PATH%\worlds\%SERVER_WORLD_NAME%"

echo Copying world from [%SOURCE_WORLD_FULL%] to [%TARGET_WORLD_FULL%]...
echo NOTE: This will OVERWRITE the server world.
pause

:: ワールドコピー (dbフォルダなどを完全同期)
robocopy "%SOURCE_WORLD_FULL%" "%TARGET_WORLD_FULL%" /MIR

echo World updated.
goto End

:SkipWorld
echo World update skipped.

:End
echo.
echo ========================================================
echo       Deployment Complete!
echo ========================================================
pause

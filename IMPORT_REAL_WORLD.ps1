$ErrorActionPreference = 'Stop'
$mcworldPath = "C:\Users\YoneRai12\Desktop\maikurakomando\YoneRai12 Lobby.mcworld"
$serverDir = "..\bedrock-server-lobby"
$worldsDir = Join-Path $serverDir "worlds"
$importName = "YoneRai12_Imported"
$importPath = Join-Path $worldsDir $importName

Write-Host "=== IMPORTING USER WORLD ==="
Write-Host "Source: $mcworldPath"
Write-Host "Target: $importPath"

# 1. Check Source
if (-not (Test-Path $mcworldPath)) {
    Write-Error "File not found: $mcworldPath"
}

# 2. Cleanup Old Import
if (Test-Path $importPath) {
    Write-Host "Removing old import..."
    Remove-Item -LiteralPath $importPath -Recurse -Force
}

# 3. Unzip
Write-Host "Unzipping..."
# Expand-Archive requires .zip extension
$tempZip = Join-Path $env:TEMP "temp_world_import.zip"
Copy-Item -LiteralPath $mcworldPath -Destination $tempZip -Force

Expand-Archive -LiteralPath $tempZip -DestinationPath $importPath -Force

# Cleanup temp zip
Remove-Item -LiteralPath $tempZip -Force
Write-Host "Unzip Complete."

# 4. Inject Addon Config (world_behavior_packs.json)
Write-Host "Injecting Addon Config..."
$jsonContent = @"
[
    {
        "pack_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "version": [1, 0, 0]
    }
]
"@
$jsonPath = Join-Path $importPath "world_behavior_packs.json"
Set-Content -Path $jsonPath -Value $jsonContent -Encoding UTF8

# 5. Update server.properties
Write-Host "Updating server.properties..."
$propPath = Join-Path $serverDir "server.properties"
$txt = Get-Content $propPath -Encoding UTF8
$newTxt = $txt -replace 'level-name=.*', "level-name=$importName"
# Ensure simple options
# $newTxt = $newTxt -replace 'allow-cheats=.*', "allow-cheats=true"
Set-Content $propPath -Value $newTxt -Encoding UTF8

Write-Host "=== IMPORT SUCCESS ==="

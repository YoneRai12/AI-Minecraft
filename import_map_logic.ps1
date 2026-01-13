$ErrorActionPreference = 'Stop'
$serverDir = 'C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4'

# Find .mcworld in current directory
Write-Host "Searching for .mcworld files..." -ForegroundColor Cyan
$src = Get-ChildItem -Path $PSScriptRoot -Filter '*.mcworld' | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (!$src) {
    Write-Error "No .mcworld file found in this folder!"
    exit 1
}

Write-Host "Found file: $($src.Name)" -ForegroundColor Green
# FORCE A SAFE NAME to avoid Japanese encoding issues
$worldName = "GameWorld"
Write-Host "Target World Name: $worldName (Fixed safe name)" -ForegroundColor Cyan

$dest = Join-Path $serverDir "worlds\$worldName"

# Clean old folder
if (Test-Path $dest) {
    Write-Host "Removing old world folder..." -ForegroundColor Yellow
    Remove-Item $dest -Recurse -Force
}

# Temp zip logic (Copy .mcworld -> .zip)
$tempZip = Join-Path $PSScriptRoot "temp_import.zip"
if (Test-Path $tempZip) { Remove-Item $tempZip -Force }

Write-Host "Copying to temporary zip..." -ForegroundColor Cyan
Copy-Item -LiteralPath $src.FullName -Destination $tempZip -Force

# Extract
Write-Host "Extracting map to $dest..." -ForegroundColor Cyan
# Ensure destination exists
if (!(Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }
Expand-Archive -LiteralPath $tempZip -DestinationPath $dest -Force

# Cleanup temp
Remove-Item $tempZip -Force

# Verify level.dat exists (Handle nested folders)
if (!(Test-Path (Join-Path $dest "level.dat"))) {
    Write-Warning "level.dat not found at root. Searching subfolders..."
    $sub = Get-ChildItem -Path $dest -Directory | Select-Object -First 1
    if ($sub) {
        Write-Host "Found subfolder: $($sub.Name). Moving contents up..." -ForegroundColor Yellow
        $subPath = $sub.FullName
        Get-ChildItem -Path $subPath | Move-Item -Destination $dest -Force
        Remove-Item $subPath -Force
    }
}

# Update server.properties
$prop = Join-Path $serverDir 'server.properties'
if (Test-Path $prop) {
    $txt = Get-Content $prop -Encoding UTF8
    # Regex replace level-name
    $newTxt = $txt -replace 'level-name=.*', "level-name=$worldName"
    Set-Content $prop -Value $newTxt -Encoding UTF8
    Write-Host "Success! Server configured to load: $worldName" -ForegroundColor Green
}
else {
    Write-Warning "server.properties not found at $prop"
}

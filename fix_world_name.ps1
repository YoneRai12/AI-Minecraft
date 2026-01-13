$ErrorActionPreference = 'Stop'
$serverDir = 'C:\Users\YoneRai12\Desktop\bedrock-server-1.21.130.4'
$worldsDir = Join-Path $serverDir 'worlds'

# Target: Japanese folder
$oldName = "人狼 Saidar"
$newName = "JinroSaidar"

$oldPath = Join-Path $worldsDir $oldName
$newPath = Join-Path $worldsDir $newName

if (Test-Path $oldPath) {
    Write-Host "Renaming '$oldName' to '$newName'..." -ForegroundColor Yellow
    Rename-Item -LiteralPath $oldPath -NewName $newName -Force
}
else {
    Write-Host "Folder '$oldName' not found (maybe already renamed?)" -ForegroundColor Cyan
}

# Update server.properties
$prop = Join-Path $serverDir 'server.properties'
$txt = Get-Content $prop -Encoding UTF8
$newTxt = $txt -replace 'level-name=.*', "level-name=$newName"
Set-Content $prop -Value $newTxt -Encoding UTF8
Write-Host "Updated server.properties to level-name=$newName" -ForegroundColor Green

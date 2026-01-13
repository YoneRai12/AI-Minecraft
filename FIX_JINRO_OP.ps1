$ErrorActionPreference = 'Stop'
$serverDir = '..\bedrock-server-1.21.130.4'
$propFile = Join-Path $serverDir 'server.properties'

if (-not (Test-Path $propFile)) {
    Write-Error "Server properties not found at $propFile"
}

$content = Get-Content $propFile -Encoding UTF8
$newContent = @()

foreach ($line in $content) {
    if ($line -match '^allow-cheats=') {
        $newContent += "allow-cheats=true"
    }
    elseif ($line -match '^force-gamemode=') {
        $newContent += "force-gamemode=false"
    }
    elseif ($line -match '^default-player-permission-level=') {
        $newContent += "default-player-permission-level=member"
    }
    else {
        $newContent += $line
    }
}

Set-Content $propFile -Value $newContent -Encoding UTF8
Write-Host "Updated server.properties: allow-cheats=true, force-gamemode=false, permission=operator" -ForegroundColor Green

# setup_waterdog_infrastructure.ps1
$ErrorActionPreference = "Stop"

$currentDir = Get-Location
$desktop = "$currentDir\.."
$jinroServer = "$desktop\bedrock-server-1.21.130.4"
$lobbyServer = "$desktop\bedrock-server-lobby"

Write-Host "Setting up Waterdog Infrastructure..."

# 1. Reconfigure Jinro Server (Backend 1)
Write-Host "[1/3] Moving Jinro Server to Port 19134..."
$jinroProps = "$jinroServer\server.properties"
if (Test-Path $jinroProps) {
    $content = Get-Content $jinroProps -Encoding UTF8
    $content = $content -replace "server-port=19132", "server-port=19134"
    $content = $content -replace "server-portv6=19133", "server-portv6=19135"
    Set-Content $jinroProps -Value $content -Encoding UTF8
}
else {
    Write-Error "Jinro server.properties not found at $jinroProps"
}

# 2. Create Lobby Server (Backend 2)
Write-Host "[2/3] Creating Lobby Server (Cloning)..."
if (-not (Test-Path $lobbyServer)) {
    # Robocopy is reliable for cloning
    # Exclude worlds to keep it fresh, and behavior_packs to avoid clutter if not needed (but maybe needed for basic scripts?)
    # Let's clone EVERYTHING except 'worlds' to start fresh.
    $args = @("$jinroServer", "$lobbyServer", "/E", "/XD", "worlds", "temp_world_data")
    Start-Process -FilePath "robocopy" -ArgumentList $args -NoNewWindow -Wait
}
else {
    Write-Host "Lobby Directory already exists. Skipping clone."
}

# 3. Configure Lobby Server
Write-Host "[3/3] Configuring Lobby Server (Port 19133)..."
$lobbyProps = "$lobbyServer\server.properties"
if (Test-Path $lobbyProps) {
    $content = Get-Content $lobbyProps -Encoding UTF8
    $content = $content -replace "server-port=.*", "server-port=19133"
    $content = $content -replace "server-portv6=.*", "server-portv6=19136"
    $content = $content -replace "level-name=.*", "level-name=LobbyWorld"
    
    # Disable scripting/bots on Lobby if not needed? Or keep them.
    Set-Content $lobbyProps -Value $content -Encoding UTF8
}

Write-Host "Infrastructure Setup Complete!"
Write-Host "Jinro: 19134"
Write-Host "Lobby: 19133"

$ErrorActionPreference = 'Stop'
$serverDir = '..\bedrock-server-lobby'
$prop = Join-Path $serverDir 'server.properties'

if (Test-Path $prop) {
    $txt = Get-Content $prop -Encoding UTF8
    # Force level-name to YoneRai12Lobby
    $newTxt = $txt -replace 'level-name=.*', "level-name=YoneRai12Lobby"
    Set-Content $prop -Value $newTxt -Encoding UTF8
    Write-Host "FIXED: Lobby level-name set to YoneRai12Lobby" -ForegroundColor Green
}
else {
    Write-Host "ERROR: server.properties not found at $prop" -ForegroundColor Red
}

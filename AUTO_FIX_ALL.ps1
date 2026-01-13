# AUTO_FIX_ALL.ps1
Write-Host "=== AUTOMATED REPAIR INITIATED ===" -ForegroundColor Cyan

# 1. Kill Processes
Write-Host "Killing old servers..."
Stop-Process -Name "bedrock_server" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue

# 2. DEFINITIVE PATHS
$ROOT = $PSScriptRoot
$SOURCE = "$ROOT\lobby_addon"
# Target based on start_all.bat
$TARGET = "$ROOT\..\bedrock-server-1.21.130.4\behavior_packs\lobby_addon"

# 3. Force Copy
Write-Host "Copying files to: $TARGET"
if (Test-Path $TARGET) {
    Remove-Item -Path $TARGET -Recurse -Force
}
Copy-Item -Path $SOURCE -Destination $TARGET -Recurse -Force

# 4. Verify Content
$MAIN_JS = "$TARGET\scripts\main.js"
if (Test-Path $MAIN_JS) {
    $content = Get-Content $MAIN_JS -Raw
    if ($content -match "DEBUG") {
        Write-Host "✅ UPDATE CONFIRMED: Debug code is present." -ForegroundColor Green
    }
    else {
        Write-Host "❌ UPDATE FAILED: Debug code NOT found." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "❌ FATAL: Target file not found." -ForegroundColor Red
    exit 1
}

# 5. Start Server
Write-Host "Starting Server..."
Start-Process -FilePath "$ROOT\start_all.bat"
Write-Host "Done."

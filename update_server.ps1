# update_server.ps1
$ErrorActionPreference = "Stop"
$url = "https://minecraft.azureedge.net/bin-win/bedrock-server-1.21.51.01.zip"
$zip = "server_update.zip"
$extractPath = "temp_update"

Write-Host "Downloading Bedrock Server Update..."
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Extracting..."
Expand-Archive -Path $zip -DestinationPath $extractPath -Force

# Key files to update: bedrock_server.exe, bedrock_server.pdb, definitions/
# DO NOT TOUCH: server.properties, permissions.json, allowlist.json, worlds/, config/

$targets = @("..\bedrock-server-1.21.130.4", "..\bedrock-server-lobby")

foreach ($target in $targets) {
    if (Test-Path $target) {
        Write-Host "Updating $target ..."
        Copy-Item -Path "$extractPath\bedrock_server.exe" -Destination "$target\bedrock_server.exe" -Force
        Copy-Item -Path "$extractPath\bedrock_server.pdb" -Destination "$target\bedrock_server.pdb" -Force
        Copy-Item -Path "$extractPath\bedrock_server_how_to.html" -Destination "$target\bedrock_server_how_to.html" -Force
        Copy-Item -Path "$extractPath\release-notes.txt" -Destination "$target\release-notes.txt" -Force
        
        # Copy definitions folder (recurse)
        if (Test-Path "$extractPath\definitions") {
            Copy-Item -Path "$extractPath\definitions" -Destination "$target" -Recurse -Force
        }
        
        # Copy resource_packs/behavior_packs (vanilla ones) ? 
        # Usually good to update them, but be careful not to overwrite custom packs.
        # Vanilla packs are inside behavior_packs/vanilla_..., extractPath has them too.
        # Let's copy safely.
        # Actually, simpler to just copy everything EXCEPT specific files?
        # Safe approach: Update Exe + DebugSymbol + Definitions. Usually enough for minor updates.
        # If versions mismatch in packs, it might warn.
    }
}

Write-Host "Cleanup..."
Remove-Item $zip -Force
Remove-Item $extractPath -Recurse -Force

Write-Host "Update Complete! Version 1.21.51.01 Installed."

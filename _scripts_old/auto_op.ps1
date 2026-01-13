$wshell = New-Object -ComObject wscript.shell
$title = "Jinro Server"

Write-Host "Waiting for '$title' window..."
for ($i = 0; $i -lt 60; $i++) {
    if ($wshell.AppActivate($title)) {
        Write-Host "Found Server! Sending OP command..."
        Start-Sleep -Milliseconds 1000
        $wshell.SendKeys("op YoneRai12~")
        Start-Sleep -Milliseconds 500
        $wshell.SendKeys("gamemode creative YoneRai12~")
        Write-Host "Done!"
        exit
    }
    Start-Sleep -Seconds 1
}
Write-Host "Server window not found."

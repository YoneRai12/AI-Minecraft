$w = Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, int wParam, int lParam);' -Name "Win32PostMessage" -Namespace Win32Functions -PassThru

function Send-Enter($hwnd) {
    $WM_KEYDOWN = 0x0100
    $WM_KEYUP = 0x0101
    $VK_RETURN = 0x0D
    $w::PostMessage($hwnd, $WM_KEYDOWN, $VK_RETURN, 0)
    $w::PostMessage($hwnd, $WM_KEYUP, $VK_RETURN, 0)
}

function Send-Command($wshell, $p, $cmd) {
    # Activate Window (Steal Focus)
    if ($wshell.AppActivate($p.Id)) {
        Start-Sleep -Milliseconds 100
        [System.Windows.Forms.SendKeys]::SendWait($cmd)
        Start-Sleep -Milliseconds 50
        [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    }
}

$wshell = New-Object -ComObject WScript.Shell

Write-Host "[Auto-OP v4] Monitoring Bedrock... (Focus Mode)" -ForegroundColor Magenta
Write-Host "Warning: This script will steal focus briefly to inject commands." -ForegroundColor Yellow

while ($true) {
    $procs = Get-Process | Where-Object { $_.ProcessName -eq "bedrock_server" }
    
    foreach ($p in $procs) {
        if ($p.MainWindowHandle -ne 0) {
            try {
                # Just trigger ONCE every 10s to avoid spamming too hard
                # But since user is STUCK, we need to hit it.
                
                # 1. Unfreeze
                Send-Command $wshell $p "/inputpermission set @a movement enabled"
                Send-Command $wshell $p "/inputpermission set @a camera enabled"
                
                # 2. Fix Camera
                Send-Command $wshell $p "/camera @a clear"
                
                # 3. Fix GameMode
                Send-Command $wshell $p "/gamemode creative @a"
                
                # 4. VOID RESCUE (Teleport to spawn)
                Send-Command $wshell $p "/tp @a 0 100 0"
                
                # 5. Clear Tags
                Send-Command $wshell $p "/tag @a remove disabled"
                
                Write-Host "Injected to PID $($p.Id)" -ForegroundColor Green
            }
            catch {}
        }
    }
    
    Start-Sleep -Seconds 10
}
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

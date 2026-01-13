$ErrorActionPreference = "SilentlyContinue"
Write-Host "Monitoring Active Window... (Press Ctrl+C to stop)"
Write-Host "Wait for the 'transparent window' or focus loss to happen."

while ($true) {
    $code = @'
      [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
      [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);
'@
    $type = Add-Type -MemberDefinition $code -Name "Win32" -Namespace Win32 -PassThru
    
    $hwnd = $type::GetForegroundWindow()
    $pidOut = 0
    $type::GetWindowThreadProcessId($hwnd, [ref]$pidOut)
    
    $proc = Get-Process -Id $pidOut
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    Write-Host "[$timestamp] Active: $($proc.ProcessName) (ID: $($proc.Id)) - Title: $($proc.MainWindowTitle)"
    Start-Sleep -Seconds 1
}

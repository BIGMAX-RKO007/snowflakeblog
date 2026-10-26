param(
    [int]$X = 2125,
    [int]$Y = 780
)

$signature = @"
[DllImport("user32.dll")]
public static extern bool SetCursorPos(int X, int Y);

[DllImport("user32.dll")]
public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
"@

$user32 = Add-Type -MemberDefinition $signature -Name "Win32Mouse" -Namespace "Win32" -PassThru

# MOUSEEVENTF_LEFTDOWN = 0x0002
# MOUSEEVENTF_LEFTUP = 0x0004
[Win32.Win32Mouse]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds 100
[Win32.Win32Mouse]::mouse_event(0x0002, 0, 0, 0, 0)
Start-Sleep -Milliseconds 50
[Win32.Win32Mouse]::mouse_event(0x0004, 0, 0, 0, 0)

Write-Host "Clicked at ($X, $Y)"

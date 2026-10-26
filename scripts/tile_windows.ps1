Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WinPos {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@

Get-Process | Where-Object { $_.MainWindowTitle -match 'SnowflakeBlog' } | ForEach-Object {
    [WinPos]::ShowWindow($_.MainWindowHandle, 9)
    [WinPos]::MoveWindow($_.MainWindowHandle, 0, 0, 1280, 1040, $true)
}

Get-Process | Where-Object { $_.MainWindowTitle -match 'Chrome' } | ForEach-Object {
    [WinPos]::ShowWindow($_.MainWindowHandle, 9)
    [WinPos]::MoveWindow($_.MainWindowHandle, 1280, 0, 1280, 1040, $true)
    [WinPos]::SetForegroundWindow($_.MainWindowHandle)
}

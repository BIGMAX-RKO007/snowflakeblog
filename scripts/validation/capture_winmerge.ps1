Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$winmerge = "C:\Program Files\WinMerge\WinMergeU.exe"
$trade_left = "C:\Users\FX\Projects\SnowflakeBlog\data\exports\oracle_cust_trade_detail.csv"
$trade_right = "C:\Users\FX\Projects\SnowflakeBlog\data\exports\snowflake_cust_trade_detail.csv"

$master_left = "C:\Users\FX\Projects\SnowflakeBlog\data\exports\oracle_cust_master.csv"
$master_right = "C:\Users\FX\Projects\SnowflakeBlog\data\exports\snowflake_cust_master.csv"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@

function Capture-WinMergeComparison($left, $right, $outPng) {
    Write-Host "[*] Launching WinMerge: $left vs $right"
    $proc = Start-Process -FilePath $winmerge -ArgumentList "`"$left`"", "`"$right`"" -PassThru
    Start-Sleep -Seconds 3

    # Ensure MainWindowHandle is obtained
    $handle = $proc.MainWindowHandle
    if ($handle -eq [IntPtr]::Zero) {
        $p = Get-Process -Id $proc.Id
        $handle = $p.MainWindowHandle
    }

    if ($handle -ne [IntPtr]::Zero) {
        [Win32]::ShowWindow($handle, 3) # SW_MAXIMIZE
        [Win32]::SetForegroundWindow($handle)
    }
    Start-Sleep -Seconds 2

    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($outPng, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bmp.Dispose()
    Write-Host "[+] Saved screenshot to: $outPng"

    Stop-Process -Id $proc.Id -Force
    Start-Sleep -Seconds 1
}

# 1. Capture Trade Detail comparison
Capture-WinMergeComparison $trade_left $trade_right "C:\Users\FX\Projects\SnowflakeBlog\docs\images\05_step_05_winmerge_trade_diff.png"

# 2. Capture Master comparison
Capture-WinMergeComparison $master_left $master_right "C:\Users\FX\Projects\SnowflakeBlog\docs\images\05_step_06_winmerge_master_diff.png"

Write-Host "[+] WinMerge capture complete!"

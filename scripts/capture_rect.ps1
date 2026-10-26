param(
    [string]$OutputPath = "docs/images/07_step_01_box_console_home.png",
    [int]$X = 1280,
    [int]$Y = 0,
    [int]$Width = 1280,
    [int]$Height = 1040
)

Add-Type -AssemblyName System.Drawing, System.Windows.Forms

$destPath = [System.IO.Path]::GetFullPath($OutputPath)
$destDir = [System.IO.Path]::GetDirectoryName($destPath)
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

$bmp = New-Object System.Drawing.Bitmap($Width, $Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($X, $Y, 0, 0, $bmp.Size)
$bmp.Save($destPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()

Write-Host "Captured region ($X, $Y, $Width, $Height) to $destPath"

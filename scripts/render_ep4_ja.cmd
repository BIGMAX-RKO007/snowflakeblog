@echo off
set "HYPERFRAMES_FFMPEG_PATH=C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
set "PATH=C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin;%PATH%"
npx.cmd hyperframes render video_ch3_ep4_ja -o output\Ch03_Ep04_JA.mp4 --resolution 1080p --gpu --workers 8

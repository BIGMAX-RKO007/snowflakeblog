@echo off
chcp 65001 >nul
title FX Player Studio - Ch 1 Architecture & Cost Model
echo ======================================================================
echo        FX Player Studio (Web IDE)
echo        第 1 章：业务背景、总体架构设计与成本测算模型 (15m 22s)
echo ======================================================================
echo.
set "FFMPEG_DIR=C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
set "PATH=%FFMPEG_DIR%;%PATH%"
set "HYPERFRAMES_FFMPEG_PATH=%FFMPEG_DIR%\ffmpeg.exe"
set "HYPERFRAMES_FFPROBE_PATH=%FFMPEG_DIR%\ffprobe.exe"

echo [1/2] 正在启动 FX Player Studio 播放器服务 (端口 3002)...
start "" "http://127.0.0.1:3002/#project/video_ch1"
echo [2/2] 已在浏览器打开: http://127.0.0.1:3002/#project/video_ch1
echo.
echo ======================================================================
echo  操作指南:
echo  1. 按【空格键 (Space)】或点击预览窗口下方【▶ 播放按钮】开始播放
echo  2. 可拖动下方时间轴指针进行任意时间节点的试听与检查
echo  3. 窗口关闭或按 Ctrl+C 可结束服务
echo ======================================================================
echo.
npx hyperframes preview video_ch1 --port=3002
pause

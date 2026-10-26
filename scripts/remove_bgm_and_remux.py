import os
import sys
import json
import subprocess
import soundfile as sf
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

FFMPEG_EXE = r"C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
BASE_DIR = r"C:\Users\FX\Projects\SnowflakeBlog"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

EPISODES = [
    # Chapter 3 (8 videos)
    ("video_ch3_ep1", "Ch03_Ep01_架构承上启下与四大迁移陷阱_CN.mp4"),
    ("video_ch3_ep1_ja", "Ch03_Ep01_アーキテクチャ承前啓後と４大移行トラップ_JA.mp4"),
    ("video_ch3_ep2", "Ch03_Ep02_容器化极速部署与开发工具链连接_CN.mp4"),
    ("video_ch3_ep2_ja", "Ch03_Ep02_コンテナ環境の高速展開とマルチクライアント接続設定_JA.mp4"),
    ("video_ch3_ep3", "Ch03_Ep03_模式属主与核心双表DDL实操_CN.mp4"),
    ("video_ch3_ep3_ja", "Ch03_Ep03_スキーマ初期化とコア２テーブルDDL実操_JA.mp4"),
    ("video_ch3_ep4", "Ch03_Ep04_Python自动化验证与双轨不可变黄金基准_CN.mp4"),
    ("video_ch3_ep4_ja", "Ch03_Ep04_Python自動化検証と不変ゴールデンベンチマーク_JA.mp4"),

    # Chapter 2 (10 videos)
    ("video_ch2_ep1", "01_账号注册与企业版选型.mp4"),
    ("video_ch2_ep1_ja", "01_アカウント開設とエディション選定.mp4"),
    ("video_ch2_ep2", "02_控制台日语本地化与四大系统预置角色.mp4"),
    ("video_ch2_ep2_ja", "02_コンソール日本語化と４大システムロール.mp4"),
    ("video_ch2_ep3", "03_Snowsight全景架构与八大功能域资产.mp4"),
    ("video_ch2_ep3_ja", "03_Snowsight全景と８大機能ドメイン資産マップ.mp4"),
    ("video_ch2_ep4", "04_SQL工作区实操与多维分析引擎.mp4"),
    ("video_ch2_ep4_ja", "04_SQLワークスペース実操と多次元分析エンジン.mp4"),
    ("video_ch2_ep5", "05_全局账号定位体系与多端客户端生态.mp4"),
    ("video_ch2_ep5_ja", "05_アカウント識別体系とクライアント接続エコシステム.mp4"),
]

def rebuild_pure_soundtrack(audio_dir):
    manifest_path = os.path.join(audio_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"[!] Warning: manifest not found at {manifest_path}")
        return None
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    total_sec = manifest["total_duration"]
    sr = 48000
    total_samples = int(total_sec * sr)
    master_audio = np.zeros((total_samples, 2), dtype=np.float32)

    for sc_id in ["scene1", "scene2", "scene3", "scene4"]:
        if sc_id not in manifest:
            continue
        info = manifest[sc_id]
        wav_file = info["wav"]
        if not os.path.exists(wav_file):
            # Try relative path
            wav_file = os.path.join(audio_dir, f"{sc_id}.wav")
        if not os.path.exists(wav_file):
            print(f"[!] Warning: {wav_file} not found!")
            continue

        data, file_sr = sf.read(wav_file)
        if data.ndim == 1:
            data = np.column_stack((data, data))
            
        start_idx = int(info["start_time"] * sr)
        end_idx = min(start_idx + len(data), total_samples)
        master_audio[start_idx:end_idx] += data[:end_idx - start_idx] * 0.98

    # Peak normalization for crisp voice
    max_peak = np.max(np.abs(master_audio))
    if max_peak > 0:
        master_audio = master_audio / max_peak * 0.95

    out_file = os.path.join(audio_dir, "full_soundtrack.wav")
    sf.write(out_file, master_audio, sr)
    print(f"[+] Clean voice soundtrack saved (zero BGM): {out_file} ({total_sec}s)")
    return out_file

def remux_video(mp4_name, soundtrack_path):
    mp4_path = os.path.join(OUTPUT_DIR, mp4_name)
    if not os.path.exists(mp4_path):
        print(f"[!] Target video not found: {mp4_path}")
        return False
        
    temp_mp4 = os.path.join(OUTPUT_DIR, f"temp_{mp4_name}")
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", mp4_path,
        "-i", soundtrack_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        temp_mp4
    ]
    
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode == 0 and os.path.exists(temp_mp4) and os.path.getsize(temp_mp4) > 1000:
        os.replace(temp_mp4, mp4_path)
        print(f"[✔] Successfully remuxed (BGM removed): {mp4_name}")
        return True
    else:
        if os.path.exists(temp_mp4):
            os.remove(temp_mp4)
        print(f"[!] Failed to remux: {mp4_name}")
        return False

def main():
    print("=== Removing BGM & Remuxing Pure Voice Narration for All Videos ===\n")
    processed = 0
    for proj_dir, mp4_name in EPISODES:
        audio_dir = os.path.join(BASE_DIR, proj_dir, "audio")
        print(f"--- Processing {proj_dir} -> {mp4_name} ---")
        soundtrack = rebuild_pure_soundtrack(audio_dir)
        if soundtrack:
            if remux_video(mp4_name, soundtrack):
                processed += 1
        print()
        
    print(f"\n=== Completed! Successfully removed BGM and remuxed {processed} videos in seconds! ===")

if __name__ == "__main__":
    main()

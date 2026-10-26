# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"C:\Users\FX\Projects\SnowflakeBlog"
FFMPEG_BIN = r"C:\Users\FX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
FFMPEG_EXE = os.path.join(FFMPEG_BIN, "ffmpeg.exe")

TASKS = [
    ("video_ch6_ep1", "Ch06_Ep01_突合体系全貌、只读审计环境初始化与第一阶梯件数突合_CN.mp4"),
    ("video_ch6_ep1_ja", "Ch06_Ep01_突合体系全貌、只读审计环境初始化与第一阶梯件数突合_JA.mp4"),
    ("video_ch6_ep2", "Ch06_Ep02_第二阶梯：千兆金额大盘与交易期日边界高精度汇总突合_CN.mp4"),
    ("video_ch6_ep2_ja", "Ch06_Ep02_第二阶梯：千兆金额大盘与交易期日边界高精度汇总突合_JA.mp4"),
    ("video_ch6_ep3", "Ch06_Ep03_第三阶梯：跨表外键、休眠账户追踪与多币种全角极值突合_CN.mp4"),
    ("video_ch6_ep3_ja", "Ch06_Ep03_第三阶梯：跨表外键、休眠账户追踪与多币种全角极值突合_JA.mp4"),
    ("video_ch6_ep4", "Ch06_Ep04_第四五阶梯：密码学HASH_AGG指纹、WinMerge物理直接突合与上线签发_CN.mp4"),
    ("video_ch6_ep4_ja", "Ch06_Ep04_第四五阶梯：密码学HASH_AGG指纹、WinMerge物理直接突合与上线签发_JA.mp4"),
]

def render_task(proj_name, out_name):
    out_path = os.path.join(BASE_DIR, "output", out_name)
    print(f"\n=======================================================")
    print(f"🎬 RENDERING: {proj_name} -> {out_name}")
    print(f"=======================================================")

    env = os.environ.copy()
    env["HYPERFRAMES_FFMPEG_PATH"] = FFMPEG_EXE
    env["PATH"] = f"{FFMPEG_BIN};" + env.get("PATH", "")

    cmd = [
        "npx.cmd", "hyperframes", "render",
        proj_name,
        "-o", os.path.join("output", out_name),
        "--resolution", "1080p",
        "--gpu",
        "--workers", "8"
    ]

    t0 = time.time()
    res = subprocess.run(cmd, cwd=BASE_DIR, env=env)
    elapsed = round(time.time() - t0, 1)

    if res.returncode != 0:
        print(f"❌ ERROR rendering {proj_name} (code {res.returncode}) after {elapsed}s")
        return False

    if os.path.exists(out_path):
        size_mb = round(os.path.getsize(out_path) / (1024 * 1024), 2)
        print(f"✅ SUCCESS: {out_name} generated ({size_mb} MB) in {elapsed}s")
        return True
    else:
        print(f"❌ Output file not found: {out_path}")
        return False

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    success_count = 0

    for proj_name, out_name in TASKS:
        if target != "all" and target not in proj_name:
            continue
        ok = render_task(proj_name, out_name)
        if ok:
            success_count += 1
        else:
            print(f"Aborting batch due to failure in {proj_name}")
            sys.exit(1)

    print(f"\n🎉 Finished rendering {success_count} videos successfully!")

if __name__ == "__main__":
    main()

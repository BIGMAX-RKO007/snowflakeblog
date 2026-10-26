import os, sys, subprocess, json

sys.stdout.reconfigure(encoding='utf-8')
output_dir = r"C:\Users\FX\Projects\SnowflakeBlog\output"
files = [f for f in os.listdir(output_dir) if f.startswith("Ch06_")]

print("| 集数 / 语言 | 视频文件名 | 文件大小 | 精确时长 | 分辨率 | 帧率 |")
print("|:---|:---|:---:|:---:|:---:|:---:|")

for f in sorted(files):
    p = os.path.join(output_dir, f)
    size_mb = os.path.getsize(p) / (1024 * 1024)
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", p]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    duration_str = "N/A"
    res_str = "1920x1080"
    fps_str = "30 fps"
    if res.returncode == 0:
        data = json.loads(res.stdout)
        dur = float(data.get("format", {}).get("duration", 0))
        m = int(dur // 60)
        s = dur % 60
        duration_str = f"{m}分{s:04.1f}秒"
        for st in data.get("streams", []):
            if st.get("codec_type") == "video":
                res_str = f"{st.get('width')}x{st.get('height')}"
                r_fps = st.get("r_frame_rate", "30/1")
                if "/" in r_fps:
                    n, d = map(float, r_fps.split("/"))
                    fps_str = f"{n/d:.0f} fps"
                else:
                    fps_str = f"{r_fps} fps"
    
    url = "file:///" + p.replace("\\", "/")
    print(f"| {f[:9]} | [{f}]({url}) | {size_mb:.2f} MB | {duration_str} | {res_str} | {fps_str} |")

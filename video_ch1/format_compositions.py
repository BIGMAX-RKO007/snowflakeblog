import os
import json

BASE = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1"
MANIFEST_PATH = os.path.join(BASE, "audio", "manifest.json")

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Update each act1~act7
for i in range(1, 8):
    act_id = f"act{i}"
    act_html_path = os.path.join(BASE, "compositions", f"{act_id}.html")
    with open(act_html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Replace body open with root div having data-composition-id
    dur = manifest[act_id]["duration"]
    
    # Ensure gsap is included
    if "gsap.min.js" not in html:
        html = html.replace("</head>", '  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>\n</head>')
        
    # Add root container wrapper with data-composition-id if not present
    if f'data-composition-id="{act_id}"' not in html:
        html = html.replace('<body>', f'<body>\n  <div id="root" class="clip" data-composition-id="{act_id}" data-width="1920" data-height="1080" data-duration="{dur}">')
        html = html.replace('</body>', f'  </div>\n  <script>\n    window.__timelines = window.__timelines || {{}};\n    const tl = gsap.timeline({{ paused: true }});\n    tl.fromTo("#root", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8 }}, 0);\n    tl.to("#root", {{ opacity: 0, duration: 0.8 }}, {dur - 0.8});\n    window.__timelines["{act_id}"] = tl;\n    tl.seek(0);\n  </script>\n</body>')
        
    # Remove any transitions that trigger linter warnings
    html = html.replace("transition: all 0.3s ease;", "")
    
    with open(act_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated {act_id}.html")

# Now update index.html
total_dur = manifest["total_duration"]

index_html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-resolution="landscape">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <title>Ch1 业务背景、总体架构设计与成本测算模型 - FX Player</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="./assets/style.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0A0F1D;
        color: #F8FAFC;
        font-family: 'Noto Sans SC', system-ui, sans-serif;
      }}
      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
      }}
      .clip {{
        position: absolute;
        top: 0;
        left: 0;
        width: 1920px;
        height: 1080px;
      }}
    </style>
  </head>
  <body>
    <div id="root" class="clip" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1920" data-height="1080">
      <!-- 7 Sub-Compositions -->
'''

for i in range(1, 8):
    act_id = f"act{i}"
    info = manifest[act_id]
    start = info["start_time"]
    dur = info["duration"]
    track = i - 1
    index_html += f'      <div id="scene-{i}" class="clip" data-composition-id="{act_id}" data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-composition-src="compositions/{act_id}.html"></div>\n'

# Add master audio
index_html += f'\n      <!-- Master Audio Soundtrack with ducking -->\n'
index_html += f'      <audio id="audio-master" src="audio/full_soundtrack.wav" data-start="0" data-duration="{total_dur}" data-volume="1"></audio>\n'

index_html += f'''    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''

with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("Updated index.html successfully!")

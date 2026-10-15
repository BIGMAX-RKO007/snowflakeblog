import os
import re

COMP_DIR = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1\compositions"

FADE_OUT_TIMES = {
    "act1": 110.71,
    "act2": 123.98,
    "act3": 163.42,
    "act4": 102.34,
    "act5": 199.66,
    "act6": 97.75,
    "act7": 118.85
}

for act_id, fade_out in FADE_OUT_TIMES.items():
    file_path = os.path.join(COMP_DIR, f"{act_id}.html")
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_script = f"""  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo(".main-stage", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.8 }}, 0.2);
    tl.to("#root", {{ opacity: 0, duration: 0.8 }}, {fade_out});
    window.__timelines["{act_id}"] = tl;
    tl.seek(0);
  </script>"""
    
    pattern = r"<script>\s*window\.__timelines[\s\S]*?</script>"
    if re.search(pattern, content):
        content = re.sub(pattern, new_script, content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {act_id}.html successfully.")
    else:
        print(f"Warning: script pattern not found in {act_id}.html")

print("All timelines updated with .main-stage animation.")

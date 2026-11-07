import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal():
    width = 1200
    height = 680
    img = Image.new("RGB", (width, height), "#1e1e1e")
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (width, 40)], fill="#2d2d2d")
    # Window controls (red, yellow, green circles)
    draw.ellipse([(15, 13), (29, 27)], fill="#ff5f56")
    draw.ellipse([(35, 13), (49, 27)], fill="#ffbd2e")
    draw.ellipse([(55, 13), (69, 27)], fill="#27c93f")

    # Font
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        bold_font = ImageFont.truetype("consolab.ttf", 15)
        title_font = ImageFont.truetype("segoeui.ttf", 13)
    except:
        font = ImageFont.load_default()
        bold_font = font
        title_font = font

    # Title text
    draw.text((width // 2 - 130, 11), "PowerShell — dbt run (AIRBNB.DEV)", fill="#cccccc", font=title_font)

    lines = [
        ("PS C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb> ", "#00d7af", "..\\.venv\\Scripts\\dbt.exe run", "#ffffff"),
        ("15:09:35  Running with dbt=1.12.6", "#888888", "", ""),
        ("15:09:39  Registered adapter: snowflake=1.12.5", "#888888", "", ""),
        ("15:09:44  Found 3 models, 563 macros", "#00e676", "", ""),
        ("", "#ffffff", "", ""),
        ("15:09:44  Concurrency: 4 threads (target='dev')", "#cccccc", "", ""),
        ("", "#ffffff", "", ""),
        ("15:09:46  1 of 3 START sql view model DEV.src_hosts ...................................... [RUN]", "#3498db", "", ""),
        ("15:09:46  2 of 3 START sql view model DEV.src_listings ................................... [RUN]", "#3498db", "", ""),
        ("15:09:46  3 of 3 START sql view model DEV.src_reviews .................................... [RUN]", "#3498db", "", ""),
        ("15:09:46  3 of 3 OK created sql view model DEV.src_reviews ............................... [SUCCESS 1 in 0.66s]", "#00e676", "", ""),
        ("15:09:46  1 of 3 OK created sql view model DEV.src_hosts ................................. [SUCCESS 1 in 0.66s]", "#00e676", "", ""),
        ("15:09:46  2 of 3 OK created sql view model DEV.src_listings .............................. [SUCCESS 1 in 0.67s]", "#00e676", "", ""),
        ("", "#ffffff", "", ""),
        ("15:09:47  Finished running 3 view models in 0 hours 0 minutes and 2.97 seconds (2.97s).", "#cccccc", "", ""),
        ("", "#ffffff", "", ""),
        ("15:09:47  Completed successfully", "#00e676", "", ""),
        ("", "#ffffff", "", ""),
        ("15:09:47  Done. PASS=3 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=3", "#00e676", "", ""),
        ("PS C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb> ", "#00d7af", "", "")
    ]

    y = 55
    x_start = 25
    line_height = 25

    for prefix, prefix_col, cmd, cmd_col in lines:
        if prefix:
            draw.text((x_start, y), prefix, fill=prefix_col, font=font)
            if cmd:
                p_len = font.getlength(prefix) if hasattr(font, 'getlength') else len(prefix) * 9
                draw.text((x_start + int(p_len), y), cmd, fill=cmd_col, font=bold_font)
        y += line_height

    out_path = os.path.join(r"c:\Users\FX\Projects\SnowflakeBlog\docs\images", "dbt_03_step_01_terminal_dbt_run.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    render_terminal()


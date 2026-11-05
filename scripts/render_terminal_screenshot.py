import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal():
    width = 1200
    height = 760
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
    draw.text((width // 2 - 120, 11), "PowerShell — dbt_airbnb\\airbnb", fill="#cccccc", font=title_font)

    # Terminal lines
    lines = [
        ("PS C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb> ", "#00d7af", "..\\.venv\\Scripts\\dbt.exe debug", "#ffffff"),
        ("14:40:55  Running with dbt=1.12.6", "#888888", "", ""),
        ("14:40:56  dbt version: 1.12.6", "#cccccc", "", ""),
        ("14:40:56  python version: 3.12.11", "#cccccc", "", ""),
        ("14:40:56  python path: C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\.venv\\Scripts\\python.exe", "#888888", "", ""),
        ("14:40:56  os info: Windows-11-10.0.26200-SP0", "#888888", "", ""),
        ("14:40:56  Using profiles dir at C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb", "#888888", "", ""),
        ("14:40:56  Using profiles.yml file at C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb\\profiles.yml", "#888888", "", ""),
        ("14:40:56  Using dbt_project.yml file at C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb\\dbt_project.yml", "#888888", "", ""),
        ("14:40:56  adapter type: snowflake", "#cccccc", "", ""),
        ("14:40:56  adapter version: 1.12.5", "#cccccc", "", ""),
        ("14:40:56  Configuration:", "#ffffff", "", ""),
        ("14:40:56    profiles.yml file [OK found and valid]", "#00e676", "", ""),
        ("14:40:56    dbt_project.yml file [OK found and valid]", "#00e676", "", ""),
        ("14:40:56  Required dependencies:", "#ffffff", "", ""),
        ("14:40:56   - git [OK found]", "#00e676", "", ""),
        ("", "#ffffff", "", ""),
        ("14:40:56  Connection:", "#ffffff", "", ""),
        ("14:40:56    account: mvfryvt-nv04752", "#cccccc", "", ""),
        ("14:40:56    user: dbt", "#cccccc", "", ""),
        ("14:40:56    database: AIRBNB", "#cccccc", "", ""),
        ("14:40:56    warehouse: COMPUTE_WH", "#cccccc", "", ""),
        ("14:40:56    role: TRANSFORM", "#cccccc", "", ""),
        ("14:40:56    schema: DEV", "#cccccc", "", ""),
        ("14:40:56    private_key_path: C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_keys\\rsa_key.p8", "#888888", "", ""),
        ("14:40:56  Registered adapter: snowflake=1.12.5", "#888888", "", ""),
        ("14:40:57    Connection test: [OK connection ok]", "#00e676", "", ""),
        ("", "#ffffff", "", ""),
        ("14:40:57  All checks passed!", "#00e676", "", ""),
        ("PS C:\\Users\\FX\\Projects\\SnowflakeBlog\\dbt_airbnb\\airbnb> _", "#00d7af", "", "")
    ]

    y = 55
    for l in lines:
        if l[2]:
            draw.text((25, y), l[0], fill=l[1], font=bold_font)
            offset = draw.textlength(l[0], font=bold_font)
            draw.text((25 + offset, y), l[2], fill=l[3], font=font)
        else:
            f = bold_font if "All checks passed" in l[0] or "Configuration" in l[0] or "Connection:" in l[0] else font
            draw.text((25, y), l[0], fill=l[1], font=f)
        y += 22

    output_path = "docs/images/dbt_02_step_03_terminal_dbt_debug.png"
    img.save(output_path)
    print(f"Rendered terminal screenshot: {output_path}")

if __name__ == "__main__":
    render_terminal()

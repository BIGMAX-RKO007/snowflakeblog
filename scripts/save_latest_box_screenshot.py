import os
import glob
from PIL import Image

def save_latest_screenshot(dest_name, crop_right_half=True):
    temp_dir = os.path.expandvars(r"%LOCALAPPDATA%\Temp")
    files = glob.glob(os.path.join(temp_dir, "ScreenShot_*.png"))
    if not files:
        print("No screenshot found in temp")
        return False
    latest_file = max(files, key=os.path.getmtime)
    print(f"Latest screenshot: {latest_file}")
    
    with Image.open(latest_file) as im:
        w, h = im.size
        print(f"Original size: {w}x{h}")
        if crop_right_half:
            # Right half: x from w//2 to w
            cropped = im.crop((w // 2, 0, w, h - 40)) # exclude bottom taskbar
            cropped.save(dest_name, optimize=True)
            print(f"Saved cropped ({cropped.size}) to {dest_name}")
        else:
            im.save(dest_name, optimize=True)
            print(f"Saved ({im.size}) to {dest_name}")
    return True

if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else "docs/images/07_step_01_box_console_home.png"
    save_latest_screenshot(dest)

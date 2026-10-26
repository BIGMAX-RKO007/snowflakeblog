from PIL import ImageGrab
import sys

def capture_chrome_region(output_path, bbox=None):
    if bbox:
        img = ImageGrab.grab(bbox=bbox)
    else:
        # right half of 2560x1080: (1280, 0, 2560, 1040)
        img = ImageGrab.grab(bbox=(1280, 0, 2560, 1040))
    img.save(output_path)
    print(f"Captured to {output_path} with size {img.size}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/images/07_step_01_box_console_home.png"
    capture_chrome_region(out)

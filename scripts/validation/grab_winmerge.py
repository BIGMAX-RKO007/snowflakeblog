import time
import sys
import ctypes
from PIL import ImageGrab

user32 = ctypes.windll.user32

def find_winmerge(keyword):
    hwnds = []
    def enum_cb(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            if "WinMerge" in title and keyword.lower() in title.lower():
                hwnds.append((hwnd, title))
        return True

    CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(CMPFUNC(enum_cb), 0)
    return hwnds

def grab_comparison(keyword, output_path):
    matches = find_winmerge(keyword)
    print(f"[*] Found {len(matches)} windows for '{keyword}':", matches)
    if not matches:
        return False
    hwnd = matches[0][0]
    user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    user32.SetForegroundWindow(hwnd)
    time.sleep(1.2)
    img = ImageGrab.grab()
    img.save(output_path)
    print(f"[+] Saved screenshot to: {output_path} (size: {img.size})")
    return True

if __name__ == '__main__':
    kw = sys.argv[1] if len(sys.argv) > 1 else "cust_master"
    out = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\FX\Projects\SnowflakeBlog\docs\images\05_step_06_winmerge_master_diff.png"
    grab_comparison(kw, out)

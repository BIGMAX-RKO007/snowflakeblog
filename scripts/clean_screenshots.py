"""
clean_screenshots.py - Right-only cropping to remove Edge Copilot widget while keeping 100% of Left, Top, and Bottom.
"""
import os
import shutil
from PIL import Image

AFFECTED_IMAGES = [
    '01_cat_01_ingestion.png',
    '01_cat_02_transformation.png',
    '01_cat_03_ai_ml.png',
    '01_cat_04_monitoring.png',
    '01_cat_05_data_sharing.png',
    '01_cat_06_governance.png',
    '01_cat_07_compute.png',
    '01_cat_08_admin.png',
    '01_img_03.png',
    '01_img_08.png',
    '01_img_09.png',
    '01_img_10.png',
    '01_img_11.png',
    '01_img_12.png',
    '01_img_13.png',
    '01_img_14.png',
    '01_img_15.png',
    '01_img_16.png',
    '01_img_17.png',
    '01_img_18.png',
    '01_img_19.png',
    '01_img_20.png',
    '01_img_21.png',
]

def clean_right_only(images_dir='docs/images', backup_dir='docs/images/.backup'):
    results = []

    for name in AFFECTED_IMAGES:
        backup_path = os.path.join(backup_dir, name)
        file_path = os.path.join(images_dir, name)
        
        # Read from untouched backup if available, else original
        src_path = backup_path if os.path.exists(backup_path) else file_path
        if not os.path.exists(src_path):
            continue

        with Image.open(src_path) as im:
            w, h = im.size
            if w >= 2500:
                cut_right = 48
            elif w >= 1400:
                cut_right = 46
            else:
                cut_right = 54

            # ONLY crop right side (x=0, y=0, right=w-cut_right, bottom=h)
            crop_box = (0, 0, w - cut_right, h)
            cropped = im.crop(crop_box)
            cropped.save(file_path, format='PNG', optimize=True)
            cw, ch = cropped.size

        results.append((name, (w, h), (cw, ch)))
        print(f"[RIGHT-ONLY CLEANED] {name}: {w}x{h} -> {cw}x{ch} (full top/left/bottom preserved)")

    print(f"\nSuccessfully processed {len(results)} images with right-only cropping.")

if __name__ == '__main__':
    clean_right_only()

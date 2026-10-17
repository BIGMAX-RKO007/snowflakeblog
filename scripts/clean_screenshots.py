"""
clean_screenshots.py - Automatically cleans Edge Page Context Halo (glow) and Copilot Action Widget from screenshots.
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

def clean_all(images_dir='docs/images', backup_dir='docs/images/.backup'):
    os.makedirs(backup_dir, exist_ok=True)
    results = []

    for name in AFFECTED_IMAGES:
        file_path = os.path.join(images_dir, name)
        if not os.path.exists(file_path):
            continue

        # Backup original
        backup_path = os.path.join(backup_dir, name)
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)

        # Open and crop
        with Image.open(file_path) as im:
            w, h = im.size
            if w >= 2500:
                crop_box = (22, 18, w - 48, h - 18)
            elif w >= 1400:
                crop_box = (20, 16, w - 46, h - 16)
            else:
                crop_box = (16, 14, w - 54, h - 14)

            cropped = im.crop(crop_box)
            cropped.save(file_path, format='PNG', optimize=True)
            cw, ch = cropped.size

        results.append((name, (w, h), (cw, ch)))
        print(f"[CLEANED] {name}: {w}x{h} -> {cw}x{ch}")

    print(f"\nSuccessfully cleaned {len(results)} images.")

if __name__ == '__main__':
    clean_all()

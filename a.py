import os
import shutil

base_dir = r"d:\Team NovaDesk\skin_guard_ml\data\HAM10000"

images_dir = os.path.join(base_dir, "all_images")

# Create all_images if not exists
os.makedirs(images_dir, exist_ok=True)

parts = ["HAM10000_images_part_1", "HAM10000_images_part_2"]

for part in parts:
    part_path = os.path.join(base_dir, part)

    if not os.path.exists(part_path):
        print("❌ Folder not found:", part_path)
        continue

    for img in os.listdir(part_path):
        src = os.path.join(part_path, img)
        dst = os.path.join(images_dir, img)
        shutil.copy(src, dst)

print("✅ Done copying all images!")

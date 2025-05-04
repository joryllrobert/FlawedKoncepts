import os
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

# Constants
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
WALLPAPER_DIR = Path('wallpapers')
RAW_BASE_URL = "https://raw.githubusercontent.com/wallpapers"

def generate_thumbnail(image_path: Path, thumbnail_path: Path):
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "magick",
        str(image_path),
        "-resize", "500x500^",
        "-gravity", "center",
        "-extent", "500x500",
        "-quality", "75",
        str(thumbnail_path)
    ]
    try:
        subprocess.run(command, check=True)
        print(f"✓ Thumbnail: {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed thumbnail for {image_path}: {e}")

def parse_name_author(filename: str):
    name_part = Path(filename).stem
    separators = ['-', '_']
    for sep in separators:
        if sep in name_part:
            parts = name_part.split(sep)
            if len(parts) >= 2:
                return sep.join(parts[:-1]).replace('_', ' ').replace('-', ' '), parts[-1].replace('_', ' ').replace('-', ' ')
    return name_part, "Unknown"

def process_subfolder(folder: Path):
    json_entries = []
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            name, author = parse_name_author(file.name)

            # Create thumbnail path
            thumbnail_dir = folder / "thumbnails"
            thumbnail_filename = file.stem + ".jpg"
            thumbnail_path = thumbnail_dir / thumbnail_filename

            if not thumbnail_path.exists():
                generate_thumbnail(file, thumbnail_path)

            # Create URLs (encode spaces/special characters)
            subfolder_name = folder.name
            encoded_file = quote(file.name)
            encoded_thumb = quote(thumbnail_filename)

            entry = {
                "name": name,
                "author": author,
                "url": f"{RAW_BASE_URL}/{subfolder_name}/{encoded_file}",
                "thumbUrl": f"{RAW_BASE_URL}/{subfolder_name}/thumbnails/{encoded_thumb}"
            }
            json_entries.append(entry)

    # Write JSON
    if json_entries:
        json_path = folder / f"{folder.name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_entries, f, indent=2)
        print(f"📄 JSON written: {json_path}")

def process_all_subfolders(root: Path):
    for subfolder in root.iterdir():
        if subfolder.is_dir() and subfolder.name != "thumbnails":
            print(f"\n🔍 Processing folder: {subfolder.name}")
            process_subfolder(subfolder)

if __name__ == "__main__":
    if not WALLPAPER_DIR.exists():
        print(f"❌ 'wallpapers' folder not found at: {WALLPAPER_DIR.resolve()}")
    else:
        process_all_subfolders(WALLPAPER_DIR)

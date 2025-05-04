import os
import json
import random
import subprocess
from pathlib import Path
from urllib.parse import quote

# Constants
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
WALLPAPER_DIR = Path('wallpapers')
RAW_BASE_URL = "https://raw.githubusercontent.com/joryllrobert/FlawedKoncepts/main/wallpapers"

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
        print(f"✓ Thumbnail created: {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create thumbnail for {image_path}: {e}")

def parse_name_author(filename: str):
    name_part = Path(filename).stem
    for sep in ['-', '_']:
        if sep in name_part:
            parts = name_part.split(sep)
            if len(parts) >= 2:
                name = sep.join(parts[:-1]).replace('_', ' ').replace('-', ' ').strip()
                author = parts[-1].replace('_', ' ').replace('-', ' ').strip()
                return name, author
    return name_part.replace('_', ' ').replace('-', ' ').strip(), "Unknown"

def clean_orphan_thumbnails(thumbnail_dir: Path, valid_basenames: set):
    removed = 0
    for thumb in thumbnail_dir.glob("*.jpg"):
        if thumb.stem not in valid_basenames:
            thumb.unlink()
            print(f"🗑️ Removed orphan thumbnail: {thumb}")
            removed += 1
    return removed

def process_subfolder(folder: Path):
    json_entries = []
    valid_basenames = set()
    thumbnail_dir = folder / "thumbnails"
    created, removed = 0, 0

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            if file.parent.name == "thumbnails":
                continue  # Skip thumbnails

            name, author = parse_name_author(file.name)
            base_name = file.stem
            valid_basenames.add(base_name)

            thumbnail_filename = base_name + ".jpg"
            thumbnail_path = thumbnail_dir / thumbnail_filename

            if not thumbnail_path.exists():
                generate_thumbnail(file, thumbnail_path)
                created += 1

            subfolder_name = folder.name
            encoded_file = quote(file.name)
            encoded_thumb = quote(thumbnail_filename)

            json_entries.append({
                "name": name,
                "author": author,
                "url": f"{RAW_BASE_URL}/{subfolder_name}/{encoded_file}",
                "thumbUrl": f"{RAW_BASE_URL}/{subfolder_name}/thumbnails/{encoded_thumb}"
            })

    # Clean orphan thumbnails
    if thumbnail_dir.exists():
        removed = clean_orphan_thumbnails(thumbnail_dir, valid_basenames)

    # Shuffle entries before writing JSON
    if json_entries:
        random.shuffle(json_entries)
        json_path = folder / f"{folder.name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_entries, f, indent=2)
        print(f"📄 JSON written: {json_path}")

    # Summary per folder
    print(f"📂 Folder: {folder.name} | Thumbnails created: {created} | Orphans removed: {removed}")

def process_all_subfolders(root: Path):
    for subfolder in root.iterdir():
        if subfolder.is_dir() and subfolder.name != "thumbnails":
            print(f"\n🔍 Processing: {subfolder.name}")
            process_subfolder(subfolder)

if __name__ == "__main__":
    if not WALLPAPER_DIR.exists():
        print(f"❌ 'wallpapers' folder not found at: {WALLPAPER_DIR.resolve()}")
    else:
        process_all_subfolders(WALLPAPER_DIR)

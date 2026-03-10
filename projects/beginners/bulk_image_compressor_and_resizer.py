"""Bulk Image Compressor and Resizer (Beginner)

Resize and save copies of images in a folder.

Requires:
- Pillow (PIL)

Example:
    python bulk_image_compressor_and_resizer.py --source ./images --out ./out --width 800

"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def process_folder(source: Path, out: Path, width: int) -> None:
    out.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png"}
    for p in source.iterdir():
        if p.suffix.lower() not in exts or not p.is_file():
            continue

        with Image.open(p) as img:
            w, h = img.size
            new_h = int(h * (width / w))
            resized = img.resize((width, new_h))

            target = out / p.name
            resized.save(target, optimize=True, quality=85)
            print("saved", target)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bulk resize images.")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=800)
    return p


def main() -> None:
    args = build_parser().parse_args()
    process_folder(args.source, args.out, args.width)


if __name__ == "__main__":
    main()

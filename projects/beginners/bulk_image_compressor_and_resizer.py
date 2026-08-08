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


def demo() -> None:
    """Generate a few images in a scratch folder and resize those.

    A tool that exits with "the following arguments are required" the first
    time anyone runs it has not demonstrated anything. The real flags still
    work; this is what happens when none are given.
    """
    import tempfile

    from PIL import Image

    folder = Path(tempfile.mkdtemp(prefix="bulk-demo-"))
    source, out = folder / "in", folder / "out"
    source.mkdir()
    for index, size in enumerate(((1600, 1200), (2400, 1200), (900, 900)), 1):
        Image.new("RGB", size, (40 * index, 90, 160)).save(
            source / f"sample_{index}.jpg")
    print(f"no --source given, so three images were generated in {source}\n")
    process_folder(source, out, 800)

    print("\n{:>18} {:>12} {:>12} {:>9}".format(
        "file", "before", "after", "saved"))
    for original in sorted(source.iterdir()):
        resized = out / original.name
        if not resized.exists():
            continue
        before, after = original.stat().st_size, resized.stat().st_size
        print("{:>18} {:>11,}B {:>11,}B {:>8.0%}".format(
            original.name, before, after, 1 - after / before))


def main() -> None:
    import sys

    if len(sys.argv) == 1:
        demo()
        return
    args = build_parser().parse_args()
    process_folder(args.source, args.out, args.width)


if __name__ == "__main__":
    main()

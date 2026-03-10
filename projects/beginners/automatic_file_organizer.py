"""Automatic File Organizer (Beginner)

Sort files in a folder (e.g., Downloads) into subfolders by file extension.

SAFETY:
- Start with a test folder.
- Use --dry-run first.

Examples:
    python automatic_file_organizer.py --source ./Downloads --dry-run
    python automatic_file_organizer.py --source ./Downloads

"""

from __future__ import annotations

import argparse
from pathlib import Path


def organize(source: Path, dry_run: bool = True) -> None:
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source folder does not exist or is not a directory: {source}")

    for item in source.iterdir():
        if item.is_dir():
            continue

        ext = item.suffix.lower().lstrip(".") or "no_extension"
        target_dir = source / ext
        target_path = target_dir / item.name

        if dry_run:
            print(f"[DRY RUN] {item} -> {target_path}")
            continue

        target_dir.mkdir(exist_ok=True)
        item.rename(target_path)
        print(f"moved {item.name} -> {target_dir.name}/")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Organize files into folders by extension.")
    p.add_argument("--source", type=Path, required=True, help="Folder to organize")
    p.add_argument("--dry-run", action="store_true", help="Print actions without moving files")
    return p


def main() -> None:
    args = build_parser().parse_args()
    organize(args.source, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

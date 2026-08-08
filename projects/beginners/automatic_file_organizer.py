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

        # A file literally named "no_extension" collides with the folder this
        # would create for it, and mkdir then fails with FileExistsError. The
        # same happens for any file whose name matches a bucket.
        if target_dir.exists() and not target_dir.is_dir():
            print(f"skipped {item.name}: a file of that name is in the way "
                  f"of the {ext}/ folder")
            continue

        if dry_run:
            print(f"[DRY RUN] {item} -> {target_path}")
            continue

        target_dir.mkdir(exist_ok=True)
        if target_path.exists():
            print(f"skipped {item.name}: already present in {ext}/")
            continue
        item.rename(target_path)
        print(f"moved {item.name} -> {target_dir.name}/")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Organize files into folders by extension.")
    p.add_argument("--source", type=Path, required=True, help="Folder to organize")
    p.add_argument("--dry-run", action="store_true", help="Print actions without moving files")
    return p


def demo() -> None:
    """Build a scratch folder of files and organise that.

    Running a tool with no arguments should show what it does, not exit with
    "the following arguments are required". The real flags still work.
    """
    import tempfile

    folder = Path(tempfile.mkdtemp(prefix="organizer-demo-"))
    for name in ("notes.txt", "report.pdf", "photo.jpg", "song.mp3",
                 "archive.zip", "script.py", "no_extension"):
        (folder / name).write_text("sample", encoding="utf-8")
    print(f"no --source given, so a demo folder was created at {folder}")
    print(f"it holds {len(list(folder.iterdir()))} files\n")
    organize(folder, dry_run=False)
    print("\nafter organising:")
    for child in sorted(folder.iterdir()):
        if child.is_dir():
            names = ", ".join(sorted(item.name for item in child.iterdir()))
            print(f"  {child.name}/  {names}")
        else:
            print(f"  {child.name}")


def main() -> None:
    import sys

    if len(sys.argv) == 1:
        demo()
        return
    args = build_parser().parse_args()
    organize(args.source, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

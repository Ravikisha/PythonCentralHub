"""Capture the images the projects produce, so their pages can show them.

`scripts/projects_run.py` records that a project wrote `foo.png`; this runs the
project again and keeps the file, under `public/images/projects/<name>.png`.

That distinction matters for how the pages read. A `<Figure>` on a project page
is not an illustration commissioned for the page -- it is the output of the
program the page ships, produced by running it. If the project changes and
stops producing that image, this script stops copying it and the page's figure
asset goes missing, which `scripts/check_docs.py` reports.

    python scripts/projects_capture.py            # every project that emits one
    python scripts/projects_capture.py fibonacci  # one, by substring
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
LEDGER = os.path.join(REPO, "docs", "projects_run_ledger.json")
OUT = os.path.join(REPO, "public", "images", "projects")
KEEP = (".png", ".jpg", ".jpeg", ".svg", ".gif")


def producers(pattern: str | None) -> list[dict]:
    with open(LEDGER, encoding="utf-8") as handle:
        ledger = json.load(handle)
    rows = []
    for row in ledger["runs"]:
        if not row["ok"] or not row["artifacts"]:
            continue
        if pattern and pattern not in row["source"]:
            continue
        images = [a for a in row["artifacts"]
                  if a["name"].lower().endswith(KEEP)]
        if images:
            rows.append({**row, "images": images})
    return rows


def capture(row: dict, timeout: int) -> list[str]:
    source = os.path.join(REPO, row["source"].replace("/", os.sep))
    workdir = tempfile.mkdtemp(prefix="pch-capture-")
    written = []
    try:
        shutil.copyfile(source, os.path.join(workdir,
                                             os.path.basename(source)))
        subprocess.run(
            [sys.executable, os.path.basename(source)], cwd=workdir,
            stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout,
            env=dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8"))
        os.makedirs(OUT, exist_ok=True)
        for image in row["images"]:
            produced = os.path.join(workdir, image["name"])
            if not os.path.exists(produced):
                continue
            target = os.path.join(OUT, image["name"])
            shutil.copyfile(produced, target)
            written.append(os.path.relpath(target, REPO).replace(os.sep, "/"))
    except subprocess.TimeoutExpired:
        pass
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pattern", nargs="?")
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()

    rows = producers(args.pattern)
    if not rows:
        print("no project in the ledger produced an image. Run "
              "scripts/projects_run.py first.")
        return 0

    total = []
    for index, row in enumerate(rows, 1):
        written = capture(row, args.timeout)
        total.extend(written)
        name = row["source"].split("/")[-1]
        print(f"  [{index:3}/{len(rows)}] {name:46} "
              f"{len(written)} image(s)")

    print(f"\n{len(total)} image(s) captured into "
          f"{os.path.relpath(OUT, REPO).replace(os.sep, '/')}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

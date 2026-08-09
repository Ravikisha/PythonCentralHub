"""Rewrite a project page's "What it produces" section from the run ledger.

This exists because doing it by hand kept breaking the same thing. The output
section usually contains two parts -- the transcript and a ``<Figure>`` that
shows the image the project wrote -- and a regex that replaced the section
wholesale silently deleted the figure. That regression was introduced and
repaired three separate times before this script existed, which is the point
at which a one-off edit should become a tool.

So: the transcript is regenerated, any existing ``<Figure>`` in the section is
carried across unchanged, and a figure is *added* when the ledger says the
project produced an image and the page has none.

    python scripts/projects_wire_output.py --report
    python scripts/projects_wire_output.py --page time_series --apply
    python scripts/projects_wire_output.py --apply          # every page that ran
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(REPO, "src", "content", "docs", "projects")
LEDGER = os.path.join(REPO, "docs", "projects_run_ledger.json")
IMAGES = os.path.join(REPO, "public", "images", "projects")

SECTION = re.compile(r"(^## What it produces\n)([\s\S]*?)(?=^## |\Z)", re.M)
FIGURE = re.compile(r"<Figure[\s\S]*?/>")
FILECODE = re.compile(r'<FileCode\s+file="([^"]+)"')
# Any existing component import tells us the relative path to use.
FIGURE_IMPORT = re.compile(
    r"^import \w+ from '(\.\.[^']*)/components/\w+\.astro'", re.M)
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".svg", ".gif")

FIGURE_TEMPLATE = """<Figure
  single src="/images/projects/{image}"
  alt="Output of {stem}.py, produced by running the file."
  title="Produced by this project, not drawn for the page"
  caption="Written by the run above. If the project stops producing it, the page's figure asset goes missing and check_docs reports it — which is the point of generating it rather than drawing it."
/>"""


def load_ledger() -> dict:
    with io.open(LEDGER, encoding="utf-8") as handle:
        return {row["source"]: row for row in json.load(handle)["runs"]}


def pages():
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name.endswith(".mdx"):
                yield os.path.join(root, name)


def transcript(run: dict, command: str, keep: int | None) -> str:
    lines = (run["stdout"] or "").rstrip("\n").split("\n")
    trimmed = keep is not None and len(lines) > keep
    if trimmed:
        lines = lines[:keep]
    body = "\n".join(lines)
    text = (f"\nRunning the file exactly as it ships takes "
            f"**{run['seconds']:.1f} s** and prints:\n\n"
            f'```text title="{command}"\n{body}\n')
    if trimmed:
        text += "...\n"
    text += "```\n"
    if trimmed:
        # Say what was cut. A transcript that silently stops looks like the
        # program stopped, which is the opposite of the point.
        total = len((run["stdout"] or "").rstrip("\n").split("\n"))
        text += (f"\nThe first {keep} of {total} lines are shown; the run "
                 f"continues past this point.\n")
    return text


def wire(path: str, ledger: dict, keep: int | None) -> tuple[str, str] | None:
    """Return (new page text, what changed), or None if nothing to do."""
    page = io.open(path, encoding="utf-8").read()
    match = SECTION.search(page)
    source_match = FILECODE.search(page)
    if not match or not source_match:
        return None
    run = ledger.get(source_match.group(1))
    if not run or not run.get("ok"):
        return None

    stem = os.path.basename(source_match.group(1))[:-3]
    existing = FIGURE.search(match.group(2))
    notes = []

    block = transcript(run, f"python {stem}.py", keep)

    if existing:
        # The figure is the part that kept getting lost. Carry it across
        # verbatim rather than regenerating it -- a hand-edited caption is
        # worth keeping.
        block += "\n" + existing.group(0) + "\n"
        notes.append("kept the existing figure")
    else:
        artifacts = [a["name"] for a in run.get("artifacts", [])
                     if a["name"].lower().endswith(IMAGE_SUFFIXES)]
        available = [a for a in artifacts
                     if os.path.exists(os.path.join(IMAGES, a))]
        if available and "<Figure" not in page:
            block += "\n" + FIGURE_TEMPLATE.format(image=available[0],
                                                   stem=stem) + "\n"
            notes.append(f"added a figure ({available[0]})")
            # The component has to be imported as well as used. Adding the
            # tag without the import produces a page that passes mdxcheck
            # and fails check_docs, which is how it slipped through once.
            if "components/Figure.astro" not in page:
                page = FIGURE_IMPORT.sub(
                    lambda m: m.group(0) + "\nimport Figure from "
                    f"'{m.group(1)}/components/Figure.astro'", page, count=1)
                notes.append("and its import")
        elif artifacts and not available:
            notes.append(f"!! {artifacts[0]} was never captured")

    updated = page[:match.start(2)] + block + "\n" + page[match.end(2):]
    if updated == page:
        return None
    return updated, ", ".join(notes) or "transcript only"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", help="substring of the page filename")
    parser.add_argument("--keep", type=int,
                        help="trim the transcript to this many lines")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    ledger = load_ledger()
    changed = 0
    for path in pages():
        name = os.path.basename(path)[:-4]
        if args.page and args.page not in name:
            continue
        result = wire(path, ledger, args.keep)
        if not result:
            continue
        updated, note = result
        changed += 1
        print(f"  {name:46} {note}")
        if args.apply:
            io.open(path, "w", encoding="utf-8", newline="").write(updated)

    print(f"\n{changed} page(s) "
          f"{'rewritten' if args.apply else 'would change'}")
    if not args.apply:
        print("nothing written; pass --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

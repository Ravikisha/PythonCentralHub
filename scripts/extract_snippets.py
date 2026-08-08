"""Rewrite a project page's walkthrough using code from the file it ships.

183 of 203 project pages present numbered snippets "from" the project file that
define functions the file does not contain. `Advance/customer_segmentation_ml`
walks the reader through a `segment_customers(df)` helper and a `main()` that
prints "[Demo] Segmentation logic here."; the shipped file has neither, and
instead defines a `CustomerSegmentationML` class. A reader following the page
cannot arrive at the file.

This script removes the possibility of that drift by generating the walkthrough
from the source rather than beside it::

    python scripts/extract_snippets.py --report            # what is stale
    python scripts/extract_snippets.py --page customer_seg # preview one page
    python scripts/extract_snippets.py --apply             # rewrite

The walkthrough it writes is deliberately plain: the imports, then each
top-level class or function in file order, each with the line numbers it
occupies in the real file. It is not a substitute for prose -- waves 3 to 5
add that -- but it is *true*, which the current text is not.
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(REPO, "src", "content", "docs", "projects")

FILECODE = re.compile(r'<FileCode\s+file="([^"]+)"')
SNIPPET = re.compile(r'```python[^\n]*\n([\s\S]*?)```')
# The generated section runs from "### Code Breakdown" to the next "## ".
BREAKDOWN = re.compile(r"(### Code Breakdown\n)([\s\S]*?)(?=\n## )")

MAX_LINES = 26          # a snippet longer than this is elided in the middle
MAX_PIECES = 5


def defined_names(code: str) -> set:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    return {node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef))}


def pieces(code: str) -> list[dict]:
    """Imports plus every top-level class and function, in file order."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    lines = code.split("\n")
    out = []

    header = [node for node in tree.body
              if isinstance(node, (ast.Import, ast.ImportFrom))]
    if header:
        start = min(node.lineno for node in header)
        end = max(node.end_lineno for node in header)
        out.append({"kind": "imports", "name": "imports",
                    "start": start, "end": end,
                    "code": "\n".join(lines[start - 1:end])})

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            out.append({
                "kind": "class" if isinstance(node, ast.ClassDef)
                else "function",
                "name": node.name,
                "start": node.lineno,
                "end": node.end_lineno,
                "code": "\n".join(lines[node.lineno - 1:node.end_lineno]),
            })
    return out


def elide(code: str, keep: int = MAX_LINES) -> str:
    lines = code.split("\n")
    if len(lines) <= keep:
        return code
    head = lines[:keep - 8]
    tail = lines[-6:]
    indent = " " * (len(tail[0]) - len(tail[0].lstrip()))
    return "\n".join(head + [f"{indent}# ... {len(lines) - keep + 2} more "
                             f"lines in the file ..."] + tail)


def build_walkthrough(source: str, code: str) -> str | None:
    found = pieces(code)
    if not found:
        return None
    filename = os.path.basename(source)
    chosen = found[:1] + sorted(
        found[1:], key=lambda p: p["end"] - p["start"], reverse=True
    )[:MAX_PIECES - 1]
    chosen.sort(key=lambda p: p["start"])

    blocks = []
    for index, piece in enumerate(chosen, 1):
        if piece["kind"] == "imports":
            label = "What it imports"
        else:
            label = f"`{piece['name']}` — the {piece['kind']}"
        blocks.append(
            f"{index}. **{label}** (lines {piece['start']}–{piece['end']})\n"
            f"```python title=\"{filename}\" "
            f"showLineNumbers startLineNumber={piece['start']}\n"
            f"{elide(piece['code'])}\n```\n")
    total = len(found) - 1
    note = (f"\nThe file defines {total} top-level "
            f"{'symbol' if total == 1 else 'symbols'} in all; the whole thing "
            f"is above under *Write the Code*.\n")
    return "\n".join(blocks) + note


def stale_count(text: str, code: str) -> int:
    available = defined_names(code)
    stale = 0
    for snippet in SNIPPET.findall(text):
        declared = defined_names(snippet)
        if declared and declared - available:
            stale += 1
    return stale


def pages(filter_text: str | None):
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.endswith(".mdx"):
                continue
            if filter_text and filter_text not in name:
                continue
            yield os.path.join(root, name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--page", help="substring of a page filename")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    changed, stale_pages, no_anchor, no_source = 0, 0, [], []
    for path in pages(args.page):
        text = io.open(path, encoding="utf-8").read()
        match = FILECODE.search(text)
        name = os.path.basename(path)[:-4]
        if not match:
            no_source.append(name)
            continue
        source = match.group(1)
        candidate = os.path.join(REPO, source.replace("/", os.sep))
        if not os.path.exists(candidate):
            no_source.append(name)
            continue
        code = io.open(candidate, encoding="utf-8", errors="replace").read()

        stale = stale_count(text, code)
        if stale:
            stale_pages += 1
        if args.report:
            if stale:
                print(f"  {stale:2} stale  {name[:50]}")
            continue

        if not BREAKDOWN.search(text):
            no_anchor.append(name)
            continue
        walkthrough = build_walkthrough(source, code)
        if walkthrough is None:
            no_anchor.append(name)
            continue

        updated = BREAKDOWN.sub(
            lambda m: m.group(1) + walkthrough, text, count=1)
        if updated == text:
            continue
        changed += 1
        if args.page and not args.apply:
            print(updated[updated.index("### Code Breakdown"):][:2200])
        if args.apply:
            io.open(path, "w", encoding="utf-8", newline="").write(updated)

    if args.report:
        print(f"\n{stale_pages} page(s) carry at least one stale snippet")
        return 0
    verb = "rewrote" if args.apply else "would rewrite"
    print(f"\n{verb} {changed} page(s)")
    if no_anchor:
        print(f"{len(no_anchor)} page(s) have no '### Code Breakdown' anchor "
              f"or no parseable source:")
        for name in no_anchor[:10]:
            print("  -", name)
        if len(no_anchor) > 10:
            print(f"  ... and {len(no_anchor) - 10} more")
    if no_source:
        print(f"{len(no_source)} page(s) have no usable <FileCode> source")
        for name in no_source[:5]:
            print("  -", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

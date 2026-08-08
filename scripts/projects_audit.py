"""Measure the projects section against the enhancement targets.

Run it before and after each wave so progress is a number rather than a
feeling::

    python scripts/projects_audit.py               # summary + per-tier table
    python scripts/projects_audit.py --gaps        # only what is still missing
    python scripts/projects_audit.py --pages       # every page, one row each
    python scripts/projects_audit.py --json        # machine-readable
    python scripts/projects_audit.py --progress    # rewrite the progress log

Targets come from docs/projects_upgrade_plan.md. The two that make this
section different from the tutorial modules are the last two in ``TARGETS``:

``snippets_match``
    Every ``python`` snippet in a page's walkthrough must define something that
    actually exists in the file the page ships. 183 of 203 pages failed this at
    the baseline, which is why wave 1 exists.

``runs``
    ``scripts/projects_run.py`` must have executed the project successfully.
    A page describing a program nobody ran is the projects-section equivalent
    of a number nobody measured.
"""

from __future__ import annotations

import argparse
import ast
import collections
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(REPO, "src", "content", "docs", "projects")
LEDGER = os.path.join(REPO, "docs", "projects_run_ledger.json")
PROGRESS = os.path.join(REPO, "docs", "projects_progress.md")

TIERS = ("Beginners", "intermediate", "Advance")

TARGETS = {
    "words": 900,
    "figures": 1,
    "quiz": 1,
    "exercises": 1,
    "mermaid": 1,
    "sketches": 0,          # p5 is per-page optional; only where a knob exists
    "sections": ["Pitfalls", "Recap"],
    "snippets_match": True,
    "runs": True,
}

SNIPPET = re.compile(r'```python[^\n]*\n([\s\S]*?)```')
FILECODE = re.compile(r'<FileCode\s+file="([^"]+)"')
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.M)


def load_ledger() -> dict:
    if not os.path.exists(LEDGER):
        return {}
    try:
        with open(LEDGER, encoding="utf-8") as handle:
            return {row["source"]: row for row in json.load(handle)["runs"]}
    except (OSError, ValueError, KeyError):
        return {}


def defined_names(code: str) -> set:
    """Every function and class name defined anywhere in a file."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            out.add(node.name)
    return out


def snippet_report(text: str, source_code: str | None) -> dict:
    """Do the page's walkthrough snippets exist in the file it ships?"""
    if source_code is None:
        return {"checked": 0, "missing": 0, "names": []}
    available = defined_names(source_code)
    checked, missing, names = 0, 0, []
    for snippet in SNIPPET.findall(text):
        declared = defined_names(snippet)
        if not declared:
            continue                      # imports or a call, nothing to anchor
        checked += 1
        absent = sorted(declared - available)
        if absent:
            missing += 1
            names.extend(absent)
    return {"checked": checked, "missing": missing, "names": sorted(set(names))}


def measure(path: str, ledger: dict) -> dict:
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    relative = os.path.relpath(path, REPO).replace(os.sep, "/")
    tier = relative.split("/")[4] if len(relative.split("/")) > 4 else "?"

    match = FILECODE.search(text)
    source = match.group(1) if match else None
    source_code = None
    if source:
        candidate = os.path.join(REPO, source.replace("/", os.sep))
        if os.path.exists(candidate):
            with open(candidate, encoding="utf-8", errors="replace") as handle:
                source_code = handle.read()

    snippets = snippet_report(text, source_code)
    headings = set(HEADING.findall(text))
    run = ledger.get(source) if source else None

    return {
        "path": relative,
        "tier": tier,
        "name": os.path.basename(path)[:-4],
        "source": source,
        "source_exists": source_code is not None,
        "words": len(text.split()),
        "figures": text.count("<Figure"),
        "quiz": text.count("<Quiz"),
        "exercises": text.count("<DataCampExercise"),
        "mermaid": len(re.findall(r"^```mermaid", text, re.M)),
        "sketches": len(re.findall(r"^```p5", text, re.M)),
        "code_blocks": len(SNIPPET.findall(text)),
        "snippets_checked": snippets["checked"],
        "snippets_missing": snippets["missing"],
        "missing_names": snippets["names"],
        "sections": sorted(headings & set(TARGETS["sections"])),
        "order": int(m.group(1)) if (m := re.search(r"order:\s*(\d+)", text))
        else None,
        "runs": bool(run and run.get("ok")),
        "ran_at": run.get("finished") if run else None,
    }


def shortfalls(row: dict) -> list[str]:
    out = []
    if row["words"] < TARGETS["words"]:
        out.append(f"words {row['words']}")
    for key in ("figures", "quiz", "exercises", "mermaid"):
        if row[key] < TARGETS[key]:
            out.append(key)
    for section in TARGETS["sections"]:
        if section not in row["sections"]:
            out.append(f"no {section}")
    if row["snippets_missing"]:
        out.append(f"{row['snippets_missing']} stale snippet(s)")
    if not row["runs"]:
        out.append("never run")
    return out


def collect() -> list[dict]:
    ledger = load_ledger()
    rows = []
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name.endswith(".mdx"):
                rows.append(measure(os.path.join(root, name), ledger))
    return rows


def totals(rows: list[dict]) -> dict:
    duplicates = collections.Counter(
        row["order"] for row in rows if row["order"] is not None)
    return {
        "pages": len(rows),
        "words": sum(row["words"] for row in rows),
        "figures": sum(row["figures"] for row in rows),
        "quizzes": sum(row["quiz"] for row in rows),
        "exercises": sum(row["exercises"] for row in rows),
        "mermaid": sum(row["mermaid"] for row in rows),
        "sketches": sum(row["sketches"] for row in rows),
        "pages_with_stale_snippets": sum(
            1 for row in rows if row["snippets_missing"]),
        "stale_snippets": sum(row["snippets_missing"] for row in rows),
        "pages_that_run": sum(1 for row in rows if row["runs"]),
        "pages_missing_source": sum(
            1 for row in rows if not row["source_exists"]),
        "duplicate_orders": sum(count - 1
                                for count in duplicates.values() if count > 1),
        "pages_at_target": sum(1 for row in rows if not shortfalls(row)),
    }


def render_summary(rows: list[dict], numbers: dict) -> list[str]:
    lines = ["Projects section audit",
             "=" * 78]
    for key, value in numbers.items():
        lines.append(f"  {key:26} {value:>8,}")
    lines.append("")
    lines.append(f"  {'tier':13} {'pages':>6} {'words/pg':>9} {'fig':>5} "
                 f"{'quiz':>5} {'exer':>5} {'merm':>5} {'p5':>4} "
                 f"{'stale':>6} {'runs':>6} {'at target':>10}")
    for tier in TIERS:
        subset = [row for row in rows if row["tier"] == tier]
        if not subset:
            continue
        lines.append(
            f"  {tier:13} {len(subset):6} "
            f"{sum(r['words'] for r in subset) // len(subset):9,} "
            f"{sum(r['figures'] for r in subset):5} "
            f"{sum(r['quiz'] for r in subset):5} "
            f"{sum(r['exercises'] for r in subset):5} "
            f"{sum(r['mermaid'] for r in subset):5} "
            f"{sum(r['sketches'] for r in subset):4} "
            f"{sum(1 for r in subset if r['snippets_missing']):6} "
            f"{sum(1 for r in subset if r['runs']):6} "
            f"{sum(1 for r in subset if not shortfalls(r)):10}")
    return lines


def write_progress(rows: list[dict], numbers: dict) -> None:
    stamp = datetime.date.today().isoformat()
    header = ("| Date | Pages | At target | Stale snippets | Pages that run | "
              "Figures | Quizzes | Exercises | mermaid | p5 | Dup orders |")
    divider = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    row = (f"| {stamp} | {numbers['pages']} | {numbers['pages_at_target']} | "
           f"{numbers['stale_snippets']} | {numbers['pages_that_run']} | "
           f"{numbers['figures']} | {numbers['quizzes']} | "
           f"{numbers['exercises']} | {numbers['mermaid']} | "
           f"{numbers['sketches']} | {numbers['duplicate_orders']} |")

    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = ("# Projects section — progress log\n\n"
                "Regenerate with `python scripts/projects_audit.py "
                "--progress`. One row per run; the plan is in\n"
                "`docs/projects_upgrade_plan.md`.\n\n"
                f"{header}\n{divider}\n")
    lines = text.rstrip("\n").split("\n")
    # Replace today's row if it exists, otherwise append.
    lines = [line for line in lines if not line.startswith(f"| {stamp} |")]
    lines.append(row)
    with open(PROGRESS, "w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\nprogress log updated: {os.path.relpath(PROGRESS, REPO)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaps", action="store_true",
                        help="list only pages that miss a target")
    parser.add_argument("--pages", action="store_true",
                        help="one row per page")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--progress", action="store_true",
                        help="append today's numbers to the progress log")
    parser.add_argument("--tier", choices=TIERS)
    args = parser.parse_args()

    rows = collect()
    if args.tier:
        rows = [row for row in rows if row["tier"] == args.tier]
    numbers = totals(rows)

    if args.json:
        print(json.dumps({"totals": numbers, "pages": rows}, indent=1))
        return 0

    print("\n".join(render_summary(rows, numbers)))

    if args.pages or args.gaps:
        print(f"\n  {'tier':13} {'w':>5} {'fig':>4} {'qz':>3} {'ex':>3} "
              f"{'mer':>4} {'p5':>3} {'run':>4}  page")
        for row in sorted(rows, key=lambda r: (r["tier"], r["name"])):
            gaps = shortfalls(row)
            if args.gaps and not gaps:
                continue
            print(f"  {row['tier']:13} {row['words']:5} {row['figures']:4} "
                  f"{row['quiz']:3} {row['exercises']:3} {row['mermaid']:4} "
                  f"{row['sketches']:3} {'yes' if row['runs'] else 'no':>4}  "
                  f"{row['name'][:44]}")
            if args.gaps and gaps:
                print(f"        {', '.join(gaps)}")

    remaining = numbers["pages"] - numbers["pages_at_target"]
    print(f"\n{numbers['pages_at_target']} of {numbers['pages']} pages meet "
          f"every target; {remaining} to go.")

    if args.progress:
        write_progress(rows, numbers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Measure the Deep Learning module against the enhancement targets.

Run it before and after each wave so progress is a number rather than a feeling::

    python scripts/dl_audit.py                 # summary + per-page table
    python scripts/dl_audit.py --gaps          # only what is still missing
    python scripts/dl_audit.py --json          # machine-readable, for diffing

Targets come from docs/dl_upgrade_plan.md and mirror what the Machine Learning
module already ships: a quiz and at least one diagram on every concept page,
real KaTeX derivations where the maths matters, generated figures instead of
prose descriptions of plots, and exercises whose expected output was produced by
running the solution.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(REPO, "src", "content", "docs", "Deep Learning")
IMAGES = os.path.join(REPO, "public", "images", "dl")

# Per-concept-page minimums for a page to count as "upgraded".
TARGETS = {
    "words": 2500,
    "exercises": 5,
    "quiz": 1,
    "diagrams": 1,          # mermaid OR figure
    "sketches": 1,          # p5
    "sections": ["What you'll learn", "Pitfalls", "Recap", "Next"],
}


def pages() -> list[tuple[str, str, str]]:
    """Return (phase, name, text) for every Deep Learning page."""
    out = []
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.endswith(".mdx"):
                continue
            path = os.path.join(root, name)
            phase = os.path.basename(root)
            with open(path, encoding="utf-8") as handle:
                out.append((phase if phase != "Deep Learning" else "(root)",
                            name[:-4], handle.read()))
    return out


def measure(text: str) -> dict:
    # Orders are floats here: the module inserts pages as 401.5, 473.3 and so on
    # rather than renumbering its neighbours.
    order = re.search(r"order:\s*([\d.]+)", text)
    mermaid = len(re.findall(r"^```mermaid", text, re.M))
    figures = len(re.findall(r"<Figure", text))
    missing = [s for s in TARGETS["sections"]
               if not re.search(r"^## .*" + re.escape(s.split()[0]), text, re.M | re.I)]
    return {
        "order": float(order.group(1)) if order else -1.0,
        "words": len(text.split()),
        "exercises": len(re.findall(r"<DataCampExercise", text)),
        "quiz": len(re.findall(r"<Quiz", text)),
        "sketches": len(re.findall(r"^```p5", text, re.M)),
        "mermaid": mermaid,
        "figures": figures,
        "diagrams": mermaid + figures,
        "display_math": len(re.findall(r"^\$\$", text, re.M)) // 2,
        "inline_math": len(re.findall(r"(?<!\$)\$[^$\n]{1,120}\$(?!\$)", text)),
        "code": len(re.findall(r"^```python", text, re.M)),
        # Count torch only inside fenced code. Prose that merely says
        # "no torch here" is not framework coverage.
        "torch": len(re.findall(
            r"\btorch\b|PyTorch",
            "\n".join(re.findall(r"^```[\s\S]*?^```", text, re.M)))),
        "keras": len(re.findall(r"\bkeras\b|Keras", text)),
        "missing_sections": missing,
    }


def shortfalls(row: dict) -> list[str]:
    out = []
    for key in ("words", "exercises", "quiz", "diagrams", "sketches"):
        if row[key] < TARGETS[key]:
            out.append(f"{key} {row[key]}/{TARGETS[key]}")
    if row["missing_sections"]:
        out.append("no " + ", ".join(s.split()[0] for s in row["missing_sections"]))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", action="store_true", help="only pages below target")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    rows = []
    for phase, name, text in pages():
        row = measure(text)
        row.update(phase=phase, name=name)
        row["concept"] = row["exercises"] > 0
        row["shortfalls"] = shortfalls(row) if row["concept"] else []
        rows.append(row)
    rows.sort(key=lambda r: (r["order"], r["name"]))

    concept = [r for r in rows if r["concept"]]
    svgs = sum(len(files) for _, _, files in os.walk(IMAGES)) if os.path.isdir(IMAGES) else 0
    totals = {
        "pages": len(rows),
        "concept_pages": len(concept),
        "words": sum(r["words"] for r in rows),
        "exercises": sum(r["exercises"] for r in rows),
        "quizzes": sum(r["quiz"] for r in rows),
        "sketches": sum(r["sketches"] for r in rows),
        "mermaid": sum(r["mermaid"] for r in rows),
        "figures": sum(r["figures"] for r in rows),
        "display_math": sum(r["display_math"] for r in rows),
        "committed_svgs": svgs,
        "pages_at_target": sum(1 for r in concept if not r["shortfalls"]),
        "torch_pages": sum(1 for r in rows if r["torch"]),
    }

    if args.json:
        print(json.dumps({"totals": totals, "pages": rows}, indent=2))
        return 0

    duplicates = collections.Counter(r["order"] for r in rows)
    clashes = {o: c for o, c in duplicates.items() if c > 1}

    print("Deep Learning module audit")
    print("=" * 78)
    for key, value in totals.items():
        print(f"  {key:18s} {value:,}")
    if clashes:
        print(f"  DUPLICATE sidebar orders: {clashes}")
    else:
        print("  sidebar orders: unique")

    listing = [r for r in rows if r["shortfalls"]] if args.gaps else rows
    print()
    print(f"{'ord':>6} {'words':>6} {'ex':>3} {'qz':>3} {'p5':>3} {'mer':>4} "
          f"{'fig':>4} {'math':>5}  page")
    for r in listing:
        print(f"{r['order']:>6.1f} {r['words']:>6} {r['exercises']:>3} {r['quiz']:>3} "
              f"{r['sketches']:>3} {r['mermaid']:>4} {r['figures']:>4} "
              f"{r['display_math']:>5}  {r['name'][:52]}")
        if r["shortfalls"]:
            print(f"{'':>36}  -> {'; '.join(r['shortfalls'])}")

    remaining = len(concept) - totals["pages_at_target"]
    print()
    print(f"{totals['pages_at_target']} of {len(concept)} concept pages meet every "
          f"target; {remaining} to go.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

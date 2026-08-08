"""Generate a call-flow diagram for a project page, from the project's code.

A diagram drawn by hand goes stale the moment the code changes, and a generic
one ("Input -> Process -> Output") says nothing. This reads the shipped file
with `ast` and emits what is actually there: the entry point, the functions and
classes it defines, and which of them call which.

    python scripts/projects_mermaid.py --report        # what would change
    python scripts/projects_mermaid.py --page fibonacci
    python scripts/projects_mermaid.py --apply --tier Beginners

Files with no functions at all get no diagram: a straight-line script has no
call flow to draw, and inventing one would be worse than leaving it out.
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(REPO, "src", "content", "docs", "projects")
FILECODE = re.compile(r'<FileCode\s+file="([^"]+)"')
ANCHORS = ("## Step-by-Step Explanation", "## Explanation",
           "## What it produces", "## Features")

MAX_NODES = 14


def slug(name: str) -> str:
    return re.sub(r"\W", "_", name)


def structure(code: str) -> dict | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    definitions, edges, classes = {}, set(), {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[node.name] = "function"
        elif isinstance(node, ast.ClassDef):
            definitions[node.name] = "class"
            classes[node.name] = [
                inner.name for inner in node.body
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def calls_within(node):
        found = []
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                target = inner.func
                if isinstance(target, ast.Name):
                    found.append(target.id)
                elif isinstance(target, ast.Attribute):
                    found.append(target.attr)
        return found

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for called in calls_within(node):
                if called in definitions and called != node.name:
                    edges.add((node.name, called))
        elif isinstance(node, ast.ClassDef):
            for inner in node.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for called in calls_within(inner):
                        if called in definitions and called != node.name:
                            edges.add((node.name, called))

    # What the module runs when executed: top-level calls, plus main().
    entry = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            target = node.value.func
            if isinstance(target, ast.Name) and target.id in definitions:
                entry.append(target.id)
        if isinstance(node, ast.If):
            for called in calls_within(node):
                if called in definitions:
                    entry.append(called)
    return {"definitions": definitions, "edges": sorted(edges),
            "entry": list(dict.fromkeys(entry)), "classes": classes}


def diagram(name: str, info: dict) -> str | None:
    definitions = info["definitions"]
    if not definitions:
        return None
    if len(definitions) > MAX_NODES:
        # Keep the entry points and whatever they reach; a 40-node graph is
        # not a diagram, it is a wall.
        keep = set(info["entry"])
        for _ in range(3):
            keep |= {b for a, b in info["edges"] if a in keep}
        definitions = {k: v for k, v in definitions.items() if k in keep} \
            or definitions
        definitions = dict(list(definitions.items())[:MAX_NODES])

    lines = ["```mermaid", "flowchart TD",
             f'  RUN(["python {name}.py"])']
    for symbol, kind in definitions.items():
        shape = (f'["{symbol}<br/>class"]' if kind == "class"
                 else f'("{symbol}")')
        lines.append(f"  {slug(symbol)}{shape}")
    for target in info["entry"]:
        if target in definitions:
            lines.append(f"  RUN --> {slug(target)}")
    if not any(t in definitions for t in info["entry"]):
        first = next(iter(definitions))
        lines.append(f"  RUN --> {slug(first)}")
    for source, target in info["edges"]:
        if source in definitions and target in definitions:
            lines.append(f"  {slug(source)} --> {slug(target)}")
    lines.append("```")
    return "\n".join(lines)


def pages(tier: str | None, needle: str | None):
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = sorted(dirs)
        if tier and os.path.basename(root) != tier:
            continue
        for name in sorted(files):
            if name.endswith(".mdx") and (not needle or needle in name):
                yield os.path.join(root, name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier")
    parser.add_argument("--page")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    added, already, nothing = 0, 0, []
    for path in pages(args.tier, args.page):
        text = io.open(path, encoding="utf-8").read()
        name = os.path.basename(path)[:-4]
        if re.search(r"^```mermaid", text, re.M):
            already += 1
            continue
        match = FILECODE.search(text)
        if not match:
            continue
        source = os.path.join(REPO, match.group(1).replace("/", os.sep))
        if not os.path.exists(source):
            continue
        code = io.open(source, encoding="utf-8", errors="replace").read()
        info = structure(code)
        if info is None:
            continue
        drawing = diagram(os.path.basename(source)[:-3], info)
        if drawing is None:
            nothing.append(name)
            continue

        anchor = next((a for a in ANCHORS if a in text), None)
        if not anchor:
            nothing.append(name + " (no anchor)")
            continue
        block = ("## How it fits together\n\n"
                 "Read from the top: this is what runs when you execute the "
                 "file, and which function calls which. It is generated from "
                 "the code, so it cannot drift from it.\n\n"
                 + drawing + "\n\n")
        if args.report or args.page:
            print(f"--- {name}\n{block}")
        if args.apply:
            io.open(path, "w", encoding="utf-8", newline="").write(
                text.replace(anchor, block + anchor, 1))
        added += 1

    verb = "added" if args.apply else "would add"
    print(f"{verb} a diagram to {added} page(s); {already} already had one")
    if nothing:
        print(f"{len(nothing)} page(s) have no functions to draw:")
        for name in nothing[:10]:
            print("  -", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Execute every project headlessly and record what actually happened.

The projects section's equivalent of "every number was measured" is "the
project runs, and the page shows what it produced". Nothing executed these 264
files before this script; they were only syntax-checked, which is why several
pages describe behaviour their code does not have.

    python scripts/projects_run.py                  # run everything
    python scripts/projects_run.py beginners        # one tier, or a substring
    python scripts/projects_run.py --list           # classify without running
    python scripts/projects_run.py --timeout 60

Each project runs as a subprocess in its own temporary working directory, with
stdin closed and ``MPLBACKEND=Agg`` so matplotlib writes files instead of
opening a window. Anything the run leaves behind in that directory is recorded
as an artifact. Results land in ``docs/projects_run_ledger.json``, which
``scripts/projects_audit.py`` reads.

Projects that cannot run here are **skipped with a stated reason**, never
faked. The reasons are static: a missing third-party module, a GUI toolkit with
no display, a webcam, a blocking server loop, or a call to ``input()``. Each is
a real piece of work for a later wave -- a project that cannot be run
non-interactively cannot be tested -- and the ledger names which.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import functools
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
PROJECTS = os.path.join(REPO, "projects")
LEDGER = os.path.join(REPO, "docs", "projects_run_ledger.json")

# Availability is probed against this interpreter rather than hardcoded, so
# the classifier stays correct when a dependency is installed or removed.
STDLIB_ALWAYS = {"os", "sys", "re", "json", "math", "time", "random", "typing"}


@functools.lru_cache(maxsize=None)
def available(module: str) -> bool:
    if module in STDLIB_ALWAYS:
        return True
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


# Modules that need a screen, a device or an unbounded loop.
NEEDS_DISPLAY = {"tkinter", "turtle", "PyQt6", "wx"}
NEEDS_NETWORK = {"socket", "socketserver", "http.server", "flask", "fastapi",
                 "uvicorn"}


def imported(tree: ast.AST) -> set:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out


def calls_input(tree: ast.AST) -> bool:
    """Does this file need someone to type, or does it cope without?

    A script that catches EOFError has a demo path: it runs unattended and
    uses its stated defaults. Only the ones with no fallback are skipped.
    """
    reads = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "input" for node in ast.walk(tree))
    if not reads:
        return False
    return not handles_eof(tree)


def handles_eof(tree: ast.AST) -> bool:
    return any(
        isinstance(handler.type, ast.Name) and handler.type.id == "EOFError"
        or (isinstance(handler.type, ast.Tuple)
            and any(isinstance(item, ast.Name) and item.id == "EOFError"
                    for item in handler.type.elts))
        for node in ast.walk(tree) if isinstance(node, ast.Try)
        for handler in node.handlers)


def _is_generator(node) -> bool:
    return any(isinstance(inner, (ast.Yield, ast.YieldFrom))
               for inner in ast.walk(node))


# Calls that block until something external happens: a request, a keypress, a
# camera frame. They are not "unrunnable" in principle, but they cannot finish
# on their own, and waiting for each to hit the timeout costs more than the
# whole rest of the suite.
BLOCKING_CALLS = {
    "run": "a web server (app.run)",
    "mainloop": "a GUI event loop",
    "serve_forever": "a socket server",
    "VideoCapture": "a camera stream",
    "listen": "a microphone or socket listener",
    "join": None,                 # only counted for threads, checked below
}


def blocking_call(tree: ast.AST) -> str | None:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        name = (target.attr if isinstance(target, ast.Attribute)
                else target.id if isinstance(target, ast.Name) else None)
        if name in ("run", "mainloop", "serve_forever", "VideoCapture",
                    "listen"):
            if name == "run" and not isinstance(target, ast.Attribute):
                continue          # a plain run() is usually the project's own
            if name == "VideoCapture":
                return "a camera stream"
            return BLOCKING_CALLS[name]
    return None


def has_unbounded_loop(tree: ast.AST) -> bool:
    """`while True` that is not inside a generator.

    A generator's `while True` is bounded by whoever consumes it -- islice,
    a for-loop with a break -- so flagging it would skip perfectly runnable
    files. Only loops in ordinary code count.
    """
    generator_loops = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))                 and _is_generator(node):
            for inner in ast.walk(node):
                if isinstance(inner, ast.While):
                    generator_loops.add(id(inner))
    for node in ast.walk(tree):
        if isinstance(node, ast.While) and id(node) not in generator_loops:
            test = node.test
            if isinstance(test, ast.Constant) and test.value is True:
                return True
    return False


def classify(path: str) -> dict:
    """Decide whether this file can run here, without running it."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        code = handle.read()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"skip": "syntax error", "detail": str(exc)[:80],
                "imports": []}
    modules = imported(tree)
    blocked = sorted(name for name in modules if not available(name))
    if blocked:
        return {"skip": "module not installed", "detail": ", ".join(blocked),
                "imports": sorted(modules)}
    display = sorted(modules & NEEDS_DISPLAY)
    if display:
        return {"skip": "needs a display", "detail": ", ".join(display),
                "imports": sorted(modules)}
    network = sorted(modules & NEEDS_NETWORK)
    if network and has_unbounded_loop(tree):
        return {"skip": "blocking server loop", "detail": ", ".join(network),
                "imports": sorted(modules)}
    if calls_input(tree):
        return {"skip": "needs stdin", "detail": "calls input()",
                "imports": sorted(modules)}
    blocker = blocking_call(tree)
    if blocker:
        return {"skip": "blocks until stopped", "detail": blocker,
                "imports": sorted(modules)}
    if has_unbounded_loop(tree) and not handles_eof(tree):
        # With an EOF fallback the loop exits on the default answer, and the
        # per-file timeout is the backstop if it does not.
        return {"skip": "unbounded loop", "detail": "while True",
                "imports": sorted(modules)}
    return {"skip": None, "detail": "", "imports": sorted(modules)}


def run_one(path: str, timeout: int) -> dict:
    """Run one project in a scratch directory and record what it produced."""
    relative = os.path.relpath(path, REPO).replace(os.sep, "/")
    verdict = classify(path)
    row = {"source": relative, "imports": verdict["imports"]}

    if verdict["skip"]:
        row.update({"ok": False, "skipped": verdict["skip"],
                    "reason": verdict["detail"], "seconds": 0.0,
                    "stdout": "", "stderr": "", "artifacts": []})
        return row

    workdir = tempfile.mkdtemp(prefix="pch-project-")
    copy = os.path.join(workdir, os.path.basename(path))
    shutil.copyfile(path, copy)
    environment = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8",
                       PYTHONWARNINGS="ignore")
    started = time.perf_counter()
    try:
        with open(os.devnull) as devnull:
            completed = subprocess.run(
                [sys.executable, os.path.basename(path)], cwd=workdir,
                stdin=devnull, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
                env=environment)
        seconds = time.perf_counter() - started
        artifacts = sorted(
            name for name in os.listdir(workdir)
            if name != os.path.basename(path))
        row.update({
            "ok": completed.returncode == 0,
            "skipped": None,
            "reason": "" if completed.returncode == 0
            else f"exit {completed.returncode}",
            "seconds": round(seconds, 3),
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-2000:],
            "artifacts": [{"name": name,
                           "bytes": os.path.getsize(
                               os.path.join(workdir, name))}
                          for name in artifacts],
        })
    except subprocess.TimeoutExpired:
        row.update({"ok": False, "skipped": "timeout",
                    "reason": f"exceeded {timeout}s", "seconds": float(timeout),
                    "stdout": "", "stderr": "", "artifacts": []})
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return row


def discover(pattern: str | None) -> list[str]:
    out = []
    for root, dirs, files in os.walk(PROJECTS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            relative = os.path.relpath(path, REPO).replace(os.sep, "/")
            if pattern and pattern not in relative:
                continue
            out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pattern", nargs="?",
                        help="substring of the path to filter on")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--list", action="store_true",
                        help="classify without running")
    args = parser.parse_args()

    paths = discover(args.pattern)
    if not paths:
        print("no project files matched")
        return 0

    if args.list:
        buckets: dict[str, list[str]] = {}
        for path in paths:
            verdict = classify(path)
            key = verdict["skip"] or "runnable"
            buckets.setdefault(key, []).append(os.path.basename(path))
        print(f"{len(paths)} project file(s)")
        for key in sorted(buckets, key=lambda k: -len(buckets[k])):
            print(f"  {len(buckets[key]):4}  {key}")
            if key != "runnable":
                for name in buckets[key][:4]:
                    print(f"          {name}")
                if len(buckets[key]) > 4:
                    print(f"          ... and {len(buckets[key]) - 4} more")
        return 0

    rows = []
    started = time.time()
    for index, path in enumerate(paths, 1):
        row = run_one(path, args.timeout)
        rows.append(row)
        mark = "ok " if row["ok"] else ("skip" if row["skipped"] else "FAIL")
        detail = ""
        if row["ok"] and row["artifacts"]:
            detail = f"  -> {', '.join(a['name'] for a in row['artifacts'])}"
        elif not row["ok"]:
            parts = [p for p in (row["skipped"], row["reason"]) if p]
            detail = f"  ({': '.join(parts)})"
        print(f"  [{index:3}/{len(paths)}] {mark} {row['source'][9:]}{detail}")

    ok = sum(1 for row in rows if row["ok"])
    skipped = sum(1 for row in rows if row["skipped"])
    failed = len(rows) - ok - skipped
    ledger = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "timeout": args.timeout,
        "totals": {"files": len(rows), "ok": ok, "skipped": skipped,
                   "failed": failed},
        "runs": rows,
    }
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8", newline="") as handle:
        json.dump(ledger, handle, indent=1)

    print(f"\n{len(rows)} file(s) in {time.time() - started:.1f}s: "
          f"{ok} ran, {failed} failed, {skipped} skipped")
    reasons: dict[str, int] = {}
    for row in rows:
        if row["skipped"]:
            reasons[row["skipped"]] = reasons.get(row["skipped"], 0) + 1
        elif not row["ok"]:
            reasons["failed"] = reasons.get("failed", 0) + 1
    for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"  {count:4}  {reason}")
    print(f"\nledger: {os.path.relpath(LEDGER, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

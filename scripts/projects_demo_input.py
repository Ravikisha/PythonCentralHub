"""Give input()-driven projects a demo path, and keep only the ones that work.

56 projects stop at `EOFError` the moment nothing is typed, so they never
appear in the run ledger and their pages have no real output to show. Each
needs the same three lines the earlier beginner projects got: a wrapper that
answers with a stated default when stdin is closed.

The awkward part is the default itself, which depends on what is being asked.
This infers it from the prompt — a `(y/n)` question gets `n`, a menu gets `1`,
"how many" gets a small number — and prints the answer it used so the captured
output never hides that a default was substituted.

Inference is a guess, so nothing is taken on trust: every rewritten file is
executed, and **any file that does not then run is reverted**. What survives is
only what was demonstrated to work.

    python scripts/projects_demo_input.py --report
    python scripts/projects_demo_input.py --apply
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
PROJECTS = os.path.join(REPO, "projects")

HELPER = '''

def ask(prompt="", default=""):
    """Read a line, or fall back to `default` when nobody is there to type.

    Without this the script raises EOFError the moment it runs unattended — in
    a test, a scheduled job, or the build that captures this output for the
    docs. The fallback is printed rather than silent, so a reader can always
    tell which answers were typed and which were assumed.
    """
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default
'''

# (pattern tried against the lowercased prompt, the answer to give)
RULES = (
    (r"\(y/n\)|\(yes/no\)|yes or no|again\?", "n"),
    (r"choice|option|select|menu|enter your", "1"),
    (r"how many|number of|count|length|size|how much", "5"),
    (r"file ?name|path to|filename", "demo.txt"),
    (r"url|website|link", "https://example.com"),
    (r"e-?mail", "demo@example.com"),
    (r"name", "Demo"),
    (r"password", "Password123@"),
    (r"search|query|keyword|word", "python"),
    (r"number|digit|integer|value|amount|age|year", "7"),
    (r"press enter|continue", ""),
)


EXIT_OPTION = re.compile(
    r"""["']\s*\(?([0-9]|[A-Za-z])[.)]?\s*[-:.]?\s*(?:exit|quit|close)""",
    re.I)


def exit_choice(code: str) -> str | None:
    """The menu entry that leaves, taken from what the program prints.

    Menu-driven projects loop until the user picks Exit. Answering "1" forever
    means they never terminate -- 14 of them timed out on exactly that -- so
    the default for a menu has to be the option that ends it, and the program
    itself advertises which that is.
    """
    matches = EXIT_OPTION.findall(code)
    return matches[-1] if matches else None


def default_for(prompt: str, code: str = "") -> str:
    lowered = prompt.lower()
    for pattern, answer in RULES:
        if re.search(pattern, lowered):
            if answer == "1" and code:
                return exit_choice(code) or answer
            return answer
    return (exit_choice(code) or "1") if code else "1"


def prompt_text(node: ast.Call) -> str:
    if node.args and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        return node.args[0].value
    if node.args and isinstance(node.args[0], ast.JoinedStr):
        return "".join(part.value for part in node.args[0].values
                       if isinstance(part, ast.Constant)
                       and isinstance(part.value, str))
    return ""


def rewrite(code: str) -> str | None:
    """Replace every `input(...)` with `ask(..., default)` and add the helper."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "input"]
    if not calls:
        return None

    lines = code.split("\n")
    # Rewrite from the end so earlier offsets stay valid.
    edits = sorted(calls, key=lambda n: (n.lineno, n.col_offset), reverse=True)
    for node in edits:
        if node.lineno != node.end_lineno:
            return None                    # multi-line call: leave it alone
        line = lines[node.lineno - 1]
        original = line[node.col_offset:node.end_col_offset]
        if not original.startswith("input("):
            return None
        inner = original[len("input("):-1].strip()
        answer = default_for(prompt_text(node), code)
        replacement = (f'ask({inner}, {answer!r})' if inner
                       else f'ask("", {answer!r})')
        lines[node.lineno - 1] = (line[:node.col_offset] + replacement
                                  + line[node.end_col_offset:])

    text = "\n".join(lines)
    if "def ask(" in text:
        return text
    last_import = 0
    for index, line in enumerate(text.split("\n")):
        if re.match(r"^\s*(import|from)\s", line):
            last_import = index
    out = text.split("\n")
    out.insert(last_import + 1, HELPER.rstrip("\n"))
    return "\n".join(out)


def runs_clean(path: str, timeout: int = 30) -> tuple[bool, str]:
    workdir = tempfile.mkdtemp(prefix="pch-demo-")
    try:
        shutil.copyfile(path, os.path.join(workdir, os.path.basename(path)))
        done = subprocess.run(
            [sys.executable, os.path.basename(path)], cwd=workdir,
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            env=dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8"))
        tail = [line for line in done.stderr.strip().split("\n")
                if line and not line.startswith(" ")]
        return done.returncode == 0, (tail[-1][:70] if tail else "")
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def candidates():
    for root, dirs, files in os.walk(PROJECTS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            code = io.open(path, encoding="utf-8", errors="replace").read()
            if "def ask(" in code or "input(" not in code:
                continue
            yield path, code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    kept, reverted, unchanged = [], [], []
    for path, original in candidates():
        updated = rewrite(original)
        if updated is None:
            unchanged.append((os.path.basename(path), "could not rewrite"))
            continue
        try:
            ast.parse(updated)
        except SyntaxError as exc:
            unchanged.append((os.path.basename(path), f"bad rewrite: {exc}"))
            continue

        if args.report:
            kept.append(os.path.basename(path))
            continue

        io.open(path, "w", encoding="utf-8", newline="").write(updated)
        ok, why = runs_clean(path, args.timeout)
        if ok:
            kept.append(os.path.basename(path))
            print(f"  kept     {os.path.basename(path)}")
        else:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            reverted.append((os.path.basename(path), why))
            print(f"  reverted {os.path.basename(path)}  ({why})")

    if args.report:
        print(f"{len(kept)} file(s) could be rewritten")
        for name in kept[:12]:
            print("   ", name)
        return 0

    print(f"\n{len(kept)} kept, {len(reverted)} reverted, "
          f"{len(unchanged)} left alone")
    if reverted:
        print("\nreverted because the demo path did not make them run:")
        for name, why in reverted[:15]:
            print(f"   {name:44} {why}")
    if unchanged:
        print(f"\n{len(unchanged)} could not be rewritten safely")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

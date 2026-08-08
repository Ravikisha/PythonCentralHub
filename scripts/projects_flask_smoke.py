"""Give Flask projects a way to run that is not "block on a socket forever".

21 projects end in `app.run(...)`, which never returns. That makes them
impossible to test, to schedule, or to capture output from — and it is why they
appear in the run ledger as "blocks until stopped" rather than as working
projects.

The fix is not to remove the server. It is to add the thing every web project
should have anyway: a smoke path that dispatches one request to each route
through Flask's test client and prints what came back. No socket is opened and
no port is bound, but the request goes through the real application object, so
what it prints is the app's actual behaviour.

    python scripts/projects_flask_smoke.py --report
    python scripts/projects_flask_smoke.py --apply
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
PROJECTS = os.path.join(REPO, "projects")

SMOKE = '''

def smoke_test():
    """Exercise every GET route once, without starting a server.

    `app.test_client()` dispatches a real request through the real application
    object -- no socket, no port, no waiting. A web project that cannot be
    driven this way cannot be tested either, so this is worth having whether or
    not anything is capturing the output.
    """
    print("smoke test: dispatching one request per route\\n")
    with app.test_client() as client:
        rules = sorted(app.url_map.iter_rules(), key=lambda rule: str(rule))
        checked = 0
        for rule in rules:
            if "GET" not in rule.methods or rule.arguments:
                continue
            response = client.get(str(rule))
            body = response.get_data(as_text=True)
            body = " ".join(body.split())[:60]
            print(f"  GET {str(rule):26} {response.status_code}  {body}")
            checked += 1
    print(f"\\n{checked} route(s) answered. Pass --serve to start the real "
          f"server instead.")
'''


def has_flask_app(code: str) -> bool:
    return bool(re.search(r"^\s*app\s*=\s*Flask\(", code, re.M))


def find_run(code: str):
    """The `app.run(...)` statement inside the __main__ guard, if there is one."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        source = ast.dump(node.test)
        if "__main__" not in source:
            continue
        for statement in node.body:
            for inner in ast.walk(statement):
                if (isinstance(inner, ast.Call)
                        and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "run"
                        and isinstance(inner.func.value, ast.Name)
                        and inner.func.value.id == "app"):
                    return node
    return None


def rewrite(code: str) -> str | None:
    node = find_run(code)
    if node is None:
        return None
    lines = code.split("\n")
    start, end = node.lineno - 1, node.end_lineno
    body = "\n".join(lines[start:end])
    indented = "\n".join("    " + line if line.strip() else line
                         for line in body.split("\n")[1:])
    replacement = [
        'if __name__ == "__main__":',
        "    # Serving is opt-in, because a run that never returns cannot be",
        "    # tested or captured. With no arguments the file answers every",
        "    # route once and exits; `--serve` starts the real server.",
        '    if "--serve" in sys.argv:',
        indented if indented.strip() else "        app.run()",
        "    else:",
        "        smoke_test()",
    ]
    updated = lines[:start] + replacement + lines[end:]
    text = "\n".join(updated)

    if not re.search(r"^import sys$", text, re.M):
        text = re.sub(r"(^(?:from|import)\s+\S+.*$)", r"import sys\n\1",
                      text, count=1, flags=re.M)
    if "def smoke_test(" not in text:
        marker = 'if __name__ == "__main__":'
        text = text.replace(marker, SMOKE.strip("\n") + "\n\n\n" + marker, 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    changed, skipped = [], []
    for root, dirs, files in os.walk(PROJECTS):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            code = io.open(path, encoding="utf-8", errors="replace").read()
            if not has_flask_app(code) or "def smoke_test(" in code:
                continue
            updated = rewrite(code)
            if updated is None:
                skipped.append((name, "no app.run() under __main__"))
                continue
            try:
                ast.parse(updated)
            except SyntaxError as exc:
                skipped.append((name, f"rewrite would not parse: {exc}"))
                continue
            changed.append(name)
            if args.apply:
                io.open(path, "w", encoding="utf-8",
                        newline="").write(updated)

    verb = "rewrote" if args.apply else "would rewrite"
    print(f"{verb} {len(changed)} Flask project(s)")
    for name in changed[:8]:
        print("   ", name)
    if len(changed) > 8:
        print(f"    ... and {len(changed) - 8} more")
    if skipped:
        print(f"\nskipped {len(skipped)}:")
        for name, why in skipped:
            print(f"    {name}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

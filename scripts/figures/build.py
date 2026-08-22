"""Render every committed figure for the docs site.

Discovers each ``scripts/figures/<group>/<page-slug>.py`` module, renders the
``FIGURES`` list it exports, and writes the SVG pair to
``public/images/<group>/<page-slug>/``.

Run with ``npm run figures``. The output SVGs are committed, so the Astro build
never needs Python or matplotlib.

Options::

    python scripts/figures/build.py                  # everything
    python scripts/figures/build.py phase-03         # only groups matching a filter
    python scripts/figures/build.py --list           # show what would be rendered
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PUBLIC = os.path.join(REPO, "public", "images")

# Page modules import `_style` directly; make that resolvable however we're run.
sys.path.insert(0, HERE)

from _style import render  # noqa: E402


def discover() -> list[tuple[str, str, str]]:
    """Return (group, slug, path) for every page figure module."""
    found: list[tuple[str, str, str]] = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if not d.startswith(("_", "."))]
        if root == HERE:
            continue
        group = os.path.relpath(root, HERE).replace(os.sep, "/")
        for f in sorted(files):
            if f.endswith(".py") and not f.startswith("_"):
                found.append((group, f[:-3], os.path.join(root, f)))
    return found


def load(path: str, name: str):
    """Import one page module, with its own sibling `_data` helper.

    Several groups ship a `_data.py`, and `sys.modules` caches by plain name —
    so without the pop below, the second group to be built silently receives the
    first group's datasets and fails with a confusing ImportError (or worse,
    renders the wrong data).
    """
    directory = os.path.dirname(os.path.abspath(path))
    sys.path.insert(0, directory)
    sys.modules.pop("_data", None)
    try:
        spec = importlib.util.spec_from_file_location(f"pchfig_{name}", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load figure module: {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if directory in sys.path:
            sys.path.remove(directory)
        sys.modules.pop("_data", None)
    return mod


LOCK = os.path.join(REPO, ".figure-build.lock")


def _alive(pid: int) -> bool:
    """True if a process with this pid exists. Signal 0 is the portable probe."""
    if pid <= 0:
        return False
    if os.name == "nt":
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, check=False)
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class BuildLock:
    """Serialise figure builds across processes.

    Every module here loads TensorFlow and trains something. Four builds in
    parallel exhausted memory on this machine and two of them were killed
    mid-render, so concurrent invocations queue instead of racing.
    """

    def __init__(self, path: str = LOCK, poll: float = 2.0):
        self.path = path
        self.poll = poll
        self.handle = None

    def __enter__(self):
        announced = False
        while True:
            try:
                self.handle = os.open(
                    self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.handle, str(os.getpid()).encode())
                return self
            except FileExistsError:
                if self._steal_if_stale():
                    continue
                if not announced:
                    holder = ""
                    try:
                        with open(self.path) as handle:
                            holder = f" (pid {handle.read().strip()})"
                    except OSError:
                        pass
                    print(f"  . another figure build is running{holder}; "
                          f"waiting")
                    announced = True
                time.sleep(self.poll)

    def _steal_if_stale(self) -> bool:
        """Remove the lock if the process that wrote it is gone.

        A killed build leaves the file behind and every later build then waits
        on it forever. Nothing else writes this file, so a holder pid that no
        longer exists means the lock is abandoned.
        """
        try:
            with open(self.path) as handle:
                pid = int(handle.read().strip())
        except (OSError, ValueError):
            return False
        if pid == os.getpid() or _alive(pid):
            return False
        print(f"  . removing a stale lock left by pid {pid}")
        try:
            os.unlink(self.path)
        except OSError:
            return False
        return True

    def __exit__(self, *_):
        if self.handle is not None:
            os.close(self.handle)
        try:
            os.unlink(self.path)
        except OSError:
            pass
        return False


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    modules = discover()

    if args:
        modules = [m for m in modules if any(a in f"{m[0]}/{m[1]}" for a in args)]

    if not modules:
        print("No figure modules matched.")
        return 0

    if "--list" in flags:
        for group, slug, path in modules:
            print(f"{group}/{slug}")
        return 0

    started = time.time()
    total = 0
    failed: list[str] = []

    with BuildLock():
        for group, slug, path in modules:
            try:
                mod = load(path, f"{group}_{slug}".replace("/", "_"))
                specs = getattr(mod, "FIGURES", [])
                if not specs:
                    print(f"  ! {group}/{slug}: no FIGURES exported, skipped")
                    continue
                out_dir = os.path.join(PUBLIC, *group.split("/"), slug)
                for spec in specs:
                    paths = render(spec, out_dir)
                    total += len(paths)
                rel = os.path.relpath(out_dir, REPO).replace(os.sep, "/")
                print(f"  + {group}/{slug}: {len(specs)} figure(s) -> {rel}/")
            except Exception as exc:  # keep going; report at the end
                failed.append(f"{group}/{slug}: {exc}")
                print(f"  x {group}/{slug}: {exc}")

    elapsed = time.time() - started
    print(f"\n{total} SVG file(s) in {elapsed:.1f}s")

    if failed:
        print(f"\n{len(failed)} module(s) failed:")
        for f in failed:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

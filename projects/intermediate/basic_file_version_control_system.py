"""Basic file version control -- commit, diff, log and revert.

The earlier version of this file advertised "revert to previous versions" and
stored exactly one version per file: `self.versions[name] = version_data`
overwrote the previous entry on every commit. `log` printed a single line and
`revert` could only ever restore the most recent state, which is not version
control -- it is a backup with a history-shaped label on it.

The fix is one character of data structure: a list per file instead of a dict
entry. Everything else here follows from that.

    python basic_file_version_control_system.py         # scripted demo
    python basic_file_version_control_system.py --test  # unit tests
"""

import difflib
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

DEMO_ANSWERS = iter([])


def ask(prompt="", default=""):
    """Read a line, or take the next scripted answer when nobody is there."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        answer = next(DEMO_ANSWERS, default)
        print(f"{answer}   (scripted demo answer)")
        return answer


def make_diff(old: str, new: str, name: str = "file",
              old_label: str = "before", new_label: str = "after") -> str:
    """A unified diff between two versions of a text file.

    `difflib.unified_diff` is the same format `git diff` prints, and it works
    on any pair of line lists. Storing content and computing the diff on
    demand is the simpler half of the trade-off; the other half is below.
    """
    lines = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"{name} ({old_label})", tofile=f"{name} ({new_label})")
    return "".join(lines)


class BasicFileVersionControl:
    """A repository is a directory plus a JSON index of every commit."""

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.version_file = os.path.join(repo_path, ".versions.json")
        # name -> list of commits, oldest first. The list is the whole fix.
        self.versions: dict[str, list] = {}

        os.makedirs(repo_path, exist_ok=True)
        if os.path.exists(self.version_file):
            with open(self.version_file, encoding="utf-8") as handle:
                self.versions = json.load(handle)

    def _save(self):
        # JSON rather than pickle: an index that only Python can read, and
        # that executes arbitrary code when loaded, is a poor choice for a
        # file format meant to outlive the program that wrote it.
        with open(self.version_file, "w", encoding="utf-8") as handle:
            json.dump(self.versions, handle, indent=1)

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def hash_file(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as handle:
            while chunk := handle.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def commit(self, file_path, message):
        """Record the current contents as a new version."""
        if not os.path.exists(file_path):
            print("File does not exist.")
            return None

        with open(file_path, encoding="utf-8") as handle:
            content = handle.read()
        file_hash = self.hash_content(content)
        name = os.path.basename(file_path)
        history = self.versions.setdefault(name, [])

        if history and history[-1]["hash"] == file_hash:
            print("No changes detected.")
            return None

        version = {
            "hash": file_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "message": message,
            "content": content,
        }
        history.append(version)
        self._save()
        print(f"[{name} v{len(history)}] {message}  ({file_hash[:8]})")
        return len(history)

    def revert(self, file_name, version=None):
        """Restore a specific version -- the last one by default.

        `version` is 1-based, matching what `log` prints. Reverting to
        anything other than the newest commit is the capability the previous
        implementation claimed and did not have.
        """
        history = self.versions.get(file_name)
        if not history:
            print("No version history found for this file.")
            return None

        index = len(history) - 1 if version is None else version - 1
        if not 0 <= index < len(history):
            print(f"No version {version}; {file_name} has {len(history)}.")
            return None

        target = history[index]
        with open(os.path.join(self.repo_path, file_name), "w",
                  encoding="utf-8") as handle:
            handle.write(target["content"])
        print(f"Reverted {file_name} to v{index + 1} ({target['message']})")
        return target["content"]

    def log(self, file_name):
        """Every commit for a file, oldest first."""
        history = self.versions.get(file_name)
        if not history:
            print("No version history found for this file.")
            return []
        print(f"History of {file_name}: {len(history)} version(s)")
        for number, version in enumerate(history, start=1):
            print(f"  v{number}  {version['timestamp']}  "
                  f"{version['hash'][:8]}  {version['message']}")
        return history

    def diff(self, file_name, first=None, second=None):
        """Diff two committed versions, or the last one against the file."""
        history = self.versions.get(file_name)
        if not history:
            print("No version history found for this file.")
            return ""
        if first is None:
            first = len(history) - 1 if len(history) > 1 else 1
        if second is None:
            second = len(history)
        old, new = history[first - 1], history[second - 1]
        text = make_diff(old["content"], new["content"], file_name,
                         f"v{first}", f"v{second}")
        print(text or "(identical)")
        return text

    def storage_report(self):
        """What storing whole copies costs, measured on this repository.

        Real version control stores diffs (or packs objects) precisely
        because this number grows with versions x file size rather than with
        the size of the changes.
        """
        total = sum(len(v["content"]) for h in self.versions.values()
                    for v in h)
        newest = sum(len(h[-1]["content"]) for h in self.versions.values()
                     if h)
        diffs = 0
        for history in self.versions.values():
            for older, newer in zip(history, history[1:]):
                diffs += len(make_diff(older["content"], newer["content"]))
            if history:
                diffs += len(history[0]["content"])
        print(f"\nstored as full copies: {total:,} bytes")
        print(f"newest versions only:  {newest:,} bytes")
        print(f"as first copy + diffs: {diffs:,} bytes "
              f"({diffs / total:.0%} of the full-copy cost)")
        return total, diffs


def demo(repo_path="./repo"):
    """Three commits, a diff, and a revert to the middle one."""
    vcs = BasicFileVersionControl(repo_path)
    target = os.path.join(repo_path, "notes.txt")

    stages = [
        ("Shopping list\n- bread\n- milk\n", "first draft"),
        ("Shopping list\n- bread\n- milk\n- eggs\n", "add eggs"),
        ("Shopping list\n- sourdough\n- milk\n- eggs\n- coffee\n",
         "better bread, and coffee"),
    ]
    for content, message in stages:
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(content)
        vcs.commit(target, message)

    # Committing the same content twice must not create a version.
    vcs.commit(target, "no change at all")

    print()
    vcs.log("notes.txt")
    print("\ndiff v2 -> v3:")
    vcs.diff("notes.txt", 2, 3)

    print("reverting to v1, then reading the file back:")
    vcs.revert("notes.txt", 1)
    with open(target, encoding="utf-8") as handle:
        print("   " + handle.read().replace("\n", "\n   ").rstrip())
    print("\nthe history is untouched -- reverting is not deleting:")
    vcs.log("notes.txt")
    vcs.storage_report()
    return vcs


def main():
    repo_path = "./repo"
    vcs = BasicFileVersionControl(repo_path)

    while True:
        print("\nBasic File Version Control System")
        print("1. Commit File   2. Revert File   3. View Log")
        print("4. Exit          5. Diff versions")
        choice = ask("Enter your choice: ", "4")

        if choice == "1":
            file_path = ask("Enter the file path to commit: ", "demo.txt")
            vcs.commit(file_path, ask("Enter commit message: ", "update"))
        elif choice == "2":
            name = ask("Enter the file name to revert: ", "demo.txt")
            raw = ask("Version number (blank for latest): ", "")
            vcs.revert(name, int(raw) if raw.isdigit() else None)
        elif choice == "3":
            vcs.log(ask("Enter the file name to view log: ", "demo.txt"))
        elif choice == "5":
            vcs.diff(ask("File name: ", "demo.txt"))
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import shutil
        import tempfile
        import unittest

        class TestVersionControl(unittest.TestCase):
            def setUp(self):
                self.dir = tempfile.mkdtemp(prefix="fvcs-")
                self.vcs = BasicFileVersionControl(self.dir)
                self.path = os.path.join(self.dir, "f.txt")

            def tearDown(self):
                shutil.rmtree(self.dir, ignore_errors=True)

            def write(self, text):
                with open(self.path, "w", encoding="utf-8") as handle:
                    handle.write(text)

            def test_history_accumulates(self):
                for text in ("one\n", "two\n", "three\n"):
                    self.write(text)
                    self.vcs.commit(self.path, text.strip())
                self.assertEqual(len(self.vcs.versions["f.txt"]), 3)

            def test_identical_commit_ignored(self):
                self.write("same\n")
                self.vcs.commit(self.path, "a")
                self.vcs.commit(self.path, "b")
                self.assertEqual(len(self.vcs.versions["f.txt"]), 1)

            def test_revert_to_older_version(self):
                self.write("one\n")
                self.vcs.commit(self.path, "one")
                self.write("two\n")
                self.vcs.commit(self.path, "two")
                self.assertEqual(self.vcs.revert("f.txt", 1), "one\n")
                # ...and the newer version is still there afterwards.
                self.assertEqual(len(self.vcs.versions["f.txt"]), 2)

            def test_diff_shows_the_change(self):
                self.write("a\nb\n")
                self.vcs.commit(self.path, "1")
                self.write("a\nc\n")
                self.vcs.commit(self.path, "2")
                text = self.vcs.diff("f.txt", 1, 2)
                self.assertIn("-b", text)
                self.assertIn("+c", text)

            def test_index_survives_reopening(self):
                self.write("persisted\n")
                self.vcs.commit(self.path, "once")
                reopened = BasicFileVersionControl(self.dir)
                self.assertEqual(len(reopened.versions["f.txt"]), 1)

        unittest.main(argv=sys.argv[:1], exit=False)
    elif "--menu" in sys.argv:
        main()
    else:
        # The scripted demo is the default. `sys.stdin.isatty()` looks like
        # the right test and is not: under Git Bash it returns True even with
        # stdin redirected from /dev/null, so the menu ran unattended and the
        # captured transcript was one line long.
        demo()

"""Verify docs pages: internal links, figure assets, sidebar order, component imports.

Runs in seconds and catches the mistakes a full Astro build would take ~30 minutes
to surface (and some it would not surface at all, like a link to a page that does
not exist — Starlight renders those happily and 404s at runtime).

    python scripts/check_docs.py "src/content/docs/Machine Learning"
    python scripts/check_docs.py            # every module

Exit code 1 if anything is wrong.
"""

from __future__ import annotations

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "src", "content", "docs")
PUBLIC = os.path.join(REPO, "public")


def slugify(part: str) -> str:
    """Reproduce Astro's content-collection slug for one path segment.

    Lowercase, drop characters Astro strips, and turn each remaining space into a
    hyphen — so "Phase 03 - Supervised Learning" becomes
    "phase-03---supervised-learning" (three hyphens), and an ampersand vanishes,
    leaving a double hyphen behind it.
    """
    s = part.lower()
    s = re.sub(r"[^\w\s-]", "", s)   # drop (), &, commas, quotes, etc.
    s = s.replace("_", "-")
    return s.replace(" ", "-")


def route_for(path: str) -> str:
    rel = os.path.relpath(path, DOCS)
    parts = rel.replace(os.sep, "/").split("/")
    parts[-1] = parts[-1][: -len(".mdx")] if parts[-1].endswith(".mdx") else parts[-1]
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "/".join(slugify(p) for p in parts) + "/"


def walk(root: str) -> list[str]:
    out = []
    for dirpath, _, files in os.walk(root):
        out.extend(
            os.path.join(dirpath, f) for f in sorted(files) if f.endswith(".mdx")
        )
    return sorted(out)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else DOCS
    target = target if os.path.isabs(target) else os.path.join(REPO, target)

    all_routes = {route_for(p) for p in walk(DOCS)}
    pages = walk(target)
    problems: list[str] = []
    # Keyed by (directory, order): Starlight autogenerates the sidebar per
    # folder, so two pages in different folders may share an order value
    # without ever competing for a position.
    orders: dict[tuple[str, float], list[str]] = {}

    for path in pages:
        rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()

        # --- sidebar order ------------------------------------------------
        # Fractional orders are legitimate: the Deep Learning module inserts
        # pages as 401.5 or 473.3 rather than renumbering their neighbours.
        m = re.search(r"^\s+order:\s*(\d+(?:\.\d+)?)\s*$", text, re.M)
        if m:
            folder = rel.rsplit('/', 1)[0] if '/' in rel else ''
            orders.setdefault((folder, float(m.group(1))), []).append(rel)
        else:
            problems.append(f"{rel}: no sidebar.order in frontmatter")

        # --- internal links -----------------------------------------------
        # Markdown links only — `![alt](path)` is an image, not a route.
        for link in re.findall(r"(?<!!)\]\((/[^)\s#]*)", text):
            if link.startswith("/images/") or link.startswith("/scripts/"):
                continue
            normalised = link if link.endswith("/") else link + "/"
            if normalised not in all_routes:
                problems.append(f"{rel}: dead internal link {link}")

        # --- Figure assets --------------------------------------------------
        for block in re.findall(r"<Figure\b[^>]*?/>", text, re.S):
            src = re.search(r'src="([^"]+)"', block)
            if not src:
                problems.append(f"{rel}: <Figure> without src")
                continue
            # A Figure is satisfied either by a themed pair or by one standalone
            # file. Checking both beats parsing the `single` attribute out of a
            # block whose caption prose may contain the word "single".
            base = src.group(1)
            pair = [base + "-dark.svg", base + "-light.svg"]

            def exists(p: str) -> bool:
                return os.path.exists(os.path.join(PUBLIC, p.lstrip("/")))

            if not (all(exists(p) for p in pair) or exists(base)):
                problems.append(f"{rel}: missing figure asset {base} (-dark/-light)")
            if 'alt="' not in block:
                problems.append(f"{rel}: <Figure> without alt text")

        # --- component imports resolve -------------------------------------
        for imp in re.findall(r'from\s+"((?:\.\./)+components/[^"]+)"', text):
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), imp))
            if not os.path.exists(resolved):
                problems.append(f"{rel}: import does not resolve: {imp}")

        # --- components used but not imported --------------------------------
        for comp in ("Figure", "Quiz", "AlgorithmCard", "DataCampExercise"):
            if re.search(rf"<{comp}\b", text) and f"import {comp} " not in text:
                problems.append(f"{rel}: uses <{comp}> without importing it")

        # --- currency signs swallowed as inline math -------------------------
        # Two `$` in prose become a math span. Real math carries a backslash
        # command or a sub/superscript; accidental spans are English words.
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        prose = re.sub(r"\{`.*?`\}", "", prose, flags=re.S)
        prose = re.sub(r"^\$\$.*?^\$\$", "", prose, flags=re.S | re.M)
        for m in re.finditer(r"(?<![\\$])\$([^$\n]{1,200}?)\$(?!\$)", prose):
            body = m.group(1)
            if re.search(r"\\|[_^]", body):
                continue
            if len(re.findall(r"[A-Za-z]{3,}", body)) >= 3:
                snippet = body[:60].replace("\n", " ")
                problems.append(
                    f"{rel}: prose swallowed as inline math (unescaped $?): ${snippet}...$"
                )

        # --- frontmatter YAML that will not parse -----------------------------
        # An unquoted YAML scalar containing ": " is a mapping, not a string, so
        # `description: one thing: another` fails the whole content collection
        # with "incomplete explicit mapping pair" — and takes the entire module
        # down, not just the one page. Quote the value or reword it.
        fm = re.match(r"---\n(.*?)\n---", text, re.S)
        if fm:
            for offset, line in enumerate(fm.group(1).splitlines(), 2):
                pair = re.match(r"^(\w[\w.]*):\s+(.*)$", line)
                if not pair:
                    continue
                value = pair.group(2)
                if not value or value[0] in "\"'|>[{":
                    continue
                if ": " in value or value.rstrip().endswith(":"):
                    problems.append(
                        f"{rel}:{offset}: frontmatter '{pair.group(1)}' is an "
                        f"unquoted YAML scalar containing ':' — quote it or "
                        f"reword"
                    )

        # --- prose braces MDX would evaluate as JavaScript --------------------
        # `{A, B, C}` in prose is a JSX expression: the page compiles and then
        # throws "A is not defined" at runtime. Backslash-escaping does NOT
        # work here — remarkEscapeBraces turns the literal brace into a visible
        # `&#123;`. Wrap the set in inline math instead: `$\{A, B, C\}$`.
        def _blank(m):
            return "".join("\n" if c == "\n" else " " for c in m.group(0))

        # Fences indented inside a list item still start a code block, so allow
        # leading whitespace — otherwise `showLineNumbers{1}` on an indented
        # fence reads as a prose brace.
        scan = re.sub(r"^[ \t]*```.*?^[ \t]*```", _blank, text, flags=re.S | re.M)
        scan = re.sub(r"`[^`\n]*`", _blank, scan)
        scan = re.sub(r"\$\$.*?\$\$", _blank, scan, flags=re.S)
        # inline math may wrap onto the next line, so allow one newline inside
        scan = re.sub(r"(?<!\\)\$[^$]{1,300}?\$", _blank, scan)
        scan = re.sub(r"^---\n.*?\n---", _blank, scan, flags=re.S)
        scan = re.sub(r"^<[A-Z]\w*[\s\S]*?^/>", _blank, scan, flags=re.M)
        # Single-line self-closing components too. `showLineNumbers={1}`
        # on a one-line <FileCode ... /> is a JSX attribute, not a prose
        # brace, and the multi-line rule above never sees it.
        scan = re.sub(r"<[A-Z]\w*[^<>]*?/>", _blank, scan)
        scan = re.sub(r"^import .*$", _blank, scan, flags=re.M)
        src_lines = text.splitlines()
        seen_lines: set[int] = set()
        for m in re.finditer(r"[{}]", scan):
            lineno = scan[: m.start()].count("\n") + 1
            if lineno in seen_lines:
                continue
            seen_lines.add(lineno)
            problems.append(
                f"{rel}:{lineno}: brace in prose — MDX will evaluate it as JS. "
                f"Use inline math: {src_lines[lineno - 1].strip()[:80]}"
            )

        # --- `<` that MDX will read as the start of a JSX tag ------------------
        # `<1 ms` or `<0.05` in prose is a parse error: MDX expects a tag name
        # after `<`. Write "under 1 ms", or wrap it in backticks or math.
        for m in re.finditer(r"<(?=\d)", scan):
            lineno = scan[: m.start()].count("\n") + 1
            problems.append(
                f"{rel}:{lineno}: '<' before a digit — MDX reads it as a JSX "
                f"tag. Reword or use inline code: "
                f"{src_lines[lineno - 1].strip()[:70]}"
            )

        # --- a brace that already leaked through as a visible entity ----------
        if "&#123;" in text or "&#125;" in text:
            problems.append(f"{rel}: literal &#123;/&#125; in the source")

        # --- bare pipes inside inline math in a table row --------------------
        # A table cell splits on every `|`, so `$\tfrac{|A|}{|B|}$` tears the
        # row apart and leaves an unclosed brace. MDX then fails to compile.
        # Escape as `\|`, or rename the quantity (n_A rather than |A|).
        for lineno, line in enumerate(text.splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue
            for m in re.finditer(r"\$[^$\n]*\$", line):
                if re.search(r"(?<!\\)\|", m.group(0)):
                    problems.append(
                        f"{rel}:{lineno}: unescaped | inside inline math in a "
                        f"table row: {m.group(0)[:60]}"
                    )

        # --- a backtick inside a template-literal prop ------------------------
        # `code={`...`}` is a JS template literal, so a backtick anywhere in the
        # Python inside it CLOSES the literal early. MDX then hands the rest to
        # acorn and fails with "Unexpected content after expression". Docstrings
        # referring to `subset` are the usual culprit — drop the backticks.
        for m in re.finditer(r"(\w+)=\{`", text):
            start = m.end()
            end = text.find("`}", start)
            if end == -1:
                problems.append(
                    f"{rel}: unterminated {m.group(1)}={{`...`}} prop"
                )
                break
            # An escaped backtick (\`) is fine and used deliberately in hints.
            stray_m = re.search(r"(?<!\\)`", text[start:end])
            if stray_m:
                stray = start + stray_m.start()
                lineno = text[:stray].count("\n") + 1
                problems.append(
                    f"{rel}:{lineno}: backtick inside {m.group(1)}={{`...`}} — it "
                    f"ends the template literal early: "
                    f"{text.splitlines()[lineno - 1].strip()[:70]}"
                )

    for (folder, order), files in sorted(orders.items()):
        if len(files) > 1:
            problems.append(f"duplicate sidebar.order {order:g} in {folder}: "
                            f"{', '.join(files)}")

    print(f"checked {len(pages)} page(s) under {os.path.relpath(target, REPO)}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("no problems found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

/**
 * lint-dsa-mdx.mjs — catch the two MDX bugs that break a page at build time and
 * are invisible to every other check in this repo.
 *
 * WHY THIS EXISTS
 * ---------------
 * `npm run build` is off-limits here (~800 content pages, over ten minutes), so
 * nothing in the normal loop actually compiles an .mdx file. `dsa:audit` only
 * greps for section headings, and `tsc` never sees these files. Both bugs below
 * shipped undetected at least once:
 *
 * 1. An unescaped backtick inside a JSX template-literal attribute
 *    (`hint={`…`}`, `code={…}`, `desc={…}`, …). Markdown prose is full of
 *    inline-code backticks, and one of them inside such an attribute terminates
 *    the literal early — a parse error, not a rendering glitch. Escaped
 *    backticks (\`) are fine and are handled here.
 *
 * 2. A component used in the body but never imported — `<Quiz>` without its
 *    import line. Found exactly this on Cyclic Sort.mdx, a page the audit
 *    scored as complete.
 *
 * 3. An unescaped `|` inside a markdown table cell. GFM splits cells before it
 *    parses inline code, so `` `mask | (1 << i)` `` in a table row silently
 *    shifts every following column. Write `\|`. Found one shipped instance on
 *    BFS and Dijkstra with Extra State.mdx.
 *
 * 4. Frontmatter that is not valid YAML. This one fails the *whole build* at
 *    `astro sync` with "incomplete explicit mapping pair" and a stack trace that
 *    names no file, so it is expensive to locate by hand. The usual cause is an
 *    unquoted value containing `: ` — `description: The default sheet: 150
 *    problems` parses as a nested mapping. Quote the value.
 *    Found on Phase-00/Sheet - NeetCode 150.mdx after it had broken the build.
 *
 * Usage: node scripts/lint-dsa-mdx.mjs [dir]     (npm run dsa:lint)
 * Exits 1 if anything is found, so it can gate a commit.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import yaml from "js-yaml";
import { join, relative } from "node:path";

const ROOT = process.argv[2] ?? "src/content/docs/DSA with Python";

/** Attributes whose values are written as template literals in this corpus. */
const TEMPLATE_ATTRS = ["hint", "code", "solution", "sct", "desc", "title", "lib", "caption"];

/** Names that look like components but are not — MDX/HTML built-ins. */
const NOT_COMPONENTS = new Set(["Fragment"]);

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

/** Line number of a character offset, 1-based, for a clickable report. */
const lineAt = (text, index) => text.slice(0, index).split("\n").length;

/**
 * Walk forward from just after an opening backtick to the terminator, honouring
 * backslash escapes. Returns the index of the closing backtick, or -1.
 */
function findLiteralEnd(text, start) {
  for (let i = start; i < text.length; i++) {
    if (text[i] === "\\") {
      i++;
      continue;
    }
    if (text[i] === "`") return i;
  }
  return -1;
}

const problems = [];
const files = walk(ROOT);

for (const file of files) {
  const text = readFileSync(file, "utf8");
  const rel = relative(process.cwd(), file);

  // ── 0. frontmatter must be valid YAML ───────────────────────────────────
  // Checked first because a failure here breaks `astro sync`, and therefore the
  // entire build, with an error that names no file.
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) {
    problems.push(`${rel}:1 — no frontmatter block`);
  } else {
    try {
      yaml.load(fm[1]);
    } catch (err) {
      const reason = String(err.message).split("\n")[0];
      problems.push(
        `${rel}:1 — frontmatter is not valid YAML: ${reason} ` +
          `(most often an unquoted value containing ": " — wrap it in double quotes)`,
      );
    }
  }

  // ── 1. template-literal attributes ──────────────────────────────────────
  const attrPattern = new RegExp(`(${TEMPLATE_ATTRS.join("|")})=\\{\``, "g");
  for (const m of text.matchAll(attrPattern)) {
    const end = findLiteralEnd(text, m.index + m[0].length);
    if (end === -1) {
      problems.push(`${rel}:${lineAt(text, m.index)} — ${m[1]}={\` is never terminated`);
      continue;
    }
    // A correctly-formed attribute closes as `}. Anything else means the
    // literal ended early, i.e. an unescaped backtick inside the value.
    if (text.slice(end, end + 2) !== "`}") {
      problems.push(
        `${rel}:${lineAt(text, end)} — unescaped backtick inside ${m[1]}={\`…\`} ` +
          `(escape it as \\\` or rewrite with straight quotes)`,
      );
    }
  }

  // ── 2. unescaped pipes inside table cells ───────────────────────────────
  // Only inline-code spans are checked: prose pipes in a table are already
  // visibly broken, whereas a pipe inside backticks looks safe and is not.
  text.split("\n").forEach((line, idx) => {
    if (!line.startsWith("|")) return;
    for (const span of line.match(/`[^`]*`/g) ?? []) {
      if (span.includes("|") && !span.includes("\\|")) {
        problems.push(
          `${rel}:${idx + 1} — unescaped \`|\` inside a table cell: ${span} ` +
            `(write \\| — backticks do not protect it)`,
        );
      }
    }
  });

  // ── 3. imports stranded inside a fenced code block ──────────────────────
  // MDX only honours ESM imports at the top level; anything inside ``` is
  // literal text. Two pages shipped with their ONLY `import ProblemLadder`
  // line sitting inside a python fence, which meant the component was never
  // imported at all *and* the displayed Python was syntactically invalid.
  //
  // Check 4 below used to miss this, because its regex matched the in-fence
  // line and concluded the component was imported. So the fence mask is
  // computed once here and reused there.
  const lines = text.split("\n");
  const inFence = new Array(lines.length).fill(false);
  {
    let fence = null;
    lines.forEach((line, idx) => {
      const m = /^(`{3,}|~{3,})/.exec(line);
      if (m) {
        if (fence === null) fence = m[1];
        else if (line.startsWith(fence)) fence = null;
        inFence[idx] = true; // the delimiter itself counts as fenced
        return;
      }
      inFence[idx] = fence !== null;
    });
  }

  lines.forEach((line, idx) => {
    if (inFence[idx] && /^import\s+\w+\s+from/.test(line)) {
      problems.push(
        `${rel}:${idx + 1} — \`${line.trim()}\` is inside a fenced code block, ` +
          `so MDX treats it as text: the component is NOT imported`,
      );
    }
  });

  // ── 4. used-but-not-imported components ─────────────────────────────────
  // Both sides ignore fenced blocks: an import in there does not count, and
  // a `<Node>` in a code comment is not a component usage.
  const unfenced = lines.map((line, idx) => (inFence[idx] ? "" : line)).join("\n");
  const imported = new Set([...unfenced.matchAll(/^import\s+(\w+)\s+from/gm)].map((m) => m[1]));
  const used = new Set(
    [...unfenced.matchAll(/<([A-Z]\w*)/g)]
      .map((m) => m[1])
      .filter((name) => !NOT_COMPONENTS.has(name)),
  );
  for (const name of used) {
    if (!imported.has(name)) {
      const at = text.indexOf(`<${name}`);
      problems.push(`${rel}:${lineAt(text, at)} — <${name}> is used but never imported`);
    }
  }

  // ── 5. LaTeX commands collapsed into a control character ────────────────
  // `\alpha`, `\text`, `\beta`, `\v…`, `\f…` are all one backslash away from a C
  // escape. Push a page's content through a tool that interprets escapes once —
  // a shell heredoc, a careless replace() — and `\alpha` silently becomes BEL +
  // "lpha". It renders as "lpha" with an invisible control byte, and it also
  // makes any generated YAML unparseable.
  //
  // Found three of these in the wild, so this is not hypothetical.
  const CONTROL = { "\x07": "a", "\x08": "b", "\x09": "t", "\x0b": "v", "\x0c": "f" };
  lines.forEach((line, idx) => {
    for (const [ch, letter] of Object.entries(CONTROL)) {
      // A tab used for indentation is ordinary; one sitting inside $…$ maths, or
      // directly before a LaTeX-looking word, is a collapsed backslash.
      if (!line.includes(ch)) continue;
      const suspicious =
        /\$[^$]*[\x07\x08\x09\x0b\x0c][^$]*\$/.test(line) ||
        new RegExp(`[\\x07\\x08\\x09\\x0b\\x0c](?:lpha|eta|ext|rac|au|imes)`).test(line);
      if (suspicious) {
        problems.push(
          `${rel}:${idx + 1} — a LaTeX command collapsed into a control character ` +
            `(0x0${ch.charCodeAt(0).toString(16)}): this was almost certainly \\${letter}… ` +
            `and now renders with the backslash and first letter missing`,
        );
        break;
      }
    }
  });
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`MDX lint — ${files.length} pages under ${ROOT}`);
console.log(bar);

if (problems.length === 0) {
  console.log(
    "\nOK — frontmatter parses, no unescaped backticks or pipes, no missing imports.\n",
  );
  process.exit(0);
}

console.log(`\n${problems.length} problem(s):`);
for (const p of problems) console.log(`  · ${p}`);
console.log("\nEach of these is a build-time parse or reference error.\n");
process.exit(1);

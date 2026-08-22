// Catch math that renders as a KaTeX error while every other check passes.
//
// remark-math ends a math span at the next literal `$`, so an escaped `\$` meant
// as a dollar sign truncates the span and KaTeX is handed the fragment before it.
// On one Chapter 6 page that produced seven `katex-error` nodes in the rendered
// HTML while `mdxcheck` reported the file as fine — mdxcheck compiles the MDX and
// KaTeX is configured with `throwOnError: false`, so a parse error is a rendered
// error node rather than a build failure.
//
// Use `\mathdollar` (or `\textdollar` in text mode) instead. Both render the same
// glyph without putting a `$` character in the source.
//
//   node scripts/lint-math.mjs "src/content/docs/Some Module"
//
// Exits 1 on a finding so it can gate a module.

import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = process.argv[2] || "src/content/docs";

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (e.endsWith(".mdx")) out.push(p);
  }
  return out;
}

/** Blank out fenced code and JSX attribute values; only prose/math is left. */
function stripCode(src) {
  const keepNewlines = (m) => m.replace(/[^\n]/g, " ");
  return src
    .replace(/```[\s\S]*?```/g, keepNewlines)
    .replace(/\{`[\s\S]*?`\}/g, keepNewlines)
    .replace(/`[^`\n]*`/g, keepNewlines);
}

const RULES = [
  {
    // The one that bit us: a backslash-escaped dollar anywhere outside code.
    re: /\\\$/g,
    what: "escaped dollar sign in math",
    fix: "use \\mathdollar (math mode) or \\textdollar (inside \\text{})",
  },
];

const files = walk(ROOT).sort();
let findings = 0;
const byModule = new Map();

for (const f of files) {
  const src = stripCode(readFileSync(f, "utf8"));
  const rel = relative(ROOT, f).replace(/\\/g, "/");
  for (const rule of RULES) {
    rule.re.lastIndex = 0;
    let m;
    while ((m = rule.re.exec(src)) !== null) {
      const line = src.slice(0, m.index).split("\n").length;
      const text = src.split("\n")[line - 1].trim().slice(0, 96);
      console.log(`  ${rel}:${line}  ${rule.what}`);
      console.log(`     ${text}`);
      console.log(`     -> ${rule.fix}`);
      findings++;
      const mod = rel.split("/")[0];
      byModule.set(mod, (byModule.get(mod) ?? 0) + 1);
    }
  }
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`math lint — ${files.length} pages under ${ROOT}`);
console.log(bar);

if (findings === 0) {
  console.log("\nOK — no math span is truncated by a literal dollar sign.");
  process.exit(0);
}
console.log(`\n${findings} site(s), by module:`);
for (const [mod, n] of [...byModule].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(6)}  ${mod}`);
}
console.log("\nFAIL — these render as katex-error nodes that mdxcheck does not see.");
process.exit(1);

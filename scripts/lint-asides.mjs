/**
 * lint-asides — two silent renderers, caught before they ship.
 *
 * 1. Starlight aside titles are plain text. The label of a `:::caution[...]` is
 *    rendered by taking only its leading text node, so
 *
 *        :::danger[`np.linalg.eig` does not tell you whether it is valid]
 *
 *    renders as the title "np.linalg.eig" and silently drops the rest of the
 *    sentence. Inline math truncates the same way: "An orthogonal $\mathbf{P}$
 *    is a property of symmetry" renders as "An orthogonal ". Nothing warns.
 *
 * 2. Inline math in a heading renders correctly in the body, but the table of
 *    contents takes the *text content* of the rendered KaTeX, so a heading
 *    "Rotations in $\mathbb{R}^2$" appears in the sidebar as
 *    "Rotations in R2\mathbb{R}^2R2".
 *
 * Usage:
 *   node scripts/lint-asides.mjs                 census over all docs, exit 0
 *   node scripts/lint-asides.mjs "<dir>"         gate one subtree, exit 1 on any hit
 */

import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const DOCS = resolve("src/content/docs");
const scope = process.argv[2] ? resolve(process.argv[2]) : null;
const root = scope ?? DOCS;

function walk(dir) {
  let out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out = out.concat(walk(p));
    else if (e.endsWith(".mdx")) out.push(p);
  }
  return out;
}

const ASIDE = /^\s*:::(note|tip|caution|danger)\[([^\]]*)\]/;
const HEADING = /^(#{2,6})\s+(.*)$/;
const files = walk(root).sort();

const hits = [];
for (const f of files) {
  const src = readFileSync(f, "utf8");
  const lines = src.split(/\r?\n/);
  let inFence = false;
  lines.forEach((line, i) => {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
    if (inFence) return;

    const aside = line.match(ASIDE);
    if (aside) {
      const label = aside[2];
      // The label is truncated at the first inline node of any kind.
      const bad = label.includes("`") ? "code span"
        : /\$[^$]+\$/.test(label) ? "inline math"
        : /(\*\*|__|\*[^*]+\*|\[[^\]]*\]\()/.test(label) ? "inline markup"
        : null;
      if (bad) {
        const kept = label.split(/[`$*_[]/)[0];
        hits.push({ f, line: i + 1, kind: "aside", why: bad,
          detail: `title renders as "${kept.trim()}"` });
      }
      return;
    }

    const h = line.match(HEADING);
    if (h && /\$[^$]+\$/.test(h[2])) {
      hits.push({ f, line: i + 1, kind: "heading", why: "inline math",
        detail: "mangles the table of contents" });
    }
  });
}

const byModule = new Map();
for (const h of hits) {
  const mod = relative(DOCS, h.f).replace(/\\/g, "/").split("/")[0];
  byModule.set(mod, (byModule.get(mod) ?? 0) + 1);
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`aside/heading lint — ${files.length} pages under ${relative(process.cwd(), root) || "."}`);
console.log(bar);

if (!hits.length) {
  console.log("\nOK — every aside title is plain text and no heading carries math.");
  process.exit(0);
}

for (const h of hits) {
  const rel = relative(DOCS, h.f).replace(/\\/g, "/");
  console.log(`  ${rel}:${h.line}  ${h.kind} ${h.why} — ${h.detail}`);
}

console.log(`\n${hits.length} site(s), by module:`);
for (const [mod, n] of [...byModule].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(4)}  ${mod}`);
}

if (scope) {
  console.log("\nFAIL — rewrite these as plain text.");
  process.exit(1);
}
console.log("\nCensus only. Pass a directory to gate it.");
process.exit(0);

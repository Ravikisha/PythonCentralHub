// Stricter MDX check: compiles each .mdx with remark-gfm as well as the math
// plugins, so GFM tables are actually parsed as tables.
//
// scripts/mdxcheck.mjs deliberately omits remark-gfm to stay fast. That makes
// it blind to malformed tables: without the plugin a broken table row is just
// a paragraph and compiles cleanly, then fails under Astro, which does load
// remark-gfm. This script closes that gap.
//
//   node scripts/mdxcheck-gfm.mjs "src/content/docs/<section>"
import { compile } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = process.argv[2] ||
  "src/content/docs/Mathematics for Machine Learning";

function walk(dir) {
  let out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out = out.concat(walk(p));
    else if (e.endsWith(".mdx")) out.push(p);
  }
  return out;
}

const files = walk(ROOT).sort();
let failed = 0;
let tables = 0;

for (const f of files) {
  const rel = relative(ROOT, f).replace(/\\/g, "/");
  let src = readFileSync(f, "utf8");
  const fmEnd = src.indexOf("\n---", 4);
  if (src.startsWith("---") && fmEnd !== -1) src = src.slice(fmEnd + 4);

  // count table header separators outside fenced code, for reporting only
  const bare = src.replace(/```[\s\S]*?```/g, "");
  tables += (bare.match(/^\s*\|[\s:|-]+\|\s*$/gm) || []).length;

  try {
    await compile(src, {
      remarkPlugins: [remarkGfm, remarkMath],
      rehypePlugins: [[rehypeKatex, { throwOnError: false }]],
    });
  } catch (err) {
    failed++;
    const pos = err.line ? `:${err.line}:${err.column ?? 0}` : "";
    console.log(`FAIL ${rel}${pos}\n     ${err.reason || err.message}`);
  }
}

console.log(
  `\n${files.length} MDX files checked with remark-gfm, ` +
  `${tables} tables parsed, ${failed} failed.`
);
process.exit(failed ? 1 : 0);

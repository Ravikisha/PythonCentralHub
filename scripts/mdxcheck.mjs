// Fast MDX syntax check for the DSA section — compiles each .mdx with the same
// math plugins the site uses, without running a full Astro build.
// Catches JSX / template-literal / brace errors in seconds instead of ~30 minutes.
import { compile } from "@mdx-js/mdx";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = process.argv[2] ||
  "D:\\PythonCentralHub\\src\\content\\docs\\DSA with Python";

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

for (const f of files) {
  const rel = relative(ROOT, f).replace(/\\/g, "/");
  let src = readFileSync(f, "utf8");
  // strip YAML frontmatter (remark-frontmatter is not a dependency here)
  const fmEnd = src.indexOf("\n---", 4);
  if (src.startsWith("---") && fmEnd !== -1) src = src.slice(fmEnd + 4);
  try {
    await compile(src, {
      remarkPlugins: [remarkMath],
      rehypePlugins: [[rehypeKatex, { throwOnError: false }]],
    });
  } catch (err) {
    failed++;
    const pos = err.line ? `:${err.line}:${err.column ?? 0}` : "";
    console.log(`FAIL ${rel}${pos}\n     ${err.reason || err.message}`);
  }
}

console.log(`\n${files.length} MDX files checked, ${failed} failed.`);
process.exit(failed ? 1 : 0);

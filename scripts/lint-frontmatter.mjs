// Validate every page's YAML frontmatter against what the Starlight content
// collection expects.
//
// This is the failure mode mdxcheck cannot see: mdxcheck strips frontmatter
// before compiling, so a description containing an unquoted ": " parses as a
// nested YAML mapping, the collection schema rejects it, and EVERY page in the
// module 500s — not just the offending one.
//
//   node scripts/lint-frontmatter.mjs "src/content/docs/<section>"
import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { parse } from "yaml";

const ROOT = process.argv[2] ||
  "src/content/docs/Mathematics for Machine Learning";

function walk(dir) {
  let out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out = out.concat(walk(p));
    else if (e.endsWith(".mdx") || e.endsWith(".md")) out.push(p);
  }
  return out;
}

const files = walk(ROOT).sort();
let bad = 0;
const orders = new Map();

for (const f of files) {
  const rel = relative(ROOT, f).replace(/\\/g, "/");
  const src = readFileSync(f, "utf8").replace(/\r\n/g, "\n");
  const fail = (msg) => { bad++; console.log(`FAIL ${rel}\n     ${msg}`); };

  if (!src.startsWith("---")) { fail("no frontmatter block"); continue; }
  const end = src.indexOf("\n---", 3);
  if (end === -1) { fail("frontmatter block is not closed"); continue; }

  let fm;
  try {
    fm = parse(src.slice(4, end));
  } catch (err) {
    fail(`frontmatter is not valid YAML: ${err.message.split("\n")[0]}`);
    continue;
  }
  if (fm === null || typeof fm !== "object") { fail("frontmatter is empty"); continue; }

  if (typeof fm.title !== "string" || !fm.title.trim()) {
    fail(`title must be a non-empty string, got ${JSON.stringify(fm.title)}`);
  }
  if ("description" in fm && typeof fm.description !== "string") {
    // the classic symptom: "a: b" parsed as a nested mapping
    fail(`description parsed as ${typeof fm.description}, not a string — ` +
         `quote it: ${JSON.stringify(fm.description).slice(0, 90)}`);
  }
  const ord = fm.sidebar?.order;
  if (ord !== undefined) {
    if (typeof ord !== "number") {
      fail(`sidebar.order must be a number, got ${JSON.stringify(ord)}`);
    } else {
      const dir = rel.includes("/") ? rel.slice(0, rel.lastIndexOf("/")) : ".";
      const key = `${dir}#${ord}`;
      if (orders.has(key)) {
        bad++;
        console.log(`FAIL ${rel}\n     sidebar.order ${ord} already used by ` +
                    `${orders.get(key)}`);
      } else orders.set(key, rel);
    }
  }
}

console.log(`\n${files.length} pages checked, ${bad} problem(s).`);
process.exit(bad ? 1 : 0);

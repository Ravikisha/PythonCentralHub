// Point every source link at a renamed GitHub repository.
//
//   node scripts/rename-repo.mjs <owner>/<new-name>          (dry run: counts)
//   node scripts/rename-repo.mjs <owner>/<new-name> --write  (rewrites files)
//
// Rewrites REPO_URL in lib/site.ts and every github.com/Ravikisha/PythonCentralHub
// link in the lessons (project pages link their source files). Run it after
// renaming the repository on GitHub; GitHub redirects the old URLs until then.
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const OLD = "github.com/Ravikisha/PythonCentralHub";
const [target, flag] = process.argv.slice(2);
if (!target || !/^[\w.-]+\/[\w.-]+$/.test(target)) {
  console.error("usage: node scripts/rename-repo.mjs <owner>/<new-name> [--write]");
  process.exit(1);
}
const NEW = `github.com/${target}`;
const write = flag === "--write";

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (/\.(mdx?|tsx?|mjs)$/.test(entry)) out.push(p);
  }
  return out;
}

const files = [join("lib", "site.ts"), ...walk(join("src", "content", "docs")), ...walk("components")];
let changed = 0;
let links = 0;
for (const file of files) {
  const src = readFileSync(file, "utf8");
  if (!src.includes(OLD)) continue;
  const count = src.split(OLD).length - 1;
  links += count;
  changed += 1;
  if (write) writeFileSync(file, src.split(OLD).join(NEW));
}
console.log(`${write ? "Rewrote" : "Would rewrite"} ${links} link(s) in ${changed} file(s): ${OLD} -> ${NEW}`);
if (!write) console.log("Run again with --write to apply.");

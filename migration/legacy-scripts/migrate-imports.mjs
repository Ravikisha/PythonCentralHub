// Move content off per-page component imports.
//
//   node scripts/migrate-imports.mjs --report   (default: changes nothing)
//   node scripts/migrate-imports.mjs --write
//
// The Astro build required every page to import the components it used, which
// is why 1062 of the 1190 content files open with an import line and a run of
// `../`. Next supplies them through `mdx-components.tsx` instead, so the
// migration deletes those lines rather than rewriting a thousand relative
// paths -- and an author adding a quiz no longer counts directories.
//
// Only imports of components the map actually provides are removed. Anything
// still unported keeps its import, so the failure stays loud and greppable
// instead of turning into an "undefined is not a component" at render time.
import { readdirSync, statSync, readFileSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";

const DOCS = "src/content/docs";
const COMPONENTS = "src/components";
const LIST = "migration/mdx-component-list.json";
const WRITE = process.argv.includes("--write");

const list = JSON.parse(readFileSync(LIST, "utf8"));
/** Components ported to React and provided by mdx-components.tsx. */
const PORTED = new Set([...list.ported, ...Object.keys(list.aliases ?? {})]);

function walk(dir, test, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, test, out);
    else if (test(entry)) out.push(p);
  }
  return out;
}

const contentFiles = walk(DOCS, (f) => /\.mdx?$/.test(f));
const componentFiles = walk(COMPONENTS, (f) => /\.tsx$/.test(f));

/** name -> repo path, for every .tsx component that exists. */
const tsxPath = new Map();
for (const f of componentFiles) {
  const name = f.split(/[\\/]/).pop().replace(/\.tsx$/, "");
  if (!tsxPath.has(name)) tsxPath.set(name, f.split("\\").join("/"));
}

const IMPORT_RE = /^import\s+([A-Za-z0-9_]+)\s+from\s+["']([^"']+)["'];?\s*$/;
/**
 * Named imports from Starlight's component package.
 *
 * A bare package specifier, so the default-import pattern above never matched
 * it -- which is how `/404` reached a production build still importing
 * Starlight's TypeScript and failed there rather than here.
 */
const STARLIGHT_RE = /^import\s+\{[^}]+\}\s+from\s+["']@astrojs\/starlight\/components["'];?\s*$/;

const usedTsx = new Set();
const unported = new Map(); // name -> file count
let touched = 0;
let removed = 0;

for (const file of contentFiles) {
  const src = readFileSync(file, "utf8");
  const lines = src.split(/\r?\n/);
  const kept = [];
  let changed = false;

  for (const line of lines) {
    if (STARLIGHT_RE.test(line)) {
      changed = true;
      removed++;
      continue; // CardGrid / LinkCard come from the map now
    }

    const m = line.match(IMPORT_RE);
    if (!m) {
      kept.push(line);
      continue;
    }

    const [, name, spec] = m;
    const isTsx = spec.endsWith(".tsx");
    const isAstro = spec.endsWith(".astro");

    if (isTsx && tsxPath.has(name)) {
      usedTsx.add(name);
      changed = true;
      removed++;
      continue; // provided by the map
    }
    if (isAstro && PORTED.has(name)) {
      changed = true;
      removed++;
      continue; // provided by the map
    }
    if (isAstro) {
      unported.set(name, (unported.get(name) ?? 0) + 1);
    }
    kept.push(line);
  }

  if (!changed) continue;
  touched++;

  // Collapse the blank gap an import block leaves behind, without disturbing
  // the frontmatter fence or the prose that follows.
  const text = kept.join("\n").replace(/(^---\n[\s\S]*?\n---\n)\n{2,}/, "$1\n");
  if (WRITE) writeFileSync(file, text);
}

console.log(`${WRITE ? "rewrote" : "would rewrite"} ${touched} file(s)`);
console.log(`${WRITE ? "removed" : "would remove"} ${removed} import line(s)`);
console.log(`\n.tsx components the map must provide: ${usedTsx.size}`);
console.log([...usedTsx].sort().join(", "));

if (unported.size) {
  console.log(`\nstill-unported .astro components (imports left in place):`);
  for (const [name, count] of [...unported].sort((a, b) => b[1] - a[1])) {
    console.log(`  ${String(count).padStart(4)}  ${name}`);
  }
}

if (!WRITE) console.log("\n--report: nothing written. Re-run with --write.");

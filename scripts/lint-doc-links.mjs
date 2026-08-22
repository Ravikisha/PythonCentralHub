/**
 * lint-doc-links — relative links and Figure refs, checked without a build.
 *
 * Two failure modes the dev-server 200 check cannot see, because it only visits
 * pages and never follows their links:
 *
 * 1. Starlight page URLs end in a trailing slash, so from
 *    /module/chapter/page/ a link written "./sibling/" resolves to
 *    /module/chapter/page/sibling/ — a 404 — and "../other-chapter/x/"
 *    resolves to /module/chapter/other-chapter/x/, also a 404. The correct
 *    forms are "../sibling/" and "../../other-chapter/x/". This is easy to get
 *    wrong because the file layout has one fewer level than the URL.
 *
 * 2. A <Figure src="/images/..."> needs BOTH a -light.svg and a -dark.svg on
 *    disk. A missing one renders as a broken image in one theme only, so it can
 *    ship unnoticed.
 *
 * Usage:
 *   node scripts/lint-doc-links.mjs                census over all docs, exit 0
 *   node scripts/lint-doc-links.mjs "<dir>"        gate one subtree, exit 1 on any hit
 */

import { readdirSync, statSync, readFileSync, existsSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const DOCS = resolve("src/content/docs");
const PUBLIC = resolve("public");
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

/** Starlight's slug for one path segment. */
function slug(name) {
  return name
    .toLowerCase()
    .replaceAll(" - ", "---")
    .replace(/[^a-z0-9 -]/g, "")
    .replaceAll(" ", "-");
}

function slugPath(absFile) {
  const rel = relative(DOCS, absFile).replace(/\\/g, "/");
  return rel
    .slice(0, -".mdx".length)
    .split("/")
    .map(slug);
}

// Every page that exists, as a slug path.
const pages = new Set(walk(DOCS).map((f) => slugPath(f).join("/")));

/** Resolve a relative href against a page's own slug path (trailing-slash URL). */
function resolveHref(here, href) {
  const cur = here.slice();
  for (const part of href.replace(/^\/+|\/+$/g, "").split("/")) {
    if (part === "..") cur.pop();
    else if (part !== "." && part !== "") cur.push(part);
  }
  return cur.join("/");
}

const LINK = /\]\((\.\.?\/[^)\s]*)\)/g;
const FIG = /<Figure\s[^>]*?src="(\/images\/[^"]+)"/gs;

const files = walk(root).sort();
const badLinks = [];
const badFigs = [];
let nLinks = 0;
let nFigs = 0;

for (const f of files) {
  const src = readFileSync(f, "utf8");
  const here = slugPath(f);
  const rel = relative(DOCS, f).replace(/\\/g, "/");

  for (const m of src.matchAll(LINK)) {
    nLinks++;
    const target = resolveHref(here, m[1]);
    if (!pages.has(target)) {
      // Suggest the right number of "../" if the tail matches a real page.
      const tail = m[1]
        .replace(/^\/+|\/+$/g, "")
        .split("/")
        .filter((p) => p !== ".." && p !== ".");
      let suggestion = null;
      for (let up = 1; up <= here.length; up++) {
        const cand = here.slice(0, here.length - up).concat(tail).join("/");
        if (pages.has(cand)) {
          suggestion = "../".repeat(up) + tail.join("/") + "/";
          break;
        }
      }
      badLinks.push({ rel, href: m[1], target, suggestion });
    }
  }

  for (const m of src.matchAll(FIG)) {
    nFigs++;
    const srcPath = m[1];
    // A src that already carries a file extension is a single asset (a raster
    // screenshot, say). Only extensionless srcs are the theme-pair convention,
    // where the component appends -light.svg / -dark.svg itself.
    if (/\.[a-z0-9]{2,5}$/i.test(srcPath)) {
      const p = join(PUBLIC, srcPath.replace(/^\//, ""));
      if (!existsSync(p)) badFigs.push({ rel, missing: srcPath });
      continue;
    }
    for (const suffix of ["-light.svg", "-dark.svg"]) {
      const p = join(PUBLIC, srcPath.replace(/^\//, "") + suffix);
      if (!existsSync(p)) badFigs.push({ rel, missing: srcPath + suffix });
    }
  }
}

const bar = "─".repeat(72);
console.log(bar);
console.log(
  `doc link lint — ${files.length} pages under ${relative(process.cwd(), root) || "."}`
);
console.log(bar);

if (!badLinks.length && !badFigs.length) {
  console.log(`\nOK — ${nLinks} relative links resolve, ${nFigs} figure refs have both themes.`);
  process.exit(0);
}

for (const b of badLinks) {
  console.log(`  ${b.rel}`);
  console.log(`     ${b.href}  ->  /${b.target}  (404)`);
  if (b.suggestion) console.log(`     did you mean  ${b.suggestion}`);
  else console.log(`     no page matches this tail — the target may not exist yet`);
}
for (const b of badFigs) {
  console.log(`  ${b.rel}`);
  console.log(`     missing SVG: ${b.missing}`);
}

console.log(
  `\n${nLinks} links checked, ${badLinks.length} broken.  ` +
    `${nFigs} figure refs checked, ${badFigs.length} missing SVGs.`
);

if (scope) {
  console.log("\nFAIL");
  process.exit(1);
}
console.log("\nCensus only. Pass a directory to gate it.");
process.exit(0);

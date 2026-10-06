// Copy the images the content references into public/.
//
//   node scripts/sync-content-assets.mjs
//
// The Astro build resolved `![alt](../../assets/x.png)` through its asset
// pipeline, so the file never had to exist under a public URL. Next serves
// static files from public/ and nothing rewrites those paths, which is why
// pages that looked fine in the old site rendered with broken images in the
// new one -- sixteen of them, found one at a time by watching the network tab.
//
// This runs in `npm run build`, so an author adding an image under src/assets
// gets it published without knowing any of the above.
import { readdirSync, statSync, readFileSync, copyFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const DOCS = "src/content/docs";
const FROM = "src/assets";
const TO = "public/assets";

/** `../../assets/x.png` and `/assets/x.png`, the two shapes the content uses. */
const REFERENCE = /(?:\.\.\/)+assets\/([^\s)"'>]+)|\/assets\/([^\s)"'>]+)/g;

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (/\.mdx?$/.test(entry)) out.push(p);
  }
  return out;
}

const referenced = new Set();

for (const file of walk(DOCS)) {
  const source = readFileSync(file, "utf8");
  for (const match of source.matchAll(REFERENCE)) {
    const name = (match[1] ?? match[2]).split("#")[0].split("?")[0];
    // Skip anything that is not a plain file name -- a couple of pages show
    // markdown syntax rather than link to an image.
    if (name && !name.includes("<") && !name.includes("{")) referenced.add(name);
  }
}

mkdirSync(TO, { recursive: true });

const copied = [];
const absent = [];

for (const name of referenced) {
  if (existsSync(join(TO, name))) continue;

  const from = join(FROM, name);
  if (existsSync(from)) {
    copyFileSync(from, join(TO, name));
    copied.push(name);
  } else {
    absent.push(name);
  }
}

console.log(
  `${TO}: ${referenced.size} referenced, ${copied.length} copied, ${referenced.size - copied.length - absent.length} already there`
);

if (absent.length) {
  // Not fatal: a missing image is a broken picture, not a broken build, and
  // failing here would block a deploy over a typo in one page.
  console.warn(`  no source for: ${absent.join(", ")}`);
}

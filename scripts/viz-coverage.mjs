/**
 * scripts/viz-coverage.mjs — how much of the site carries a visual, by section.
 *
 * A page counts as covered if it does any of:
 *   · imports from `components/viz/`   (an interactive React island)
 *   · contains a ` ```p5 ` block        (an animated sketch)
 *   · contains a ` ```mermaid ` block   (a diagram)
 *
 * WHY THIS SCRIPT EXISTS
 * ----------------------
 * The number was measured by hand several times during this work and came out
 * wrong once: a detector that matched component NAMES against /[A-Z]\w*Viz/
 * missed the real components (ArrayStepper, GridWalker, …) and reported 84 gaps
 * in a section that actually had 31. Matching the import PATH is the reliable
 * test, and having one script means progress reports cannot drift from each
 * other.
 *
 * Run: npm run viz:coverage
 *      npm run viz:coverage -- --list "Flask Tutorials"   # name the gaps
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

const ROOT = "src/content/docs";
const listArg = process.argv.indexOf("--list");
const listSection = listArg === -1 ? null : process.argv[listArg + 1];

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

const sections = new Map();
let total = 0;
let covered = 0;
const kinds = { island: 0, p5: 0, mermaid: 0 };

for (const file of walk(ROOT)) {
  const text = readFileSync(file, "utf8");
  const rel = relative(ROOT, file).split(sep).join("/");
  const section = rel.includes("/") ? rel.split("/")[0] : "(root pages)";

  const hasIsland = text.includes("components/viz/");
  const hasP5 = text.includes("```p5");
  const hasMermaid = text.includes("```mermaid");
  const ok = hasIsland || hasP5 || hasMermaid;

  if (hasIsland) kinds.island += 1;
  if (hasP5) kinds.p5 += 1;
  if (hasMermaid) kinds.mermaid += 1;

  total += 1;
  if (ok) covered += 1;

  if (!sections.has(section)) sections.set(section, { total: 0, covered: 0, gaps: [] });
  const s = sections.get(section);
  s.total += 1;
  if (ok) s.covered += 1;
  else s.gaps.push(rel);
}

if (listSection) {
  const s = sections.get(listSection);
  if (!s) {
    console.error(`No section named "${listSection}". Sections:`);
    for (const k of sections.keys()) console.error(`  ${k}`);
    process.exit(1);
  }
  console.log(`\n${s.gaps.length} page(s) with no visual in ${listSection}:\n`);
  for (const g of s.gaps) console.log(`  ${g}`);
  console.log();
  process.exit(0);
}

const bar = "─".repeat(72);
const pct = (a, b) => (b === 0 ? 100 : (100 * a) / b);
const meter = (p) => {
  const filled = Math.round((p / 100) * 24);
  return "█".repeat(filled) + "·".repeat(24 - filled);
};

console.log(bar);
console.log(`visual coverage — ${covered} / ${total} pages (${pct(covered, total).toFixed(1)}%)`);
console.log(bar);
console.log();

const rows = [...sections.entries()].sort((a, b) => b[1].total - a[1].total - 0);
for (const [name, s] of rows.sort((a, b) => (a[1].total - a[1].covered < b[1].total - b[1].covered ? 1 : -1))) {
  const p = pct(s.covered, s.total);
  const gap = s.total - s.covered;
  console.log(
    `  ${meter(p)} ${String(Math.round(p)).padStart(3)}%  ${String(s.covered).padStart(4)}/${String(s.total).padEnd(4)}  ` +
      `${gap ? String(gap).padStart(3) + " left" : "  complete"}  ${name}`,
  );
}

console.log(`\n  by kind (a page may have several): ${kinds.p5} p5 · ${kinds.mermaid} mermaid · ${kinds.island} island`);
console.log(`  remaining: ${total - covered}\n`);

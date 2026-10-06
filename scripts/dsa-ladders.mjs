/**
 * scripts/dsa-ladders.mjs — replace hand-written LeetCode tables with <ProblemLadder>.
 *
 * Those tables were the site's single largest source of drift: 502 links across
 * 89 files, each carrying its own copy of a problem's title and difficulty, none
 * of them aware of sheet membership or reported companies. `<ProblemLadder>` reads
 * src/data/dsa instead, so that metadata is stated once.
 *
 * The one thing the tables have that the database does not is the **per-page
 * commentary** — the "the twist" column explaining why *this* problem belongs on
 * *this* page. That is genuinely valuable, so it is harvested into the ladder's
 * `notes` prop rather than discarded.
 *
 * Idempotent: a page that already has a <ProblemLadder> is skipped.
 *
 * Run: node scripts/dsa-ladders.mjs [--dry]
 */
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

const DOCS = "src/content/docs/DSA with Python";
const DRY = process.argv.includes("--dry");

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

/** The page's declared canonical pattern — always the first entry. */
function canonicalPattern(text) {
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) return null;
  const block = fm[1].match(/^patterns:\r?\n\s+-\s+(.+?)\s*$/m);
  return block ? block[1] : null;
}

const HEADING = /^##+ +(?:LeetCode problem set|Practice problems|Problem set|More practice)\s*$/im;

let changed = 0;
let skipped = 0;
let noPattern = 0;

for (const file of walk(DOCS)) {
  const text = readFileSync(file, "utf8");
  const name = relative(DOCS, file).split(sep).pop();

  if (/<ProblemLadder\b/.test(text)) {
    skipped += 1;
    continue;
  }

  const heading = text.match(HEADING);
  if (!heading) continue;

  const pattern = canonicalPattern(text);
  if (!pattern) {
    // Without a declared pattern the ladder would render empty, which is worse
    // than leaving the hand-written table in place.
    noPattern += 1;
    console.log(`skip (no patterns: in frontmatter)  ${name}`);
    continue;
  }

  // The section runs from its heading to the next heading of the same level or above.
  const start = heading.index;
  const level = heading[0].match(/^#+/)[0].length;
  const after = text.slice(start + heading[0].length);
  const nextHeading = after.match(new RegExp(`^#{1,${level}} `, "m"));
  const end = nextHeading ? start + heading[0].length + nextHeading.index : text.length;
  const section = text.slice(start, end);

  // Harvest the commentary column. Rows look like:
  //   | 643 | [Maximum Average Subarray I](url) | Easy | the twist |
  const notes = {};
  for (const row of section.matchAll(
    /^\|\s*(\d+)\s*\|\s*\[[^\]]+\]\(https:\/\/leetcode\.com[^)]*\)\s*\|[^|]*\|\s*([^|]*?)\s*\|/gm,
  )) {
    const twist = row[2].trim();
    if (twist && twist !== "--" && twist !== "—") notes[Number(row[1])] = twist;
  }

  if (Object.keys(notes).length === 0 && !/leetcode\.com/.test(section)) {
    // Nothing to replace — this section was already prose-only.
    continue;
  }

  // Keep the section's prose; drop only the table rows.
  const body = section.slice(heading[0].length);
  const prose = body
    .split(/\r?\n/)
    .filter((line) => !/^\|/.test(line.trim()))
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const notesAttr =
    Object.keys(notes).length > 0
      ? `\n  notes={${JSON.stringify(notes)}}`
      : "";

  const replacement =
    `${heading[0]}\n\n` +
    `Generated from the problem database, so each entry carries its sheet\n` +
    `membership and reported companies. Tick them off as you go — progress is\n` +
    `saved in this browser, and the Export button writes it to a file you can keep.\n\n` +
    (prose ? `${prose}\n\n` : "") +
    `<ProblemLadder pattern="${pattern}"${notesAttr} />\n\n`;

  let next = text.slice(0, start) + replacement + text.slice(end);

  // No import: the Next app provides every MDX component globally
  // (mdx-components.tsx). An import of the old .astro file fails the build.
  if (!DRY) writeFileSync(file, next, "utf8");
  changed += 1;
  console.log(`ok  ${name}  (${Object.keys(notes).length} notes carried over)`);
}

console.log(
  `\n${DRY ? "[dry run] " : ""}${changed} page(s) converted, ${skipped} already had a ladder, ` +
    `${noPattern} skipped for missing frontmatter patterns.`,
);

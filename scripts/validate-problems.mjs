/**
 * scripts/validate-problems.mjs — integrity checks for the DSA problem database.
 *
 * The database is only worth centralising if it cannot silently rot. This is the
 * guard: it fails the build on anything that would make a rendered page wrong,
 * and warns (without failing) on work that is merely incomplete.
 *
 * Errors — a page would render something false:
 *   * duplicate slug or duplicate LeetCode number
 *   * malformed slug (would produce a 404 on leetcode.com)
 *   * bad difficulty value
 *   * a `pages:` entry naming a file that does not exist
 *   * a sheet section transcription whose length disagrees with the sheet's own
 *     published count — that means a line was dropped in transcription
 *   * a sheet listing a title that no problem row resolves to
 *   * a company slug on a problem with no profile in companies.yaml
 *
 * Warnings — real but non-breaking gaps:
 *   * rows still marked `review: true`
 *   * patterns that no page declares (an orphaned tag)
 *   * pages whose declared patterns match zero problems (an empty ladder)
 *
 * Run: node scripts/validate-problems.mjs
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import yaml from "js-yaml";

const DIR = "src/data/dsa";
const DOCS = "src/content/docs/DSA with Python";

const problems = yaml.load(readFileSync(join(DIR, "problems.yaml"), "utf8")) ?? [];
const sheets = yaml.load(readFileSync(join(DIR, "sheets.yaml"), "utf8")) ?? {};
const companies = yaml.load(readFileSync(join(DIR, "companies.yaml"), "utf8")) ?? {};

const errors = [];
const warnings = [];
const err = (m) => errors.push(m);
const warn = (m) => warnings.push(m);

/** Must stay identical to slugify() in merge-sheets.mjs and titleSlug() in index.ts. */
const titleSlug = (title) =>
  title
    .toLowerCase()
    .replace(/['’.,()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

// ── page inventory ─────────────────────────────────────────────────────────

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

const pageSlug = (file) =>
  relative(DOCS, file)
    .split(sep)
    .pop()
    .replace(/\.mdx$/, "")
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const files = existsSync(DOCS) ? walk(DOCS) : [];
const pageSlugs = new Set(files.map(pageSlug));

/** Patterns declared in page frontmatter — the authority for what a pattern is. */
const declaredPatterns = new Set();
for (const file of files) {
  const fm = readFileSync(file, "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) continue;
  const block = fm[1].match(/^patterns:\r?\n((?:\s+-\s+.*\r?\n?)+)/m);
  if (!block) continue;
  for (const line of block[1].split(/\r?\n/)) {
    const m = line.match(/^\s+-\s+(.+?)\s*$/);
    if (m) declaredPatterns.add(m[1]);
  }
}

// ── per-problem checks ─────────────────────────────────────────────────────

const VALID_DIFF = new Set(["easy", "medium", "hard"]);
const SLUG_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const seenSlug = new Map();
const seenLc = new Map();
const usedPatterns = new Set();

for (const p of problems) {
  const where = `problem ${p.lc ?? "?"} (${p.slug})`;

  if (!p.slug || !SLUG_RE.test(p.slug)) {
    err(`${where}: slug "${p.slug}" is malformed — it would 404 on leetcode.com`);
  }
  if (seenSlug.has(p.slug)) {
    err(`duplicate slug "${p.slug}" — two rows describe the same problem`);
  }
  seenSlug.set(p.slug, p);

  if (p.lc !== null && p.lc !== undefined) {
    if (seenLc.has(p.lc)) {
      err(`duplicate LeetCode number ${p.lc}: "${p.slug}" and "${seenLc.get(p.lc).slug}"`);
    }
    seenLc.set(p.lc, p);
  }

  if (!VALID_DIFF.has(p.difficulty)) {
    err(`${where}: difficulty "${p.difficulty}" is not easy/medium/hard`);
  }

  if (!p.title) err(`${where}: missing title`);

  for (const page of p.pages ?? []) {
    if (!pageSlugs.has(page)) {
      err(`${where}: pages entry "${page}" does not match any .mdx under ${DOCS}`);
    }
  }

  for (const c of p.companies ?? []) {
    if (!companies[c]) {
      err(`${where}: company "${c}" has no profile in companies.yaml`);
    }
  }

  if (p.freq !== undefined && (p.freq < 1 || p.freq > 5)) {
    err(`${where}: freq ${p.freq} is outside 1-5`);
  }

  for (const pattern of p.patterns ?? []) usedPatterns.add(pattern);
  if ((p.patterns ?? []).length === 0) warn(`${where}: no pattern assigned — it will never appear in a ladder`);
  if (p.review) warn(`${where}: review:true — difficulty and patterns are still guesses`);
}

// ── sheet checks ───────────────────────────────────────────────────────────

for (const [key, sheet] of Object.entries(sheets)) {
  if (sheet.sections) {
    let transcribed = 0;
    for (const [section, titles] of Object.entries(sheet.sections)) {
      transcribed += titles.length;
      for (const title of titles) {
        if (!seenSlug.has(titleSlug(title))) {
          err(`sheet ${key} / ${section}: "${title}" resolves to no problem row`);
        }
      }
    }
    if (transcribed !== sheet.count) {
      err(
        `sheet ${key}: ${transcribed} problems transcribed but the sheet publishes ${sheet.count}` +
          ` — a line was dropped or duplicated`,
      );
    }
  }

  if (sheet.steps) {
    let claimed = 0;
    // Only sheets that publish per-step counts get the sum checked. Striver's
    // SDE sheet publishes a 191 total but no firm per-day quota, so inventing
    // per-step numbers just to satisfy an assertion would be worse than not
    // asserting.
    const hasStepCounts = Object.values(sheet.steps).every((s) => typeof s.count === "number");
    for (const [stepKey, step] of Object.entries(sheet.steps)) {
      claimed += step.count ?? 0;
      for (const pattern of step.patterns ?? []) {
        if (!pageSlugs.has(pattern) && !declaredPatterns.has(pattern)) {
          err(`sheet ${key} / ${stepKey}: pattern "${pattern}" matches no page and no declared pattern`);
        }
      }
      if ((step.patterns ?? []).length === 0) {
        warn(`sheet ${key} / ${stepKey} ("${step.title}"): no pages mapped — the step renders empty`);
      }
    }
    if (hasStepCounts && claimed !== sheet.count) {
      err(`sheet ${key}: step counts sum to ${claimed} but the sheet publishes ${sheet.count}`);
    }
  }
}

// ── company checks ─────────────────────────────────────────────────────────

for (const [slug, company] of Object.entries(companies)) {
  if (company.slug !== slug) {
    err(`company "${slug}": its slug field says "${company.slug}" — the two must agree`);
  }
  for (const pattern of company.patterns ?? []) {
    if (!usedPatterns.has(pattern)) {
      err(
        `company "${slug}": pattern "${pattern}" is tagged on no problem, so its board would render empty`,
      );
    }
  }
  if (!company.rounds?.length) err(`company "${slug}": no rounds defined`);
  if (!company.bar) err(`company "${slug}": no bar described`);
}

// ── orphan checks ──────────────────────────────────────────────────────────

for (const pattern of usedPatterns) {
  if (!declaredPatterns.has(pattern) && !pageSlugs.has(pattern)) {
    warn(`pattern "${pattern}" is used by problems but matches no page — orphaned tag`);
  }
}
for (const pattern of declaredPatterns) {
  if (!usedPatterns.has(pattern)) {
    warn(`pattern "${pattern}" is declared in a page's frontmatter but no problem carries it — empty ladder`);
  }
}

// ── report ────────────────────────────────────────────────────────────────

const line = "─".repeat(72);
console.log(line);
console.log(`DSA problem database — ${problems.length} problems, ${Object.keys(sheets).length} sheets, ${Object.keys(companies).length} companies`);
console.log(line);

if (warnings.length) {
  // Warnings are a backlog, not a failure. Print a capped sample plus a count so
  // the output stays readable while the review queue is still large.
  const SHOW = 15;
  console.log(`\n${warnings.length} warning(s):`);
  for (const w of warnings.slice(0, SHOW)) console.log(`  · ${w}`);
  if (warnings.length > SHOW) console.log(`  … and ${warnings.length - SHOW} more`);
}

if (errors.length) {
  console.log(`\n${errors.length} error(s):`);
  for (const e of errors) console.log(`  ✗ ${e}`);
  console.log("\nFAILED");
  process.exit(1);
}

console.log(`\nOK — no errors.`);

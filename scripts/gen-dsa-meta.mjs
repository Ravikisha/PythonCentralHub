/**
 * gen-dsa-meta.mjs — print META entries for scripts/dsa-frontmatter.mjs.
 *
 * Run it, paste the output into that file's META table, then run
 * `node scripts/dsa-frontmatter.mjs` followed by `node scripts/dsa-ladders.mjs`.
 * It prints entries to stdout and a skip report to stderr; it never writes a file.
 *
 * It already generated the 44 entries for Phases 04/06/07/08/11/13/14/15/16/17/20.
 * Re-run it after tagging problems in overrides.yaml to pick up the pages it
 * currently skips (Phase-01/02, four Phase-04 sort pages, Maximum Flow,
 * Phase-18/19) — it only emits a page whose slug already carries problems, so
 * nothing it produces can create an "empty ladder" warning.
 *
 * Everything is derived from data that already exists rather than invented:
 *
 *   patterns   the page's own filename slug (the canonical convention)
 *   sheets     reverse-index of sheets.yaml — which section of each sheet lists
 *              this slug. Nothing guessed; if no sheet lists it, the key is absent.
 *   companies  the most frequent company tags across the problems carrying this
 *              pattern (crowd-reported, as companies.yaml already warns)
 *   difficulty the modal tier of those problems, as a proxy for the page's tier
 *   prereqs    one hand-written default per phase (12 decisions, not 44)
 *
 * Only pages whose slug ALREADY has problems are emitted, so every declared
 * pattern produces a non-empty ladder and no "empty ladder" validator warning.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import yaml from "js-yaml";

const DOCS = "src/content/docs/DSA with Python";
const problems = yaml.load(readFileSync("src/data/dsa/problems.yaml", "utf8"));
const sheets = yaml.load(readFileSync("src/data/dsa/sheets.yaml", "utf8"));

// ── one prereq decision per phase ─────────────────────────────────────────
const PHASE_PREREQS = {
  "Phase-04-Sorting-and-Searching": ["arrays-and-dynamic-arrays", "big-o-and-complexity-deep-dive"],
  "Phase-06-Patterns-Search-and-Selection": ["binary-search-template-and-variants", "heaps-and-priority-queues"],
  "Phase-07-Patterns-Intervals-and-Greedy": ["sorting-with-custom-comparators", "arrays-and-dynamic-arrays"],
  "Phase-08-Patterns-Linked-Lists": ["linked-lists", "two-pointers"],
  "Phase-11-Recursion-and-Backtracking": ["python-recursion-and-iterative-conversion"],
  "Phase-13-Bit-Manipulation-and-Math": ["big-o-and-complexity-deep-dive"],
  "Phase-14-Design-Problems": ["hash-tables", "linked-lists"],
  "Phase-15-Simulation-and-Implementation": ["arrays-and-dynamic-arrays"],
  "Phase-16-Advanced-Graph-Algorithms": ["graph-traversal-and-connected-components", "union-find-problem-patterns"],
  "Phase-17-Advanced-CP-Topics": ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
  "Phase-20-Problem-Sets": ["pattern-recognition-guide"],
};

// Phase-07's own page must not list itself as a prereq.
const selfSafe = (slug, list) => list.filter((p) => p !== slug);

const pageSlug = (name) =>
  name
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const full = join(dir, e);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (e.endsWith(".mdx")) out.push(full);
  }
  return out;
}

// ── pattern slug -> {striver step/day} ─────────────────────────────────
// Only striver_a2z and striver_sde are derivable: they map PATTERNS to steps in
// sheets.yaml, which is curated data. neetcode150 / blind75 /
// lc_top_interview_150 index by problem title, so the "section" of a topic page
// could only be inferred from its problems -- and that inference is wrong
// whenever a page's problems live elsewhere (merge-sort's problems are filed
// under "Linked List"). Those three sheets are therefore left off the page and
// shown per-problem by <ProblemLadder> instead, which is where they belong.
const sheetOf = new Map();
for (const [key, sheet] of Object.entries(sheets)) {
  if (!sheet.steps) continue;
  for (const [stepKey, step] of Object.entries(sheet.steps)) {
    for (const pat of step.patterns ?? []) {
      if (!sheetOf.has(pat)) sheetOf.set(pat, {});
      if (sheetOf.get(pat)[key] === undefined) sheetOf.get(pat)[key] = stepKey;
    }
  }
}

// ── pattern slug -> problems carrying it ─────────────────────────────────
const byPattern = new Map();
for (const p of problems) {
  for (const pat of p.patterns ?? []) {
    if (!byPattern.has(pat)) byPattern.set(pat, []);
    byPattern.get(pat).push(p);
  }
}

const modalDifficulty = (list) => {
  const c = { easy: 0, medium: 0, hard: 0 };
  for (const p of list) c[p.difficulty] = (c[p.difficulty] ?? 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1])[0][0];
};

const topCompanies = (list, n = 4) => {
  const c = new Map();
  for (const p of list) for (const co of p.companies ?? []) c.set(co, (c.get(co) ?? 0) + 1);
  return [...c.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, n)
    .map(([co]) => co);
};

const q = (s) => `"${s}"`;
const arr = (a) => `[${a.map(q).join(", ")}]`;

let emitted = 0;
const skipped = [];
const chunks = new Map();

for (const file of walk(DOCS).sort()) {
  const text = readFileSync(file, "utf8");
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (fm && fm[1].includes("patterns:")) continue; // already has it

  const rel = relative(DOCS, file).split(sep).join("/");
  const phase = rel.split("/")[0];
  const name = rel.split("/").pop().replace(/\.mdx$/, "");
  const slug = pageSlug(name);

  const list = byPattern.get(slug);
  if (!list || list.length === 0) {
    skipped.push(`${phase}/${name} — slug "${slug}" carries no problems`);
    continue;
  }
  const prereqs = selfSafe(slug, PHASE_PREREQS[phase] ?? []);
  if (prereqs.length === 0) {
    skipped.push(`${phase}/${name} — no prereq default for this phase`);
    continue;
  }

  const sh = sheetOf.get(slug) ?? {};
  const shStr = Object.keys(sh).length
    ? `{ ${Object.entries(sh)
        .map(([k, v]) => `${k}: ${v === true ? "true" : q(v)}`)
        .join(", ")} }`
    : null;

  const lines = [
    `  ${q(rel)}: {`,
    `    patterns: ${arr([slug])},`,
    `    difficulty: ${q(modalDifficulty(list))},`,
    `    prereqs: ${arr(prereqs)},`,
  ];
  if (shStr) lines.push(`    sheets: ${shStr},`);
  const cos = topCompanies(list);
  if (cos.length) lines.push(`    companies: ${arr(cos)},`);
  lines.push(`  },`);

  if (!chunks.has(phase)) chunks.set(phase, []);
  chunks.get(phase).push({ lines: lines.join("\n"), n: list.length });
  emitted += 1;
}

for (const [phase, entries] of [...chunks.entries()].sort()) {
  console.log(`\n  // ── ${phase} ${"─".repeat(Math.max(0, 60 - phase.length))}`);
  for (const e of entries) console.log(e.lines);
}

console.error(`\n${emitted} entries emitted.`);
console.error(`${skipped.length} skipped:`);
for (const s of skipped) console.error(`  · ${s}`);

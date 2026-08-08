/**
 * scripts/merge-sheets.mjs — fold sheet membership into the problem database.
 *
 * Input:   src/data/dsa/problems.generated.yaml  (harvested from the corpus)
 *          src/data/dsa/sheets.yaml              (transcribed public sheets)
 * Output:  src/data/dsa/problems.yaml            (the source of truth)
 *
 * Two jobs:
 *
 *  1. **Resolve.** Sheets list problems by title. Map each title to a slug and
 *     write the membership onto that problem's row.
 *  2. **Create.** Most sheet problems are not yet referenced anywhere in the
 *     corpus — those get a new row, with a pattern inferred from the sheet
 *     section it appeared in.
 *
 * Difficulty is only trustworthy for rows harvested from the corpus, where a
 * page stated it. Newly created rows are marked `review: true` so
 * validate-problems.mjs can report the remaining backlog instead of letting a
 * guessed "medium" pass as fact.
 *
 * Idempotent: safe to re-run. It never drops hand-added fields on existing
 * rows in problems.yaml — those are read back in and merged.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import yaml from "js-yaml";

const GENERATED = "src/data/dsa/problems.generated.yaml";
const SHEETS = "src/data/dsa/sheets.yaml";
const OUT = "src/data/dsa/problems.yaml";

/**
 * LeetCode's slug rule, which is stable enough to rely on: lowercase, drop
 * everything that is not a letter, digit or separator, then collapse separators.
 *
 *   "Pow(x, n)"                     -> "powx-n"
 *   "Two Sum II - Input Array..."   -> "two-sum-ii-input-array-is-sorted"
 *   "Insert Delete GetRandom O(1)"  -> "insert-delete-getrandom-o1"
 */
export function slugify(title) {
  return title
    .toLowerCase()
    .replace(/['’.,()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Sheet section -> the pattern slugs on this site that teach it. Used only to
 * seed `patterns` on problems the corpus has never mentioned; once such a
 * problem is linked from a real page, the harvester supplies better data.
 */
const SECTION_PATTERNS = {
  "Arrays & Hashing": ["hash-tables", "arrays-and-dynamic-arrays"],
  "Two Pointers": ["two-pointers"],
  "Sliding Window": ["sliding-window"],
  Stack: ["stacks-and-queues", "monotonic-stack"],
  "Binary Search": ["binary-search-template-and-variants"],
  "Linked List": ["linked-lists"],
  Trees: ["binary-trees-and-bst", "tree-dfs-paths-and-sums"],
  Tries: ["tries"],
  "Heap / Priority Queue": ["heaps-and-priority-queues"],
  Backtracking: ["backtracking"],
  Graphs: ["graph-traversal-and-connected-components"],
  "Advanced Graphs": ["shortest-paths-dijkstra-bellman-ford-and-floyd-warshall"],
  "1-D Dynamic Programming": ["one-dimensional-dp"],
  "2-D Dynamic Programming": ["two-dimensional-dp-and-knapsack"],
  Greedy: ["greedy-reachability-and-jumps"],
  Intervals: ["merge-intervals"],
  "Math & Geometry": ["math-and-geometry-problems"],
  "Bit Manipulation": ["bit-manipulation-tricks"],
  // Blind 75 section names that differ from NeetCode's
  Array: ["arrays-and-dynamic-arrays"],
  String: ["strings"],
  Matrix: ["matrix-and-grid-manipulation"],
  "Binary Tree": ["binary-trees-and-bst"],
  "Binary Search Tree": ["bst-patterns"],
  Trie: ["tries"],
  Heap: ["heaps-and-priority-queues"],
  Graph: ["graph-traversal-and-connected-components"],
  "Dynamic Programming": ["from-recursion-to-dp"],
  Binary: ["bit-manipulation-tricks"],
  // LeetCode Top Interview 150 section names
  "Array / String": ["arrays-and-dynamic-arrays", "strings"],
  Hashmap: ["hash-tables"],
  "Binary Tree General": ["binary-trees-and-bst"],
  "Binary Tree BFS": ["tree-bfs-and-level-order"],
  "Graph General": ["graph-traversal-and-connected-components"],
  "Graph BFS": ["breadth-first-search"],
  "Divide & Conquer": ["divide-and-conquer"],
  "Kadane's Algorithm": ["kadane-and-maximum-subarray"],
  Math: ["math-and-geometry-problems"],
  "1D DP": ["one-dimensional-dp"],
  "Multidimensional DP": ["two-dimensional-dp-and-knapsack"],
};

// ── load ───────────────────────────────────────────────────────────────────

const generated = yaml.load(readFileSync(GENERATED, "utf8")) ?? [];
const sheets = yaml.load(readFileSync(SHEETS, "utf8")) ?? {};
/** Previously written problems.yaml — hand edits live here and must survive. */
const previous = existsSync(OUT) ? (yaml.load(readFileSync(OUT, "utf8")) ?? []) : [];

/** slug -> row */
const bySlug = new Map();

const mergeRow = (row) => {
  const existing = bySlug.get(row.slug);
  if (!existing) {
    bySlug.set(row.slug, { ...row });
    return;
  }
  for (const [k, v] of Object.entries(row)) {
    if (v === undefined || v === null) continue;
    if (Array.isArray(v)) {
      existing[k] = [...new Set([...(existing[k] ?? []), ...v])];
    } else if (k === "sheets") {
      existing.sheets = { ...(existing.sheets ?? {}), ...v };
    } else if (existing[k] === undefined) {
      existing[k] = v;
    }
  }
};

// Hand-edited rows first so their scalars win, then the harvest fills gaps.
for (const row of previous) mergeRow(row);
for (const row of generated) mergeRow(row);

/** title (normalised) -> slug, for resolving sheet entries. */
const titleIndex = new Map();
for (const row of bySlug.values()) {
  if (row.title) titleIndex.set(slugify(row.title), row.slug);
  titleIndex.set(row.slug, row.slug);
}

// ── merge sheet membership ─────────────────────────────────────────────────

const created = [];
const stats = {};

for (const [sheetKey, sheet] of Object.entries(sheets)) {
  // Step-indexed sheets (Striver) carry no per-problem titles; they are
  // rendered from their pattern mapping instead, so there is nothing to fold in.
  if (!sheet.sections) continue;

  let seen = 0;
  for (const [section, titles] of Object.entries(sheet.sections)) {
    for (const title of titles) {
      seen += 1;
      const key = slugify(title);
      let slug = titleIndex.get(key);

      if (!slug) {
        slug = key;
        const patterns = SECTION_PATTERNS[section] ?? [];
        mergeRow({
          lc: null,
          slug,
          title,
          difficulty: "medium",
          review: true, // difficulty + patterns are guesses until a page links it
          patterns,
          pages: [],
        });
        titleIndex.set(key, slug);
        created.push({ slug, title, sheet: sheetKey, section });
      }

      const row = bySlug.get(slug);
      row.sheets = row.sheets ?? {};
      row.sheets[sheetKey] = sheet.ordered === false && Object.keys(sheet.sections).length === 1 ? true : section;
    }
  }
  stats[sheetKey] = { transcribed: seen, claimed: sheet.count };
}

// ── apply hand-curated overrides last, so they win outright ────────────────

const OVERRIDES = "src/data/dsa/overrides.yaml";
const overrides = existsSync(OVERRIDES) ? (yaml.load(readFileSync(OVERRIDES, "utf8")) ?? {}) : {};
const unmatchedOverrides = [];
const createdFromOverrides = [];

for (const [slug, patch] of Object.entries(overrides)) {
  let row = bySlug.get(slug);
  if (!row) {
    // An override may also CREATE a problem, provided it supplies enough to be a
    // real row. That is how a page can add a problem the corpus has never linked
    // and no sheet lists — without it, tagging such a problem silently no-ops.
    if (patch.lc !== undefined && patch.title !== undefined) {
      row = { lc: patch.lc, slug, title: patch.title, difficulty: patch.difficulty ?? "medium", patterns: [], pages: [] };
      bySlug.set(slug, row);
      createdFromOverrides.push(slug);
    } else {
      unmatchedOverrides.push(slug);
      continue;
    }
  }
  for (const [k, v] of Object.entries(patch)) {
    // `key: null` deletes — that is how `review: null` clears the flag.
    if (v === null) delete row[k];
    else row[k] = v;
  }
}

// ── emit ──────────────────────────────────────────────────────────────────

const rows = [...bySlug.values()].sort((a, b) => {
  // Numbered problems first, in LeetCode order; unnumbered ones alphabetically.
  if (a.lc && b.lc) return a.lc - b.lc;
  if (a.lc) return -1;
  if (b.lc) return 1;
  return a.slug.localeCompare(b.slug);
});

const header = `# =============================================================================
# The DSA problem database — the single source of truth for every practice link
# on this site. Nothing here is hand-written into a page: <ProblemLadder>,
# <SheetTracker> and <CompanyBoard> all read this file.
#
# Regenerate sheet membership with:  node scripts/merge-sheets.mjs
# Validate with:                     node scripts/validate-problems.mjs
#
# Fields
#   lc          LeetCode number, or null for problems that are not on LeetCode.
#   slug        LeetCode URL slug. Also this row's primary key.
#   title       Official problem title.
#   difficulty  easy | medium | hard.
#   premium     true when the problem is behind LeetCode Premium.
#   review      true means difficulty/patterns are still unverified guesses.
#   patterns    Pattern slugs. <ProblemLadder pattern="x"> matches on these.
#   pages       Pages on this site that already link the problem.
#   sheets      sheet key -> that sheet's section name for this problem.
#   companies   Company slugs. See companies.yaml for the accuracy caveat.
#   freq        1-5, how often it is reported. Absent means unknown, not rare.
# =============================================================================

`;

writeFileSync(OUT, header + yaml.dump(rows, { lineWidth: 100, noRefs: true }), "utf8");

// ── report ────────────────────────────────────────────────────────────────

const needsReview = rows.filter((r) => r.review).length;
const noPattern = rows.filter((r) => !r.patterns || r.patterns.length === 0).length;

console.log(`wrote ${OUT}`);
console.log(`  ${rows.length} problems total`);
console.log(`  ${created.length} newly created from sheets`);
console.log(`  ${Object.keys(overrides).length} rows patched from overrides.yaml`);
if (createdFromOverrides.length) console.log(`  ${createdFromOverrides.length} row(s) created by overrides: ${createdFromOverrides.join(", ")}`);
console.log(`  ${needsReview} still marked review:true (difficulty/patterns unverified)`);
console.log(`  ${noPattern} with no pattern assigned`);
if (unmatchedOverrides.length) {
  console.log(`\n  WARNING — overrides.yaml keys matching no problem (typo, or a renamed slug):`);
  for (const slug of unmatchedOverrides) console.log(`    ${slug}`);
}
console.log("");
for (const [key, s] of Object.entries(stats)) {
  const ok = s.transcribed === s.claimed ? "ok" : "MISMATCH";
  console.log(`  ${key.padEnd(24)} ${String(s.transcribed).padStart(3)} transcribed / ${s.claimed} claimed  ${ok}`);
}

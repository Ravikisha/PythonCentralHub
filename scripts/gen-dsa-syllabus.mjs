/**
 * scripts/gen-dsa-syllabus.mjs — derive the course's teaching order as data.
 *
 * WHY THIS EXISTS
 * ---------------
 * The problem database knows which patterns exist and which problems carry them, but
 * it does not know what order to *learn* them in. That order lives in the filesystem:
 * the phase directory names are a deliberate sequence, and every page carries a
 * `sidebar.order` within its phase.
 *
 * The study-plan generator needs that ordering, and hand-maintaining a second copy of
 * it would drift the moment a page moves. So this script reads it off the pages and
 * writes `src/data/dsa/syllabus.yaml`, the same way `merge-sheets.mjs` writes
 * `problems.yaml`.
 *
 * A page contributes to the syllabus only if it declares `patterns:` — the pattern
 * pages. Orientation, foundations, reference and company pages teach no pattern (see
 * `EXEMPT_PHASES` in audit-dsa.mjs) and are deliberately absent: a study plan is a
 * sequence of *patterns to drill*, not a reading list.
 *
 * Run: npm run dsa:syllabus  (and it is part of `npm run dsa`)
 */
import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import yaml from "js-yaml";

const DOCS = "src/content/docs/DSA with Python";
const OUT = "src/data/dsa/syllabus.yaml";

/**
 * Human labels for the phase directories that make up the *teaching sequence*, mirroring
 * the sidebar in astro.config.mjs. This map is also the filter: a phase absent from it is
 * absent from the syllabus.
 *
 * Deliberately stops at Phase-17. Phases 18-21 (templates, strategy, problem sets, company
 * guides) do declare `patterns:`, but those are **aliases of other pages' patterns** — the
 * cheatsheets and company boards point *at* the pattern pages rather than teaching a new
 * pattern. Including them would list every pattern twice and put "Hard Mix Problem Set" in
 * the middle of a learning sequence.
 */
const PHASE_LABELS = {
  "Phase-01-Foundations": "Foundations",
  "Phase-02-Python-for-DSA-and-CP": "Python for DSA & CP",
  "Phase-03-Core-Data-Structures": "Core Data Structures",
  "Phase-04-Sorting-and-Searching": "Sorting & Searching",
  "Phase-05-Patterns-Arrays-and-Strings": "Arrays & Strings",
  "Phase-06-Patterns-Search-and-Selection": "Search & Selection",
  "Phase-07-Patterns-Intervals-and-Greedy": "Intervals & Greedy",
  "Phase-08-Patterns-Linked-Lists": "Linked Lists",
  "Phase-09-Patterns-Trees": "Trees",
  "Phase-10-Patterns-Graphs": "Graphs",
  "Phase-11-Recursion-and-Backtracking": "Recursion & Backtracking",
  "Phase-12-Dynamic-Programming": "Dynamic Programming",
  "Phase-13-Bit-Manipulation-and-Math": "Bit Manipulation & Math",
  "Phase-14-Design-Problems": "Design Problems",
  "Phase-15-Simulation-and-Implementation": "Simulation & Implementation",
  "Phase-16-Advanced-Graph-Algorithms": "Advanced Graph Algorithms",
  "Phase-17-Advanced-CP-Topics": "Advanced CP Topics",
};

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

/** Starlight's slug rule for a docs file path, as used by the audit's pageSlug check. */
const slugify = (s) =>
  s
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

const entries = [];
let skipped = 0;

for (const file of walk(DOCS)) {
  const parts = relative(DOCS, file).split(sep);
  const phase = parts[0];
  const name = parts[parts.length - 1].replace(/\.mdx$/, "");

  // Phases outside the teaching sequence alias other pages' patterns — see PHASE_LABELS.
  if (!(phase in PHASE_LABELS)) {
    skipped += 1;
    continue;
  }

  const fm = readFileSync(file, "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) continue;

  let meta;
  try {
    meta = yaml.load(fm[1]);
  } catch {
    console.error(`  ! frontmatter does not parse: ${relative(process.cwd(), file)}`);
    process.exitCode = 1;
    continue;
  }

  // Only pattern pages belong in a study plan. Everything else teaches no pattern.
  if (!Array.isArray(meta?.patterns) || meta.patterns.length === 0) {
    skipped += 1;
    continue;
  }

  entries.push({
    phase,
    phaseLabel: PHASE_LABELS[phase],
    title: meta.title ?? name,
    url: `/dsa-with-python/${slugify(phase)}/${slugify(name)}/`,
    order: meta.sidebar?.order ?? 999,
    difficulty: meta.difficulty ?? "medium",
    patterns: meta.patterns,
  });
}

// Teaching order: phase directory name sorts correctly because of the zero-padded
// numeric prefix, then `sidebar.order` within the phase.
entries.sort((a, b) => a.phase.localeCompare(b.phase) || a.order - b.order || a.title.localeCompare(b.title));

const seen = new Map();
for (const e of entries) {
  for (const p of e.patterns) {
    if (!seen.has(p)) seen.set(p, e.title);
  }
}

/**
 * Per-phase counts for EVERY phase, including the ones outside the teaching sequence.
 * The roadmap's phase map needs Phase-00 (orientation) and 18-21 (reference, strategy,
 * problem sets, company guides), which are deliberately absent from `pages` above.
 */
const phaseRows = [];
for (const dir of readdirSync(DOCS)) {
  if (!statSync(join(DOCS, dir)).isDirectory()) continue;
  const files = walk(join(DOCS, dir)).filter((f) => f.endsWith(".mdx"));
  const patterns = new Set();
  let first = null;
  let firstOrder = Infinity;

  for (const f of files) {
    const fm = readFileSync(f, "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!fm) continue;
    let meta;
    try {
      meta = yaml.load(fm[1]);
    } catch {
      continue;
    }
    for (const pat of meta?.patterns ?? []) patterns.add(pat);
    const order = meta?.sidebar?.order ?? 999;
    if (order < firstOrder) {
      firstOrder = order;
      const name = f.split(sep).pop().replace(/\.mdx$/, "");
      first = { title: meta?.title ?? name, url: `/dsa-with-python/${slugify(dir)}/${slugify(name)}/` };
    }
  }

  phaseRows.push({
    phase: dir,
    label: PHASE_LABELS[dir] ?? dir.replace(/^Phase-\d+-/, "").replace(/-/g, " "),
    number: dir.slice(6, 8),
    pages: files.length,
    patterns: [...patterns].sort(),
    inSyllabus: dir in PHASE_LABELS,
    firstPage: first,
  });
}
phaseRows.sort((a, b) => a.phase.localeCompare(b.phase));

const doc = {
  generated: "scripts/gen-dsa-syllabus.mjs — do not edit by hand",
  phases: phaseRows,
  pages: entries.map(({ phase, phaseLabel, title, url, difficulty, patterns }) => ({
    phase,
    phaseLabel,
    title,
    url,
    difficulty,
    patterns,
  })),
};

writeFileSync(OUT, yaml.dump(doc, { lineWidth: 100, noRefs: true }), "utf8");

const bar = "─".repeat(72);
console.log(bar);
console.log(`DSA syllabus — ${entries.length} pattern pages in teaching order`);
console.log(bar);
console.log(`  distinct patterns : ${seen.size}`);
console.log(`  phases covered    : ${new Set(entries.map((e) => e.phase)).size}`);
console.log(`  pages skipped     : ${skipped} (no \`patterns:\` — orientation / reference / company)`);
console.log(`  phase rows        : ${phaseRows.length} (every phase, incl. non-syllabus)`);
console.log(`  written to        : ${OUT}`);

// The Astro sidebar's hand-written page-count badges are gone: the Next
// sidebar (components/docs/Sidebar.tsx) counts pages from the content itself.
console.log("");

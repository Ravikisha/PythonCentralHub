/**
 * scripts/audit-dsa.mjs — spine coverage audit for the DSA course.
 *
 * WHY THIS EXISTS
 * ---------------
 * The plan is to bring 113 existing pages (and ~52 new ones) to a single page
 * spine: a cue, an interactive visualization, a dry run, a variant ladder,
 * pitfalls, interviewer follow-ups, a generated practice ladder, exercises, a
 * quiz, and a recall card. A retrofit of that size does not fail by being
 * *wrong*; it fails by quietly stopping at 60% with no way to see which 60%.
 *
 * So coverage is measured, not remembered. This script scores every page against
 * the spine, writes docs/dsa-coverage.md, and exits non-zero once the ratchet
 * (see BASELINE below) is armed.
 *
 * THE RATCHET
 * -----------
 * Failing the whole build today would just mean the check gets disabled. Instead
 * `BASELINE` records how many pages currently pass. The script fails only if
 * that number goes *down* — so coverage can only improve, and raising the
 * baseline is an explicit, reviewable commit.
 *
 * Run: npm run dsa:audit
 */
import { readdirSync, readFileSync, statSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join, relative, sep } from "node:path";

const DOCS = "src/content/docs/DSA with Python";
const REPORT = "docs/dsa-coverage.md";

/**
 * Number of pages that currently satisfy every spine requirement.
 * RAISE THIS as pages are retrofitted. Never lower it without saying why.
 */
const BASELINE = 153;

// ── page discovery ─────────────────────────────────────────────────────────

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

const phaseOf = (file) => relative(DOCS, file).split(sep)[0];
const nameOf = (file) => relative(DOCS, file).split(sep).pop().replace(/\.mdx$/, "");

/**
 * Pages that are legitimately exempt from parts of the spine.
 *
 * A cheatsheet has no "cue" and needs no visualization; a problem set is all
 * practice and no template. Exempting them is honest — forcing a Dry run section
 * onto a complexity cheatsheet would be cargo-culting the checklist.
 */
const EXEMPT_PHASES = {
  // Orientation and sheet-tracker pages teach no pattern — they route the reader
  // to the pages that do. Requiring a cue or a dry run here would be nonsense.
  "Phase-00-Start-Here": [
    "cue",
    "dryrun",
    "variants",
    "viz",
    "complexity",
    "followups",
    "exercises",
    "recall",
    "ladder",
    "pitfalls",
    "quiz",
  ],
  "Phase-18-Templates-and-Cheatsheets": ["cue", "dryrun", "variants", "viz", "quiz"],
  "Phase-19-Interview-and-Contest-Strategy": ["cue", "dryrun", "variants", "viz", "exercises"],
  "Phase-20-Problem-Sets": ["cue", "dryrun", "variants", "viz", "recall"],

  // Phase-01 and Phase-02 are *foundations and language reference*, not patterns.
  // Three checks are meaningless here and forcing them would be cargo-culting:
  //
  //   cue      — "you are looking at this pattern when…" presupposes a pattern.
  //              "Big-O and Complexity Deep Dive" is not something you recognise
  //              from a problem statement; it is something you already know.
  //   variants  — the variant map mutates a pattern's parameters. Nothing to mutate.
  //   ladder    — none of these pages owns a problem set. They are prerequisites
  //              *for* the pattern pages, which carry the ladders. Inventing a
  //              pattern slug per page would trip validate-problems.mjs with an
  //              "empty ladder" warning, exactly as it does for Phase-00.
  //
  // Everything else IS required and delivered: complexity, pitfalls, followups,
  // exercises, quiz, recall — plus dryrun on the eight pages where there is
  // genuinely something to trace (see EXEMPT_PAGES for the two where there is not).
  // Phase-21 is company *guides*, not pattern pages. The practice surface is
  // <CompanyBoard>, which renders the loop, the bar, the pattern families and the
  // reported-problem table straight from companies.yaml — so a `ladder` here would be
  // a second, worse copy of it, and there is no algorithm to cue, trace or vary.
  //
  // What IS required and delivered on all ten: frontmatter, pitfalls (the mistakes
  // specific to that loop), followups (its signature follow-up style) and a recall card.
  // Phase-22 is the low-level design / OOD round. Two checks do not apply:
  //
  //   viz    — the picture here is a mermaid class or state diagram, which is not one of
  //            VIZ_COMPONENTS and never will be: there is no array or graph to scrub
  //            through. Same reasoning already applied to Phases 18-20.
  //   ladder — LeetCode has essentially no OOD problems. "Design a parking lot" is asked
  //            in interviews and does not exist as a judge problem, so a ladder here would
  //            have to alias unrelated pattern slugs to look non-empty.
  //
  // Everything else is required and delivered: cue, dryrun (walking a design decision is
  // exactly what these pages should trace), complexity, variants, pitfalls, followups,
  // exercises, quiz, recall.
  // Phase-23 is the concurrency round (LC 1114-1226). Same two exemptions as Phase-22,
  // for the same reasons:
  //
  //   viz    — the thing to visualise is a thread *interleaving*, which is neither an array
  //            walk nor a graph traversal. A mermaid sequence diagram is the right picture
  //            and is not a VIZ_COMPONENTS entry.
  //   ladder — checked: LC 1114, 1115, 1116, 1117, 1188, 1195 and 1226 are all ABSENT from
  //            problems.yaml, because the harvester only sees problems linked from pattern
  //            pages and no pattern page links them. A ladder would resolve to nothing.
  //
  // Everything else is required and delivered, including dryrun — a traced interleaving is
  // exactly what these pages should show.
  "Phase-23-Concurrency": ["viz", "ladder"],
  "Phase-22-Low-Level-Design": ["viz", "ladder"],
  "Phase-21-Company-Guides": [
    "cue",
    "dryrun",
    "variants",
    "viz",
    "complexity",
    "exercises",
    "ladder",
    "quiz",
  ],
  "Phase-01-Foundations": ["cue", "variants", "ladder"],
  "Phase-02-Python-for-DSA-and-CP": ["cue", "variants", "ladder"],
};

/**
 * Per-page exemptions, keyed by `<phase>/<page name>`.
 *
 * Phase-level exemption is too blunt when one check is inapplicable to a couple of
 * pages but perfectly sensible for their neighbours. `dryrun` is the case in point:
 * tracing the call stack frame by frame, or applying the Master Theorem to a
 * concrete recurrence, is exactly what those pages should do — but a roadmap page
 * and an "install these tools" page have no algorithm to trace at all.
 */
const EXEMPT_PAGES = {
  // Routes the reader through the track. No algorithm on the page.
  "Phase-01-Foundations/Introduction to DSA with Python": ["dryrun"],
  // Accounts, interpreter choice, and a practice routine. Nothing to trace.
  "Phase-01-Foundations/Setup for CP and Interviews": ["dryrun"],
};

// ── requirement checks ─────────────────────────────────────────────────────

const VIZ_COMPONENTS = [
  "ArrayStepper",
  "TreeWalker",
  "GraphTraversal",
  "DPTable",
  "RecursionTree",
  "GridPathfinder",
  "LinkedListRewire",
  "BinarySearchDial",
  "StackMachine",
  "HeapView",
  "IntervalTimeline",
  "SortRace",
  "TrieView",
  "DSUView",
  "ComplexityChart",
  "BitBoard",
  "SegmentTreeView",
  "StateMachineView",
];

/**
 * Each check returns { ok, detail }. `detail` appears in the report so a failing
 * page says what is missing, not just that something is.
 */
const CHECKS = {
  /**
   * Pattern pages must declare `patterns:` and `difficulty:` — the ladder and the
   * company boards are driven off them.
   *
   * Orientation pages (Phase-00) teach no pattern and have no difficulty tier, so
   * demanding those keys there is wrong: satisfying it would mean inventing a
   * pattern slug per page, and `validate-problems.mjs` would then correctly report
   * eight "declared in frontmatter but no problem carries it — empty ladder"
   * warnings. Those pages get the requirement that actually applies to them
   * instead: a title and a description, since they are the routing surface.
   */
  frontmatter: (text, phase) => {
    const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!fm) return { ok: false, detail: "no frontmatter" };
    // Phase-00 (orientation) and Phase-01/02 (foundations and language reference)
    // teach no pattern, so `patterns:` / `difficulty:` do not apply — see
    // EXEMPT_PHASES. They get the requirement that fits a reference surface instead.
    const NO_PATTERN_PHASES = new Set([
      "Phase-00-Start-Here",
      "Phase-01-Foundations",
      "Phase-02-Python-for-DSA-and-CP",
      "Phase-21-Company-Guides",
      "Phase-22-Low-Level-Design",
      "Phase-23-Concurrency",
    ]);
    const keys = NO_PATTERN_PHASES.has(phase)
      ? ["title:", "description:"]
      : ["patterns:", "difficulty:"];
    const missing = keys.filter((k) => !fm[1].includes(k));
    return missing.length === 0
      ? { ok: true }
      : { ok: false, detail: `missing ${missing.join(" ")}` };
  },

  cue: (text) => {
    // The "cue" is what turns a reference page into a recognition drill: how do
    // you know, from the problem statement alone, that this is the pattern?
    const ok = /:::tip\[You are looking at|^## The cue/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no '## The cue' or 'You are looking at' tip" };
  },

  viz: (text) => {
    const used = VIZ_COMPONENTS.filter((c) => new RegExp(`<${c}\\b`).test(text));
    if (used.length > 0) return { ok: true, detail: used.join(", ") };
    // A p5 sketch still counts — the 35 existing ones are not being thrown away,
    // only migrated where a library component teaches it better.
    if (/```p5/.test(text)) return { ok: true, detail: "p5 (legacy)" };
    return { ok: false, detail: "no interactive visualization" };
  },

  dryrun: (text) => {
    const ok = /^## Dry run/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no '## Dry run' section" };
  },

  complexity: (text) => {
    const ok = /^## (Time and space complexity|Complexity)/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no complexity section" };
  },

  variants: (text) => {
    const ok = /^## (The variant map|Variant ladder|The variants)/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no variant map" };
  },

  pitfalls: (text) => {
    // Either a dedicated section, or the :::caution blocks that serve the same
    // purpose on the pages written before the spine existed.
    const ok = /^## (Pitfalls|Edge-case checklist)/m.test(text) || /:::caution/.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no pitfalls / edge cases / caution" };
  },

  followups: (text) => {
    const ok = /^## Interview follow-ups/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no '## Interview follow-ups'" };
  },

  ladder: (text) => {
    if (/<ProblemLadder\b/.test(text)) return { ok: true };
    // A hand-written LeetCode table is the thing ProblemLadder replaces, so it
    // is reported as a to-do rather than a pass.
    const links = (text.match(/leetcode\.com\/problems\//g) ?? []).length;
    return {
      ok: false,
      detail: links > 0 ? `${links} hand-written LC links, no <ProblemLadder>` : "no practice ladder",
    };
  },

  exercises: (text) => {
    const n = (text.match(/<DataCampExercise\b/g) ?? []).length;
    return n >= 3 ? { ok: true, detail: `${n}` } : { ok: false, detail: `${n} of 3 required` };
  },

  quiz: (text) => {
    if (!/<Quiz\b/.test(text)) return { ok: false, detail: "no <Quiz>" };
    // Count questions by their `q:` keys — a 1-question quiz is not a self-check.
    const block = text.slice(text.indexOf("<Quiz"));
    const n = (block.match(/^\s*q:\s/gm) ?? []).length;
    return n >= 4 ? { ok: true, detail: `${n} questions` } : { ok: false, detail: `${n} of 4 questions` };
  },

  recall: (text) => {
    const ok = /^## Recall card/m.test(text);
    return ok ? { ok: true } : { ok: false, detail: "no '## Recall card'" };
  },

  noRawLinks: (text) => {
    // Once a page has a ladder, stray hand-written LeetCode links are drift
    // waiting to happen. Links inside prose (an editorial aside) are fine; the
    // check only fires on table rows, which is where the duplication lives.
    if (!/<ProblemLadder\b/.test(text)) return { ok: true };
    const rows = (text.match(/^\|\s*\d+\s*\|\s*\[[^\]]+\]\(https:\/\/leetcode\.com/gm) ?? []).length;
    return rows === 0
      ? { ok: true }
      : { ok: false, detail: `${rows} hand-written table rows duplicate the ladder` };
  },
};

const ORDER = Object.keys(CHECKS);

// ── run ────────────────────────────────────────────────────────────────────

if (!existsSync(DOCS)) {
  console.error(`No such directory: ${DOCS}`);
  process.exit(1);
}

const files = walk(DOCS).sort();
const results = [];

for (const file of files) {
  const text = readFileSync(file, "utf8");
  const phase = phaseOf(file);
  const exempt = new Set([
    ...(EXEMPT_PHASES[phase] ?? []),
    ...(EXEMPT_PAGES[`${phase}/${nameOf(file)}`] ?? []),
  ]);

  const checks = {};
  for (const key of ORDER) {
    if (exempt.has(key)) {
      checks[key] = { ok: true, exempt: true };
      continue;
    }
    checks[key] = CHECKS[key](text, phase);
  }

  const required = ORDER.filter((k) => !exempt.has(k));
  const passed = required.filter((k) => checks[k].ok);

  results.push({
    file,
    phase,
    name: nameOf(file),
    checks,
    passed: passed.length,
    required: required.length,
    complete: passed.length === required.length,
  });
}

// ── report ─────────────────────────────────────────────────────────────────

const complete = results.filter((r) => r.complete);
const byPhase = new Map();
for (const r of results) {
  byPhase.set(r.phase, [...(byPhase.get(r.phase) ?? []), r]);
}

const perCheck = ORDER.map((key) => {
  const applicable = results.filter((r) => !r.checks[key].exempt);
  return { key, pass: applicable.filter((r) => r.checks[key].ok).length, of: applicable.length };
});

const pct = (n, d) => (d === 0 ? "—" : `${Math.round((n / d) * 100)}%`);

const lines = [
  "# DSA course — spine coverage",
  "",
  "<!-- Generated by scripts/audit-dsa.mjs. Do not edit by hand. -->",
  "",
  `**${complete.length} of ${results.length} pages** satisfy every spine requirement.`,
  `Ratchet baseline is **${BASELINE}** — the audit fails if the number above drops below it.`,
  "",
  "## By requirement",
  "",
  "| Requirement | Passing | Coverage |",
  "| --- | --- | --- |",
  ...perCheck.map((c) => `| \`${c.key}\` | ${c.pass} / ${c.of} | ${pct(c.pass, c.of)} |`),
  "",
  "## By phase",
  "",
  "| Phase | Complete | Pages |",
  "| --- | --- | --- |",
  ...[...byPhase.entries()]
    .sort()
    .map(([phase, rs]) => {
      const done = rs.filter((r) => r.complete).length;
      return `| ${phase} | ${done} / ${rs.length} | ${pct(done, rs.length)} |`;
    }),
  "",
  "## Page detail",
  "",
  "Only incomplete pages are listed. A page disappears from this table when it is done.",
  "",
];

for (const [phase, rs] of [...byPhase.entries()].sort()) {
  const incomplete = rs.filter((r) => !r.complete);
  if (incomplete.length === 0) continue;
  lines.push(`### ${phase}`, "");
  for (const r of incomplete) {
    const missing = ORDER.filter((k) => !r.checks[k].ok).map(
      (k) => `\`${k}\`${r.checks[k].detail ? ` (${r.checks[k].detail})` : ""}`,
    );
    lines.push(`- **${r.name}** — ${r.passed}/${r.required} · missing: ${missing.join(", ")}`);
  }
  lines.push("");
}

mkdirSync(dirname(REPORT), { recursive: true });
writeFileSync(REPORT, lines.join("\n"), "utf8");

// ── console summary ────────────────────────────────────────────────────────

const bar = "─".repeat(72);
console.log(bar);
console.log(`DSA spine coverage — ${complete.length} / ${results.length} pages complete`);
console.log(bar);
for (const c of perCheck) {
  const width = 28;
  const filled = c.of === 0 ? 0 : Math.round((c.pass / c.of) * width);
  console.log(
    `  ${c.key.padEnd(12)} ${"█".repeat(filled)}${"░".repeat(width - filled)} ` +
      `${String(c.pass).padStart(3)}/${c.of}  ${pct(c.pass, c.of)}`,
  );
}
console.log(`\n  report written to ${REPORT}`);

if (complete.length < BASELINE) {
  console.log(
    `\nFAILED — ${complete.length} complete pages is below the ratchet baseline of ${BASELINE}.` +
      `\nA page that used to satisfy the spine no longer does. See ${REPORT}.`,
  );
  process.exit(1);
}

console.log(
  `\nOK — at or above the baseline of ${BASELINE}.` +
    (complete.length > BASELINE
      ? ` Raise BASELINE in scripts/audit-dsa.mjs to ${complete.length} to lock this in.`
      : ""),
);

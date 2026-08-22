/**
 * src/data/dsa/index.ts — the single read path into the DSA problem database.
 *
 * Everything that renders a practice link on this site goes through here:
 * `<ProblemLadder>`, `<SheetTracker>`, `<CompanyBoard>`, the master index, and
 * the coverage audit. Nothing hand-writes a leetcode.com URL into a page.
 *
 * The four YAML files are read once at build time (Vite inlines them via
 * `?raw`), parsed, cross-linked, and frozen. There is no runtime fetch and no
 * client-side copy of the whole database — components receive only the rows
 * they need, already filtered.
 */
import yaml from "js-yaml";

import problemsRaw from "./problems.yaml?raw";
import sheetsRaw from "./sheets.yaml?raw";
import companiesRaw from "./companies.yaml?raw";
import syllabusRaw from "./syllabus.yaml?raw";
import recallRaw from "./recall.yaml?raw";

export type Difficulty = "easy" | "medium" | "hard";

export interface Problem {
  /** LeetCode number. `null` for problems that do not exist on LeetCode. */
  lc: number | null;
  /** LeetCode URL slug — the primary key. */
  slug: string;
  title: string;
  difficulty: Difficulty;
  /** Behind LeetCode Premium: linkable, but not solvable for free. */
  premium?: boolean;
  /** Difficulty and patterns are still unverified guesses. */
  review?: boolean;
  /** Pattern slugs. `<ProblemLadder pattern="x">` matches on these. */
  patterns: string[];
  /** Pages on this site that link the problem. */
  pages: string[];
  /** sheet key -> that sheet's section name for this problem. */
  sheets?: Record<string, string | boolean>;
  /** Company slugs. Crowd-reported — see the caveat in companies.yaml. */
  companies?: string[];
  /** 1-5 reported frequency. Absent means unknown, not rare. */
  freq?: number;
  /** Related problem numbers worth doing straight after. */
  variants?: number[];
}

export interface Sheet {
  key: string;
  name: string;
  author: string;
  url: string;
  count: number;
  blurb: string;
  ordered?: boolean;
  /** Title-listed sheets: section name -> problem titles. */
  sections?: Record<string, string[]>;
  /** Step-indexed sheets (Striver): step key -> step metadata. */
  by?: "step";
  steps?: Record<string, { title: string; count: number; patterns: string[] }>;
}

export interface CompanyRound {
  name: string;
  count: string | number;
  minutes: string | number;
  focus: string;
}

export interface Company {
  slug: string;
  name: string;
  blurb: string;
  rounds: CompanyRound[];
  bar: string;
  /** Pattern slugs this company leans on — the stable signal. */
  patterns: string[];
  quirks: string[];
}

// ── parse ─────────────────────────────────────────────────────────────────

export const problems: readonly Problem[] = Object.freeze(
  (yaml.load(problemsRaw) as Problem[]).map((p) =>
    Object.freeze({
      ...p,
      patterns: p.patterns ?? [],
      pages: p.pages ?? [],
    }),
  ),
);

export const sheets: readonly Sheet[] = Object.freeze(
  Object.entries(yaml.load(sheetsRaw) as Record<string, Omit<Sheet, "key">>).map(([key, s]) =>
    Object.freeze({ key, ...s }),
  ),
);

export const companies: readonly Company[] = Object.freeze(
  Object.values(yaml.load(companiesRaw) as Record<string, Company>).map((c) => Object.freeze(c)),
);

// ── indexes ───────────────────────────────────────────────────────────────

const bySlug = new Map(problems.map((p) => [p.slug, p]));
const byLc = new Map(problems.filter((p) => p.lc !== null).map((p) => [p.lc as number, p]));

const byPattern = new Map<string, Problem[]>();
for (const p of problems) {
  for (const pattern of p.patterns) {
    byPattern.set(pattern, [...(byPattern.get(pattern) ?? []), p]);
  }
}

const byCompany = new Map<string, Problem[]>();
for (const p of problems) {
  for (const c of p.companies ?? []) {
    byCompany.set(c, [...(byCompany.get(c) ?? []), p]);
  }
}

const sheetByKey = new Map(sheets.map((s) => [s.key, s]));
const companyBySlug = new Map(companies.map((c) => [c.slug, c]));

export const getProblem = (slugOrLc: string | number): Problem | undefined =>
  typeof slugOrLc === "number" ? byLc.get(slugOrLc) : bySlug.get(slugOrLc);

export const getSheet = (key: string): Sheet | undefined => sheetByKey.get(key);

export const getCompany = (slug: string): Company | undefined => companyBySlug.get(slug);

export const problemUrl = (p: Problem): string => `https://leetcode.com/problems/${p.slug}/`;

const DIFF_ORDER: Record<Difficulty, number> = { easy: 0, medium: 1, hard: 2 };

/**
 * Sort a ladder the way a reader should work it: easiest first, then by
 * reported frequency (most-reported first, since that is the better use of
 * limited time), then by problem number for stability.
 */
export function ladderSort(a: Problem, b: Problem): number {
  const d = DIFF_ORDER[a.difficulty] - DIFF_ORDER[b.difficulty];
  if (d !== 0) return d;
  const f = (b.freq ?? 0) - (a.freq ?? 0);
  if (f !== 0) return f;
  return (a.lc ?? 1e9) - (b.lc ?? 1e9);
}

/**
 * Problems for one or more pattern slugs, deduplicated and ladder-sorted.
 *
 * Accepts several patterns because a page often teaches more than one (a
 * frontmatter `patterns:` list is passed straight through).
 */
export function problemsForPatterns(patterns: string | string[]): Problem[] {
  const wanted = Array.isArray(patterns) ? patterns : [patterns];
  const seen = new Set<string>();
  const out: Problem[] = [];
  for (const pattern of wanted) {
    for (const p of byPattern.get(pattern) ?? []) {
      if (seen.has(p.slug)) continue;
      seen.add(p.slug);
      out.push(p);
    }
  }
  return out.sort(ladderSort);
}

/** Problems reported at a company, ladder-sorted. */
export function problemsForCompany(slug: string): Problem[] {
  return [...(byCompany.get(slug) ?? [])].sort(ladderSort);
}

/** Problems in a sheet, grouped in the sheet's own section order. */
export function problemsForSheet(key: string): { section: string; problems: Problem[] }[] {
  const sheet = sheetByKey.get(key);
  if (!sheet) return [];

  if (sheet.sections) {
    return Object.entries(sheet.sections).map(([section, titles]) => ({
      section,
      // Resolve by title through the same slug rule merge-sheets.mjs used, so a
      // sheet entry and its problem row can never drift apart.
      problems: titles
        .map((t) => bySlug.get(titleSlug(t)))
        .filter((p): p is Problem => p !== undefined),
    }));
  }

  if (sheet.steps) {
    return Object.entries(sheet.steps).map(([, step]) => ({
      section: step.title,
      problems: problemsForPatterns(step.patterns),
    }));
  }

  return [];
}

/** Must stay identical to `slugify` in scripts/merge-sheets.mjs. */
export function titleSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/['’.,()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Cross-sheet overlap: the problems that appear in the most sheets at once.
 *
 * This is the actual payoff of holding every sheet in one database — it answers
 * "what is the smallest set of problems that gets me the most coverage".
 */
export function crossSheetOverlap(minSheets = 2): { problem: Problem; sheets: string[] }[] {
  return problems
    .map((problem) => ({ problem, sheets: Object.keys(problem.sheets ?? {}) }))
    .filter((row) => row.sheets.length >= minSheets)
    .sort(
      (a, b) => b.sheets.length - a.sheets.length || ladderSort(a.problem, b.problem),
    );
}

/** Difficulty counts for a set of problems — used by progress rings and headers. */
export function difficultyBreakdown(list: readonly Problem[]): Record<Difficulty, number> {
  const out: Record<Difficulty, number> = { easy: 0, medium: 0, hard: 0 };
  for (const p of list) out[p.difficulty] += 1;
  return out;
}

/** Every pattern slug the database knows, sorted. Used by the audit. */
export const allPatterns: readonly string[] = Object.freeze([...byPattern.keys()].sort());


// ── syllabus and study plans ───────────────────────────────────────────────

/** One pattern page, in teaching order. Generated by scripts/gen-dsa-syllabus.mjs. */
export interface SyllabusPage {
  phase: string;
  phaseLabel: string;
  title: string;
  url: string;
  difficulty: string;
  patterns: string[];
}

/**
 * The course's pattern pages in the order they are meant to be learned: phase
 * sequence first, then `sidebar.order` within a phase.
 *
 * Generated, never hand-edited — the ordering lives in the filesystem and would
 * drift the moment a page moved.
 */
export const syllabus: readonly SyllabusPage[] = Object.freeze(
  ((yaml.load(syllabusRaw) as { pages: SyllabusPage[] }).pages ?? []).map((p) => Object.freeze(p)),
);

export interface StudyWeek {
  week: number;
  /** Pages to work through this week, in teaching order. */
  pages: SyllabusPage[];
  /** Problems drawn from those pages' patterns, deduplicated. */
  problems: Problem[];
  breakdown: Record<Difficulty, number>;
}

export interface StudyPlanOptions {
  /** Number of weeks available. */
  weeks?: number;
  /** Study hours per week — sets the problem budget. */
  hoursPerWeek?: number;
  /**
   * Restrict to a company's pattern families, in the course's teaching order.
   * Omit for the general plan (every pattern page).
   */
  company?: string;
  /** Rough problems solved per study hour. */
  problemsPerHour?: number;
}

export interface StudyPlan {
  weeks: StudyWeek[];
  /** Pages that did not fit in the available weeks. */
  deferred: SyllabusPage[];
  totalProblems: number;
  problemBudget: number;
  options: Required<Omit<StudyPlanOptions, "company">> & { company?: string };
}

/**
 * Build a week-by-week plan from the syllabus and the problem database.
 *
 * The shape of the answer is deliberately "pages, in order, split into weeks" rather
 * than "a hand-picked problem list": the teaching order already encodes prerequisites,
 * so slicing it is both defensible and self-maintaining. Weeks are balanced by
 * *problem count*, not by page count, because a 14-problem page is not a 3-problem
 * page's worth of work.
 *
 * `problemsPerHour` is the one honest fudge factor. It defaults to 1, which is
 * deliberately conservative: a medium takes most people 30-45 minutes including
 * reading the editorial afterwards.
 */
export function buildStudyPlan(opts: StudyPlanOptions = {}): StudyPlan {
  const weeks = Math.max(1, Math.min(opts.weeks ?? 8, 52));
  const hoursPerWeek = Math.max(1, opts.hoursPerWeek ?? 10);
  const problemsPerHour = opts.problemsPerHour ?? 1;
  const problemBudget = Math.max(1, Math.round(hoursPerWeek * problemsPerHour));

  const company = opts.company ? getCompany(opts.company) : undefined;
  const wanted = company ? new Set(company.patterns) : null;

  // Keep teaching order; filter to the company's families when one is given.
  const pages = syllabus.filter(
    (p) => !wanted || p.patterns.some((pat) => wanted.has(pat)),
  );

  /** Problems for a page, deduplicated against everything already scheduled. */
  const seen = new Set<string>();
  const forPage = (p: SyllabusPage): Problem[] => {
    const out: Problem[] = [];
    for (const prob of problemsForPatterns(p.patterns)) {
      if (seen.has(prob.slug)) continue;
      seen.add(prob.slug);
      out.push(prob);
    }
    return out;
  };

  const scheduled: { page: SyllabusPage; problems: Problem[] }[] = pages.map((page) => ({
    page,
    problems: forPage(page),
  }));

  const out: StudyWeek[] = [];
  let cursor = 0;

  for (let w = 1; w <= weeks && cursor < scheduled.length; w++) {
    const weekPages: SyllabusPage[] = [];
    const weekProblems: Problem[] = [];

    // Always take at least one page, then keep going while the budget allows. Taking
    // one unconditionally is what stops a single oversized page stalling the plan.
    while (cursor < scheduled.length) {
      const next = scheduled[cursor];
      const wouldBe = weekProblems.length + next.problems.length;
      if (weekPages.length > 0 && wouldBe > problemBudget) break;
      weekPages.push(next.page);
      weekProblems.push(...next.problems);
      cursor += 1;
    }

    out.push({
      week: w,
      pages: weekPages,
      problems: weekProblems,
      breakdown: difficultyBreakdown(weekProblems),
    });
  }

  return {
    weeks: out,
    deferred: scheduled.slice(cursor).map((s) => s.page),
    totalProblems: out.reduce((a, w) => a + w.problems.length, 0),
    problemBudget,
    options: { weeks, hoursPerWeek, problemsPerHour, company: opts.company },
  };
}

/** One phase's headline numbers. Generated by scripts/gen-dsa-syllabus.mjs. */
export interface PhaseRow {
  phase: string;
  label: string;
  number: string;
  pages: number;
  patterns: string[];
  /** False for orientation, reference, strategy, problem-set and company phases. */
  inSyllabus: boolean;
  firstPage: { title: string; url: string } | null;
}

/** Every phase directory, in order, with derived counts. */
export const phases: readonly PhaseRow[] = Object.freeze(
  ((yaml.load(syllabusRaw) as { phases?: PhaseRow[] }).phases ?? []).map((p) => Object.freeze(p)),
);

// --- spaced repetition -------------------------------------------------------

/** One prompt: `label` is the face shown, `text` is what the reader recalls. */
export interface RecallPrompt {
  /**
   * `aspect` — the bold named an aspect ("Cue"), so the label is a question.
   * `cloze`  — the bold WAS the claim, so it is hidden and the rest is the face.
   * `fact`   — a bold-only bullet with no second half.
   */
  kind: "aspect" | "cloze" | "fact";
  label: string;
  text: string;
}

/** One page's Recall card, as a set of prompts. */
export interface RecallCard {
  id: string;
  title: string;
  phase: string;
  url: string;
  patterns: string[];
  prompts: RecallPrompt[];
}

/**
 * Every Recall card on the course, generated by scripts/gen-recall-deck.mjs.
 * Derived from the pages themselves, so a card cannot drift from its page.
 */
export const recallCards: readonly RecallCard[] = Object.freeze(
  ((yaml.load(recallRaw) as { cards?: RecallCard[] }).cards ?? []).map((c) => Object.freeze(c)),
);

/** A prompt lifted out of its card, so a deck can be a flat shuffled list. */
export interface DeckItem extends RecallPrompt {
  /** `${card.id}#${index}` — stable across regenerations unless the page changes. */
  key: string;
  cardId: string;
  cardTitle: string;
  phase: string;
  url: string;
  patterns: string[];
}

/**
 * Flatten the cards into drillable items, optionally narrowed to some phases or
 * patterns. Order is deterministic here; the component shuffles per session so
 * that scheduling, not authoring order, decides what comes up.
 */
export function buildDeck(opts: { phases?: string[]; patterns?: string[] } = {}): DeckItem[] {
  const wantPhase = opts.phases?.length ? new Set(opts.phases) : null;
  const wantPattern = opts.patterns?.length ? new Set(opts.patterns) : null;
  const items: DeckItem[] = [];
  for (const c of recallCards) {
    if (wantPhase && !wantPhase.has(c.phase)) continue;
    if (wantPattern && !c.patterns.some((x) => wantPattern.has(x))) continue;
    c.prompts.forEach((p, i) => {
      items.push({
        ...p,
        key: `${c.id}#${i}`,
        cardId: c.id,
        cardTitle: c.title,
        phase: c.phase,
        url: c.url,
        patterns: c.patterns,
      });
    });
  }
  return items;
}

/** Every phase that contributes at least one card, in course order. */
export const recallPhases: readonly string[] = Object.freeze([
  ...new Set(recallCards.map((c) => c.phase)),
].sort());

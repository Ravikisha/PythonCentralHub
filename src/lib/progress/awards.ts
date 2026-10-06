/**
 * XP and badges, derived rather than stored.
 *
 * Nothing here is persisted. XP is a pure function of the progress already in
 * the store, and badges are thresholds over the same numbers. Storing either
 * would create a second copy of the truth that could drift from the first --
 * and a stored XP total is exactly the kind of number that has to be
 * recomputed anyway the moment the formula changes.
 *
 * The weights say what the site values: finishing a page is the unit of work,
 * a quiz is a smaller check, and a certificate is the only thing that took an
 * exam to earn.
 */
import type { ProgressState } from "./local";

export const XP_PER_PAGE = 10;
export const XP_PER_QUIZ = 5;
export const XP_PER_CERTIFICATE = 250;

export interface Award {
  /** Stable id, also the i18n key suffix: `pch.badge<Id>`. */
  id: string;
  earned: boolean;
  /** 0–1, for the ones still in progress. */
  ratio: number;
  /** How far along, in the badge's own unit. */
  have: number;
  need: number;
}

export interface Tally {
  xp: number;
  pages: number;
  quizzes: number;
  certificates: number;
  streak: number;
  /** Modules at 100%, needs the manifest counts to know. */
  modulesFinished: number;
  badges: Award[];
}

/** Badge thresholds. Order is display order. */
const BADGES: { id: string; need: number; of: keyof Counters }[] = [
  { id: "FirstPage", need: 1, of: "pages" },
  { id: "TenPages", need: 10, of: "pages" },
  { id: "FiftyPages", need: 50, of: "pages" },
  { id: "HundredPages", need: 100, of: "pages" },
  { id: "Quizzer", need: 10, of: "quizzes" },
  { id: "WeekStreak", need: 7, of: "streak" },
  { id: "MonthStreak", need: 30, of: "streak" },
  { id: "ModuleDone", need: 1, of: "modulesFinished" },
  { id: "Certified", need: 1, of: "certificates" },
];

interface Counters {
  pages: number;
  quizzes: number;
  streak: number;
  modulesFinished: number;
  certificates: number;
}

/**
 * Count everything and hand back the tally.
 *
 * `moduleCounts` comes from the build manifest; without it the
 * "module finished" badge simply never fires rather than guessing.
 * `certificates` is passed in because it is the one number the client cannot
 * derive -- only the server issues those.
 */
export function tally(
  state: ProgressState,
  moduleCounts: Record<string, number> = {},
  certificates = 0
): Tally {
  const pages = Object.values(state.modules).reduce((n, l) => n + l.length, 0);
  const quizzes = Object.keys(state.quizzes).length;
  const streak = state.streak.longest;

  const modulesFinished = Object.entries(state.modules).filter(([slug, list]) => {
    const total = moduleCounts[slug];
    return total ? list.length >= total : false;
  }).length;

  const counters: Counters = { pages, quizzes, streak, modulesFinished, certificates };

  const badges = BADGES.map(({ id, need, of }) => {
    const have = counters[of];
    return { id, need, have, earned: have >= need, ratio: Math.min(1, have / need) };
  });

  return {
    xp: pages * XP_PER_PAGE + quizzes * XP_PER_QUIZ + certificates * XP_PER_CERTIFICATE,
    pages,
    quizzes,
    certificates,
    streak,
    modulesFinished,
    badges,
  };
}

/**
 * Level from XP, on a widening curve: level n needs 100·n·(n+1)/2 XP, so each
 * level costs a little more than the last. Ten pages is level 1; the curve
 * keeps later levels meaningful without ever hard-stopping.
 */
export function levelFor(xp: number): { level: number; into: number; span: number } {
  let level = 0;
  let spent = 0;
  let cost = 100;

  while (spent + cost <= xp) {
    spent += cost;
    level += 1;
    cost = 100 * (level + 1);
  }

  // Levels count from 1: a new learner is at level 1 on their way to 2, not
  // "Level 0", which read as having nothing at all.
  return { level: level + 1, into: xp - spent, span: cost };
}

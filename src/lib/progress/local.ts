/**
 * Local progress store — the source of truth the UI reads from.
 *
 * Every progress interaction writes here first and renders immediately, then
 * a debounced background flush pushes the change to Firestore. That ordering
 * is what makes the feature usable on a static site: marking a page complete
 * cannot wait on an auth round trip plus a database write, and a reader with
 * no account (or no network) still gets working progress tracking.
 *
 * This module is deliberately Firebase-free. It renders on all ~1190 content
 * pages, so anything it imports statically would be shipped site-wide; the
 * sync layer is reached through a dynamic `import()` only when there is
 * something to flush.
 *
 * Every localStorage access is wrapped: private windows and blocked site data
 * throw on access rather than returning null, and progress tracking degrading
 * to "works until you close the tab" beats a page that throws.
 */
import { moduleOf, today, daysBetween } from "./ids";
import { readHint } from "../auth/hint";

const KEY = "pch-progress";

export interface QuizResult {
  correct: number;
  total: number;
  /** Epoch millis of the attempt. */
  at: number;
}

export interface ProgressState {
  v: 1;
  /** module slug -> completed page ids */
  modules: Record<string, string[]>;
  bookmarks: string[];
  /** `${pageId}#${ordinal}` -> best result */
  quizzes: Record<string, QuizResult>;
  /** pageId -> the learner's own note, private to them */
  notes: Record<string, string>;
  streak: { last: string; count: number; longest: number };
  /** Set once the cloud copy has been pulled down on this device. */
  hydrated: boolean;
}

function empty(): ProgressState {
  return {
    v: 1,
    modules: {},
    bookmarks: [],
    quizzes: {},
    notes: {},
    streak: { last: "", count: 0, longest: 0 },
    hydrated: false,
  };
}

export function read(): ProgressState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return empty();
    const parsed = JSON.parse(raw) as Partial<ProgressState>;
    // Merged into a fresh object so a value written by an older version of
    // this code never leaves a field undefined for the callers below.
    return { ...empty(), ...parsed, v: 1 };
  } catch {
    return empty();
  }
}

export function write(state: ProgressState): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* storage unavailable -- state stays in memory for this page only */
  }
  notify();
}

/* -------------------------------------------------------------------------- */
/* Change notification                                                         */
/* -------------------------------------------------------------------------- */

const listeners = new Set<(s: ProgressState) => void>();

/** Re-render on progress changes, including ones made in another tab. */
export function subscribe(fn: (state: ProgressState) => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function notify(): void {
  const state = read();
  listeners.forEach((fn) => fn(state));
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", (e) => {
    if (e.key === KEY) notify();
  });
}

/* -------------------------------------------------------------------------- */
/* Completion                                                                  */
/* -------------------------------------------------------------------------- */

export function isComplete(pageId: string, state = read()): boolean {
  return (state.modules[moduleOf(pageId)] ?? []).includes(pageId);
}

export function completedIn(moduleSlug: string, state = read()): number {
  return (state.modules[moduleSlug] ?? []).length;
}

export function totalCompleted(state = read()): number {
  return Object.values(state.modules).reduce((n, list) => n + list.length, 0);
}

/** Mark a page complete or clear it. Returns the new completion state. */
export function setComplete(pageId: string, on: boolean): boolean {
  const state = read();
  const mod = moduleOf(pageId);
  const list = new Set(state.modules[mod] ?? []);

  if (on) list.add(pageId);
  else list.delete(pageId);

  state.modules[mod] = [...list];
  if (on) bumpStreak(state);
  write(state);

  queue({ kind: on ? "complete" : "uncomplete", module: mod, pageId });
  return on;
}

/* -------------------------------------------------------------------------- */
/* Bookmarks                                                                   */
/* -------------------------------------------------------------------------- */

export function isBookmarked(pageId: string, state = read()): boolean {
  return state.bookmarks.includes(pageId);
}

export function setBookmark(pageId: string, on: boolean): boolean {
  const state = read();
  const set = new Set(state.bookmarks);
  if (on) set.add(pageId);
  else set.delete(pageId);
  state.bookmarks = [...set];
  write(state);

  queue({ kind: on ? "bookmark" : "unbookmark", pageId });
  return on;
}

/* -------------------------------------------------------------------------- */
/* Quiz results                                                                */
/* -------------------------------------------------------------------------- */

/**
 * Record a finished quiz, keeping the best score.
 *
 * `ordinal` distinguishes several quizzes on one page. These scores are for
 * the learner's own dashboard only -- the answers are in the page source, so
 * they can never gate a certificate. Phase 3's exams are graded server-side
 * for exactly that reason.
 */
export function recordQuiz(
  pageId: string,
  ordinal: number,
  correct: number,
  total: number
): void {
  const state = read();
  const key = `${pageId}#${ordinal}`;
  const prev = state.quizzes[key];
  if (prev && prev.correct >= correct) return;

  state.quizzes[key] = { correct, total, at: Date.now() };
  bumpStreak(state);
  write(state);

  queue({ kind: "quiz", key, correct, total });
}

/* -------------------------------------------------------------------------- */
/* Notes                                                                       */
/* -------------------------------------------------------------------------- */

/** Longest note we will store. Generous for a margin note, bounded for sync. */
export const NOTE_MAX = 4000;

export function getNote(pageId: string, state = read()): string {
  return state.notes[pageId] ?? "";
}

/**
 * Save or clear a private note. An empty note is deleted rather than stored as
 * "", so an emptied box does not keep a row alive forever.
 */
export function setNote(pageId: string, body: string): void {
  const state = read();
  const text = body.trim().slice(0, NOTE_MAX);

  if (text) state.notes[pageId] = text;
  else delete state.notes[pageId];

  write(state);
  queue({ kind: "note", pageId, text });
}

/* -------------------------------------------------------------------------- */
/* Streak                                                                      */
/* -------------------------------------------------------------------------- */

/**
 * Advance the day streak.
 *
 * Only real activity counts -- completing a page or finishing a quiz. Merely
 * loading a page does not, or the streak would measure browsing rather than
 * learning (and would cost a write on every page view).
 */
function bumpStreak(state: ProgressState): void {
  const day = today();
  if (state.streak.last === day) return;

  const gap = daysBetween(state.streak.last, day);
  state.streak.count = gap === 1 ? state.streak.count + 1 : 1;
  state.streak.last = day;
  state.streak.longest = Math.max(state.streak.longest, state.streak.count);
}

/* -------------------------------------------------------------------------- */
/* Last page visited                                                           */
/* -------------------------------------------------------------------------- */

const LAST_KEY = "pch-last-page";

export interface LastPage {
  pageId: string;
  href: string;
  title: string;
  at: number;
}

/**
 * Remember where the reader was, for the dashboard's "continue" link.
 *
 * Kept in its own key and never synced: it changes on every page view, and
 * putting it in the synced state would mean a Firestore write per page view
 * for something worth one line on one screen.
 */
export function setLastPage(pageId: string, href: string, title: string): void {
  try {
    localStorage.setItem(LAST_KEY, JSON.stringify({ pageId, href, title, at: Date.now() }));
  } catch {
    /* ignore */
  }
}

export function getLastPage(): LastPage | null {
  try {
    const raw = localStorage.getItem(LAST_KEY);
    return raw ? (JSON.parse(raw) as LastPage) : null;
  } catch {
    return null;
  }
}

/* -------------------------------------------------------------------------- */
/* Flush queue                                                                 */
/* -------------------------------------------------------------------------- */

export type PendingOp =
  | { kind: "complete" | "uncomplete"; module: string; pageId: string }
  | { kind: "bookmark" | "unbookmark"; pageId: string }
  | { kind: "quiz"; key: string; correct: number; total: number }
  | { kind: "note"; pageId: string; text: string };

let pending: PendingOp[] = [];
let timer: number | undefined;

/**
 * True when progress should be mirrored to Firestore.
 *
 * Only a real account (Google, GitHub, email+password) syncs. A guest's
 * progress is complete in localStorage and never leaves the device, so this
 * is checked from the Firebase-free auth hint -- no SDK, no network, nothing
 * loaded on a page where the answer is "no".
 */
function syncs(): boolean {
  const hint = readHint();
  return !!hint && !hint.anon;
}

/**
 * Buffer a change and flush it after a quiet period.
 *
 * Debounced rather than written straight through: a reader working down a
 * module can mark several pages in a few seconds, and each write would
 * otherwise be a separate Firestore round trip (and a separate billed write).
 */
function queue(op: PendingOp): void {
  // Guests never sync, so there is nothing to buffer -- and buffering anyway
  // would grow a queue that can only ever be discarded.
  if (!syncs()) return;

  pending.push(op);
  if (typeof window === "undefined") return;

  window.clearTimeout(timer);
  timer = window.setTimeout(() => void flush(), 1500);

  // A tab closed mid-debounce would lose the buffered writes, so take the
  // last chance to send them. Progress is already safe in localStorage; this
  // is only about getting it to the cloud copy.
  window.addEventListener("pagehide", flushNow, { once: true });
}

function flushNow(): void {
  if (pending.length) void flush();
}

export async function flush(): Promise<void> {
  if (!pending.length) return;

  // Signed out between queueing and flushing: keep the local copy, drop the
  // writes rather than leaving them to pile up.
  if (!syncs()) {
    pending = [];
    return;
  }

  const ops = pending;
  pending = [];

  try {
    const { pushOps } = await import("./sync");
    await pushOps(ops, read());
  } catch (err) {
    // Put them back so the next change retries them. Local state is already
    // correct either way, so a failed sync is never data loss.
    pending = ops.concat(pending);
    console.warn("[progress] sync deferred:", err);
  }
}

/**
 * Replace local state wholesale, e.g. after merging with the cloud copy.
 * Does not queue a flush: the caller has just reconciled both sides.
 */
export function replace(state: ProgressState): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* ignore */
  }
  notify();
}

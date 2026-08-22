/**
 * useDrill — SM-2-lite scheduling for the Recall-card deck.
 *
 * WHY NOT FULL SM-2
 * -----------------
 * Real SM-2 tracks an easiness factor per item and grades 0–5. That precision
 * is wasted here: the reader grades themselves, self-grading is noisy, and six
 * buttons is a worse interface than three. So this keeps SM-2's actual
 * mechanism — a repetition counter driving an expanding interval, reset to zero
 * on a lapse — and drops the easiness factor.
 *
 * The intervals, in days: 1, 3, 7, 16, 35, 75, 160. "Hard" repeats the current
 * interval instead of advancing, "Again" resets to the start of the ladder.
 *
 * Storage is separate from `useProgress` (`pch:dsa:drill:v1`) so that clearing
 * one cannot damage the other, and because the two have different lifetimes:
 * problem progress is a permanent record, drill state is a rolling schedule.
 */
import { useCallback, useEffect, useState } from "react";

export const DRILL_KEY = "pch:dsa:drill:v1";
const CHANNEL = "pch:dsa:drill";

/** How the reader rated their own recall. */
export type Grade = "again" | "hard" | "good";

/** Days between reviews, indexed by repetition count. */
export const INTERVALS = [1, 3, 7, 16, 35, 75, 160] as const;

export const DAY_MS = 86_400_000;

export interface CardState {
  /** How many consecutive successful reviews. Index into INTERVALS. */
  r: number;
  /** Epoch millis this item next becomes due. */
  due: number;
  /** Total reviews ever, including lapses — the honest exposure count. */
  n: number;
  /** Total "again" grades. A high ratio means the page needs rereading. */
  lapses: number;
}

export interface DrillState {
  v: 1;
  cards: Record<string, CardState>;
}

const EMPTY: DrillState = { v: 1, cards: {} };

function read(): DrillState {
  if (typeof localStorage === "undefined") return EMPTY;
  try {
    const raw = localStorage.getItem(DRILL_KEY);
    if (!raw) return EMPTY;
    const parsed = JSON.parse(raw) as DrillState;
    if (parsed?.v !== 1) return EMPTY; // forward-compatible: unknown version reads empty
    return { v: 1, cards: parsed.cards ?? {} };
  } catch {
    return EMPTY;
  }
}

function write(state: DrillState) {
  try {
    localStorage.setItem(DRILL_KEY, JSON.stringify(state));
  } catch {
    /* quota or private mode — drilling still works, it just will not persist */
  }
  window.dispatchEvent(new CustomEvent(CHANNEL));
}

/**
 * The scheduling rule itself, kept pure so it can be tested without React.
 *
 * `good`  advances one rung of the ladder.
 * `hard`  repeats the current rung — you saw it, but not fluently.
 * `again` drops to rung 0 and is due tomorrow, and counts as a lapse.
 */
export function schedule(prev: CardState | undefined, grade: Grade, now: number): CardState {
  const cur: CardState = prev ?? { r: 0, due: 0, n: 0, lapses: 0 };
  const n = cur.n + 1;

  if (grade === "again") {
    return { r: 0, due: now + INTERVALS[0] * DAY_MS, n, lapses: cur.lapses + 1 };
  }
  const r = grade === "good" ? Math.min(cur.r + 1, INTERVALS.length - 1) : cur.r;
  return { r, due: now + INTERVALS[r] * DAY_MS, n, lapses: cur.lapses };
}

export function useDrill() {
  const [state, setState] = useState<DrillState>(EMPTY);

  // Hydrate after mount: localStorage does not exist during SSR, and reading it
  // in the initial useState would make the server and client markup disagree.
  useEffect(() => {
    setState(read());
    const sync = () => setState(read());
    window.addEventListener(CHANNEL, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(CHANNEL, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const grade = useCallback((key: string, g: Grade) => {
    const next = read();
    next.cards[key] = schedule(next.cards[key], g, Date.now());
    write(next);
    setState(next);
  }, []);

  const reset = useCallback(() => {
    write(EMPTY);
    setState(EMPTY);
  }, []);

  return { state, grade, reset };
}

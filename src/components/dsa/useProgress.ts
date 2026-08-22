/**
 * useProgress — the reader's own record of what they have solved.
 *
 * Backed by `localStorage`, with no account and no server. That is a deliberate
 * trade: 700+ problems is far too many to track in your head, but requiring a
 * login to tick a checkbox would be worse. The cost of the trade is that the
 * data dies with a cleared cache — which is why export/import is a first-class
 * feature here rather than an afterthought.
 *
 * Every mounted tracker shares one state: writes broadcast a custom event, and
 * the `storage` event keeps other tabs in sync too.
 */
import { useCallback, useEffect, useState } from "react";

export const STORAGE_KEY = "pch:dsa:v1";
const CHANNEL = "pch:dsa:progress";

/** Where a problem stands. `review` means solved once but flagged to redo. */
export type Status = "todo" | "attempted" | "solved" | "review";

export interface ProblemProgress {
  /** Status. */
  s: Status;
  /** Last-touched epoch millis. */
  t: number;
  /** How many times the reader has marked an attempt. */
  n: number;
}

export interface ProgressState {
  v: 1;
  problems: Record<string, ProblemProgress>;
  /** Page slug -> epoch millis last marked read. */
  pages: Record<string, number>;
}

const EMPTY: ProgressState = { v: 1, problems: {}, pages: {} };

function read(): ProgressState {
  if (typeof localStorage === "undefined") return EMPTY;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY;
    const parsed = JSON.parse(raw) as ProgressState;
    // Forward-compatible: an unknown version is treated as empty rather than
    // crashing the page, and the old value is left untouched on disk.
    if (parsed?.v !== 1) return EMPTY;
    return { v: 1, problems: parsed.problems ?? {}, pages: parsed.pages ?? {} };
  } catch {
    return EMPTY;
  }
}

function write(next: ProgressState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Quota exceeded or storage disabled (private mode). Progress simply does
    // not persist; the UI keeps working for the session.
  }
  window.dispatchEvent(new CustomEvent(CHANNEL, { detail: next }));
}

/** The next status when a reader clicks the cycle control. */
const NEXT: Record<Status, Status> = {
  todo: "attempted",
  attempted: "solved",
  solved: "review",
  review: "todo",
};

export function useProgress() {
  // Start empty so server and first client render agree; the effect below then
  // loads the real value. Hydrating straight from localStorage would mismatch.
  const [state, setState] = useState<ProgressState>(EMPTY);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setState(read());
    setReady(true);

    const onLocal = (e: Event) => setState((e as CustomEvent<ProgressState>).detail);
    const onCrossTab = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) setState(read());
    };
    window.addEventListener(CHANNEL, onLocal);
    window.addEventListener("storage", onCrossTab);
    return () => {
      window.removeEventListener(CHANNEL, onLocal);
      window.removeEventListener("storage", onCrossTab);
    };
  }, []);

  const statusOf = useCallback(
    (slug: string): Status => state.problems[slug]?.s ?? "todo",
    [state],
  );

  const setStatus = useCallback((slug: string, s: Status) => {
    const current = read();
    const prev = current.problems[slug];
    const next: ProgressState = {
      ...current,
      problems: {
        ...current.problems,
        [slug]: {
          s,
          t: Date.now(),
          n: (prev?.n ?? 0) + (s === "attempted" || s === "solved" ? 1 : 0),
        },
      },
    };
    write(next);
  }, []);

  const cycleStatus = useCallback(
    (slug: string) => {
      setStatus(slug, NEXT[read().problems[slug]?.s ?? "todo"]);
    },
    [setStatus],
  );

  /** Solved count for a specific set of slugs — drives every progress ring. */
  const solvedCount = useCallback(
    (slugs: readonly string[]): number =>
      slugs.reduce((n, slug) => n + (state.problems[slug]?.s === "solved" ? 1 : 0), 0),
    [state],
  );

  const exportJson = useCallback((): string => JSON.stringify(read(), null, 2), []);

  /**
   * Merge an exported file back in. Merge rather than replace, so importing an
   * older backup cannot silently delete newer progress — the more advanced
   * status for each problem wins.
   */
  const importJson = useCallback((text: string): { ok: boolean; message: string } => {
    let incoming: ProgressState;
    try {
      incoming = JSON.parse(text) as ProgressState;
    } catch {
      return { ok: false, message: "That is not valid JSON." };
    }
    if (incoming?.v !== 1 || typeof incoming.problems !== "object") {
      return { ok: false, message: "Unrecognised progress file — expected a v1 export." };
    }

    const RANK: Record<Status, number> = { todo: 0, attempted: 1, review: 2, solved: 3 };
    const current = read();
    const merged: ProgressState = { v: 1, problems: { ...current.problems }, pages: { ...current.pages } };
    let changed = 0;
    for (const [slug, entry] of Object.entries(incoming.problems)) {
      const mine = merged.problems[slug];
      if (!mine || RANK[entry.s] > RANK[mine.s]) {
        merged.problems[slug] = entry;
        changed += 1;
      }
    }
    for (const [page, t] of Object.entries(incoming.pages ?? {})) {
      if (!merged.pages[page] || t > merged.pages[page]) merged.pages[page] = t;
    }
    write(merged);
    return { ok: true, message: `Merged ${changed} problem${changed === 1 ? "" : "s"}.` };
  }, []);

  const reset = useCallback(() => write(EMPTY), []);

  return {
    /** False until localStorage has been read — render checkboxes disabled until then. */
    ready,
    state,
    statusOf,
    setStatus,
    cycleStatus,
    solvedCount,
    exportJson,
    importJson,
    reset,
  };
}

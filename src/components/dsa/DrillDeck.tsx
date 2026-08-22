/**
 * DrillDeck — spaced repetition over the course's Recall cards.
 *
 * The deck is generated from the pages themselves (scripts/gen-recall-deck.mjs),
 * so a prompt cannot drift from the page it came from. Scheduling is SM-2-lite;
 * see useDrill for why the easiness factor is dropped.
 *
 * The interaction is deliberately three keys: space to reveal, then 1/2/3 to
 * grade. Anything slower than that and the reader stops using it.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useDrill, INTERVALS, type Grade } from "./useDrill";

export interface DeckItem {
  key: string;
  kind: "aspect" | "cloze" | "fact";
  label: string;
  text: string;
  cardId: string;
  cardTitle: string;
  phase: string;
  url: string;
}

interface Props {
  items: DeckItem[];
  /** Phase directory names, for the filter control. */
  phases: string[];
  /**
   * What one entry of `phases` is called in the UI. The Mathematics for Machine
   * Learning deck groups by chapter rather than phase, and the filter control
   * would otherwise read "Every phase" over a list of chapters.
   */
  groupNoun?: string;
  /**
   * Display label per `phases` entry. Anything absent falls back to the DSA
   * `Phase-NN-` rule.
   *
   * A map rather than a formatting function on purpose: Astro serialises island
   * props to JSON, so a function prop cannot cross the server/client boundary —
   * it fails at hydration, not at build. The caller formats server-side.
   */
  groupLabels?: Record<string, string>;
}

/** Deterministic shuffle, seeded per session so a reload reorders the queue. */
function shuffle<T>(list: T[], seed: number): T[] {
  const out = [...list];
  let s = seed || 1;
  for (let i = out.length - 1; i > 0; i--) {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const j = s % (i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

const phaseLabel = (p: string) => p.replace(/^Phase-(\d+)-/, "$1 · ").replace(/-/g, " ");

export default function DrillDeck({
  items,
  phases,
  groupNoun = "phase",
  groupLabels,
}: Props) {
  const { state, grade, reset } = useDrill();
  const [phase, setPhase] = useState<string>("all");
  const [revealed, setRevealed] = useState(false);
  const [pos, setPos] = useState(0);
  const [seed, setSeed] = useState(1);
  const [onlyDue, setOnlyDue] = useState(true);
  const [done, setDone] = useState(0);

  // A new seed per mount; kept out of render so SSR and hydration agree.
  useEffect(() => setSeed(Math.floor(Math.random() * 2 ** 31)), []);

  const pool = useMemo(
    () => (phase === "all" ? items : items.filter((i) => i.phase === phase)),
    [items, phase],
  );

  // "Due" means never seen, or scheduled on or before now — so a fresh reader
  // gets the whole deck rather than an empty queue. Order within the due set is
  // shuffled, not sorted: reviewing in page order lets you recall the sequence
  // instead of the fact, which is exactly the failure spaced repetition exists
  // to prevent.
  const queue = useMemo(() => {
    const now = Date.now();
    const due = pool.filter((i) => {
      const st = state.cards[i.key];
      return !st || st.due <= now;
    });
    const chosen = onlyDue ? due : pool;
    return shuffle(chosen, seed);
  }, [pool, state, seed, onlyDue]);

  const current = queue[pos % Math.max(queue.length, 1)];

  const answer = useCallback(
    (g: Grade) => {
      if (!current) return;
      grade(current.key, g);
      setRevealed(false);
      setPos((p) => p + 1);
      setDone((d) => d + 1);
    },
    [current, grade],
  );

  // Keyboard: space reveals, 1/2/3 grade. Ignored while typing in a control.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && /^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName)) return;
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        setRevealed((r) => !r);
      } else if (revealed && (e.key === "1" || e.key === "2" || e.key === "3")) {
        e.preventDefault();
        answer(e.key === "1" ? "again" : e.key === "2" ? "hard" : "good");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [revealed, answer]);

  const stats = useMemo(() => {
    const now = Date.now();
    let seen = 0;
    let dueNow = 0;
    let mature = 0;
    for (const i of pool) {
      const st = state.cards[i.key];
      if (!st) { dueNow += 1; continue; }
      seen += 1;
      if (st.due <= now) dueNow += 1;
      if (st.r >= 3) mature += 1;
    }
    return { seen, dueNow, mature, total: pool.length };
  }, [pool, state]);

  const nextIn = (g: Grade): string => {
    const st = current ? state.cards[current.key] : undefined;
    const r = st?.r ?? 0;
    const days = g === "again" ? INTERVALS[0] : INTERVALS[g === "good" ? Math.min(r + 1, INTERVALS.length - 1) : r];
    return days === 1 ? "1 day" : `${days} days`;
  };

  return (
    <div className="drill">
      <div className="drill-bar">
        <select value={phase} onChange={(e) => { setPhase(e.target.value); setPos(0); setRevealed(false); }}>
          <option value="all">Every {groupNoun} ({items.length} prompts)</option>
          {phases.map((p) => (
            <option key={p} value={p}>{groupLabels?.[p] ?? phaseLabel(p)}</option>
          ))}
        </select>
        <label className="drill-toggle">
          <input type="checkbox" checked={onlyDue} onChange={(e) => { setOnlyDue(e.target.checked); setPos(0); }} />
          due only
        </label>
        <span className="drill-stats">
          <b>{stats.dueNow}</b> due · {stats.seen}/{stats.total} seen · {stats.mature} mature
        </span>
      </div>

      {!current ? (
        <div className="drill-empty">
          <p><b>Nothing due.</b> Every prompt in this selection is scheduled for later.</p>
          <p className="drill-hint">
            Untick <em>due only</em> to drill anyway, or come back tomorrow — the first
            interval is {INTERVALS[0]} day and the longest is {INTERVALS[INTERVALS.length - 1]}.
          </p>
        </div>
      ) : (
        <div className="drill-card">
          <div className="drill-meta">
            <a href={current.url}>{current.cardTitle}</a>
            <span className={`drill-kind drill-kind-${current.kind}`}>{current.kind}</span>
          </div>

          <p className="drill-front">{current.label}</p>

          {revealed ? (
            <p className="drill-back">{current.text}</p>
          ) : (
            <button className="drill-reveal" onClick={() => setRevealed(true)}>
              Reveal <kbd>space</kbd>
            </button>
          )}

          {revealed && (
            <div className="drill-grades">
              <button className="g-again" onClick={() => answer("again")}>
                <kbd>1</kbd> Again <small>{nextIn("again")}</small>
              </button>
              <button className="g-hard" onClick={() => answer("hard")}>
                <kbd>2</kbd> Hard <small>{nextIn("hard")}</small>
              </button>
              <button className="g-good" onClick={() => answer("good")}>
                <kbd>3</kbd> Good <small>{nextIn("good")}</small>
              </button>
            </div>
          )}
        </div>
      )}

      <div className="drill-foot">
        <span>{done} graded this session</span>
        <button
          className="drill-reset"
          onClick={() => {
            if (confirm("Erase all drill scheduling? Your solved-problem progress is stored separately and will not be touched.")) {
              reset();
              setPos(0);
              setDone(0);
            }
          }}
        >
          Reset schedule
        </button>
      </div>

      <style>{`
        .drill { border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem; padding: 1rem; }
        .drill-bar { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.9rem; }
        .drill-bar select { padding: 0.3rem 0.5rem; border-radius: 0.35rem; background: var(--sl-color-black); color: var(--sl-color-white); border: 1px solid var(--sl-color-gray-5); max-width: 100%; }
        .drill-toggle { display: inline-flex; gap: 0.35rem; align-items: center; font-size: 0.85rem; }
        .drill-stats { margin-left: auto; font-size: 0.82rem; color: var(--sl-color-gray-3); }
        .drill-card { background: var(--sl-color-gray-6); border-radius: 0.45rem; padding: 1rem; }
        .drill-meta { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; font-size: 0.8rem; margin-bottom: 0.6rem; }
        .drill-kind { text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.66rem; padding: 0.1rem 0.4rem; border-radius: 0.2rem; border: 1px solid var(--sl-color-gray-5); color: var(--sl-color-gray-3); }
        .drill-front { font-size: 1.05rem; margin: 0.4rem 0 0.9rem; }
        .drill-back { border-top: 1px dashed var(--sl-color-gray-5); padding-top: 0.8rem; margin: 0; color: var(--sl-color-white); }
        .drill-reveal { width: 100%; padding: 0.55rem; border-radius: 0.35rem; border: 1px solid var(--sl-color-gray-5); background: transparent; color: var(--sl-color-white); cursor: pointer; }
        .drill-grades { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-top: 0.9rem; }
        .drill-grades button { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; padding: 0.5rem; border-radius: 0.35rem; cursor: pointer; border: 1px solid var(--sl-color-gray-5); background: transparent; color: var(--sl-color-white); }
        .drill-grades small { color: var(--sl-color-gray-3); font-size: 0.7rem; }
        .g-again { border-color: #d9534f !important; }
        .g-hard  { border-color: #dbab5a !important; }
        .g-good  { border-color: #8cd2a0 !important; }
        .drill-grades kbd, .drill-reveal kbd { font-size: 0.7rem; border: 1px solid var(--sl-color-gray-5); border-radius: 0.2rem; padding: 0 0.25rem; }
        .drill-empty { padding: 1.2rem; text-align: center; }
        .drill-hint { font-size: 0.85rem; color: var(--sl-color-gray-3); }
        .drill-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 0.8rem; font-size: 0.78rem; color: var(--sl-color-gray-3); }
        .drill-reset { background: none; border: none; color: var(--sl-color-gray-3); text-decoration: underline; cursor: pointer; font-size: 0.78rem; }
        @media (max-width: 30rem) { .drill-grades { grid-template-columns: 1fr; } .drill-stats { margin-left: 0; } }
      `}</style>
    </div>
  );
}

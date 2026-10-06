"use client";

/**
 * MockInterview — a timed 45-minute round with a real judge and a rubric.
 *
 * WHAT THIS IS FOR
 * ----------------
 * Solving problems untimed on LeetCode trains the wrong thing. The round is 45
 * minutes, it has a shape, and most failures are pacing and communication
 * failures rather than algorithmic ones. So the clock here is not decoration:
 * it is segmented into the four phases the FAANG playbook page describes, and
 * it tells you when you have overspent one.
 *
 * THE JUDGE
 * ---------
 * Pyodide, shared with the site's code playground via `window.__pchPyodide` so
 * the ~10 MB runtime is downloaded at most once per page. Output is captured by
 * redirecting `sys.stdout` inside Python rather than by using the playground's
 * JS stdout hooks, which belong to the playground and would fight with us.
 *
 * WHAT IT DELIBERATELY DOES NOT DO
 * --------------------------------
 * It does not grade your code. There is no hidden test suite per problem — the
 * course has 446 problems and hand-writing judges for them would be a different
 * project. You write your own assertions, which is itself the skill the "test
 * your solution" phase is scored on. The rubric at the end is self-scored, and
 * self-scoring is honest only if you do it right after the timer, so it is
 * presented immediately and cannot be skipped to.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export interface MockProblem {
  lc: number | null;
  slug: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
  patterns: string[];
}

interface Props {
  problems: MockProblem[];
  /** Total round length in minutes. */
  minutes?: number;
}

/** The four phases, as minute budgets that sum to the round. */
const PHASES = [
  { name: "Clarify", share: 5 / 45, hint: "Restate the problem. Ask about input size, duplicates, empty input, and what to return on failure. Say the constraint back." },
  { name: "Approach", share: 8 / 45, hint: "State a brute force and its complexity FIRST, then the optimisation. Get agreement before typing." },
  { name: "Code", share: 22 / 45, hint: "Narrate as you go. Name variables properly. If you get stuck, say what you are stuck on." },
  { name: "Test", share: 10 / 45, hint: "Walk a small example by hand. Then edge cases: empty, one element, duplicates, overflow. State the final complexity." },
] as const;

const RUBRIC = [
  { key: "clarify", label: "Clarified before coding", detail: "Restated the problem and asked about at least two edge conditions." },
  { key: "bruteforce", label: "Stated a brute force first", detail: "Named an obvious solution and its complexity before optimising." },
  { key: "approach", label: "Justified the approach", detail: "Said why this pattern fits, not just what the code does." },
  { key: "narration", label: "Talked while coding", detail: "No silent stretches longer than about thirty seconds." },
  { key: "working", label: "Code runs", detail: "It executes and produces the right answer on your own examples." },
  { key: "edges", label: "Tested edge cases", detail: "Empty, single element, duplicates — before being asked." },
  { key: "complexity", label: "Stated final complexity", detail: "Time and space, correctly, without prompting." },
  { key: "pacing", label: "Finished inside the clock", detail: "Working code with time left for testing." },
] as const;

const STORE = "pch:dsa:mock:v1";

interface Session {
  at: number;
  slug: string;
  title: string;
  difficulty: string;
  score: number;
  outOf: number;
  seconds: number;
}

const mmss = (s: number) => {
  const m = Math.floor(Math.abs(s) / 60);
  const r = Math.abs(s) % 60;
  return `${s < 0 ? "-" : ""}${m}:${String(r).padStart(2, "0")}`;
};

const STARTER = `# Write your solution here, then add your own assertions below.
# The judge runs this file as-is — nothing is hidden, so what you assert
# is what gets checked. That is the point of the "test" phase.

def solve(nums):
    ...


assert solve([]) == ..., "empty input"
print("all assertions passed")
`;

export default function MockInterview({ problems, minutes = 45 }: Props) {
  const total = minutes * 60;

  const [difficulty, setDifficulty] = useState<"any" | "easy" | "medium" | "hard">("medium");
  const [problem, setProblem] = useState<MockProblem | null>(null);
  const [left, setLeft] = useState(total);
  const [running, setRunning] = useState(false);
  const [finished, setFinished] = useState(false);
  const [code, setCode] = useState(STARTER);
  const [output, setOutput] = useState("");
  const [busy, setBusy] = useState(false);
  const [marks, setMarks] = useState<Record<string, boolean>>({});
  const [log, setLog] = useState<Session[]>([]);
  const tick = useRef<number | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORE);
      if (raw) setLog(JSON.parse(raw) as Session[]);
    } catch { /* unreadable history is not worth failing over */ }
  }, []);

  const pool = useMemo(
    () => (difficulty === "any" ? problems : problems.filter((p) => p.difficulty === difficulty)),
    [problems, difficulty],
  );

  const start = useCallback(() => {
    if (pool.length === 0) return;
    setProblem(pool[Math.floor(Math.random() * pool.length)]);
    setLeft(total);
    setRunning(true);
    setFinished(false);
    setCode(STARTER);
    setOutput("");
    setMarks({});
  }, [pool, total]);

  // The clock. Runs down to zero and stops; it does not auto-submit, because
  // being over time is information you want to see rather than be rescued from.
  useEffect(() => {
    if (!running) return;
    tick.current = window.setInterval(() => {
      setLeft((s) => {
        if (s <= 1) {
          window.clearInterval(tick.current!);
          setRunning(false);
          setFinished(true);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => { if (tick.current) window.clearInterval(tick.current); };
  }, [running]);

  const elapsed = total - left;
  const phase = useMemo(() => {
    let acc = 0;
    for (let i = 0; i < PHASES.length; i++) {
      acc += PHASES[i].share * total;
      if (elapsed < acc) return { ...PHASES[i], index: i, endsAt: acc };
    }
    return { ...PHASES[PHASES.length - 1], index: PHASES.length - 1, endsAt: total };
  }, [elapsed, total]);

  const run = useCallback(async () => {
    setBusy(true);
    setOutput("Loading Python…");
    try {
      const loader = (window as unknown as { __pchPyodide?: () => Promise<any> }).__pchPyodide;
      if (!loader) {
        setOutput(
          "The Python runtime is not available on this page.\n" +
            "python-playground.js provides it; check that the script is loaded.",
        );
        return;
      }
      const py = await loader();
      // Capture output inside Python so the playground's own stdout hooks,
      // which are global, are left exactly as they were.
      py.globals.set("__mock_src", code);
      const res = await py.runPythonAsync(`
import sys, io, traceback
__buf = io.StringIO()
__old_out, __old_err = sys.stdout, sys.stderr
sys.stdout = sys.stderr = __buf
try:
    exec(compile(__mock_src, "<mock>", "exec"), {"__name__": "__main__"})
except BaseException:
    traceback.print_exc()
finally:
    sys.stdout, sys.stderr = __old_out, __old_err
__buf.getvalue()
`);
      setOutput(String(res).trim() || "(no output)");
    } catch (err) {
      setOutput(`Runner error: ${(err as Error).message}`);
    } finally {
      setBusy(false);
    }
  }, [code]);

  const finish = () => { setRunning(false); setFinished(true); };

  const score = RUBRIC.filter((r) => marks[r.key]).length;

  const save = () => {
    if (!problem) return;
    const entry: Session = {
      at: Date.now(),
      slug: problem.slug,
      title: problem.title,
      difficulty: problem.difficulty,
      score,
      outOf: RUBRIC.length,
      seconds: elapsed,
    };
    const next = [entry, ...log].slice(0, 25);
    setLog(next);
    try { localStorage.setItem(STORE, JSON.stringify(next)); } catch { /* private mode */ }
    setProblem(null);
    setFinished(false);
    setLeft(total);
  };

  const pct = Math.min(100, (elapsed / total) * 100);
  const over = phase.index === PHASES.length - 1 && left === 0;

  return (
    <div className="mock">
      {!problem ? (
        <div className="mock-setup">
          <h3>Start a {minutes}-minute round</h3>
          <p className="mock-sub">
            A problem is drawn at random and the clock starts immediately — no reading it
            over first, because you do not get that in the round either.
          </p>
          <div className="mock-controls">
            <select value={difficulty} onChange={(e) => setDifficulty(e.target.value as typeof difficulty)}>
              <option value="any">Any difficulty</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <span className="mock-count">{pool.length} problems</span>
            <button className="mock-go" onClick={start} disabled={pool.length === 0}>
              Start
            </button>
          </div>

          {log.length > 0 && (
            <div className="mock-log">
              <h4>Your last {log.length} round{log.length === 1 ? "" : "s"}</h4>
              <table>
                <thead>
                  <tr><th>Problem</th><th>Score</th><th>Time</th></tr>
                </thead>
                <tbody>
                  {log.map((s, i) => (
                    <tr key={i}>
                      <td>
                        <a href={`https://leetcode.com/problems/${s.slug}/`} target="_blank" rel="noopener">
                          {s.title}
                        </a>
                        <span className={`d-${s.difficulty}`}> {s.difficulty}</span>
                      </td>
                      <td>{s.score}/{s.outOf}</td>
                      <td>{mmss(s.seconds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="mock-head">
            <div>
              <a
                className="mock-title"
                href={`https://leetcode.com/problems/${problem.slug}/`}
                target="_blank"
                rel="noopener"
              >
                {problem.lc ? `${problem.lc}. ` : ""}{problem.title}
              </a>
              <span className={`d-${problem.difficulty}`}>{problem.difficulty}</span>
            </div>
            <div className={`mock-clock ${left <= 300 ? "low" : ""}`}>{mmss(left)}</div>
          </div>

          <div className="mock-track">
            {PHASES.map((p, i) => (
              <div
                key={p.name}
                className={`mock-seg ${i === phase.index ? "on" : i < phase.index ? "past" : ""}`}
                style={{ flexGrow: p.share }}
                title={p.hint}
              >
                {p.name}
              </div>
            ))}
            <div className="mock-needle" style={{ left: `${pct}%` }} />
          </div>

          {!finished && (
            <p className="mock-hint"><b>{phase.name}.</b> {phase.hint}</p>
          )}
          {over && <p className="mock-over">Time is up. Score yourself now, while it is fresh.</p>}

          {!finished ? (
            <>
              <textarea
                className="mock-editor"
                value={code}
                spellCheck={false}
                onChange={(e) => setCode(e.target.value)}
                rows={16}
              />
              <div className="mock-actions">
                <button onClick={run} disabled={busy}>{busy ? "Running…" : "Run"}</button>
                <button className="mock-finish" onClick={finish}>Finish and score</button>
              </div>
              {output && <pre className="mock-out">{output}</pre>}
            </>
          ) : (
            <div className="mock-rubric">
              <h4>Score yourself — {score} of {RUBRIC.length}</h4>
              <p className="mock-sub">
                Tick only what you actually did. A rubric you flatter is worth nothing;
                the point is to find the one line you keep missing.
              </p>
              {RUBRIC.map((r) => (
                <label key={r.key} className="mock-check">
                  <input
                    type="checkbox"
                    checked={!!marks[r.key]}
                    onChange={(e) => setMarks({ ...marks, [r.key]: e.target.checked })}
                  />
                  <span><b>{r.label}</b> — {r.detail}</span>
                </label>
              ))}
              <div className="mock-actions">
                <button className="mock-go" onClick={save}>Save and finish</button>
                <button onClick={() => { setProblem(null); setFinished(false); setLeft(total); }}>
                  Discard
                </button>
              </div>
            </div>
          )}
        </>
      )}

      <style>{`
        .mock { border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem; padding: 1rem; }
        .mock h3, .mock h4 { margin: 0 0 0.4rem; }
        .mock-sub { font-size: 0.86rem; color: var(--sl-color-gray-3); margin: 0 0 0.8rem; }
        .mock-controls { display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap; }
        .mock-controls select, .mock button { padding: 0.4rem 0.7rem; border-radius: 0.35rem; border: 1px solid var(--sl-color-gray-5); background: var(--sl-color-black); color: var(--sl-color-white); cursor: pointer; }
        .mock-go { background: var(--sl-color-accent) !important; border-color: var(--sl-color-accent) !important; }
        .mock-count { font-size: 0.82rem; color: var(--sl-color-gray-3); }
        .mock-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
        .mock-title { font-size: 1.05rem; font-weight: 600; }
        .mock-clock { font-variant-numeric: tabular-nums; font-size: 1.9rem; font-weight: 700; }
        .mock-clock.low { color: #d9534f; }
        .mock-track { position: relative; display: flex; gap: 2px; margin: 0.8rem 0 0.5rem; height: 1.5rem; }
        .mock-seg { display: flex; align-items: center; justify-content: center; font-size: 0.7rem; background: var(--sl-color-gray-6); color: var(--sl-color-gray-3); border-radius: 0.2rem; overflow: hidden; }
        .mock-seg.on { background: var(--sl-color-accent); color: var(--sl-color-black); }
        .mock-seg.past { background: var(--sl-color-gray-5); }
        .mock-needle { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--sl-color-white); }
        .mock-hint { font-size: 0.86rem; margin: 0.3rem 0 0.8rem; }
        .mock-over { color: #d9534f; font-weight: 600; }
        .mock-editor { width: 100%; font-family: var(--sl-font-mono, monospace); font-size: 0.84rem; line-height: 1.5; padding: 0.7rem; border-radius: 0.35rem; border: 1px solid var(--sl-color-gray-5); background: var(--sl-color-black); color: var(--sl-color-white); resize: vertical; }
        .mock-actions { display: flex; gap: 0.5rem; margin-top: 0.6rem; flex-wrap: wrap; }
        .mock-out { margin-top: 0.7rem; padding: 0.7rem; border-radius: 0.35rem; background: var(--sl-color-gray-6); font-size: 0.8rem; white-space: pre-wrap; max-height: 16rem; overflow: auto; }
        .mock-check { display: flex; gap: 0.5rem; align-items: flex-start; font-size: 0.86rem; padding: 0.3rem 0; }
        .mock-log { margin-top: 1.2rem; }
        .mock-log table { width: 100%; font-size: 0.84rem; }
        .d-easy { color: #8cd2a0; font-size: 0.74rem; }
        .d-medium { color: #dbab5a; font-size: 0.74rem; }
        .d-hard { color: #d9534f; font-size: 0.74rem; }
      `}</style>
    </div>
  );
}

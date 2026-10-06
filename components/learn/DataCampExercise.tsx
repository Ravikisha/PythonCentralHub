"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { runExercise, type RunResult, type RunStatus } from "./exercise-runner";

/**
 * A graded Python exercise: an editor, Run and Submit, and the course's own
 * check on the result.
 *
 * The name and props are DataCamp Light's, because 792 lessons use them, but
 * DataCamp is gone from here. Its backend runs Python 3.5.2 with numpy 1.11,
 * pandas 0.19 and scikit-learn 0.18, and 1,178 of the 2,900 exercises -- any
 * with an f-string, `np.random.default_rng` or modern pandas -- failed there
 * with "invalid syntax". They now run on Pyodide (current Python and
 * libraries) in a Web Worker, graded by a compatible implementation of the
 * two checks the course uses; see public/scripts/exercise-worker.js.
 *
 * The editor is a plain textarea: it loads instantly, works on a phone, and
 * is accessible without an editor library. Tab indents (Escape, then Tab,
 * leaves the editor), Enter keeps the indentation, Ctrl/Cmd+Enter runs and
 * Ctrl/Cmd+Shift+Enter submits. Edits are kept in this browser, so a reload
 * does not lose them.
 *
 * Authors: backticks and `${` still break these props -- they are template
 * literals in the MDX -- and an `sct` must check output that does not depend
 * on ordering or randomness.
 */
export interface DataCampExerciseProps {
  /** Always Python here; kept for the content's existing props. */
  lang?: string;
  /** The starting code shown to the learner. */
  code: string;
  /** Runs before the learner's code, in the same namespace. */
  preExerciseCode?: string;
  /** A complete, passing answer. */
  solution?: string;
  /** The check run on Submit (test_output_contains / success_msg). */
  sct?: string;
  hint?: string;
  /** Kept for compatibility; the hint always sits under the controls. */
  hintPlacement?: "before" | "after";
  /** Kept for compatibility; the controls always show. */
  showControls?: boolean;
  /** Editor height in px (DataCamp's), used as a minimum. */
  height?: number | "auto";
  /** What the solution prints, shown on request. */
  expectedOutput?: string;
}

const INDENT = "    ";

/** Small, stable string hash for the saved-draft key. */
function hash(text: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(36);
}

const STATUS_TEXT: Record<RunStatus, string> = {
  loading: "Starting Python… (the first run takes a few seconds)",
  packages: "Loading libraries…",
  running: "Running…",
};

type Phase = "idle" | "busy";

export function DataCampExercise({
  code,
  preExerciseCode,
  solution,
  sct,
  hint,
  height = "auto",
  expectedOutput,
}: DataCampExerciseProps) {
  const id = useId().replace(/:/g, "");
  const pathname = usePathname();
  const draftKey = useMemo(() => `pch-ex:${pathname}:${hash(code)}`, [pathname, code]);

  const [value, setValue] = useState(code);
  const [phase, setPhase] = useState<Phase>("idle");
  const [status, setStatus] = useState<string>("");
  const [result, setResult] = useState<RunResult | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [full, setFull] = useState(false);
  const editor = useRef<HTMLTextAreaElement>(null);
  const root = useRef<HTMLDivElement>(null);

  // A saved draft, read after mount so the server HTML (the starting code)
  // matches the first client render.
  useEffect(() => {
    try {
      const saved = localStorage.getItem(draftKey);
      if (saved !== null && saved !== code) setValue(saved);
    } catch {
      /* storage blocked: start from the given code */
    }
  }, [draftKey, code]);

  useEffect(() => {
    try {
      if (value === code) localStorage.removeItem(draftKey);
      else localStorage.setItem(draftKey, value);
    } catch {
      /* not saved; the editor still works */
    }
  }, [value, code, draftKey]);

  // Fullscreen is this element, fixed over the page, so nothing is rebuilt
  // and nothing typed is lost. Escape leaves it.
  useEffect(() => {
    if (!full) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && document.activeElement !== editor.current) setFull(false);
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [full]);

  const execute = useCallback(
    async (grade: boolean) => {
      if (phase === "busy") return;
      setPhase("busy");
      setResult(null);
      setStatus(STATUS_TEXT.loading);
      const outcome = await runExercise(
        { pre: preExerciseCode, code: value, sct: grade ? (sct ?? null) : null },
        (s) => setStatus(STATUS_TEXT[s]),
      );
      // A Submit always gets a verdict. A run cut off by the time limit, or a
      // Python that failed to start, comes back with no grade at all, and the
      // learner was left with no answer to what they had just submitted.
      if (grade && !outcome.grade) {
        outcome.grade = {
          passed: false,
          message: outcome.timedOut
            ? "Your code ran past the 30-second limit, so it could not be checked. Look for a loop that never ends."
            : (outcome.error ?? "Your code could not be checked. Run it again."),
        };
      }
      setResult(outcome);
      if (grade) setSubmitted(true);
      // Announced rather than stored here, like a finished quiz: the page's
      // progress controls record it (components/progress/PageProgress.tsx).
      if (grade && outcome.grade?.passed && root.current) {
        const ordinal = [...document.querySelectorAll(".ex")].indexOf(root.current);
        document.dispatchEvent(
          new CustomEvent("pch:exercise-passed", { detail: { ordinal } }),
        );
      }
      setStatus("");
      setPhase("idle");
    },
    [phase, preExerciseCode, value, sct],
  );

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    const el = e.currentTarget;
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      void execute(e.shiftKey && Boolean(sct));
      return;
    }
    if (e.key === "Escape") {
      el.blur();
      return;
    }

    const { selectionStart: start, selectionEnd: end } = el;
    const before = value.slice(0, start);
    const lineStart = before.lastIndexOf("\n") + 1;

    if (e.key === "Tab") {
      e.preventDefault();
      if (e.shiftKey) {
        // Dedent the current line.
        const line = value.slice(lineStart);
        const cut = line.startsWith(INDENT) ? INDENT.length : line.match(/^ */)?.[0].length ?? 0;
        if (!cut) return;
        const next = value.slice(0, lineStart) + value.slice(lineStart + cut);
        setValue(next);
        requestAnimationFrame(() => el.setSelectionRange(Math.max(lineStart, start - cut), Math.max(lineStart, end - cut)));
      } else {
        const next = value.slice(0, start) + INDENT + value.slice(end);
        setValue(next);
        requestAnimationFrame(() => el.setSelectionRange(start + INDENT.length, start + INDENT.length));
      }
      return;
    }

    if (e.key === "Enter" && !e.shiftKey && start === end) {
      // Keep the indentation, and add a level after a line ending in ":".
      e.preventDefault();
      const line = value.slice(lineStart, start);
      let indent = line.match(/^\s*/)?.[0] ?? "";
      if (/:\s*(#.*)?$/.test(line)) indent += INDENT;
      const insert = "\n" + indent;
      const next = value.slice(0, start) + insert + value.slice(end);
      setValue(next);
      requestAnimationFrame(() => el.setSelectionRange(start + insert.length, start + insert.length));
    }
  }

  const rows = Math.min(28, Math.max(6, value.split("\n").length + 1));
  const minHeight = typeof height === "number" ? Math.min(height, 520) : undefined;
  const grade = result?.grade;

  return (
    <div
      className="ex"
      ref={root}
      data-full={full ? "true" : undefined}
      data-state={grade ? (grade.passed ? "passed" : "failed") : undefined}
      role={full ? "dialog" : undefined}
      aria-modal={full ? true : undefined}
      aria-label={full ? "Exercise" : undefined}
    >
      <div className="pch-viz__bar ex__bar">
        <span className="pch-viz__tag">exercise</span>
        <span className="pch-viz__title">
          {grade?.passed ? "Exercise complete" : "Your turn"}
        </span>
        <button
          type="button"
          className="ex__icon"
          onClick={() => setFull((v) => !v)}
          aria-label={full ? "Exit fullscreen" : "Open in fullscreen"}
          title={full ? "Exit fullscreen (Esc)" : "Open in fullscreen"}
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
            <path
              fill="currentColor"
              d={
                full
                  ? "M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"
                  : "M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"
              }
            />
          </svg>
        </button>
      </div>

      <div className="ex__body">
        <div className="ex__pane">
          <label className="ex__label" htmlFor={`${id}-code`}>
            script.py
          </label>
          <textarea
            id={`${id}-code`}
            ref={editor}
            className="ex__editor"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={onKeyDown}
            rows={rows}
            style={minHeight ? { minHeight } : undefined}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            aria-describedby={`${id}-keys`}
          />
          <p className="sr-only" id={`${id}-keys`}>
            Tab indents. Press Escape, then Tab, to leave the editor. Control
            plus Enter runs the code; Control plus Shift plus Enter submits it.
          </p>
        </div>

        <div className="ex__pane ex__pane--out">
          <span className="ex__label">Output</span>
          <pre className="ex__output" aria-live="polite">
            {status ? (
              <span className="ex__status">{status}</span>
            ) : result ? (
              <>
                {result.stdout}
                {result.error ? <span className="ex__error">{result.error}</span> : null}
                {!result.stdout && !result.error ? (
                  <span className="ex__status">Ran without printing anything.</span>
                ) : null}
              </>
            ) : (
              <span className="ex__status">Press Run to see what your code prints.</span>
            )}
          </pre>
        </div>
      </div>

      {result?.notice ? <p className="ex__notice">{result.notice}</p> : null}

      {grade ? (
        <p className="ex__verdict" role={grade.passed ? "status" : "alert"}>
          <strong>{grade.passed ? "Correct." : "Not yet."}</strong> {grade.message}
        </p>
      ) : null}

      {showHint && hint ? <p className="ex__hint">{hint}</p> : null}

      {showSolution && solution ? (
        <div className="ex__solution">
          <span className="ex__label">Solution</span>
          <pre>{solution}</pre>
          <button type="button" className="ex__small" onClick={() => setValue(solution)}>
            Put it in the editor
          </button>
        </div>
      ) : null}

      {expectedOutput ? (
        <details className="ex__expected">
          <summary>Expected output</summary>
          <pre>{expectedOutput}</pre>
        </details>
      ) : null}

      <div className="ex__controls">
        <div className="ex__aux">
          {hint ? (
            <button type="button" className="ex__small" onClick={() => setShowHint((v) => !v)}>
              {showHint ? "Hide hint" : "Hint"}
            </button>
          ) : null}
          {solution && submitted ? (
            // Offered once they have tried: the point is to attempt it first.
            <button
              type="button"
              className="ex__small"
              onClick={() => setShowSolution((v) => !v)}
            >
              {showSolution ? "Hide solution" : "Show solution"}
            </button>
          ) : null}
          <button
            type="button"
            className="ex__small"
            onClick={() => {
              setValue(code);
              setResult(null);
            }}
            disabled={value === code}
          >
            Reset
          </button>
        </div>
        <div className="ex__main">
          <button
            type="button"
            className="button"
            onClick={() => void execute(false)}
            disabled={phase === "busy"}
          >
            Run
          </button>
          {sct ? (
            <button
              type="button"
              className="button button--primary"
              onClick={() => void execute(true)}
              disabled={phase === "busy"}
            >
              Submit
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default DataCampExercise;

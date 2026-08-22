/**
 * VizPlayer — the transport shell every DSA visualization mounts inside.
 *
 * Owns *all* animation state so that stage renderers stay pure:
 *   play / pause · step ±1 · scrub · speed · reset · frame counter
 *   keyboard (space, ← →, Home, End) · reduced-motion · code line highlight
 *   watch panel · per-frame caption · phase pill · result bar
 *
 * It is internal plumbing — MDX authors never write `<VizPlayer>` directly.
 * They write `<ArrayStepper algo="..." values={...} />` and that component
 * builds a `Frame[]` (see ./frames.ts) and hands it here.
 *
 * Chassis reuse: the outer card, header bar, tag pill and caption bar are the
 * site's existing `.pch-viz` "instrument panel" classes from src/styles/viz.css,
 * so a stepper sits next to a p5 sketch or a mermaid diagram without looking
 * like it came from a different site. Only the transport row and stage are new
 * (`.pch-vz__*`, defined in src/styles/dsa-viz.css).
 *
 * Plays through once on mount, then parks on the final frame with the scrub bar
 * live. Under `prefers-reduced-motion` it never autoplays — it renders frame 0
 * and waits for the reader.
 */
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type { Frame } from "./frames";

/**
 * Tag pill identity. Drives the pill colour + glyph via dsa-viz.css, and — for
 * the six mathematics tags at the end of the union — math-viz.css.
 *
 * The tag string is rendered in the pill, so it names what the reader is looking
 * at. That is why the maths labs do not borrow `grid` for a matrix or `chart`
 * for a density: the pill would read wrong.
 */
export type VizTag =
  | "array"
  | "tree"
  | "graph"
  | "dp"
  | "recursion"
  | "grid"
  | "list"
  | "search"
  | "stack"
  | "heap"
  | "interval"
  | "sort"
  | "trie"
  | "dsu"
  | "chart"
  | "bits"
  | "segtree"
  | "state"
  // ---- Mathematics for Machine Learning (src/components/viz/math/*) --------
  /** Matrices and their factorisations: MatrixLab, ElimStepper, EigenLab, SVDLab. */
  | "matrix"
  /** Vectors, spans, norms, projections: SpanExplorer, NormBall, ProjectionLab. */
  | "vector"
  /** Functions of several variables: SurfaceGrad, TaylorLab, AutodiffGraph. */
  | "field"
  /** Densities and inference: DistributionLab, BayesLab. */
  | "dist"
  /** Optimisation: DescentLab, ConstraintLab, ConvexLab. */
  | "opt"
  /** Fitted models: RegressionLab, PCALab, EMLab, MarginLab. */
  | "fit";

export interface VizPlayerProps<S> {
  /** The precomputed trace. Must be non-empty. */
  frames: Frame<S>[];
  /** Pure renderer for one frame's state. */
  renderStage: (frame: Frame<S>, index: number) => ReactNode;
  /** Header title — say what the reader is looking at, not the algorithm name. */
  title: string;
  /** Pill label, lowercase. */
  tag: VizTag;
  /** Right-aligned mono label, e.g. the algorithm or complexity. */
  lib?: string;
  /** Static explanation shown in the tip bar under the transport. */
  desc?: string;
  /** Source lines that `frame.line` indexes into (1-based). */
  code?: string[];
  /** Final answer, shown in the result bar once the trace completes. */
  result?: string;
  /** Milliseconds per frame at 1x. Default 900. */
  ms?: number;
  /** Play once on mount. Default true; always false under reduced motion. */
  autoPlay?: boolean;
}

const SPEEDS = [0.5, 1, 2, 4] as const;

export default function VizPlayer<S>({
  frames,
  renderStage,
  title,
  tag,
  lib,
  desc,
  code,
  result,
  ms = 900,
  autoPlay = true,
}: VizPlayerProps<S>) {
  const last = Math.max(0, frames.length - 1);
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<number>(1);
  const rootRef = useRef<HTMLDivElement>(null);

  // ── Reduced motion: decided after mount so SSR output stays deterministic ──
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  // Kick off the single autoplay pass once we know the motion preference.
  const kicked = useRef(false);
  useEffect(() => {
    if (kicked.current) return;
    kicked.current = true;
    if (autoPlay && !reduced && last > 0) setPlaying(true);
  }, [autoPlay, reduced, last]);

  // ── The clock ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!playing) return;
    if (idx >= last) {
      setPlaying(false);
      return;
    }
    const t = window.setTimeout(() => setIdx((i) => Math.min(i + 1, last)), ms / speed);
    return () => window.clearTimeout(t);
  }, [playing, idx, last, ms, speed]);

  // Pause when the tab is hidden — a background timer is wasted work.
  useEffect(() => {
    const onVis = () => {
      if (document.hidden) setPlaying(false);
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  const step = useCallback(
    (delta: number) => {
      setPlaying(false);
      setIdx((i) => Math.min(last, Math.max(0, i + delta)));
    },
    [last],
  );

  const toggle = useCallback(() => {
    // Pressing play on the final frame restarts — otherwise the button is a no-op.
    setPlaying((p) => {
      if (!p && idx >= last) setIdx(0);
      return !p;
    });
  }, [idx, last]);

  const reset = useCallback(() => {
    setPlaying(false);
    setIdx(0);
  }, []);

  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case " ":
        case "k":
          e.preventDefault();
          toggle();
          break;
        case "ArrowRight":
        case "l":
          e.preventDefault();
          step(1);
          break;
        case "ArrowLeft":
        case "j":
          e.preventDefault();
          step(-1);
          break;
        case "Home":
          e.preventDefault();
          reset();
          break;
        case "End":
          e.preventDefault();
          setPlaying(false);
          setIdx(last);
          break;
        default:
          break;
      }
    },
    [toggle, step, reset, last],
  );

  const frame = frames[Math.min(idx, last)];
  const stage = useMemo(() => renderStage(frame, idx), [renderStage, frame, idx]);

  if (frames.length === 0) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className={`pch-viz__tag pch-vz__tag--${tag}`}>{tag}</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          This visualization produced no frames — check the algorithm name and inputs.
        </p>
      </div>
    );
  }

  const atEnd = idx >= last;

  return (
    <div
      ref={rootRef}
      className={`pch-viz pch-vz${playing ? " is-playing" : ""}`}
      tabIndex={0}
      role="group"
      aria-label={`${title} — interactive step-through, ${frames.length} steps`}
      onKeyDown={onKeyDown}
    >
      <div className="pch-viz__bar">
        <span className={`pch-viz__tag pch-vz__tag--${tag}`}>{tag}</span>
        <span className="pch-viz__title">{title}</span>
        {lib ? <span className="pch-viz__lib">{lib}</span> : null}
      </div>

      <div className="pch-vz__stage">{stage}</div>

      {code && code.length > 0 ? (
        <pre className="pch-vz__code" aria-hidden="true">
          {code.map((ln, i) => (
            <span
              key={i}
              className={`pch-vz__codeline${frame.line === i + 1 ? " is-here" : ""}`}
            >
              <span className="pch-vz__gutter">{i + 1}</span>
              {ln || " "}
            </span>
          ))}
        </pre>
      ) : null}

      {frame.watch && frame.watch.length > 0 ? (
        <div className="pch-vz__watch">
          {frame.watch.map((w) => (
            <span key={w.label} className={`pch-vz__var tone-${w.tone ?? "info"}`}>
              <b>{w.label}</b>
              <span>{String(w.value)}</span>
            </span>
          ))}
        </div>
      ) : null}

      <div className="pch-vz__caption" aria-live="polite">
        {frame.phase ? <span className="pch-vz__phase">{frame.phase}</span> : null}
        <span>{frame.caption}</span>
      </div>

      {atEnd && result ? (
        <div className="pch-vz__result">
          <b>Result</b> {result}
        </div>
      ) : null}

      <div className="pch-vz__transport">
        <button
          type="button"
          className={`pch-viz__btn pch-vz__play${playing ? "" : " is-paused"}`}
          onClick={toggle}
          aria-label={playing ? "Pause" : atEnd ? "Replay" : "Play"}
        >
          {playing ? "Pause" : atEnd ? "Replay" : "Play"}
        </button>
        <button
          type="button"
          className="pch-viz__btn pch-vz__icon"
          onClick={() => step(-1)}
          disabled={idx === 0}
          aria-label="Previous step"
          title="Previous step (←)"
        >
          ‹
        </button>
        <button
          type="button"
          className="pch-viz__btn pch-vz__icon"
          onClick={() => step(1)}
          disabled={atEnd}
          aria-label="Next step"
          title="Next step (→)"
        >
          ›
        </button>

        <input
          className="pch-vz__scrub"
          type="range"
          min={0}
          max={last}
          value={idx}
          onChange={(e) => {
            setPlaying(false);
            setIdx(Number(e.target.value));
          }}
          aria-label="Scrub through steps"
        />

        <span className="pch-vz__count">
          {idx + 1}<i>/</i>{frames.length}
        </span>

        <label className="pch-vz__speed">
          <span className="sr-only">Playback speed</span>
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            aria-label="Playback speed"
          >
            {SPEEDS.map((s) => (
              <option key={s} value={s}>
                {s}×
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          className="pch-viz__btn pch-vz__icon"
          onClick={reset}
          aria-label="Back to start"
          title="Back to start (Home)"
        >
          ⟲
        </button>
      </div>

      {desc ? <p className="pch-viz__cap">{desc}</p> : null}
    </div>
  );
}

/**
 * frames.ts — the one contract every DSA visualization in this repo speaks.
 *
 * WHY THIS EXISTS
 * ---------------
 * The site's original algorithm visuals were p5.js sketches: 35 of them, each a
 * bespoke `draw()` loop on its own timer. That worked, but it meant (a) every
 * new visual cost a full sketch, and (b) the reader could not stop on the frame
 * they did not understand — the animation just kept going.
 *
 * The fix is to separate *what happens* from *how it is drawn*:
 *
 *     algorithm  ──▶  Frame[]  ──▶  VizPlayer (transport)  ──▶  stage renderer
 *      (pure)          (data)        (play/step/scrub)          (SVG/HTML)
 *
 * An algorithm is a plain function that walks its own logic and pushes one
 * `Frame` per meaningful step. It never touches the DOM, never sets a timer,
 * and is trivially testable. `VizPlayer` owns all transport. A stage renderer
 * is a pure function of one frame.
 *
 * The payoff: an author writing MDX declares *data plus an algorithm name* —
 *
 *     <ArrayStepper algo="variable-window-sum" values={[2,3,1,2,4,3]} target={7} />
 *
 * — and gets a scrubbable, captioned, keyboard-driven visual with zero draw code.
 */

/** Semantic colour roles. Stage renderers map these onto the site's tokens. */
export type Tone =
  /** Currently being read / operated on. */
  | "active"
  /** Part of the accepted answer, or a satisfied condition. */
  | "good"
  /** Rejected, violating a constraint, or being discarded. */
  | "bad"
  /** Already processed and no longer interesting. */
  | "muted"
  /** Borderline — condition just broke, about to shrink/backtrack. */
  | "warn"
  /** Neutral emphasis: in scope but not the focus. */
  | "info";

/** A named cursor into a sequence. Rendered as a labelled caret under a cell. */
export interface Pointer {
  /** Short label, e.g. `left`, `r`, `slow`. Keep it under 6 characters. */
  name: string;
  /** Zero-based index. `-1` parks the pointer off the left edge. */
  index: number;
  tone?: Tone;
}

/** An inclusive index range drawn as a bracket/shade over a sequence. */
export interface Band {
  from: number;
  /** Inclusive. `to < from` renders as an empty band. */
  to: number;
  label?: string;
  tone?: Tone;
}

/** One entry in the watch panel — the "what are the variables right now" strip. */
export interface Watch {
  label: string;
  value: string | number;
  tone?: Tone;
}

/**
 * One step of an algorithm, fully self-describing.
 *
 * `state` is the only component-specific part; everything else is shared
 * chrome that `VizPlayer` renders identically for all 18 visualizations.
 */
export interface Frame<S = unknown> {
  /** Component-specific snapshot. Must be immutable — never mutate and re-push. */
  state: S;
  /**
   * One sentence, present tense, explaining *this* step. This is the single
   * most important field: it is what turns an animation into a lesson.
   */
  caption: string;
  /** 1-based line number in the accompanying `code` to highlight. */
  line?: number;
  /** Variables worth watching at this step. */
  watch?: Watch[];
  /** Set on the last frame to render the "done" badge and stop autoplay. */
  done?: boolean;
  /**
   * Optional phase label, e.g. `expand` / `shrink` / `backtrack`. Shown as a
   * pill so the reader can see which half of a two-phase loop they are in.
   */
  phase?: string;
}

/** What every algorithm generator returns. */
export interface Trace<S> {
  frames: Frame<S>[];
  /** Source lines the `line` field indexes into. 1-based when highlighted. */
  code?: string[];
  /** Final answer, rendered in the result bar. */
  result?: string;
}

/**
 * Helper for building traces without repeating boilerplate.
 *
 * Usage inside an algorithm:
 *
 *     const t = tracer<ArrayState>(CODE);
 *     t.push({ values, pointers: [...] }, "Expand right to index 3.", { line: 5 });
 *     return t.done("best = 9");
 */
export function tracer<S>(code?: string[]) {
  const frames: Frame<S>[] = [];
  return {
    frames,
    push(
      state: S,
      caption: string,
      extra: Omit<Frame<S>, "state" | "caption"> = {},
    ) {
      frames.push({ state, caption, ...extra });
      return frames.length - 1;
    },
    /** Marks the final frame as done and returns the finished trace. */
    done(result?: string): Trace<S> {
      if (frames.length > 0) frames[frames.length - 1].done = true;
      return { frames, code, result };
    },
  };
}

/**
 * Guard against runaway generators. A visualization with 4000 frames is not a
 * teaching tool, it is a hang — better to truncate loudly than to ship it.
 */
export const MAX_FRAMES = 600;

export function capFrames<S>(trace: Trace<S>): Trace<S> {
  if (trace.frames.length <= MAX_FRAMES) return trace;
  const kept = trace.frames.slice(0, MAX_FRAMES);
  const last = kept[kept.length - 1];
  kept[kept.length - 1] = {
    ...last,
    caption: `${last.caption} (trace truncated at ${MAX_FRAMES} steps — shrink the input to see the whole run)`,
    done: true,
  };
  return { ...trace, frames: kept };
}

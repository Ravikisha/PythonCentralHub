/**
 * algos/complexity.ts — growth-rate comparisons for <ComplexityChart>.
 *
 * Big-O is taught as notation and then used as intuition, and the gap between
 * the two is where students get hurt: everyone can recite that O(n²) is worse
 * than O(n log n), and almost nobody has a feel for *how much* worse at n = 10⁵,
 * or for the fact that O(2ⁿ) is unusable past about n = 25.
 *
 * These traces step through increasing n and report actual operation counts, so
 * the answer to "will this pass?" becomes arithmetic rather than vibes.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

export interface Curve {
  label: string;
  /** Operation counts, one per n in `ns`. */
  points: number[];
  tone: Tone;
}

export interface ComplexityState {
  /** The n values on the x axis. */
  ns: number[];
  curves: Curve[];
  /** Index into `ns` currently highlighted. */
  cursor?: number;
  /** Rows of the comparison table, built up as the trace advances. */
  table?: { n: number; cells: { label: string; value: string; tone: Tone }[] }[];
  /** Log scale is the default — linear makes everything but the worst curve flat. */
  logScale?: boolean;
}

export interface ComplexityInput {
  /** Which growth rates to compare. Defaults to the interview-relevant set. */
  curves?: string[];
  /** n values to evaluate at. */
  ns?: number[];
}

export type ComplexityAlgo = (input: ComplexityInput) => Trace<ComplexityState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

/** Formulae keyed by the name an author writes in `curves`. */
const FORMULAE: Record<string, { fn: (n: number) => number; tone: Tone }> = {
  "O(1)": { fn: () => 1, tone: "good" },
  "O(log n)": { fn: (n) => Math.log2(n), tone: "good" },
  "O(n)": { fn: (n) => n, tone: "active" },
  "O(n log n)": { fn: (n) => n * Math.log2(n), tone: "warn" },
  "O(n²)": { fn: (n) => n * n, tone: "bad" },
  "O(2^n)": { fn: (n) => 2 ** n, tone: "bad" },
  "O(n!)": { fn: (n) => { let f = 1; for (let i = 2; i <= n; i++) f *= i; return f; }, tone: "bad" },
};

/** Human-readable magnitude — "3.2 × 10⁹" beats 3200000000. */
function human(v: number): string {
  if (!Number.isFinite(v)) return "overflow";
  if (v < 1000) return v < 10 ? v.toFixed(1) : String(Math.round(v));
  const exp = Math.floor(Math.log10(v));
  const mant = v / 10 ** exp;
  return `${mant.toFixed(1)}e${exp}`;
}

/**
 * A rough but useful yardstick: interview judges accept roughly 10^8 simple
 * operations per second. Stating a concrete budget is what turns Big-O from
 * notation into a decision procedure.
 */
const BUDGET = 1e8;

const growth: ComplexityAlgo = (input) => {
  const names = (input.curves ?? ["O(log n)", "O(n)", "O(n log n)", "O(n²)", "O(2^n)"]).filter(
    (c) => c in FORMULAE,
  );
  const ns = input.ns ?? [10, 20, 50, 100, 1000, 10000, 100000];
  const t = tracer<ComplexityState>();

  const curves: Curve[] = names.map((name) => ({
    label: name,
    tone: FORMULAE[name].tone,
    points: ns.map((n) => FORMULAE[name].fn(n)),
  }));

  const table: NonNullable<ComplexityState["table"]>[number][] = [];

  const state = (cursor?: number): ComplexityState => ({
    ns,
    curves,
    cursor,
    table: [...table],
    logScale: true,
  });

  t.push(
    state(),
    `Five growth rates on a logarithmic vertical axis — linear would flatten everything except the worst curve into a single line at the bottom. The yardstick to hold onto: an online judge accepts roughly 10^8 simple operations, so any curve crossing that line is a time-limit exceeded.`,
    { phase: "setup", watch: [w("budget", "1e8 ops", "warn")] },
  );

  for (let i = 0; i < ns.length; i++) {
    const n = ns[i];
    const cells = curves.map((c) => {
      const v = c.points[i];
      return {
        label: c.label,
        value: human(v),
        tone: (v > BUDGET ? "bad" : v > BUDGET / 100 ? "warn" : "good") as Tone,
      };
    });
    table.push({ n, cells });

    const overBudget = cells.filter((c) => c.tone === "bad").map((c) => c.label);

    t.push(
      state(i),
      overBudget.length === 0
        ? `At n = ${n.toLocaleString()} every one of these is comfortable. Constraints this small are a hint that an exponential or quadratic solution is *intended* — if a problem says n ≤ 20, it is asking for a bitmask or a backtracking search.`
        : `At n = ${n.toLocaleString()}, ${overBudget.join(" and ")} ${overBudget.length === 1 ? "exceeds" : "exceed"} the 10^8 budget. ${
            overBudget.includes("O(2^n)")
              ? "Exponential dies first, and it dies early — somewhere around n = 25 it becomes unusable no matter how fast the machine is."
              : ""
          }`,
      {
        phase: `n = ${n}`,
        watch: [
          w("n", n.toLocaleString(), "active"),
          ...cells.map((c) => w(c.label, c.value, c.tone)),
        ],
      },
    );
  }

  t.push(
    state(),
    `Read the constraint, not your instincts. n ≤ 20 means exponential is fine. n ≤ 5,000 means O(n²) is fine. n ≤ 10^5 means you need O(n log n) — and this is by far the most common constraint in interviews, which is why sorting, sliding windows and heaps dominate the pattern list. n ≤ 10^9 means the answer cannot involve visiting every element at all, so think binary search on the answer, or maths.`,
    { phase: "answer" },
  );

  return capFrames(t.done("growth compared against a 10^8 operation budget"));
};

/**
 * Registry. The `algo` prop of <ComplexityChart> indexes this.
 *
 * | key      | uses          |
 * |----------|---------------|
 * | growth   | curves, ns    |
 *
 * Valid `curves` entries: O(1), O(log n), O(n), O(n log n), O(n²), O(2^n), O(n!).
 */
export const COMPLEXITY_ALGOS: Record<string, ComplexityAlgo> = { growth };

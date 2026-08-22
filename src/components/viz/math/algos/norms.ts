/**
 * algos/norms.ts — one vector, many rulers.
 *
 * §3.1 defines a norm by three properties and then gives two examples, and a
 * reader can finish the section believing the choice between them is cosmetic.
 * It is not: the *shape of the unit ball* is what a regulariser actually
 * optimises against, and that shape is what separates Lasso from Ridge.
 *
 * So the trace sweeps p and, at each value, draws three things that have to
 * agree: the set of vectors of length one, the probe vector, and the probe
 * rescaled to length one — which must land on the ball. If the rescaling ever
 * missed, the norm formula and the ball formula would have disagreed, and the
 * reader would see it immediately.
 *
 * The sweep deliberately runs past both ends of the useful range. Below p = 1
 * the "ball" caves inwards and the triangle inequality fails, so the object
 * stops being a norm — and the trace measures the violation rather than
 * asserting it. Above p = 2 the ball inflates towards the square of the maximum
 * norm, which the last frame reaches exactly.
 */
import { tracer, capFrames, type Trace } from "../../frames";

/** `Infinity` survives the JSON round-trip badly, so the max norm is a string. */
export type PValue = number | "inf";

export interface NormsInput {
  /**
   * The p values to visit, in order. Values below 1 are allowed and are
   * reported as *not* norms.
   */
  ps?: PValue[];
  /** The probe vector, in R^2. */
  probe?: [number, number];
}

export interface NormsState {
  /** Current exponent. `null` means the max norm. */
  p: number | null;
  pLabel: string;
  /** The unit ball, as a closed polygon of data-space points. */
  ball: [number, number][];
  probe: [number, number];
  /** ‖probe‖_p. */
  probeNorm: number;
  /** probe / ‖probe‖_p — must lie on `ball`. */
  onBall: [number, number];
  /**
   * The triangle-inequality check: ‖u + v‖_p against ‖u‖_p + ‖v‖_p for the two
   * axis vectors. Above one these are equal; below one the left side wins,
   * which is the failure.
   */
  triangle: { lhs: number; rhs: number; holds: boolean };
  /** Previous balls, drawn faintly so the sweep leaves a trail. */
  trail: { pLabel: string; ball: [number, number][] }[];
  /** Where the ball touches the axes and where it bulges — the sparsity cue. */
  corners: [number, number][];
}

const CODE = [
  "def norm(x, p):",
  "    if p == inf: return max(abs(x))",
  "    return sum(abs(xi)**p for xi in x) ** (1/p)",
  "",
  "# the unit ball: every x with norm(x, p) == 1",
  "r = lambda th: (abs(cos th)**p + abs(sin th)**p) ** (-1/p)",
  "ball = [(r(th)*cos th, r(th)*sin th) for th in angles]",
  "",
  "# a norm must satisfy norm(u + v) <= norm(u) + norm(v)",
];

const SAMPLES = 240;

/** ‖x‖_p, with `null` meaning the max norm. */
function pnorm(x: number[], p: number | null): number {
  if (p === null) return Math.max(...x.map(Math.abs));
  return Math.abs(x.reduce((s, v) => s + Math.abs(v) ** p, 0)) ** (1 / p);
}

/** The unit ball of ℓ_p in the plane, sampled by angle. */
function unitBall(p: number | null): [number, number][] {
  const out: [number, number][] = [];
  for (let i = 0; i < SAMPLES; i++) {
    const th = (2 * Math.PI * i) / SAMPLES;
    const c = Math.cos(th);
    const s = Math.sin(th);
    // Solve ‖r·(c, s)‖_p = 1 for r. The norm is homogeneous, so r = 1/‖(c, s)‖_p.
    const r = 1 / pnorm([c, s], p);
    out.push([r * c, r * s]);
  }
  return out;
}

const fmt = (v: number, d = 3) => String(Number(v.toFixed(d)));

const DEFAULT_PS: PValue[] = [0.6, 1, 1.5, 2, 3, 6, "inf"];

/** Prose for the p values the sweep is likely to visit. */
function remark(p: number | null): string {
  if (p === null)
    return "This is the maximum norm, ℓ∞ — the ball is the full square, because a vector is short only if *every* coordinate is short. It is the norm behind adversarial perturbation budgets: change every pixel a little, none of them much.";
  if (p < 1)
    return "The ball has caved inwards, and that is fatal. A norm must satisfy the triangle inequality, and this shape does not — the watch panel below shows a pair of vectors whose sum is measured as longer than the two of them added. Values of p below one give a quasinorm, not a norm.";
  if (p === 1)
    return "ℓ1, the Manhattan norm: the ball is a diamond whose only sharp points sit exactly on the axes. That is the whole of Lasso. A corner is a place where one coordinate is exactly zero, and optimisation pushed against a corner returns exact zeros rather than small values.";
  if (p === 2)
    return "ℓ2, the Euclidean norm — the book's default, and the only p whose ball is a circle. A circle has no corners and no preferred direction, so Ridge shrinks every coefficient a bit and sets none of them to zero.";
  if (p < 2)
    return "Between the diamond and the circle. The corners are already rounding off, and with them goes the exact-zero behaviour: an optimum on a smooth boundary has no reason to land on an axis.";
  return "Past the circle the ball bulges towards the corners of the square. High p tolerates one large coordinate as long as the rest are small — the opposite of what ℓ1 rewards.";
}

export function norms({ ps = DEFAULT_PS, probe = [1.6, 0.9] }: NormsInput = {}): Trace<NormsState> {
  const t = tracer<NormsState>(CODE);
  const trail: { pLabel: string; ball: [number, number][] }[] = [];

  ps.forEach((raw, i) => {
    const p = raw === "inf" ? null : raw;
    const pLabel = raw === "inf" ? "∞" : String(raw);
    const ball = unitBall(p);
    const probeNorm = pnorm(probe, p);
    const onBall: [number, number] = [probe[0] / probeNorm, probe[1] / probeNorm];

    // The cheapest triangle-inequality witness there is: the two axis vectors.
    // ‖e1 + e2‖_p is 2^(1/p) and each part has norm 1, so the test is whether
    // 2^(1/p) exceeds 2 — true exactly when p < 1.
    const lhs = pnorm([1, 1], p);
    const rhs = pnorm([1, 0], p) + pnorm([0, 1], p);
    const holds = lhs <= rhs + 1e-12;

    // Where the ball meets the axes, and its point in the 45° direction. The gap
    // between the two is what makes ℓ1 sparse and ℓ∞ not.
    const corners: [number, number][] = [
      [1, 0],
      [0, 1],
      [-1, 0],
      [0, -1],
    ].map((c) => [c[0] as number, c[1] as number]);

    t.push(
      {
        p,
        pLabel,
        ball,
        probe,
        probeNorm,
        onBall,
        triangle: { lhs, rhs, holds },
        trail: trail.map((tr) => ({ pLabel: tr.pLabel, ball: tr.ball })),
        corners,
      },
      `p = ${pLabel}. The probe (${probe[0]}, ${probe[1]}) measures ${fmt(probeNorm)} long, so dividing by that lands it on the ball — the white dot on the boundary. ${remark(p)}`,
      {
        line: holds ? 7 : 9,
        phase: holds ? (p === null || p >= 1 ? "norm" : "not a norm") : "not a norm",
        watch: [
          { label: "p", value: pLabel },
          { label: "‖x‖_p", value: fmt(probeNorm) },
          {
            label: "‖e1+e2‖ vs ‖e1‖+‖e2‖",
            value: `${fmt(lhs)} vs ${fmt(rhs)}`,
            tone: holds ? "good" : "bad",
          },
          { label: "triangle inequality", value: holds ? "holds" : "FAILS", tone: holds ? "good" : "bad" },
        ],
        done: i === ps.length - 1,
      },
    );

    trail.push({ pLabel, ball });
  });

  const usable = ps.filter((p) => p === "inf" || (p as number) >= 1).length;
  return capFrames(
    t.done(`${usable} of the ${ps.length} exponents give an actual norm`),
  );
}

export const NORM_ALGOS = {
  norms,
} as const;

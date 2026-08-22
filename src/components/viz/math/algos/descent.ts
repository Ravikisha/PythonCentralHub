/**
 * algos/descent.ts — gradient descent and its three common variants, one update
 * per frame.
 *
 * §7.1 is the chapter the module was missing entirely, and it is the one place
 * where a step-through beats an animation by the largest margin. The interesting
 * events in an optimiser are discrete and they are *specific*: the step where
 * the learning rate overshoots and the loss goes up; the step where momentum
 * finally carries the iterate along the ravine instead of across it; the single
 * Newton step that lands on the optimum of a quadratic. Each of those is one
 * frame with a caption.
 *
 * Determinism: SGD needs noise, and the README forbids `Math.random()` because a
 * trace must be identical before and after hydration. The noise here comes from
 * an integer-seeded LCG indexed by step number, so run *n* is always run *n*.
 *
 * The contour grid is computed once and the **same frozen reference** is shared
 * by every frame. Copying a 64×64 grid into 200 frames would be 800k numbers for
 * no benefit; frames must not be mutated, and this one never is.
 */
import { tracer, capFrames, type Trace } from "../../frames";

export type SurfaceName = "quadratic" | "ill-conditioned" | "rosenbrock" | "saddle";
export type MethodName = "gd" | "momentum" | "sgd" | "newton";

interface Surface {
  name: SurfaceName;
  /** Human description used in the opening caption. */
  blurb: string;
  f: (x: number, y: number) => number;
  grad: (x: number, y: number) => [number, number];
  /** Hessian, row-major. Constant for the quadratics; exact for Rosenbrock. */
  hess: (x: number, y: number) => [[number, number], [number, number]];
  /** Plot window and a sensible starting point. */
  window: [number, number, number, number];
  start: [number, number];
  /** The optimum, when there is one worth marking. */
  optimum: [number, number] | null;
  /** Contour levels; geometric spacing suits these surfaces better than linear. */
  levels: number[];
  /** A learning rate that behaves, used when the caller does not pass one. */
  defaultLr: number;
}

const SURFACES: Record<SurfaceName, Surface> = {
  quadratic: {
    name: "quadratic",
    blurb:
      "a well-conditioned bowl, f(x, y) = x² + y². The Hessian is 2I, so every direction curves the same amount and the gradient points straight at the minimum",
    f: (x, y) => x * x + y * y,
    grad: (x, y) => [2 * x, 2 * y],
    hess: () => [
      [2, 0],
      [0, 2],
    ],
    window: [-3, 3, -3, 3],
    start: [2.4, 1.8],
    optimum: [0, 0],
    levels: [0.25, 1, 2.25, 4, 6.25, 9, 12.25],
    defaultLr: 0.25,
  },
  "ill-conditioned": {
    name: "ill-conditioned",
    blurb:
      "a ravine, f(x, y) = 0.05x² + 5y². The Hessian is diag(0.1, 10), so κ = 100: the surface curves a hundred times more steeply across the valley than along it",
    f: (x, y) => 0.05 * x * x + 5 * y * y,
    grad: (x, y) => [0.1 * x, 10 * y],
    hess: () => [
      [0.1, 0],
      [0, 10],
    ],
    window: [-10, 10, -2.2, 2.2],
    start: [-8.5, 1.6],
    optimum: [0, 0],
    levels: [0.5, 2, 5, 10, 20, 35],
    defaultLr: 0.16,
  },
  rosenbrock: {
    name: "rosenbrock",
    blurb:
      "the Rosenbrock banana, f(x, y) = (1 − x)² + 100(y − x²)². Non-convex, with a curved valley — the gradient almost never points at the optimum",
    f: (x, y) => (1 - x) ** 2 + 100 * (y - x * x) ** 2,
    grad: (x, y) => [-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)],
    hess: (x, y) => [
      [2 - 400 * (y - 3 * x * x), -400 * x],
      [-400 * x, 200],
    ],
    window: [-1.8, 1.8, -0.6, 2.6],
    start: [-1.4, 1.6],
    optimum: [1, 1],
    levels: [0.5, 2, 8, 30, 120, 400],
    defaultLr: 0.0018,
  },
  saddle: {
    name: "saddle",
    blurb:
      "a saddle, f(x, y) = x² − y². The gradient vanishes at the origin but it is not a minimum: the Hessian has one positive and one negative eigenvalue",
    f: (x, y) => x * x - y * y,
    grad: (x, y) => [2 * x, -2 * y],
    hess: () => [
      [2, 0],
      [0, -2],
    ],
    window: [-3, 3, -3, 3],
    start: [2.2, 0.08],
    optimum: null,
    levels: [-6, -3, -1, 0, 1, 3, 6],
    defaultLr: 0.16,
  },
};

/** Deterministic unit-normal-ish noise, indexed by step. */
function jitter(step: number, k: number): number {
  let s = (step * 2654435761 + k * 40503 + 12345) & 0x7fffffff;
  s = (s * 1103515245 + 12345) & 0x7fffffff;
  // Two uniforms folded to something roughly bell-shaped; the shape does not
  // matter here, only that it is repeatable and centred.
  const u1 = ((s >>> 8) & 0xffff) / 0xffff;
  s = (s * 1103515245 + 12345) & 0x7fffffff;
  const u2 = ((s >>> 8) & 0xffff) / 0xffff;
  return u1 + u2 - 1;
}

export interface SurfaceGrid {
  xs: number[];
  ys: number[];
  /** `z[j][i]` is f(xs[i], ys[j]). Row-major over y, matching SVG row order. */
  z: number[][];
  levels: number[];
  window: [number, number, number, number];
  optimum: [number, number] | null;
}

export interface DescentState {
  /** Shared, frozen, identical reference in every frame. */
  grid: SurfaceGrid;
  surface: SurfaceName;
  method: MethodName;
  /** Every iterate so far, including the current one. */
  path: [number, number][];
  /** The current iterate. */
  at: [number, number];
  /** Gradient at the current iterate, before the step that produced it. */
  grad: [number, number];
  /** The update vector actually applied to reach `at`. */
  step: [number, number] | null;
  /** Momentum buffer, for the momentum method. */
  velocity: [number, number] | null;
  loss: number;
  /** True on a frame where the loss went up. */
  uphill: boolean;
}

const CODE = {
  gd: [
    "theta = theta_0",
    "for t in range(steps):",
    "    g = grad_f(theta)",
    "    theta = theta - lr * g          # downhill, scaled by lr",
  ],
  momentum: [
    "theta, v = theta_0, 0",
    "for t in range(steps):",
    "    g = grad_f(theta)",
    "    v = beta * v - lr * g           # a running average of past steps",
    "    theta = theta + v",
  ],
  sgd: [
    "theta = theta_0",
    "for t in range(steps):",
    "    g = grad_f(theta) + noise       # one minibatch, not the full sum",
    "    theta = theta - lr * g",
  ],
  newton: [
    "theta = theta_0",
    "for t in range(steps):",
    "    g, H = grad_f(theta), hess_f(theta)",
    "    theta = theta - solve(H, g)     # curvature sets the step, not lr",
  ],
} as const satisfies Record<MethodName, readonly string[]>;

export interface DescentInput {
  surface?: SurfaceName;
  method?: MethodName;
  /** Step size. Defaults to a value chosen per surface. Ignored by `newton`. */
  lr?: number;
  /** Momentum coefficient. Only used by `method: "momentum"`. */
  beta?: number;
  /** Gradient noise scale. Only used by `method: "sgd"`. */
  noise?: number;
  steps?: number;
  start?: [number, number];
}

const fmt = (v: number, d = 3) => {
  if (!Number.isFinite(v)) return "diverged";
  const a = Math.abs(v);
  if (a !== 0 && (a < 1e-3 || a >= 1e5)) return v.toExponential(1);
  return v.toFixed(d).replace(/\.?0+$/, "") || "0";
};

/** Solve a 2×2 system, or return null when the matrix is effectively singular. */
function solve2(
  H: [[number, number], [number, number]],
  g: [number, number],
): [number, number] | null {
  const det = H[0][0] * H[1][1] - H[0][1] * H[1][0];
  if (Math.abs(det) < 1e-12) return null;
  return [
    (H[1][1] * g[0] - H[0][1] * g[1]) / det,
    (H[0][0] * g[1] - H[1][0] * g[0]) / det,
  ];
}

function buildGrid(s: Surface, n = 61): SurfaceGrid {
  const [x0, x1, y0, y1] = s.window;
  const xs = Array.from({ length: n }, (_, i) => x0 + ((x1 - x0) * i) / (n - 1));
  const ys = Array.from({ length: n }, (_, j) => y0 + ((y1 - y0) * j) / (n - 1));
  const z = ys.map((y) => xs.map((x) => s.f(x, y)));
  return Object.freeze({
    xs,
    ys,
    z,
    levels: s.levels,
    window: s.window,
    optimum: s.optimum,
  }) as SurfaceGrid;
}

export function descend({
  surface = "quadratic",
  method = "gd",
  lr,
  beta = 0.85,
  noise = 0.9,
  steps = 24,
  start,
}: DescentInput = {}): Trace<DescentState> {
  const s = SURFACES[surface];
  const rate = lr ?? s.defaultLr;
  const grid = buildGrid(s);

  const t = tracer<DescentState>([...CODE[method]]);

  let at: [number, number] = [...(start ?? s.start)] as [number, number];
  let velocity: [number, number] = [0, 0];
  const path: [number, number][] = [[...at] as [number, number]];
  let loss = s.f(at[0], at[1]);

  const snap = (
    caption: string,
    extra: {
      grad: [number, number];
      step: [number, number] | null;
      uphill?: boolean;
      line?: number;
      phase?: string;
      watch?: { label: string; value: string | number; tone?: "good" | "bad" | "warn" | "info" }[];
    },
  ) => {
    t.push(
      {
        grid,
        surface,
        method,
        path: path.map((p) => [...p] as [number, number]),
        at: [...at] as [number, number],
        grad: extra.grad,
        step: extra.step,
        velocity: method === "momentum" ? ([...velocity] as [number, number]) : null,
        loss,
        uphill: extra.uphill ?? false,
      },
      caption,
      { line: extra.line, phase: extra.phase, watch: extra.watch },
    );
  };

  const g0 = s.grad(at[0], at[1]);
  snap(
    `Starting at (${fmt(at[0], 2)}, ${fmt(at[1], 2)}) on ${s.blurb}. The loss is ${fmt(loss)} and the gradient is (${fmt(g0[0], 2)}, ${fmt(g0[1], 2)}) — the direction of steepest ASCENT, so every method below goes the other way.`,
    {
      grad: g0,
      step: null,
      line: 1,
      phase: "start",
      watch: [
        { label: "loss", value: fmt(loss) },
        { label: "|grad|", value: fmt(Math.hypot(g0[0], g0[1]), 2) },
        ...(method === "newton" ? [] : [{ label: "lr", value: fmt(rate, 4) }]),
      ],
    },
  );

  let diverged = false;
  let plateaued = false;

  for (let k = 0; k < steps; k++) {
    const g = s.grad(at[0], at[1]);
    const gNorm = Math.hypot(g[0], g[1]);

    if (gNorm < 1e-6) {
      plateaued = true;
      snap(
        s.optimum
          ? `The gradient is effectively zero, so no method can move further: this is a stationary point, and on this surface it is the minimum.`
          : `The gradient is effectively zero — but look at the Hessian: one eigenvalue is positive and one negative. A vanishing gradient marks a stationary point, not a minimum. This is the saddle every training run is warned about.`,
        {
          grad: g,
          step: null,
          phase: "converged",
          watch: [
            { label: "loss", value: fmt(loss), tone: "good" },
            { label: "|grad|", value: fmt(gNorm, 6), tone: "good" },
          ],
        },
      );
      break;
    }

    let step: [number, number] | null = null;
    let caption = "";
    let line = 4;

    if (method === "gd") {
      step = [-rate * g[0], -rate * g[1]];
      line = 4;
    } else if (method === "momentum") {
      velocity = [beta * velocity[0] - rate * g[0], beta * velocity[1] - rate * g[1]];
      step = [...velocity] as [number, number];
      line = 5;
    } else if (method === "sgd") {
      const gn: [number, number] = [g[0] + noise * jitter(k, 1), g[1] + noise * jitter(k, 2)];
      step = [-rate * gn[0], -rate * gn[1]];
      line = 4;
    } else {
      const H = s.hess(at[0], at[1]);
      const nStep = solve2(H, g);
      if (!nStep) {
        snap(
          `The Hessian is singular here, so the Newton step is undefined — there is no unique quadratic model to jump to. This is exactly why practical second-order methods add a damping term.`,
          { grad: g, step: null, phase: "blocked", watch: [{ label: "det H", value: "0", tone: "bad" }] },
        );
        break;
      }
      step = [-nStep[0], -nStep[1]];
      line = 4;
    }

    const before = loss;
    at = [at[0] + step[0], at[1] + step[1]];
    path.push([...at] as [number, number]);
    loss = s.f(at[0], at[1]);

    if (!Number.isFinite(loss) || Math.abs(at[0]) > 1e6 || Math.abs(at[1]) > 1e6) {
      diverged = true;
      snap(
        `The iterate has left the surface: the loss is ${fmt(loss)}. The step size is larger than the curvature tolerates, so each update overshoots further than the last and the process runs away. This is divergence, not slow convergence.`,
        {
          grad: g,
          step,
          uphill: true,
          line,
          phase: "diverged",
          watch: [{ label: "loss", value: fmt(loss), tone: "bad" }],
        },
      );
      break;
    }

    const uphill = loss > before + 1e-12;

    if (method === "gd") {
      caption = uphill
        ? `Step ${k + 1}: the gradient direction was right but the step of ${fmt(rate, 4)} carried the iterate past the valley floor and up the far side — the loss rose from ${fmt(before)} to ${fmt(loss)}. Descent directions do not guarantee descent; only small enough steps along them do.`
        : `Step ${k + 1}: subtract ${fmt(rate, 4)} times the gradient. The loss falls from ${fmt(before)} to ${fmt(loss)}.`;
    } else if (method === "momentum") {
      const vN = Math.hypot(velocity[0], velocity[1]);
      caption = `Step ${k + 1}: the velocity buffer keeps ${fmt(beta, 2)} of its previous value and adds this gradient, giving a step of length ${fmt(vN, 3)} — ${vN > rate * gNorm ? "longer" : "shorter"} than plain descent would take. Along a consistent direction the buffer accumulates; across the valley the alternating signs cancel.`;
    } else if (method === "sgd") {
      caption = `Step ${k + 1}: the gradient this step is a noisy estimate, not the true one, so the path wobbles. Each individual step is worse than a full-batch step — but it cost a fraction as much to compute, which is the entire trade.`;
    } else {
      caption =
        surface === "quadratic" || surface === "ill-conditioned"
          ? `Step ${k + 1}: Newton solves H·Δ = g and steps by Δ. On a quadratic the Hessian is exact, so this single step lands on the minimum regardless of conditioning — no learning rate involved.`
          : `Step ${k + 1}: Newton fits a quadratic to the local curvature and jumps to *its* minimum. The loss goes from ${fmt(before)} to ${fmt(loss)}. Far from the optimum the quadratic model is poor, which is why the jumps look erratic at first.`;
    }

    snap(caption, {
      grad: g,
      step,
      uphill,
      line,
      phase: method === "sgd" ? "noisy" : uphill ? "overshoot" : "descend",
      watch: [
        { label: "loss", value: fmt(loss), tone: uphill ? "bad" : "good" },
        { label: "|grad|", value: fmt(gNorm, 2) },
        { label: "|step|", value: fmt(Math.hypot(step[0], step[1]), 3) },
        ...(method === "momentum"
          ? [{ label: "|v|", value: fmt(Math.hypot(velocity[0], velocity[1]), 3), tone: "info" as const }]
          : []),
      ],
    });
  }

  const result = diverged
    ? `diverged — lr ${fmt(rate, 4)} exceeds what this curvature allows`
    : plateaued
      ? s.optimum
        ? `reached the minimum, loss ${fmt(loss)}`
        : `stalled at a saddle, loss ${fmt(loss)}`
      : `loss ${fmt(loss)} after ${path.length - 1} step${path.length === 2 ? "" : "s"}`;

  return capFrames(t.done(result));
}

export const DESCENT_ALGOS = {
  descend,
} as const;

/** Exported so a page can name the surfaces without hard-coding the list. */
export const SURFACE_NAMES = Object.keys(SURFACES) as SurfaceName[];

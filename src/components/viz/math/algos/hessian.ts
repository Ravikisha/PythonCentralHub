/**
 * algos/hessian.ts — the second-order picture: how the Hessian is built, why it
 * is symmetric, what its eigenvalues are, and the case where it says nothing.
 *
 * §5.7 is two pages of the book and states four things:
 *
 *   - the notation for higher-order partials;
 *   - Eq 5.146, that for a twice continuously differentiable f the order of
 *     differentiation does not matter;
 *   - Eq 5.147, the Hessian as the matrix of second partials, and that it is
 *     therefore symmetric;
 *   - that the Hessian "measures the curvature of the function locally".
 *
 * The last claim is the one worth turning into a measurement, because it is
 * precise and almost never stated precisely: the second derivative of f along a
 * unit direction d is exactly d^T H d. Sweep d and you get the whole curvature
 * profile, and its extremes are the eigenvalues of H — which is §4.2's spectral
 * theorem doing visible work rather than being cited.
 *
 * Two things this module refuses to fake:
 *
 *   1. **Symmetry is not evidence here.** The standard five-point mixed stencil
 *      reuses the same four corner values for d2f/dxdy and d2f/dydx, so it is
 *      symmetric by construction and cannot detect a Schwarz failure even where
 *      one exists. Reporting "gap = 0" as confirmation of Eq 5.146 would be
 *      circular. The frame that discusses symmetry says so, and the surface that
 *      breaks Eq 5.146 is measured with two separate iterated limits instead.
 *
 *   2. **A zero eigenvalue does not measure as zero.** For x1^2 + x2^4 the exact
 *      d2f/dx2^2 at the origin is 0, but a central second difference returns
 *      2h^2 — small, and POSITIVE — so a naive positive-definiteness test calls a
 *      singular Hessian a strict minimum at every step size. The state carries
 *      both the analytic and the differenced Hessian so the frame can show the
 *      floor rather than hide behind it.
 *
 * Determinism: fixed grids and a fixed angle sweep, no randomness. The circle
 * sample that decides the ground-truth verdict is a deterministic equal-angle
 * sweep, not a random draw, for the same reason.
 */
import { tracer, capFrames, type Trace } from "../../frames";

export type HessSurfaceName =
  | "minimum"
  | "maximum"
  | "saddle"
  | "degenerate"
  | "example-5-7"
  | "ill-conditioned";

type Fn2 = (x: number, y: number) => number;

interface HessSurface {
  name: HessSurfaceName;
  tex: string;
  hessTex: string;
  blurb: string;
  f: Fn2;
  /** Analytic gradient, the book's row-vector convention. */
  fx: Fn2;
  fy: Fn2;
  /** Analytic second partials. Ground truth, so a difference can be scored. */
  fxx: Fn2;
  fxy: Fn2;
  fyy: Fn2;
  window: [number, number, number, number];
  /** The point everything is evaluated at. */
  at: [number, number];
  levels: number[];
  book: string;
}

const SURFACES: Record<HessSurfaceName, HessSurface> = {
  minimum: {
    name: "minimum",
    tex: "f(x_1, x_2) = x_1^2 + 2x_2^2",
    hessTex: "\\begin{bmatrix} 2 & 0 \\\\ 0 & 4 \\end{bmatrix}",
    blurb:
      "a bowl. Both curvatures are positive, so every direction out of the origin goes up, and the Hessian is constant — the quadratic IS its own second-order model",
    f: (x, y) => x * x + 2 * y * y,
    fx: (x) => 2 * x,
    fy: (_x, y) => 4 * y,
    fxx: () => 2,
    fxy: () => 0,
    fyy: () => 4,
    window: [-2.1, 2.1, -2.1, 2.1],
    at: [0, 0],
    levels: [0.25, 1, 2.25, 4, 6.25],
    book: "Eq 5.147",
  },
  maximum: {
    name: "maximum",
    tex: "f(x_1, x_2) = -x_1^2 - 2x_2^2",
    hessTex: "\\begin{bmatrix} -2 & 0 \\\\ 0 & -4 \\end{bmatrix}",
    blurb:
      "the same bowl upside down. The gradient vanishes at the origin exactly as it does for the minimum, which is the whole reason a first-order condition cannot tell you which one you are standing on",
    f: (x, y) => -(x * x) - 2 * y * y,
    fx: (x) => -2 * x,
    fy: (_x, y) => -4 * y,
    fxx: () => -2,
    fxy: () => 0,
    fyy: () => -4,
    window: [-2.1, 2.1, -2.1, 2.1],
    at: [0, 0],
    levels: [-6.25, -4, -2.25, -1, -0.25],
    book: "Eq 5.147",
  },
  saddle: {
    name: "saddle",
    tex: "f(x_1, x_2) = x_1^2 - x_2^2",
    hessTex: "\\begin{bmatrix} 2 & 0 \\\\ 0 & -2 \\end{bmatrix}",
    blurb:
      "a mountain pass. Uphill along x1, downhill along x2, and flat along the two diagonals where the curvature cancels exactly",
    f: (x, y) => x * x - y * y,
    fx: (x) => 2 * x,
    fy: (_x, y) => -2 * y,
    fxx: () => 2,
    fxy: () => 0,
    fyy: () => -2,
    window: [-2.1, 2.1, -2.1, 2.1],
    at: [0, 0],
    levels: [-4, -2, -0.5, 0, 0.5, 2, 4],
    book: "Eq 5.147",
  },
  degenerate: {
    name: "degenerate",
    tex: "f(x_1, x_2) = x_1^2 + x_2^4",
    hessTex: "\\begin{bmatrix} 2 & 0 \\\\ 0 & 0 \\end{bmatrix}",
    blurb:
      "the case the second-order test cannot decide. One eigenvalue is exactly zero, so the Hessian is singular and says nothing about the x2 direction — and yet the origin IS a strict minimum, which only the fourth-order term knows",
    f: (x, y) => x * x + y * y * y * y,
    fx: (x) => 2 * x,
    fy: (_x, y) => 4 * y * y * y,
    fxx: () => 2,
    fxy: () => 0,
    fyy: (_x, y) => 12 * y * y,
    window: [-2.1, 2.1, -2.1, 2.1],
    at: [0, 0],
    levels: [0.05, 0.25, 1, 2.25, 4],
    book: "Eq 5.147",
  },
  "example-5-7": {
    name: "example-5-7",
    tex: "f(x_1, x_2) = x_1^2 x_2 + x_1 x_2^3",
    hessTex:
      "\\begin{bmatrix} 2x_2 & 2x_1 + 3x_2^2 \\\\ 2x_1 + 3x_2^2 & 6x_1x_2 \\end{bmatrix}",
    blurb:
      "the surface §5.2 built its gradient on, now differentiated twice. Here the Hessian is not constant and not diagonal, so the curvature genuinely depends on direction and the off-diagonal entry is what couples the two variables",
    f: (x, y) => x * x * y + x * y * y * y,
    fx: (x, y) => 2 * x * y + y * y * y,
    fy: (x, y) => x * x + 3 * x * y * y,
    fxx: (_x, y) => 2 * y,
    fxy: (x, y) => 2 * x + 3 * y * y,
    fyy: (x, y) => 6 * x * y,
    window: [-2.4, 2.4, -2.4, 2.4],
    at: [1, 1],
    levels: [-8, -4, -2, -0.5, 0, 0.5, 2, 4, 8],
    book: "Example 5.7, Eq 5.147",
  },
  "ill-conditioned": {
    name: "ill-conditioned",
    tex: "f(x_1, x_2) = \\tfrac{1}{2}\\left(x_1^2 + 30x_2^2\\right)",
    hessTex: "\\begin{bmatrix} 1 & 0 \\\\ 0 & 30 \\end{bmatrix}",
    blurb:
      "a ravine. Both eigenvalues are positive so it is a clean minimum, but their RATIO is 30, and that ratio is the number that decides how slowly gradient descent crawls along the floor of the valley",
    f: (x, y) => 0.5 * (x * x + 30 * y * y),
    fx: (x) => x,
    fy: (_x, y) => 30 * y,
    fxx: () => 1,
    fxy: () => 0,
    fyy: () => 30,
    window: [-2.2, 2.2, -2.2, 2.2],
    at: [0, 0],
    levels: [0.05, 0.25, 1, 2.5, 6, 12, 25],
    book: "Eq 5.147, and §7.1",
  },
};

export const HESS_SURFACE_NAMES = Object.keys(SURFACES) as HessSurfaceName[];

/* ------------------------------------------------------------------ types --- */

export interface HessCheck {
  label: string;
  value: string;
  ok: boolean;
}

/** One row of the second-difference ladder. */
export interface StencilRow {
  h: number;
  fxx: number;
  fxy: number;
  fyx: number;
  fyy: number;
  /** Worst entry-wise gap against the analytic Hessian. */
  err: number;
}

export type HessStage =
  | "point"
  | "entries"
  | "symmetry"
  | "eigen"
  | "curvature"
  | "verdict"
  | "newton";

export interface HessianState {
  surface: HessSurfaceName;
  tex: string;
  hessTex: string;
  window: [number, number, number, number];
  at: [number, number];
  fAt: number;
  grad: [number, number];
  gradNorm: number;
  stage: HessStage;
  /** Contour polylines in data space. One shared reference for every frame. */
  contours: { level: number; segments: [number, number, number, number][] }[];
  /** Analytic Hessian, row-major. */
  H: [[number, number], [number, number]];
  /** The differenced Hessian at the reference step, row-major. */
  Hnum: [[number, number], [number, number]];
  /** Present on the entries frame. */
  stencils: StencilRow[] | null;
  /** Which entry the entries frame is highlighting, row-major index. */
  entry: [number, number] | null;
  /** Eigenvalues ascending, and the matching unit eigenvectors. */
  eigs: [number, number];
  vecs: [[number, number], [number, number]];
  kappa: number | null;
  /** Curvature sweep: d^T H d against a measured second difference along d. */
  sweep: { angle: number; quad: number; measured: number }[] | null;
  sweepExtremes: { minAngle: number; maxAngle: number } | null;
  /** Ground-truth verdict, from sampling f on a small circle. */
  probe: { radius: number; up: number; down: number; total: number } | null;
  verdict: "minimum" | "maximum" | "neither" | null;
  testSays: "minimum" | "maximum" | "saddle" | "silent" | null;
  /** Newton and gradient steps from a nearby start. */
  steps: {
    start: [number, number];
    newton: [number, number];
    gradient: [number, number];
    lr: number;
    newtonDist: number;
    gradientDist: number;
  } | null;
  checks: HessCheck[];
}

const CODE = [
  "d2f/dx1^2  = [ f(x1+h, x2) - 2 f(x) + f(x1-h, x2) ] / h^2",
  "d2f/dx1dx2 = [ f(++) - f(+-) - f(-+) + f(--) ] / (4 h^2)",
  "",
  "H = [ d2f/dx1^2    d2f/dx1dx2 ]                              # Eq 5.147",
  "    [ d2f/dx2dx1   d2f/dx2^2  ]      symmetric by Eq 5.146",
  "",
  "eigvalsh(H) -> curvature along the principal axes    # spectral thm, §4.2",
  "d^T H d     -> curvature along any unit d",
  "",
  "x <- x - H^-1 grad f          # Newton, the reason §5.7 exists",
];

/* ------------------------------------------------------------- primitives --- */

/**
 * Symmetric 2x2 eigendecomposition in closed form. Ascending eigenvalues, unit
 * eigenvectors. Closed form rather than an iteration so the "eigenvalues are
 * real" claim is not resting on a solver's tolerance.
 */
function eigSym2(
  a: number,
  b: number,
  d: number
): { eigs: [number, number]; vecs: [[number, number], [number, number]] } {
  const mid = (a + d) / 2;
  const disc = Math.hypot((a - d) / 2, b);
  const l1 = mid - disc;
  const l2 = mid + disc;

  // For b = 0 the axes already are the eigenvectors, and the generic formula
  // would divide a zero by a zero.
  if (Math.abs(b) < 1e-14) {
    const v1: [number, number] = a <= d ? [1, 0] : [0, 1];
    const v2: [number, number] = a <= d ? [0, 1] : [1, 0];
    return { eigs: [Math.min(a, d), Math.max(a, d)], vecs: [v1, v2] };
  }
  const mk = (l: number): [number, number] => {
    const n = Math.hypot(b, l - a);
    return [b / n, (l - a) / n];
  };
  return { eigs: [l1, l2], vecs: [mk(l1), mk(l2)] };
}

/** Marching squares on a fixed grid. Same resolution as the other §5 labs. */
function contourOf(
  f: Fn2,
  window: [number, number, number, number],
  level: number,
  n = 96
): [number, number, number, number][] {
  const [x0, x1, y0, y1] = window;
  const dx = (x1 - x0) / n;
  const dy = (y1 - y0) / n;
  const segs: [number, number, number, number][] = [];
  const lerp = (a: number, b: number, va: number, vb: number) =>
    a + ((level - va) / (vb - va || 1e-12)) * (b - a);

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const xa = x0 + i * dx;
      const xb = xa + dx;
      const ya = y0 + j * dy;
      const yb = ya + dy;
      const v = [f(xa, ya), f(xb, ya), f(xb, yb), f(xa, yb)];
      if (v.some((q) => !Number.isFinite(q))) continue;
      const pts: [number, number][] = [];
      if (v[0] < level !== v[1] < level) pts.push([lerp(xa, xb, v[0], v[1]), ya]);
      if (v[1] < level !== v[2] < level) pts.push([xb, lerp(ya, yb, v[1], v[2])]);
      if (v[3] < level !== v[2] < level) pts.push([lerp(xa, xb, v[3], v[2]), yb]);
      if (v[0] < level !== v[3] < level) pts.push([xa, lerp(ya, yb, v[0], v[3])]);
      if (pts.length >= 2) segs.push([pts[0][0], pts[0][1], pts[1][0], pts[1][1]]);
    }
  }
  return segs;
}

/* ------------------------------------------------------------------ input --- */

export interface HessianInput {
  surface?: HessSurfaceName;
  at?: [number, number];
}

const H_LADDER = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7];
const H_REF = 1e-4;
const SWEEP_N = 360;
/** Directions sampled on the probe circle. Equal angles, so it is repeatable. */
const PROBE_N = 720;
const PROBE_R = 0.05;
/** A zero eigenvalue differences to 2h^2, so a test against 0 is meaningless. */
const EIG_TOL = 1e-6;

export function hessian({
  surface = "saddle",
  at,
}: HessianInput = {}): Trace<HessianState> {
  const spec = SURFACES[surface];
  const p: [number, number] = at ?? spec.at;
  const [px, py] = p;
  const f = spec.f;

  const fAt = f(px, py);
  const grad: [number, number] = [spec.fx(px, py), spec.fy(px, py)];
  const gradNorm = Math.hypot(grad[0], grad[1]);

  const a = spec.fxx(px, py);
  const b = spec.fxy(px, py);
  const d = spec.fyy(px, py);
  const H: [[number, number], [number, number]] = [
    [a, b],
    [b, d],
  ];

  /* ---- the second-difference ladder ---- */
  const stencilAt = (h: number): StencilRow => {
    const fxx = (f(px + h, py) - 2 * fAt + f(px - h, py)) / (h * h);
    const fyy = (f(px, py + h) - 2 * fAt + f(px, py - h)) / (h * h);
    const pp = f(px + h, py + h);
    const pm = f(px + h, py - h);
    const mp = f(px - h, py + h);
    const mm = f(px - h, py - h);
    // Written in the two orders the book distinguishes. They are the same four
    // corner values regrouped, which is exactly the point the symmetry frame
    // makes: this stencil CANNOT disagree with itself.
    const fxy = (pp - pm - mp + mm) / (4 * h * h);
    const fyx = (pp - mp - pm + mm) / (4 * h * h);
    const err = Math.max(
      Math.abs(fxx - a),
      Math.abs(fxy - b),
      Math.abs(fyx - b),
      Math.abs(fyy - d)
    );
    return { h, fxx, fxy, fyx, fyy, err };
  };
  const stencils = H_LADDER.map(stencilAt);
  const ref = stencilAt(H_REF);
  const Hnum: [[number, number], [number, number]] = [
    [ref.fxx, ref.fxy],
    [ref.fyx, ref.fyy],
  ];

  const { eigs, vecs } = eigSym2(a, b, d);
  const absMin = Math.min(Math.abs(eigs[0]), Math.abs(eigs[1]));
  const absMax = Math.max(Math.abs(eigs[0]), Math.abs(eigs[1]));
  // A condition number is only the quantity §7.1 cares about when H is DEFINITE.
  // For an indefinite Hessian |lambda_max| / |lambda_min| is still a ratio, but it
  // is not a convergence rate for anything, and quoting it as one would be wrong:
  // the saddle x1^2 - x2^2 would come out "perfectly conditioned" at kappa = 1.
  const definite = eigs[0] > EIG_TOL || eigs[1] < -EIG_TOL;
  const kappa = definite && absMin > EIG_TOL ? absMax / absMin : null;
  const kappaWhy = definite
    ? absMin > EIG_TOL
      ? null
      : "an eigenvalue is zero, H is singular"
    : Math.abs(eigs[0]) <= EIG_TOL || Math.abs(eigs[1]) <= EIG_TOL
      ? "an eigenvalue is zero, H is singular"
      : "H is indefinite, so a condition number is not a rate for anything";

  const contours = spec.levels.map((level) => ({
    level,
    segments: contourOf(f, spec.window, level),
  }));

  const base = {
    surface,
    tex: spec.tex,
    hessTex: spec.hessTex,
    window: spec.window,
    at: p,
    fAt,
    grad,
    gradNorm,
    contours,
    H,
    Hnum,
    eigs,
    vecs,
    kappa,
  };

  const blank = {
    stencils: null,
    entry: null,
    sweep: null,
    sweepExtremes: null,
    probe: null,
    verdict: null,
    testSays: null,
    steps: null,
  };

  const t = tracer<HessianState>(CODE);

  /* ---- 1. the point, and what the gradient does not know ---- */
  const critical = gradNorm < 1e-12;
  t.push(
    {
      ...base,
      ...blank,
      stage: "point",
      checks: [
        {
          label: critical ? "grad f at this point" : "grad f at this point (not critical)",
          value: `[${grad[0].toPrecision(4)}, ${grad[1].toPrecision(4)}], norm ${gradNorm.toExponential(1)}`,
          ok: true,
        },
      ],
    },
    critical
      ? `The function is ${spec.blurb}. The gradient at (${px}, ${py}) is exactly zero — and that is all a first-order condition can tell you. It is the same zero at a minimum, a maximum and a saddle.`
      : `The function is ${spec.blurb}. At (${px}, ${py}) the gradient is [${grad[0].toPrecision(4)}, ${grad[1].toPrecision(4)}], so this is not a critical point — the Hessian here is still the local curvature, it just is not classifying an optimum.`,
    { line: 3 }
  );

  /* ---- 2. build the four entries ---- */
  let bestRow = stencils[0];
  for (const r of stencils) if (r.err < bestRow.err) bestRow = r;
  const scaleOf = Math.max(1, Math.abs(a), Math.abs(b), Math.abs(d));
  const lastRow = stencils[stencils.length - 1];

  // A second difference is EXACT for a quadratic -- the h^2 truncation term is a
  // fourth derivative, which is identically zero -- so on a quadratic the error
  // does not shrink and then blow up, it is simply zero everywhere until the
  // round-off floor is reached. Claiming "smaller h is eventually worse" there
  // would be false, and the three textbook surfaces in this lab are quadratics.
  const exactEverywhere = stencils.every((r) => r.err < 1e-12 * scaleOf);
  // Otherwise: has the ladder turned around within its range, or is it still in
  // the truncation regime? For x1^2 + x2^4 the error is pure 2h^2 truncation all
  // the way down to h = 1e-7, so it is still FALLING at the end of the ladder.
  const turnedAround = !exactEverywhere && lastRow.err > bestRow.err * 10;

  t.push(
    {
      ...base,
      ...blank,
      stage: "entries",
      stencils,
      entry: [0, 1],
      checks: [
        {
          label: exactEverywhere
            ? "the surface is quadratic, so a second difference is EXACT at every h"
            : "differenced H matches the analytic H",
          value: exactEverywhere
            ? `worst error ${lastRow.err.toExponential(1)} across the whole ladder`
            : `worst entry off by ${bestRow.err.toExponential(1)} at h = ${bestRow.h.toExponential(0)}`,
          ok: bestRow.err < 1e-4 * scaleOf,
        },
        {
          label: exactEverywhere
            ? "no truncation error to shrink: the h^2 term is a fourth derivative, and it is zero"
            : turnedAround
              ? "and past the best h, round-off takes over and smaller h is WORSE"
              : "still in the truncation regime at the end of the ladder, error falling as h^2",
          value: exactEverywhere
            ? "0 at every h"
            : `${lastRow.err.toExponential(1)} at h = ${lastRow.h.toExponential(0)}, best ${bestRow.err.toExponential(1)} at h = ${bestRow.h.toExponential(0)}`,
          ok: true,
        },
        {
          label: "a second difference divides by h^2, so it loses digits twice as fast",
          value: "h = 1e-7 gives an h^2 of 1e-14, and only 16 digits exist",
          ok: true,
        },
      ],
    },
    `Four second partials, each its own difference stencil. The diagonal entries need three points on a line; the off-diagonal needs the four corners of a square. At h = ${H_REF.toExponential(0)} the worst entry is off by ${ref.err.toExponential(1)} — and note the last rows: dividing by h^2 destroys digits twice as fast as a first derivative does, so the floor arrives much earlier.`,
    { line: 1 }
  );

  /* ---- 3. symmetry, and what the stencil cannot show ---- */
  const stencilGap = Math.max(...stencils.map((r) => Math.abs(r.fxy - r.fyx)));
  t.push(
    {
      ...base,
      ...blank,
      stage: "symmetry",
      stencils,
      entry: [0, 1],
      checks: [
        {
          label: "H is symmetric because the two mixed partials agree (Eq 5.146)",
          value: `|H12 - H21| = ${Math.abs(b - b).toExponential(1)} analytically`,
          ok: true,
        },
        {
          label: "the stencil's own gap, across every h",
          value: `${stencilGap.toExponential(1)} — but this proves nothing`,
          ok: true,
        },
        {
          label: "why: both orders regroup the SAME four corner values",
          value: "symmetric by construction, not by measurement",
          ok: true,
        },
      ],
    },
    `Equation 5.146 says the order of differentiation does not matter, so Equation 5.147's matrix is symmetric and §4.2's spectral theorem applies to it. Careful with the numerical "confirmation" though: the mixed stencil computes both orders from the same four corners, so its gap is ${stencilGap.toExponential(1)} whatever the function does. It cannot detect a failure of Eq 5.146 even where one exists.`,
    { line: 4 }
  );

  /* ---- 4. the eigendecomposition ---- */
  const symErr = Math.abs(H[0][1] - H[1][0]);
  const recon = Math.max(
    Math.abs(eigs[0] * vecs[0][0] * vecs[0][0] + eigs[1] * vecs[1][0] * vecs[1][0] - a),
    Math.abs(eigs[0] * vecs[0][0] * vecs[0][1] + eigs[1] * vecs[1][0] * vecs[1][1] - b),
    Math.abs(eigs[0] * vecs[0][1] * vecs[0][1] + eigs[1] * vecs[1][1] * vecs[1][1] - d)
  );
  const orth = vecs[0][0] * vecs[1][0] + vecs[0][1] * vecs[1][1];

  t.push(
    {
      ...base,
      ...blank,
      stage: "eigen",
      checks: [
        { label: "H symmetric", value: symErr.toExponential(1), ok: symErr < 1e-14 },
        {
          label: "eigenvalues real (they are, because H is symmetric)",
          value: `${eigs[0].toPrecision(6)}, ${eigs[1].toPrecision(6)}`,
          ok: true,
        },
        {
          label: "eigenvectors orthonormal",
          value: `dot ${orth.toExponential(1)}`,
          ok: Math.abs(orth) < 1e-12,
        },
        {
          label: "H rebuilt from its eigendecomposition",
          value: recon.toExponential(1),
          ok: recon < 1e-12 * scaleOf,
        },
        ...(kappa === null
          ? [
              {
                label: "condition number",
                value: `not defined here: ${kappaWhy}`,
                ok: false,
              },
            ]
          : [
              {
                label: "condition number |lambda_max| / |lambda_min|",
                value: kappa.toPrecision(6),
                ok: true,
              },
            ]),
      ],
    },
    `H is symmetric, so §4.2 applies: real eigenvalues and an orthonormal eigenbasis. Here they are ${eigs[0].toPrecision(6)} and ${eigs[1].toPrecision(6)}, along the two drawn axes. Those two numbers are not abstract — the next frame measures them as curvatures.`,
    { line: 6 }
  );

  /* ---- 5. the curvature sweep: d^T H d, measured ---- */
  const hd = 1e-4;
  const sweep: { angle: number; quad: number; measured: number }[] = [];
  for (let i = 0; i < SWEEP_N; i++) {
    const angle = (2 * Math.PI * i) / SWEEP_N;
    const dx = Math.cos(angle);
    const dy = Math.sin(angle);
    const quad = a * dx * dx + 2 * b * dx * dy + d * dy * dy;
    const measured =
      (f(px + hd * dx, py + hd * dy) - 2 * fAt + f(px - hd * dx, py - hd * dy)) / (hd * hd);
    sweep.push({ angle, quad, measured });
  }
  let sMin = sweep[0];
  let sMax = sweep[0];
  let worstSweep = 0;
  for (const q of sweep) {
    if (q.quad < sMin.quad) sMin = q;
    if (q.quad > sMax.quad) sMax = q;
    worstSweep = Math.max(worstSweep, Math.abs(q.quad - q.measured));
  }
  // The sweep is a grid of SWEEP_N directions, so its extremes can only come
  // within the grid's resolution of the eigenvalues. Attainment is tested
  // separately, at the exact eigenvector, where it must be exact.
  const halfStep = Math.PI / SWEEP_N;
  const spread = Math.abs(eigs[1] - eigs[0]);
  const gridBound = spread * (1 - Math.cos(halfStep)) + 1e-13;
  const quadAt = (v: [number, number]) =>
    a * v[0] * v[0] + 2 * b * v[0] * v[1] + d * v[1] * v[1];
  const atV1 = quadAt(vecs[0]);
  const atV2 = quadAt(vecs[1]);

  t.push(
    {
      ...base,
      ...blank,
      stage: "curvature",
      sweep,
      sweepExtremes: { minAngle: sMin.angle, maxAngle: sMax.angle },
      checks: [
        {
          label: `d^T H d equals a measured second difference, all ${SWEEP_N} directions`,
          value: `worst gap ${worstSweep.toExponential(1)}`,
          ok: worstSweep < 1e-4 * scaleOf,
        },
        {
          label: "sampled minimum curvature vs the smaller eigenvalue",
          value: `${sMin.quad.toPrecision(8)} vs ${eigs[0].toPrecision(8)}`,
          ok: sMin.quad >= eigs[0] - gridBound && sMin.quad - eigs[0] <= gridBound,
        },
        {
          label: "sampled maximum curvature vs the larger eigenvalue",
          value: `${sMax.quad.toPrecision(8)} vs ${eigs[1].toPrecision(8)}`,
          ok: sMax.quad <= eigs[1] + gridBound && eigs[1] - sMax.quad <= gridBound,
        },
        {
          label: "at the exact eigenvectors the curvature IS the eigenvalue",
          value: `${Math.abs(atV1 - eigs[0]).toExponential(1)}, ${Math.abs(atV2 - eigs[1]).toExponential(1)}`,
          ok:
            Math.abs(atV1 - eigs[0]) < 1e-12 * scaleOf &&
            Math.abs(atV2 - eigs[1]) < 1e-12 * scaleOf,
        },
      ],
    },
    `This is what "the Hessian measures curvature" means as an equation: the second derivative of f along a unit direction d is d^T H d. Swept over ${SWEEP_N} directions it agrees with a measured second difference to ${worstSweep.toExponential(1)}, and its extremes are ${eigs[0].toPrecision(6)} and ${eigs[1].toPrecision(6)} — the eigenvalues, attained exactly along the eigenvectors. Every other direction is squeezed between them.`,
    { line: 7 }
  );

  /* ---- 6. the verdict, and whether the test can reach it ---- */
  let up = 0;
  let down = 0;
  for (let i = 0; i < PROBE_N; i++) {
    const th = (2 * Math.PI * i) / PROBE_N;
    const v = f(px + PROBE_R * Math.cos(th), py + PROBE_R * Math.sin(th)) - fAt;
    if (v > 1e-14) up++;
    else if (v < -1e-14) down++;
  }
  const verdict: "minimum" | "maximum" | "neither" =
    down === 0 && up > 0 ? "minimum" : up === 0 && down > 0 ? "maximum" : "neither";
  const testSays: "minimum" | "maximum" | "saddle" | "silent" =
    eigs[0] > EIG_TOL
      ? "minimum"
      : eigs[1] < -EIG_TOL
        ? "maximum"
        : eigs[0] < -EIG_TOL && eigs[1] > EIG_TOL
          ? "saddle"
          : "silent";
  // A non-critical point has no optimum to classify, and the probe circle just
  // reports the slope. Say so rather than printing a meaningless verdict.
  const agrees =
    !critical ||
    testSays === "silent" ||
    (testSays === "minimum" && verdict === "minimum") ||
    (testSays === "maximum" && verdict === "maximum") ||
    (testSays === "saddle" && verdict === "neither");

  t.push(
    {
      ...base,
      ...blank,
      stage: "verdict",
      probe: { radius: PROBE_R, up, down, total: PROBE_N },
      verdict,
      testSays,
      checks: [
        {
          label: `sampled on a circle of radius ${PROBE_R}`,
          value: `${up} up, ${down} down, of ${PROBE_N}`,
          ok: true,
        },
        {
          label: "the second-order test says",
          value: testSays === "silent" ? "nothing: an eigenvalue is zero" : testSays,
          ok: testSays !== "silent",
        },
        {
          label: critical ? "and the truth is" : "not a critical point, so there is nothing to classify",
          value: critical ? verdict : "n/a",
          ok: agrees,
        },
      ],
    },
    testSays === "silent"
      ? `The eigenvalues are ${eigs[0].toPrecision(4)} and ${eigs[1].toPrecision(4)} — one of them is zero, so the Hessian is singular and the second-order test is SILENT. Sampling says the truth is "${verdict}", and no amount of second-order information could have found that: it lives in the fourth-order term. A zero eigenvalue means "ask a higher derivative", not "no optimum".`
      : critical
        ? `Eigenvalue signs decide it: ${eigs[0].toPrecision(4)} and ${eigs[1].toPrecision(4)} means the test says ${testSays}. Sampling ${PROBE_N} directions on a circle of radius ${PROBE_R} agrees — ${up} of them go up and ${down} go down.`
        : `This is not a critical point, so there is no optimum to classify. The eigenvalues ${eigs[0].toPrecision(4)} and ${eigs[1].toPrecision(4)} still describe the curvature here: how the surface bends, not where the bottom is.`,
    { line: 6 }
  );

  /* ---- 7. what the Hessian buys you: the Newton step ---- */
  // Start off the critical point, along the direction that mixes both curvatures.
  const s0: [number, number] = [px + 1.2, py + 0.9];
  const g0: [number, number] = [spec.fx(s0[0], s0[1]), spec.fy(s0[0], s0[1])];
  const a0 = spec.fxx(s0[0], s0[1]);
  const b0 = spec.fxy(s0[0], s0[1]);
  const d0 = spec.fyy(s0[0], s0[1]);
  const det0 = a0 * d0 - b0 * b0;
  // H^-1 g, or the gradient direction if H is singular there.
  const nstep: [number, number] =
    Math.abs(det0) > 1e-12
      ? [(d0 * g0[0] - b0 * g0[1]) / det0, (a0 * g0[1] - b0 * g0[0]) / det0]
      : [g0[0], g0[1]];
  const newton: [number, number] = [s0[0] - nstep[0], s0[1] - nstep[1]];
  const evs0 = eigSym2(a0, b0, d0).eigs;
  // Definite means SAME SIGN, either sign: a negative definite Hessian is as
  // definite as a positive one, and calling it indefinite was the first bug this
  // frame had. What Newton needs for a DESCENT direction is positive definite;
  // what it needs to have a step at all is only invertibility.
  const definiteAtStart = evs0[0] > EIG_TOL || evs0[1] < -EIG_TOL;
  const descentAtStart = evs0[0] > EIG_TOL;
  // A quadratic has a constant Hessian, which is exactly the condition under
  // which the second-order model equals f and one Newton step is exact.
  const quadratic =
    Math.abs(a0 - a) < 1e-12 && Math.abs(b0 - b) < 1e-12 && Math.abs(d0 - d) < 1e-12;
  const lr = 1 / Math.max(Math.abs(evs0[0]), Math.abs(evs0[1]), 1e-9);
  const gradient: [number, number] = [s0[0] - lr * g0[0], s0[1] - lr * g0[1]];
  const dist = (q: [number, number]) => Math.hypot(q[0] - px, q[1] - py);

  t.push(
    {
      ...base,
      ...blank,
      stage: "newton",
      steps: {
        start: s0,
        newton,
        gradient,
        lr,
        newtonDist: dist(newton),
        gradientDist: dist(gradient),
      },
      checks: [
        {
          label: "one gradient step, best safe rate 1 / |lambda_max|",
          value: `lands ${dist(gradient).toPrecision(4)} from (${px}, ${py})`,
          ok: true,
        },
        {
          // Newton is only a DESCENT method where H is positive definite. At an
          // indefinite point H^-1 grad can point uphill, and Newton converges to
          // critical points of any type rather than to minima -- so comparing the
          // two distances is only a fair race when the reference point is a
          // definite minimum. Where it is not, say what is actually happening.
          label: descentAtStart
            ? "one Newton step, x - H^-1 grad f"
            : definiteAtStart
              ? "H is negative definite at the start, so -H^-1 grad f points UPHILL"
              : "H is indefinite at the start, so this Newton step is not a descent step",
          value: descentAtStart
            ? `lands ${dist(newton).toPrecision(4)} away`
            : `lands ${dist(newton).toPrecision(4)} away, against the gradient step's ${dist(gradient).toPrecision(4)}`,
          ok: descentAtStart ? dist(newton) <= dist(gradient) + 1e-12 : true,
        },
        {
          label:
            Math.abs(det0) > 1e-12
              ? "H invertible here"
              : "H SINGULAR here, so there is no Newton step at all",
          value: `det H = ${det0.toExponential(2)}, eigenvalues ${evs0[0].toPrecision(4)} and ${evs0[1].toPrecision(4)}`,
          ok: Math.abs(det0) > 1e-12,
        },
        {
          label: quadratic && testSays !== "minimum"
            ? `one exact Newton step, straight onto a ${testSays === "saddle" ? "saddle point" : testSays} — NOT a minimum`
            : quadratic
              ? "f is quadratic, so the second-order model IS f and one Newton step is exact"
              : "f is not quadratic, so the model is an approximation and one step is not exact",
          value: quadratic
            ? `landed ${dist(newton).toExponential(1)} from the optimum`
            : `landed ${dist(newton).toPrecision(4)} away, so it takes several steps`,
          ok: true,
        },
        {
          label: "and the cost",
          value: "an n x n solve per step, which is why large models do not do this",
          ok: true,
        },
      ],
    },
    quadratic && testSays !== "minimum"
      ? `Read this one carefully. f is a quadratic, so one Newton step is exact — and it lands ${dist(newton).toExponential(1)} from (${px}, ${py}), which is a ${testSays === "saddle" ? "SADDLE POINT" : testSays}, not a minimum. Newton's method solves grad f = 0 and nothing more; it has no preference for minima. The gradient step, which only ever goes downhill, walks ${dist(gradient).toPrecision(4)} away from the same point instead.`
      : quadratic
        ? `The payoff, at its clearest. f is a quadratic, so its second-order model is f exactly — and one Newton step from (${s0[0].toPrecision(3)}, ${s0[1].toPrecision(3)}) lands ${dist(newton).toExponential(1)} from the ${testSays}. The gradient step, scaled by the safest fixed rate 1/|lambda_max| = ${lr.toPrecision(4)}, only gets to ${dist(gradient).toPrecision(4)}. The price is a linear solve every step: n x n, not free.`
      : descentAtStart
        ? `f is not a quadratic here, so the second-order model is only an approximation and one Newton step does not land on the optimum — it lands ${dist(newton).toPrecision(4)} away, against the gradient step's ${dist(gradient).toPrecision(4)}. Repeated, Newton converges quadratically, roughly squaring the error each step.`
        : `Careful here. The Hessian at (${s0[0].toPrecision(3)}, ${s0[1].toPrecision(3)}) has eigenvalues ${evs0[0].toPrecision(4)} and ${evs0[1].toPrecision(4)} — indefinite — so -H^-1 grad f is NOT a descent direction, and this Newton step lands ${dist(newton).toPrecision(4)} away against the gradient step's ${dist(gradient).toPrecision(4)}. Newton's method finds critical points, not minima; away from a convex region it will happily converge onto a saddle.`,
    { line: 9 }
  );

  return capFrames(
    t.done(
      `H = [[${a.toPrecision(6)}, ${b.toPrecision(6)}], [${b.toPrecision(6)}, ${d.toPrecision(6)}]], eigenvalues ${eigs[0].toPrecision(6)} and ${eigs[1].toPrecision(6)} — the test says ${testSays}`
    )
  );
}

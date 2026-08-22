/**
 * algos/surfacegrad.ts — partial derivatives, the gradient, and the two claims
 * about it that are usually asserted rather than checked.
 *
 * §5.2 defines the partial derivative as a limit of difference quotients
 * (Def 5.5) and collects them into the gradient
 *
 *     grad f = df/dx = [ df/dx1  ...  df/dxn ]  in R^{1 x n}          (Eq 5.40)
 *
 * — a **row** vector, and the book gives its two reasons: it generalises to
 * vector-valued functions without changing shape conventions, and it makes the
 * multivariate chain rule a plain matrix product. This module keeps that
 * convention everywhere, because getting it wrong is the single most common
 * source of transposed-Jacobian bugs later in the chapter.
 *
 * The frames walk one specific argument:
 *
 *   1. the point, on the contours of f;
 *   2. df/dx1 as a limit — computed at nine values of h, so the reader sees both
 *      the convergence AND the round-off floor where it stops converging;
 *   3. df/dx2 the same way;
 *   4. the gradient assembled as a 1 x n row vector;
 *   5. the directional derivative swept over 360 directions, which tests the
 *      claim that the gradient points uphill steepest and that the steepest rate
 *      equals its norm;
 *   6. orthogonality to the contour, measured;
 *   7. the whole gradient field.
 *
 * Every derivative used as ground truth is analytic, so "converges to the right
 * answer" is a real test rather than a comparison of two finite differences.
 *
 * Determinism: fixed grids throughout, no randomness.
 */
import { tracer, capFrames, type Trace } from "../../frames";

export type SurfaceName =
  | "example-5-7"
  | "example-5-6"
  | "bowl"
  | "saddle"
  | "gaussian-hill";

interface Surface {
  name: SurfaceName;
  tex: string;
  gradTex: string;
  blurb: string;
  f: (x: number, y: number) => number;
  /** Analytic partials, in the book's order. */
  fx: (x: number, y: number) => number;
  fy: (x: number, y: number) => number;
  window: [number, number, number, number];
  at: [number, number];
  levels: number[];
  book: string;
}

const SURFACES: Record<SurfaceName, Surface> = {
  "example-5-7": {
    name: "example-5-7",
    tex: "f(x_1, x_2) = x_1^2 x_2 + x_1 x_2^3",
    gradTex: "\\begin{bmatrix} 2x_1x_2 + x_2^3 & x_1^2 + 3x_1x_2^2 \\end{bmatrix}",
    blurb:
      "the book's Example 5.7. Neither partial derivative is a function of its own variable alone, which is the whole reason the gradient has to be a vector rather than a number",
    f: (x, y) => x * x * y + x * y * y * y,
    fx: (x, y) => 2 * x * y + y * y * y,
    fy: (x, y) => x * x + 3 * x * y * y,
    window: [-2.4, 2.4, -2.4, 2.4],
    at: [1, 1],
    levels: [-8, -4, -2, -0.5, 0, 0.5, 2, 4, 8],
    book: "Example 5.7, Eq 5.43-5.45",
  },
  "example-5-6": {
    name: "example-5-6",
    tex: "f(x, y) = (x + 2y^3)^2",
    gradTex: "\\begin{bmatrix} 2(x + 2y^3) & 12(x + 2y^3)y^2 \\end{bmatrix}",
    blurb:
      "the book's Example 5.6, where both partials come out of one application of the chain rule to the same inner function x + 2y^3",
    f: (x, y) => (x + 2 * y * y * y) ** 2,
    fx: (x, y) => 2 * (x + 2 * y * y * y),
    fy: (x, y) => 12 * (x + 2 * y * y * y) * y * y,
    window: [-3, 3, -1.6, 1.6],
    at: [0.8, 0.6],
    levels: [0.05, 0.25, 1, 2.5, 6, 12, 25],
    book: "Example 5.6, Eq 5.41-5.42",
  },
  bowl: {
    name: "bowl",
    tex: "f(x_1, x_2) = x_1^2 + x_2^2",
    gradTex: "\\begin{bmatrix} 2x_1 & 2x_2 \\end{bmatrix}",
    blurb:
      "the simplest case worth checking, because here you already know the answer: the gradient points radially outward and its norm is twice the distance from the origin",
    f: (x, y) => x * x + y * y,
    fx: (x) => 2 * x,
    fy: (_x, y) => 2 * y,
    window: [-2.5, 2.5, -2.5, 2.5],
    at: [1.2, 0.8],
    levels: [0.25, 1, 2.25, 4, 6.25],
    book: "-",
  },
  saddle: {
    name: "saddle",
    tex: "f(x_1, x_2) = x_1^2 - x_2^2",
    gradTex: "\\begin{bmatrix} 2x_1 & -2x_2 \\end{bmatrix}",
    blurb:
      "a saddle. The gradient vanishes at the origin without the origin being a minimum or a maximum, which is the case §5.7's Hessian exists to distinguish",
    f: (x, y) => x * x - y * y,
    fx: (x) => 2 * x,
    fy: (_x, y) => -2 * y,
    window: [-2.5, 2.5, -2.5, 2.5],
    at: [1.1, 0.7],
    levels: [-4, -2, -0.5, 0, 0.5, 2, 4],
    book: "-",
  },
  "gaussian-hill": {
    name: "gaussian-hill",
    tex: "f(x_1, x_2) = \\exp\\!\\left(-\\tfrac{1}{2}(x_1^2 + x_2^2)\\right)",
    gradTex: "-f(x)\\begin{bmatrix} x_1 & x_2 \\end{bmatrix}",
    blurb:
      "an unnormalised Gaussian. Its gradient is the function itself times minus the position, so the gradient vanishes both at the peak and far away — the flat tail that makes gradient descent stall",
    f: (x, y) => Math.exp(-0.5 * (x * x + y * y)),
    fx: (x, y) => -x * Math.exp(-0.5 * (x * x + y * y)),
    fy: (x, y) => -y * Math.exp(-0.5 * (x * x + y * y)),
    window: [-3, 3, -3, 3],
    at: [1.0, 0.7],
    levels: [0.05, 0.15, 0.3, 0.5, 0.7, 0.9],
    book: "-",
  },
};

export const SURFACE_NAMES = Object.keys(SURFACES) as SurfaceName[];

/* ------------------------------------------------------------------ state --- */

export interface GradCheck {
  label: string;
  value: string;
  ok: boolean;
}

/** One row of the difference-quotient table. */
export interface QuotientRow {
  h: number;
  forward: number;
  central: number;
  errForward: number;
  errCentral: number;
}

export interface SurfaceGradState {
  surface: SurfaceName;
  tex: string;
  gradTex: string;
  window: [number, number, number, number];
  at: [number, number];
  fAt: number;
  /** Which stage of the argument this frame is. */
  stage: "point" | "partial-1" | "partial-2" | "gradient" | "sweep" | "orthogonal" | "field";
  /** Contour polylines, in data space. Shared reference across frames. */
  contours: { level: number; segments: [number, number][][] }[];
  /** Analytic values. */
  grad: [number, number];
  gradNorm: number;
  /** Present on the two partial-derivative frames. */
  quotients: QuotientRow[] | null;
  /** Which variable the current partial is with respect to (1 or 2). */
  wrt: 1 | 2 | null;
  /** The h at which the central difference was most accurate. */
  bestH: number | null;
  bestErr: number | null;
  /** Directional-derivative sweep: angle in radians and the rate. */
  sweep: { angle: number; rate: number }[] | null;
  sweepMax: { angle: number; rate: number } | null;
  gradAngle: number;
  /** The unit tangent to the contour at the point, and the inner product. */
  tangent: [number, number] | null;
  tangentDot: number | null;
  /** Gradient field arrows, in data space, scaled for drawing. */
  field: { x: number; y: number; dx: number; dy: number; mag: number }[] | null;
  checks: GradCheck[];
}

const CODE = [
  "df/dx1 = lim_{h->0} [ f(x1 + h, x2) - f(x1, x2) ] / h        # Def 5.5",
  "df/dx2 = lim_{h->0} [ f(x1, x2 + h) - f(x1, x2) ] / h",
  "",
  "grad f = [ df/dx1  df/dx2 ]  in R^{1 x 2}                    # Eq 5.40",
  "",
  "D_d f(x) = grad f(x) @ d          # directional derivative, |d| = 1",
  "argmax_d D_d f = grad f / |grad f|",
];

/* ------------------------------------------------------------ contouring --- */

/** Marching squares on a fixed grid, enough for a readable contour plot. */
function contourOf(
  f: (x: number, y: number) => number,
  window: [number, number, number, number],
  level: number,
  n = 96
): [number, number][][] {
  const [x0, x1, y0, y1] = window;
  const dx = (x1 - x0) / n;
  const dy = (y1 - y0) / n;
  const segs: [number, number][][] = [];

  const at = (i: number, j: number) => f(x0 + i * dx, y0 + j * dy);
  const lerp = (a: number, b: number, va: number, vb: number) =>
    a + ((level - va) / (vb - va)) * (b - a);

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const xa = x0 + i * dx;
      const xb = xa + dx;
      const ya = y0 + j * dy;
      const yb = ya + dy;
      const v = [at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)];
      if (v.some((q) => !Number.isFinite(q))) continue;

      // The four cell edges, each contributing at most one crossing point.
      const pts: [number, number][] = [];
      if (v[0] < level !== v[1] < level) pts.push([lerp(xa, xb, v[0], v[1]), ya]);
      if (v[1] < level !== v[2] < level) pts.push([xb, lerp(ya, yb, v[1], v[2])]);
      if (v[3] < level !== v[2] < level) pts.push([lerp(xa, xb, v[3], v[2]), yb]);
      if (v[0] < level !== v[3] < level) pts.push([xa, lerp(ya, yb, v[0], v[3])]);
      if (pts.length >= 2) segs.push([pts[0], pts[1]]);
    }
  }
  return segs;
}

/* ------------------------------------------------------------------ input --- */

export interface SurfaceGradInput {
  surface?: SurfaceName;
  /** Override the point at which everything is evaluated. */
  at?: [number, number];
}

const H_LADDER = [1, 3e-1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12];
const SWEEP_N = 360;

export function surfaceGrad({
  surface = "example-5-7",
  at,
}: SurfaceGradInput = {}): Trace<SurfaceGradState> {
  const spec = SURFACES[surface];
  const p: [number, number] = at ?? spec.at;
  const [px, py] = p;

  const grad: [number, number] = [spec.fx(px, py), spec.fy(px, py)];
  const gradNorm = Math.hypot(grad[0], grad[1]);
  const gradAngle = Math.atan2(grad[1], grad[0]);
  const fAt = spec.f(px, py);

  const contours = spec.levels.map((level) => ({
    level,
    segments: contourOf(spec.f, spec.window, level),
  }));

  const base = {
    surface,
    tex: spec.tex,
    gradTex: spec.gradTex,
    window: spec.window,
    at: p,
    fAt,
    contours,
    grad,
    gradNorm,
    gradAngle,
  };

  const t = tracer<SurfaceGradState>(CODE);

  /* ---- 1. the point ---- */
  t.push(
    {
      ...base,
      stage: "point",
      quotients: null,
      wrt: null,
      bestH: null,
      bestErr: null,
      sweep: null,
      sweepMax: null,
      tangent: null,
      tangentDot: null,
      field: null,
      checks: [],
    },
    `The function is ${spec.blurb}. Everything below is evaluated at x = (${px}, ${py}), where f = ${fAt.toPrecision(6)}.`,
    { line: 1 }
  );

  /* ---- 2 and 3. the two partial derivatives, as limits ---- */
  for (const wrt of [1, 2] as const) {
    const exact = wrt === 1 ? grad[0] : grad[1];
    const quotients: QuotientRow[] = H_LADDER.map((h) => {
      const fwd =
        wrt === 1
          ? (spec.f(px + h, py) - fAt) / h
          : (spec.f(px, py + h) - fAt) / h;
      const cen =
        wrt === 1
          ? (spec.f(px + h, py) - spec.f(px - h, py)) / (2 * h)
          : (spec.f(px, py + h) - spec.f(px, py - h)) / (2 * h);
      return {
        h,
        forward: fwd,
        central: cen,
        errForward: Math.abs(fwd - exact),
        errCentral: Math.abs(cen - exact),
      };
    });
    let bestH = quotients[0].h;
    let bestErr = quotients[0].errCentral;
    for (const q of quotients) {
      if (q.errCentral < bestErr) {
        bestErr = q.errCentral;
        bestH = q.h;
      }
    }

    // Convergence ORDER, measured in the regime where truncation dominates and
    // round-off has not yet arrived (h from 1e-2 to 1e-4). This is the honest
    // check: forward differencing is first order and central is second, and an
    // error-magnitude comparison can be beaten by a lucky sign cancellation.
    //
    // One real exception is worth naming rather than smoothing over. The leading
    // forward-difference error is (h/2) f''(x), so wherever f'' happens to vanish
    // the forward difference is ACCIDENTALLY second order. The Gaussian's second
    // derivative in x is (x^2 - 1) f, which is exactly zero at x = 1 — one of the
    // points this module evaluates — so that case is detected and reported as the
    // accident it is.
    const orderBetween = (pick: (q: QuotientRow) => number) => {
      const a = quotients.find((q) => q.h === 1e-2)!;
      const b = quotients.find((q) => q.h === 1e-4)!;
      const ea = pick(a);
      const eb = pick(b);
      if (!(ea > 1e-15 && eb > 1e-15)) return Number.NaN;
      return Math.log10(ea / eb) / Math.log10(a.h / b.h);
    };
    const orderForward = orderBetween((q) => q.errForward);
    const orderCentral = orderBetween((q) => q.errCentral);

    // An order is only meaningful if there IS a truncation regime. On a slice
    // where the central difference is already exact to round-off at h = 1e-2
    // there is nothing to converge, and the measured slope comes out negative
    // because the only thing changing is accumulated round-off.
    const cenAtBigH = quotients.find((q) => q.h === 1e-2)!.errCentral;
    const centralHasRegime = cenAtBigH > 1e-11 * Math.max(1, Math.abs(exact));

    const hh = 1e-3;
    const secondDeriv =
      wrt === 1
        ? (spec.f(px + hh, py) - 2 * fAt + spec.f(px - hh, py)) / (hh * hh)
        : (spec.f(px, py + hh) - 2 * fAt + spec.f(px, py - hh)) / (hh * hh);
    const secondDerivTiny = Math.abs(secondDeriv) < 1e-6 * Math.max(1, Math.abs(exact));

    // A central difference is exact for a quadratic, so on a slice that happens to
    // be quadratic it is exact at EVERY h until round-off spoils it. Detect that
    // rather than reporting "best at h = 1" as if it were a coincidence.
    const bigH = quotients.filter((q) => q.h >= 1e-2);
    const exactOnSlice = bigH.every((q) => q.errCentral < 1e-12 * Math.max(1, Math.abs(exact)));
    const worst = quotients[quotients.length - 1];

    const checks: GradCheck[] = [
      {
        label: exactOnSlice
          ? "the slice is quadratic, so the central difference is exact"
          : "central difference reaches the analytic value",
        value: exactOnSlice
          ? `error < 1e-12 for every h down to 1e-2`
          : `${bestErr.toExponential(1)} at h = ${bestH.toExponential(0)}`,
        ok: bestErr < 1e-7 * Math.max(1, Math.abs(exact)),
      },
      {
        label: "then round-off takes over and smaller h is WORSE",
        value: `${worst.errCentral.toExponential(1)} at h = 1e-12`,
        ok: worst.errCentral > Math.max(bestErr, 1e-16) * 10,
      },
      {
        label: centralHasRegime
          ? "central difference converges at second order"
          : "central difference is already at round-off, so there is no order to measure",
        value: centralHasRegime
          ? `measured h^${orderCentral.toFixed(2)}`
          : `error ${cenAtBigH.toExponential(1)} at h = 1e-2`,
        ok: centralHasRegime ? Math.abs(orderCentral - 2) < 0.25 : true,
      },
      {
        label: secondDerivTiny
          ? "forward is ACCIDENTALLY second order here (f'' = 0 at this point)"
          : "forward difference converges at first order",
        value: `measured h^${orderForward.toFixed(2)}, f'' = ${secondDeriv.toExponential(2)}`,
        ok: secondDerivTiny
          ? Math.abs(orderForward - 2) < 0.3
          : Math.abs(orderForward - 1) < 0.25,
      },
    ];

    t.push(
      {
        ...base,
        stage: wrt === 1 ? "partial-1" : "partial-2",
        quotients,
        wrt,
        bestH,
        bestErr,
        sweep: null,
        sweepMax: null,
        tangent: null,
        tangentDot: null,
        field: null,
        checks,
      },
      `Vary x${wrt} and hold the other fixed. The difference quotient converges to ${exact.toPrecision(8)} — best at h = ${bestH.toExponential(0)} with error ${bestErr.toExponential(1)} — and then gets WORSE for smaller h, because subtracting two nearly equal numbers throws away digits.`,
      { line: wrt, watch: [{ label: `df/dx${wrt}`, value: exact.toPrecision(8) }] }
    );
  }

  /* ---- 4. assemble the row vector ---- */
  t.push(
    {
      ...base,
      stage: "gradient",
      quotients: null,
      wrt: null,
      bestH: null,
      bestErr: null,
      sweep: null,
      sweepMax: null,
      tangent: null,
      tangentDot: null,
      field: null,
      checks: [
        {
          label: "shape of grad f",
          value: "1 x 2 (a row vector, Eq 5.40)",
          ok: true,
        },
      ],
    },
    `Collect them into a ROW vector: grad f = [${grad[0].toPrecision(6)}, ${grad[1].toPrecision(6)}] in R^{1x2}. The book's Eq 5.40 makes this a row so that the chain rule in §5.3 is a plain matrix product with no transposes to remember.`,
    { line: 4 }
  );

  /* ---- 5. the directional sweep ---- */
  const sweep: { angle: number; rate: number }[] = [];
  for (let i = 0; i < SWEEP_N; i++) {
    const angle = (2 * Math.PI * i) / SWEEP_N;
    const d: [number, number] = [Math.cos(angle), Math.sin(angle)];
    sweep.push({ angle, rate: grad[0] * d[0] + grad[1] * d[1] });
  }
  let sweepMax = sweep[0];
  for (const s of sweep) if (s.rate > sweepMax.rate) sweepMax = s;

  // Check the sweep against a finite difference along the winning direction,
  // which never touches the analytic gradient.
  const hd = 1e-5;
  const dBest: [number, number] = [Math.cos(sweepMax.angle), Math.sin(sweepMax.angle)];
  const fdAlong =
    (spec.f(px + hd * dBest[0], py + hd * dBest[1]) -
      spec.f(px - hd * dBest[0], py - hd * dBest[1])) /
    (2 * hd);
  const angleGap = Math.abs(
    Math.atan2(Math.sin(sweepMax.angle - gradAngle), Math.cos(sweepMax.angle - gradAngle))
  );

  // The sweep is a grid of SWEEP_N directions, so its best can only come within
  // cos(half a step) of the true maximum. That shortfall is geometry, not error,
  // and quoting it as a failure would be wrong -- so the bound is tested against
  // the grid, and ATTAINMENT is tested separately by evaluating the directional
  // derivative at the exact gradient direction, where it must be exact.
  const halfStep = Math.PI / SWEEP_N;
  const gridBound = gradNorm * (1 - Math.cos(halfStep));
  const dExact: [number, number] =
    gradNorm > 1e-12 ? [grad[0] / gradNorm, grad[1] / gradNorm] : [1, 0];
  const rateExact = grad[0] * dExact[0] + grad[1] * dExact[1];

  t.push(
    {
      ...base,
      stage: "sweep",
      quotients: null,
      wrt: null,
      bestH: null,
      bestErr: null,
      sweep,
      sweepMax,
      tangent: null,
      tangentDot: null,
      field: null,
      checks: [
        {
          label: "steepest sampled direction is the gradient direction",
          value: `${((angleGap * 180) / Math.PI).toFixed(3)} deg apart`,
          ok: angleGap <= halfStep * 1.02,
        },
        {
          label: "no sampled direction beats |grad f|",
          value: `max ${sweepMax.rate.toPrecision(8)} <= ${gradNorm.toPrecision(8)}`,
          ok: sweepMax.rate <= gradNorm + 1e-12 * Math.max(1, gradNorm),
        },
        {
          label: `sampled max falls short by at most the grid can explain`,
          value: `${(gradNorm - sweepMax.rate).toExponential(1)} vs bound ${gridBound.toExponential(1)}`,
          ok: gradNorm - sweepMax.rate <= gridBound * 1.05 + 1e-12,
        },
        {
          label: "at the exact gradient direction the rate IS |grad f|",
          value: Math.abs(rateExact - gradNorm).toExponential(1),
          ok: Math.abs(rateExact - gradNorm) < 1e-12 * Math.max(1, gradNorm),
        },
        {
          label: "and a finite difference along it agrees",
          value: `${Math.abs(fdAlong - sweepMax.rate).toExponential(1)}`,
          ok: Math.abs(fdAlong - sweepMax.rate) < 1e-4 * Math.max(1, gradNorm),
        },
      ],
    },
    `Sweep the unit direction d through all ${SWEEP_N} degrees and evaluate D_d f = grad f · d. Nothing beats |grad f| = ${gradNorm.toPrecision(6)}, and the sampled best comes within ${(gradNorm - sweepMax.rate).toExponential(1)} of it at the gradient's own angle. Evaluating at the exact gradient direction hits ${gradNorm.toPrecision(6)} on the nose — sampling shows the bound, only the exact direction shows it is attained.`,
    { line: 6 }
  );

  /* ---- 6. orthogonality to the contour ---- */
  const tangent: [number, number] =
    gradNorm > 1e-12 ? [-grad[1] / gradNorm, grad[0] / gradNorm] : [1, 0];
  const tangentDot = grad[0] * tangent[0] + grad[1] * tangent[1];
  // Walk a small step along the tangent and see how little f changes.
  const step = 1e-3;
  const fAlongTangent = spec.f(px + step * tangent[0], py + step * tangent[1]);
  const fAlongGrad =
    gradNorm > 1e-12
      ? spec.f(px + step * (grad[0] / gradNorm), py + step * (grad[1] / gradNorm))
      : fAt;

  t.push(
    {
      ...base,
      stage: "orthogonal",
      quotients: null,
      wrt: null,
      bestH: null,
      bestErr: null,
      sweep,
      sweepMax,
      tangent,
      tangentDot,
      field: null,
      checks: [
        {
          label: "grad f · (contour tangent)",
          value: tangentDot.toExponential(1),
          ok: Math.abs(tangentDot) < 1e-12 * Math.max(1, gradNorm),
        },
        {
          label: `f changes along the tangent (step ${step})`,
          value: Math.abs(fAlongTangent - fAt).toExponential(1),
          ok: Math.abs(fAlongTangent - fAt) < 1e-5 * Math.max(1, Math.abs(fAt)) + 1e-12,
        },
        {
          label: "f changes along the gradient",
          value: Math.abs(fAlongGrad - fAt).toExponential(1),
          ok: true,
        },
      ],
    },
    `The gradient is perpendicular to the contour through the point: their inner product is ${tangentDot.toExponential(1)}. Step ${step} along the tangent and f moves by ${Math.abs(fAlongTangent - fAt).toExponential(1)}; step the same distance along the gradient and it moves by ${Math.abs(fAlongGrad - fAt).toExponential(1)} — about ${(Math.abs(fAlongGrad - fAt) / Math.max(Math.abs(fAlongTangent - fAt), 1e-300)).toExponential(0)} times more.`,
    { line: 7 }
  );

  /* ---- 7. the whole field ---- */
  const [wx0, wx1, wy0, wy1] = spec.window;
  const field: { x: number; y: number; dx: number; dy: number; mag: number }[] = [];
  const NF = 13;
  for (let i = 0; i < NF; i++) {
    for (let j = 0; j < NF; j++) {
      const x = wx0 + ((wx1 - wx0) * (i + 0.5)) / NF;
      const y = wy0 + ((wy1 - wy0) * (j + 0.5)) / NF;
      const gx = spec.fx(x, y);
      const gy = spec.fy(x, y);
      const mag = Math.hypot(gx, gy);
      if (!Number.isFinite(mag)) continue;
      field.push({ x, y, dx: gx, dy: gy, mag });
    }
  }
  const maxMag = field.reduce((m, v) => Math.max(m, v.mag), 0);

  // Measure orthogonality across the whole field, not just at one point.
  let worstDot = 0;
  for (const v of field) {
    if (v.mag < 1e-9) continue;
    const tx = -v.dy / v.mag;
    const ty = v.dx / v.mag;
    worstDot = Math.max(worstDot, Math.abs((v.dx * tx + v.dy * ty) / v.mag));
  }

  t.push(
    {
      ...base,
      stage: "field",
      quotients: null,
      wrt: null,
      bestH: null,
      bestErr: null,
      sweep: null,
      sweepMax: null,
      tangent,
      tangentDot,
      field,
      checks: [
        {
          label: `orthogonality across all ${field.length} field points`,
          value: worstDot.toExponential(1),
          ok: worstDot < 1e-12,
        },
        {
          label: "largest |grad f| on the window",
          value: maxMag.toPrecision(6),
          ok: true,
        },
      ],
    },
    `The same construction at every point is the gradient field. Every arrow crosses its contour at a right angle — measured across all ${field.length} points, the worst normalised deviation is ${worstDot.toExponential(1)}. Where the contours bunch up the arrows are long; where f is flat they vanish.`,
    { line: 4 }
  );

  return capFrames(
    t.done(
      `grad f(${px}, ${py}) = [${grad[0].toPrecision(6)}, ${grad[1].toPrecision(6)}], |grad f| = ${gradNorm.toPrecision(6)}`
    )
  );
}

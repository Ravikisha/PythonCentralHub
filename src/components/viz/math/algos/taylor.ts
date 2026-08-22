/**
 * algos/taylor.ts — Taylor polynomials, one degree per frame.
 *
 * §5.1.1 defines the Taylor polynomial of degree n as
 *
 *     T_n(x) = sum_{k=0}^{n} f^(k)(x0) / k! * (x - x0)^k        (Eq 5.7)
 *
 * and §5.8 lifts it to several variables. The interesting thing about a Taylor
 * expansion is *sequential* — each degree buys a specific amount of accuracy and
 * buys it in a specific place — so it belongs in a stepper rather than a slider:
 * "the frame where T_2 stops being symmetric", "the frame where a degree-4
 * polynomial becomes exact and every later term is zero".
 *
 * ## Why jet arithmetic rather than finite differences
 *
 * The coefficients f^(k)(x0)/k! could be estimated by repeated finite
 * differencing, and that would be a bad idea: the k-th difference of a smooth
 * function loses about k*8 digits, so by k = 5 there is nothing left. Instead
 * this module carries a **truncated Taylor series** (a "jet") through every
 * elementary operation using the standard recurrences. Each recurrence is exact
 * in exact arithmetic, so the coefficients come out to machine precision at every
 * order, and the composition rules are just the chain rule written once.
 *
 * That also makes the module a small forward-mode automatic differentiator, which
 * is the connection §5.6 draws explicitly: forward-mode AD *is* jet arithmetic
 * truncated at order 1.
 *
 * Determinism: no randomness anywhere. Every sample point is on a fixed grid.
 */
import { tracer, capFrames, type Trace } from "../../frames";

/* ------------------------------------------------------------------ jets --- */

/**
 * A jet is the coefficient list [a0, a1, ..., aN] of a truncated series
 * sum a_k * (x - x0)^k. So a_k is f^(k)(x0)/k!, NOT f^(k)(x0).
 */
export type Jet = number[];

const N_DEFAULT = 9;

function jetConst(c: number, n: number): Jet {
  const out = new Array<number>(n + 1).fill(0);
  out[0] = c;
  return out;
}

/** The identity function x, expanded about x0: x = x0 + 1*(x - x0). */
function jetVar(x0: number, n: number): Jet {
  const out = new Array<number>(n + 1).fill(0);
  out[0] = x0;
  if (n >= 1) out[1] = 1;
  return out;
}

function jAdd(a: Jet, b: Jet): Jet {
  return a.map((v, i) => v + b[i]);
}

function jSub(a: Jet, b: Jet): Jet {
  return a.map((v, i) => v - b[i]);
}

function jScale(a: Jet, s: number): Jet {
  return a.map((v) => v * s);
}

/** Cauchy product: the coefficient rule for a product of two series. */
function jMul(a: Jet, b: Jet): Jet {
  const n = a.length - 1;
  const out = new Array<number>(n + 1).fill(0);
  for (let k = 0; k <= n; k++) {
    let s = 0;
    for (let j = 0; j <= k; j++) s += a[j] * b[k - j];
    out[k] = s;
  }
  return out;
}

/** w = a / b, from b*w = a solved one coefficient at a time. */
function jDiv(a: Jet, b: Jet): Jet {
  const n = a.length - 1;
  const out = new Array<number>(n + 1).fill(0);
  out[0] = a[0] / b[0];
  for (let k = 1; k <= n; k++) {
    let s = a[k];
    for (let j = 1; j <= k; j++) s -= b[j] * out[k - j];
    out[k] = s / b[0];
  }
  return out;
}

/** w = exp(u):  k*w_k = sum_{j=1..k} j*u_j*w_{k-j}. */
function jExp(u: Jet): Jet {
  const n = u.length - 1;
  const out = new Array<number>(n + 1).fill(0);
  out[0] = Math.exp(u[0]);
  for (let k = 1; k <= n; k++) {
    let s = 0;
    for (let j = 1; j <= k; j++) s += j * u[j] * out[k - j];
    out[k] = s / k;
  }
  return out;
}

/** w = log(u):  u_k = w_k*u_0 + (1/k) sum_{j=1..k-1} j*w_j*u_{k-j}. */
function jLog(u: Jet): Jet {
  const n = u.length - 1;
  const out = new Array<number>(n + 1).fill(0);
  out[0] = Math.log(u[0]);
  for (let k = 1; k <= n; k++) {
    let s = 0;
    for (let j = 1; j <= k - 1; j++) s += j * out[j] * u[k - j];
    out[k] = (u[k] - s / k) / u[0];
  }
  return out;
}

/** sin and cos share one recurrence, so they are computed as a pair. */
function jSinCos(u: Jet): { sin: Jet; cos: Jet } {
  const n = u.length - 1;
  const s = new Array<number>(n + 1).fill(0);
  const c = new Array<number>(n + 1).fill(0);
  s[0] = Math.sin(u[0]);
  c[0] = Math.cos(u[0]);
  for (let k = 1; k <= n; k++) {
    let ss = 0;
    let cc = 0;
    for (let j = 1; j <= k; j++) {
      ss += j * u[j] * c[k - j];
      cc += j * u[j] * s[k - j];
    }
    s[k] = ss / k;
    c[k] = -cc / k;
  }
  return { sin: s, cos: c };
}

/** w = u^p:  k*u_0*w_k = sum_{j=1..k} (p*j - (k-j)) * u_j * w_{k-j}. */
function jPow(u: Jet, p: number): Jet {
  const n = u.length - 1;
  const out = new Array<number>(n + 1).fill(0);
  out[0] = Math.pow(u[0], p);
  for (let k = 1; k <= n; k++) {
    let s = 0;
    for (let j = 1; j <= k; j++) s += (p * j - (k - j)) * u[j] * out[k - j];
    out[k] = s / (k * u[0]);
  }
  return out;
}

/** Evaluate a truncated series at x, keeping only the first n+1 terms. */
export function jetAt(coeffs: Jet, x0: number, x: number, upto: number): number {
  let acc = 0;
  const d = x - x0;
  let pw = 1;
  for (let k = 0; k <= upto && k < coeffs.length; k++) {
    acc += coeffs[k] * pw;
    pw *= d;
  }
  return acc;
}

/* -------------------------------------------------------------- functions --- */

export type FnName =
  | "sin-plus-cos"
  | "x-to-the-fourth"
  | "sigmoid"
  | "log1p"
  | "gaussian-bump";

interface Univariate {
  name: FnName;
  /** As the book writes it. */
  tex: string;
  blurb: string;
  /** Exact value, for the reference curve and the error measurement. */
  f: (x: number) => number;
  /** Taylor coefficients about x0, to order n, by jet arithmetic. */
  jet: (x0: number, n: number) => Jet;
  x0: number;
  window: [number, number];
  /** Non-null when f is a polynomial: the degree at which T_n becomes exact. */
  exactAt: number | null;
  book: string;
}

const FNS: Record<FnName, Univariate> = {
  "sin-plus-cos": {
    name: "sin-plus-cos",
    tex: "f(x) = \\sin(x) + \\cos(x)",
    blurb:
      "the book's Example 5.4 and Exercise 5.4. Its derivatives cycle with period four, so the coefficients read +1, +1, -1, -1 and repeat",
    f: (x) => Math.sin(x) + Math.cos(x),
    jet: (x0, n) => {
      const { sin, cos } = jSinCos(jetVar(x0, n));
      return jAdd(sin, cos);
    },
    x0: 0,
    window: [-4, 4],
    exactAt: null,
    book: "Example 5.4, Exercise 5.4",
  },
  "x-to-the-fourth": {
    name: "x-to-the-fourth",
    tex: "f(x) = x^4",
    blurb:
      "the book's Example 5.3, expanded at x0 = 1. A polynomial of degree 4, so T_4 is not an approximation of f — it IS f, and every coefficient past the fourth is exactly zero",
    f: (x) => x * x * x * x,
    jet: (x0, n) => {
      const x = jetVar(x0, n);
      return jMul(jMul(x, x), jMul(x, x));
    },
    x0: 1,
    window: [-0.6, 2.6],
    exactAt: 4,
    book: "Example 5.3",
  },
  sigmoid: {
    name: "sigmoid",
    tex: "f(x) = \\dfrac{1}{1 + \\exp(-x)}",
    blurb:
      "the logistic sigmoid of Exercise 5.2. Odd symmetry about x0 = 0 makes every even coefficient past the constant vanish, so the polynomials go up in steps of two",
    f: (x) => 1 / (1 + Math.exp(-x)),
    jet: (x0, n) => {
      const x = jetVar(x0, n);
      const denom = jAdd(jetConst(1, n), jExp(jScale(x, -1)));
      return jDiv(jetConst(1, n), denom);
    },
    x0: 0,
    window: [-6, 6],
    exactAt: null,
    book: "Exercise 5.2",
  },
  log1p: {
    name: "log1p",
    tex: "f(x) = \\log(1 + x)",
    blurb:
      "the inner function of Exercise 5.7a. Its coefficients are (-1)^(k+1)/k, and its series only converges for |x| < 1 — the first function here whose Taylor series has a boundary",
    f: (x) => Math.log(1 + x),
    jet: (x0, n) => jLog(jAdd(jetConst(1, n), jetVar(x0, n))),
    x0: 0,
    window: [-0.9, 2.4],
    exactAt: null,
    book: "Exercise 5.7a",
  },
  "gaussian-bump": {
    name: "gaussian-bump",
    tex: "f(x) = \\exp\\!\\left(-\\tfrac{1}{2}x^2\\right)",
    blurb:
      "the unnormalised Gaussian of Exercise 5.3 with mu = 0 and sigma = 1. Its Taylor series converges everywhere but converges slowly far from the centre, which is exactly the failure mode a Laplace approximation runs into",
    f: (x) => Math.exp(-0.5 * x * x),
    jet: (x0, n) => {
      const x = jetVar(x0, n);
      return jExp(jScale(jMul(x, x), -0.5));
    },
    x0: 0,
    window: [-4, 4],
    exactAt: null,
    book: "Exercise 5.3",
  },
};

export const TAYLOR_FNS = Object.keys(FNS) as FnName[];

/* ------------------------------------------------------------------ state --- */

export interface TaylorCheck {
  label: string;
  value: string;
  ok: boolean;
}

export interface TaylorState {
  fn: FnName;
  tex: string;
  x0: number;
  window: [number, number];
  /** Current degree of the polynomial being shown. */
  degree: number;
  maxDegree: number;
  /** All coefficients computed, so the panel can show the ones not yet used. */
  coeffs: number[];
  /** f^(k)(x0), reconstructed from the coefficients: a_k * k!. */
  derivs: number[];
  /** T_n as the book writes it. */
  polyText: string;
  /** Samples of f and of T_n on a shared grid. */
  xs: number[];
  fs: number[];
  ts: number[];
  /** Largest |f - T_n| over the window, and where it happens. */
  maxErr: number;
  maxErrAt: number;
  /** Same, restricted to a tight neighbourhood of x0. */
  nearErr: number;
  nearHalfWidth: number;
  /** Ratio of this degree's NEAR error to the previous degree's. */
  errRatio: number | null;
  /** True when the window error grew: the series is diverging out there. */
  divergesOnWindow: boolean;
  /** The degree of the next nonzero coefficient, which sets the local order. */
  localOrder: number;
  exact: boolean;
  checks: TaylorCheck[];
}

const CODE = [
  "T_n(x) = sum_{k=0}^{n} f^(k)(x0)/k! * (x - x0)^k      # Eq 5.7",
  "",
  "coeffs = jet(f, x0, N)          # a_k = f^(k)(x0)/k!, by jet arithmetic",
  "for n in 0..N:",
  "    T_n = lambda x: sum(coeffs[k] * (x - x0)**k for k in range(n + 1))",
  "    err = max(abs(f(x) - T_n(x)) for x in window)",
];

const N_SAMPLES = 241;

function fmtCoeff(v: number): string {
  if (Math.abs(v) < 5e-13) return "0";
  const r = Math.round(v);
  if (Math.abs(v - r) < 1e-12) return String(r);
  return v.toFixed(6).replace(/0+$/, "").replace(/\.$/, "");
}

function polyText(coeffs: number[], x0: number, upto: number): string {
  const parts: string[] = [];
  for (let k = 0; k <= upto; k++) {
    const c = coeffs[k];
    if (Math.abs(c) < 5e-13) continue;
    const mag = fmtCoeff(Math.abs(c));
    const sign = c < 0 ? "-" : parts.length ? "+" : "";
    const base =
      x0 === 0 ? "x" : x0 > 0 ? `(x - ${fmtCoeff(x0)})` : `(x + ${fmtCoeff(-x0)})`;
    const pow = k === 0 ? "" : k === 1 ? base : `${base}^${k}`;
    const coef = k === 0 || mag !== "1" ? mag : "";
    const body = coef && pow ? `${coef}${pow}` : coef || pow;
    parts.push(`${sign}${sign ? " " : ""}${body}`);
  }
  return parts.length ? parts.join(" ") : "0";
}

export interface TaylorInput {
  fn?: FnName;
  /** Highest degree to walk to. Clamped to the jet length. */
  maxDegree?: number;
  /** Override the function's own expansion point. */
  x0?: number;
}

export function taylor({
  fn = "sin-plus-cos",
  maxDegree = 5,
  x0,
}: TaylorInput = {}): Trace<TaylorState> {
  const spec = FNS[fn];
  const centre = x0 ?? spec.x0;
  const N = Math.min(Math.max(maxDegree, 0), N_DEFAULT);
  const coeffs = spec.jet(centre, N_DEFAULT);

  // f^(k)(x0) = a_k * k!, which is the form the book's Eq 5.7 is written in.
  const derivs: number[] = [];
  let fact = 1;
  for (let k = 0; k <= N_DEFAULT; k++) {
    if (k > 0) fact *= k;
    derivs.push(coeffs[k] * fact);
  }

  const [lo, hi] = spec.window;
  const xs: number[] = [];
  const fs: number[] = [];
  for (let i = 0; i < N_SAMPLES; i++) {
    const x = lo + ((hi - lo) * i) / (N_SAMPLES - 1);
    xs.push(x);
    fs.push(spec.f(x));
  }
  const nearHalfWidth = Math.min(0.5, (hi - lo) / 12);

  const t = tracer<TaylorState>(CODE);
  let prevErr: number | null = null;
  let prevNear: number | null = null;

  for (let n = 0; n <= N; n++) {
    const ts = xs.map((x) => jetAt(coeffs, centre, x, n));

    let maxErr = 0;
    let maxErrAt = centre;
    let nearErr = 0;
    for (let i = 0; i < xs.length; i++) {
      const e = Math.abs(fs[i] - ts[i]);
      if (e > maxErr) {
        maxErr = e;
        maxErrAt = xs[i];
      }
      if (Math.abs(xs[i] - centre) <= nearHalfWidth) nearErr = Math.max(nearErr, e);
    }

    const exact = spec.exactAt !== null && n >= spec.exactAt;
    const errRatio = prevNear !== null && prevNear > 0 ? nearErr / prevNear : null;
    const divergesOnWindow = prevErr !== null && maxErr > prevErr * 1.000001;

    // The first nonzero coefficient strictly past degree n sets the local order.
    let localOrder = n + 1;
    for (let k = n + 1; k <= N_DEFAULT; k++) {
      if (Math.abs(coeffs[k]) > 5e-13) {
        localOrder = k;
        break;
      }
    }

    // Two checks per frame, both independent of the construction.
    const valueAtCentre = Math.abs(jetAt(coeffs, centre, centre, n) - spec.f(centre));
    const checks: TaylorCheck[] = [
      {
        label: "T_n(x0) = f(x0)",
        value: valueAtCentre.toExponential(1),
        ok: valueAtCentre < 1e-12,
      },
    ];
    if (n >= 1) {
      // The local error is governed by the FIRST NONZERO discarded term, not by
      // n + 1. For an odd or even function half the coefficients vanish, so the
      // order jumps in twos: T_1 of the sigmoid is already accurate to h^3
      // because the h^2 term is exactly zero. Predicting n + 1 here would be
      // wrong for three of the five functions on this page.
      const h = 1e-2;
      const eh = Math.abs(spec.f(centre + h) - jetAt(coeffs, centre, centre + h, n));
      const e2h = Math.abs(spec.f(centre + 2 * h) - jetAt(coeffs, centre, centre + 2 * h, n));
      const order = eh > 1e-15 && e2h > 1e-15 ? Math.log2(e2h / eh) : Number.NaN;
      checks.push({
        label: `error near x0 scales as h^${localOrder}`,
        value: Number.isFinite(order) ? `measured h^${order.toFixed(2)}` : "exact",
        ok: !Number.isFinite(order) || Math.abs(order - localOrder) < 0.35,
      });
    }
    if (spec.exactAt !== null) {
      checks.push({
        label: `coefficients past degree ${spec.exactAt}`,
        value: coeffs
          .slice(spec.exactAt + 1, spec.exactAt + 4)
          .every((c) => Math.abs(c) < 5e-13)
          ? "all zero"
          : "nonzero",
        ok: coeffs.slice(spec.exactAt + 1, spec.exactAt + 4).every((c) => Math.abs(c) < 5e-13),
      });
    }

    const near = `error within ±${nearHalfWidth} of x0 is ${nearErr.toExponential(2)}`;
    const caption =
      n === 0
        ? `Degree 0: T_0 is the constant f(x0) = ${fmtCoeff(coeffs[0])} — a horizontal line touching f at exactly one point. ${near}.`
        : exact && n === spec.exactAt
          ? `Degree ${n}: f is a polynomial of degree ${spec.exactAt}, so T_${n} is not an approximation — it reproduces f exactly, and the largest error over the WHOLE window is ${maxErr.toExponential(1)}, machine noise.`
          : exact
            ? `Degree ${n}: the new coefficient is exactly zero, so nothing changes. A Taylor polynomial cannot improve on an exact representation.`
            : Math.abs(coeffs[n]) < 5e-13
              ? `Degree ${n}: the coefficient of (x − x0)^${n} is exactly zero, so T_${n} equals T_${n - 1}. ${near}, unchanged.`
              : `Degree ${n}: adding ${fmtCoeff(coeffs[n])}·(x − x0)^${n}. ${near}${errRatio !== null && errRatio < 1 ? `, a factor of ${(1 / errRatio).toFixed(1)} better than degree ${n - 1}` : ""}${divergesOnWindow ? ` — but the error at the EDGE of the window grew to ${maxErr.toPrecision(3)}. A Taylor polynomial buys accuracy near x0 by giving it up far away.` : "."}`;

    t.push(
      {
        fn,
        tex: spec.tex,
        x0: centre,
        window: spec.window,
        degree: n,
        maxDegree: N,
        coeffs: coeffs.slice(0, N_DEFAULT + 1),
        derivs,
        polyText: polyText(coeffs, centre, n),
        xs,
        fs,
        ts,
        maxErr,
        maxErrAt,
        nearErr,
        nearHalfWidth,
        errRatio,
        divergesOnWindow,
        localOrder,
        exact,
        checks,
      },
      caption,
      {
        line: 5,
        watch: [
          { label: "degree", value: String(n) },
          { label: `|f − T_n| near x0`, value: nearErr.toExponential(2) },
          { label: "on the whole window", value: maxErr.toPrecision(4) },
        ],
      }
    );

    prevErr = maxErr;
    prevNear = nearErr;
  }

  const last = t.frames[t.frames.length - 1].state;
  return capFrames(
    t.done(
      `T_${N}: error ${last.nearErr.toExponential(2)} near x0, ${last.maxErr.toPrecision(3)} on [${spec.window[0]}, ${spec.window[1]}]`
    )
  );
}

/* ------------------------------------------------- exported for the tests --- */

export const _jets = { jetConst, jetVar, jAdd, jSub, jScale, jMul, jDiv, jExp, jLog, jSinCos, jPow };

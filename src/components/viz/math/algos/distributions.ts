/**
 * algos/distributions.ts — densities, mass functions, and what conditioning a
 * Gaussian actually does.
 *
 * Three generators, because Chapter 6 asks three different questions and they
 * do not share a frame shape:
 *
 *   `gaussianSweep`        — one frame per parameter value. Answers "what does
 *                            σ control?" and, in the same picture, "why is the
 *                            cdf the thing you read probabilities off, not the
 *                            pdf?"
 *   `discreteMass`         — one frame per outcome, accumulating the cdf as a
 *                            staircase. Answers "why is a pmf value a
 *                            probability but a pdf value is not?"
 *   `gaussianConditioning` — joint, then each marginal, then a conditional
 *                            slice. This is §6.5's central result, and it is the
 *                            one every reader gets wrong first: conditioning
 *                            shrinks the variance, marginalising does not.
 *
 * All curves are sampled into the frame state, so the stage renderer stays a
 * pure function of one frame and no maths happens during render.
 */
import { tracer, capFrames, type Trace } from "../../frames";

const SAMPLES = 160;

/* -------------------------------------------------------------------------- */
/* Numerics                                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Abramowitz & Stegun 7.1.26. Max absolute error 1.5e-7, which is four orders
 * of magnitude finer than a 600-pixel-wide plot can show — and the alternative
 * is a dependency, which this directory does not take.
 */
function erf(x: number): number {
  const sign = x < 0 ? -1 : 1;
  const z = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * z);
  const y =
    1 -
    ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t +
      0.254829592) *
      t *
      Math.exp(-z * z);
  return sign * y;
}

const normPdf = (x: number, mu: number, sd: number) =>
  Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI));

const normCdf = (x: number, mu: number, sd: number) =>
  0.5 * (1 + erf((x - mu) / (sd * Math.SQRT2)));

const linspace = (a: number, b: number, n: number) =>
  Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1));

const fmt = (v: number, d = 2) => v.toFixed(d).replace(/\.?0+$/, "") || "0";

/* -------------------------------------------------------------------------- */
/* State                                                                       */
/* -------------------------------------------------------------------------- */

export interface CurveState {
  kind: "curve";
  xs: number[];
  /** Density, sampled at `xs`. */
  pdf: number[];
  /** Cumulative distribution, sampled at `xs`. Drawn on its own axis. */
  cdf: number[];
  /** Every earlier frame's density, drawn faint so the sweep leaves a trail. */
  ghosts: number[][];
  /** Shaded interval, when the frame is making a point about an area. */
  shade: { from: number; to: number; mass: number } | null;
  params: { label: string; value: string }[];
  /** Vertical marker, e.g. at the mean. */
  markers: { at: number; label: string }[];
}

export interface BarsState {
  kind: "bars";
  bars: { label: string; p: number; cum: number; revealed: boolean }[];
  /** Index of the outcome this frame added, or null on the summary frames. */
  at: number | null;
  params: { label: string; value: string }[];
}

export interface JointState {
  kind: "joint";
  mu: [number, number];
  cov: [[number, number], [number, number]];
  /** Contour levels as multiples of the standard deviation, for the stage. */
  levels: number[];
  /** Marginal densities, sampled, once the frame reveals them. */
  marginalX: { xs: number[]; pdf: number[] } | null;
  marginalY: { xs: number[]; pdf: number[] } | null;
  /** The conditioning slice: the value of x₁ being conditioned on. */
  slice: number | null;
  /** The resulting conditional density of x₂ given that slice. */
  conditional: { xs: number[]; pdf: number[]; mu: number; sd: number } | null;
  params: { label: string; value: string }[];
}

export type DistState = CurveState | BarsState | JointState;

/* -------------------------------------------------------------------------- */
/* 1. Parameter sweep over a univariate Gaussian                               */
/* -------------------------------------------------------------------------- */

export interface SweepInput {
  /** Which parameter moves. The other is held fixed. */
  sweep: "mean" | "sd";
  /** Values the swept parameter takes, one frame each. */
  values: number[];
  /** Held-fixed value of the other parameter. */
  fixed?: number;
  /** Domain of the plot. Defaults to ±4 around the widest case. */
  domain?: [number, number];
  /** Shade this interval on every frame and report its mass. */
  interval?: [number, number];
}

const SWEEP_CODE = [
  "p(x) = 1/(sigma*sqrt(2*pi)) * exp(-0.5*((x-mu)/sigma)**2)",
  "F(x) = integral of p from -inf to x       # the cdf",
  "P(a <= X <= b) = F(b) - F(a)              # an AREA, never a pdf value",
];

export function gaussianSweep({
  sweep,
  values,
  fixed = sweep === "sd" ? 0 : 1,
  domain,
  interval,
}: SweepInput): Trace<CurveState> {
  const widest = sweep === "sd" ? Math.max(...values) : fixed;
  const centre = sweep === "mean" ? (Math.min(...values) + Math.max(...values)) / 2 : fixed;
  const span = domain ?? [centre - 4 * widest - 1, centre + 4 * widest + 1];
  const xs = linspace(span[0], span[1], SAMPLES);

  const t = tracer<CurveState>(SWEEP_CODE);
  const ghosts: number[][] = [];

  values.forEach((v, i) => {
    const mu = sweep === "mean" ? v : fixed;
    const sd = sweep === "sd" ? v : fixed;
    const pdf = xs.map((x) => normPdf(x, mu, sd));
    const cdf = xs.map((x) => normCdf(x, mu, sd));

    const shade = interval
      ? {
          from: interval[0],
          to: interval[1],
          mass: normCdf(interval[1], mu, sd) - normCdf(interval[0], mu, sd),
        }
      : null;

    const caption =
      sweep === "sd"
        ? i === 0
          ? `σ = ${fmt(sd)}. The curve integrates to 1, so a narrow σ has to buy its narrowness with height — the peak is ${fmt(normPdf(mu, mu, sd))}, which is above 1 and therefore cannot be a probability.`
          : `σ = ${fmt(sd)}. Wider, so flatter: the area is still exactly 1. The cdf on the right tells the same story as a gentler climb.`
        : i === 0
          ? `μ = ${fmt(mu)}. Moving the mean slides the whole shape without changing it — μ is a location parameter, σ is a scale parameter.`
          : `μ = ${fmt(mu)}. Same curve, new position. The cdf shifts with it; its S-shape is unchanged.`;

    t.push(
      {
        kind: "curve",
        xs,
        pdf,
        cdf,
        ghosts: ghosts.map((g) => [...g]),
        shade,
        markers: [{ at: mu, label: "mu" }],
        params: [
          { label: "mu", value: fmt(mu) },
          { label: "sigma", value: fmt(sd) },
          { label: "peak density", value: fmt(normPdf(mu, mu, sd), 3) },
        ],
      },
      caption,
      {
        line: shade ? 3 : 1,
        phase: sweep === "sd" ? "scale" : "location",
        watch: [
          { label: sweep === "sd" ? "sigma" : "mu", value: fmt(v) },
          ...(shade
            ? [{ label: `P(${fmt(interval![0])} <= X <= ${fmt(interval![1])})`, value: fmt(shade.mass, 3) }]
            : []),
        ],
      },
    );

    ghosts.push(pdf);
  });

  return capFrames(t.done(sweep === "sd" ? "area fixed at 1, height traded for width" : "shape fixed, location moved"));
}

/* -------------------------------------------------------------------------- */
/* 2. Discrete mass, accumulating into a cdf                                   */
/* -------------------------------------------------------------------------- */

export interface MassInput {
  /** Outcome labels, in the order the staircase should build. */
  labels: string[];
  /** Probabilities, one per label. Must sum to 1 within 1e-9. */
  probs: number[];
}

const MASS_CODE = [
  "P(X = x_i) = p_i                 # a pmf value IS a probability",
  "sum_i p_i = 1                    # the mass has to go somewhere",
  "F(x_k) = sum_{i <= k} p_i        # the cdf is a running total",
];

export function discreteMass({ labels, probs }: MassInput): Trace<BarsState> {
  const total = probs.reduce((a, b) => a + b, 0);
  if (Math.abs(total - 1) > 1e-9) {
    // Not an exception: a lab that throws takes the page down. Report it in the
    // trace so the author sees it on the page during authoring.
    const t = tracer<BarsState>(MASS_CODE);
    t.push(
      { kind: "bars", bars: [], at: null, params: [{ label: "sum", value: fmt(total, 4) }] },
      `These probabilities sum to ${fmt(total, 4)}, not 1, so they are not a probability mass function. Fix the input.`,
    );
    return t.done("invalid pmf");
  }

  const t = tracer<BarsState>(MASS_CODE);
  let cum = 0;
  const bars = labels.map((label, i) => ({ label, p: probs[i], cum: 0, revealed: false }));

  t.push(
    {
      kind: "bars",
      bars: bars.map((b) => ({ ...b })),
      at: null,
      params: [{ label: "outcomes", value: String(labels.length) }],
    },
    `${labels.length} outcomes and nothing assigned yet. Unlike a density, each bar here is a probability in its own right — no integration needed.`,
    { line: 1, phase: "setup" },
  );

  labels.forEach((label, i) => {
    cum += probs[i];
    bars[i] = { ...bars[i], cum, revealed: true };
    t.push(
      { kind: "bars", bars: bars.map((b) => ({ ...b })), at: i, params: [
        { label: "this outcome", value: fmt(probs[i], 3) },
        { label: "running total", value: fmt(cum, 3) },
      ] },
      `P(X = ${label}) = ${fmt(probs[i], 3)}. The staircase steps up by exactly that much, so F(${label}) = ${fmt(cum, 3)}.`,
      {
        line: 3,
        phase: "accumulate",
        watch: [
          { label: "F", value: fmt(cum, 3), tone: i === labels.length - 1 ? "good" : "info" },
          { label: "remaining", value: fmt(1 - cum, 3) },
        ],
      },
    );
  });

  t.push(
    { kind: "bars", bars: bars.map((b) => ({ ...b })), at: null, params: [{ label: "F(last)", value: "1" }] },
    "The staircase reaches exactly 1 and stays there. Every cdf does: it is non-decreasing, starts at 0 and ends at 1, whether the variable is discrete or continuous.",
    { line: 2, phase: "accumulate" },
  );

  return capFrames(t.done("mass sums to 1"));
}

/* -------------------------------------------------------------------------- */
/* 3. Marginalising and conditioning a bivariate Gaussian                      */
/* -------------------------------------------------------------------------- */

export interface ConditioningInput {
  mu?: [number, number];
  /** Covariance, row-major. Must be symmetric positive definite. */
  cov?: [[number, number], [number, number]];
  /** The value of x₁ to condition on. */
  slice?: number;
}

const COND_CODE = [
  "p(x1, x2) = N(mu, Sigma)",
  "p(x1) = integral p(x1, x2) dx2            # marginal: sum x2 away",
  "p(x2 | x1) = N(mu2 + s12/s11*(x1-mu1),    # conditional: SHRINKS variance",
  "               s22 - s12**2/s11)",
];

export function gaussianConditioning({
  mu = [0, 0],
  cov = [
    [1, 0.8],
    [0.8, 1],
  ],
  slice = 1.2,
}: ConditioningInput = {}): Trace<JointState> {
  const [[s11, s12], [, s22]] = cov;
  const sd1 = Math.sqrt(s11);
  const sd2 = Math.sqrt(s22);
  const rho = s12 / (sd1 * sd2);

  // The §6.5 conditioning formulas, written out rather than solved numerically.
  const condMu = mu[1] + (s12 / s11) * (slice - mu[0]);
  const condVar = s22 - (s12 * s12) / s11;
  const condSd = Math.sqrt(condVar);

  const xs1 = linspace(mu[0] - 3.4 * sd1, mu[0] + 3.4 * sd1, SAMPLES);
  const xs2 = linspace(mu[1] - 3.4 * sd2, mu[1] + 3.4 * sd2, SAMPLES);

  const levels = [0.5, 1, 1.5, 2];
  const t = tracer<JointState>(COND_CODE);

  const base: JointState = {
    kind: "joint",
    mu,
    cov,
    levels,
    marginalX: null,
    marginalY: null,
    slice: null,
    conditional: null,
    params: [
      { label: "rho", value: fmt(rho) },
      { label: "sd(x2)", value: fmt(sd2, 3) },
    ],
  };

  const watch = (extra: { label: string; value: string | number; tone?: "good" | "info" | "warn" }[] = []) => [
    { label: "rho", value: fmt(rho) },
    ...extra,
  ];

  t.push(
    { ...base },
    `A bivariate Gaussian with correlation ρ = ${fmt(rho)}. The contours are ellipses tilted by the off-diagonal covariance ${fmt(s12)} — that tilt is the correlation, drawn.`,
    { line: 1, phase: "joint", watch: watch() },
  );

  t.push(
    { ...base, marginalX: { xs: xs1, pdf: xs1.map((x) => normPdf(x, mu[0], sd1)) } },
    `Marginalise x₂ away by integrating over it: p(x₁) = N(${fmt(mu[0])}, ${fmt(s11)}). Marginalising throws information away, and the width you are left with is the *full* spread of x₁ — ${fmt(sd1, 3)}.`,
    { line: 2, phase: "marginal", watch: watch([{ label: "sd(x1)", value: fmt(sd1, 3) }]) },
  );

  t.push(
    {
      ...base,
      marginalX: { xs: xs1, pdf: xs1.map((x) => normPdf(x, mu[0], sd1)) },
      marginalY: { xs: xs2, pdf: xs2.map((x) => normPdf(x, mu[1], sd2)) },
    },
    `The same operation the other way gives p(x₂) = N(${fmt(mu[1])}, ${fmt(s22)}), with spread ${fmt(sd2, 3)}. Both marginals are Gaussian — that closure is what makes the Gaussian so convenient.`,
    { line: 2, phase: "marginal", watch: watch([{ label: "sd(x2)", value: fmt(sd2, 3) }]) },
  );

  t.push(
    {
      ...base,
      marginalX: { xs: xs1, pdf: xs1.map((x) => normPdf(x, mu[0], sd1)) },
      marginalY: { xs: xs2, pdf: xs2.map((x) => normPdf(x, mu[1], sd2)) },
      slice,
    },
    `Now condition instead: fix x₁ = ${fmt(slice)}. That is a vertical slice through the joint density, not an integral over it. The slice is a curve in x₂ — it just is not normalised yet.`,
    { line: 3, phase: "conditional", watch: watch([{ label: "x1", value: fmt(slice) }]) },
  );

  t.push(
    {
      ...base,
      marginalY: { xs: xs2, pdf: xs2.map((x) => normPdf(x, mu[1], sd2)) },
      slice,
      conditional: {
        xs: xs2,
        pdf: xs2.map((x) => normPdf(x, condMu, condSd)),
        mu: condMu,
        sd: condSd,
      },
    },
    `Normalise the slice and it is Gaussian again: p(x₂ | x₁ = ${fmt(slice)}) = N(${fmt(condMu, 3)}, ${fmt(condVar, 3)}). The mean moved — knowing x₁ tells you something about x₂ — and the standard deviation fell from ${fmt(sd2, 3)} to ${fmt(condSd, 3)}.`,
    {
      line: 4,
      phase: "conditional",
      watch: watch([
        { label: "sd marginal", value: fmt(sd2, 3) },
        { label: "sd conditional", value: fmt(condSd, 3), tone: "good" },
      ]),
    },
  );

  const shrink = (1 - condSd / sd2) * 100;
  t.push(
    {
      ...base,
      marginalY: { xs: xs2, pdf: xs2.map((x) => normPdf(x, mu[1], sd2)) },
      slice,
      conditional: {
        xs: xs2,
        pdf: xs2.map((x) => normPdf(x, condMu, condSd)),
        mu: condMu,
        sd: condSd,
      },
    },
    `Side by side: conditioning narrowed the distribution by ${fmt(shrink, 1)}%, and — read the formula — that narrowing does not depend on which value of x₁ you conditioned on. Marginalising never narrows anything. This is the distinction to hold on to.`,
    {
      phase: "conditional",
      watch: watch([{ label: "variance drop", value: `${fmt(shrink, 1)}%`, tone: "good" }]),
    },
  );

  return capFrames(
    t.done(`conditioning cut sd(x2) from ${fmt(sd2, 3)} to ${fmt(condSd, 3)}`),
  );
}

export const DIST_ALGOS = {
  gaussianSweep,
  discreteMass,
  gaussianConditioning,
} as const;

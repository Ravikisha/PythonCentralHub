/**
 * algos/eigen.ts — the "eigen" analysis of §4.2, stepped.
 *
 * The book's Example 4.5 lays out three steps: write the characteristic
 * polynomial, find its roots, solve a homogeneous system per root. Every one of
 * those steps is a place a reader loses the thread, and the usual presentation
 * hides two facts that matter more than the arithmetic:
 *
 *   1. The polynomial can have complex roots, and then there is NO real
 *      invariant direction. A rotation is the canonical case, and a stepper that
 *      silently returns nothing there teaches the wrong lesson. So this trace
 *      finds complex roots too and says so.
 *   2. Algebraic and geometric multiplicity can differ (Def 4.9 vs 4.11), and
 *      when they do the matrix is DEFECTIVE and Theorem 4.20 does not apply.
 *      That is the whole reason §4.4 needs a hypothesis.
 *
 * The characteristic polynomial comes from Faddeev-LeVerrier rather than a
 * symbolic expansion: it is exact for integer matrices, it is six lines, and it
 * gives the coefficients the book names in Equations 4.23 and 4.24 (the constant
 * term is det, the next-to-leading is the trace up to sign) so the trace can
 * check them against independently computed values.
 *
 * Roots come from Durand-Kerner, which converges to all roots simultaneously and
 * handles complex ones without special-casing. Eigenvectors are computed only for
 * roots that are real, by real Gaussian elimination on A - lambda*I.
 *
 * Sizes 2 to 4. Beyond that there is nothing to draw and the arithmetic stops
 * being followable, which is the point of a stepper.
 */
import { tracer, capFrames, type Trace } from "../../frames";

const EPS = 1e-10;

export interface EigenInput {
  /** Square matrix, 2x2 up to 4x4. */
  matrix: number[][];
  /** A probe vector to carry through the frames, for the 2-D stage. */
  probe?: number[];
}

export interface Complex {
  re: number;
  im: number;
}

export interface EigenPair {
  value: Complex;
  /** Algebraic multiplicity: how many times this root appears. */
  algebraic: number;
  /** Geometric multiplicity: dim of the eigenspace. 0 when the value is complex. */
  geometric: number;
  /** A basis of the eigenspace, empty when the eigenvalue is not real. */
  basis: number[][];
}

export interface EigenState {
  matrix: number[][];
  n: number;
  probe: number[] | null;
  /** Characteristic polynomial coefficients, constant term first. */
  poly: number[] | null;
  /** Pretty-printed polynomial, e.g. "10 - 7L + L^2". */
  polyText: string | null;
  pairs: EigenPair[];
  /** Index of the eigenvalue this frame is about, or null. */
  focus: number | null;
  /** Numeric claims verified this frame. */
  checks: { label: string; value: string; ok: boolean }[];
  /** Small matrices worth showing, e.g. A - lambda I. */
  matrices: { label: string; rows: number[][] }[];
  /** True once the trace has decided. */
  defective: boolean | null;
  /** True when every root is real. */
  allReal: boolean;
}

const CODE = [
  "p(L) = det(A - L*I)                 # the characteristic polynomial, Def 4.5",
  "roots = solve(p)                    # the eigenvalues, Thm 4.8",
  "for L in roots:",
  "    E_L = null_space(A - L*I)       # the eigenspace, Def 4.10",
  "    check A @ v == L * v for v in E_L",
  "det(A) == prod(roots)               # Thm 4.16",
  "trace(A) == sum(roots)              # Thm 4.17",
  "diagonalizable iff sum(dim E_L) == n   # Thm 4.20",
];

/* -------------------------------------------------------------------------- */
/* Small matrix helpers                                                        */
/* -------------------------------------------------------------------------- */

const zeros = (n: number, m = n) => Array.from({ length: n }, () => new Array(m).fill(0));
const eye = (n: number): number[][] =>
  Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));

function mul(A: number[][], B: number[][]): number[][] {
  const n = A.length, m = B[0].length, k = B.length;
  const C = zeros(n, m);
  for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) {
    let s = 0;
    for (let t = 0; t < k; t++) s += A[i][t] * B[t][j];
    C[i][j] = s;
  }
  return C;
}

const trace = (A: number[][]) => A.reduce((s, r, i) => s + r[i], 0);
const matVec = (A: number[][], v: number[]) => A.map((r) => r.reduce((s, x, i) => s + x * v[i], 0));

/** Determinant by Gaussian elimination with partial pivoting. */
function det(A: number[][]): number {
  const n = A.length;
  const M = A.map((r) => [...r]);
  let d = 1;
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let i = c; i < n; i++) if (Math.abs(M[i][c]) > Math.abs(M[p][c])) p = i;
    if (Math.abs(M[p][c]) < 1e-14) return 0;
    if (p !== c) { [M[c], M[p]] = [M[p], M[c]]; d = -d; }
    d *= M[c][c];
    for (let i = c + 1; i < n; i++) {
      const f = M[i][c] / M[c][c];
      for (let j = c; j < n; j++) M[i][j] -= f * M[c][j];
    }
  }
  return d;
}

/**
 * Faddeev-LeVerrier: coefficients of det(A - L*I) as a polynomial in L,
 * returned constant-term first. Exact on integer input for these sizes.
 */
function charPoly(A: number[][]): number[] {
  const n = A.length;
  // c[0] = 1 is the coefficient of L^n in det(L*I - A); we convert at the end.
  const c = new Array(n + 1).fill(0);
  c[0] = 1;
  let M = zeros(n);
  for (let k = 1; k <= n; k++) {
    // M_k = A * M_{k-1} + c_{k-1} * I
    const prev = k === 1 ? zeros(n) : M;
    const AM = mul(A, prev);
    M = AM.map((row, i) => row.map((v, j) => v + (i === j ? c[k - 1] : 0)));
    c[k] = -trace(mul(A, M)) / k;
  }
  // c holds det(L*I - A) = L^n + c1 L^(n-1) + ... + cn. Reverse to constant-first.
  const asc = c.slice().reverse(); // constant term first for det(L I - A)
  // det(A - L I) = (-1)^n det(L I - A), so scale.
  const sign = n % 2 === 0 ? 1 : -1;
  return asc.map((v) => sign * v);
}

/** Evaluate a real-coefficient polynomial at a complex point. */
function polyAt(coef: number[], z: Complex): Complex {
  let re = 0, im = 0;
  // Horner from the top.
  for (let i = coef.length - 1; i >= 0; i--) {
    const nre = re * z.re - im * z.im + coef[i];
    const nim = re * z.im + im * z.re;
    re = nre; im = nim;
  }
  return { re, im };
}

const cAdd = (a: Complex, b: Complex): Complex => ({ re: a.re + b.re, im: a.im + b.im });
const cSub = (a: Complex, b: Complex): Complex => ({ re: a.re - b.re, im: a.im - b.im });
const cMul = (a: Complex, b: Complex): Complex => ({ re: a.re * b.re - a.im * b.im, im: a.re * b.im + a.im * b.re });
function cDiv(a: Complex, b: Complex): Complex {
  const d = b.re * b.re + b.im * b.im;
  if (d < 1e-300) return { re: 0, im: 0 };
  return { re: (a.re * b.re + a.im * b.im) / d, im: (a.im * b.re - a.re * b.im) / d };
}

/** Derivative coefficients of a real polynomial, constant term first. */
const dPoly = (coef: number[]) => coef.slice(1).map((c, i) => c * (i + 1));

/**
 * Durand-Kerner, then cluster, then polish.
 *
 * Plain Durand-Kerner is fine for simple roots and poor for repeated ones — a
 * double root converges at half the rate and typically lands ~1e-8 off, with a
 * spurious imaginary part of the same size. That is not a cosmetic problem here:
 * an eigenvalue that is 1.000000012 instead of 1 makes `A - L*I` nonsingular,
 * which collapses the eigenspace to nothing and reports a diagonalizable matrix
 * as defective. The book's Example 4.8 fails exactly that way.
 *
 * So: (1) run Durand-Kerner, (2) merge roots that are close relative to their
 * size — the cluster size IS the algebraic multiplicity, (3) drop an imaginary
 * part that is negligible relative to the real part, (4) polish each real root
 * with a multiplicity-damped Newton step, which restores full accuracy for
 * repeated roots, and (5) snap to a nearby integer or half-integer only when the
 * gap is below 1e-9, so a genuinely irrational eigenvalue is never faked.
 */
function roots(coef: number[]): Complex[] {
  const deg = coef.length - 1;
  if (deg < 1) return [];
  const lead = coef[deg];
  const a = coef.map((v) => v / lead);
  let z: Complex[] = Array.from({ length: deg }, (_, i) => ({
    re: 0.4 * Math.cos((2 * Math.PI * i) / deg + 0.7) + 0.9,
    im: 0.4 * Math.sin((2 * Math.PI * i) / deg + 0.7) + 0.3,
  }));
  for (let iter = 0; iter < 2000; iter++) {
    let moved = 0;
    const next = z.map((zi, i) => {
      let denom: Complex = { re: 1, im: 0 };
      for (let j = 0; j < deg; j++) {
        if (i === j) continue;
        denom = cMul(denom, cSub(zi, z[j]));
      }
      const step = cDiv(polyAt(a, zi), denom);
      moved = Math.max(moved, Math.hypot(step.re, step.im));
      return cSub(zi, step);
    });
    z = next;
    if (moved < 1e-15) break;
  }

  // Cluster: roots within a relative tolerance are one repeated root.
  const scale = Math.max(1, ...z.map((v) => Math.hypot(v.re, v.im)));
  const tol = 1e-4 * scale;
  const clusters: { sum: Complex; count: number }[] = [];
  for (const v of z) {
    const hit = clusters.find(
      (c) => Math.hypot(c.sum.re / c.count - v.re, c.sum.im / c.count - v.im) < tol,
    );
    if (hit) { hit.sum = cAdd(hit.sum, v); hit.count += 1; }
    else clusters.push({ sum: { ...v }, count: 1 });
  }

  const ap = dPoly(a);
  const out: Complex[] = [];
  for (const c of clusters) {
    let re = c.sum.re / c.count;
    let im = c.sum.im / c.count;
    const isReal = Math.abs(im) < 1e-5 * Math.max(1, Math.abs(re));
    if (isReal) {
      im = 0;
      // Multiplicity-damped Newton: x <- x - m * p(x) / p'(x).
      for (let k = 0; k < 60; k++) {
        const p = polyAt(a, { re, im: 0 }).re;
        const d = polyAt(ap, { re, im: 0 }).re;
        if (Math.abs(d) < 1e-300) break;
        const step = (c.count * p) / d;
        re -= step;
        if (Math.abs(step) < 1e-16 * Math.max(1, Math.abs(re))) break;
      }
      // Snap only when the gap is at floating-point noise level.
      for (const grid of [1, 2, 4]) {
        const snapped = Math.round(re * grid) / grid;
        if (Math.abs(re - snapped) < 1e-9 * Math.max(1, Math.abs(re))) { re = snapped; break; }
      }
      if (Math.abs(re) < 1e-12) re = 0;
    }
    for (let k = 0; k < c.count; k++) out.push({ re, im: k % 2 === 0 ? im : -im });
  }
  return out.sort((p, q) => q.re - p.re || q.im - p.im);
}

/**
 * Null space of A, as a basis of unit vectors, by Gaussian elimination.
 *
 * The pivot tolerance is scaled by the largest entry rather than absolute: an
 * eigenvalue known to 1e-15 still leaves `A - L*I` with a pivot around 1e-14
 * times the matrix scale, and an absolute threshold either rejects that (losing
 * the eigenvector) or accepts genuine rank on a small matrix.
 */
function nullSpace(A: number[][], relTol = 1e-9): number[][] {
  const n = A.length;
  const M = A.map((r) => [...r]);
  const scale = Math.max(1e-300, ...A.flat().map(Math.abs));
  const tol = relTol * scale * n;
  const pivotCols: number[] = [];
  let row = 0;
  for (let col = 0; col < n && row < n; col++) {
    let p = row;
    for (let i = row; i < n; i++) if (Math.abs(M[i][col]) > Math.abs(M[p][col])) p = i;
    if (Math.abs(M[p][col]) < tol) continue;
    [M[row], M[p]] = [M[p], M[row]];
    const piv = M[row][col];
    for (let j = 0; j < n; j++) M[row][j] /= piv;
    for (let i = 0; i < n; i++) {
      if (i === row) continue;
      const f = M[i][col];
      if (Math.abs(f) < 1e-300) continue;
      for (let j = 0; j < n; j++) M[i][j] -= f * M[row][j];
    }
    pivotCols.push(col);
    row++;
  }
  const free = [];
  for (let c = 0; c < n; c++) if (!pivotCols.includes(c)) free.push(c);

  const basis: number[][] = [];
  for (const f of free) {
    const v = new Array(n).fill(0);
    v[f] = 1;
    pivotCols.forEach((pc, i) => { v[pc] = -M[i][f]; });
    const norm = Math.sqrt(v.reduce((s, x) => s + x * x, 0));
    // Fix the sign so the first substantial entry is positive: the eigenvector
    // is only defined up to scale (Remark after Def 4.7) and an arbitrary sign
    // makes the frames flicker.
    const lead = v.find((x) => Math.abs(x) > 1e-9) ?? 1;
    const s = lead < 0 ? -1 : 1;
    basis.push(v.map((x) => (s * x) / norm));
  }
  return basis;
}

const fmt = (v: number, d = 4) => {
  const z = Math.abs(v) < 1e-9 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

const cFmt = (z: Complex) => {
  if (z.im === 0) return fmt(z.re);
  const sign = z.im < 0 ? "-" : "+";
  return `${fmt(z.re)} ${sign} ${fmt(Math.abs(z.im))}i`;
};

const vec = (v: number[]) => `(${v.map((x) => fmt(x, 3)).join(", ")})`;

/** "10 - 7L + L^2", constant term first, skipping zero coefficients. */
function polyText(coef: number[]): string {
  const parts: string[] = [];
  coef.forEach((c, k) => {
    if (Math.abs(c) < 1e-9) return;
    const mag = fmt(Math.abs(c));
    const power = k === 0 ? "" : k === 1 ? "L" : `L^${k}`;
    const body = k === 0 ? mag : mag === "1" ? power : `${mag}${power}`;
    parts.push((c < 0 ? "- " : parts.length ? "+ " : "") + body);
  });
  return parts.length ? parts.join(" ") : "0";
}

/* -------------------------------------------------------------------------- */
/* The trace                                                                   */
/* -------------------------------------------------------------------------- */

export function eigen({ matrix, probe }: EigenInput): Trace<EigenState> {
  const n = matrix.length;
  const t = tracer<EigenState>(CODE);
  const A = matrix.map((r) => [...r]);

  const blank: EigenState = {
    matrix: A,
    n,
    probe: probe ? [...probe] : null,
    poly: null,
    polyText: null,
    pairs: [],
    focus: null,
    checks: [],
    matrices: [],
    defective: null,
    allReal: true,
  };

  const snap = (
    caption: string,
    patch: Partial<EigenState>,
    extra: { line?: number; phase?: string; watch?: { label: string; value: string | number; tone?: "good" | "bad" | "active" | "muted" | "warn" | "info" }[] } = {},
  ) => t.push({ ...blank, ...patch }, caption, extra);

  snap(
    `A is ${n}x${n}. The eigenvalue equation Ax = Lx asks for directions the matrix only scales — and the only way a nonzero x can satisfy (A - L I)x = 0 is for A - L I to be singular, so det(A - L I) = 0 is where the eigenvalues must come from.`,
    {},
    { line: 1, phase: "setup" },
  );

  const coef = charPoly(A);
  const dt = det(A);
  const tr = trace(A);

  snap(
    `The characteristic polynomial is p(L) = ${polyText(coef)}. Two of its coefficients are quantities you already have: the constant term is det(A) = ${fmt(dt)} (Equation 4.23) and the coefficient of L^${n - 1} is ${n % 2 === 0 ? "minus" : "plus"} the trace, ${fmt(tr)} (Equation 4.24).`,
    {
      poly: coef,
      polyText: polyText(coef),
      checks: [
        { label: "constant term vs det(A)", value: `${fmt(coef[0])} vs ${fmt(dt)}`, ok: Math.abs(coef[0] - dt) < 1e-7 },
        {
          label: `|coef of L^${n - 1}| vs |trace|`,
          value: `${fmt(Math.abs(coef[n - 1]))} vs ${fmt(Math.abs(tr))}`,
          ok: Math.abs(Math.abs(coef[n - 1]) - Math.abs(tr)) < 1e-7,
        },
      ],
    },
    { line: 1, phase: "polynomial" },
  );

  const rts = roots(coef);
  const allReal = rts.every((r) => r.im === 0);

  // Group equal roots to get algebraic multiplicities.
  const grouped: { value: Complex; algebraic: number }[] = [];
  for (const r of rts) {
    const hit = grouped.find((g) => Math.abs(g.value.re - r.re) < 1e-6 && Math.abs(g.value.im - r.im) < 1e-6);
    if (hit) hit.algebraic += 1;
    else grouped.push({ value: { ...r }, algebraic: 1 });
  }

  snap(
    allReal
      ? `Its roots are the eigenvalues: ${grouped.map((g) => cFmt(g.value) + (g.algebraic > 1 ? ` (repeated ${g.algebraic} times)` : "")).join(", ")}. Theorem 4.8 is what licenses this: L is an eigenvalue exactly when it is a root of p.`
      : `Its roots include a complex pair: ${grouped.map((g) => cFmt(g.value)).join(", ")}. A complex eigenvalue has no real eigenvector, so this matrix leaves NO real direction invariant — which is exactly what a rotation does, and why the book draws no eigenvectors for its rotation example.`,
    {
      poly: coef,
      polyText: polyText(coef),
      pairs: grouped.map((g) => ({ value: g.value, algebraic: g.algebraic, geometric: 0, basis: [] })),
      allReal,
    },
    { line: 2, phase: "eigenvalues" },
  );

  const pairs: EigenPair[] = [];
  grouped.forEach((g, i) => {
    if (g.value.im !== 0) {
      pairs.push({ value: g.value, algebraic: g.algebraic, geometric: 0, basis: [] });
      snap(
        `L = ${cFmt(g.value)} is not real, so (A - L I)x = 0 has no real solution other than zero. There is no real eigenspace to draw. Its partner ${cFmt({ re: g.value.re, im: -g.value.im })} is the conjugate — real matrices always produce complex eigenvalues in pairs.`,
        { poly: coef, polyText: polyText(coef), pairs: [...pairs], focus: i, allReal },
        { line: 2, phase: "complex" },
      );
      return;
    }

    const L = g.value.re;
    const shifted = A.map((row, r) => row.map((v, c) => v - (r === c ? L : 0)));
    const basis = nullSpace(shifted);
    pairs.push({ value: g.value, algebraic: g.algebraic, geometric: basis.length, basis });

    snap(
      `For L = ${fmt(L)}, subtract L from the diagonal and solve the homogeneous system. The eigenspace E_${fmt(L)} is the null space of A - ${fmt(L)}I, and it has dimension ${basis.length}${basis.length ? `, spanned by ${basis.map(vec).join(" and ")}` : ""}.`,
      {
        poly: coef,
        polyText: polyText(coef),
        pairs: [...pairs],
        focus: i,
        allReal,
        matrices: [{ label: `A - ${fmt(L)}I`, rows: shifted }],
        checks: basis.map((v, k) => {
          const Av = matVec(A, v);
          const gap = Math.max(...Av.map((x, j) => Math.abs(x - L * v[j])));
          return { label: `A v${k + 1} = ${fmt(L)} v${k + 1}`, value: gap < 1e-8 ? "exact" : gap.toExponential(1), ok: gap < 1e-8 };
        }),
      },
      { line: 4, phase: "eigenspace" },
    );

    if (basis.length < g.algebraic) {
      snap(
        `Note the mismatch: L = ${fmt(L)} has algebraic multiplicity ${g.algebraic} but geometric multiplicity ${basis.length}. Definition 4.11's remark says the geometric multiplicity can be lower than the algebraic one and never higher — and when it is lower, the matrix is DEFECTIVE and Theorem 4.20 will not apply.`,
        { poly: coef, polyText: polyText(coef), pairs: [...pairs], focus: i, allReal, defective: true },
        { line: 4, phase: "defective" },
      );
    }
  });

  // Theorems 4.16 and 4.17, measured.
  const prodRe = rts.reduce<Complex>((acc, r) => cMul(acc, r), { re: 1, im: 0 });
  const sumRe = rts.reduce<Complex>((acc, r) => cAdd(acc, r), { re: 0, im: 0 });

  snap(
    `Two theorems tie the eigenvalues back to §4.1. Theorem 4.16: det(A) is the product of the eigenvalues, repeats included. Theorem 4.17: the trace is their sum. Both hold for complex eigenvalues too — the imaginary parts cancel in conjugate pairs, which is why the products and sums below come out real.`,
    {
      poly: coef,
      polyText: polyText(coef),
      pairs: [...pairs],
      allReal,
      checks: [
        {
          label: "prod(eigenvalues) vs det(A)",
          value: `${cFmt(prodRe)} vs ${fmt(dt)}`,
          ok: Math.abs(prodRe.re - dt) < 1e-6 && Math.abs(prodRe.im) < 1e-6,
        },
        {
          label: "sum(eigenvalues) vs trace(A)",
          value: `${cFmt(sumRe)} vs ${fmt(tr)}`,
          ok: Math.abs(sumRe.re - tr) < 1e-6 && Math.abs(sumRe.im) < 1e-6,
        },
      ],
    },
    { line: 6, phase: "theorems" },
  );

  const totalGeom = pairs.reduce((s, p) => s + p.geometric, 0);
  const defective = totalGeom < n;

  snap(
    defective
      ? `The eigenspace dimensions add to ${totalGeom}, short of ${n}. So the eigenvectors do not form a basis of R^${n}, the matrix is defective (Definition 4.13), and Theorem 4.20 says it cannot be diagonalized. ${allReal ? "" : "Here the shortfall is caused by complex eigenvalues — over the complex numbers this matrix would diagonalize perfectly well."}`
      : `The eigenspace dimensions add to exactly ${n}, so the eigenvectors form a basis of R^${n}. By Theorem 4.20 the matrix is diagonalizable: A = P D P-inverse with the eigenvectors as the columns of P.`,
    {
      poly: coef,
      polyText: polyText(coef),
      pairs: [...pairs],
      allReal,
      defective,
      checks: [
        { label: "sum of eigenspace dimensions", value: `${totalGeom} of ${n}`, ok: !defective },
        { label: "diagonalizable over R", value: defective ? "no" : "yes", ok: !defective },
      ],
    },
    { line: 8, phase: "verdict" },
  );

  return capFrames(
    t.done(
      defective
        ? `defective: ${totalGeom} independent eigenvectors, ${n} needed`
        : `diagonalizable, spectrum ${grouped.map((g) => cFmt(g.value)).join(", ")}`,
    ),
  );
}

export const EIGEN_ALGOS = {
  eigen,
} as const;

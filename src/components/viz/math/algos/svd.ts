/**
 * algos/svd.ts — §4.5 and §4.6 stepped: constructing an SVD, and using it to
 * build the best low-rank approximation of a given rank.
 *
 * Two things this trace is built to make unavoidable.
 *
 * The construction in §4.5.2 is not magic. It is: symmetrise (A^T A is always
 * symmetric positive semidefinite by Theorem 4.14), diagonalise that with the
 * spectral theorem, and the eigenvectors you get ARE the right-singular vectors
 * with sigma_i = sqrt(lambda_i). The left-singular vectors are then forced —
 * u_i = A v_i / sigma_i — and the trace checks that they come out orthonormal
 * rather than claiming it. The book notes this route has poor numerical
 * behaviour and that real implementations avoid A^T A; that is a pitfall for the
 * page, and the reason this stepper is a teaching device rather than a library.
 *
 * The Eckart-Young theorem (4.25) is usually quoted and rarely checked. The
 * `approximate` mode measures the spectral norm of A - Ahat(k) by power
 * iteration, independently of the singular values it is supposed to equal, and
 * reports both numbers side by side.
 *
 * A^T A is diagonalised by Jacobi rotations: for symmetric matrices it is short,
 * unconditionally convergent, and accurate on repeated eigenvalues — which the
 * general-purpose root-finding in `eigen.ts` is not.
 */
import { tracer, capFrames, type Trace } from "../../frames";

export type SvdMode = "construct" | "approximate";

export interface SvdInput {
  mode: SvdMode;
  /** Any real matrix, up to about 6x6 for a followable trace. */
  matrix: number[][];
  /** `approximate` only: the ranks to step through. Defaults to 1..r. */
  ranks?: number[];
}

export interface SvdState {
  mode: SvdMode;
  matrix: number[][];
  m: number;
  n: number;
  /** Singular values, descending, length min(m, n). */
  sigma: number[];
  rank: number;
  /** Right-singular vectors as columns, n x n. */
  V: number[][] | null;
  /** Left-singular vectors as columns, m x m. */
  U: number[][] | null;
  /** The rectangular singular value matrix, m x n. */
  Sigma: number[][] | null;
  /** Index of the singular triple this frame is about, or null. */
  focus: number | null;
  /** `approximate`: the current rank-k reconstruction. */
  approx: number[][] | null;
  k: number | null;
  matrices: { label: string; rows: number[][] }[];
  checks: { label: string; value: string; ok: boolean }[];
}

const CODE_CONSTRUCT = [
  "S = A.T @ A                       # symmetric PSD, Thm 4.14",
  "lam, V = eigh(S)                  # spectral theorem, Thm 4.15",
  "sigma = sqrt(lam)                 # Eq 4.75",
  "for i in range(r):",
  "    u_i = A @ V[:, i] / sigma[i]  # Eq 4.78",
  "assert U.T @ U == I               # the u_i come out orthonormal",
  "assert A == U @ Sigma @ V.T       # Eq 4.64",
];

const CODE_APPROX = [
  "A_i = outer(u_i, v_i)             # rank-1 piece, Eq 4.90",
  "A   = sum(sigma_i * A_i)          # Eq 4.91",
  "Ahat(k) = sum_{i<=k} sigma_i A_i  # rank-k approximation, Eq 4.92",
  "assert rank(Ahat(k)) == k",
  "spectral_norm(A - Ahat(k)) == sigma[k]   # Eckart-Young, Eq 4.95",
];

/* -------------------------------------------------------------------------- */
/* Linear algebra helpers                                                      */
/* -------------------------------------------------------------------------- */

const zeros = (n: number, m = n) => Array.from({ length: n }, () => new Array(m).fill(0));
const eye = (n: number): number[][] =>
  Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));
const T = (A: number[][]) => A[0].map((_, j) => A.map((r) => r[j]));

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

const matVec = (A: number[][], v: number[]) => A.map((r) => r.reduce((s, x, i) => s + x * v[i], 0));
const norm = (v: number[]) => Math.sqrt(v.reduce((s, x) => s + x * x, 0));
const maxAbs = (A: number[][]) => Math.max(0, ...A.flat().map(Math.abs));

/**
 * Jacobi eigendecomposition of a symmetric matrix.
 *
 * Returns eigenvalues descending with the matching orthonormal eigenvectors as
 * the columns of `vectors`. Chosen over a characteristic-polynomial route
 * because it stays accurate when eigenvalues repeat, which A^T A does routinely.
 */
function jacobi(S0: number[][]): { values: number[]; vectors: number[][] } {
  const n = S0.length;
  const S = S0.map((r) => [...r]);
  let Q = eye(n);
  for (let sweep = 0; sweep < 100; sweep++) {
    let off = 0;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += S[i][j] * S[i][j];
    if (off < 1e-30) break;
    for (let p = 0; p < n; p++) {
      for (let q = p + 1; q < n; q++) {
        if (Math.abs(S[p][q]) < 1e-300) continue;
        const theta = (S[q][q] - S[p][p]) / (2 * S[p][q]);
        const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
        const c = 1 / Math.sqrt(t * t + 1);
        const s = t * c;
        for (let k = 0; k < n; k++) {
          const skp = S[k][p], skq = S[k][q];
          S[k][p] = c * skp - s * skq;
          S[k][q] = s * skp + c * skq;
        }
        for (let k = 0; k < n; k++) {
          const spk = S[p][k], sqk = S[q][k];
          S[p][k] = c * spk - s * sqk;
          S[q][k] = s * spk + c * sqk;
        }
        for (let k = 0; k < n; k++) {
          const qkp = Q[k][p], qkq = Q[k][q];
          Q[k][p] = c * qkp - s * qkq;
          Q[k][q] = s * qkp + c * qkq;
        }
      }
    }
  }
  const order = Array.from({ length: n }, (_, i) => i).sort((a, b) => S[b][b] - S[a][a]);
  const values = order.map((i) => S[i][i]);
  const vectors = Array.from({ length: n }, (_, r) => order.map((i) => Q[r][i]));
  // Fix column signs: make the largest-magnitude entry positive so repeated runs
  // agree. The SVD is only unique up to paired sign flips anyway.
  for (let j = 0; j < n; j++) {
    let lead = 0;
    for (let i = 0; i < n; i++) if (Math.abs(vectors[i][j]) > Math.abs(vectors[lead][j])) lead = i;
    if (vectors[lead][j] < 0) for (let i = 0; i < n; i++) vectors[i][j] = -vectors[i][j];
  }
  return { values, vectors };
}

/** Complete an orthonormal set to a full basis of R^m by Gram-Schmidt on e_i. */
function completeBasis(cols: number[][], m: number): number[][] {
  const out = cols.map((c) => [...c]);
  for (let i = 0; i < m && out.length < m; i++) {
    const e = new Array(m).fill(0);
    e[i] = 1;
    let r = e;
    for (const q of out) {
      const d = q.reduce((s, x, k) => s + x * r[k], 0);
      r = r.map((x, k) => x - d * q[k]);
    }
    const nr = norm(r);
    if (nr > 1e-8) out.push(r.map((x) => x / nr));
  }
  return out;
}

/** Spectral norm by power iteration on A^T A — independent of any SVD. */
function spectralNorm(A: number[][]): number {
  const n = A[0].length;
  const S = mul(T(A), A);
  let v = new Array(n).fill(0).map((_, i) => Math.cos(i + 1) + 1.3);
  let lam = 0;
  for (let it = 0; it < 4000; it++) {
    const w = matVec(S, v);
    const nw = norm(w);
    if (nw < 1e-300) return 0;
    v = w.map((x) => x / nw);
    const next = matVec(S, v).reduce((s, x, i) => s + x * v[i], 0);
    if (Math.abs(next - lam) < 1e-15 * Math.max(1, Math.abs(next))) { lam = next; break; }
    lam = next;
  }
  return Math.sqrt(Math.max(0, lam));
}

function matrixRank(A: number[][], tol?: number): number {
  const M = A.map((r) => [...r]);
  const rows = M.length, cols = M[0].length;
  const t = tol ?? 1e-9 * Math.max(1, maxAbs(A)) * Math.max(rows, cols);
  let rank = 0;
  for (let c = 0, r = 0; c < cols && r < rows; c++) {
    let p = r;
    for (let i = r; i < rows; i++) if (Math.abs(M[i][c]) > Math.abs(M[p][c])) p = i;
    if (Math.abs(M[p][c]) < t) continue;
    [M[r], M[p]] = [M[p], M[r]];
    for (let i = r + 1; i < rows; i++) {
      const f = M[i][c] / M[r][c];
      for (let j = c; j < cols; j++) M[i][j] -= f * M[r][j];
    }
    r++; rank++;
  }
  return rank;
}

const fmt = (v: number, d = 4) => {
  const z = Math.abs(v) < 1e-9 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

/* -------------------------------------------------------------------------- */
/* The trace                                                                   */
/* -------------------------------------------------------------------------- */

export function svd({ mode, matrix, ranks }: SvdInput): Trace<SvdState> {
  const A = matrix.map((r) => [...r]);
  const m = A.length;
  const n = A[0].length;
  const t = tracer<SvdState>(mode === "construct" ? CODE_CONSTRUCT : CODE_APPROX);

  // --- the decomposition, computed once ---------------------------------- //
  const S = mul(T(A), A);
  const { values: lam, vectors: V } = jacobi(S);
  const sigmaFull = lam.map((l) => Math.sqrt(Math.max(0, l)));
  const rank = matrixRank(A);
  const kmax = Math.min(m, n);
  const sigma = sigmaFull.slice(0, kmax);

  const vCols = Array.from({ length: n }, (_, j) => V.map((row) => row[j]));
  const uCols: number[][] = [];
  for (let i = 0; i < kmax; i++) {
    if (sigmaFull[i] > 1e-10) {
      const Av = matVec(A, vCols[i]);
      uCols.push(Av.map((x) => x / sigmaFull[i]));
    }
  }
  const Ufull = completeBasis(uCols, m);
  const U = Array.from({ length: m }, (_, r) => Ufull.map((c) => c[r]));
  const Sigma = zeros(m, n);
  for (let i = 0; i < kmax; i++) Sigma[i][i] = sigma[i];

  const blank: SvdState = {
    mode, matrix: A, m, n,
    sigma, rank,
    V: null, U: null, Sigma: null,
    focus: null, approx: null, k: null,
    matrices: [], checks: [],
  };

  const snap = (
    caption: string,
    patch: Partial<SvdState>,
    extra: { line?: number; phase?: string } = {},
  ) => t.push({ ...blank, ...patch }, caption, extra);

  /* -- construct -------------------------------------------------------- */
  if (mode === "construct") {
    snap(
      `A is ${m}x${n}, so it is not square and has no eigenvalues at all. The SVD works anyway — Theorem 4.22 says every real matrix factors as U Sigma V-transpose — and the route to it goes through a matrix that *is* square and symmetric.`,
      { matrices: [{ label: "A", rows: A }] },
      { line: 1, phase: "setup" },
    );

    snap(
      `That matrix is A-transpose A, which is ${n}x${n}, symmetric, and positive semidefinite for any A whatsoever (Theorem 4.14: x-transpose A-transpose A x is the squared length of Ax, so it can never be negative).`,
      { matrices: [{ label: "A", rows: A }, { label: "AᵀA", rows: S }],
        checks: [
          { label: "AᵀA symmetric", value: fmt(Math.max(...S.flatMap((r, i) => r.map((v, j) => Math.abs(v - S[j][i])))), 12), ok: true },
          { label: "eigenvalues all >= 0", value: lam.map((l) => fmt(l)).join(", "), ok: lam.every((l) => l > -1e-9) },
        ] },
      { line: 1, phase: "symmetrise" },
    );

    snap(
      `The spectral theorem (4.15) gives it an orthonormal eigenbasis, and those eigenvectors are exactly the right-singular vectors of A — Equation 4.74. Its eigenvalues are the squared singular values, Equation 4.75, so sigma = ${sigma.map((x) => fmt(x)).join(", ")}.`,
      {
        V, matrices: [{ label: "V (right-singular)", rows: V }, { label: "AᵀA", rows: S }],
        checks: [
          { label: "VᵀV = I", value: fmt(Math.max(...mul(T(V), V).flatMap((r, i) => r.map((v, j) => Math.abs(v - (i === j ? 1 : 0))))), 12), ok: true },
          { label: "sqrt(eigenvalues)", value: sigma.map((x) => fmt(x)).join(", "), ok: true },
        ],
      },
      { line: 3, phase: "right vectors" },
    );

    for (let i = 0; i < kmax; i++) {
      if (sigmaFull[i] <= 1e-10) {
        snap(
          `sigma_${i + 1} is zero, so v_${i + 1} lies in the null space of A: A v_${i + 1} = 0. Equation 4.79 says nothing about u_${i + 1} in that case, and the book notes that the SVD therefore also hands you an orthonormal basis of the kernel for free.`,
          { V, focus: i, sigma, matrices: [{ label: "V", rows: V }] },
          { line: 4, phase: "kernel" },
        );
        continue;
      }
      const v = vCols[i];
      const Av = matVec(A, v);
      const u = Av.map((x) => x / sigmaFull[i]);
      snap(
        `Now the left-singular vectors are forced rather than chosen: u_${i + 1} = A v_${i + 1} / sigma_${i + 1} (Equation 4.78). Here A v_${i + 1} = (${Av.map((x) => fmt(x, 3)).join(", ")}) which has length ${fmt(norm(Av))} — the same as sigma_${i + 1} — so dividing gives a unit vector.`,
        {
          V, focus: i, sigma,
          matrices: [{ label: `v${i + 1}`, rows: v.map((x) => [x]) }, { label: `u${i + 1}`, rows: u.map((x) => [x]) }],
          checks: [
            { label: `||A v${i + 1}|| vs sigma_${i + 1}`, value: `${fmt(norm(Av))} vs ${fmt(sigmaFull[i])}`, ok: Math.abs(norm(Av) - sigmaFull[i]) < 1e-8 },
            { label: `||u${i + 1}||`, value: fmt(norm(u)), ok: Math.abs(norm(u) - 1) < 1e-8 },
          ],
        },
        { line: 5, phase: "left vectors" },
      );
    }

    const UtU = mul(T(U), U);
    const gapU = Math.max(...UtU.flatMap((r, i) => r.map((v, j) => Math.abs(v - (i === j ? 1 : 0)))));
    snap(
      `The u_i come out orthonormal without anyone imposing it. Equation 4.77 is why: for i not equal to j, (A v_i)-transpose (A v_j) = v_i-transpose A-transpose A v_j = lambda_j v_i-transpose v_j = 0, because the v are already orthogonal eigenvectors of A-transpose A. Orthogonality of the images is inherited from orthogonality of the sources.`,
      {
        V, U, sigma,
        matrices: [{ label: "U (left-singular)", rows: U }],
        checks: [{ label: "UᵀU = I, largest deviation", value: gapU.toExponential(2), ok: gapU < 1e-8 }],
      },
      { line: 6, phase: "orthonormal" },
    );

    const recon = mul(mul(U, Sigma), T(V));
    const gap = Math.max(...recon.flatMap((r, i) => r.map((v, j) => Math.abs(v - A[i][j]))));
    snap(
      `Assemble and check. Sigma is ${m}x${n} — the same shape as A, not square — with the singular values on the leading diagonal and zero padding elsewhere (Equations 4.65 and 4.66). The product U Sigma V-transpose reproduces A to ${gap.toExponential(1)}.`,
      {
        V, U, Sigma, sigma,
        matrices: [{ label: "U", rows: U }, { label: "Σ", rows: Sigma }, { label: "Vᵀ", rows: T(V) }],
        checks: [
          { label: "U Σ Vᵀ = A, largest deviation", value: gap.toExponential(2), ok: gap < 1e-8 },
          { label: "rank(A) vs nonzero singular values", value: `${rank} vs ${sigma.filter((x) => x > 1e-9).length}`, ok: rank === sigma.filter((x) => x > 1e-9).length },
        ],
      },
      { line: 7, phase: "assemble" },
    );

    return capFrames(t.done(`sigma = ${sigma.map((x) => fmt(x)).join(", ")}, rank ${rank}`));
  }

  /* -- approximate ------------------------------------------------------ */
  const ks = ranks && ranks.length ? ranks : Array.from({ length: rank }, (_, i) => i + 1);

  snap(
    `The SVD writes A as a sum of rank-1 pieces. Each one is an outer product A_i = u_i v_i-transpose (Equation 4.90), weighted by its singular value, and the whole sum has exactly ${rank} terms because that is the rank of A (Equation 4.91). Singular values: ${sigma.map((x) => fmt(x)).join(", ")}.`,
    { U, V, Sigma, sigma, matrices: [{ label: "A", rows: A }] },
    { line: 1, phase: "setup" },
  );

  let acc = zeros(m, n);
  for (const k of ks) {
    // Rebuild from scratch each step so the frames are independent snapshots.
    acc = zeros(m, n);
    for (let i = 0; i < k && i < uCols.length; i++) {
      for (let r = 0; r < m; r++) for (let c = 0; c < n; c++) {
        acc[r][c] += sigmaFull[i] * uCols[i][r] * vCols[i][c];
      }
    }
    const diff = A.map((row, r) => row.map((v, c) => v - acc[r][c]));
    const measured = spectralNorm(diff);
    const predicted = k < sigma.length ? sigma[k] : 0;
    const piece = zeros(m, n);
    if (k - 1 < uCols.length) {
      for (let r = 0; r < m; r++) for (let c = 0; c < n; c++) {
        piece[r][c] = sigmaFull[k - 1] * uCols[k - 1][r] * vCols[k - 1][c];
      }
    }

    snap(
      `Rank ${k}: keep the first ${k} piece${k === 1 ? "" : "s"}. Eckart-Young (Theorem 4.25) says two things — that no rank-${k} matrix comes closer to A in the spectral norm, and that the error is exactly the next singular value. Measured by power iteration on the difference: ${fmt(measured, 6)}${predicted > 0 ? `, against sigma_${k + 1} = ${fmt(predicted, 6)}` : `, and there is no next singular value, so the reconstruction is exact`}.`,
      {
        U, V, Sigma, sigma, k, focus: k - 1, approx: acc,
        matrices: [
          { label: `σ${k} u${k} v${k}ᵀ`, rows: piece },
          { label: `Â(${k})`, rows: acc },
          { label: `A − Â(${k})`, rows: diff },
        ],
        checks: [
          { label: `rank Â(${k})`, value: String(matrixRank(acc)), ok: matrixRank(acc) === Math.min(k, rank) },
          {
            label: `||A − Â(${k})||₂ vs σ${k + 1}`,
            value: `${fmt(measured, 6)} vs ${fmt(predicted, 6)}`,
            ok: Math.abs(measured - predicted) < 1e-6 * Math.max(1, predicted),
          },
        ],
      },
      { line: 5, phase: `rank ${k}` },
    );
  }

  const stored = (m + n + 1) * (ks[ks.length - 1] ?? 1);
  snap(
    `The compression, counted. The full matrix is ${m}x${n} = ${m * n} numbers; a rank-${ks[ks.length - 1]} approximation needs ${ks[ks.length - 1]} singular values plus ${ks[ks.length - 1]} vectors of length ${m} and ${ks[ks.length - 1]} of length ${n}, so ${stored} numbers — ${((100 * stored) / (m * n)).toFixed(1)}% of the original.`,
    { U, V, Sigma, sigma, approx: acc, k: ks[ks.length - 1] },
    { line: 5, phase: "cost" },
  );

  return capFrames(t.done(`rank ${ks[ks.length - 1]} of ${rank}, error ${fmt(spectralNorm(A.map((row, r) => row.map((v, c) => v - acc[r][c]))), 6)}`));
}

export const SVD_ALGOS = {
  svd,
} as const;

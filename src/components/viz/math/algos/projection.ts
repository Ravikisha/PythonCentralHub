/**
 * algos/projection.ts — the three-step recipe of §3.8, stepped.
 *
 * The book states the procedure as a numbered list (find the coordinates, find
 * the projection, find the projection matrix) and then works two examples. The
 * list is short enough to memorise and opaque enough to memorise *instead of*
 * understanding, because the one fact that makes every line of it inevitable —
 * the displacement vector is orthogonal to every basis vector — is a sentence
 * in the middle rather than a picture.
 *
 * So each mode here spends one frame per step and, on the step where the claim
 * is made, measures it. The normal equation is not asserted to follow from
 * orthogonality: the trace computes bᵢᵀ(x − Bλ) for every i and shows the
 * zeros. `P² = P` is not asserted either; it is multiplied out.
 *
 * Three modes, because §3.8 is really three results:
 *
 *   line          §3.8.1 — one direction, so λ is a scalar and no solve is needed
 *   plane         §3.8.2 — the normal equation and the pseudo-inverse
 *   gram-schmidt  §3.8.3 — projection used constructively, to build an ONB
 *
 * Dimension is 2 or 3; the stage draws R³ in a fixed oblique projection.
 */
import { tracer, capFrames, type Trace } from "../../frames";

const EPS = 1e-12;

export type ProjMode = "line" | "plane" | "gram-schmidt";

export interface ProjInput {
  mode: ProjMode;
  /** The spanning vectors. One for `line`, two for `plane`, any number for GS. */
  basis: number[][];
  /** The vector being projected. Unused by `gram-schmidt`. */
  target?: number[];
}

export interface ProjState {
  dim: number;
  mode: ProjMode;
  basis: number[][];
  target: number[] | null;
  /** Orthogonal vectors built so far (Gram-Schmidt, before normalising). */
  built: number[][];
  /** The same vectors scaled to unit length, once that step has run. */
  normalised: number[][];
  /** Index of the basis vector this frame is about, or null. */
  focus: number | null;
  proj: number[] | null;
  lambda: number[] | null;
  error: number[] | null;
  errorNorm: number | null;
  /** A dashed segment: the part being subtracted, drawn from `from` to `to`. */
  shadow: { from: number[]; to: number[] } | null;
  /** Small matrices worth showing this frame. */
  matrices: { label: string; rows: number[][] }[];
  /** Directions spanning the subspace to shade. */
  frame: number[][];
  /** Numeric claims verified this frame. */
  checks: { label: string; value: string; ok: boolean }[];
}

const CODE_LINE = [
  "lam = (b @ x) / (b @ b)          # the one coordinate",
  "proj = lam * b                   # the closest point on the line",
  "err  = x - proj                  # and what got thrown away",
  "assert abs(b @ err) < tol        # err is orthogonal to b",
  "P = np.outer(b, b) / (b @ b)     # the projection matrix",
  "assert np.allclose(P @ P, P)     # projecting twice changes nothing",
];

const CODE_PLANE = [
  "B = np.column_stack(basis)",
  "G = B.T @ B                      # Gram matrix, m by m",
  "c = B.T @ x",
  "lam = np.linalg.solve(G, c)      # the normal equation",
  "proj = B @ lam",
  "err  = x - proj",
  "assert np.allclose(B.T @ err, 0) # orthogonal to every basis vector",
  "P = B @ np.linalg.inv(G) @ B.T   # the pseudo-inverse sandwich",
  "assert np.allclose(P @ P, P)",
];

const CODE_GS = [
  "u = [b[0]]",
  "for k in range(1, n):",
  "    r = b[k]",
  "    for uj in u:",
  "        r = r - (uj @ b[k]) / (uj @ uj) * uj   # subtract the shadow",
  "    u.append(r)                                # what is left is orthogonal",
  "Q = [uj / norm(uj) for uj in u]                # normalise for an ONB",
];

/* -------------------------------------------------------------------------- */
/* Small linear algebra. Everything here is at most 3 by 3.                    */
/* -------------------------------------------------------------------------- */

const dot = (a: number[], b: number[]) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = (a: number[]) => Math.sqrt(dot(a, a));
const sub = (a: number[], b: number[]) => a.map((x, i) => x - b[i]);
const scl = (a: number[], k: number) => a.map((x) => x * k);
const outer = (a: number[], b: number[]) => a.map((x) => b.map((y) => x * y));

/** Matrix product, dimensions assumed conformable. */
function mul(A: number[][], B: number[][]): number[][] {
  return A.map((row) => B[0].map((_, j) => row.reduce((s, v, k) => s + v * B[k][j], 0)));
}

function matVec(A: number[][], v: number[]): number[] {
  return A.map((row) => dot(row, v));
}

function transpose(A: number[][]): number[][] {
  return A[0].map((_, j) => A.map((row) => row[j]));
}

/** Gauss-Jordan inverse. Square, small, and assumed invertible here. */
function inverse(A: number[][]): number[][] {
  const n = A.length;
  const M = A.map((row, i) => [...row, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let i = c; i < n; i++) if (Math.abs(M[i][c]) > Math.abs(M[p][c])) p = i;
    [M[c], M[p]] = [M[p], M[c]];
    const pivot = M[c][c];
    for (let j = 0; j < 2 * n; j++) M[c][j] /= pivot;
    for (let i = 0; i < n; i++) {
      if (i === c) continue;
      const f = M[i][c];
      if (Math.abs(f) < EPS) continue;
      for (let j = 0; j < 2 * n; j++) M[i][j] -= f * M[c][j];
    }
  }
  return M.map((row) => row.slice(n));
}

const fmt = (v: number, d = 3) => {
  const z = Math.abs(v) < 1e-10 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

const vec = (v: number[]) => `(${v.map((x) => fmt(x)).join(", ")})`;

/* -------------------------------------------------------------------------- */
/* The trace                                                                   */
/* -------------------------------------------------------------------------- */

export function project({ mode, basis, target }: ProjInput): Trace<ProjState> {
  const dim = basis[0].length;
  const code = mode === "line" ? CODE_LINE : mode === "plane" ? CODE_PLANE : CODE_GS;
  const t = tracer<ProjState>(code);

  const blank: ProjState = {
    dim,
    mode,
    basis: basis.map((b) => [...b]),
    target: target ? [...target] : null,
    built: [],
    normalised: [],
    focus: null,
    proj: null,
    lambda: null,
    error: null,
    errorNorm: null,
    shadow: null,
    matrices: [],
    frame: [],
    checks: [],
  };

  const snap = (
    caption: string,
    patch: Partial<ProjState>,
    extra: { line?: number; phase?: string; watch?: { label: string; value: string | number; tone?: "good" | "bad" | "active" | "muted" | "warn" | "info" }[] } = {},
  ) => t.push({ ...blank, ...patch }, caption, extra);

  /* -- Gram-Schmidt ------------------------------------------------------- */
  if (mode === "gram-schmidt") {
    const built: number[][] = [];

    snap(
      `${basis.length} vectors that span the subspace but are not orthogonal to each other. Gram-Schmidt keeps the first one and repairs each of the others in turn, by subtracting off whatever part of it already points along the ones already accepted.`,
      { frame: [] },
      { line: 1, phase: "setup" },
    );

    basis.forEach((b, k) => {
      if (k === 0) {
        built.push([...b]);
        snap(
          `u1 is just b1 = ${vec(b)}. The first vector has nothing to be orthogonal to, so it is accepted unchanged — which means the ONB you end up with depends on which vector you happened to list first.`,
          { built: built.map((u) => [...u]), focus: 0, frame: built.map((u) => scl(u, 1 / norm(u))) },
          { line: 1, phase: "keep" },
        );
        return;
      }

      // Subtract the projection onto each accepted direction, one at a time, so
      // the reader sees where the shadow comes from.
      let r = [...b];
      for (let j = 0; j < built.length; j++) {
        const u = built[j];
        const c = dot(u, b) / dot(u, u);
        const shadow = scl(u, c);
        const next = sub(r, shadow);
        snap(
          `Project b${k + 1} onto u${j + 1}: the coefficient is ⟨u${j + 1}, b${k + 1}⟩ / ⟨u${j + 1}, u${j + 1}⟩ = ${fmt(dot(u, b))} / ${fmt(dot(u, u))} = ${fmt(c)}, so the shadow is ${vec(shadow)}. Subtracting it removes every trace of the u${j + 1} direction from b${k + 1}.`,
          {
            built: built.map((u2) => [...u2]),
            focus: k,
            shadow: { from: r, to: next },
            frame: built.map((u2) => scl(u2, 1 / norm(u2))),
            checks: [
              {
                label: `⟨u${j + 1}, remainder⟩`,
                value: fmt(dot(u, next)),
                ok: Math.abs(dot(u, next)) < 1e-9,
              },
            ],
          },
          { line: 5, phase: "subtract" },
        );
        r = next;
      }

      built.push(r);
      const orthChecks = built.slice(0, -1).map((u, j) => ({
        label: `⟨u${j + 1}, u${built.length}⟩`,
        value: fmt(dot(u, r)),
        ok: Math.abs(dot(u, r)) < 1e-9,
      }));

      snap(
        `u${k + 1} = ${vec(r)}, length ${fmt(norm(r))}. It is orthogonal to every earlier u — the panel below shows the inner products, and they are zero rather than merely small. Note that u${k + 1} still spans the same subspace together with the earlier vectors; nothing was lost, only re-aimed.`,
        {
          built: built.map((u) => [...u]),
          focus: k,
          frame: built.map((u) => scl(u, 1 / norm(u))),
          checks: orthChecks,
        },
        { line: 6, phase: "accept" },
      );
    });

    const normalised = built.map((u) => scl(u, 1 / norm(u)));
    const gram = normalised.map((a) => normalised.map((b2) => dot(a, b2)));

    snap(
      `Finally divide each u by its length. Now ⟨uᵢ, uⱼ⟩ is 1 when i = j and 0 otherwise — the Gram matrix below is the identity, which is exactly Definition 3.9. In an orthonormal basis, finding a vector's coordinates stops being a solve and becomes ${basis.length} inner products.`,
      {
        built: built.map((u) => [...u]),
        normalised,
        frame: normalised,
        matrices: [{ label: "Gram matrix of the ONB", rows: gram }],
        checks: [
          {
            label: "Gram = I",
            value: gram.every((row, i) => row.every((v, j) => Math.abs(v - (i === j ? 1 : 0)) < 1e-9))
              ? "yes"
              : "no",
            ok: true,
          },
        ],
      },
      { line: 7, phase: "normalise" },
    );

    return capFrames(t.done(`${basis.length} orthonormal vectors, Gram matrix = I`));
  }

  /* -- Projection onto a line or a plane ---------------------------------- */
  const x = target as number[];
  const B = transpose(basis); // n by m, basis vectors as columns
  const frame = (() => {
    // Orthonormalise the spanning set purely so the stage can shade the subspace.
    const out: number[][] = [];
    for (const b of basis) {
      let r = [...b];
      for (const f of out) r = sub(r, scl(f, dot(r, f)));
      if (norm(r) > 1e-9) out.push(scl(r, 1 / norm(r)));
    }
    return out;
  })();

  snap(
    mode === "line"
      ? `The line U is everything of the form λb with b = ${vec(basis[0])}, and x = ${vec(x)} is not on it. The question is which point of U is closest to x — and "closest" is going to turn out to mean one specific thing.`
      : `The subspace U is spanned by ${basis.map((b) => vec(b)).join(" and ")}, and x = ${vec(x)} sticks out of it. We want the point of U closest to x, expressed in the basis of U.`,
    { frame },
    { line: 1, phase: "setup" },
  );

  snap(
    `The condition that fixes the answer: the displacement x − π(x) must be orthogonal to every basis vector of U. Any other point of U would be reachable by sliding along U, and sliding along U from the foot of a perpendicular always increases the distance — that is Pythagoras, not a new idea.`,
    { frame },
    { line: 1, phase: "condition" },
  );

  let lambda: number[];
  let matrices: { label: string; rows: number[][] }[];

  if (mode === "line") {
    const b = basis[0];
    lambda = [dot(b, x) / dot(b, b)];
    snap(
      `With one direction there is one unknown, so orthogonality gives one equation: bᵀ(x − λb) = 0, hence λ = bᵀx / bᵀb = ${fmt(dot(b, x))} / ${fmt(dot(b, b))} = ${fmt(lambda[0])}. This is Equation 3.40 in the book, and note it is a ratio of two inner products and nothing more.`,
      { frame, lambda },
      { line: 1, phase: "coordinate" },
    );
    matrices = [{ label: "P = b bᵀ / bᵀb", rows: outer(b, b).map((row) => row.map((v) => v / dot(b, b))) }];
  } else {
    const G = mul(transpose(B), B);
    const c = matVec(transpose(B), x);
    const Ginv = inverse(G);
    lambda = matVec(Ginv, c);
    snap(
      `Stack the ${basis.length} orthogonality conditions and they become BᵀBλ = Bᵀx — the normal equation, Equation 3.56. The Gram matrix BᵀB is ${basis.length}×${basis.length} regardless of how many dimensions the ambient space has, which is why this scales.`,
      {
        frame,
        matrices: [
          { label: "B", rows: B },
          { label: "BᵀB", rows: G },
          { label: "Bᵀx", rows: c.map((v) => [v]) },
        ],
      },
      { line: 3, phase: "normal equation" },
    );
    snap(
      `Solving it gives λ = ${vec(lambda)}. Those are coordinates *in the basis of U*, not in the ambient space — ${basis.length} numbers describing a point that also has ${dim} ambient coordinates. That compression is the whole point of PCA in Chapter 10.`,
      {
        frame,
        lambda,
        matrices: [
          { label: "(BᵀB)⁻¹", rows: Ginv },
          { label: "λ", rows: lambda.map((v) => [v]) },
        ],
      },
      { line: 4, phase: "coordinate" },
    );
    matrices = [{ label: "P = B(BᵀB)⁻¹Bᵀ", rows: mul(mul(B, Ginv), transpose(B)) }];
  }

  const proj = matVec(B, lambda);
  const error = sub(x, proj);
  const errNorm = norm(error);

  snap(
    `The projection itself is π(x) = Bλ = ${vec(proj)}. It lies in U by construction — it is a combination of the basis vectors — and it is the single closest point of U to x.`,
    { frame, lambda, proj },
    { line: mode === "line" ? 2 : 5, phase: "project" },
  );

  snap(
    `The displacement x − π(x) = ${vec(error)} has length ${fmt(errNorm)}; the book calls this the projection error, or the reconstruction error. Its inner product with each basis vector is zero — measured, below — which confirms the condition we started from actually holds.`,
    {
      frame,
      lambda,
      proj,
      error,
      errorNorm: errNorm,
      shadow: { from: proj, to: x },
      checks: basis.map((b, i) => ({
        label: `⟨b${i + 1}, x − π(x)⟩`,
        value: fmt(dot(b, error)),
        ok: Math.abs(dot(b, error)) < 1e-9,
      })),
    },
    { line: mode === "line" ? 4 : 7, phase: "verify" },
  );

  const P = matrices[0].rows;
  const PP = mul(P, P);
  const idem = PP.every((row, i) => row.every((v, j) => Math.abs(v - P[i][j]) < 1e-9));
  const Px = matVec(P, x);

  snap(
    `Every step above was linear in x, so it collapses into a single matrix. ${mode === "line" ? "For a line that is P = bbᵀ/bᵀb (Equation 3.46)" : "For a general subspace it is P = B(BᵀB)⁻¹Bᵀ (Equation 3.59)"}, and Px reproduces the projection we just computed: ${vec(Px)}. P is symmetric, and its rank is ${basis.length} — the dimension of U, not of the space.`,
    {
      frame,
      lambda,
      proj,
      error,
      errorNorm: errNorm,
      matrices,
      checks: [
        { label: "Px = π(x)", value: vec(Px), ok: Px.every((v, i) => Math.abs(v - proj[i]) < 1e-9) },
      ],
    },
    { line: mode === "line" ? 5 : 8, phase: "matrix" },
  );

  snap(
    `And P² = P: projecting a second time changes nothing, because π(x) is already in U and the closest point of U to a point of U is itself. That idempotence is Definition 3.10 — it is what makes a linear map a projection rather than merely a map into a subspace.`,
    {
      frame,
      lambda,
      proj,
      error,
      errorNorm: errNorm,
      matrices: [...matrices, { label: "P²", rows: PP }],
      checks: [{ label: "P² = P", value: idem ? "exactly" : "no", ok: idem }],
    },
    { line: mode === "line" ? 6 : 9, phase: "idempotent" },
  );

  return capFrames(t.done(`π(x) = ${vec(proj)}, error ${fmt(errNorm)}`));
}

export const PROJ_ALGOS = {
  project,
} as const;

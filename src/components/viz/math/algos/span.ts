/**
 * algos/span.ts — building a span one vector at a time, testing each new vector
 * against what is already there.
 *
 * This is the trace that makes §2.5 and §2.6 concrete. Linear independence is
 * usually presented as a condition to *check* — solve the homogeneous system,
 * look at the pivots — and that framing hides what the concept is for. Adding
 * vectors one at a time makes the question a decision: does this vector reach
 * somewhere the previous ones could not?
 *
 * The book's own procedure is the one implemented here (§2.6.1, Remark after
 * Example 2.16): write the candidate vectors as the columns of a matrix, reduce
 * to row-echelon form, and the vectors belonging to pivot columns are a basis.
 * Crucially the book notes that "there is an ordering of vectors when the matrix
 * is built" — so which vectors survive depends on the order they are offered in,
 * and that is exactly what a step-through can show and a static figure cannot.
 *
 * Dimension is 2 or 3. Beyond that there is nothing to draw, and the interesting
 * cases (a vector that lies in the plane of the previous two; three vectors that
 * happen to be coplanar) all occur by dimension 3.
 */
import { tracer, capFrames, type Trace } from "../../frames";

const EPS = 1e-9;

export interface SpanInput {
  /** Candidate vectors, offered in this order. Each of length `dim`. */
  vectors: number[][];
  /** Ambient dimension. 2 or 3. */
  dim?: 2 | 3;
}

export interface SpanState {
  /** Every candidate, in offer order. */
  vectors: number[][];
  dim: number;
  /** Indices accepted into the basis so far. */
  basis: number[];
  /** Indices rejected as dependent, with the combination that reproduces them. */
  rejected: { index: number; combo: number[] }[];
  /** The candidate this frame is deciding about, or null on the summary frames. */
  testing: number | null;
  /** Verdict for `testing` once the frame has decided. */
  verdict: "accepted" | "rejected" | null;
  /**
   * What the accepted set currently spans: 0 = the origin only, 1 = a line,
   * 2 = a plane, 3 = all of space. Equals `basis.length`.
   */
  spanDim: number;
  /** Orthonormal directions spanning the current subspace, for drawing it. */
  frame: number[][];
}

const CODE = [
  "basis = []",
  "for v in vectors:                      # order matters",
  "    r = v - project(v, span(basis))    # what v adds that basis cannot reach",
  "    if norm(r) > tol:",
  "        basis.append(v)                # a genuinely new direction",
  "    else:",
  "        record v as a combination of basis   # linearly dependent",
  "rank = len(basis)",
];

const dot = (a: number[], b: number[]) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = (a: number[]) => Math.sqrt(dot(a, a));
const sub = (a: number[], b: number[]) => a.map((x, i) => x - b[i]);
const scale = (a: number[], k: number) => a.map((x) => x * k);

const fmt = (v: number) => {
  const z = Math.abs(v) < 1e-10 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(2)));
};

/**
 * Gram–Schmidt against the current orthonormal frame.
 *
 * Returns the residual (what the candidate adds) and the coefficients of its
 * projection onto that frame. Using an orthonormal frame rather than solving a
 * least-squares system each step keeps the arithmetic transparent: the residual
 * norm *is* the distance from the candidate to the current subspace, which is
 * the number the caption quotes.
 */
function residual(v: number[], frame: number[][]) {
  let r = [...v];
  const coeffs: number[] = [];
  for (const f of frame) {
    const c = dot(r, f);
    coeffs.push(c);
    r = sub(r, scale(f, c));
  }
  return { r, coeffs };
}

/** Coefficients expressing `v` in terms of the accepted original vectors. */
function comboInBasis(v: number[], accepted: number[][]): number[] {
  // Small normal-equation solve: accepted is at most 3 vectors, so a direct
  // Gaussian elimination on the Gram matrix is clearer than pulling in a solver.
  const k = accepted.length;
  if (k === 0) return [];
  const G: number[][] = Array.from({ length: k }, (_, i) =>
    Array.from({ length: k + 1 }, (_, j) => (j < k ? dot(accepted[i], accepted[j]) : dot(accepted[i], v))),
  );
  // Forward elimination, then back-substitution.
  for (let c = 0; c < k; c++) {
    let p = c;
    for (let i = c; i < k; i++) if (Math.abs(G[i][c]) > Math.abs(G[p][c])) p = i;
    if (Math.abs(G[p][c]) < EPS) continue;
    [G[c], G[p]] = [G[p], G[c]];
    for (let i = c + 1; i < k; i++) {
      const f = G[i][c] / G[c][c];
      for (let j = c; j <= k; j++) G[i][j] -= f * G[c][j];
    }
  }
  const out = new Array(k).fill(0);
  for (let i = k - 1; i >= 0; i--) {
    if (Math.abs(G[i][i]) < EPS) continue;
    let s = G[i][k];
    for (let j = i + 1; j < k; j++) s -= G[i][j] * out[j];
    out[i] = s / G[i][i];
  }
  return out;
}

const SPAN_WORD = ["just the origin", "a line", "a plane", "all of space"];

export function span({ vectors, dim = 2 }: SpanInput): Trace<SpanState> {
  const t = tracer<SpanState>(CODE);
  const basis: number[] = [];
  const rejected: { index: number; combo: number[] }[] = [];
  const frame: number[][] = [];

  const snap = (
    caption: string,
    extra: { testing?: number | null; verdict?: SpanState["verdict"]; line?: number; phase?: string } = {},
  ) =>
    t.push(
      {
        vectors: vectors.map((v) => [...v]),
        dim,
        basis: [...basis],
        rejected: rejected.map((r) => ({ index: r.index, combo: [...r.combo] })),
        testing: extra.testing ?? null,
        verdict: extra.verdict ?? null,
        spanDim: basis.length,
        frame: frame.map((f) => [...f]),
      },
      caption,
      {
        line: extra.line,
        phase: extra.phase,
        watch: [
          { label: "accepted", value: basis.length },
          { label: "rank so far", value: basis.length, tone: "good" },
          { label: "spans", value: SPAN_WORD[Math.min(basis.length, 3)] },
        ],
      },
    );

  snap(
    `${vectors.length} candidate vector${vectors.length === 1 ? "" : "s"} in R^${dim}, and an empty basis. Each one will be offered in turn, and the only question asked of it is whether it reaches somewhere the ones already accepted cannot.`,
    { line: 1, phase: "setup" },
  );

  vectors.forEach((v, i) => {
    const accepted = basis.map((b) => vectors[b]);
    const { r } = residual(v, frame);
    const rn = norm(r);
    const vn = norm(v);

    snap(
      basis.length === 0
        ? `Testing v${i + 1} = (${v.map(fmt).join(", ")}). Nothing has been accepted yet, so the current span is just the origin — anything nonzero reaches further than that.`
        : `Testing v${i + 1} = (${v.map(fmt).join(", ")}) against the ${SPAN_WORD[Math.min(basis.length, 3)]} already spanned. Subtract off the part that lies inside it; what is left over is what v${i + 1} genuinely adds.`,
      { testing: i, line: 3, phase: "test" },
    );

    if (vn < EPS) {
      rejected.push({ index: i, combo: new Array(basis.length).fill(0) });
      snap(
        `v${i + 1} is the zero vector. It adds nothing and, by the book's own remark, any set containing the zero vector is automatically linearly dependent.`,
        { testing: i, verdict: "rejected", line: 7, phase: "reject" },
      );
      return;
    }

    // Relative test, not absolute: a long vector can have a small residual and
    // still be independent, and a short one the reverse.
    if (rn / vn > 1e-7) {
      basis.push(i);
      frame.push(scale(r, 1 / rn));
      snap(
        `The leftover has length ${fmt(rn)}, which is not zero — so v${i + 1} points somewhere genuinely new. Accept it. The span grows to ${SPAN_WORD[Math.min(basis.length, 3)]}, and the rank is now ${basis.length}.`,
        { testing: i, verdict: "accepted", line: 5, phase: "accept" },
      );
    } else {
      const combo = comboInBasis(v, accepted);
      const written = combo
        .map((c, k) => `${fmt(c)}·v${basis[k] + 1}`)
        .join(" + ")
        .replace(/\+ -/g, "- ");
      rejected.push({ index: i, combo });
      snap(
        `The leftover is ${rn < 1e-12 ? "exactly zero" : `only ${rn.toExponential(1)} long`} — v${i + 1} already lies inside the span. It is a linear combination of what we have: v${i + 1} = ${written}. Reject it; the set is linearly dependent and this is the redundant member.`,
        { testing: i, verdict: "rejected", line: 7, phase: "reject" },
      );
    }
  });

  const rank = basis.length;
  const full = rank === dim;

  snap(
    full
      ? `Finished. ${rank} of ${vectors.length} vectors were accepted, and because the rank equals the ambient dimension ${dim}, they are a basis for the whole of R^${dim} — every vector in the space is a unique combination of them.`
      : `Finished. Rank ${rank} out of a possible ${dim}, so the accepted vectors are a basis for ${SPAN_WORD[rank]} inside R^${dim} — a proper subspace. ${vectors.length - rank} candidate${vectors.length - rank === 1 ? " was" : "s were"} redundant.`,
    { line: 8, phase: "result" },
  );

  if (rejected.length > 0) {
    snap(
      `One thing to notice: which vectors got rejected depends on the order they were offered in. The book says so explicitly — building the matrix imposes an ordering. A different order can produce a different basis, but never a different rank.`,
      { line: 8, phase: "result" },
    );
  }

  return capFrames(t.done(`rank ${rank}, spanning ${SPAN_WORD[Math.min(rank, 3)]}`));
}

export const SPAN_ALGOS = {
  span,
} as const;

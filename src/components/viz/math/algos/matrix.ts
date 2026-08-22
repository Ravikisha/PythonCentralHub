/**
 * algos/matrix.ts — what a 2×2 matrix does to the plane, one column at a time.
 *
 * The trace exists to make one specific claim visible: **the columns of A are
 * the images of the basis vectors, and everything else follows by linearity.**
 * Pages state that in a sentence and readers nod without believing it. Here it
 * is built: frame 2 places `A e₁`, frame 3 places `A e₂`, frame 4 completes the
 * parallelogram they span, and frame 5 shows the whole grid following. Nothing
 * is drawn that was not derived from a column.
 *
 * SCOPE: 2×2 only, deliberately. A 3×3 map needs a projection to be drawn at
 * all, and a reader trying to decide whether the third basis vector went *into*
 * the screen or out of it is not learning linear algebra. The determinant page
 * (§4.1) covers 3×3 by hand and by Laplace expansion instead.
 */
import { tracer, capFrames, type Trace } from "../../frames";

const EPS = 1e-12;

export interface MatrixInput {
  /** A 2×2 matrix, row-major: `[[a, b], [c, d]]`. */
  matrix: number[][];
  /**
   * A vector to push through the map after the basis columns are established,
   * demonstrating that `A(x₁e₁ + x₂e₂) = x₁(Ae₁) + x₂(Ae₂)`.
   */
  probe?: [number, number];
  /** Show the eigenvector frames. Skipped when the eigenvalues are complex. */
  eigen?: boolean;
}

export interface MatrixState {
  A: number[][];
  /** Images of the basis vectors, revealed one per frame: `[Ae₁, Ae₂]`. */
  columns: (number[] | null)[];
  /** Draw the parallelogram the revealed columns span. */
  cell: boolean;
  /** Draw the whole transformed grid. */
  grid: boolean;
  det: number;
  /** The probe vector and its image, once that frame is reached. */
  probe: { v: number[]; image: number[]; combo: string } | null;
  /** Real eigen-directions, as unit vectors paired with their eigenvalue. */
  eigen: { value: number; vector: number[] }[] | null;
  /** Which piece the caption is talking about, for a highlight. */
  focus: "none" | "col0" | "col1" | "cell" | "grid" | "probe" | "eigen";
}

const CODE = [
  "e1, e2 = (1, 0), (0, 1)          # the basis we start from",
  "A @ e1  ==  A[:, 0]              # first column IS the image of e1",
  "A @ e2  ==  A[:, 1]              # second column IS the image of e2",
  "# linearity: A(x1 e1 + x2 e2) = x1 (A e1) + x2 (A e2)",
  "det(A) = a*d - b*c               # signed area of the image of the unit square",
  "A @ v = lam * v                  # an eigenvector keeps its direction",
];

const show = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(2));

const apply = (A: number[][], v: number[]) => [
  A[0][0] * v[0] + A[0][1] * v[1],
  A[1][0] * v[0] + A[1][1] * v[1],
];

/**
 * Real eigenpairs of a 2×2, or null when the discriminant is negative.
 *
 * Solved from the characteristic polynomial rather than by iteration, because
 * this lab is about the *definition* of an eigenvector; the iterative story is
 * `EigenLab`'s job (§4.2).
 */
function realEigen(A: number[][]): { value: number; vector: number[] }[] | null {
  const [[a, b], [c, d]] = A;
  const tr = a + d;
  const det = a * d - b * c;
  const disc = tr * tr - 4 * det;
  if (disc < -EPS) return null; // a rotation: no real invariant direction

  const root = Math.sqrt(Math.max(disc, 0));
  const values = [(tr + root) / 2, (tr - root) / 2];

  return values.map((lam) => {
    // (A − λI)v = 0. Take whichever row is not degenerate.
    let v: number[];
    if (Math.abs(b) > EPS) v = [b, lam - a];
    else if (Math.abs(c) > EPS) v = [lam - d, c];
    else v = Math.abs(a - lam) < EPS ? [1, 0] : [0, 1]; // already diagonal
    const n = Math.hypot(v[0], v[1]) || 1;
    return { value: lam, vector: [v[0] / n, v[1] / n] };
  });
}

export function transform({ matrix, probe, eigen = true }: MatrixInput): Trace<MatrixState> {
  const A = [
    [matrix[0][0], matrix[0][1]],
    [matrix[1][0], matrix[1][1]],
  ];
  const det = A[0][0] * A[1][1] - A[0][1] * A[1][0];
  const c0 = apply(A, [1, 0]);
  const c1 = apply(A, [0, 1]);
  const pairs = eigen ? realEigen(A) : null;

  const t = tracer<MatrixState>(CODE);

  const base: MatrixState = {
    A,
    columns: [null, null],
    cell: false,
    grid: false,
    det,
    probe: null,
    eigen: null,
    focus: "none",
  };

  const snap = (
    caption: string,
    state: Partial<MatrixState>,
    extra: { line?: number; phase?: string } = {},
  ) =>
    t.push({ ...base, ...state }, caption, {
      ...extra,
      watch: [
        { label: "det A", value: show(det), tone: Math.abs(det) < 1e-9 ? "bad" : "info" },
        { label: "A e1", value: `(${show(c0[0])}, ${show(c0[1])})` },
        { label: "A e2", value: `(${show(c1[0])}, ${show(c1[1])})` },
      ],
    });

  snap(
    "The plane before anything happens, with the standard basis e1 = (1, 0) and e2 = (0, 1) and the unit square they span.",
    {},
    { line: 1, phase: "basis" },
  );

  snap(
    `e1 lands on (${show(c0[0])}, ${show(c0[1])}) — which is literally the first column of A. Reading a column is the same as applying A to a basis vector.`,
    { columns: [c0, null], focus: "col0" },
    { line: 2, phase: "columns" },
  );

  snap(
    `e2 lands on (${show(c1[0])}, ${show(c1[1])}) — the second column. A 2×2 matrix is exactly "where the two basis vectors go", nothing more.`,
    { columns: [c0, c1], focus: "col1" },
    { line: 3, phase: "columns" },
  );

  snap(
    "Those two images span a parallelogram: the image of the unit square. Every other point of the plane is now determined, because a linear map is fixed by what it does to a basis.",
    { columns: [c0, c1], cell: true, focus: "cell" },
    { line: 4, phase: "linearity" },
  );

  if (probe) {
    const image = apply(A, probe);
    snap(
      `Check linearity on v = (${show(probe[0])}, ${show(probe[1])}): ${show(probe[0])}·Ae1 + ${show(probe[1])}·Ae2 = (${show(image[0])}, ${show(image[1])}). Same answer as multiplying A by v, because it is the same computation.`,
      {
        columns: [c0, c1],
        cell: true,
        focus: "probe",
        probe: {
          v: probe,
          image,
          combo: `${show(probe[0])}·Ae1 + ${show(probe[1])}·Ae2`,
        },
      },
      { line: 4, phase: "linearity" },
    );
  }

  snap(
    "The whole grid follows the basis. Straight lines stay straight and evenly spaced lines stay evenly spaced — that is what linearity looks like.",
    { columns: [c0, c1], cell: true, grid: true, focus: "grid" },
    { line: 4, phase: "grid" },
  );

  const areaCaption =
    Math.abs(det) < 1e-9
      ? `det A = 0. The parallelogram has collapsed to a line: A squashes the plane onto a one-dimensional subspace, so it throws information away and cannot be inverted.`
      : det < 0
        ? `det A = ${show(det)}. The magnitude ${show(Math.abs(det))} is the area of the parallelogram; the minus sign says the map flipped orientation — e1 and e2 swapped handedness.`
        : `det A = ${show(det)}. That is the area of the parallelogram, and the factor by which A scales every area in the plane.`;

  snap(areaCaption, { columns: [c0, c1], cell: true, grid: true, focus: "cell" }, {
    line: 5,
    phase: "determinant",
  });

  if (eigen) {
    if (pairs) {
      snap(
        `A has real eigenvalues ${show(pairs[0].value)} and ${show(pairs[1].value)}. Along each eigenvector the map only stretches — the direction survives untouched. Every other direction gets rotated as well as scaled.`,
        { columns: [c0, c1], cell: true, grid: true, eigen: pairs, focus: "eigen" },
        { line: 6, phase: "eigen" },
      );
    } else {
      snap(
        "The characteristic polynomial has no real roots, so there is no direction this map leaves alone: every vector gets turned. That is the algebraic signature of a rotation, and the reason §4.2 needs complex eigenvalues.",
        { columns: [c0, c1], cell: true, grid: true, focus: "eigen" },
        { line: 6, phase: "eigen" },
      );
    }
  }

  const result =
    Math.abs(det) < 1e-9
      ? "singular: the plane collapses to a line"
      : `area scaled by ${show(Math.abs(det))}${det < 0 ? ", orientation flipped" : ""}`;

  return capFrames(t.done(result));
}

export const MATRIX_ALGOS = {
  transform,
} as const;

/**
 * algos/elimination.ts — Gaussian elimination, one row operation per frame.
 *
 * This is the algorithm §2.3 is about, and the reason it gets a step-through
 * rather than a p5 sketch is that the hard part is bookkeeping, not geometry.
 * A reader who is lost is lost at a specific row operation: "why is that row
 * being multiplied by −1.5 before it is added?" An animation cannot answer
 * that. A frame with a caption and the multiplier in the watch panel can.
 *
 * Two deliberate choices about *which* Gaussian elimination this is:
 *
 * 1. **Textbook pivoting, not partial pivoting.** A row is only swapped when
 *    the pivot position is zero. Libraries always swap to the largest available
 *    magnitude because it is numerically better, and the §2.3 page says so in
 *    its pitfalls — but showing that here would mean the trace does not match
 *    the elimination the reader is doing by hand on the same matrix, which is
 *    the whole point of the lab.
 * 2. **Exact rational-ish arithmetic is not attempted.** Values are float64,
 *    displayed rounded. `EPS` decides what counts as zero, and the page names
 *    that as the reason `matrix_rank` takes a tolerance.
 */
import { tracer, capFrames, type Trace } from "../../frames";

/** Below this magnitude an entry is treated as zero for pivot selection. */
const EPS = 1e-10;

export interface ElimInput {
  /** Coefficient matrix, row-major. Every row must be the same length. */
  matrix: number[][];
  /** Optional right-hand side. When present the trace ends with the solution. */
  rhs?: number[];
  /** Continue past row echelon form to reduced row echelon form. */
  reduced?: boolean;
}

export interface ElimState {
  /** The augmented matrix as it stands, including any rhs columns. */
  rows: number[][];
  /** How many of those columns are coefficients. The rest are the rhs. */
  coefCols: number;
  /** Current pivot position, or null before the first / after the last. */
  pivot: [number, number] | null;
  /** Row currently being rewritten. */
  activeRow: number | null;
  /** Row being used to rewrite it. */
  sourceRow: number | null;
  /** Entries this step drove to zero, for a one-frame highlight. */
  cleared: [number, number][];
  /** Rows already finished and no longer touched. */
  settled: number[];
  /** The row operation in the notation the page uses, e.g. `R3 <- R3 - 2 R1`. */
  op: string | null;
  /** Pivot columns found so far. Its length is the rank. */
  pivotCols: number[];
}

const CODE = [
  "r = 0                                  # current pivot row",
  "for c in range(n_cols):                # walk the columns",
  "    p = first row >= r with A[p][c] != 0",
  "    if p is None: continue             # no pivot in this column",
  "    if p != r: swap(A[r], A[p])",
  "    for i in range(r + 1, n_rows):     # clear below the pivot",
  "        f = A[i][c] / A[r][c]",
  "        A[i] -= f * A[r]",
  "    r += 1",
  "# reduced form: normalise each pivot to 1, then clear upwards",
  "for each pivot (r, c) in reverse:",
  "    A[r] /= A[r][c]",
  "    for i in range(r):",
  "        A[i] -= A[i][c] * A[r]",
];

/** Round for display only. The algorithm always carries full precision. */
const show = (v: number) => {
  const r = Math.abs(v) < EPS ? 0 : v;
  return Number.isInteger(r) ? String(r) : r.toFixed(3).replace(/\.?0+$/, "");
};

const clone = (rows: number[][]) => rows.map((r) => [...r]);

/** `R3 <- R3 - 2 R1`, with the multiplier printed the way a reader would write it. */
function opLabel(target: number, source: number, factor: number): string {
  const f = Math.abs(factor);
  const sign = factor > 0 ? "-" : "+";
  const mult = Math.abs(f - 1) < EPS ? "" : `${show(f)} `;
  return `R${target + 1} <- R${target + 1} ${sign} ${mult}R${source + 1}`;
}

export function elimination({ matrix, rhs, reduced = false }: ElimInput): Trace<ElimState> {
  const nRows = matrix.length;
  const coefCols = matrix[0]?.length ?? 0;
  const hasRhs = Array.isArray(rhs) && rhs.length === nRows;

  // The augmented matrix is the single object the trace mutates. Coefficient
  // columns first, rhs appended — which is exactly how the page writes it.
  let rows: number[][] = matrix.map((row, i) => (hasRhs ? [...row, rhs![i]] : [...row]));

  const t = tracer<ElimState>(CODE);
  const pivotCols: number[] = [];
  const settled: number[] = [];

  const snap = (
    caption: string,
    extra: Partial<ElimState> & { line?: number; phase?: string } = {},
  ) => {
    const { line, phase, ...state } = extra;
    t.push(
      {
        rows: clone(rows),
        coefCols,
        pivot: null,
        activeRow: null,
        sourceRow: null,
        cleared: [],
        settled: [...settled],
        op: null,
        pivotCols: [...pivotCols],
        ...state,
      },
      caption,
      {
        line,
        phase,
        watch: [
          { label: "pivots", value: pivotCols.length },
          { label: "rank so far", value: pivotCols.length },
        ],
      },
    );
  };

  snap(
    hasRhs
      ? `The augmented matrix. The last column is the right-hand side; every row is one equation.`
      : `The starting matrix. Elimination will not change its row space, only its shape.`,
    { line: 1, phase: "setup" },
  );

  // ---- Forward elimination: down the columns, one pivot at a time ----------
  let r = 0;
  for (let c = 0; c < coefCols && r < nRows; c++) {
    // Find a pivot in this column, at or below row r.
    let p = -1;
    for (let i = r; i < nRows; i++) {
      if (Math.abs(rows[i][c]) > EPS) {
        p = i;
        break;
      }
    }

    if (p === -1) {
      snap(
        `Column ${c + 1} has no nonzero entry at or below row ${r + 1}, so it holds no pivot. This column's variable is free.`,
        { line: 4, phase: "forward" },
      );
      continue;
    }

    if (p !== r) {
      snap(
        `Row ${r + 1} has a zero where the pivot must go, so swap it with row ${p + 1}, which does not.`,
        { line: 5, phase: "forward", activeRow: r, sourceRow: p, op: `R${r + 1} <-> R${p + 1}` },
      );
      [rows[r], rows[p]] = [rows[p], rows[r]];
      snap(`Swapped. Row ${r + 1} now leads with ${show(rows[r][c])}.`, {
        line: 5,
        phase: "forward",
        pivot: [r, c],
      });
    }

    pivotCols.push(c);
    snap(
      `Pivot ${pivotCols.length}: the ${show(rows[r][c])} at row ${r + 1}, column ${c + 1}. Everything below it in this column has to become zero.`,
      { line: 3, phase: "forward", pivot: [r, c] },
    );

    for (let i = r + 1; i < nRows; i++) {
      if (Math.abs(rows[i][c]) <= EPS) {
        snap(`Row ${i + 1} already has a zero in column ${c + 1}. Nothing to do.`, {
          line: 6,
          phase: "forward",
          pivot: [r, c],
          activeRow: i,
        });
        continue;
      }

      const f = rows[i][c] / rows[r][c];
      snap(
        `Row ${i + 1} has ${show(rows[i][c])} where it needs a zero. The pivot is ${show(rows[r][c])}, so the multiplier is ${show(rows[i][c])} / ${show(rows[r][c])} = ${show(f)}.`,
        {
          line: 7,
          phase: "forward",
          pivot: [r, c],
          activeRow: i,
          sourceRow: r,
          op: opLabel(i, r, f),
        },
      );

      for (let k = 0; k < rows[i].length; k++) rows[i][k] -= f * rows[r][k];
      rows[i][c] = 0; // exact, not almost — the subtraction was designed to zero it

      snap(`Subtracting ${show(f)} times row ${r + 1} clears the entry.`, {
        line: 8,
        phase: "forward",
        pivot: [r, c],
        activeRow: i,
        sourceRow: r,
        cleared: [[i, c]],
        op: opLabel(i, r, f),
      });
    }

    settled.push(r);
    r++;
  }

  const rank = pivotCols.length;
  snap(
    `Row echelon form: ${rank} pivot${rank === 1 ? "" : "s"}, so the rank is ${rank}. Every entry below a pivot is zero.`,
    { line: 9, phase: "echelon" },
  );

  // ---- Reduced form: normalise, then clear upwards ------------------------
  if (reduced) {
    for (let k = pivotCols.length - 1; k >= 0; k--) {
      const pr = k;
      const pc = pivotCols[k];
      const lead = rows[pr][pc];

      if (Math.abs(lead - 1) > EPS) {
        snap(
          `Normalise pivot ${k + 1}: divide row ${pr + 1} by ${show(lead)} so the pivot becomes 1.`,
          {
            line: 12,
            phase: "reduced",
            pivot: [pr, pc],
            activeRow: pr,
            op: `R${pr + 1} <- R${pr + 1} / ${show(lead)}`,
          },
        );
        for (let j = 0; j < rows[pr].length; j++) rows[pr][j] /= lead;
        rows[pr][pc] = 1;
        snap(`Row ${pr + 1} now leads with 1.`, {
          line: 12,
          phase: "reduced",
          pivot: [pr, pc],
          activeRow: pr,
        });
      }

      for (let i = pr - 1; i >= 0; i--) {
        if (Math.abs(rows[i][pc]) <= EPS) continue;
        const f = rows[i][pc];
        snap(
          `Clear above pivot ${k + 1}: row ${i + 1} has ${show(f)} in column ${pc + 1}.`,
          {
            line: 14,
            phase: "reduced",
            pivot: [pr, pc],
            activeRow: i,
            sourceRow: pr,
            op: opLabel(i, pr, f),
          },
        );
        for (let j = 0; j < rows[i].length; j++) rows[i][j] -= f * rows[pr][j];
        rows[i][pc] = 0;
        snap(`Cleared. Column ${pc + 1} is now zero everywhere except its pivot.`, {
          line: 14,
          phase: "reduced",
          pivot: [pr, pc],
          activeRow: i,
          sourceRow: pr,
          cleared: [[i, pc]],
        });
      }
    }
  }

  // ---- Result -------------------------------------------------------------
  let result: string | undefined;
  if (hasRhs) {
    // Inconsistent iff some row is all-zero in the coefficients but not in the rhs.
    const inconsistent = rows.some(
      (row) =>
        row.slice(0, coefCols).every((v) => Math.abs(v) <= EPS) &&
        row.slice(coefCols).some((v) => Math.abs(v) > EPS),
    );

    if (inconsistent) {
      result = "no solution — a row reads 0 = nonzero";
      snap(
        `A row now says 0 = ${show(rows.find((row) => row.slice(0, coefCols).every((v) => Math.abs(v) <= EPS))![coefCols])}. The system is inconsistent: no vector satisfies all the equations at once.`,
        { phase: "result" },
      );
    } else if (rank < coefCols) {
      const free = coefCols - rank;
      result = `infinitely many solutions — ${free} free variable${free === 1 ? "" : "s"}`;
      snap(
        `${rank} pivots for ${coefCols} unknowns leaves ${free} free variable${free === 1 ? "" : "s"}, so the solution set is a particular solution plus the null space.`,
        { phase: "result" },
      );
    } else if (reduced) {
      const sol = pivotCols.map((_, i) => show(rows[i][coefCols]));
      result = `x = (${sol.join(", ")})`;
      snap(
        `Reduced row echelon form with a pivot in every column: the right-hand column is the solution, read straight off.`,
        { phase: "result" },
      );
    } else {
      result = `unique solution — back-substitute from the bottom row`;
      snap(
        `A pivot in every column means exactly one solution. Back-substitution from the last row recovers it; passing \`reduced\` makes the trace finish the job instead.`,
        { phase: "result" },
      );
    }
  } else {
    result = `rank ${rank} of ${Math.min(nRows, coefCols)} possible`;
  }

  return capFrames(t.done(result));
}

/** Registry, so a page can name an algorithm as a string like the DSA labs do. */
export const ELIM_ALGOS = {
  elimination,
} as const;

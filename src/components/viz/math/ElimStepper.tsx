/**
 * ElimStepper — Gaussian elimination, one row operation per frame.
 *
 * The stage is the augmented matrix itself, because that is what the reader has
 * on paper. Three things are highlighted and nothing else: the pivot (a ring),
 * the row being rewritten (amber), and the row it is being rewritten with
 * (blue). The row operation is printed in the notation the page uses, so the
 * reader can copy it into their own working.
 *
 * MDX usage:
 *
 *     import ElimStepper from "../../../../components/viz/math/ElimStepper.tsx";
 *
 *     <ElimStepper
 *       client:visible
 *       matrix={[[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]}
 *       rhs={[8, -11, -3]}
 *       reduced
 *       title="Three pivots turn a system into an answer"
 *       desc="The ring marks the pivot. Every operation below it is chosen to put a zero under that ring."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { elimination, type ElimInput, type ElimState } from "./algos/elimination";
import { MatrixGrid, Scalars } from "./stage";

export interface ElimStepperProps extends ElimInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

/** Display rounding. The trace itself always carries full precision. */
const fmt = (v: number) => {
  const z = Math.abs(v) < 1e-10 ? 0 : v;
  if (Number.isInteger(z)) return String(z);
  const r = Number(z.toFixed(3));
  return Number.isInteger(r) ? String(r) : String(r);
};

function renderStage(frame: Frame<ElimState>) {
  const st = frame.state;
  const clearedSet = new Set(st.cleared.map(([r, c]) => `${r}-${c}`));

  const cellClass = (r: number, c: number) => {
    const classes: string[] = [];
    if (st.pivot && st.pivot[0] === r && st.pivot[1] === c) classes.push("pch-mz__cell--pivot");
    if (clearedSet.has(`${r}-${c}`)) classes.push("pch-mz__cell--good");
    else if (st.activeRow === r) classes.push("pch-mz__cell--active");
    else if (st.sourceRow === r) classes.push("pch-mz__cell--info");
    else if (st.settled.includes(r) && st.activeRow === null) classes.push("pch-mz__cell--muted");
    return classes.join(" ") || undefined;
  };

  const hasRhs = st.rows[0] !== undefined && st.rows[0].length > st.coefCols;

  return (
    <div>
      <div className="pch-mz__row">
        <MatrixGrid
          rows={st.rows}
          cellClass={cellClass}
          format={fmt}
          divider={hasRhs ? st.coefCols : undefined}
        />
        {st.op && <span className="pch-mz__op">{st.op}</span>}
      </div>
      <Scalars
        items={[
          { label: "pivot columns", value: st.pivotCols.length ? st.pivotCols.map((c) => c + 1).join(", ") : "none yet" },
          { label: "rank", value: String(st.pivotCols.length) },
          ...(st.pivot ? [{ label: "pivot", value: `row ${st.pivot[0] + 1}, col ${st.pivot[1] + 1}` }] : []),
        ]}
      />
    </div>
  );
}

export default function ElimStepper({
  matrix,
  rhs,
  reduced = false,
  title,
  desc,
  lib,
  ms = 1100,
  autoPlay = true,
}: ElimStepperProps) {
  const trace = useMemo(
    () => elimination({ matrix, rhs, reduced }),
    [matrix, rhs, reduced],
  );

  return (
    <VizPlayer<ElimState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="matrix"
      lib={lib ?? (reduced ? "reduced row echelon form" : "row echelon form")}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

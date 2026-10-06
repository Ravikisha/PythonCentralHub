"use client";

/**
 * DPTable — step-through visualization for dynamic-programming table fills.
 *
 * Draws the table with **dependency arrows into the cell being written**. That
 * is the whole point: a recurrence like `dp[i][j] = dp[i-1][j-1] + 1` is easy to
 * read and hard to *believe* until you see which earlier cells it consumes, in
 * what order the table becomes safe to read, and why the base row exists.
 *
 * After the fill completes, algorithms that can reconstruct an answer highlight
 * the traced-back path — so "the table holds the length, not the answer" stops
 * being an abstract warning.
 *
 * MDX usage:
 *
 *     import DPTable from "../../../../components/viz/DPTable.tsx";
 *
 *     <DPTable
 *       client:visible
 *       algo="lcs"
 *       a="ABCBDAB"
 *       b="BDCABA"
 *       title="Filling the LCS table one cell at a time"
 *       desc="A match reads the diagonal; a mismatch takes the better of above and left."
 *     />
 *
 * See ./algos/dp.ts for the algorithm registry and each one's inputs.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame } from "./frames";
import { DP_ALGOS, type DPInput, type DPState } from "./algos/dp";

export interface DPTableProps extends DPInput {
  /** Key into the algorithm registry in ./algos/dp.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

/** Cell pitch in SVG user units — arrows need absolute geometry, so SVG it is. */
const CW = 46;
const CH = 38;
const GUTTER_X = 46;
const GUTTER_Y = 30;

const cellX = (c: number) => GUTTER_X + c * CW;
const cellY = (r: number) => GUTTER_Y + r * CH;
const midX = (c: number) => cellX(c) + CW / 2;
const midY = (r: number) => cellY(r) + CH / 2;

function Stage({ state }: { state: DPState }) {
  const rows = state.grid.length;
  const cols = Math.max(...state.grid.map((r) => r.length), 1);
  const width = GUTTER_X + cols * CW + 6;
  const height = GUTTER_Y + rows * CH + 6;

  const pathKeys = new Set((state.path ?? []).map((p) => `${p.r},${p.c}`));

  return (
    <div className="pch-vz-dp">
      {state.rowTitle || state.colTitle ? (
        <div className="pch-vz-dp__axes">
          {state.rowTitle ? <span className="pch-vz-dp__axis">rows: {state.rowTitle}</span> : null}
          {state.colTitle ? <span className="pch-vz-dp__axis">cols: {state.colTitle}</span> : null}
        </div>
      ) : null}

      <svg
        className="pch-vz-dp__svg"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Dynamic programming table"
        preserveAspectRatio="xMidYMin meet"
      >
        <defs>
          <marker
            id="pch-dp-arrow"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path className="pch-vz-dp__arrowhead" d="M0 0L10 5L0 10z" />
          </marker>
        </defs>

        {/* Column headers */}
        {state.colLabels?.slice(0, cols).map((label, c) => (
          <text key={`ch${c}`} className="pch-vz-dp__head" x={midX(c)} y={GUTTER_Y - 10} textAnchor="middle">
            {label}
          </text>
        ))}
        {/* Row headers */}
        {state.rowLabels?.slice(0, rows).map((label, r) => (
          <text
            key={`rh${r}`}
            className="pch-vz-dp__head"
            x={GUTTER_X - 8}
            y={midY(r)}
            dy="0.34em"
            textAnchor="end"
          >
            {label}
          </text>
        ))}

        {/* Cells */}
        {state.grid.map((row, r) =>
          row.map((cell, c) => {
            const isCursor = state.cursor?.r === r && state.cursor?.c === c;
            const onPath = pathKeys.has(`${r},${c}`);
            const tone = onPath ? "good" : (cell?.tone ?? "muted");
            return (
              <g
                key={`${r}-${c}`}
                className={`pch-vz-dp__cell tone-${tone}${cell ? "" : " is-empty"}${
                  isCursor ? " is-cursor" : ""
                }${onPath ? " is-path" : ""}`}
              >
                <rect x={cellX(c) + 1.5} y={cellY(r) + 1.5} width={CW - 3} height={CH - 3} rx={5} />
                {cell ? (
                  <text x={midX(c)} y={midY(r)} dy="0.34em" textAnchor="middle">
                    {cell.value}
                  </text>
                ) : null}
              </g>
            );
          }),
        )}

        {/* Dependency arrows, drawn last so they sit above the cells. */}
        {state.cursor && state.deps
          ? state.deps.map((d, i) => (
              <line
                key={`dep${i}`}
                className="pch-vz-dp__dep"
                x1={midX(d.c)}
                y1={midY(d.r)}
                x2={midX(state.cursor!.c)}
                y2={midY(state.cursor!.r)}
                markerEnd="url(#pch-dp-arrow)"
              />
            ))
          : null}
      </svg>
    </div>
  );
}

export default function DPTable({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: DPTableProps) {
  const trace = useMemo(() => {
    const fn = DP_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<DPState>[] };
    return fn(input as DPInput);
  }, [algo, input.a, input.b, input.target, JSON.stringify(input.values), JSON.stringify(input.weights)]);

  if (!DP_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--dp">dp</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown DPTable algo <code>{algo}</code>. Known keys: {Object.keys(DP_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<DPState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="dp"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

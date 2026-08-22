/**
 * ComplexityChart — growth-rate comparison on a log axis, with a live table.
 *
 * The one visualization here that is a chart rather than a data structure, and it
 * exists because Big-O is taught as notation and then used as intuition. Everyone
 * can recite that O(n²) beats O(2ⁿ); far fewer can say whether O(n²) passes at
 * n = 10⁵ without working it out. This makes that arithmetic visible.
 *
 * The horizontal budget line is at 10⁸ operations — roughly what an online judge
 * accepts in a second. Any curve crossing it is a time-limit exceeded, which is
 * what turns Big-O from notation into a decision procedure.
 *
 * MDX usage:
 *
 *     import ComplexityChart from "../../../../components/viz/ComplexityChart.tsx";
 *
 *     <ComplexityChart client:visible algo="growth"
 *       title="Read the constraint, not your instincts" />
 *
 *     <ComplexityChart client:visible algo="growth"
 *       curves={["O(n)", "O(n log n)", "O(n²)"]}
 *       ns={[100, 1000, 10000, 100000, 1000000]}
 *       title="The three that actually matter in interviews" />
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame } from "./frames";
import { COMPLEXITY_ALGOS, type ComplexityInput, type ComplexityState } from "./algos/complexity";

export interface ComplexityChartProps extends ComplexityInput {
  /** Registry key. Only `growth` exists so far, and it is the default. */
  algo?: string;
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const W = 600;
const H = 260;
const PAD_L = 52;
const PAD_R = 14;
const PAD_T = 14;
const PAD_B = 34;

/** Roughly what an online judge accepts in a second. */
const BUDGET = 1e8;

function Stage({ state }: { state: ComplexityState }) {
  const all = state.curves.flatMap((c) => c.points.filter((v) => Number.isFinite(v) && v > 0));
  const maxV = Math.max(BUDGET * 4, ...all);
  const minV = 1;

  // Log scale on both axes: n spans four orders of magnitude and the operation
  // counts span far more, so linear axes would show a single vertical wall.
  const lx = (i: number) => PAD_L + (i / Math.max(1, state.ns.length - 1)) * (W - PAD_L - PAD_R);
  const ly = (v: number) => {
    const clamped = Math.max(minV, Math.min(v, maxV));
    const frac = Math.log10(clamped) / Math.log10(maxV);
    return H - PAD_B - frac * (H - PAD_T - PAD_B);
  };

  const budgetY = ly(BUDGET);

  return (
    <div className="pch-vz-cx">
      <svg
        className="pch-vz-cx__svg"
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label="Growth rate comparison"
        preserveAspectRatio="xMidYMin meet"
      >
        {/* Decade gridlines */}
        {[1, 3, 6, 9, 12].map((e) =>
          10 ** e <= maxV ? (
            <g key={e}>
              <line className="pch-vz-cx__grid" x1={PAD_L} y1={ly(10 ** e)} x2={W - PAD_R} y2={ly(10 ** e)} />
              <text className="pch-vz-cx__axislabel" x={PAD_L - 6} y={ly(10 ** e)} dy="0.34em" textAnchor="end">
                1e{e}
              </text>
            </g>
          ) : null,
        )}

        {/* The budget line — the whole point of the chart */}
        <line className="pch-vz-cx__budget" x1={PAD_L} y1={budgetY} x2={W - PAD_R} y2={budgetY} />
        <text className="pch-vz-cx__budgetlabel" x={W - PAD_R} y={budgetY - 5} textAnchor="end">
          judge budget ≈ 1e8 ops
        </text>

        {/* n axis */}
        {state.ns.map((n, i) => (
          <text
            key={n}
            className={`pch-vz-cx__axislabel${state.cursor === i ? " is-here" : ""}`}
            x={lx(i)}
            y={H - PAD_B + 16}
            textAnchor="middle"
          >
            {n >= 1000 ? `${n / 1000}k` : n}
          </text>
        ))}

        {/* Cursor rule */}
        {state.cursor !== undefined ? (
          <line
            className="pch-vz-cx__cursor"
            x1={lx(state.cursor)}
            y1={PAD_T}
            x2={lx(state.cursor)}
            y2={H - PAD_B}
          />
        ) : null}

        {/* Curves, revealed up to the cursor so the trace builds them left to right */}
        {state.curves.map((c) => {
          const upto = state.cursor === undefined ? c.points.length - 1 : state.cursor;
          const pts = c.points
            .slice(0, upto + 1)
            .map((v, i) => `${lx(i)},${ly(v)}`)
            .join(" ");
          if (!pts) return null;
          return (
            <g key={c.label} className={`pch-vz-cx__curve tone-${c.tone}`}>
              <polyline points={pts} fill="none" />
              {c.points.slice(0, upto + 1).map((v, i) => (
                <circle key={i} cx={lx(i)} cy={ly(v)} r={2.6} />
              ))}
              <text className="pch-vz-cx__curvelabel" x={lx(upto) + 5} y={ly(c.points[upto]) - 4}>
                {c.label}
              </text>
            </g>
          );
        })}
      </svg>

      {state.table && state.table.length > 0 ? (
        <div className="pch-vz-cx__tablewrap">
          <table className="pch-vz-cx__table">
            <thead>
              <tr>
                <th>n</th>
                {state.curves.map((c) => (
                  <th key={c.label}>{c.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {state.table.map((row) => (
                <tr key={row.n}>
                  <th>{row.n.toLocaleString()}</th>
                  {row.cells.map((cell) => (
                    <td key={cell.label} className={`tone-${cell.tone}`}>
                      {cell.value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}

export default function ComplexityChart({
  algo = "growth",
  title,
  desc,
  lib,
  ms = 1400,
  autoPlay,
  ...input
}: ComplexityChartProps) {
  const trace = useMemo(() => {
    const fn = COMPLEXITY_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<ComplexityState>[] };
    return fn(input as ComplexityInput);
  }, [algo, JSON.stringify(input.curves), JSON.stringify(input.ns)]);

  if (!COMPLEXITY_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--chart">chart</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown ComplexityChart algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(COMPLEXITY_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<ComplexityState>
      frames={trace.frames}
      result={trace.result}
      title={title}
      tag="chart"
      lib={lib ?? "log scale"}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

/**
 * IntervalTimeline — step-through visualization for interval algorithms.
 *
 * Bars on a shared time axis, packed onto rows so overlapping intervals never
 * collide, plus an optional sweep line and a result band below the axis.
 *
 * The reason this earns a component: in every interval problem the **sort key** is
 * the algorithm, and the wrong key produces plausible code that fails on one
 * specific overlap shape. Seeing the bars in sorted order makes the choice
 * arguable rather than memorised — you can look at a greedy selection sorted by
 * end time and see why sorting by start time would have been worse.
 *
 * MDX usage:
 *
 *     import IntervalTimeline from "../../../../components/viz/IntervalTimeline.tsx";
 *
 *     <IntervalTimeline client:visible algo="merge"
 *       intervals={[[1,3],[2,6],[8,10],[15,18]]}
 *       title="Sort by start, then one linear pass" />
 *
 *     <IntervalTimeline client:visible algo="sweep-line"
 *       intervals={[[0,30],[5,10],[15,20],[6,12]]}
 *       title="No interval is ever compared with another" />
 *
 * See ./algos/intervals.ts for the registry.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame } from "./frames";
import { INTERVAL_ALGOS, type IntervalInput, type IntervalState } from "./algos/intervals";

export interface IntervalTimelineProps extends IntervalInput {
  /** Key into the algorithm registry in ./algos/intervals.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

const WIDTH = 620;
const PAD_L = 12;
const PAD_R = 12;
const ROW_H = 30;
const BAR_H = 20;
const AXIS_H = 26;

function Stage({ state }: { state: IntervalState }) {
  const span = Math.max(1, state.max - state.min);
  const usable = WIDTH - PAD_L - PAD_R;
  const x = (v: number) => PAD_L + ((v - state.min) / span) * usable;

  const rows = Math.max(1, ...state.bars.map((b) => b.row + 1));
  const resultRows = state.result && state.result.length > 0 ? 1 : 0;
  const barsH = rows * ROW_H;
  const height = barsH + AXIS_H + (resultRows ? ROW_H + 18 : 0) + 8;
  const axisY = barsH + 10;

  /** Ticks at the interval endpoints — the only coordinates that matter here. */
  const ticks = [...new Set(state.bars.flatMap((b) => [b.start, b.end]))].sort((a, b) => a - b);

  return (
    <div className="pch-vz-iv">
      <svg
        className="pch-vz-iv__svg"
        viewBox={`0 0 ${WIDTH} ${height}`}
        role="img"
        aria-label="Interval timeline"
        preserveAspectRatio="xMidYMin meet"
      >
        {/* Bars */}
        {state.bars.map((b, i) => {
          const bx = x(b.start);
          const bw = Math.max(3, x(b.end) - bx);
          return (
            <g key={i} className={`pch-vz-iv__bar tone-${b.tone ?? "info"}`}>
              <rect x={bx} y={b.row * ROW_H + 4} width={bw} height={BAR_H} rx={4} />
              {bw > 34 && b.label ? (
                <text x={bx + bw / 2} y={b.row * ROW_H + 4 + BAR_H / 2} dy="0.34em" textAnchor="middle">
                  {b.label}
                </text>
              ) : null}
            </g>
          );
        })}

        {/* Axis with ticks at the endpoints */}
        <line className="pch-vz-iv__axis" x1={PAD_L} y1={axisY} x2={WIDTH - PAD_R} y2={axisY} />
        {ticks.map((v) => (
          <g key={`t${v}`}>
            <line className="pch-vz-iv__tick" x1={x(v)} y1={axisY - 3} x2={x(v)} y2={axisY + 3} />
            <text className="pch-vz-iv__ticklabel" x={x(v)} y={axisY + 14} textAnchor="middle">
              {v}
            </text>
          </g>
        ))}

        {/* Sweep line */}
        {state.sweep !== undefined && Number.isFinite(state.sweep) ? (
          <line
            className="pch-vz-iv__sweep"
            x1={x(state.sweep)}
            y1={0}
            x2={x(state.sweep)}
            y2={axisY}
          />
        ) : null}

        {/* Result band under the axis */}
        {state.result && state.result.length > 0
          ? state.result.map((b, i) => {
              const bx = x(b.start);
              const bw = Math.max(3, x(b.end) - bx);
              const y = axisY + 22;
              return (
                <g key={`r${i}`} className={`pch-vz-iv__bar is-result tone-${b.tone ?? "good"}`}>
                  <rect x={bx} y={y} width={bw} height={BAR_H} rx={4} />
                  {bw > 34 && b.label ? (
                    <text x={bx + bw / 2} y={y + BAR_H / 2} dy="0.34em" textAnchor="middle">
                      {b.label}
                    </text>
                  ) : null}
                </g>
              );
            })
          : null}
        {resultRows ? (
          <text className="pch-vz-iv__band" x={PAD_L} y={axisY + 20}>
            {state.resultLabel ?? "result"}
          </text>
        ) : null}
      </svg>

      {state.legend && state.legend.length > 0 ? (
        <div className="pch-vz-grid__legend">
          {state.legend.map((l) => (
            <span key={l.label} className={`pch-vz-arr__chip tone-${l.tone ?? "muted"}`}>
              <b>{l.label}</b>
              <span>{l.value}</span>
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function IntervalTimeline({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: IntervalTimelineProps) {
  const trace = useMemo(() => {
    const fn = INTERVAL_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<IntervalState>[] };
    return fn(input as IntervalInput);
  }, [algo, JSON.stringify(input.intervals)]);

  if (!INTERVAL_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--interval">interval</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown IntervalTimeline algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(INTERVAL_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<IntervalState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="interval"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

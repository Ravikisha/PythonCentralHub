/**
 * HeapView — step-through visualization of a binary heap, in both of its faces.
 *
 * A heap is an **array** and a **tree** at the same time, and the reason it works
 * at all is that the tree's shape is implied by index arithmetic rather than
 * stored: parent at `(i - 1) // 2`, children at `2i + 1` and `2i + 2`. Nearly
 * every heap bug is losing track of which face you are reasoning about.
 *
 * So both faces are drawn, always, with the same cell highlighted in each. The
 * per-index notes carry the arithmetic itself (`p=(5-1)//2=2`), because that is
 * the step readers get wrong.
 *
 * MDX usage:
 *
 *     import HeapView from "../../../../components/viz/HeapView.tsx";
 *
 *     <HeapView client:visible algo="sift-up" values={[5, 8, 12, 9, 15, 20, 3]}
 *       title="Append, then bubble up until the parent promise holds" />
 *
 *     <HeapView client:visible algo="top-k" values={[3, 2, 1, 5, 6, 4]} k={2}
 *       title="A MIN-heap to find the k LARGEST — and why that is right" />
 *
 * See ./algos/heaps.ts for the registry and each algorithm's inputs.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame, Tone } from "./frames";
import { HEAP_ALGOS, type HeapInput, type HeapState } from "./algos/heaps";

export interface HeapViewProps extends HeapInput {
  /** Key into the algorithm registry in ./algos/heaps.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

const R = 17;
const LEVEL_H = 62;
const PAD_Y = 26;

/**
 * Position a complete-tree node from its index alone — no layout pass needed,
 * which is the same property that makes the array representation work.
 */
function treePos(i: number, size: number) {
  const depth = Math.floor(Math.log2(i + 1));
  const maxDepth = Math.max(0, Math.floor(Math.log2(Math.max(size, 1))));
  const indexInLevel = i - (2 ** depth - 1);
  const levelCount = 2 ** depth;
  // Spread each level evenly across the full width so parents sit above children.
  const span = 2 ** maxDepth;
  const step = span / levelCount;
  const slot = indexInLevel * step + step / 2;
  return { slot, depth, maxDepth, span };
}

function TreeFace({ values, marks }: { values: number[]; marks?: Record<number, Tone> }) {
  if (values.length === 0) {
    return <p className="pch-vz-heap__empty">heap is empty</p>;
  }
  const { span, maxDepth } = treePos(0, values.length);
  const colW = 46;
  const width = span * colW + 30;
  const height = (maxDepth + 1) * LEVEL_H + PAD_Y;
  const xy = (i: number) => {
    const p = treePos(i, values.length);
    return { x: 15 + p.slot * colW, y: PAD_Y + p.depth * LEVEL_H };
  };

  return (
    <svg
      className="pch-vz-heap__svg"
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Heap as a tree"
      preserveAspectRatio="xMidYMin meet"
    >
      {values.map((_, i) => {
        if (i === 0) return null;
        const p = Math.floor((i - 1) / 2);
        const a = xy(p);
        const b = xy(i);
        return (
          <line
            key={`e${i}`}
            className="pch-vz-tree__edge tone-muted"
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
          />
        );
      })}
      {values.map((v, i) => {
        const { x, y } = xy(i);
        return (
          <g key={i} className={`pch-vz-tree__node tone-${marks?.[i] ?? "info"}`}>
            <circle cx={x} cy={y} r={R} />
            <text x={x} y={y} dy="0.34em" textAnchor="middle">
              {v}
            </text>
            <text className="pch-vz-heap__idx" x={x} y={y + R + 11} textAnchor="middle">
              {i}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function Stage({ state }: { state: HeapState }) {
  return (
    <div className="pch-vz-heap">
      <div className="pch-vz-heap__faces">
        <div className="pch-vz-heap__face">
          <span className="pch-vz-tree__panellabel">as a tree</span>
          <TreeFace values={state.values} marks={state.marks} />
        </div>

        <div className="pch-vz-heap__face">
          <span className="pch-vz-tree__panellabel">as an array — the real thing</span>
          <div className="pch-vz-arr">
            <div
              className="pch-vz-arr__grid pch-vz-arr__cells"
              style={{ ["--n" as string]: Math.max(state.values.length, 1) }}
            >
              {state.values.map((v, i) => (
                <span key={i} className={`pch-vz-arr__cell tone-${state.marks?.[i] ?? "info"}`}>
                  <b className="pch-vz-arr__val">{v}</b>
                  <i className="pch-vz-arr__idx">{i}</i>
                </span>
              ))}
            </div>
            {state.notes && Object.keys(state.notes).length > 0 ? (
              <div
                className="pch-vz-arr__grid pch-vz-arr__ptrs"
                style={{ ["--n" as string]: Math.max(state.values.length, 1) }}
              >
                {Object.entries(state.notes).map(([idx, note]) => (
                  <span
                    key={idx}
                    className="pch-vz-arr__ptrstack"
                    style={{ gridColumn: Number(idx) + 1 }}
                  >
                    <b className={`pch-vz-arr__ptr tone-${state.marks?.[Number(idx)] ?? "info"}`}>
                      {note}
                    </b>
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {state.second ? (
        <div className="pch-vz-heap__face">
          <span className="pch-vz-tree__panellabel">{state.second.label}</span>
          <div
            className="pch-vz-arr__grid pch-vz-arr__cells is-aux"
            style={{ ["--n" as string]: Math.max(state.second.values.length, 1) }}
          >
            {state.second.values.map((v, i) => (
              <span key={i} className={`pch-vz-arr__cell tone-${state.second!.marks?.[i] ?? "muted"}`}>
                <b className="pch-vz-arr__val">{v}</b>
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {state.output && state.output.length > 0 ? (
        <div className="pch-vz-tree__out">
          <span className="pch-vz-tree__outlabel">extracted</span>
          {state.output.map((o, i) => (
            <span key={i} className={`pch-vz-tree__slot tone-${o.tone ?? "muted"}`}>
              {o.text}
            </span>
          ))}
        </div>
      ) : null}

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

export default function HeapView({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: HeapViewProps) {
  const trace = useMemo(() => {
    const fn = HEAP_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<HeapState>[] };
    return fn(input as HeapInput);
  }, [algo, input.k, JSON.stringify(input.values)]);

  if (!HEAP_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--heap">heap</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown HeapView algo <code>{algo}</code>. Known keys: {Object.keys(HEAP_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<HeapState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="heap"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

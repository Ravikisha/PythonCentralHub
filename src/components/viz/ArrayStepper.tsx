"use client";

/**
 * ArrayStepper — step-through visualization for any single-sequence algorithm.
 *
 * The workhorse of the DSA module: sliding windows, two pointers, prefix sums,
 * Kadane's, cyclic sort, Dutch-flag partitioning, in-place writers, and the
 * prefix-sum-plus-hash-map family all reduce to "a row of cells, some named
 * cursors, and some highlighted ranges".
 *
 * MDX usage — data plus an algorithm name, never draw code:
 *
 *     import ArrayStepper from "../../../../components/viz/ArrayStepper.tsx";
 *
 *     <ArrayStepper
 *       client:visible
 *       algo="variable-window-sum"
 *       values={[2, 3, 1, 2, 4, 3]}
 *       target={7}
 *       title="Shrinking to the shortest window that reaches 7"
 *       desc="Watch left only ever move forward — that is why the nested while loop is still O(n)."
 *     />
 *
 * See ./algos/arrays.ts for the algorithm registry and each one's inputs.
 */
import { useMemo } from "react";
import VizPlayer, { type VizTag } from "./VizPlayer";
import type { Band, Frame, Tone } from "./frames";
import { ALGOS, type ArrayInput, type ArrayState, type AuxRow } from "./algos/arrays";

export interface ArrayStepperProps extends ArrayInput {
  /** Key into the algorithm registry in ./algos/arrays.ts. */
  algo: string;
  title: string;
  /** Static explanation under the transport row. */
  desc?: string;
  /** Right-aligned mono label. Defaults to the algorithm key. */
  lib?: string;
  /**
   * Header pill. Defaults to `array`; pass `sort` or `search` on the sorting and
   * binary-search pages so the panel is labelled for what it is teaching.
   */
  tag?: VizTag;
  /** Render cells as proportional bars — for height/histogram problems. */
  bars?: boolean;
  /** Show the Python source with a live line highlight. Default true. */
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

/**
 * Greedily pack bands into rows so overlapping ranges never draw on top of one
 * another. Non-overlapping bands (the three regions of a Dutch-flag partition,
 * say) still share a single row.
 */
function packBands(bands: Band[]): Band[][] {
  const rows: Band[][] = [];
  for (const b of bands) {
    if (b.to < b.from) continue; // empty range — nothing to draw
    const row = rows.find((r) => r.every((o) => b.from > o.to || b.to < o.from));
    if (row) row.push(b);
    else rows.push([b]);
  }
  return rows;
}

function BandRow({ bands, n }: { bands: Band[]; n: number }) {
  return (
    <div className="pch-vz-arr__grid pch-vz-arr__bands" style={{ ["--n" as string]: n }}>
      {bands.map((b, i) => (
        <span
          key={i}
          className={`pch-vz-arr__band tone-${b.tone ?? "info"}`}
          style={{ gridColumn: `${b.from + 1} / ${b.to + 2}` }}
        >
          {b.label ?? ""}
        </span>
      ))}
    </div>
  );
}

function Cells({
  values,
  marks,
  bars,
}: {
  values: (number | string)[];
  marks?: Record<number, Tone>;
  bars?: boolean;
}) {
  const max = bars
    ? Math.max(1, ...values.map((v) => (typeof v === "number" ? v : 0)))
    : 1;
  return (
    <div className="pch-vz-arr__grid pch-vz-arr__cells" style={{ ["--n" as string]: values.length }}>
      {values.map((v, i) => (
        <span key={i} className={`pch-vz-arr__cell tone-${marks?.[i] ?? "info"}`}>
          {bars ? (
            <span
              className="pch-vz-arr__bar"
              style={{ height: `${((typeof v === "number" ? v : 0) / max) * 100}%` }}
            />
          ) : null}
          <b className="pch-vz-arr__val">{v}</b>
          <i className="pch-vz-arr__idx">{i}</i>
        </span>
      ))}
    </div>
  );
}

function PointerRow({
  pointers,
  n,
}: {
  pointers: NonNullable<ArrayState["pointers"]>;
  n: number;
}) {
  // Group by index so two cursors on the same cell stack instead of colliding.
  const byIndex = new Map<number, typeof pointers>();
  for (const p of pointers) {
    if (p.index < 0 || p.index >= n) continue;
    const list = byIndex.get(p.index) ?? [];
    list.push(p);
    byIndex.set(p.index, list);
  }
  return (
    <div className="pch-vz-arr__grid pch-vz-arr__ptrs" style={{ ["--n" as string]: n }}>
      {[...byIndex.entries()].map(([index, list]) => (
        <span key={index} className="pch-vz-arr__ptrstack" style={{ gridColumn: index + 1 }}>
          {list.map((p) => (
            <b key={p.name} className={`pch-vz-arr__ptr tone-${p.tone ?? "active"}`}>
              {p.name}
            </b>
          ))}
        </span>
      ))}
    </div>
  );
}

function AuxRowView({ row }: { row: AuxRow }) {
  return (
    <div className="pch-vz-arr__aux">
      <span className="pch-vz-arr__auxlabel">{row.label}</span>
      <div className="pch-vz-arr__grid pch-vz-arr__cells is-aux" style={{ ["--n" as string]: row.values.length }}>
        {row.values.map((v, i) => (
          <span key={i} className={`pch-vz-arr__cell tone-${row.marks?.[i] ?? "muted"}`}>
            <b className="pch-vz-arr__val">{v}</b>
            <i className="pch-vz-arr__idx">{i}</i>
          </span>
        ))}
      </div>
    </div>
  );
}

function Stage({ state, bars }: { state: ArrayState; bars?: boolean }) {
  const n = state.values.length;
  const bandRows = packBands(state.bands ?? []);
  return (
    <div className={`pch-vz-arr${bars ? " is-bars" : ""}`}>
      {bandRows.map((row, i) => (
        <BandRow key={i} bands={row} n={n} />
      ))}
      <Cells values={state.values} marks={state.marks} bars={bars} />
      {state.pointers && state.pointers.length > 0 ? (
        <PointerRow pointers={state.pointers} n={n} />
      ) : null}
      {state.rows?.map((r) => (
        <AuxRowView key={r.label} row={r} />
      ))}
      {state.chips && state.chips.length > 0 ? (
        <div className="pch-vz-arr__chips">
          {state.chips.map((c) => (
            <span key={c.label} className={`pch-vz-arr__chip tone-${c.tone ?? "muted"}`}>
              <b>{c.label}</b>
              <span>{c.value}</span>
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function ArrayStepper({
  algo,
  title,
  desc,
  lib,
  bars = false,
  showCode = true,
  tag = "array",
  ms,
  autoPlay,
  ...input
}: ArrayStepperProps) {
  const trace = useMemo(() => {
    const fn = ALGOS[algo];
    if (!fn) {
      return {
        frames: [] as Frame<ArrayState>[],
        code: undefined,
        result: undefined,
      };
    }
    return fn(input as ArrayInput);
    // `input` is a fresh object each render, so compare its parts instead.
  }, [algo, input.text, input.k, input.target, input.pattern, JSON.stringify(input.values)]);

  if (!ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className={`pch-viz__tag pch-vz__tag--${tag}`}>{tag}</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown ArrayStepper algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<ArrayState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag={tag}
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} bars={bars} />}
    />
  );
}

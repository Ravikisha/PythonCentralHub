"use client";

/**
 * DSUView — step-through visualization of union-find.
 *
 * A union-find structure is a **forest of parent pointers**, which is a directed
 * graph, so this renders through `GraphStage`. Union by size and path compression
 * are both visible as changes to that forest's shape — and the shape is the whole
 * argument for why the operations are effectively constant time.
 *
 * MDX usage:
 *
 *     import DSUView from "../../../../components/viz/DSUView.tsx";
 *
 *     <DSUView client:visible n={8}
 *       unions={[[0,1],[2,3],[1,2],[4,5],[6,7],[5,6],[0,3]]}
 *       title="Small tree under large — and why the reverse breaks it" />
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import { GraphStage } from "./GraphTraversal";
import type { Frame } from "./frames";
import type { GraphState } from "./algos/graphs";
import { DSU_ALGOS, type DsuInput } from "./algos/structures";

export interface DSUViewProps extends DsuInput {
  /** Registry key. Only `union-find` exists so far, and it is the default. */
  algo?: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

export default function DSUView({
  algo = "union-find",
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: DSUViewProps) {
  const trace = useMemo(() => {
    const fn = DSU_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<GraphState>[] };
    return fn(input as DsuInput);
  }, [algo, input.n, JSON.stringify(input.unions)]);

  if (!DSU_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--dsu">dsu</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown DSUView algo <code>{algo}</code>. Known keys: {Object.keys(DSU_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<GraphState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="dsu"
      lib={lib ?? "disjoint set union"}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <GraphStage state={f.state} />}
    />
  );
}

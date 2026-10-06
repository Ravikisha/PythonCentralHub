"use client";

/**
 * SegmentTreeView — step-through visualization of a segment tree.
 *
 * Each node covers a range and stores that range's aggregate, so this is a tree
 * with annotations — `TreeStage` renders it unchanged.
 *
 * What the visualization is for: a range query does **not** walk to the leaves.
 * It stops the moment a node lies entirely inside the query range, and prunes the
 * moment one lies entirely outside. Watching those two rules fire is what makes
 * the O(log n) bound believable rather than asserted.
 *
 * MDX usage:
 *
 *     import SegmentTreeView from "../../../../components/viz/SegmentTreeView.tsx";
 *
 *     <SegmentTreeView client:visible values={[2, 5, 1, 4, 9, 3]} range={[1, 4]}
 *       title="A query decomposes into O(log n) fully-covered nodes" />
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import { TreeStage } from "./TreeWalker";
import type { Frame } from "./frames";
import type { TreeState } from "./algos/trees";
import { SEGTREE_ALGOS, type SegTreeInput } from "./algos/structures";

export interface SegmentTreeViewProps extends SegTreeInput {
  /** Registry key. Only `range-sum` exists so far, and it is the default. */
  algo?: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

export default function SegmentTreeView({
  algo = "range-sum",
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: SegmentTreeViewProps) {
  const trace = useMemo(() => {
    const fn = SEGTREE_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<TreeState>[] };
    return fn(input as SegTreeInput);
  }, [algo, JSON.stringify(input.values), JSON.stringify(input.range)]);

  if (!SEGTREE_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--segtree">segtree</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown SegmentTreeView algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(SEGTREE_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<TreeState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="segtree"
      lib={lib ?? "range query"}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <TreeStage state={f.state} />}
    />
  );
}

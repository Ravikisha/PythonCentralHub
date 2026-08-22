/**
 * RecursionTree — step-through visualization of a call tree.
 *
 * Phase 11 (Recursion and Backtracking) shipped with no visualizations, which is
 * the worst place to have none: the code is six lines and every hard part of it
 * is invisible. This makes four of those parts visible at once —
 *
 *   * where the work actually happens (the shape of the tree, not the code),
 *   * what is on the stack at the moment a result is recorded,
 *   * what `path.pop()` undoes, and what happens if you omit it,
 *   * what memoisation removes — the same tree with the duplicate subtrees gone.
 *
 * Rendered through TreeWalker's stage: a call tree and a binary tree are the same
 * picture, so there is one renderer for both.
 *
 * MDX usage:
 *
 *     import RecursionTree from "../../../../components/viz/RecursionTree.tsx";
 *
 *     <RecursionTree client:visible algo="fib-naive" n={6}
 *       title="Every identical subtree here is recomputed from scratch" />
 *
 *     <RecursionTree client:visible algo="subsets" values={[1, 2, 3]}
 *       title="Include or exclude — one decision per level" />
 *
 * Keep inputs small. These trees are exponential by nature; see the size caps
 * documented in ./algos/recursion.ts.
 */
import { useMemo } from "react";
import VizPlayer, { type VizTag } from "./VizPlayer";
import { TreeStage } from "./TreeWalker";
import type { Frame } from "./frames";
import type { TreeState } from "./algos/trees";
import { RECURSION_ALGOS, type RecursionInput } from "./algos/recursion";

export interface RecursionTreeProps extends RecursionInput {
  /** Key into the algorithm registry in ./algos/recursion.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  /** Defaults to `recursion`. Pass `dp` on memoisation pages. */
  tag?: VizTag;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

export default function RecursionTree({
  algo,
  title,
  desc,
  lib,
  tag = "recursion",
  showCode = true,
  ms,
  autoPlay,
  ...input
}: RecursionTreeProps) {
  const trace = useMemo(() => {
    const fn = RECURSION_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<TreeState>[] };
    return fn(input as RecursionInput);
  }, [algo, input.n, input.target, JSON.stringify(input.values)]);

  if (!RECURSION_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className={`pch-viz__tag pch-vz__tag--${tag}`}>{tag}</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown RecursionTree algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(RECURSION_ALGOS).join(", ")}.
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
      tag={tag}
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <TreeStage state={f.state} />}
    />
  );
}

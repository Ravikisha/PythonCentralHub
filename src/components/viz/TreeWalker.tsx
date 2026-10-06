"use client";

/**
 * TreeWalker — step-through visualization for binary-tree algorithms.
 *
 * Draws the tree as SVG and, crucially, the **call stack or queue beside it**.
 * Tree recursion is short code whose whole lesson is *ordering*: when does a
 * node get visited relative to its children, and what is on the stack at that
 * moment. A static diagram cannot show that; this can.
 *
 * MDX usage — paste the array straight from the LeetCode problem statement:
 *
 *     import TreeWalker from "../../../../components/viz/TreeWalker.tsx";
 *
 *     <TreeWalker
 *       client:visible
 *       algo="level-order"
 *       tree={[3, 9, 20, null, null, 15, 7]}
 *       title="BFS visits the tree one level at a time"
 *       desc="Watch the queue: its length at the top of each outer iteration is exactly the width of the level."
 *     />
 *
 * See ./algos/trees.ts for the algorithm registry and each one's inputs.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame, Tone } from "./frames";
import { TREE_ALGOS, type TreeInput, type TreeState } from "./algos/trees";

export interface TreeWalkerProps extends TreeInput {
  /** Key into the algorithm registry in ./algos/trees.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

/** Column pitch and row pitch in SVG user units. */
const COL = 56;
const ROW = 74;
const PAD_X = 34;
const PAD_Y = 30;
const R = 19;

const cx = (x: number) => PAD_X + x * COL;
const cy = (y: number) => PAD_Y + y * ROW;

/**
 * Exported so `<RecursionTree>` can reuse it. A call tree and a binary tree are
 * the same picture — nodes, edges, a stack panel and an output strip — so there
 * is no reason for two renderers.
 */
export function TreeStage({ state }: { state: TreeState }) {
  const width = Math.max(1, state.cols) * COL + PAD_X;
  const height = (state.depth + 1) * ROW + PAD_Y;
  const pos = new Map(state.nodes.map((n) => [n.id, n]));

  return (
    <div className="pch-vz-tree">
      <div className="pch-vz-tree__main">
        <svg
          className="pch-vz-tree__svg"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Binary tree"
          preserveAspectRatio="xMidYMin meet"
        >
          {/* Edges first so nodes paint over their endpoints. */}
          {state.edges.map((e, i) => {
            const a = pos.get(e.from);
            const b = pos.get(e.to);
            if (!a || !b) return null;
            return (
              <g key={i} className={`pch-vz-tree__edge tone-${e.tone ?? "muted"}`}>
                <line x1={cx(a.x)} y1={cy(a.y)} x2={cx(b.x)} y2={cy(b.y)} />
                {/* Edge labels carry the character on a trie edge, or a weight. */}
                {e.label ? (
                  <text
                    className="pch-vz-tree__edgelabel"
                    x={(cx(a.x) + cx(b.x)) / 2}
                    y={(cy(a.y) + cy(b.y)) / 2}
                    dy="0.34em"
                    textAnchor="middle"
                  >
                    {e.label}
                  </text>
                ) : null}
              </g>
            );
          })}

          {state.nodes.map((n) => {
            const tone: Tone = state.marks?.[n.id] ?? "info";
            return (
              <g key={n.id} className={`pch-vz-tree__node tone-${tone}`}>
                <circle cx={cx(n.x)} cy={cy(n.y)} r={R} />
                <text x={cx(n.x)} y={cy(n.y)} dy="0.34em" textAnchor="middle">
                  {n.value}
                </text>
                {state.notes?.[n.id] ? (
                  <text
                    className="pch-vz-tree__note"
                    x={cx(n.x)}
                    y={cy(n.y) + R + 13}
                    textAnchor="middle"
                  >
                    {state.notes[n.id]}
                  </text>
                ) : null}
              </g>
            );
          })}
        </svg>

        {state.panel ? (
          <div className={`pch-vz-tree__panel is-${state.panel.kind ?? "stack"}`}>
            <span className="pch-vz-tree__panellabel">{state.panel.label}</span>
            <div className="pch-vz-tree__panelitems">
              {state.panel.items.length === 0 ? (
                <span className="pch-vz-tree__empty">empty</span>
              ) : (
                state.panel.items.map((it, i) => (
                  <span key={i} className={`pch-vz-tree__slot tone-${it.tone ?? "info"}`}>
                    {it.text}
                  </span>
                ))
              )}
            </div>
          </div>
        ) : null}
      </div>

      {state.output && state.output.length > 0 ? (
        <div className="pch-vz-tree__out">
          <span className="pch-vz-tree__outlabel">output</span>
          {state.output.map((o, i) => (
            <span key={i} className={`pch-vz-tree__slot tone-${o.tone ?? "muted"}`}>
              {o.text}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function TreeWalker({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: TreeWalkerProps) {
  const trace = useMemo(() => {
    const fn = TREE_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<TreeState>[] };
    return fn(input as TreeInput);
  }, [algo, JSON.stringify(input.tree), input.target, input.p, input.q]);

  if (!TREE_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--tree">tree</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown TreeWalker algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(TREE_ALGOS).join(", ")}.
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
      tag="tree"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <TreeStage state={f.state} />}
    />
  );
}

"use client";

/**
 * StateMachineView — step-through visualization of a DP state machine.
 *
 * Some DP problems are far clearer as a state machine than as a table. The stock
 * problems are the canonical case: "with cooldown" has three states and five
 * transitions, and drawn that way the recurrence is readable directly off the
 * diagram — whereas `dp[i][2]` requires holding an arbitrary index convention in
 * your head.
 *
 * A state machine is a directed graph with per-node values, so this renders
 * through `GraphStage` unchanged.
 *
 * MDX usage:
 *
 *     import StateMachineView from "../../../../components/viz/StateMachineView.tsx";
 *
 *     <StateMachineView client:visible algo="stock-cooldown" values={[1, 2, 3, 0, 2]}
 *       title="Three states, five transitions — the recurrence is the diagram" />
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import { GraphStage } from "./GraphTraversal";
import type { Frame } from "./frames";
import type { GraphState } from "./algos/graphs";
import { STATE_ALGOS, type StateInput } from "./algos/states";

export interface StateMachineViewProps extends StateInput {
  /** Key into the algorithm registry in ./algos/states.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

export default function StateMachineView({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: StateMachineViewProps) {
  const trace = useMemo(() => {
    const fn = STATE_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<GraphState>[] };
    return fn(input as StateInput);
  }, [algo, input.target, input.text, JSON.stringify(input.values)]);

  if (!STATE_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--state">state</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown StateMachineView algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(STATE_ALGOS).join(", ")}.
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
      tag="state"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <GraphStage state={f.state} />}
    />
  );
}

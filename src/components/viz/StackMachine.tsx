/**
 * StackMachine — step-through visualization for stack algorithms.
 *
 * Draws the input row being scanned and the stack as a column beside it, growing
 * upward. The monotonic stack is the reason this component exists: its code is
 * six lines, and two of its properties are invisible in the source —
 *
 *   * the stack contents *mean* something ("indices still waiting for an answer"),
 *   * a `while` inside a `for` is still O(n), because each element is pushed once
 *     and popped once across the entire run.
 *
 * The second only becomes believable once you watch the pop counter and see it
 * top out at n.
 *
 * MDX usage:
 *
 *     import StackMachine from "../../../../components/viz/StackMachine.tsx";
 *
 *     <StackMachine client:visible algo="next-greater"
 *       values={[73, 74, 75, 71, 69, 72, 76, 73]}
 *       title="The stack holds every index still waiting for a warmer day" />
 *
 *     <StackMachine client:visible algo="valid-parens" text="([]{})"
 *       title="Stack depth is nesting depth" />
 *
 * See ./algos/stacks.ts for the registry and each algorithm's inputs.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame } from "./frames";
import { STACK_ALGOS, type StackInput, type StackState } from "./algos/stacks";

export interface StackMachineProps extends StackInput {
  /** Key into the algorithm registry in ./algos/stacks.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

function Stage({ state }: { state: StackState }) {
  return (
    <div className="pch-vz-stack">
      <div className="pch-vz-stack__main">
        <div className="pch-vz-stack__tape">
          <div
            className="pch-vz-arr__grid pch-vz-arr__cells"
            style={{ ["--n" as string]: state.input.length }}
          >
            {state.input.map((cell, i) => (
              <span key={i} className={`pch-vz-arr__cell tone-${cell.tone ?? "info"}`}>
                <b className="pch-vz-arr__val">{cell.label}</b>
                <i className="pch-vz-arr__idx">{i}</i>
              </span>
            ))}
          </div>

          <div
            className="pch-vz-arr__grid pch-vz-arr__ptrs"
            style={{ ["--n" as string]: state.input.length }}
          >
            {state.cursor !== undefined && state.cursor >= 0 ? (
              <span className="pch-vz-arr__ptrstack" style={{ gridColumn: state.cursor + 1 }}>
                <b className="pch-vz-arr__ptr tone-active">read</b>
              </span>
            ) : null}
          </div>

          {state.output && state.output.length > 0 ? (
            <div className="pch-vz-arr__aux">
              <span className="pch-vz-arr__auxlabel">{state.outputLabel ?? "out"}</span>
              <div
                className="pch-vz-arr__grid pch-vz-arr__cells is-aux"
                style={{ ["--n" as string]: state.output.length }}
              >
                {state.output.map((cell, i) => (
                  <span key={i} className={`pch-vz-arr__cell tone-${cell.tone ?? "muted"}`}>
                    <b className="pch-vz-arr__val">{cell.label}</b>
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* The stack column. Rendered bottom-up so "top of stack" is visually on
            top, which is how everyone draws it on a whiteboard. */}
        <div className="pch-vz-stack__col">
          <span className="pch-vz-tree__panellabel">stack (top)</span>
          <div className="pch-vz-stack__slots">
            {state.stack.length === 0 ? (
              <span className="pch-vz-tree__empty">empty</span>
            ) : (
              [...state.stack].reverse().map((slot, i) => (
                <span key={i} className={`pch-vz-stack__slot tone-${slot.tone ?? "warn"}`}>
                  <b>{slot.label}</b>
                  {slot.note ? <i>{slot.note}</i> : null}
                </span>
              ))
            )}
          </div>
          <span className="pch-vz-stack__floor">bottom</span>
        </div>
      </div>

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

export default function StackMachine({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: StackMachineProps) {
  const trace = useMemo(() => {
    const fn = STACK_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<StackState>[] };
    return fn(input as StackInput);
  }, [algo, input.text, JSON.stringify(input.values)]);

  if (!STACK_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--stack">stack</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown StackMachine algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(STACK_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<StackState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="stack"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

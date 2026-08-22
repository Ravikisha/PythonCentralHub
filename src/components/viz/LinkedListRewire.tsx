/**
 * LinkedListRewire — step-through visualization of pointer surgery.
 *
 * Nodes hold a fixed slot on the rail for the whole trace; only the **arrows**
 * move. That is deliberate. The lesson in every linked-list problem is which
 * pointer is reassigned and in what order, and a diagram whose boxes shuffle
 * around obscures exactly that.
 *
 * Arrows that point backwards (a reversal) or wrap around (a cycle) are drawn
 * under the rail so they never cross a node box.
 *
 * MDX usage:
 *
 *     import LinkedListRewire from "../../../../components/viz/LinkedListRewire.tsx";
 *
 *     <LinkedListRewire client:visible algo="reverse" values={[1, 2, 3, 4, 5]}
 *       title="Four assignments, and the order is the whole problem" />
 *
 *     <LinkedListRewire client:visible algo="cycle-detection"
 *       values={[3, 2, 0, -4]} cycleAt={1}
 *       title="Floyd's tortoise and hare, both phases" />
 *
 * See ./algos/lists.ts for the algorithm registry and each one's inputs.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame, Tone } from "./frames";
import { LIST_ALGOS, type ListInput, type ListState } from "./algos/lists";

export interface LinkedListRewireProps extends ListInput {
  /** Key into the algorithm registry in ./algos/lists.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

const SLOT = 74;
const BOX_W = 52;
const BOX_H = 38;
const PAD_X = 18;
/** Room above the rail for cursor labels, below it for back-edges. */
const RAIL_Y = 58;
const UNDER = 40;

const boxX = (slot: number) => PAD_X + slot * SLOT;
const boxMid = (slot: number) => boxX(slot) + BOX_W / 2;

function Stage({ state }: { state: ListState }) {
  const slots = Math.max(state.slots, ...state.nodes.map((n) => n.slot + 1), 1);
  const width = PAD_X * 2 + slots * SLOT;
  const height = RAIL_Y + BOX_H + UNDER + 26;
  const bySlot = new Map(state.nodes.map((n) => [n.id, n]));

  /** The null terminator sits one slot past the last node. */
  const nullSlot = slots;

  return (
    <div className="pch-vz-list">
      <svg
        className="pch-vz-list__svg"
        viewBox={`0 0 ${width + SLOT} ${height}`}
        role="img"
        aria-label="Linked list"
        preserveAspectRatio="xMidYMin meet"
      >
        <defs>
          {(["muted", "good", "bad", "active", "warn", "info"] as Tone[]).map((tone) => (
            <marker
              key={tone}
              id={`pch-ll-arrow-${tone}`}
              viewBox="0 0 10 10"
              refX="9"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path className={`pch-vz-list__head tone-${tone}`} d="M0 0L10 5L0 10z" />
            </marker>
          ))}
        </defs>

        {/* The null terminator, always present so a `-> null` arrow has a target. */}
        <text className="pch-vz-list__null" x={boxMid(nullSlot)} y={RAIL_Y + BOX_H / 2} dy="0.34em" textAnchor="middle">
          ∅
        </text>

        {/* Links. Forward arrows run along the rail; backward and wrap-around
            arrows bow under it, which keeps them off the node boxes. */}
        {state.links.map((link, i) => {
          const from = bySlot.get(link.from);
          if (!from) return null;
          const toSlot = link.to === null ? nullSlot : bySlot.get(link.to)?.slot;
          if (toSlot === undefined) return null;
          const tone = link.tone ?? "muted";

          const x1 = boxX(from.slot) + BOX_W;
          const y1 = RAIL_Y + BOX_H / 2;
          const x2 = boxX(toSlot) - 6;
          const under = link.under || toSlot <= from.slot;

          if (!under) {
            return (
              <line
                key={i}
                className={`pch-vz-list__link tone-${tone}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y1}
                markerEnd={`url(#pch-ll-arrow-${tone})`}
              />
            );
          }

          const sx = boxMid(from.slot);
          const ex = boxMid(toSlot);
          const dip = RAIL_Y + BOX_H + UNDER * 0.7;
          return (
            <path
              key={i}
              className={`pch-vz-list__link tone-${tone}`}
              d={`M ${sx} ${RAIL_Y + BOX_H} C ${sx} ${dip}, ${ex} ${dip}, ${ex} ${RAIL_Y + BOX_H + 4}`}
              fill="none"
              markerEnd={`url(#pch-ll-arrow-${tone})`}
            />
          );
        })}

        {/* Node boxes */}
        {state.nodes.map((n) => (
          <g key={n.id} className={`pch-vz-list__node tone-${n.tone ?? "info"}`}>
            <rect x={boxX(n.slot)} y={RAIL_Y} width={BOX_W} height={BOX_H} rx={6} />
            <text x={boxMid(n.slot)} y={RAIL_Y + BOX_H / 2} dy="0.34em" textAnchor="middle">
              {n.value}
            </text>
          </g>
        ))}

        {/* Cursors, stacked when two share a node. */}
        {(() => {
          const groups = new Map<number, typeof state.cursors>();
          for (const c of state.cursors) {
            const slot = c.node === null ? nullSlot : bySlot.get(c.node)?.slot;
            if (slot === undefined) continue;
            groups.set(slot, [...(groups.get(slot) ?? []), c]);
          }
          return [...groups.entries()].map(([slot, list]) =>
            list.map((c, k) => (
              <g key={`${c.name}-${slot}`} className={`pch-vz-list__cursor tone-${c.tone ?? "active"}`}>
                <text x={boxMid(slot)} y={RAIL_Y - 10 - k * 15} textAnchor="middle">
                  {c.name}
                </text>
                {k === 0 ? (
                  <path
                    d={`M ${boxMid(slot)} ${RAIL_Y - 7} l -4 -6 l 8 0 z`}
                    className="pch-vz-list__caret"
                  />
                ) : null}
              </g>
            )),
          );
        })()}
      </svg>

      {state.second && state.second.nodes.length > 0 ? (
        <div className="pch-vz-list__second">
          <span className="pch-vz-tree__outlabel">{state.second.label}</span>
          {state.second.nodes.map((n) => (
            <span key={n.id} className={`pch-vz-tree__slot tone-${n.tone ?? "info"}`}>
              {n.value}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function LinkedListRewire({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: LinkedListRewireProps) {
  const trace = useMemo(() => {
    const fn = LIST_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<ListState>[] };
    return fn(input as ListInput);
  }, [algo, JSON.stringify(input.values), JSON.stringify(input.other), input.cycleAt, input.k]);

  if (!LIST_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--list">list</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown LinkedListRewire algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(LIST_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<ListState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="list"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

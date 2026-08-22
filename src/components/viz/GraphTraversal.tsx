/**
 * GraphTraversal — step-through visualization for graph algorithms.
 *
 * Draws the graph as SVG with the algorithm's **frontier structure** beside it.
 * BFS, DFS, Kahn's topological sort, three-colour cycle detection, two-colouring
 * and Dijkstra differ almost entirely in *which container holds the frontier*
 * and *when a node is marked* — so that container is on screen at every step.
 *
 * MDX usage:
 *
 *     import GraphTraversal from "../../../../components/viz/GraphTraversal.tsx";
 *
 *     <GraphTraversal
 *       client:visible
 *       algo="bfs"
 *       edges={[["A","B"], ["A","C"], ["B","D"], ["C","D"], ["C","E"], ["D","F"]]}
 *       start="A"
 *       title="BFS reaches every node by a shortest path first"
 *       desc="Nodes are marked seen when they are enqueued, not when they are dequeued."
 *     />
 *
 * Weighted edges take a third element (`["A","B",4]`) and are labelled on the
 * wire. Layout is derived automatically — see ./algos/graphs.ts.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame, Tone } from "./frames";
import { GRAPH_ALGOS, type GraphInput, type GraphState } from "./algos/graphs";

export interface GraphTraversalProps extends GraphInput {
  /** Key into the algorithm registry in ./algos/graphs.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

const COL = 74;
const ROW = 82;
const PAD = 36;
const R = 20;

const px = (x: number) => PAD + x * COL;
const py = (y: number) => PAD + y * ROW;

/** Shorten an edge so an arrowhead lands on the circle's rim, not its centre. */
function trim(x1: number, y1: number, x2: number, y2: number, by: number) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const k = by / len;
  return { x: x2 - dx * k, y: y2 - dy * k };
}

/**
 * Exported so `<DSUView>` and `<StateMachineView>` reuse it. A union-find forest
 * and a state machine are both "nodes, directed edges, per-node annotations" —
 * the same picture a traversal draws.
 */
export function GraphStage({ state }: { state: GraphState }) {
  const width = Math.max(1, state.cols) * COL + PAD;
  const height = Math.max(1, state.rows) * ROW + PAD;
  const pos = new Map(state.nodes.map((n) => [n.id, n]));

  return (
    <div className="pch-vz-graph">
      <div className="pch-vz-graph__main">
        <svg
          className="pch-vz-graph__svg"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Graph"
          preserveAspectRatio="xMidYMin meet"
        >
          <defs>
            {/* One marker per tone so arrowheads match their edge colour. */}
            {(["muted", "good", "bad", "active", "warn", "info"] as Tone[]).map((tone) => (
              <marker
                key={tone}
                id={`pch-arrow-${tone}`}
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path className={`pch-vz-graph__head tone-${tone}`} d="M0 0L10 5L0 10z" />
              </marker>
            ))}
          </defs>

          {state.edges.map((e, i) => {
            const a = pos.get(e.from);
            const b = pos.get(e.to);
            if (!a || !b) return null;
            const x1 = px(a.x);
            const y1 = py(a.y);
            const end = trim(x1, y1, px(b.x), py(b.y), e.directed ? R + 5 : 0);
            const tone = e.tone ?? "muted";
            return (
              <g key={i} className={`pch-vz-graph__edge tone-${tone}`}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={end.x}
                  y2={end.y}
                  markerEnd={e.directed ? `url(#pch-arrow-${tone})` : undefined}
                />
                {e.label ? (
                  <text
                    className="pch-vz-graph__weight"
                    x={(x1 + end.x) / 2}
                    y={(y1 + end.y) / 2 - 5}
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
              <g key={n.id} className={`pch-vz-graph__node tone-${tone}`}>
                <circle cx={px(n.x)} cy={py(n.y)} r={R} />
                <text x={px(n.x)} y={py(n.y)} dy="0.34em" textAnchor="middle">
                  {n.id}
                </text>
                {state.notes?.[n.id] ? (
                  <text
                    className="pch-vz-graph__note"
                    x={px(n.x)}
                    y={py(n.y) + R + 13}
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
          <div className={`pch-vz-tree__panel is-${state.panel.kind ?? "queue"}`}>
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
          <span className="pch-vz-tree__outlabel">order</span>
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

export default function GraphTraversal({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: GraphTraversalProps) {
  const trace = useMemo(() => {
    const fn = GRAPH_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<GraphState>[] };
    return fn(input as GraphInput);
  }, [algo, JSON.stringify(input.edges), JSON.stringify(input.nodes), input.start, input.directed, input.layout]);

  if (!GRAPH_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--graph">graph</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown GraphTraversal algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(GRAPH_ALGOS).join(", ")}.
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
      tag="graph"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <GraphStage state={f.state} />}
    />
  );
}

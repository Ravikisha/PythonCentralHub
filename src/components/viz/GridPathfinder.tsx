/**
 * GridPathfinder — step-through visualization of grid traversals.
 *
 * Shows the grid alongside the **same frontier structure** the graph components
 * show, because that is the point being taught: a grid is a graph in disguise.
 * Number of islands is connected components, rotting oranges is multi-source BFS,
 * maze shortest-path is plain BFS. A reader who has watched BFS on a
 * node-and-edge diagram should see the identical queue here.
 *
 * MDX usage:
 *
 *     import GridPathfinder from "../../../../components/viz/GridPathfinder.tsx";
 *
 *     <GridPathfinder client:visible algo="islands"
 *       grid={["11000", "11000", "00100", "00011"]}
 *       title="Flood each island as you count it" />
 *
 *     <GridPathfinder client:visible algo="maze-bfs"
 *       grid={["....#", ".##.#", "....#", ".#...", ".#.#."]}
 *       start={[0, 0]} end={[4, 4]}
 *       title="BFS labels every cell with its shortest distance" />
 *
 * See ./algos/grids.ts for the registry and each algorithm's grid characters.
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import type { Frame } from "./frames";
import { GRID_ALGOS, type GridInput, type GridState } from "./algos/grids";

export interface GridPathfinderProps extends GridInput {
  /** Key into the algorithm registry in ./algos/grids.ts. */
  algo: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

function Stage({ state }: { state: GridState }) {
  const cols = state.cells[0]?.length ?? 1;

  return (
    <div className="pch-vz-grid">
      <div className="pch-vz-grid__main">
        <div
          className="pch-vz-grid__board"
          style={{ ["--cols" as string]: cols }}
          role="img"
          aria-label="Grid"
        >
          {state.cells.map((row, r) =>
            row.map((cell, c) => (
              <span
                key={`${r}-${c}`}
                className={
                  `pch-vz-grid__cell tone-${cell.tone ?? "info"}` +
                  (cell.blocked ? " is-blocked" : "") +
                  (state.cursor?.r === r && state.cursor?.c === c ? " is-cursor" : "")
                }
              >
                {cell.label}
              </span>
            )),
          )}
        </div>

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

export default function GridPathfinder({
  algo,
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: GridPathfinderProps) {
  const trace = useMemo(() => {
    const fn = GRID_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<GridState>[] };
    return fn(input as GridInput);
  }, [algo, JSON.stringify(input.grid), JSON.stringify(input.start), JSON.stringify(input.end)]);

  if (!GRID_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--grid">grid</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown GridPathfinder algo <code>{algo}</code>. Known keys:{" "}
          {Object.keys(GRID_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<GridState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="grid"
      lib={lib ?? algo}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <Stage state={f.state} />}
    />
  );
}

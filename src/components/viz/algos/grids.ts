/**
 * algos/grids.ts — traced grid algorithms for <GridPathfinder>.
 *
 * A grid is a graph in disguise, and that sentence is the single most useful
 * thing to internalise about this whole family: "number of islands", "rotting
 * oranges", "shortest path in a maze" and "flood fill" are connected components,
 * multi-source BFS, plain BFS and DFS respectively — algorithms already covered
 * in Phase 10, wearing a 2-D costume.
 *
 * So these visualizations deliberately show the same frontier structure the graph
 * ones do. A reader who watched BFS on a node-and-edge diagram should recognise
 * the queue here immediately, because it is the same queue.
 *
 * AUTHORING FORMAT
 * ----------------
 *     <GridPathfinder algo="islands" grid={["11000", "11000", "00100", "00011"]} />
 *
 * A row of characters per grid row. `1`/`#` is land or wall depending on the
 * algorithm, `0`/`.` is water or open, and algorithm-specific characters are
 * documented per entry.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

export interface GridCell {
  /** What to print in the cell. Empty string for a blank. */
  label: string;
  tone?: Tone;
  /** Renders as a solid block — walls and water. */
  blocked?: boolean;
}

export interface GridState {
  cells: GridCell[][];
  /** The cell currently being examined. */
  cursor?: { r: number; c: number };
  /** Frontier contents, rendered beside the grid. */
  panel?: { label: string; items: { text: string; tone?: Tone }[]; kind?: "stack" | "queue" };
  /** Running counters shown under the grid. */
  legend?: { label: string; value: string; tone?: Tone }[];
}

export interface GridInput {
  /** One string per row. */
  grid?: string[];
  /** Start cell for path problems, as [row, col]. */
  start?: [number, number];
  /** Target cell for path problems. */
  end?: [number, number];
}

export type GridAlgo = (input: GridInput) => Trace<GridState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

/** Four-directional neighbours, in a fixed order so traces are reproducible. */
const DIRS: [number, number][] = [
  [-1, 0],
  [0, 1],
  [1, 0],
  [0, -1],
];

const parse = (input: GridInput, fallback: string[]): string[][] =>
  (input.grid && input.grid.length ? input.grid : fallback).map((row) => [...row]);

// ── 1. Number of islands (LC 200) ─────────────────────────────────────────

const ISLANDS_CODE = [
  "def num_islands(grid):",
  "    rows, cols = len(grid), len(grid[0])",
  "    count = 0",
  "    for r in range(rows):",
  "        for c in range(cols):",
  "            if grid[r][c] == '1':",
  "                count += 1          # a NEW island",
  "                flood(grid, r, c)   # sink all of it",
  "    return count",
  "",
  "def flood(grid, r, c):",
  "    stack = [(r, c)]",
  "    while stack:",
  "        r, c = stack.pop()",
  "        if not in_bounds or grid[r][c] != '1': continue",
  "        grid[r][c] = '0'            # mark visited BY SINKING it",
  "        for dr, dc in DIRS:",
  "            stack.append((r + dr, c + dc))",
];

export const islands: GridAlgo = (input) => {
  const g = parse(input, ["11000", "11000", "00100", "00011"]);
  const rows = g.length;
  const cols = g[0].length;
  const t = tracer<GridState>(ISLANDS_CODE);

  /** Island id per cell, or 0 for water/unclaimed. */
  const island: number[][] = g.map((row) => row.map(() => 0));
  const ISLAND_TONES: Tone[] = ["active", "good", "warn", "bad", "info"];
  let count = 0;

  const state = (cursor?: { r: number; c: number }, stack: [number, number][] = []): GridState => ({
    cells: g.map((row, r) =>
      row.map((ch, c) => ({
        label: island[r][c] > 0 ? String(island[r][c]) : ch === "1" ? "1" : "",
        blocked: ch !== "1" && island[r][c] === 0,
        tone:
          island[r][c] > 0
            ? ISLAND_TONES[(island[r][c] - 1) % ISLAND_TONES.length]
            : ch === "1"
              ? "info"
              : "muted",
      })),
    ),
    cursor,
    panel: {
      label: "stack",
      kind: "stack",
      items: stack.map(([r, c]) => ({ text: `${r},${c}`, tone: "info" })),
    },
    legend: [{ label: "islands", value: String(count), tone: "good" }],
  });

  t.push(
    state(),
    `Scan every cell. The moment an unclaimed piece of land is found, it must belong to an island nobody has counted yet — so increment the counter and then flood the whole island so it is never counted twice.`,
    { line: 3, phase: "setup" },
  );

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (g[r][c] !== "1" || island[r][c] > 0) continue;

      count += 1;
      t.push(
        state({ r, c }),
        `(${r}, ${c}) is land and has not been claimed, so this is island number ${count}. Flooding it now is what makes the outer scan O(rows × cols) overall rather than quadratic — every cell is visited a constant number of times in total.`,
        { line: 7, phase: `island ${count}`, watch: [w("islands", count, "good"), w("seed", `${r},${c}`, "active")] },
      );

      const stack: [number, number][] = [[r, c]];
      while (stack.length) {
        const [cr, cc] = stack.pop()!;
        if (cr < 0 || cr >= rows || cc < 0 || cc >= cols) continue;
        if (g[cr][cc] !== "1" || island[cr][cc] > 0) continue;

        island[cr][cc] = count;
        const pushed: [number, number][] = [];
        for (const [dr, dc] of DIRS) {
          const nr = cr + dr;
          const nc = cc + dc;
          if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && g[nr][nc] === "1" && island[nr][nc] === 0) {
            stack.push([nr, nc]);
            pushed.push([nr, nc]);
          }
        }

        t.push(
          state({ r: cr, c: cc }, [...stack]),
          pushed.length
            ? `Claim (${cr}, ${cc}) for island ${count} and push its ${pushed.length} unclaimed neighbour${pushed.length === 1 ? "" : "s"}. Marking the cell *as it is popped* — rather than when pushed — is why the bounds and already-claimed checks happen at the top of the loop.`
            : `Claim (${cr}, ${cc}). No unclaimed neighbours, so the flood recedes from here.`,
          {
            line: 16,
            phase: `island ${count}`,
            watch: [w("cell", `${cr},${cc}`, "active"), w("stack", stack.length), w("islands", count, "good")],
          },
        );
      }
    }
  }

  t.push(
    state(),
    `${count} island${count === 1 ? "" : "s"}. Note what the algorithm actually is: connected components on a graph whose nodes are land cells and whose edges are adjacency. The 2-D shape is a costume — recognise it and the problem is one you have already solved.`,
    { line: 9, phase: "answer", watch: [w("islands", count, "good")] },
  );

  return capFrames(t.done(`${count} island${count === 1 ? "" : "s"}`));
};

// ── 2. Shortest path through a maze (BFS) ─────────────────────────────────

const MAZE_CODE = [
  "def shortest_path(grid, start, end):",
  "    q = deque([(start, 0)])",
  "    seen = {start}",
  "    while q:",
  "        (r, c), d = q.popleft()",
  "        if (r, c) == end:",
  "            return d               # first arrival IS shortest",
  "        for dr, dc in DIRS:",
  "            nr, nc = r + dr, c + dc",
  "            if in_bounds and grid[nr][nc] != '#' and (nr, nc) not in seen:",
  "                seen.add((nr, nc))",
  "                q.append(((nr, nc), d + 1))",
  "    return -1",
];

export const mazeBfs: GridAlgo = (input) => {
  const g = parse(input, ["....#", ".##.#", "....#", ".#...", ".#.#."]);
  const rows = g.length;
  const cols = g[0].length;
  const [sr, sc] = input.start ?? [0, 0];
  const [er, ec] = input.end ?? [rows - 1, cols - 1];
  const t = tracer<GridState>(MAZE_CODE);

  const dist: (number | null)[][] = g.map((row) => row.map(() => null));
  const queue: [number, number][] = [[sr, sc]];
  dist[sr][sc] = 0;
  let found: number | null = null;

  const state = (cursor?: { r: number; c: number }): GridState => ({
    cells: g.map((row, r) =>
      row.map((ch, c) => ({
        label:
          ch === "#"
            ? ""
            : r === er && c === ec
              ? dist[r][c] !== null ? String(dist[r][c]) : "◉"
              : dist[r][c] !== null
                ? String(dist[r][c])
                : "",
        blocked: ch === "#",
        tone:
          ch === "#"
            ? "muted"
            : r === er && c === ec && found !== null
              ? "good"
              : dist[r][c] !== null
                ? queue.some(([qr, qc]) => qr === r && qc === c)
                  ? "warn"
                  : "active"
                : "info",
      })),
    ),
    cursor,
    panel: {
      label: "queue",
      kind: "queue",
      items: queue.map(([r, c]) => ({ text: `${r},${c}`, tone: "warn" })),
    },
    legend: [
      { label: "start", value: `${sr},${sc}`, tone: "active" },
      { label: "goal", value: `${er},${ec}`, tone: "good" },
      { label: "visited", value: String(dist.flat().filter((d) => d !== null).length) },
    ],
  });

  t.push(
    state({ r: sr, c: sc }),
    `Each cell will be labelled with its distance from the start. BFS fills outward in rings, so the first time it touches a cell that distance is already the shortest — no revisiting, no relaxation.`,
    { line: 3, phase: "setup" },
  );

  while (queue.length) {
    const [r, c] = queue.shift()!;
    const d = dist[r][c]!;

    if (r === er && c === ec) {
      found = d;
      t.push(
        state({ r, c }),
        `Reached the goal at distance ${d}. Because the queue is FIFO, every cell dequeued before this one had distance ≤ ${d} — so this is the shortest path and there is no reason to keep searching.`,
        { line: 7, phase: "found", watch: [w("distance", d, "good")] },
      );
      break;
    }

    const fresh: string[] = [];
    for (const [dr, dc] of DIRS) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
      if (g[nr][nc] === "#" || dist[nr][nc] !== null) continue;
      dist[nr][nc] = d + 1;
      queue.push([nr, nc]);
      fresh.push(`${nr},${nc}`);
    }

    t.push(
      state({ r, c }),
      fresh.length
        ? `Expand (${r}, ${c}) at distance ${d}. Its unvisited open neighbours ${fresh.join(", ")} get distance ${d + 1} and are marked visited **now**, on enqueue — marking on dequeue instead lets a cell enter the queue twice.`
        : `Expand (${r}, ${c}). Every neighbour is a wall or already visited, so this branch is done.`,
      {
        line: 12,
        phase: "expand",
        watch: [w("cell", `${r},${c}`, "active"), w("d", d), w("queue", queue.length, "warn")],
      },
    );
  }

  t.push(
    state(),
    found !== null
      ? `Shortest path is ${found} steps. O(rows × cols) time — every cell enters the queue at most once. Switch the deque for a heap and you have Dijkstra, which is what you need the moment cells have different costs.`
      : `The goal is unreachable — the queue emptied without arriving. Returning −1 rather than crashing is what the problem expects.`,
    { line: 13, phase: "answer", watch: [w("answer", found ?? -1, found !== null ? "good" : "bad")] },
  );

  return capFrames(t.done(found !== null ? `shortest path = ${found} steps` : "unreachable"));
};

// ── 3. Rotting oranges — multi-source BFS (LC 994) ────────────────────────

const ROT_CODE = [
  "def oranges_rotting(grid):",
  "    q = deque()",
  "    fresh = 0",
  "    for r, row in enumerate(grid):",
  "        for c, v in enumerate(row):",
  "            if v == 2: q.append((r, c))     # EVERY rotten one seeds the queue",
  "            elif v == 1: fresh += 1",
  "    minutes = 0",
  "    while q and fresh:",
  "        for _ in range(len(q)):             # one whole minute per level",
  "            r, c = q.popleft()",
  "            for dr, dc in DIRS:",
  "                if grid[nr][nc] == 1:",
  "                    grid[nr][nc] = 2; fresh -= 1; q.append((nr, nc))",
  "        minutes += 1",
  "    return -1 if fresh else minutes",
];

export const rottingOranges: GridAlgo = (input) => {
  const g = parse(input, ["2110", "1101", "0111"]);
  const rows = g.length;
  const cols = g[0].length;
  const t = tracer<GridState>(ROT_CODE);

  const grid = g.map((row) => row.map((ch) => Number(ch)));
  let queue: [number, number][] = [];
  let fresh = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === 2) queue.push([r, c]);
      else if (grid[r][c] === 1) fresh += 1;
    }
  }
  let minutes = 0;

  const state = (): GridState => ({
    cells: grid.map((row) =>
      row.map((v) => ({
        label: v === 0 ? "" : v === 1 ? "🍊" : "×",
        blocked: v === 0,
        tone: v === 0 ? "muted" : v === 1 ? "good" : "bad",
      })),
    ),
    panel: {
      label: "rotten front",
      kind: "queue",
      items: queue.map(([r, c]) => ({ text: `${r},${c}`, tone: "bad" })),
    },
    legend: [
      { label: "minute", value: String(minutes), tone: "warn" },
      { label: "fresh left", value: String(fresh), tone: fresh ? "good" : "muted" },
    ],
  });

  t.push(
    state(),
    `${queue.length} orange${queue.length === 1 ? " is" : "s are"} already rotten, and **all of them** seed the queue at once. That is the multi-source trick: several starting points in one BFS, which spreads from all of them simultaneously rather than needing one search per source.`,
    { line: 7, phase: "setup", watch: [w("sources", queue.length, "bad"), w("fresh", fresh, "good")] },
  );

  while (queue.length && fresh > 0) {
    const levelSize = queue.length;
    const nextQ: [number, number][] = [];

    for (let i = 0; i < levelSize; i++) {
      const [r, c] = queue[i];
      for (const [dr, dc] of DIRS) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
        if (grid[nr][nc] !== 1) continue;
        grid[nr][nc] = 2;
        fresh -= 1;
        nextQ.push([nr, nc]);
      }
    }

    queue = nextQ;
    minutes += 1;

    t.push(
      state(),
      `Minute ${minutes}: every orange adjacent to the previous front has rotted — ${nextQ.length} of them. Processing the queue one **level** at a time is what makes the answer a count of minutes rather than a count of oranges; this is the same level-snapshot trick as tree BFS.`,
      {
        line: 15,
        phase: `minute ${minutes}`,
        watch: [w("minute", minutes, "warn"), w("newly rotten", nextQ.length, "bad"), w("fresh left", fresh, "good")],
      },
    );
  }

  const answer = fresh > 0 ? -1 : minutes;
  t.push(
    state(),
    fresh > 0
      ? `${fresh} orange${fresh === 1 ? "" : "s"} can never rot — they are walled off from every rotten one. Return −1. Checking for this is the part most submissions miss.`
      : `Everything rotted in ${minutes} minute${minutes === 1 ? "" : "s"}. O(rows × cols), and note the loop condition includes the fresh counter so it stops the moment there is nothing left to rot rather than running an extra empty minute.`,
    { line: 16, phase: "answer", watch: [w("answer", answer, answer === -1 ? "bad" : "good")] },
  );

  return capFrames(t.done(answer === -1 ? "unreachable oranges — returns -1" : `${minutes} minutes`));
};

/**
 * Registry. The `algo` prop of <GridPathfinder> indexes this.
 *
 * | key              | grid characters              | uses          |
 * |------------------|------------------------------|---------------|
 * | islands          | `1` land, `0` water          | grid          |
 * | maze-bfs         | `#` wall, `.` open           | grid, start, end |
 * | rotting-oranges  | `2` rotten, `1` fresh, `0` empty | grid      |
 */
export const GRID_ALGOS: Record<string, GridAlgo> = {
  islands,
  "maze-bfs": mazeBfs,
  "rotting-oranges": rottingOranges,
};

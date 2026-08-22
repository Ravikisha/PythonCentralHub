/**
 * algos/graphs.ts — traced graph algorithms for <GraphTraversal>.
 *
 * Every algorithm here renders the *frontier structure* next to the graph — the
 * queue for BFS, the stack for DFS, the zero-indegree queue for Kahn's, the
 * priority queue for Dijkstra. That structure is the difference between the
 * algorithms; the graph walk is almost incidental.
 *
 * AUTHORING FORMAT
 * ----------------
 *     <GraphTraversal
 *       algo="bfs"
 *       edges={[["A","B"], ["A","C"], ["B","D"], ["C","D"]]}
 *       start="A"
 *     />
 *
 * Weighted edges take a third element: ["A","B",4]. Node positions are derived
 * automatically (BFS layers from the start node, or a circle) so authors never
 * hand-place coordinates.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

export interface GraphLayoutNode {
  id: string;
  /** Grid column (fractional allowed — layers centre their nodes). */
  x: number;
  /** Grid row. */
  y: number;
}

export interface GraphEdgeView {
  from: string;
  to: string;
  tone?: Tone;
  label?: string;
  directed?: boolean;
}

export interface GraphPanel {
  label: string;
  items: { text: string; tone?: Tone }[];
  kind?: "stack" | "queue";
}

export interface GraphState {
  nodes: GraphLayoutNode[];
  edges: GraphEdgeView[];
  marks?: Record<string, Tone>;
  /** Annotation under a node — distance, colour, indegree, component id. */
  notes?: Record<string, string>;
  panel?: GraphPanel;
  output?: { text: string; tone?: Tone }[];
  cols: number;
  rows: number;
}

export type RawEdge = [string, string] | [string, string, number];

export interface GraphInput {
  edges?: RawEdge[];
  /** Extra isolated nodes that appear in no edge. */
  nodes?: string[];
  directed?: boolean;
  start?: string;
  /** `layers` (default) stacks BFS depth downward; `circle` for dense graphs. */
  layout?: "layers" | "circle";
}

export type GraphAlgo = (input: GraphInput) => Trace<GraphState>;

// ── graph construction + layout ───────────────────────────────────────────

interface Graph {
  ids: string[];
  adj: Map<string, { to: string; weight: number }[]>;
  edges: RawEdge[];
  directed: boolean;
  layout: GraphLayoutNode[];
  view: GraphEdgeView[];
  cols: number;
  rows: number;
  start: string;
}

const DEFAULT_EDGES: RawEdge[] = [
  ["A", "B"],
  ["A", "C"],
  ["B", "D"],
  ["C", "D"],
  ["C", "E"],
  ["D", "F"],
  ["E", "F"],
];

function build(input: GraphInput): Graph {
  const edges = input.edges ?? DEFAULT_EDGES;
  const directed = input.directed ?? false;

  const ids: string[] = [];
  const seen = new Set<string>();
  const add = (id: string) => {
    if (!seen.has(id)) {
      seen.add(id);
      ids.push(id);
    }
  };
  for (const e of edges) {
    add(e[0]);
    add(e[1]);
  }
  for (const n of input.nodes ?? []) add(n);

  const adj = new Map<string, { to: string; weight: number }[]>();
  for (const id of ids) adj.set(id, []);
  for (const e of edges) {
    const wt = e.length === 3 ? (e[2] as number) : 1;
    adj.get(e[0])!.push({ to: e[1], weight: wt });
    if (!directed) adj.get(e[1])!.push({ to: e[0], weight: wt });
  }
  // Deterministic neighbour order — traces must be reproducible.
  for (const list of adj.values()) list.sort((a, b) => a.to.localeCompare(b.to));

  const start = input.start && seen.has(input.start) ? input.start : (ids[0] ?? "");

  const { layout, cols, rows } =
    (input.layout ?? "layers") === "circle"
      ? circleLayout(ids)
      : layerLayout(ids, adj, start);

  const view: GraphEdgeView[] = edges.map((e) => ({
    from: e[0],
    to: e[1],
    directed,
    label: e.length === 3 ? String(e[2]) : undefined,
  }));

  return { ids, adj, edges, directed, layout, view, cols, rows, start };
}

/** BFS-depth layers, each layer centred. Reads well for DAGs and trees alike. */
function layerLayout(
  ids: string[],
  adj: Map<string, { to: string; weight: number }[]>,
  start: string,
): { layout: GraphLayoutNode[]; cols: number; rows: number } {
  const depth = new Map<string, number>();
  const order: string[] = [];

  // Seed from `start`, then from any node still unreached (disconnected parts).
  for (const seed of [start, ...ids]) {
    if (!seed || depth.has(seed)) continue;
    depth.set(seed, 0);
    const q = [seed];
    while (q.length) {
      const cur = q.shift()!;
      order.push(cur);
      for (const { to } of adj.get(cur) ?? []) {
        if (!depth.has(to)) {
          depth.set(to, depth.get(cur)! + 1);
          q.push(to);
        }
      }
    }
  }

  const byDepth = new Map<number, string[]>();
  for (const id of order) {
    const d = depth.get(id)!;
    byDepth.set(d, [...(byDepth.get(d) ?? []), id]);
  }

  const widest = Math.max(1, ...[...byDepth.values()].map((l) => l.length));
  const layout: GraphLayoutNode[] = [];
  for (const [d, layer] of [...byDepth.entries()].sort((a, b) => a[0] - b[0])) {
    const offset = (widest - layer.length) / 2;
    layer.forEach((id, i) => layout.push({ id, x: offset + i, y: d }));
  }

  return { layout, cols: widest, rows: byDepth.size };
}

/** Even circle — better than layers once the graph is dense or highly cyclic. */
function circleLayout(ids: string[]): { layout: GraphLayoutNode[]; cols: number; rows: number } {
  const n = Math.max(1, ids.length);
  const radius = Math.max(1.4, n / 3.2);
  const layout = ids.map((id, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    return {
      id,
      x: radius + radius * Math.cos(angle),
      y: radius + radius * Math.sin(angle),
    };
  });
  return { layout, cols: Math.ceil(radius * 2) + 1, rows: Math.ceil(radius * 2) + 1 };
}

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

function stager(g: Graph) {
  return function state(
    marks: Record<string, Tone>,
    extra: Partial<Pick<GraphState, "panel" | "output" | "notes" | "edges">> = {},
  ): GraphState {
    return {
      nodes: g.layout,
      edges: extra.edges ?? g.view,
      marks,
      notes: extra.notes,
      panel: extra.panel,
      output: extra.output,
      cols: g.cols,
      rows: g.rows,
    };
  };
}

/** Tint the tree/used edges so the reader sees which edges the algorithm kept. */
function tintEdges(g: Graph, used: Set<string>, rejected?: Set<string>): GraphEdgeView[] {
  return g.view.map((e) => {
    const key = `${e.from}->${e.to}`;
    const rev = `${e.to}->${e.from}`;
    if (used.has(key) || used.has(rev)) return { ...e, tone: "good" };
    if (rejected?.has(key) || rejected?.has(rev)) return { ...e, tone: "bad" };
    return e;
  });
}

// ── 1. Breadth-first search ───────────────────────────────────────────────

const BFS_CODE = [
  "from collections import deque",
  "",
  "def bfs(graph, start):",
  "    seen = {start}                 # mark ON ENQUEUE, not on dequeue",
  "    q = deque([start])",
  "    order = []",
  "    while q:",
  "        node = q.popleft()",
  "        order.append(node)",
  "        for nxt in graph[node]:",
  "            if nxt not in seen:",
  "                seen.add(nxt)",
  "                q.append(nxt)",
  "    return order",
];

export const bfs: GraphAlgo = (input) => {
  const g = build(input);
  const state = stager(g);
  const t = tracer<GraphState>(BFS_CODE);

  const seen = new Set<string>([g.start]);
  const visited = new Set<string>();
  const queue: string[] = [g.start];
  const dist = new Map<string, number>([[g.start, 0]]);
  const treeEdges = new Set<string>();
  const order: { text: string; tone?: Tone }[] = [];

  const panel = (): GraphPanel => ({
    label: "queue",
    kind: "queue",
    items: queue.map((id) => ({ text: id, tone: "info" })),
  });
  const notes = () => Object.fromEntries([...dist.entries()].map(([k, v]) => [k, `d=${v}`]));
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = seen.has(id) ? "info" : "muted";
    for (const id of visited) m[id] = "good";
    for (const id of queue) m[id] = "warn";
    if (cur) m[cur] = "active";
    return m;
  };

  t.push(
    state(marks(g.start), { panel: panel(), notes: notes(), output: [] }),
    `Enqueue ${g.start} and mark it seen *now*, at enqueue time. Marking on dequeue instead is the most common BFS bug: a node reachable by two edges gets queued twice and the queue can blow up.`,
    { line: 4, phase: "seed", watch: [w("queue", queue.join(" "), "warn")] },
  );

  while (queue.length) {
    const cur = queue.shift()!;
    visited.add(cur);
    order.push({ text: cur, tone: "good" });

    const fresh: string[] = [];
    for (const { to } of g.adj.get(cur) ?? []) {
      if (!seen.has(to)) {
        seen.add(to);
        dist.set(to, dist.get(cur)! + 1);
        treeEdges.add(`${cur}->${to}`);
        queue.push(to);
        fresh.push(to);
      }
    }

    t.push(
      state(marks(cur), {
        panel: panel(),
        notes: notes(),
        output: [...order],
        edges: tintEdges(g, treeEdges),
      }),
      fresh.length
        ? `Dequeue ${cur} (distance ${dist.get(cur)}). Its unseen neighbours ${fresh.join(", ")} get distance ${dist.get(cur)! + 1} and join the back of the queue. Because the queue is FIFO, every node is reached by a shortest path first — that is why BFS gives shortest paths on an unweighted graph.`
        : `Dequeue ${cur} (distance ${dist.get(cur)}). Every neighbour is already seen, so nothing is enqueued.`,
      {
        line: 13,
        phase: "explore",
        watch: [w("node", cur, "active"), w("dist", dist.get(cur) ?? 0, "good"), w("queue", queue.join(" ") || "∅", "warn")],
      },
    );
  }

  t.push(
    state(Object.fromEntries(g.ids.map((id) => [id, (visited.has(id) ? "good" : "muted") as Tone])), {
      notes: notes(),
      output: [...order],
      edges: tintEdges(g, treeEdges),
    }),
    `Visit order: ${order.map((o) => o.text).join(" → ")}. Each vertex leaves the queue once and each edge is examined once, so BFS is O(V + E). The green edges form the BFS tree — the shortest-path tree from ${g.start}.`,
    { line: 14, phase: "answer" },
  );

  return capFrames(t.done(`order = [${order.map((o) => o.text).join(", ")}]`));
};

// ── 2. Depth-first search ─────────────────────────────────────────────────

const DFS_CODE = [
  "def dfs(graph, start):",
  "    seen, order = set(), []",
  "    stack = [start]",
  "    while stack:",
  "        node = stack.pop()          # LIFO — the only line that differs from BFS",
  "        if node in seen: continue",
  "        seen.add(node)",
  "        order.append(node)",
  "        for nxt in reversed(graph[node]):",
  "            if nxt not in seen:",
  "                stack.append(nxt)",
  "    return order",
];

export const dfs: GraphAlgo = (input) => {
  const g = build(input);
  const state = stager(g);
  const t = tracer<GraphState>(DFS_CODE);

  const seen = new Set<string>();
  const stack: string[] = [g.start];
  const treeEdges = new Set<string>();
  const parent = new Map<string, string>();
  const order: { text: string; tone?: Tone }[] = [];

  const panel = (): GraphPanel => ({
    label: "stack",
    kind: "stack",
    items: stack.map((id, i) => ({ text: id, tone: i === stack.length - 1 ? "active" : "info" })),
  });
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = seen.has(id) ? "good" : "muted";
    for (const id of stack) if (!seen.has(id)) m[id] = "warn";
    if (cur) m[cur] = "active";
    return m;
  };

  t.push(
    state(marks(g.start), { panel: panel(), output: [] }),
    `Push ${g.start}. The *only* structural difference from BFS is that this container pops from the end instead of the front — swap the deque for a list and breadth becomes depth.`,
    { line: 3, phase: "seed" },
  );

  while (stack.length) {
    const cur = stack.pop()!;
    if (seen.has(cur)) {
      t.push(
        state(marks(cur), { panel: panel(), output: [...order], edges: tintEdges(g, treeEdges) }),
        `${cur} was already visited by the time it came off the stack — skip it. With a stack you must check on *pop*, not on push, because a node can be pushed several times before it is popped.`,
        { line: 6, phase: "skip", watch: [w("node", cur, "muted")] },
      );
      continue;
    }
    seen.add(cur);
    order.push({ text: cur, tone: "good" });
    const p = parent.get(cur);
    if (p) treeEdges.add(`${p}->${cur}`);

    const pushed: string[] = [];
    const neighbours = [...(g.adj.get(cur) ?? [])].reverse();
    for (const { to } of neighbours) {
      if (!seen.has(to)) {
        stack.push(to);
        if (!parent.has(to)) parent.set(to, cur);
        pushed.push(to);
      }
    }

    t.push(
      state(marks(cur), { panel: panel(), output: [...order], edges: tintEdges(g, treeEdges) }),
      pushed.length
        ? `Visit ${cur} and push its unvisited neighbours ${pushed.join(", ")}. Whichever went on last comes off first, so the walk dives deep before it goes wide.`
        : `Visit ${cur}. No unvisited neighbours, so the search will backtrack to whatever is still on the stack.`,
      {
        line: 11,
        phase: pushed.length ? "descend" : "backtrack",
        watch: [w("node", cur, "active"), w("stack", stack.join(" ") || "∅", "warn"), w("visited", seen.size, "good")],
      },
    );
  }

  t.push(
    state(Object.fromEntries(g.ids.map((id) => [id, (seen.has(id) ? "good" : "muted") as Tone])), {
      output: [...order],
      edges: tintEdges(g, treeEdges),
    }),
    `Visit order: ${order.map((o) => o.text).join(" → ")}. O(V + E), same as BFS — but the order is depth-first, and unlike BFS the distances found are not shortest paths.`,
    { line: 12, phase: "answer" },
  );

  return capFrames(t.done(`order = [${order.map((o) => o.text).join(", ")}]`));
};

// ── 3. Topological sort, Kahn's algorithm ─────────────────────────────────

const KAHN_CODE = [
  "def topo_sort(graph, n):",
  "    indeg = {v: 0 for v in graph}",
  "    for v in graph:",
  "        for u in graph[v]: indeg[u] += 1",
  "    q = deque([v for v in graph if indeg[v] == 0])",
  "    out = []",
  "    while q:",
  "        v = q.popleft()",
  "        out.append(v)",
  "        for u in graph[v]:",
  "            indeg[u] -= 1            # 'remove' the edge v→u",
  "            if indeg[u] == 0:",
  "                q.append(u)",
  "    return out if len(out) == n else []   # short output ⇒ a cycle exists",
];

export const topoKahn: GraphAlgo = (input) => {
  const g = build({ ...input, directed: true });
  const state = stager(g);
  const t = tracer<GraphState>(KAHN_CODE);

  const indeg = new Map<string, number>(g.ids.map((id) => [id, 0]));
  for (const e of g.edges) indeg.set(e[1], (indeg.get(e[1]) ?? 0) + 1);

  const queue = g.ids.filter((id) => indeg.get(id) === 0);
  const out: { text: string; tone?: Tone }[] = [];
  const removed = new Set<string>();
  const usedEdges = new Set<string>();

  const notes = () => Object.fromEntries([...indeg.entries()].map(([k, v]) => [k, `in=${v}`]));
  const panel = (): GraphPanel => ({
    label: "indeg 0",
    kind: "queue",
    items: queue.map((id) => ({ text: id, tone: "warn" })),
  });
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = removed.has(id) ? "good" : indeg.get(id) === 0 ? "warn" : "info";
    if (cur) m[cur] = "active";
    return m;
  };

  t.push(
    state(marks(), { panel: panel(), notes: notes(), output: [] }),
    `Count how many prerequisites each node has. The ${queue.length} node${queue.length === 1 ? "" : "s"} with indegree 0 (${queue.join(", ") || "none"}) depend on nothing, so they are the only legal first choices.`,
    { line: 5, phase: "setup", watch: [w("ready", queue.join(" ") || "∅", "warn")] },
  );

  while (queue.length) {
    const cur = queue.shift()!;
    removed.add(cur);
    out.push({ text: cur, tone: "good" });

    const freed: string[] = [];
    for (const { to } of g.adj.get(cur) ?? []) {
      usedEdges.add(`${cur}->${to}`);
      indeg.set(to, indeg.get(to)! - 1);
      if (indeg.get(to) === 0) {
        queue.push(to);
        freed.push(to);
      }
    }

    t.push(
      state(marks(cur), { panel: panel(), notes: notes(), output: [...out], edges: tintEdges(g, usedEdges) }),
      freed.length
        ? `Take ${cur} — all its prerequisites are done. Removing its outgoing edges drops ${freed.join(", ")} to indegree 0, so they become available.`
        : `Take ${cur}. Decrementing its successors frees nobody yet — they still have other prerequisites.`,
      {
        line: 13,
        phase: "emit",
        watch: [w("emit", cur, "good"), w("order", out.map((o) => o.text).join(" "), "good"), w("ready", queue.join(" ") || "∅", "warn")],
      },
    );
  }

  const complete = out.length === g.ids.length;
  const stuck = g.ids.filter((id) => !removed.has(id));

  t.push(
    state(
      Object.fromEntries(
        g.ids.map((id) => [id, (removed.has(id) ? "good" : "bad") as Tone]),
      ),
      { notes: notes(), output: [...out], edges: tintEdges(g, usedEdges) },
    ),
    complete
      ? `Topological order: ${out.map((o) => o.text).join(" → ")}. Because every node was emitted, the graph is acyclic.`
      : `Only ${out.length} of ${g.ids.length} nodes could be emitted — ${stuck.join(", ")} never reached indegree 0, so they sit on a cycle. This length check is how Kahn's algorithm doubles as a cycle detector (LC 207 "Course Schedule" is exactly this).`,
    { line: 14, phase: "answer", watch: [w("emitted", `${out.length}/${g.ids.length}`, complete ? "good" : "bad")] },
  );

  return capFrames(
    t.done(complete ? `topo order = [${out.map((o) => o.text).join(", ")}]` : "cycle detected — no topological order"),
  );
};

// ── 4. Cycle detection in a directed graph (three-colour DFS) ─────────────

const CYCLE_CODE = [
  "WHITE, GREY, BLACK = 0, 1, 2   # unseen, on the stack, finished",
  "",
  "def has_cycle(graph):",
  "    color = {v: WHITE for v in graph}",
  "    def dfs(v):",
  "        color[v] = GREY",
  "        for u in graph[v]:",
  "            if color[u] == GREY:   return True   # back edge → cycle",
  "            if color[u] == WHITE and dfs(u): return True",
  "        color[v] = BLACK",
  "        return False",
  "    return any(dfs(v) for v in graph if color[v] == WHITE)",
];

export const cycleDirected: GraphAlgo = (input) => {
  const g = build({
    ...input,
    directed: true,
    edges: input.edges ?? [["A", "B"], ["B", "C"], ["C", "A"], ["C", "D"]],
  });
  const state = stager(g);
  const t = tracer<GraphState>(CYCLE_CODE);

  const color = new Map<string, 0 | 1 | 2>(g.ids.map((id) => [id, 0]));
  const stack: string[] = [];
  const found = { edge: null as [string, string] | null };

  const toneOf = (c: 0 | 1 | 2): Tone => (c === 0 ? "muted" : c === 1 ? "warn" : "good");
  const notes = () =>
    Object.fromEntries(
      [...color.entries()].map(([k, v]) => [k, v === 0 ? "white" : v === 1 ? "grey" : "black"]),
    );
  const panel = (): GraphPanel => ({
    label: "dfs stack",
    kind: "stack",
    items: stack.map((id, i) => ({ text: id, tone: i === stack.length - 1 ? "active" : "warn" })),
  });
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const [id, c] of color) m[id] = toneOf(c);
    if (cur) m[cur] = "active";
    return m;
  };

  const walk = (v: string): boolean => {
    color.set(v, 1);
    stack.push(v);
    t.push(
      state(marks(v), { panel: panel(), notes: notes() }),
      `Colour ${v} grey — it is now on the recursion stack. Grey means "an ancestor of whatever we look at next".`,
      { line: 6, phase: "enter", watch: [w("node", v, "active"), w("stack", stack.join(" "), "warn")] },
    );

    for (const { to } of g.adj.get(v) ?? []) {
      const c = color.get(to)!;
      if (c === 1) {
        found.edge = [v, to];
        t.push(
          state({ ...marks(v), [to]: "bad", [v]: "bad" }, {
            panel: panel(),
            notes: notes(),
            edges: g.view.map((e) => (e.from === v && e.to === to ? { ...e, tone: "bad" } : e)),
          }),
          `Edge ${v} → ${to} points at a grey node, meaning ${to} is an ancestor still on the stack. That is a back edge, and a back edge is a cycle. Note a *black* neighbour would be fine — it is finished, so it cannot be an ancestor. Confusing "already visited" with "on the stack" is the classic wrong answer here.`,
          { line: 8, phase: "cycle!", watch: [w("back edge", `${v}→${to}`, "bad")] },
        );
        stack.pop();
        return true;
      }
      if (c === 0) {
        t.push(
          state(marks(v), { panel: panel(), notes: notes() }),
          `${to} is white (never seen). Recurse into it.`,
          { line: 9, phase: "descend", watch: [w("into", to, "active")] },
        );
        if (walk(to)) {
          stack.pop();
          return true;
        }
      } else {
        t.push(
          state(marks(v), { panel: panel(), notes: notes() }),
          `${to} is black — fully explored on an earlier branch and no longer on the stack, so this edge proves nothing. Skip it.`,
          { line: 7, phase: "skip", watch: [w("neighbour", to, "good")] },
        );
      }
    }

    color.set(v, 2);
    stack.pop();
    t.push(
      state(marks(stack[stack.length - 1]), { panel: panel(), notes: notes() }),
      `${v} has no unexplored edges left, so colour it black and pop it. Black nodes are permanently safe.`,
      { line: 10, phase: "finish", watch: [w("finished", v, "good")] },
    );
    return false;
  };

  let cyclic = false;
  for (const id of g.ids) {
    if (color.get(id) === 0 && walk(id)) {
      cyclic = true;
      break;
    }
  }

  t.push(
    state(
      Object.fromEntries(
        g.ids.map((id) => [
          id,
          (found.edge && (found.edge[0] === id || found.edge[1] === id) ? "bad" : cyclic ? "muted" : "good") as Tone,
        ]),
      ),
      { notes: notes() },
    ),
    cyclic
      ? `The graph has a cycle, witnessed by the back edge ${found.edge![0]} → ${found.edge![1]}.`
      : `Every node finished black without ever meeting a grey neighbour, so the graph is acyclic — a DAG.`,
    { line: 12, phase: "answer", watch: [w("cyclic", cyclic ? "True" : "False", cyclic ? "bad" : "good")] },
  );

  return capFrames(t.done(cyclic ? "cycle found" : "acyclic (DAG)"));
};

// ── 5. Bipartite check / two-colouring (LC 785) ───────────────────────────

const BIPARTITE_CODE = [
  "def is_bipartite(graph):",
  "    color = {}",
  "    for s in graph:",
  "        if s in color: continue",
  "        color[s] = 0",
  "        q = deque([s])",
  "        while q:",
  "            v = q.popleft()",
  "            for u in graph[v]:",
  "                if u not in color:",
  "                    color[u] = 1 - color[v]",
  "                    q.append(u)",
  "                elif color[u] == color[v]:",
  "                    return False        # odd cycle",
  "    return True",
];

export const bipartite: GraphAlgo = (input) => {
  const g = build({
    ...input,
    edges: input.edges ?? [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]],
  });
  const state = stager(g);
  const t = tracer<GraphState>(BIPARTITE_CODE);

  const color = new Map<string, 0 | 1>();
  const queue: string[] = [];
  const conflict = { edge: null as [string, string] | null };

  const notes = () => Object.fromEntries([...color.entries()].map(([k, v]) => [k, v === 0 ? "red" : "blue"]));
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = "muted";
    for (const [id, c] of color) m[id] = c === 0 ? "bad" : "active";
    if (cur) m[cur] = "warn";
    return m;
  };
  const panel = (): GraphPanel => ({
    label: "queue",
    kind: "queue",
    items: queue.map((id) => ({ text: id, tone: "info" })),
  });

  let ok = true;
  outer: for (const s of g.ids) {
    if (color.has(s)) continue;
    color.set(s, 0);
    queue.length = 0;
    queue.push(s);
    t.push(
      state(marks(s), { panel: panel(), notes: notes() }),
      `Start a fresh component at ${s} and paint it red. The choice is arbitrary — only the *alternation* matters.`,
      { line: 5, phase: "seed" },
    );

    while (queue.length) {
      const v = queue.shift()!;
      for (const { to } of g.adj.get(v) ?? []) {
        if (!color.has(to)) {
          color.set(to, color.get(v)! === 0 ? 1 : 0);
          queue.push(to);
          t.push(
            state(marks(v), { panel: panel(), notes: notes() }),
            `${to} is uncoloured and adjacent to ${v}, so it must take the opposite colour: ${color.get(to) === 0 ? "red" : "blue"}.`,
            { line: 11, phase: "paint", watch: [w(v, color.get(v) === 0 ? "red" : "blue"), w(to, color.get(to) === 0 ? "red" : "blue", "good")] },
          );
        } else if (color.get(to) === color.get(v)) {
          conflict.edge = [v, to];
          ok = false;
          t.push(
            state({ ...marks(v), [v]: "bad", [to]: "bad" }, {
              panel: panel(),
              notes: notes(),
              edges: g.view.map((e) =>
                (e.from === v && e.to === to) || (e.from === to && e.to === v) ? { ...e, tone: "bad" } : e,
              ),
            }),
            `${v} and ${to} are adjacent but already share a colour. No two-colouring exists — equivalently, the graph contains an odd-length cycle.`,
            { line: 14, phase: "conflict", watch: [w("conflict", `${v}–${to}`, "bad")] },
          );
          break outer;
        }
      }
    }
  }

  t.push(
    state(marks(), { notes: notes() }),
    ok
      ? `Every edge joins a red node to a blue one, so the graph is bipartite. The two colour classes are the two sides.`
      : `Not bipartite: ${conflict.edge![0]} and ${conflict.edge![1]} cannot be separated.`,
    { line: 15, phase: "answer", watch: [w("bipartite", ok ? "True" : "False", ok ? "good" : "bad")] },
  );

  return capFrames(t.done(ok ? "bipartite" : "not bipartite (odd cycle)"));
};

// ── 6. Connected components ──────────────────────────────────────────────

const COMPONENTS_CODE = [
  "def count_components(graph):",
  "    seen, count = set(), 0",
  "    for s in graph:",
  "        if s in seen: continue",
  "        count += 1                 # a brand-new component",
  "        stack = [s]",
  "        while stack:",
  "            v = stack.pop()",
  "            if v in seen: continue",
  "            seen.add(v)",
  "            stack.extend(graph[v])",
  "    return count",
];

export const components: GraphAlgo = (input) => {
  const g = build({
    ...input,
    edges: input.edges ?? [["A", "B"], ["B", "C"], ["D", "E"], ["F", "F"]],
  });
  const state = stager(g);
  const t = tracer<GraphState>(COMPONENTS_CODE);

  const comp = new Map<string, number>();
  const seen = new Set<string>();
  let count = 0;
  const COMP_TONES: Tone[] = ["active", "good", "warn", "bad", "info"];

  const notes = () => Object.fromEntries([...comp.entries()].map(([k, v]) => [k, `c${v}`]));
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = comp.has(id) ? COMP_TONES[(comp.get(id)! - 1) % COMP_TONES.length] : "muted";
    if (cur) m[cur] = "active";
    return m;
  };

  for (const s of g.ids) {
    if (seen.has(s)) continue;
    count += 1;
    const stack = [s];
    t.push(
      state(marks(s), { notes: notes() }),
      `${s} has not been reached by any earlier search, so it must belong to a component we have not counted yet. Component count becomes ${count}.`,
      { line: 5, phase: "new", watch: [w("components", count, "good"), w("seed", s, "active")] },
    );
    while (stack.length) {
      const v = stack.pop()!;
      if (seen.has(v)) continue;
      seen.add(v);
      comp.set(v, count);
      for (const { to } of g.adj.get(v) ?? []) if (!seen.has(to)) stack.push(to);
      t.push(
        state(marks(v), { notes: notes(), panel: { label: "stack", kind: "stack", items: stack.map((id) => ({ text: id, tone: "info" })) } }),
        `Claim ${v} for component ${count}. Everything reachable from the seed belongs to the same component, so one flood per unseen node is enough.`,
        { line: 10, phase: `component ${count}`, watch: [w("component", count, "good"), w("seen", seen.size)] },
      );
    }
  }

  t.push(
    state(marks(), { notes: notes() }),
    `${count} connected component${count === 1 ? "" : "s"}. Each node is flooded exactly once across all searches, so the total cost stays O(V + E) no matter how many components there are.`,
    { line: 12, phase: "answer", watch: [w("count", count, "good")] },
  );

  return capFrames(t.done(`${count} component${count === 1 ? "" : "s"}`));
};

// ── 7. Dijkstra's shortest paths ─────────────────────────────────────────

const DIJKSTRA_CODE = [
  "import heapq",
  "",
  "def dijkstra(graph, start):",
  "    dist = {v: inf for v in graph}",
  "    dist[start] = 0",
  "    pq = [(0, start)]",
  "    while pq:",
  "        d, v = heapq.heappop(pq)",
  "        if d > dist[v]: continue      # stale entry — skip",
  "        for u, wt in graph[v]:",
  "            nd = d + wt",
  "            if nd < dist[u]:",
  "                dist[u] = nd",
  "                heapq.heappush(pq, (nd, u))",
  "    return dist",
];

export const dijkstra: GraphAlgo = (input) => {
  const g = build({
    ...input,
    edges: input.edges ?? [
      ["A", "B", 4],
      ["A", "C", 1],
      ["C", "B", 2],
      ["B", "D", 5],
      ["C", "D", 8],
      ["D", "E", 3],
    ],
    directed: input.directed ?? true,
  });
  const state = stager(g);
  const t = tracer<GraphState>(DIJKSTRA_CODE);

  const dist = new Map<string, number>(g.ids.map((id) => [id, Infinity]));
  dist.set(g.start, 0);
  const settled = new Set<string>();
  const treeEdges = new Set<string>();
  /** Simple sorted array stands in for a binary heap — same pop order. */
  const pq: { d: number; v: string }[] = [{ d: 0, v: g.start }];
  const popMin = () => {
    pq.sort((a, b) => a.d - b.d || a.v.localeCompare(b.v));
    return pq.shift()!;
  };

  const fmt = (v: number) => (v === Infinity ? "∞" : String(v));
  const notes = () => Object.fromEntries([...dist.entries()].map(([k, v]) => [k, fmt(v)]));
  const panel = (): GraphPanel => ({
    label: "heap",
    kind: "queue",
    items: [...pq].sort((a, b) => a.d - b.d).map((e) => ({ text: `${e.v}:${e.d}`, tone: "info" })),
  });
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = settled.has(id) ? "good" : dist.get(id) === Infinity ? "muted" : "warn";
    if (cur) m[cur] = "active";
    return m;
  };

  t.push(
    state(marks(g.start), { panel: panel(), notes: notes() }),
    `Every distance starts at infinity except ${g.start}, which is 0. Dijkstra's promise: whichever unsettled node has the smallest tentative distance already has its *final* distance — provided no edge weight is negative.`,
    { line: 6, phase: "seed" },
  );

  while (pq.length) {
    const { d, v } = popMin();
    if (d > (dist.get(v) ?? Infinity)) {
      t.push(
        state(marks(v), { panel: panel(), notes: notes(), edges: tintEdges(g, treeEdges) }),
        `Popped (${v}, ${d}) but ${v}'s distance is already ${fmt(dist.get(v)!)} — this is a stale entry left behind by an earlier, worse push. Skipping it is cheaper than implementing decrease-key.`,
        { line: 9, phase: "stale", watch: [w("stale", `${v}:${d}`, "muted")] },
      );
      continue;
    }
    settled.add(v);

    const improved: string[] = [];
    for (const { to, weight } of g.adj.get(v) ?? []) {
      const nd = d + weight;
      if (nd < (dist.get(to) ?? Infinity)) {
        dist.set(to, nd);
        pq.push({ d: nd, v: to });
        treeEdges.add(`${v}->${to}`);
        improved.push(`${to}→${nd}`);
      }
    }

    t.push(
      state(marks(v), { panel: panel(), notes: notes(), edges: tintEdges(g, treeEdges) }),
      improved.length
        ? `Settle ${v} at distance ${d}. Relaxing its edges improves ${improved.join(", ")}, and each improvement is pushed onto the heap.`
        : `Settle ${v} at distance ${d}. No edge out of ${v} offers a shorter route than what is already known.`,
      {
        line: 14,
        phase: "settle",
        watch: [w("settled", v, "good"), w("dist", d, "good"), w("heap", pq.length, "info")],
      },
    );
  }

  t.push(
    state(Object.fromEntries(g.ids.map((id) => [id, (settled.has(id) ? "good" : "muted") as Tone])), {
      notes: notes(),
      edges: tintEdges(g, treeEdges),
    }),
    `Final distances from ${g.start}: ${[...dist.entries()].map(([k, v]) => `${k}=${fmt(v)}`).join(", ")}. With a binary heap this is O((V + E) log V). A negative edge weight would break the "smallest tentative distance is final" argument — use Bellman-Ford there.`,
    { line: 15, phase: "answer" },
  );

  return capFrames(
    t.done(`dist = { ${[...dist.entries()].map(([k, v]) => `${k}: ${fmt(v)}`).join(", ")} }`),
  );
};

/**
 * Registry. The `algo` prop of <GraphTraversal> indexes this.
 *
 * | key             | uses                          |
 * |-----------------|-------------------------------|
 * | bfs             | edges, start                  |
 * | dfs             | edges, start                  |
 * | topo-kahn       | edges (forced directed)       |
 * | cycle-directed  | edges (forced directed)       |
 * | bipartite       | edges                         |
 * | components      | edges, nodes                  |
 * | dijkstra        | weighted edges, start         |
 */
// ── 8. 0-1 BFS (deque instead of a heap) ─────────────────────────────────

const BFS01_CODE = [
  "from collections import deque",
  "",
  "def bfs01(graph, start):",
  "    dist = {v: inf for v in graph}",
  "    dist[start] = 0",
  "    dq = deque([start])",
  "    while dq:",
  "        v = dq.popleft()",
  "        for u, wt in graph[v]:        # wt is 0 or 1 only",
  "            if dist[v] + wt < dist[u]:",
  "                dist[u] = dist[v] + wt",
  "                if wt == 0:",
  "                    dq.appendleft(u)  # same layer — jump the queue",
  "                else:",
  "                    dq.append(u)      # next layer — back of the queue",
  "    return dist",
];

/**
 * 0-1 BFS: shortest paths when every weight is 0 or 1. A deque replaces the heap
 * because only two layers are ever live at once — a 0-edge lands in the current
 * layer (push front) and a 1-edge in the next (push back), so the deque stays
 * sorted by construction. The picture that matters is the deque's contents: the
 * reader can see it holding at most two distinct distances, which is the invariant
 * that makes the log factor unnecessary.
 */
export const bfs01: GraphAlgo = (input) => {
  const g = build({
    ...input,
    edges: input.edges ?? [
      ["A", "B", 0],
      ["A", "C", 1],
      ["B", "D", 1],
      ["C", "D", 0],
      ["C", "E", 1],
      ["D", "E", 0],
    ],
    directed: input.directed ?? false,
  });
  const state = stager(g);
  const t = tracer<GraphState>(BFS01_CODE);

  const dist = new Map<string, number>(g.ids.map((id) => [id, Infinity]));
  dist.set(g.start, 0);
  const treeEdges = new Set<string>();
  const dq: string[] = [g.start];
  let relaxations = 0;

  const fmt = (v: number) => (v === Infinity ? "∞" : String(v));
  const notes = () => Object.fromEntries([...dist.entries()].map(([k, v]) => [k, fmt(v)]));
  const panel = (front?: string): GraphPanel => ({
    label: "deque",
    kind: "queue",
    items: dq.map((v) => ({
      text: `${v}:${fmt(dist.get(v) ?? Infinity)}`,
      tone: (v === front ? "active" : "info") as Tone,
    })),
  });
  const marks = (cur?: string): Record<string, Tone> => {
    const m: Record<string, Tone> = {};
    for (const id of g.ids) m[id] = dist.get(id) === Infinity ? "muted" : "warn";
    if (cur) m[cur] = "active";
    return m;
  };
  /** The distances currently sitting in the deque — the invariant to watch. */
  const layers = () => [...new Set(dq.map((v) => dist.get(v) ?? Infinity))].sort((a, b) => a - b);

  t.push(
    state(marks(g.start), { panel: panel(g.start), notes: notes() }),
    `Every weight in this graph is 0 or 1, which is the entire precondition. Dijkstra would work, but its heap is doing no useful sorting: with only two possible weights, at most two distinct distances are ever in flight, so a **deque** keeps them in order for free. Start at ${g.start} with distance 0.`,
    { line: 6, phase: "seed", watch: [w("deque", dq.length, "info")] },
  );

  while (dq.length) {
    const v = dq.shift()!;
    const d = dist.get(v) ?? Infinity;
    const improved: string[] = [];

    for (const { to, weight } of g.adj.get(v) ?? []) {
      const nd = d + weight;
      relaxations++;
      if (nd < (dist.get(to) ?? Infinity)) {
        dist.set(to, nd);
        treeEdges.add(`${v}->${to}`);
        if (weight === 0) dq.unshift(to);
        else dq.push(to);
        improved.push(`${to}→${nd} (${weight === 0 ? "front" : "back"})`);
      }
    }

    t.push(
      state(marks(v), { panel: panel(), notes: notes(), edges: tintEdges(g, treeEdges) }),
      improved.length
        ? `Pop ${v} from the **front** at distance ${fmt(d)}. Relaxing its edges improves ${improved.join(
            ", ",
          )}. A 0-weight edge reaches a node in the *same* layer, so it goes to the front and will be processed before anything at distance ${fmt(d) === "∞" ? "d" : String(d + 1)}; a 1-weight edge belongs to the next layer and goes to the back. That placement rule is the whole algorithm.`
        : `Pop ${v} at distance ${fmt(d)}. Nothing improves — every neighbour already has a distance this small or smaller, so nothing is pushed. Note that ${v} may be popped again later from a stale push; the "< dist[u]" guard makes the repeat harmless.`,
      {
        line: improved.length ? 14 : 10,
        phase: `pop ${v}`,
        watch: [
          w("popped", v, "active"),
          w("dist", fmt(d), "good"),
          w("deque holds", layers().map(fmt).join(" and ") || "—", "warn"),
          w("relaxations", relaxations, "info"),
        ],
      },
    );
  }

  t.push(
    state(Object.fromEntries(g.ids.map((id) => [id, (dist.get(id) === Infinity ? "muted" : "good") as Tone])), {
      notes: notes(),
      edges: tintEdges(g, treeEdges),
    }),
    `Final distances from ${g.start}: ${[...dist.entries()]
      .map(([k, v]) => `${k}=${fmt(v)}`)
      .join(", ")}. Note what never happened: no comparison-based ordering, no heap, no decrease-key. O(V + E) rather than Dijkstra's O((V + E) log V), from ${relaxations} relaxations. The deque held at most two distinct distances at every step — check the "deque holds" watch by scrubbing back — and that is the invariant the correctness proof needs.`,
    { line: 17, phase: "answer" },
  );

  return capFrames(
    t.done(`dist = { ${[...dist.entries()].map(([k, v]) => `${k}: ${fmt(v)}`).join(", ")} }`),
  );
};

export const GRAPH_ALGOS: Record<string, GraphAlgo> = {
  bfs,
  dfs,
  "topo-kahn": topoKahn,
  "cycle-directed": cycleDirected,
  bipartite,
  components,
  dijkstra,
  "bfs-01": bfs01,
};

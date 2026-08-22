/**
 * algos/trees.ts — traced binary-tree algorithms for <TreeWalker>.
 *
 * Phase-09 (Patterns · Trees) had zero visualizations before this file existed,
 * which is exactly backwards: tree recursion is the topic where readers most
 * need to see the call stack, because the code is short and the *order* is the
 * whole lesson. Every algorithm here therefore renders a live stack or queue
 * panel alongside the tree.
 *
 * AUTHORING FORMAT
 * ----------------
 * Trees arrive in LeetCode's level-order-with-nulls form, so an MDX author can
 * paste the array straight out of a problem statement:
 *
 *     <TreeWalker algo="level-order" tree={[3, 9, 20, null, null, 15, 7]} />
 *
 * Layout is computed once (in-order x slot, depth y) and shared by every frame,
 * so frames stay small and the tree never jitters between steps.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

/** A node placed on the drawing grid. `x` is a column slot, `y` is depth. */
export interface TreeLayoutNode {
  id: number;
  value: number | string;
  x: number;
  y: number;
}

export interface TreeEdge {
  from: number;
  to: number;
  tone?: Tone;
  label?: string;
}

/** A stack or queue rendered beside the tree — the point of most of these. */
export interface TreePanel {
  label: string;
  items: { text: string; tone?: Tone }[];
  /** `stack` grows downward with the top at the bottom; `queue` reads left→right. */
  kind?: "stack" | "queue";
}

export interface TreeState {
  nodes: TreeLayoutNode[];
  edges: TreeEdge[];
  /** Per-node tone. */
  marks?: Record<number, Tone>;
  /** Small annotation drawn under a node — depth, dp value, subtree size. */
  notes?: Record<number, string>;
  panel?: TreePanel;
  /** The result being accumulated, rendered as an ordered strip. */
  output?: { text: string; tone?: Tone }[];
  /** Grid extents so the renderer can size its viewBox. */
  cols: number;
  depth: number;
}

export interface TreeInput {
  /** Level-order with `null` for absent children, exactly as LeetCode prints it. */
  tree?: (number | string | null)[];
  /** Target value for path-sum / search style algorithms. */
  target?: number;
  /** Two node values for lowest-common-ancestor. */
  p?: number | string;
  q?: number | string;
}

export type TreeAlgo = (input: TreeInput) => Trace<TreeState>;

// ── tree construction + layout ─────────────────────────────────────────────

interface Node {
  id: number;
  value: number | string;
  left: number | null;
  right: number | null;
  depth: number;
}

interface Tree {
  nodes: Map<number, Node>;
  root: number | null;
  layout: TreeLayoutNode[];
  edges: TreeEdge[];
  cols: number;
  depth: number;
}

const DEFAULT_TREE: (number | null)[] = [3, 9, 20, null, null, 15, 7];

/**
 * Build a tree from level-order-with-nulls.
 *
 * The subtlety: a `null` in the array occupies a *slot*, not a node, and its
 * children are not listed at all. So we walk a queue of real nodes and consume
 * two array entries per node — the same rule LeetCode's own deserializer uses.
 */
function build(raw: (number | string | null)[]): Tree {
  const nodes = new Map<number, Node>();
  if (raw.length === 0 || raw[0] === null || raw[0] === undefined) {
    return { nodes, root: null, layout: [], edges: [], cols: 0, depth: 0 };
  }

  let nextId = 0;
  const mk = (value: number | string, depth: number): number => {
    const id = nextId++;
    nodes.set(id, { id, value, left: null, right: null, depth });
    return id;
  };

  const root = mk(raw[0]!, 0);
  const queue: number[] = [root];
  let i = 1;
  while (queue.length > 0 && i < raw.length) {
    const parent = nodes.get(queue.shift()!)!;
    for (const side of ["left", "right"] as const) {
      if (i >= raw.length) break;
      const v = raw[i++];
      if (v === null || v === undefined) continue;
      const child = mk(v, parent.depth + 1);
      parent[side] = child;
      queue.push(child);
    }
  }

  // In-order x assignment — guarantees no two nodes share a column, and puts a
  // BST's values in left-to-right sorted order, which is a lesson in itself.
  let col = 0;
  const layout: TreeLayoutNode[] = [];
  const assign = (id: number | null) => {
    if (id === null) return;
    const n = nodes.get(id)!;
    assign(n.left);
    layout.push({ id, value: n.value, x: col++, y: n.depth });
    assign(n.right);
  };
  assign(root);

  const edges: TreeEdge[] = [];
  for (const n of nodes.values()) {
    if (n.left !== null) edges.push({ from: n.id, to: n.left });
    if (n.right !== null) edges.push({ from: n.id, to: n.right });
  }

  const depth = Math.max(0, ...[...nodes.values()].map((n) => n.depth));
  return { nodes, root, layout, edges, cols: col, depth };
}

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

/** Frame factory bound to one tree — keeps every algorithm below terse. */
function stager(tree: Tree) {
  return function state(
    marks: Record<number, Tone>,
    extra: Partial<Pick<TreeState, "panel" | "output" | "notes" | "edges">> = {},
  ): TreeState {
    return {
      nodes: tree.layout,
      edges: extra.edges ?? tree.edges,
      marks,
      notes: extra.notes,
      panel: extra.panel,
      output: extra.output,
      cols: tree.cols,
      depth: tree.depth,
    };
  };
}

const emptyTrace = (): Trace<TreeState> => ({
  frames: [
    {
      state: { nodes: [], edges: [], cols: 0, depth: 0 },
      caption: "The tree is empty — every one of these algorithms returns its base case immediately.",
      done: true,
    },
  ],
});

/** Marks: visited nodes muted, current active, the rest untouched. */
function visitMarks(visited: Set<number>, current?: number, extra?: Record<number, Tone>): Record<number, Tone> {
  const m: Record<number, Tone> = {};
  for (const id of visited) m[id] = "muted";
  if (current !== undefined) m[current] = "active";
  return { ...m, ...extra };
}

// ── depth-first traversals ────────────────────────────────────────────────

const DFS_CODE = (order: "pre" | "in" | "post") =>
  [
    `def ${order}order(node, out):`,
    "    if node is None:",
    "        return",
    order === "pre" ? "    out.append(node.val)      # visit" : "    # (visit happens below)",
    `    ${order}order(node.left, out)`,
    order === "in" ? "    out.append(node.val)      # visit" : `    ${order}order(node.right, out)`,
    order === "in" ? `    ${order}order(node.right, out)` : "    out.append(node.val)      # visit",
  ].filter((l) => l !== "    # (visit happens below)");

function dfsTraversal(order: "pre" | "in" | "post"): TreeAlgo {
  return (input) => {
    const tree = build(input.tree ?? DEFAULT_TREE);
    if (tree.root === null) return emptyTrace();
    const state = stager(tree);
    const t = tracer<TreeState>(DFS_CODE(order));

    const out: { text: string; tone?: Tone }[] = [];
    const visited = new Set<number>();
    const stack: number[] = [];

    const panel = (): TreePanel => ({
      label: "call stack",
      kind: "stack",
      items: stack.map((id, i) => ({
        text: String(tree.nodes.get(id)!.value),
        tone: i === stack.length - 1 ? "active" : "info",
      })),
    });

    const visitLine = order === "pre" ? 4 : order === "in" ? 6 : 7;

    const walk = (id: number | null) => {
      if (id === null) return;
      const n = tree.nodes.get(id)!;
      stack.push(id);

      t.push(
        state(visitMarks(visited, id), { panel: panel(), output: [...out] }),
        `Enter ${n.value}. The recursive call is pushed onto the stack, which is now ${stack.length} frame${stack.length === 1 ? "" : "s"} deep.`,
        { line: 1, phase: "enter", watch: [w("node", n.value, "active"), w("stack depth", stack.length)] },
      );

      if (order === "pre") {
        out.push({ text: String(n.value), tone: "good" });
        t.push(
          state(visitMarks(visited, id, { [id]: "good" }), { panel: panel(), output: [...out] }),
          `Preorder visits the node *before* its children, so ${n.value} is recorded now.`,
          { line: visitLine, phase: "visit", watch: [w("output", out.map((o) => o.text).join(" ") || "∅", "good")] },
        );
      }

      walk(n.left);

      if (order === "in") {
        out.push({ text: String(n.value), tone: "good" });
        t.push(
          state(visitMarks(visited, id, { [id]: "good" }), { panel: panel(), output: [...out] }),
          `Inorder visits between the two subtrees, so ${n.value} is recorded only after the whole left subtree is done. On a BST this makes the output sorted.`,
          { line: visitLine, phase: "visit", watch: [w("output", out.map((o) => o.text).join(" "), "good")] },
        );
      }

      walk(n.right);

      if (order === "post") {
        out.push({ text: String(n.value), tone: "good" });
        t.push(
          state(visitMarks(visited, id, { [id]: "good" }), { panel: panel(), output: [...out] }),
          `Postorder visits after both children, so ${n.value} is recorded last of its subtree. This is the order you need whenever a node's answer depends on its children.`,
          { line: visitLine, phase: "visit", watch: [w("output", out.map((o) => o.text).join(" "), "good")] },
        );
      }

      stack.pop();
      visited.add(id);
      t.push(
        state(visitMarks(visited, stack[stack.length - 1]), { panel: panel(), output: [...out] }),
        `${n.value} is finished — its frame pops and control returns to ${
          stack.length ? tree.nodes.get(stack[stack.length - 1])!.value : "the caller"
        }.`,
        { line: 3, phase: "return", watch: [w("stack depth", stack.length)] },
      );
    };

    walk(tree.root);

    t.push(
      state(Object.fromEntries(tree.layout.map((n) => [n.id, "good" as Tone])), { output: [...out] }),
      `${order}order traversal: ${out.map((o) => o.text).join(" → ")}. Every node was entered once and left once, so the cost is O(n) time and O(h) stack space where h is the height.`,
      { phase: "answer" },
    );

    return capFrames(t.done(`${order}order = [${out.map((o) => o.text).join(", ")}]`));
  };
}

export const preorder = dfsTraversal("pre");
export const inorder = dfsTraversal("in");
export const postorder = dfsTraversal("post");

// ── breadth-first / level order ──────────────────────────────────────────

const BFS_CODE = [
  "from collections import deque",
  "",
  "def level_order(root):",
  "    if not root: return []",
  "    out, q = [], deque([root])",
  "    while q:",
  "        level = []",
  "        for _ in range(len(q)):     # snapshot the level size!",
  "            node = q.popleft()",
  "            level.append(node.val)",
  "            if node.left:  q.append(node.left)",
  "            if node.right: q.append(node.right)",
  "        out.append(level)",
  "    return out",
];

export const levelOrder: TreeAlgo = (input) => {
  const tree = build(input.tree ?? DEFAULT_TREE);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(BFS_CODE);

  const queue: number[] = [tree.root];
  const visited = new Set<number>();
  const levels: (number | string)[][] = [];

  const panel = (focus?: number): TreePanel => ({
    label: "queue",
    kind: "queue",
    items: queue.map((id) => ({
      text: String(tree.nodes.get(id)!.value),
      tone: id === focus ? "active" : "info",
    })),
  });

  const flatOut = () =>
    levels.flatMap((lv, i) =>
      lv.map((v) => ({ text: String(v), tone: (i === levels.length - 1 ? "good" : "muted") as Tone })),
    );

  t.push(
    state({ [tree.root]: "active" }, { panel: panel(tree.root), output: [] }),
    `Seed the queue with the root. BFS uses a queue (first in, first out) — swap it for a stack and you get DFS instead.`,
    { line: 5, phase: "seed", watch: [w("queue", 1, "active")] },
  );

  let depth = 0;
  while (queue.length > 0) {
    const levelSize = queue.length;
    const level: (number | string)[] = [];
    levels.push(level);

    t.push(
      state(visitMarks(visited, undefined, Object.fromEntries(queue.map((id) => [id, "active" as Tone]))), {
        panel: panel(),
        output: flatOut(),
      }),
      `Level ${depth} starts. The queue holds exactly the ${levelSize} node${levelSize === 1 ? "" : "s"} of this level, so snapshotting its length *before* the inner loop is what separates one level from the next. Reading len(q) inside the loop is the classic bug here.`,
      { line: 8, phase: `level ${depth}`, watch: [w("level", depth), w("levelSize", levelSize, "good")] },
    );

    for (let i = 0; i < levelSize; i++) {
      const id = queue.shift()!;
      const n = tree.nodes.get(id)!;
      level.push(n.value);
      visited.add(id);

      const kids = [n.left, n.right].filter((c): c is number => c !== null);
      for (const c of kids) queue.push(c);

      t.push(
        state(
          visitMarks(visited, id, {
            ...Object.fromEntries(queue.map((q) => [q, "info" as Tone])),
            ...Object.fromEntries(kids.map((c) => [c, "warn" as Tone])),
            [id]: "good",
          }),
          { panel: panel(), output: flatOut() },
        ),
        kids.length
          ? `Dequeue ${n.value}, record it, and enqueue its ${kids.length} child${kids.length === 1 ? "" : "ren"} (${kids.map((c) => tree.nodes.get(c)!.value).join(", ")}) for the next level.`
          : `Dequeue ${n.value} and record it. It is a leaf, so nothing is enqueued.`,
        {
          line: 10,
          phase: `level ${depth}`,
          watch: [w("node", n.value, "good"), w("queue", queue.length, "info"), w("level so far", level.join(" "), "good")],
        },
      );
    }
    depth += 1;
  }

  t.push(
    state(Object.fromEntries(tree.layout.map((n) => [n.id, "good" as Tone])), { output: flatOut() }),
    `Levels: ${levels.map((lv) => `[${lv.join(", ")}]`).join(" ")}. O(n) time; the queue peaks at the widest level, so O(w) space.`,
    { line: 14, phase: "answer" },
  );

  return capFrames(t.done(`levels = ${levels.map((lv) => `[${lv.join(",")}]`).join(", ")}`));
};

// ── right side view (LC 199) ─────────────────────────────────────────────

const RIGHT_VIEW_CODE = [
  "def right_side_view(root):",
  "    if not root: return []",
  "    out, q = [], deque([root])",
  "    while q:",
  "        n = len(q)",
  "        for i in range(n):",
  "            node = q.popleft()",
  "            if i == n - 1:            # last of the level",
  "                out.append(node.val)",
  "            if node.left:  q.append(node.left)",
  "            if node.right: q.append(node.right)",
  "    return out",
];

export const rightSideView: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [1, 2, 3, null, 5, null, 4]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(RIGHT_VIEW_CODE);

  const queue: number[] = [tree.root];
  const visited = new Set<number>();
  const out: { text: string; tone?: Tone }[] = [];
  let depth = 0;

  while (queue.length > 0) {
    const n = queue.length;
    for (let i = 0; i < n; i++) {
      const id = queue.shift()!;
      const node = tree.nodes.get(id)!;
      visited.add(id);
      const isLast = i === n - 1;
      if (isLast) out.push({ text: String(node.value), tone: "good" });

      for (const c of [node.left, node.right]) if (c !== null) queue.push(c);

      t.push(
        state(visitMarks(visited, id, { [id]: isLast ? "good" : "muted" }), {
          panel: {
            label: "queue",
            kind: "queue",
            items: queue.map((q) => ({ text: String(tree.nodes.get(q)!.value), tone: "info" })),
          },
          output: [...out],
        }),
        isLast
          ? `${node.value} is the last node dequeued from level ${depth}, so it is the one you would see standing to the right of the tree. Record it.`
          : `${node.value} is level ${depth} position ${i + 1} of ${n} — something to its right will overwrite it in the view, so skip it.`,
        {
          line: isLast ? 9 : 6,
          phase: `level ${depth}`,
          watch: [w("i", `${i} of ${n - 1}`), w("last?", isLast ? "yes" : "no", isLast ? "good" : "muted"), w("view", out.map((o) => o.text).join(" "), "good")],
        },
      );
    }
    depth += 1;
  }

  t.push(
    state(Object.fromEntries(tree.layout.map((nd) => [nd.id, "muted" as Tone])), { output: [...out] }),
    `Right-side view: ${out.map((o) => o.text).join(" → ")}. The whole trick is "the last node popped from each level" — no geometry needed.`,
    { line: 12, phase: "answer" },
  );

  return capFrames(t.done(`view = [${out.map((o) => o.text).join(", ")}]`));
};

// ── maximum depth (LC 104) ───────────────────────────────────────────────

const DEPTH_CODE = [
  "def max_depth(node):",
  "    if node is None:",
  "        return 0",
  "    left  = max_depth(node.left)",
  "    right = max_depth(node.right)",
  "    return 1 + max(left, right)",
];

export const maxDepth: TreeAlgo = (input) => {
  const tree = build(input.tree ?? DEFAULT_TREE);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(DEPTH_CODE);

  const notes: Record<number, string> = {};
  const stack: number[] = [];
  const done = new Set<number>();

  const panel = (): TreePanel => ({
    label: "call stack",
    kind: "stack",
    items: stack.map((id, i) => ({
      text: String(tree.nodes.get(id)!.value),
      tone: i === stack.length - 1 ? "active" : "info",
    })),
  });

  const walk = (id: number | null): number => {
    if (id === null) return 0;
    const n = tree.nodes.get(id)!;
    stack.push(id);
    t.push(
      state(visitMarks(done, id), { panel: panel(), notes: { ...notes } }),
      `Descend into ${n.value}. Its own answer is unknown until both children report back — this is why depth is a postorder computation.`,
      { line: 1, phase: "descend", watch: [w("node", n.value, "active"), w("depth", stack.length)] },
    );

    const l = walk(n.left);
    const r = walk(n.right);
    const d = 1 + Math.max(l, r);
    notes[id] = `h=${d}`;
    done.add(id);
    stack.pop();

    t.push(
      state(visitMarks(done, stack[stack.length - 1], { [id]: "good" }), { panel: panel(), notes: { ...notes } }),
      `${n.value} now knows both subtree heights (left ${l}, right ${r}), so its own height is 1 + max(${l}, ${r}) = ${d}. Return that up.`,
      { line: 6, phase: "combine", watch: [w("left", l), w("right", r), w("height", d, "good")] },
    );
    return d;
  };

  const answer = walk(tree.root);

  t.push(
    state(Object.fromEntries(tree.layout.map((nd) => [nd.id, "good" as Tone])), { notes: { ...notes } }),
    `Maximum depth is ${answer}. Every node computed its height exactly once from its children's — O(n) time, O(h) stack.`,
    { line: 6, phase: "answer", watch: [w("answer", answer, "good")] },
  );

  return capFrames(t.done(`max depth = ${answer}`));
};

// ── diameter (LC 543) ────────────────────────────────────────────────────

const DIAMETER_CODE = [
  "def diameter(root):",
  "    best = 0",
  "    def height(node):",
  "        nonlocal best",
  "        if node is None: return 0",
  "        l = height(node.left)",
  "        r = height(node.right)",
  "        best = max(best, l + r)     # path THROUGH this node",
  "        return 1 + max(l, r)        # height reported UP",
  "    height(root)",
  "    return best",
];

export const diameter: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [1, 2, 3, 4, 5]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(DIAMETER_CODE);

  const notes: Record<number, string> = {};
  const done = new Set<number>();
  let best = 0;
  let bestAt: number | null = null;

  const height = (id: number | null): number => {
    if (id === null) return 0;
    const n = tree.nodes.get(id)!;
    const l = height(n.left);
    const r = height(n.right);
    const through = l + r;
    const improved = through > best;
    if (improved) {
      best = through;
      bestAt = id;
    }
    const h = 1 + Math.max(l, r);
    notes[id] = `h=${h} ∪=${through}`;
    done.add(id);

    t.push(
      state(visitMarks(done, id, { [id]: improved ? "good" : "active", ...(bestAt !== null ? { [bestAt]: "good" } : {}) }), {
        notes: { ...notes },
      }),
      `At ${n.value}: left height ${l}, right height ${r}. The longest path *through* ${n.value} uses ${l} + ${r} = ${through} edges${improved ? ` — a new best.` : `, which does not beat ${best}.`} But the value returned upward is the height, 1 + max(${l}, ${r}) = ${h}. Keeping those two numbers distinct is the entire difficulty of this problem.`,
      {
        line: improved ? 8 : 9,
        phase: "combine",
        watch: [w("through", through, improved ? "good" : "muted"), w("height", h, "active"), w("best", best, "good")],
      },
    );
    return h;
  };

  height(tree.root);

  t.push(
    state(Object.fromEntries(tree.layout.map((nd) => [nd.id, nd.id === bestAt ? "good" : "muted" as Tone])), {
      notes: { ...notes },
    }),
    `Diameter is ${best} edges, and the deepest path bends at ${bestAt !== null ? tree.nodes.get(bestAt)!.value : "the root"}. Note the answer is counted in *edges* — if the problem asks for nodes, add one.`,
    { line: 11, phase: "answer", watch: [w("diameter", best, "good")] },
  );

  return capFrames(t.done(`diameter = ${best} edges`));
};

// ── validate BST (LC 98) ─────────────────────────────────────────────────

const VALID_BST_CODE = [
  "def is_valid(node, low=-inf, high=+inf):",
  "    if node is None:",
  "        return True",
  "    if not (low < node.val < high):",
  "        return False          # window violated",
  "    return (is_valid(node.left,  low, node.val) and",
  "            is_valid(node.right, node.val, high))",
];

export const validateBst: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [5, 1, 7, null, null, 6, 8]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(VALID_BST_CODE);

  const notes: Record<number, string> = {};
  const done = new Set<number>();
  let verdict = true;
  let culprit: number | null = null;

  const fmt = (v: number) => (v === -Infinity ? "−∞" : v === Infinity ? "+∞" : String(v));

  const walk = (id: number | null, low: number, high: number): boolean => {
    if (id === null) return true;
    const n = tree.nodes.get(id)!;
    const v = Number(n.value);
    notes[id] = `(${fmt(low)}, ${fmt(high)})`;
    const ok = low < v && v < high;

    t.push(
      state(visitMarks(done, id, { [id]: ok ? "active" : "bad" }), { notes: { ...notes } }),
      ok
        ? `${v} must lie strictly inside (${fmt(low)}, ${fmt(high)}) — it does. Recurse, narrowing the window: the left child inherits (${fmt(low)}, ${v}) and the right child (${v}, ${fmt(high)}).`
        : `${v} must lie inside (${fmt(low)}, ${fmt(high)}) but does not. This is the failure a "check only against the parent" solution misses — a node can beat its parent and still violate an ancestor.`,
      {
        line: ok ? 6 : 5,
        phase: ok ? "check" : "violation",
        watch: [w("node", v, ok ? "active" : "bad"), w("low", fmt(low)), w("high", fmt(high)), w("ok?", ok ? "yes" : "NO", ok ? "good" : "bad")],
      },
    );

    if (!ok) {
      verdict = false;
      culprit = id;
      return false;
    }
    done.add(id);
    return walk(n.left, low, v) && walk(n.right, v, high);
  };

  walk(tree.root, -Infinity, Infinity);

  t.push(
    state(
      Object.fromEntries(
        tree.layout.map((nd) => [nd.id, (culprit === nd.id ? "bad" : verdict ? "good" : "muted") as Tone]),
      ),
      { notes: { ...notes } },
    ),
    verdict
      ? `Every node fell inside its inherited window, so this is a valid BST. The (low, high) window — not a parent comparison — is what makes the check correct.`
      : `Not a valid BST: ${culprit !== null ? tree.nodes.get(culprit)!.value : "a node"} escaped its ancestors' window.`,
    { line: 7, phase: "answer", watch: [w("valid", verdict ? "True" : "False", verdict ? "good" : "bad")] },
  );

  return capFrames(t.done(verdict ? "valid BST" : "not a BST"));
};

// ── lowest common ancestor (LC 236) ──────────────────────────────────────

const LCA_CODE = [
  "def lca(node, p, q):",
  "    if node is None or node.val in (p, q):",
  "        return node",
  "    left  = lca(node.left,  p, q)",
  "    right = lca(node.right, p, q)",
  "    if left and right:",
  "        return node          # p and q split here → this is the LCA",
  "    return left or right     # both targets on one side",
];

export const lca: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(LCA_CODE);

  const p = String(input.p ?? 5);
  const q = String(input.q ?? 4);
  const targets = new Set([p, q]);
  const done = new Set<number>();
  const notes: Record<number, string> = {};
  let answer: number | null = null;

  const targetMarks = (): Record<number, Tone> =>
    Object.fromEntries(
      tree.layout.filter((n) => targets.has(String(n.value))).map((n) => [n.id, "warn" as Tone]),
    );

  const walk = (id: number | null): number | null => {
    if (id === null) return null;
    const n = tree.nodes.get(id)!;
    if (targets.has(String(n.value))) {
      notes[id] = "found";
      done.add(id);
      t.push(
        state({ ...visitMarks(done, id), ...targetMarks(), [id]: "good" }, { notes: { ...notes } }),
        `${n.value} is one of the two targets. Return it upward — the recursion does not need to search below a target, because any node below it would have this node as its ancestor anyway.`,
        { line: 3, phase: "found", watch: [w("node", n.value, "good")] },
      );
      return id;
    }

    const l = walk(n.left);
    const r = walk(n.right);
    done.add(id);

    if (l !== null && r !== null) {
      notes[id] = "LCA";
      answer = id;
      t.push(
        state({ ...visitMarks(done, id), ...targetMarks(), [id]: "good" }, { notes: { ...notes } }),
        `Both subtrees of ${n.value} reported a target, so the two targets are on opposite sides. ${n.value} is the lowest node that can say that — it is the LCA.`,
        { line: 7, phase: "split", watch: [w("left", tree.nodes.get(l)!.value, "good"), w("right", tree.nodes.get(r)!.value, "good"), w("LCA", n.value, "good")] },
      );
      return id;
    }

    const pass = l ?? r;
    t.push(
      state({ ...visitMarks(done, id), ...targetMarks() }, { notes: { ...notes } }),
      pass === null
        ? `Neither subtree of ${n.value} contains a target, so ${n.value} returns None.`
        : `Only one side of ${n.value} found something (${tree.nodes.get(pass)!.value}), so pass that result straight up unchanged.`,
      { line: 8, phase: "bubble", watch: [w("returns", pass === null ? "None" : String(tree.nodes.get(pass)!.value), pass === null ? "muted" : "active")] },
    );
    return pass;
  };

  walk(tree.root);

  t.push(
    state(
      {
        ...Object.fromEntries(tree.layout.map((nd) => [nd.id, "muted" as Tone])),
        ...targetMarks(),
        ...(answer !== null ? { [answer]: "good" as Tone } : {}),
      },
      { notes: { ...notes } },
    ),
    answer !== null
      ? `LCA of ${p} and ${q} is ${tree.nodes.get(answer)!.value}. One postorder pass, O(n) time — no parent pointers and no second traversal required.`
      : `At least one of ${p} and ${q} is not in this tree, so there is no LCA.`,
    { phase: "answer" },
  );

  return capFrames(t.done(answer !== null ? `LCA = ${tree.nodes.get(answer)!.value}` : "no LCA"));
};

// ── path sum to a leaf (LC 112 / 113) ────────────────────────────────────

const PATH_SUM_CODE = [
  "def has_path_sum(node, target):",
  "    if node is None:",
  "        return False",
  "    target -= node.val",
  "    if node.left is None and node.right is None:",
  "        return target == 0          # leaf: exact match?",
  "    return (has_path_sum(node.left,  target) or",
  "            has_path_sum(node.right, target))",
];

export const pathSum: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [5, 4, 8, 11, null, 13, 4, 7, 2]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(PATH_SUM_CODE);
  const target = input.target ?? 22;

  const path: number[] = [];
  const notes: Record<number, string> = {};
  // Held in a box, not a plain `let`: TypeScript narrows a `let` that is only
  // assigned inside a closure down to `null` at the use site below.
  const foundPath: { path: number[] | null } = { path: null };

  const walk = (id: number | null, remaining: number): boolean => {
    if (id === null) return false;
    const n = tree.nodes.get(id)!;
    const v = Number(n.value);
    const left = remaining - v;
    path.push(id);
    notes[id] = `rem ${left}`;

    const isLeaf = n.left === null && n.right === null;
    const pathMarks: Record<number, Tone> = Object.fromEntries(path.map((pid) => [pid, "active" as Tone]));

    if (isLeaf) {
      const hit = left === 0;
      t.push(
        state({ ...pathMarks, [id]: hit ? "good" : "bad" }, {
          notes: { ...notes },
          panel: {
            label: "path",
            kind: "queue",
            items: path.map((pid) => ({ text: String(tree.nodes.get(pid)!.value), tone: hit ? "good" : "warn" })),
          },
        }),
        hit
          ? `Leaf ${v} with 0 remaining — the path ${path.map((pid) => tree.nodes.get(pid)!.value).join(" → ")} sums to exactly ${target}.`
          : `Leaf ${v} leaves ${left} remaining, not 0. Dead end — back up and try another branch. Note the leaf test matters: stopping at a node with one child would wrongly accept a half-path.`,
        {
          line: 6,
          phase: hit ? "hit" : "dead end",
          watch: [w("remaining", left, hit ? "good" : "bad"), w("path", path.map((pid) => tree.nodes.get(pid)!.value).join("→"))],
        },
      );
      if (hit) foundPath.path = [...path];
      path.pop();
      return hit;
    }

    t.push(
      state(pathMarks, {
        notes: { ...notes },
        panel: {
          label: "path",
          kind: "queue",
          items: path.map((pid) => ({ text: String(tree.nodes.get(pid)!.value), tone: "active" })),
        },
      }),
      `Subtract ${v}: ${remaining} − ${v} = ${left} still to find below ${v}. Passing the *remaining* target down beats accumulating a running sum — one variable instead of two.`,
      { line: 4, phase: "descend", watch: [w("node", v, "active"), w("remaining", left, "warn")] },
    );

    const ok = walk(n.left, left) || walk(n.right, left);
    path.pop();
    return ok;
  };

  const ok = walk(tree.root, target);

  t.push(
    state(
      {
        ...Object.fromEntries(tree.layout.map((nd) => [nd.id, "muted" as Tone])),
        ...(foundPath.path ? Object.fromEntries(foundPath.path.map((pid) => [pid, "good" as Tone])) : {}),
      },
      { notes: { ...notes } },
    ),
    ok && foundPath.path
      ? `Found a root-to-leaf path summing to ${target}: ${foundPath.path.map((pid) => tree.nodes.get(pid)!.value).join(" → ")}.`
      : `No root-to-leaf path sums to ${target}.`,
    { line: 8, phase: "answer", watch: [w("answer", ok ? "True" : "False", ok ? "good" : "bad")] },
  );

  return capFrames(t.done(ok ? `path found (sum ${target})` : `no path sums to ${target}`));
};

// ── invert (LC 226) ──────────────────────────────────────────────────────

const INVERT_CODE = [
  "def invert(node):",
  "    if node is None:",
  "        return None",
  "    node.left, node.right = node.right, node.left",
  "    invert(node.left)",
  "    invert(node.right)",
  "    return node",
];

export const invert: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [4, 2, 7, 1, 3, 6, 9]);
  if (tree.root === null) return emptyTrace();
  const t = tracer<TreeState>(INVERT_CODE);

  // Inverting changes structure, so recompute layout after each swap rather
  // than reusing a fixed one — the whole point is watching the tree flip.
  const nodes = tree.nodes;
  const relayout = (): { layout: TreeLayoutNode[]; edges: TreeEdge[]; cols: number; depth: number } => {
    let col = 0;
    const layout: TreeLayoutNode[] = [];
    const setDepth = (id: number | null, d: number) => {
      if (id === null) return;
      const n = nodes.get(id)!;
      n.depth = d;
      setDepth(n.left, d + 1);
      setDepth(n.right, d + 1);
    };
    setDepth(tree.root, 0);
    const assign = (id: number | null) => {
      if (id === null) return;
      const n = nodes.get(id)!;
      assign(n.left);
      layout.push({ id, value: n.value, x: col++, y: n.depth });
      assign(n.right);
    };
    assign(tree.root);
    const edges: TreeEdge[] = [];
    for (const n of nodes.values()) {
      if (n.left !== null) edges.push({ from: n.id, to: n.left });
      if (n.right !== null) edges.push({ from: n.id, to: n.right });
    }
    return { layout, edges, cols: col, depth: Math.max(0, ...[...nodes.values()].map((n) => n.depth)) };
  };

  const snap = (marks: Record<number, Tone>): TreeState => {
    const l = relayout();
    return { nodes: l.layout, edges: l.edges, marks, cols: l.cols, depth: l.depth };
  };

  const done = new Set<number>();

  const walk = (id: number | null) => {
    if (id === null) return;
    const n = nodes.get(id)!;
    const lv = n.left !== null ? nodes.get(n.left)!.value : "None";
    const rv = n.right !== null ? nodes.get(n.right)!.value : "None";

    t.push(
      snap(visitMarks(done, id)),
      `At ${n.value}: about to swap its children (left ${lv}, right ${rv}).`,
      { line: 4, phase: "swap", watch: [w("node", n.value, "active"), w("left", String(lv)), w("right", String(rv))] },
    );

    [n.left, n.right] = [n.right, n.left];
    done.add(id);

    t.push(
      snap(visitMarks(done, id, { [id]: "good" })),
      `Swapped — ${n.value}'s children are now (left ${rv}, right ${lv}). Then recurse into both. The order does not matter here: swap-then-recurse and recurse-then-swap both work, because each node's swap is independent.`,
      { line: 4, phase: "swap" },
    );

    walk(n.left);
    walk(n.right);
  };

  walk(tree.root);

  const finalLayout = relayout();
  t.push(
    { ...snap(Object.fromEntries(finalLayout.layout.map((n) => [n.id, "good" as Tone]))) },
    `Mirrored. Every node swapped once, so O(n) time and O(h) stack — and this is the problem that famously ended a Homebrew maintainer's Google interview.`,
    { line: 7, phase: "answer" },
  );

  return capFrames(t.done("tree mirrored"));
};

/**
 * Registry. The `algo` prop of <TreeWalker> indexes this.
 *
 * | key              | uses                |
 * |------------------|---------------------|
 * | preorder         | tree                |
 * | inorder          | tree                |
 * | postorder        | tree                |
 * | level-order      | tree                |
 * | right-side-view  | tree                |
 * | max-depth        | tree                |
 * | diameter         | tree                |
 * | validate-bst     | tree                |
 * | lca              | tree, p, q          |
 * | path-sum         | tree, target        |
 * | invert           | tree                |
 */
// ── Morris in-order traversal (O(1) space, via temporary threads) ─────────

const MORRIS_CODE = [
  "def morris_inorder(root):",
  "    out, cur = [], root",
  "    while cur:",
  "        if cur.left is None:",
  "            out.append(cur.val)       # visit",
  "            cur = cur.right           # a real edge, or a thread back up",
  "        else:",
  "            pred = cur.left",
  "            while pred.right and pred.right is not cur:",
  "                pred = pred.right     # rightmost node of the left subtree",
  "            if pred.right is None:",
  "                pred.right = cur      # thread: remember where to return",
  "                cur = cur.left",
  "            else:",
  "                pred.right = None     # undo the thread — restore the tree",
  "                out.append(cur.val)   # visit, on the SECOND arrival",
  "                cur = cur.right",
  "    return out",
];

/**
 * Morris in-order: the O(1)-space traversal. The lesson is entirely in the
 * *threads* — temporary right pointers from a subtree's rightmost node back up to
 * its ancestor, standing in for the call stack — so this trace draws them as extra
 * edges and shows each one being created and then removed again. A reader who has
 * seen the threads appear and vanish can answer "does it modify the tree?"
 * correctly: yes, transiently, and it is restored by the time the walk ends.
 */
export const morrisInorder: TreeAlgo = (input) => {
  const tree = build(input.tree ?? [4, 2, 6, 1, 3, 5, 7]);
  if (tree.root === null) return emptyTrace();
  const state = stager(tree);
  const t = tracer<TreeState>(MORRIS_CODE);

  /** Threads live here rather than mutating the tree, so frames stay snapshots. */
  const threads = new Map<number, number>();
  const rightOf = (id: number): number | null => {
    if (threads.has(id)) return threads.get(id)!;
    return tree.nodes.get(id)!.right;
  };
  const out: (number | string)[] = [];
  const visited = new Set<number>();

  const edgesWithThreads = (): TreeEdge[] => [
    ...tree.edges,
    ...[...threads.entries()].map(([from, to]) => ({
      from,
      to,
      tone: "warn" as Tone,
      label: "thread",
    })),
  ];
  const strip = () => out.map((v) => ({ text: String(v), tone: "good" as Tone }));
  const watch = (cur: number | null, extra: Watch[] = []): Watch[] => [
    w("cur", cur === null ? "None" : String(tree.nodes.get(cur)!.value), "active"),
    w("threads", threads.size, threads.size ? "warn" : "muted"),
    w("visited", out.length, "good"),
    ...extra,
  ];

  t.push(
    state(visitMarks(visited, tree.root), { edges: edgesWithThreads(), output: strip() }),
    `In-order without recursion and without a stack. The trick: before descending into a left subtree, hang a temporary **thread** from that subtree's rightmost node back up to the current node. When the walk falls off the bottom right of the subtree it lands on the thread and arrives back at the ancestor — which is exactly what popping the call stack would have done, at O(1) extra space instead of O(h).`,
    { line: 2, phase: "start", watch: watch(tree.root) },
  );

  let cur: number | null = tree.root;
  let steps = 0;

  while (cur !== null && steps < 400) {
    steps++;
    const node = tree.nodes.get(cur)!;

    if (node.left === null) {
      out.push(node.value);
      visited.add(cur);
      const next: number | null = rightOf(cur);
      const viaThread = threads.has(cur);
      t.push(
        state(visitMarks(visited, next ?? undefined, { [cur]: "good" }), {
          edges: edgesWithThreads(),
          output: strip(),
        }),
        `**${node.value}** has no left child, so it is the next value in order — visit it immediately and move right. ${
          viaThread
            ? `Its right pointer is a *thread*, so "move right" climbs back up to **${
                tree.nodes.get(next!)!.value
              }** instead of descending. This is the return from a recursive call, without a stack.`
            : next === null
              ? `Its right pointer is null and no thread hangs here, so the walk is finished.`
              : `Its right pointer is a real edge, so the walk descends to **${tree.nodes.get(next)!.value}**.`
        }`,
        { line: 6, phase: `visit ${node.value}`, watch: watch(next, [w("out", out.join(" "), "good")]) },
      );
      cur = next;
      continue;
    }

    // Find the in-order predecessor: rightmost node of the left subtree, following
    // any thread already installed there.
    let pred = node.left;
    while (true) {
      const r: number | null = rightOf(pred);
      if (r === null || r === cur) break;
      pred = r;
    }
    const predNode = tree.nodes.get(pred)!;

    if (rightOf(pred) === null) {
      threads.set(pred, cur);
      t.push(
        state(visitMarks(visited, cur, { [pred]: "warn" }), {
          edges: edgesWithThreads(),
          output: strip(),
        }),
        `**${node.value}** has a left child, so its own value comes later. Its in-order predecessor is **${predNode.value}**, the rightmost node of the left subtree, and that node's right pointer is free — so thread it to **${node.value}** and descend left. Nothing has been visited on this step: the first arrival at a node with a left child only installs the return path.`,
        {
          line: 12,
          phase: `thread ${predNode.value}→${node.value}`,
          watch: watch(node.left, [w("pred", predNode.value, "warn")]),
        },
      );
      cur = node.left;
    } else {
      threads.delete(pred);
      out.push(node.value);
      visited.add(cur);
      const next: number | null = tree.nodes.get(cur)!.right;
      t.push(
        state(visitMarks(visited, next ?? undefined, { [cur]: "good", [pred]: "muted" }), {
          edges: edgesWithThreads(),
          output: strip(),
        }),
        `Second arrival at **${node.value}** — the thread from **${predNode.value}** brought us here, which proves the whole left subtree is done. Remove the thread (**this is what restores the tree**), visit ${node.value}, and move right. Every node with a left child is reached exactly twice: once to build the thread, once to consume it. That is why the traversal is still O(n) despite the predecessor search.`,
        { line: 17, phase: `visit ${node.value}`, watch: watch(next, [w("out", out.join(" "), "good")]) },
      );
      cur = next;
    }
  }

  t.push(
    state(Object.fromEntries([...visited].map((id) => [id, "good" as Tone])), {
      edges: edgesWithThreads(),
      output: strip(),
    }),
    `In-order result: ${out.join(", ")}. Threads remaining: ${
      threads.size
    } — the tree is exactly as it started, because every thread that was created was also removed on the second arrival. O(n) time, **O(1) extra space**: the only variables are cur and pred. The price is that the tree is temporarily mutated, which makes this unsafe under concurrent readers and the honest answer to "why is this not the default".`,
    { line: 19, phase: "answer", watch: watch(null, [w("space", "O(1)", "good")]) },
  );

  return capFrames(t.done(`inorder = [${out.join(", ")}]`));
};

export const TREE_ALGOS: Record<string, TreeAlgo> = {
  preorder,
  inorder,
  postorder,
  "morris-inorder": morrisInorder,
  "level-order": levelOrder,
  "right-side-view": rightSideView,
  "max-depth": maxDepth,
  diameter,
  "validate-bst": validateBst,
  lca,
  "path-sum": pathSum,
  invert,
};

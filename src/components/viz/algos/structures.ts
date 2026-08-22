/**
 * algos/structures.ts — tries, union-find and segment trees.
 *
 * These three share a file because they share a property: each is already the
 * shape of an existing renderer, so none of them needs a new stage.
 *
 *   * a **trie** is a tree whose edges carry characters   → TreeState
 *   * a **union-find forest** is a directed graph of parent pointers → GraphState
 *   * a **segment tree** is a tree whose nodes carry ranges → TreeState
 *
 * Recognising that saved three renderers. The components in this family are thin
 * wrappers over `TreeStage` and `GraphStage`.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { TreeEdge, TreeLayoutNode, TreeState } from "./trees";
import type { GraphEdgeView, GraphLayoutNode, GraphState } from "./graphs";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ═══════════════════════════════════════════════════════════════════════════
// TRIE
// ═══════════════════════════════════════════════════════════════════════════

export interface TrieInput {
  /** Words to insert. */
  words?: string[];
  /** Word or prefix to search for after insertion. */
  query?: string;
}

export type TrieAlgo = (input: TrieInput) => Trace<TreeState>;

interface TrieNode {
  id: number;
  /** Character on the edge from this node's parent. Root has none. */
  ch: string;
  parent: number | null;
  children: Map<string, number>;
  end: boolean;
  depth: number;
}

const TRIE_CODE = [
  "class TrieNode:",
  "    def __init__(self):",
  "        self.children = {}      # char -> TrieNode",
  "        self.is_word = False    # NOT the same as 'has no children'",
  "",
  "def insert(root, word):",
  "    node = root",
  "    for ch in word:",
  "        if ch not in node.children:",
  "            node.children[ch] = TrieNode()",
  "        node = node.children[ch]",
  "    node.is_word = True         # mark the END, not the node",
  "",
  "def search(root, word):",
  "    node = root",
  "    for ch in word:",
  "        if ch not in node.children: return False",
  "        node = node.children[ch]",
  "    return node.is_word         # prefix != word",
];

export const trieInsertSearch: TrieAlgo = (input) => {
  const words = (input.words ?? ["cat", "car", "card", "dog"]).slice(0, 6);
  const query = input.query ?? "car";
  const t = tracer<TreeState>(TRIE_CODE);

  const nodes: TrieNode[] = [
    { id: 0, ch: "•", parent: null, children: new Map(), end: false, depth: 0 },
  ];

  /** Re-derive layout each frame — the tree grows as words are inserted. */
  const layoutOf = (): { nodes: TreeLayoutNode[]; edges: TreeEdge[]; cols: number; depth: number } => {
    let slot = 0;
    const x = new Map<number, number>();
    const place = (id: number): number => {
      const node = nodes[id];
      const kids = [...node.children.entries()].sort((a, b) => a[0].localeCompare(b[0]));
      if (kids.length === 0) {
        const own = slot++;
        x.set(id, own);
        return own;
      }
      const xs = kids.map(([, cid]) => place(cid));
      const centre = (xs[0] + xs[xs.length - 1]) / 2;
      x.set(id, centre);
      return centre;
    };
    place(0);

    const layout: TreeLayoutNode[] = nodes.map((n) => ({
      id: n.id,
      // A trie node's identity is its edge character; the end-of-word marker is
      // shown as a ring rather than a different letter.
      value: n.parent === null ? "•" : n.ch,
      x: x.get(n.id) ?? 0,
      y: n.depth,
    }));

    const edges: TreeEdge[] = [];
    for (const n of nodes) {
      for (const [ch, cid] of n.children) edges.push({ from: n.id, to: cid, label: ch });
    }

    return { nodes: layout, edges, cols: Math.max(1, slot), depth: Math.max(0, ...nodes.map((n) => n.depth)) };
  };

  const state = (marks: Record<number, Tone> = {}, notes: Record<number, string> = {}): TreeState => {
    const l = layoutOf();
    const endNotes: Record<number, string> = {};
    for (const n of nodes) if (n.end) endNotes[n.id] = "word";
    return { ...l, marks, notes: { ...endNotes, ...notes } };
  };

  t.push(
    state({ 0: "active" }),
    `A trie stores characters on **edges**, not in nodes, and shares every common prefix. That sharing is the whole point: "car" and "card" occupy one path, so prefix lookup costs O(length) regardless of how many words are stored.`,
    { line: 3, phase: "setup" },
  );

  for (const word of words) {
    let cur = 0;
    for (const ch of word) {
      const existing = nodes[cur].children.get(ch);
      if (existing !== undefined) {
        cur = existing;
        t.push(
          state({ [cur]: "good" }),
          `'${ch}' already exists on this path — reuse it. This is the prefix sharing that makes a trie compact: inserting "${word}" costs nothing for the part it has in common with an earlier word.`,
          { line: 11, phase: `insert "${word}"`, watch: [w("char", ch, "good"), w("reused", "yes", "good")] },
        );
      } else {
        const id = nodes.length;
        nodes.push({
          id,
          ch,
          parent: cur,
          children: new Map(),
          end: false,
          depth: nodes[cur].depth + 1,
        });
        nodes[cur].children.set(ch, id);
        cur = id;
        t.push(
          state({ [cur]: "warn" }),
          `'${ch}' is new here — create a node for it.`,
          { line: 10, phase: `insert "${word}"`, watch: [w("char", ch, "warn"), w("nodes", nodes.length)] },
        );
      }
    }
    nodes[cur].end = true;
    t.push(
      state({ [cur]: "good" }),
      `Mark the final node as end-of-word. This flag is essential and separate from "has no children": "car" ends inside the path to "card", so without the flag a trie cannot distinguish a stored word from a mere prefix.`,
      { line: 12, phase: `insert "${word}"`, watch: [w("word", word, "good")] },
    );
  }

  // Search.
  let cur = 0;
  let failed = false;
  for (const ch of query) {
    const nxt = nodes[cur].children.get(ch);
    if (nxt === undefined) {
      failed = true;
      t.push(
        state({ [cur]: "bad" }),
        `Searching "${query}": no edge '${ch}' from here, so neither "${query}" nor anything starting with it is stored. Return False immediately — O(length), and crucially independent of how many words the trie holds.`,
        { line: 17, phase: "search", watch: [w("char", ch, "bad")] },
      );
      break;
    }
    cur = nxt;
    t.push(
      state({ [cur]: "active" }),
      `Follow '${ch}'.`,
      { line: 18, phase: "search", watch: [w("char", ch, "active"), w("depth", nodes[cur].depth)] },
    );
  }

  const found = !failed && nodes[cur].end;
  t.push(
    state({ [cur]: found ? "good" : "bad" }),
    failed
      ? `"${query}" is not in the trie.`
      : found
        ? `Reached the end of "${query}" and the end-of-word flag is set — it is a stored word.`
        : `Reached the end of "${query}" but the end-of-word flag is **not** set. "${query}" is a prefix of something stored, but was never inserted as a word itself. That distinction is what the flag exists for, and conflating the two is the standard trie bug.`,
    { line: 19, phase: "answer", watch: [w("result", found ? "True" : "False", found ? "good" : "bad")] },
  );

  return capFrames(t.done(found ? `"${query}" found` : `"${query}" not stored as a word`));
};

export const TRIE_ALGOS: Record<string, TrieAlgo> = {
  "insert-search": trieInsertSearch,
};

// ═══════════════════════════════════════════════════════════════════════════
// UNION-FIND
// ═══════════════════════════════════════════════════════════════════════════

export interface DsuInput {
  /** Number of elements, labelled 0..n-1. */
  n?: number;
  /** Union operations to perform, in order. */
  unions?: [number, number][];
}

export type DsuAlgo = (input: DsuInput) => Trace<GraphState>;

const DSU_CODE = [
  "class DSU:",
  "    def __init__(self, n):",
  "        self.parent = list(range(n))   # everyone is their own root",
  "        self.size = [1] * n",
  "",
  "    def find(self, x):",
  "        while self.parent[x] != x:",
  "            self.parent[x] = self.parent[self.parent[x]]   # PATH COMPRESSION",
  "            x = self.parent[x]",
  "        return x",
  "",
  "    def union(self, a, b):",
  "        ra, rb = self.find(a), self.find(b)",
  "        if ra == rb: return False      # already together — a cycle edge",
  "        if self.size[ra] < self.size[rb]: ra, rb = rb, ra",
  "        self.parent[rb] = ra           # UNION BY SIZE: small under large",
  "        self.size[ra] += self.size[rb]",
  "        return True",
];

export const unionFind: DsuAlgo = (input) => {
  const n = Math.max(2, Math.min(input.n ?? 8, 10));
  const unions = input.unions ?? [
    [0, 1],
    [2, 3],
    [1, 2],
    [4, 5],
    [6, 7],
    [5, 6],
    [0, 3],
  ];
  const t = tracer<GraphState>(DSU_CODE);

  const parent = Array.from({ length: n }, (_, i) => i);
  const size = Array.from({ length: n }, () => 1);

  const find = (x: number): number => {
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };

  /** Forest layout: roots on the top row, everything else below its root. */
  const layoutOf = (): { nodes: GraphLayoutNode[]; edges: GraphEdgeView[]; cols: number; rows: number } => {
    const depthOf = (x: number): number => (parent[x] === x ? 0 : depthOf(parent[x]) + 1);
    const byDepth = new Map<number, number[]>();
    for (let i = 0; i < n; i++) {
      const d = depthOf(i);
      byDepth.set(d, [...(byDepth.get(d) ?? []), i]);
    }
    const widest = Math.max(1, ...[...byDepth.values()].map((l) => l.length));
    const layout: GraphLayoutNode[] = [];
    for (const [d, level] of [...byDepth.entries()].sort((a, b) => a[0] - b[0])) {
      const offset = (widest - level.length) / 2;
      level.forEach((id, i) => layout.push({ id: String(id), x: offset + i, y: d }));
    }
    const edges: GraphEdgeView[] = [];
    for (let i = 0; i < n; i++) {
      if (parent[i] !== i) edges.push({ from: String(i), to: String(parent[i]), directed: true, tone: "good" });
    }
    return { nodes: layout, edges, cols: widest, rows: byDepth.size };
  };

  const state = (marks: Record<string, Tone> = {}): GraphState => {
    const l = layoutOf();
    const notes: Record<string, string> = {};
    for (let i = 0; i < n; i++) if (parent[i] === i) notes[String(i)] = `root ·${size[i]}`;
    return { ...l, marks, notes };
  };

  t.push(
    state(),
    `Every element starts as its own root — ${n} separate sets. Union-find answers only two questions ("are these connected?" and "connect these"), and it answers them in effectively constant time, which is why it beats a graph traversal for dynamic connectivity.`,
    { line: 3, phase: "setup", watch: [w("sets", n, "info")] },
  );

  let sets = n;
  for (const [a, b] of unions) {
    const ra = find(a);
    const rb = find(b);

    if (ra === rb) {
      t.push(
        state({ [String(a)]: "bad", [String(b)]: "bad", [String(ra)]: "warn" }),
        `union(${a}, ${b}): both already have root ${ra}, so they are in the same set. Nothing to do — and note this is exactly how union-find detects a cycle: an edge whose endpoints already share a root closes one. That is Kruskal's rejection test.`,
        { line: 13, phase: "already joined", watch: [w("root", ra, "warn"), w("sets", sets)] },
      );
      continue;
    }

    const [big, small] = size[ra] >= size[rb] ? [ra, rb] : [rb, ra];
    t.push(
      state({ [String(big)]: "good", [String(small)]: "warn" }),
      `union(${a}, ${b}): roots ${ra} (size ${size[ra]}) and ${rb} (size ${size[rb]}). Attach the **smaller** tree under the larger — union by size. Doing it the other way round lets the tree grow to depth n, and the whole complexity guarantee collapses.`,
      {
        line: 16,
        phase: "union",
        watch: [w("larger root", big, "good"), w("smaller root", small, "warn")],
      },
    );

    parent[small] = big;
    size[big] += size[small];
    sets -= 1;

    t.push(
      state({ [String(big)]: "good" }),
      `${small} now points at ${big}, whose set has ${size[big]} elements. ${sets} set${sets === 1 ? "" : "s"} remain.`,
      { line: 17, phase: "union", watch: [w("sets", sets, "good"), w("size", size[big])] },
    );
  }

  t.push(
    state(),
    `${sets} set${sets === 1 ? "" : "s"} remain. With both union-by-size and path compression, each operation is O(α(n)) amortised — the inverse Ackermann function, which is below 5 for any input that fits in the universe. Say "effectively constant" in an interview, and mention that either optimisation alone is weaker than both together.`,
    { line: 18, phase: "answer", watch: [w("final sets", sets, "good")] },
  );

  return capFrames(t.done(`${sets} disjoint set${sets === 1 ? "" : "s"}`));
};

export const DSU_ALGOS: Record<string, DsuAlgo> = {
  "union-find": unionFind,
};

// ═══════════════════════════════════════════════════════════════════════════
// SEGMENT TREE
// ═══════════════════════════════════════════════════════════════════════════

export interface SegTreeInput {
  values?: number[];
  /** Range to query, as [lo, hi] inclusive. */
  range?: [number, number];
}

export type SegTreeAlgo = (input: SegTreeInput) => Trace<TreeState>;

const SEGTREE_CODE = [
  "def build(a, node, lo, hi):",
  "    if lo == hi:",
  "        tree[node] = a[lo]                 # a leaf IS one element",
  "        return",
  "    mid = (lo + hi) // 2",
  "    build(a, 2*node,     lo,      mid)",
  "    build(a, 2*node + 1, mid + 1, hi)",
  "    tree[node] = tree[2*node] + tree[2*node + 1]",
  "",
  "def query(node, lo, hi, l, r):",
  "    if r < lo or hi < l:  return 0          # no overlap",
  "    if l <= lo and hi <= r: return tree[node]   # FULLY inside — stop here",
  "    mid = (lo + hi) // 2",
  "    return query(2*node, lo, mid, l, r) + query(2*node+1, mid+1, hi, l, r)",
];

export const segmentTree: SegTreeAlgo = (input) => {
  const a = (input.values?.length ? input.values : [2, 5, 1, 4, 9, 3]).slice(0, 8);
  const [ql, qr] = input.range ?? [1, 4];
  const t = tracer<TreeState>(SEGTREE_CODE);

  interface Seg {
    id: number;
    lo: number;
    hi: number;
    sum: number;
    parent: number | null;
    kids: number[];
    depth: number;
  }
  const segs: Seg[] = [];

  const build = (lo: number, hi: number, parent: number | null, depth: number): number => {
    const id = segs.length;
    segs.push({ id, lo, hi, sum: 0, parent, kids: [], depth });
    if (parent !== null) segs[parent].kids.push(id);
    if (lo === hi) {
      segs[id].sum = a[lo];
      return id;
    }
    const mid = Math.floor((lo + hi) / 2);
    build(lo, mid, id, depth + 1);
    build(mid + 1, hi, id, depth + 1);
    segs[id].sum = segs[id].kids.reduce((s, k) => s + segs[k].sum, 0);
    return id;
  };
  build(0, a.length - 1, null, 0);

  const layoutOf = () => {
    let slot = 0;
    const x = new Map<number, number>();
    const place = (id: number): number => {
      const s = segs[id];
      if (s.kids.length === 0) {
        const own = slot++;
        x.set(id, own);
        return own;
      }
      const xs = s.kids.map(place);
      const centre = (xs[0] + xs[xs.length - 1]) / 2;
      x.set(id, centre);
      return centre;
    };
    place(0);
    const layout: TreeLayoutNode[] = segs.map((s) => ({
      id: s.id,
      value: s.sum,
      x: x.get(s.id) ?? 0,
      y: s.depth,
    }));
    const edges: TreeEdge[] = [];
    for (const s of segs) for (const k of s.kids) edges.push({ from: s.id, to: k });
    return { nodes: layout, edges, cols: Math.max(1, slot), depth: Math.max(...segs.map((s) => s.depth)) };
  };

  const LAYOUT = layoutOf();
  const rangeNotes = Object.fromEntries(segs.map((s) => [s.id, `[${s.lo},${s.hi}]`]));

  const state = (marks: Record<number, Tone> = {}): TreeState => ({
    ...LAYOUT,
    marks,
    notes: rangeNotes,
  });

  t.push(
    state({ 0: "active" }),
    `Each node stores the sum of one range, shown beneath it. The root covers everything; leaves cover single elements. Building costs O(n) and every node's value is the sum of its two children — so an update touches only one root-to-leaf path.`,
    { line: 8, phase: "built", watch: [w("total", segs[0].sum, "good")] },
  );

  // Query.
  const visited: Record<number, Tone> = {};
  let total = 0;
  let fullyInside = 0;
  let pruned = 0;

  const query = (id: number) => {
    const s = segs[id];

    if (s.hi < ql || qr < s.lo) {
      visited[id] = "muted";
      pruned += 1;
      t.push(
        state({ ...visited, [id]: "bad" }),
        `Node [${s.lo},${s.hi}] does not overlap the query [${ql},${qr}] at all — return 0 and do not descend. Every node below it is pruned in one test.`,
        { line: 11, phase: "no overlap", watch: [w("node", `[${s.lo},${s.hi}]`, "bad"), w("pruned", pruned)] },
      );
      return;
    }

    if (ql <= s.lo && s.hi <= qr) {
      visited[id] = "good";
      total += s.sum;
      fullyInside += 1;
      t.push(
        state({ ...visited, [id]: "good" }),
        `Node [${s.lo},${s.hi}] lies **entirely** inside [${ql},${qr}], so its precomputed sum ${s.sum} can be used whole — no need to look at its children. Stopping here is where the log factor comes from; a query decomposes into at most 2·log n such nodes.`,
        {
          line: 12,
          phase: "full cover",
          watch: [w("node", `[${s.lo},${s.hi}]`, "good"), w("+", s.sum, "good"), w("total", total, "active")],
        },
      );
      return;
    }

    visited[id] = "warn";
    t.push(
      state({ ...visited, [id]: "warn" }),
      `Node [${s.lo},${s.hi}] partially overlaps [${ql},${qr}], so it must be split — recurse into both children and add what they report.`,
      { line: 14, phase: "split", watch: [w("node", `[${s.lo},${s.hi}]`, "warn")] },
    );
    for (const k of s.kids) query(k);
  };

  query(0);

  const expected = a.slice(ql, qr + 1).reduce((x, y) => x + y, 0);
  t.push(
    state(visited),
    `Sum over [${ql},${qr}] is ${total} (check: ${a.slice(ql, qr + 1).join(" + ")} = ${expected}). It was assembled from ${fullyInside} fully-covered node${fullyInside === 1 ? "" : "s"} with ${pruned} branch${pruned === 1 ? "" : "es"} pruned — O(log n) work, not O(n). A prefix-sum array also answers this in O(1), but cannot survive updates; that trade-off is why segment trees exist.`,
    { line: 14, phase: "answer", watch: [w("sum", total, "good"), w("nodes used", fullyInside, "good")] },
  );

  return capFrames(t.done(`sum[${ql}..${qr}] = ${total}`));
};

export const SEGTREE_ALGOS: Record<string, SegTreeAlgo> = {
  "range-sum": segmentTree,
};

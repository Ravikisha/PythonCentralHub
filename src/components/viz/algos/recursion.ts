/**
 * algos/recursion.ts — traced call trees for <RecursionTree>.
 *
 * Phase 11 (Recursion and Backtracking) had no visualizations at all, which is
 * the worst place to have none: the code is six lines, and every one of the
 * hard parts is invisible in it. Where does the work actually happen? What is on
 * the stack when the answer is recorded? Why does removing the `pop()` break
 * everything? Why does one `@cache` decorator turn exponential into linear?
 *
 * A call tree answers all four at once, so that is what these emit.
 *
 * TWO PASSES
 * ----------
 * Pass 1 runs the algorithm and records the *complete* call tree. Pass 2 lays it
 * out once and replays it, emitting one frame per event. Doing it this way means
 * node positions never move between frames — a tree that reflows while you scrub
 * is unreadable, and the growth animation is not worth that cost.
 *
 * Output reuses TreeState, so <RecursionTree> renders through TreeWalker's stage.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { TreeEdge, TreeLayoutNode, TreePanel, TreeState } from "./trees";

export interface RecursionInput {
  /** Numeric argument: `n` for fib, the set for subsets/permutations. */
  values?: number[];
  /** Single integer argument, e.g. fib(n) or "climb n stairs". */
  n?: number;
  /** Target for combination-sum. */
  target?: number;
}

export type RecursionAlgo = (input: RecursionInput) => Trace<TreeState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ── call-tree scaffolding ─────────────────────────────────────────────────

interface CallNode {
  id: number;
  /** Shown inside the circle. Keep it to a few characters. */
  label: string;
  /** Shown under the circle — the return value, or a memo-hit marker. */
  note?: string;
  parent: number | null;
  children: number[];
  depth: number;
}

/** Records a call tree during pass 1 and lays it out for pass 2. */
class CallTree {
  nodes: CallNode[] = [];

  open(label: string, parent: number | null): number {
    const id = this.nodes.length;
    const depth = parent === null ? 0 : this.nodes[parent].depth + 1;
    this.nodes.push({ id, label, parent, children: [], depth });
    if (parent !== null) this.nodes[parent].children.push(id);
    return id;
  }

  note(id: number, text: string) {
    this.nodes[id].note = text;
  }

  /**
   * Left-to-right slot per leaf, parents centred over their children. This is
   * the layout that makes a call tree readable: siblings never overlap, and a
   * parent visibly sits above the work it spawned.
   */
  layout(): { layout: TreeLayoutNode[]; edges: TreeEdge[]; cols: number; depth: number } {
    let slot = 0;
    const x = new Map<number, number>();

    const place = (id: number): number => {
      const node = this.nodes[id];
      if (node.children.length === 0) {
        const own = slot++;
        x.set(id, own);
        return own;
      }
      const kids = node.children.map(place);
      const centre = (kids[0] + kids[kids.length - 1]) / 2;
      x.set(id, centre);
      return centre;
    };
    if (this.nodes.length > 0) place(0);

    const layout: TreeLayoutNode[] = this.nodes.map((n) => ({
      id: n.id,
      value: n.label,
      x: x.get(n.id) ?? 0,
      y: n.depth,
    }));

    const edges: TreeEdge[] = [];
    for (const n of this.nodes) {
      for (const c of n.children) edges.push({ from: n.id, to: c });
    }

    return {
      layout,
      edges,
      cols: Math.max(1, slot),
      depth: Math.max(0, ...this.nodes.map((n) => n.depth)),
    };
  }
}

/** One replayable event from pass 1. */
type Event =
  | { kind: "enter"; id: number; caption: string; line?: number; watch?: Watch[] }
  | { kind: "leave"; id: number; caption: string; line?: number; watch?: Watch[]; note?: string }
  | { kind: "record"; id: number; caption: string; line?: number; item: string; watch?: Watch[] }
  | { kind: "prune"; id: number; caption: string; line?: number; watch?: Watch[] };

/**
 * Replay recorded events into frames. Shared by every algorithm below, which is
 * what keeps each one down to its actual logic.
 */
function replay(tree: CallTree, events: Event[], code: string[], result: string): Trace<TreeState> {
  const { layout, edges, cols, depth } = tree.layout();
  const t = tracer<TreeState>(code);

  const done = new Set<number>();
  const pruned = new Set<number>();
  const stack: number[] = [];
  const output: { text: string; tone?: Tone }[] = [];
  const notes: Record<number, string> = {};

  const panel = (): TreePanel => ({
    label: "call stack",
    kind: "stack",
    items: stack.map((id, i) => ({
      text: tree.nodes[id].label,
      tone: i === stack.length - 1 ? "active" : "info",
    })),
  });

  const marks = (current?: number): Record<number, Tone> => {
    const m: Record<number, Tone> = {};
    // Nodes not yet reached read as untouched, so the frontier is obvious.
    for (const n of tree.nodes) m[n.id] = "muted";
    for (const id of done) m[id] = "good";
    for (const id of pruned) m[id] = "bad";
    for (const id of stack) m[id] = "info";
    if (current !== undefined) m[current] = "active";
    return m;
  };

  const frame = (current: number, extra: Partial<TreeState> = {}): TreeState => ({
    nodes: layout,
    edges,
    marks: marks(current),
    notes: { ...notes },
    panel: panel(),
    output: [...output],
    cols,
    depth,
    ...extra,
  });

  for (const e of events) {
    if (e.kind === "enter") {
      stack.push(e.id);
      t.push(frame(e.id), e.caption, { line: e.line, phase: "call", watch: e.watch });
    } else if (e.kind === "record") {
      output.push({ text: e.item, tone: "good" });
      t.push(frame(e.id), e.caption, { line: e.line, phase: "record", watch: e.watch });
    } else if (e.kind === "prune") {
      pruned.add(e.id);
      t.push(frame(e.id), e.caption, { line: e.line, phase: "prune", watch: e.watch });
      stack.pop();
    } else {
      if (e.note) notes[e.id] = e.note;
      done.add(e.id);
      stack.pop();
      t.push(frame(stack[stack.length - 1] ?? e.id), e.caption, {
        line: e.line,
        phase: "return",
        watch: e.watch,
      });
    }
  }

  t.push(
    {
      nodes: layout,
      edges,
      marks: Object.fromEntries(
        tree.nodes.map((n) => [n.id, (pruned.has(n.id) ? "bad" : "good") as Tone]),
      ),
      notes: { ...notes },
      output: [...output],
      cols,
      depth,
    },
    result,
    { phase: "answer" },
  );

  return capFrames(t.done(result.split(".")[0]));
}

// ── 1. Naive Fibonacci — why memoisation matters ──────────────────────────

const FIB_CODE = [
  "def fib(n):",
  "    if n <= 1:",
  "        return n",
  "    return fib(n - 1) + fib(n - 2)",
];

export const fibNaive: RecursionAlgo = (input) => {
  const n = Math.max(0, Math.min(input.n ?? 6, 8));
  const tree = new CallTree();
  const events: Event[] = [];
  let calls = 0;

  const go = (k: number, parent: number | null): number => {
    const id = tree.open(`f${k}`, parent);
    calls += 1;
    events.push({
      kind: "enter",
      id,
      caption:
        k <= 1
          ? `fib(${k}) hits the base case and returns ${k} immediately.`
          : `fib(${k}) needs fib(${k - 1}) and fib(${k - 2}). Neither is known, so both are computed from scratch — including everything they in turn need.`,
      line: k <= 1 ? 2 : 4,
      watch: [w("n", k, "active"), w("calls so far", calls, "warn")],
    });

    if (k <= 1) {
      events.push({
        kind: "leave",
        id,
        caption: `Return ${k}.`,
        line: 3,
        note: `= ${k}`,
        watch: [w("returns", k, "good")],
      });
      return k;
    }

    const a = go(k - 1, id);
    const b = go(k - 2, id);
    const v = a + b;
    tree.note(id, `= ${v}`);
    events.push({
      kind: "leave",
      id,
      caption: `Both children have returned: ${a} + ${b} = ${v}.`,
      line: 4,
      note: `= ${v}`,
      watch: [w("returns", v, "good"), w("calls so far", calls, "warn")],
    });
    return v;
  };

  const answer = go(n, null);

  return replay(
    tree,
    events,
    FIB_CODE,
    `fib(${n}) = ${answer}, computed with ${calls} calls. Look at how many identical subtrees appear — fib(2) alone is recomputed several times. That duplication is why the naive version is O(φⁿ), and why one @cache decorator collapses it to O(n).`,
  );
};

// ── 2. Memoised Fibonacci — the same tree, pruned ─────────────────────────

const FIB_MEMO_CODE = [
  "from functools import cache",
  "",
  "@cache                      # the entire fix",
  "def fib(n):",
  "    if n <= 1:",
  "        return n",
  "    return fib(n - 1) + fib(n - 2)",
];

export const fibMemo: RecursionAlgo = (input) => {
  const n = Math.max(0, Math.min(input.n ?? 6, 12));
  const tree = new CallTree();
  const events: Event[] = [];
  const memo = new Map<number, number>();
  let calls = 0;
  let hits = 0;

  const go = (k: number, parent: number | null): number => {
    const id = tree.open(`f${k}`, parent);
    calls += 1;

    if (memo.has(k)) {
      hits += 1;
      const v = memo.get(k)!;
      tree.note(id, `hit ${v}`);
      events.push({
        kind: "enter",
        id,
        caption: `fib(${k}) is already in the cache. Return ${v} without recursing at all — this is the entire subtree that the naive version would have rebuilt.`,
        line: 3,
        watch: [w("n", k, "good"), w("cache hits", hits, "good"), w("calls", calls)],
      });
      events.push({ kind: "leave", id, caption: `Cached ${v} returned.`, line: 3, note: `hit ${v}` });
      return v;
    }

    events.push({
      kind: "enter",
      id,
      caption:
        k <= 1
          ? `fib(${k}) is a base case.`
          : `fib(${k}) is not cached yet, so it recurses — but only this once. Every later request for fib(${k}) will be a hit.`,
      line: k <= 1 ? 5 : 7,
      watch: [w("n", k, "active"), w("cached", memo.size, "info"), w("calls", calls)],
    });

    let v: number;
    if (k <= 1) v = k;
    else v = go(k - 1, id) + go(k - 2, id);

    memo.set(k, v);
    tree.note(id, `= ${v}`);
    events.push({
      kind: "leave",
      id,
      caption: `fib(${k}) = ${v}, now cached. Cache size ${memo.size}.`,
      line: 7,
      note: `= ${v}`,
      watch: [w("returns", v, "good"), w("cached", memo.size, "info")],
    });
    return v;
  };

  const answer = go(n, null);

  return replay(
    tree,
    events,
    FIB_MEMO_CODE,
    `fib(${n}) = ${answer} in ${calls} calls, ${hits} of them cache hits. Compare the shape with the naive tree: every red-free subtree that would have been rebuilt is now a single node. This is the whole of "top-down DP" — the recursion is unchanged, only the repetition is gone.`,
  );
};

// ── 3. Subsets — the include/exclude tree (LC 78) ──────────────────────────

const SUBSETS_CODE = [
  "def subsets(nums):",
  "    out, path = [], []",
  "    def go(i):",
  "        if i == len(nums):",
  "            out.append(path[:])      # copy! path keeps mutating",
  "            return",
  "        path.append(nums[i])         # branch 1: include",
  "        go(i + 1)",
  "        path.pop()                   # UNDO — this is the backtrack",
  "        go(i + 1)                    # branch 2: exclude",
  "    go(0)",
  "    return out",
];

export const subsets: RecursionAlgo = (input) => {
  const nums = (input.values ?? [1, 2, 3]).slice(0, 4);
  const tree = new CallTree();
  const events: Event[] = [];
  const path: number[] = [];
  const out: number[][] = [];

  const label = () => (path.length ? `[${path.join(",")}]` : "[]");

  const go = (i: number, parent: number | null, taken: boolean | null) => {
    const id = tree.open(label(), parent);
    events.push({
      kind: "enter",
      id,
      caption:
        taken === null
          ? `Start with an empty path and index 0. Every node in this tree is a decision about one element: include it or do not.`
          : taken
            ? `Included ${nums[i - 1]}. The path is now ${label()}.`
            : `Excluded ${nums[i - 1]}. The path is back to ${label()}.`,
      line: taken === null ? 11 : taken ? 8 : 10,
      watch: [w("i", i), w("path", label(), "active")],
    });

    if (i === nums.length) {
      out.push([...path]);
      tree.note(id, "✓");
      events.push({
        kind: "record",
        id,
        caption: `Every element has been decided, so ${label()} is a complete subset — record it. Note the copy: path is a single list that keeps mutating, so appending it without the [:] slice would store ${out.length} references to the same eventually-empty list.`,
        line: 5,
        item: label(),
        watch: [w("found", out.length, "good"), w("subset", label(), "good")],
      });
      events.push({ kind: "leave", id, caption: `Return to the previous decision.`, line: 6 });
      return;
    }

    path.push(nums[i]);
    go(i + 1, id, true);
    path.pop();

    events.push({
      kind: "leave",
      id,
      caption: `The include-branch under ${label()} is exhausted. ${
        i < nums.length ? `Undo the append — pop ${nums[i]} — and try excluding it instead. Forgetting this pop is the single most common backtracking bug: the path grows forever and the output is garbage.` : ""
      }`,
      line: 9,
      note: undefined,
      watch: [w("path", label(), "warn")],
    });

    go(i + 1, id, false);
  };

  go(0, null, null);

  return replay(
    tree,
    events,
    SUBSETS_CODE,
    `${out.length} subsets from ${nums.length} elements — exactly 2^${nums.length}, because the tree is a perfect binary tree of decisions and every leaf is one subset. That doubling is why subset problems are only tractable for small n, and why the constraint "n ≤ 20" in a problem statement is a hint that exponential is intended.`,
  );
};

// ── 4. Permutations — swap-based (LC 46) ─────────────────────────────────

const PERM_CODE = [
  "def permutations(nums):",
  "    out = []",
  "    def go(start):",
  "        if start == len(nums):",
  "            out.append(nums[:])",
  "            return",
  "        for i in range(start, len(nums)):",
  "            nums[start], nums[i] = nums[i], nums[start]",
  "            go(start + 1)",
  "            nums[start], nums[i] = nums[i], nums[start]   # swap back",
  "    go(0)",
  "    return out",
];

export const permutations: RecursionAlgo = (input) => {
  const nums = (input.values ?? [1, 2, 3]).slice(0, 3);
  const tree = new CallTree();
  const events: Event[] = [];
  const out: number[][] = [];

  const go = (start: number, parent: number | null, note: string) => {
    const id = tree.open(nums.join(""), parent);
    events.push({
      kind: "enter",
      id,
      caption: note,
      line: start === 0 ? 11 : 9,
      watch: [w("start", start), w("array", nums.join(","), "active")],
    });

    if (start === nums.length) {
      out.push([...nums]);
      tree.note(id, "✓");
      events.push({
        kind: "record",
        id,
        caption: `All positions are fixed, so [${nums.join(", ")}] is a complete permutation.`,
        line: 5,
        item: `[${nums.join(",")}]`,
        watch: [w("found", out.length, "good")],
      });
      events.push({ kind: "leave", id, caption: "Return.", line: 6 });
      return;
    }

    for (let i = start; i < nums.length; i++) {
      [nums[start], nums[i]] = [nums[i], nums[start]];
      go(
        start + 1,
        id,
        i === start
          ? `Leave ${nums[start]} in position ${start} (swapping with itself) and permute the rest.`
          : `Swap ${nums[start]} into position ${start} and permute the remaining ${nums.length - start - 1} element${nums.length - start - 1 === 1 ? "" : "s"}.`,
      );
      [nums[start], nums[i]] = [nums[i], nums[start]];
    }

    events.push({
      kind: "leave",
      id,
      caption: `Every choice for position ${start} has been tried, and the array has been restored to ${nums.join(", ")} by swapping back. That restore is what lets one shared array serve the whole tree — no copying per branch.`,
      line: 10,
      watch: [w("restored", nums.join(","), "good")],
    });
  };

  go(0, null, `Fix position 0 first: each of the ${nums.length} elements gets a turn there, and each choice spawns a subtree over the remaining positions.`);

  return replay(
    tree,
    events,
    PERM_CODE,
    `${out.length} permutations of ${nums.length} elements — that is ${nums.length}!, and the branching factor visibly shrinks by one at each level, which is where the factorial comes from. The swap-and-swap-back version uses O(n) space; building a fresh list per branch would cost O(n·n!).`,
  );
};

// ── 5. Combination sum — where pruning earns its keep (LC 39) ─────────────

const COMBO_CODE = [
  "def combination_sum(candidates, target):",
  "    out, path = [], []",
  "    def go(i, remaining):",
  "        if remaining == 0:",
  "            out.append(path[:]); return",
  "        if remaining < 0 or i == len(candidates):",
  "            return                       # dead branch — prune",
  "        path.append(candidates[i])",
  "        go(i, remaining - candidates[i])  # reuse i: repeats allowed",
  "        path.pop()",
  "        go(i + 1, remaining)             # move past candidates[i]",
  "    go(0, target)",
  "    return out",
];

export const combinationSum: RecursionAlgo = (input) => {
  const candidates = (input.values ?? [2, 3, 5]).slice(0, 3);
  const target = input.target ?? 7;
  const tree = new CallTree();
  const events: Event[] = [];
  const path: number[] = [];
  const out: number[][] = [];

  const go = (i: number, remaining: number, parent: number | null, why: string) => {
    const id = tree.open(String(remaining), parent);

    if (remaining === 0) {
      out.push([...path]);
      tree.note(id, "✓");
      events.push({
        kind: "enter",
        id,
        caption: `${why} Remaining is exactly 0, so [${path.join(" + ")}] sums to ${target}.`,
        line: 4,
        watch: [w("remaining", 0, "good"), w("path", path.join("+"), "good")],
      });
      events.push({
        kind: "record",
        id,
        caption: `Record [${path.join(", ")}].`,
        line: 5,
        item: `[${path.join(",")}]`,
        watch: [w("found", out.length, "good")],
      });
      events.push({ kind: "leave", id, caption: "Return.", line: 5, note: "✓" });
      return;
    }

    if (remaining < 0 || i === candidates.length) {
      tree.note(id, remaining < 0 ? "over" : "exhausted");
      events.push({
        kind: "enter",
        id,
        caption: `${why} ${
          remaining < 0
            ? `Remaining is ${remaining}, below zero — overshot the target. Nothing below this node can recover, so prune the whole branch here.`
            : `Out of candidates with ${remaining} still to make. Dead end.`
        }`,
        line: 6,
        watch: [w("remaining", remaining, "bad")],
      });
      events.push({ kind: "prune", id, caption: `Prune. Every step of work below this node is avoided — pruning early is what separates a usable exponential search from an unusable one.`, line: 7 });
      return;
    }

    events.push({
      kind: "enter",
      id,
      caption: `${why} ${remaining} still to make, candidates from index ${i} onward.`,
      line: 3,
      watch: [w("remaining", remaining, "active"), w("path", path.join("+") || "∅"), w("i", i)],
    });

    path.push(candidates[i]);
    go(i, remaining - candidates[i], id, `Take ${candidates[i]} again — the recursive call reuses index ${i}, which is what allows a candidate to repeat.`);
    path.pop();

    go(i + 1, remaining, id, `Stop using ${candidates[i]} and move to index ${i + 1}.`);

    events.push({
      kind: "leave",
      id,
      caption: `Both branches under ${remaining} are done.`,
      line: 11,
      watch: [w("found so far", out.length, "good")],
    });
  };

  go(0, target, null, `Start with the full target of ${target}.`);

  return replay(
    tree,
    events,
    COMBO_CODE,
    `${out.length} combination${out.length === 1 ? "" : "s"} sum to ${target}. Count the red nodes: each one is a branch abandoned the moment it became impossible. Sorting the candidates first lets you prune even earlier — break out of the loop as soon as a candidate exceeds the remainder — which is the standard follow-up.`,
  );
};

/**
 * Registry. The `algo` prop of <RecursionTree> indexes this.
 *
 * | key              | uses            |
 * |------------------|-----------------|
 * | fib-naive        | n (≤ 8)         |
 * | fib-memo         | n (≤ 12)        |
 * | subsets          | values (≤ 4)    |
 * | permutations     | values (≤ 3)    |
 * | combination-sum  | values, target  |
 *
 * The size caps are deliberate: these trees grow exponentially, and a 500-node
 * call tree teaches nothing. capFrames() is the backstop.
 */
export const RECURSION_ALGOS: Record<string, RecursionAlgo> = {
  "fib-naive": fibNaive,
  "fib-memo": fibMemo,
  subsets,
  permutations,
  "combination-sum": combinationSum,
};

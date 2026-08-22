# DSA step-through visualizations

Interactive, scrubbable visualizations for the DSA course. Replaces the pattern of
one bespoke p5 sketch per concept — a reader can pause, step backwards, and scrub
to the frame they do not understand.

## The architecture, in one line

```
algorithm (pure)  ──▶  Frame[]  ──▶  VizPlayer (transport)  ──▶  stage renderer
```

An **algorithm** walks its own logic and pushes one `Frame` per meaningful step.
It never touches the DOM, never sets a timer, and is trivially testable.
**VizPlayer** owns all transport: play, pause, step ±1, scrub, speed, reset,
keyboard, reduced-motion, the code line-highlight and the watch panel. A **stage
renderer** is a pure function of one frame.

Consequence: an author writes *data plus an algorithm name* and gets a full
visualization with zero draw code.

## Using one in MDX

```mdx
import ArrayStepper from "../../../../components/viz/ArrayStepper.tsx";

<ArrayStepper
  client:visible
  algo="variable-window-sum"
  values={[2, 3, 1, 2, 4, 3]}
  target={7}
  title="Shrinking to the shortest window that reaches 7"
  desc="Watch left only ever move forward — that is why the nested while loop is still O(n)."
/>
```

`client:visible` is required. Without it the component renders its first frame
and never hydrates.

Every component takes `title` (required), `desc`, `lib` (right-aligned mono
label), `showCode`, `ms` (milliseconds per frame at 1×) and `autoPlay`.

## Components and their algorithms

### `ArrayStepper` — any single-sequence algorithm

Also covers sorting and binary search, so those pages need no separate component.
Pass `tag="sort"` or `tag="search"` to relabel the header pill, and `bars` to
render cells as proportional bars (histogram problems).

| `algo` | inputs |
| --- | --- |
| `fixed-window` | `values`, `k` |
| `variable-window-sum` | `values`, `target` |
| `longest-unique` | `text` |
| `char-replacement` | `text`, `k` |
| `min-window` | `text`, `pattern` |
| `two-sum-sorted` | `values`, `target` |
| `reverse-in-place` | `values` or `text` |
| `dutch-flag` | `values` (0/1/2 only) |
| `prefix-sums` | `values` |
| `kadane` | `values` |
| `cyclic-sort` | `values` (a permutation of 1..n) |
| `remove-duplicates` | `values` (sorted) |
| `container-water` | `values` — pass `bars` |
| `trapping-rain` | `values` — pass `bars` |
| `subarray-sum-k` | `values`, `target` |
| `jump-game` | `values` (jump lengths) — draws the reachability frontier |
| `comparator-keys` | `text` (comma-separated words) — one array, three sort keys |
| `sieve` | `target` (upper bound, 10–60) — strided composite marking |
| `bubble-sort` · `selection-sort` · `insertion-sort` · `merge-sort` · `quick-sort` | `values` |
| `binary-search` · `binary-search-lower-bound` | `values` (sorted), `target` |
| `binary-search-rotated` | `values` (rotated), `target` |
| `count-set-bits` | `values[0]` or `target` — pass `tag="bits"` |
| `xor-single` | `values` — pass `tag="bits"` |
| `bitmask-subsets` | `values` (≤ 4) — pass `tag="bits"` |

### `TreeWalker` — binary trees, with a live call stack or queue

Trees arrive in LeetCode's level-order-with-nulls form, so an array can be pasted
straight out of a problem statement.

| `algo` | inputs |
| --- | --- |
| `preorder` · `inorder` · `postorder` | `tree` |
| `morris-inorder` | `tree` — draws the temporary threads being created and removed |
| `level-order` · `right-side-view` | `tree` |
| `max-depth` · `diameter` · `validate-bst` · `invert` | `tree` |
| `lca` | `tree`, `p`, `q` |
| `path-sum` | `tree`, `target` |

### `GraphTraversal` — graphs, with the frontier structure beside them

Edges are `[from, to]` or `[from, to, weight]`. Layout is derived automatically
(BFS layers by default, or `layout="circle"` for dense graphs).

| `algo` | inputs |
| --- | --- |
| `bfs` · `dfs` | `edges`, `start` |
| `topo-kahn` · `cycle-directed` | `edges` (forced directed) |
| `bipartite` | `edges` |
| `components` | `edges`, `nodes` |
| `dijkstra` | weighted `edges`, `start` |
| `bfs-01` | `edges` weighted 0/1, `start` — shows the deque, not a heap |

### `DPTable` — table fills, with dependency arrows

| `algo` | inputs |
| --- | --- |
| `lcs` · `edit-distance` | `a`, `b` |
| `knapsack` | `weights`, `values`, `target` (capacity) |
| `coin-change` | `values` (coins), `target` |
| `lis` | `values` |
| `unique-paths` | `target` (rows), `values[0]` (cols) |

### `RecursionTree` — call trees

Renders through `TreeWalker`'s stage. **Keep inputs small** — these trees are
exponential, and the caps below are enforced.

| `algo` | inputs |
| --- | --- |
| `fib-naive` | `n` (≤ 8) |
| `fib-memo` | `n` (≤ 12) |
| `subsets` | `values` (≤ 4) |
| `permutations` | `values` (≤ 3) |
| `combination-sum` | `values`, `target` |

### `LinkedListRewire` — pointer surgery

Nodes hold a fixed slot for the whole trace; only the arrows move, because the
arrows are the lesson.

| `algo` | inputs |
| --- | --- |
| `reverse` | `values` |
| `cycle-detection` | `values`, `cycleAt` (−1 for no cycle) |
| `merge-two-lists` | `values`, `other` |
| `remove-nth-from-end` | `values`, `k` (= n) |

### `GridPathfinder` — grids as graphs in disguise

One string per grid row.

| `algo` | grid characters | inputs |
| --- | --- | --- |
| `islands` | `1` land, `0` water | `grid` |
| `maze-bfs` | `#` wall, `.` open | `grid`, `start`, `end` |
| `rotting-oranges` | `2` rotten, `1` fresh, `0` empty | `grid` |

### `StackMachine` — stack algorithms

Input row plus a stack column that grows upward. Exists for the monotonic stack:
its code is six lines, and neither "the stack contents *mean* something" nor
"a `while` inside a `for` is still O(n)" is visible in the source.

| `algo` | inputs |
| --- | --- |
| `next-greater` | `values` |
| `valid-parens` | `text` |
| `eval-rpn` | `text` (space-separated tokens) |

### `HeapView` — a heap in both of its faces

Draws the array *and* the tree, with the same index highlighted in each, and puts
the index arithmetic (`p=(5-1)//2=2`) in the per-cell notes. Nearly every heap bug
is losing track of which face you are reasoning about.

| `algo` | inputs |
| --- | --- |
| `sift-up` | `values` |
| `sift-down` | `values` |
| `top-k` | `values`, `k` |

### `IntervalTimeline` — intervals on a shared axis

Bars packed onto rows so overlaps never collide, plus an optional sweep line and a
result band. Exists because in every interval problem the **sort key** is the
algorithm, and the wrong key produces plausible code that fails on one overlap
shape.

| `algo` | inputs |
| --- | --- |
| `merge` | `intervals` |
| `sweep-line` | `intervals` |
| `greedy-select` | `intervals` |

### `TrieView` — insertion and search in a prefix tree

Renders through `TreeStage` using its edge-label support, since a trie is a tree
whose edges carry characters.

| prop | meaning |
| --- | --- |
| `words` | words to insert, in order |
| `query` | word or prefix to search for afterwards |

### `DSUView` — union-find

Renders through `GraphStage`: a union-find structure is a forest of parent
pointers, which is a directed graph. Union by size and path compression are both
visible as changes to the forest's shape.

| prop | meaning |
| --- | --- |
| `n` | element count, labelled `0..n-1` |
| `unions` | `[[a, b], ...]` operations, in order |

### `SegmentTreeView` — range queries

Renders through `TreeStage`. Shows the two rules that give the log bound: stop
when a node is fully inside the query range, prune when it is fully outside.

| prop | meaning |
| --- | --- |
| `values` | the underlying array |
| `range` | `[lo, hi]` inclusive query |

### `StateMachineView` — DP as a state machine

Renders through `GraphStage`. Some DP problems read far better as states and
transitions than as a table — the stock family especially.

| `algo` | inputs |
| --- | --- |
| `stock-unlimited` | `values` (prices) |
| `stock-cooldown` | `values` (prices) |
| `digit-dp` | `text` (the bound N as digits, ≤ 6), `target` (forbidden digit) |

### `ComplexityChart` — growth rates on a log axis

The one chart in the library. Plots operation counts against n with a dashed
budget line at 10⁸ — roughly what an online judge accepts in a second — plus a
live comparison table. Turns Big-O from notation into a decision procedure.

| prop | meaning |
| --- | --- |
| `curves` | any of `O(1)`, `O(log n)`, `O(n)`, `O(n log n)`, `O(n²)`, `O(2^n)`, `O(n!)` |
| `ns` | n values to evaluate at |

## Adding an algorithm

1. Pick the matching `algos/*.ts` file (or add one, exporting a registry).
2. Write the real algorithm, pushing a frame at every step a reader would want to
   pause on. Push before *and* after a mutation when the mutation is the point (a
   swap, a shrink); once is enough for a plain read.
3. Caption the **decision**, not the mechanics. "Window sum 9 > 7, so shrink from
   the left" teaches; "left += 1" does not. This is the highest-value part of the
   work — the caption is what turns an animation into a lesson.
4. Register it, and document its inputs in the registry's table comment.

Two rules worth stating explicitly:

- **Never mutate a pushed state.** Frames must be independent snapshots, or
  scrubbing backwards shows the wrong thing. Spread-copy arrays and maps.
- **No backticks inside caption template literals.** They terminate the literal.
  Use straight quotes for inline code in a caption.

## Adding a component

Only needed for a genuinely new *picture*. Before writing one, check whether an
existing stage already fits. Sorting, binary search and bit manipulation all reuse
`ArrayStepper`; recursion and tries reuse `TreeStage`; union-find and state
machines reuse `GraphStage`; segment trees reuse `TreeStage`. That reuse is why
there are eleven components rather than the eighteen originally planned — and why
`SortRace`, `BinarySearchDial` and `BitBoard` were never needed.

A component is a thin wrapper: look up the algorithm, `useMemo` the trace, render
`<VizPlayer>` with a `renderStage` callback. Copy `GridPathfinder.tsx` — it is the
smallest complete example.

## Styling

All styles live in `src/styles/dsa-viz.css`, which extends the existing
`.pch-viz` "instrument panel" chassis from `viz.css`. Stage renderers speak in
**tones** (`active`, `good`, `bad`, `warn`, `muted`, `info`) and never in raw
colours, so retheming the whole library happens in the tone palette at the top of
that file.

These panels stay dark in the light theme, deliberately — they are shell output,
not page content.

## Legacy p5 sketches

The 35 existing ```p5 blocks still work and still count toward the `viz` check in
`scripts/audit-dsa.mjs`. Migrate one only where a library component teaches it
better (a stepper the reader can pause beats an autoplaying sketch for anything
with a loop invariant). Keep the p5 sketch where it is genuinely a one-off
illustration rather than an algorithm trace.

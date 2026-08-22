/**
 * algos/heaps.ts — traced heap algorithms for <HeapView>.
 *
 * A binary heap is one idea wearing two faces: it is an **array**, and it is a
 * **tree**, and the whole reason it works is that the tree's shape is implied by
 * array arithmetic — parent at `(i - 1) // 2`, children at `2i + 1` and `2i + 2`.
 * Every heap bug comes from losing track of which face you are looking at.
 *
 * So <HeapView> shows both at once, and these traces highlight the same cell in
 * both faces simultaneously.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

export interface HeapState {
  /** The backing array — the real data structure. */
  values: number[];
  /** Per-index tone, shared by the array and tree faces. */
  marks?: Record<number, Tone>;
  /** Per-index annotation, e.g. the index arithmetic being applied. */
  notes?: Record<number, string>;
  /** Elements already extracted, in extraction order. */
  output?: { text: string; tone?: Tone }[];
  /** Second heap, for the two-heaps / running-median pattern. */
  second?: { label: string; values: number[]; marks?: Record<number, Tone> };
  legend?: { label: string; value: string; tone?: Tone }[];
}

export interface HeapInput {
  values?: number[];
  /** k for top-k problems. */
  k?: number;
}

export type HeapAlgo = (input: HeapInput) => Trace<HeapState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

const parent = (i: number) => Math.floor((i - 1) / 2);
const left = (i: number) => 2 * i + 1;
const right = (i: number) => 2 * i + 2;

// ── 1. Push and sift up ───────────────────────────────────────────────────

const PUSH_CODE = [
  "def push(heap, value):",
  "    heap.append(value)              # always a valid TREE shape",
  "    i = len(heap) - 1",
  "    while i > 0:",
  "        p = (i - 1) // 2",
  "        if heap[p] <= heap[i]: break    # heap property restored",
  "        heap[i], heap[p] = heap[p], heap[i]",
  "        i = p",
];

export const siftUp: HeapAlgo = (input) => {
  const source = input.values?.length ? input.values : [5, 8, 12, 9, 15, 20, 3];
  const t = tracer<HeapState>(PUSH_CODE);
  const heap: number[] = [];

  const state = (marks: Record<number, Tone> = {}, notes: Record<number, string> = {}): HeapState => ({
    values: [...heap],
    marks,
    notes,
    legend: [{ label: "size", value: String(heap.length), tone: "info" }],
  });

  t.push(
    state(),
    `A min-heap keeps one promise only: every parent is ≤ its children. It says nothing about siblings, and nothing about left-to-right order — which is why a heap is not sorted and cannot answer "is x present" quickly.`,
    { line: 2, phase: "setup" },
  );

  for (const v of source) {
    heap.push(v);
    let i = heap.length - 1;

    t.push(
      state({ [i]: "warn" }, { [i]: "new" }),
      `Append ${v} at index ${i}. Appending always keeps the tree **complete** — that is the property that lets an array stand in for a tree at all — but it may break the parent promise.`,
      { line: 3, phase: "append", watch: [w("value", v, "warn"), w("index", i)] },
    );

    while (i > 0) {
      const p = parent(i);
      if (heap[p] <= heap[i]) {
        t.push(
          state({ [i]: "good", [p]: "info" }, { [i]: `child`, [p]: `parent` }),
          `Parent ${heap[p]} ≤ ${heap[i]}, so the promise already holds here. Everything above is untouched and was already valid, so stop — no need to walk to the root.`,
          { line: 6, phase: "settled", watch: [w("parent", heap[p]), w("child", heap[i], "good")] },
        );
        break;
      }

      t.push(
        state({ [i]: "bad", [p]: "bad" }, { [i]: `i=${i}`, [p]: `p=(${i}-1)//2=${p}` }),
        `Parent ${heap[p]} > ${heap[i]} — the promise is broken. Swap them. Note the index arithmetic: the parent of ${i} is (${i} − 1) // 2 = ${p}, computed rather than stored.`,
        { line: 7, phase: "sift up", watch: [w("swap", `${heap[p]} ↔ ${heap[i]}`, "bad")] },
      );

      [heap[i], heap[p]] = [heap[p], heap[i]];
      i = p;
    }
  }

  t.push(
    state(Object.fromEntries(heap.map((_, i) => [i, "good" as Tone]))),
    `All ${source.length} values inserted, root is ${heap[0]}. Each push walks at most one root-to-leaf path, so it is O(log n) — and the array never had a hole in it, which is what "complete tree" buys you.`,
    { line: 8, phase: "answer", watch: [w("min", heap[0], "good"), w("size", heap.length)] },
  );

  return capFrames(t.done(`heap = [${heap.join(", ")}], min = ${heap[0]}`));
};

// ── 2. Pop and sift down ──────────────────────────────────────────────────

const POP_CODE = [
  "def pop(heap):",
  "    top = heap[0]",
  "    heap[0] = heap[-1]              # move the LAST leaf to the root",
  "    heap.pop()",
  "    i = 0",
  "    while True:",
  "        small = i",
  "        for c in (2*i + 1, 2*i + 2):",
  "            if c < len(heap) and heap[c] < heap[small]: small = c",
  "        if small == i: break",
  "        heap[i], heap[small] = heap[small], heap[i]",
  "        i = small",
  "    return top",
];

export const siftDown: HeapAlgo = (input) => {
  const t = tracer<HeapState>(POP_CODE);
  // Start from a valid heap so the trace is about popping, not building.
  const heap = (input.values?.length ? [...input.values] : [3, 5, 12, 9, 15, 20, 8]).slice();
  heap.sort((a, b) => a - b); // guarantees a valid (if boring) heap to start from
  const out: { text: string; tone?: Tone }[] = [];

  const state = (marks: Record<number, Tone> = {}, notes: Record<number, string> = {}): HeapState => ({
    values: [...heap],
    marks,
    notes,
    output: [...out],
    legend: [{ label: "size", value: String(heap.length), tone: "info" }],
  });

  t.push(
    state({ [0]: "good" }),
    `Popping the minimum is easy — it is at index 0. Restoring the heap afterwards is the work, and the trick is counter-intuitive: fill the hole with the **last** leaf, not with the smaller child.`,
    { line: 2, phase: "setup" },
  );

  while (heap.length > 1) {
    const top = heap[0];
    out.push({ text: String(top), tone: "good" });
    const last = heap.pop()!;
    heap[0] = last;

    t.push(
      state({ [0]: "warn" }, { [0]: "was last leaf" }),
      `Extract ${top}, then move the last leaf ${last} to the root. Moving the last leaf keeps the tree complete; promoting a child instead would leave a hole in the middle of the array and break the index arithmetic everything else depends on.`,
      { line: 4, phase: "extract", watch: [w("extracted", top, "good"), w("new root", last, "warn")] },
    );

    let i = 0;
    for (;;) {
      let small = i;
      const l = left(i);
      const r = right(i);
      if (l < heap.length && heap[l] < heap[small]) small = l;
      if (r < heap.length && heap[r] < heap[small]) small = r;

      if (small === i) {
        t.push(
          state({ [i]: "good" }, { [i]: "settled" }),
          `${heap[i]} is now ≤ both its children, so the promise holds and sinking stops.`,
          { line: 10, phase: "settled", watch: [w("settled at", i, "good")] },
        );
        break;
      }

      t.push(
        state(
          {
            [i]: "bad",
            ...(l < heap.length ? { [l]: (small === l ? "good" : "info") as Tone } : {}),
            ...(r < heap.length ? { [r]: (small === r ? "good" : "info") as Tone } : {}),
          },
          {
            [i]: `i=${i}`,
            ...(l < heap.length ? { [l]: `2i+1` } : {}),
            ...(r < heap.length ? { [r]: `2i+2` } : {}),
          },
        ),
        `${heap[i]} is larger than its ${small === l ? "left" : "right"} child ${heap[small]}. Swap with the **smaller** child — swapping with the larger one would immediately violate the promise again on the other side.`,
        {
          line: 11,
          phase: "sift down",
          watch: [w("node", heap[i], "bad"), w("smaller child", heap[small], "good")],
        },
      );

      [heap[i], heap[small]] = [heap[small], heap[i]];
      i = small;
    }
  }

  if (heap.length === 1) out.push({ text: String(heap[0]), tone: "good" });

  t.push(
    { values: [], output: [...out], legend: [{ label: "size", value: "0" }] },
    `Extraction order: ${out.map((o) => o.text).join(" → ")} — sorted, which is heapsort. Each pop is O(log n) because the sink follows one root-to-leaf path, so n pops cost O(n log n).`,
    { line: 13, phase: "answer" },
  );

  return capFrames(t.done(`extracted in order: ${out.map((o) => o.text).join(", ")}`));
};

// ── 3. Top K with a size-limited heap (LC 215) ────────────────────────────

const TOPK_CODE = [
  "import heapq",
  "",
  "def k_largest(nums, k):",
  "    heap = []                        # MIN-heap of the k largest so far",
  "    for v in nums:",
  "        heapq.heappush(heap, v)",
  "        if len(heap) > k:",
  "            heapq.heappop(heap)      # evict the smallest",
  "    return heap[0]                   # kth largest",
];

export const topK: HeapAlgo = (input) => {
  const nums = input.values?.length ? input.values : [3, 2, 1, 5, 6, 4];
  const k = Math.max(1, Math.min(input.k ?? 2, nums.length));
  const t = tracer<HeapState>(TOPK_CODE);

  /** Sorted array standing in for a min-heap; same pop order, simpler to trace. */
  const heap: number[] = [];
  const push = (v: number) => {
    heap.push(v);
    heap.sort((a, b) => a - b);
  };

  const state = (cursor?: number, evicted?: number): HeapState => ({
    values: [...heap],
    marks: Object.fromEntries(
      heap.map((v, i) => [i, (i === 0 ? "warn" : v === cursor ? "active" : "good") as Tone]),
    ),
    notes: heap.length ? { 0: "kth largest" } : {},
    output: evicted !== undefined ? [{ text: `evicted ${evicted}`, tone: "bad" }] : [],
    legend: [
      { label: "k", value: String(k), tone: "info" },
      { label: "heap size", value: `${heap.length}/${k}`, tone: heap.length >= k ? "good" : "warn" },
    ],
  });

  t.push(
    state(),
    `Counter-intuitive setup: to find the k **largest** values, use a **min**-heap. The root is then the smallest of the k best seen so far, which makes it exactly the element to throw away when a better one arrives — and exactly the answer at the end.`,
    { line: 4, phase: "setup", watch: [w("k", k, "info")] },
  );

  for (const v of nums) {
    push(v);
    t.push(
      state(v),
      `Push ${v}. Heap size is ${heap.length}${heap.length > k ? `, over the limit of ${k}` : ""}.`,
      { line: 6, phase: "push", watch: [w("pushed", v, "active"), w("size", heap.length)] },
    );

    if (heap.length > k) {
      const gone = heap.shift()!;
      t.push(
        state(v, gone),
        `Over the limit, so evict the root ${gone} — the smallest of the ${k + 1} candidates, and therefore the one that cannot be among the top ${k}. The heap never exceeds ${k} elements, which is what makes this O(n log k) rather than O(n log n).`,
        { line: 8, phase: "evict", watch: [w("evicted", gone, "bad"), w("size", heap.length, "good")] },
      );
    }
  }

  t.push(
    state(),
    `The heap holds the ${k} largest values, and its root ${heap[0]} is the ${k}th largest overall. Memory is O(k), not O(n) — which is the real reason to prefer this over sorting when n is huge or streaming, even though sorting has the same asymptotic look.`,
    { line: 9, phase: "answer", watch: [w("kth largest", heap[0], "good"), w("top k", heap.join(","), "good")] },
  );

  return capFrames(t.done(`${k}th largest = ${heap[0]}`));
};

/**
 * Registry. The `algo` prop of <HeapView> indexes this.
 *
 * | key         | uses         |
 * |-------------|--------------|
 * | sift-up     | values       |
 * | sift-down   | values       |
 * | top-k       | values, k    |
 */
export const HEAP_ALGOS: Record<string, HeapAlgo> = {
  "sift-up": siftUp,
  "sift-down": siftDown,
  "top-k": topK,
};

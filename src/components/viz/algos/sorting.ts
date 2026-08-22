/**
 * algos/sorting.ts — traced sorts and binary searches, in the ArrayState shape.
 *
 * These deliberately reuse `<ArrayStepper>`'s renderer rather than getting their
 * own components. A sort and a sliding window are both "a row of cells with some
 * cursors and some highlighted regions", so the plan's separate SortRace and
 * BinarySearchDial components collapse into extra entries in one registry —
 * eleven more visualizations for no new rendering code, and a reader sees the
 * same controls on every page.
 *
 * Registered into ALGOS by ./arrays.ts, so MDX usage is unchanged:
 *
 *     <ArrayStepper algo="quick-sort" values={[5, 2, 9, 1, 7, 3]} tag="sort" />
 *     <ArrayStepper algo="binary-search-lower-bound" values={[1,3,3,3,7,9]} target={3} />
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { ArrayAlgo, ArrayInput, ArrayState } from "./arrays";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

const nums = (i: ArrayInput): number[] =>
  (i.values ?? (i.text ? [...i.text].map(Number) : [])).slice();

const DEFAULT = [5, 2, 9, 1, 7, 3, 8, 4];

/** Everything from `sortedFrom` onward is in its final place. */
const sortedTail = (n: number, sortedFrom: number): Record<number, Tone> => {
  const m: Record<number, Tone> = {};
  for (let i = sortedFrom; i < n; i++) m[i] = "good";
  return m;
};

// ── bubble sort ───────────────────────────────────────────────────────────

const BUBBLE_CODE = [
  "def bubble_sort(a):",
  "    n = len(a)",
  "    for end in range(n - 1, 0, -1):",
  "        swapped = False",
  "        for i in range(end):",
  "            if a[i] > a[i + 1]:",
  "                a[i], a[i + 1] = a[i + 1], a[i]",
  "                swapped = True",
  "        if not swapped:          # already sorted — stop early",
  "            break",
  "    return a",
];

export const bubbleSort: ArrayAlgo = (input) => {
  const a = nums(input).length ? nums(input) : DEFAULT;
  const t = tracer<ArrayState>(BUBBLE_CODE);
  let comparisons = 0;
  let swaps = 0;

  t.push(
    { values: [...a] },
    `Bubble sort's invariant: after pass k, the k largest values have bubbled to the end and never move again. That is why the inner loop shrinks each pass.`,
    { line: 2, phase: "setup" },
  );

  for (let end = a.length - 1; end > 0; end--) {
    let swapped = false;
    for (let i = 0; i < end; i++) {
      comparisons += 1;
      const bad = a[i] > a[i + 1];
      t.push(
        {
          values: [...a],
          marks: { ...sortedTail(a.length, end + 1), [i]: bad ? "bad" : "active", [i + 1]: bad ? "bad" : "active" },
          bands: [{ from: 0, to: end, label: "unsorted", tone: "info" }],
          pointers: [{ name: "i", index: i, tone: "active" }],
        },
        bad
          ? `${a[i]} > ${a[i + 1]}, so they are out of order — swap them.`
          : `${a[i]} ≤ ${a[i + 1]}: already in order, nothing to do.`,
        {
          line: 6,
          phase: `pass ${a.length - end}`,
          watch: [w("comparisons", comparisons), w("swaps", swaps, "warn")],
        },
      );
      if (bad) {
        [a[i], a[i + 1]] = [a[i + 1], a[i]];
        swapped = true;
        swaps += 1;
      }
    }
    t.push(
      { values: [...a], marks: sortedTail(a.length, end) },
      `Pass complete: ${a[end]} is the largest of the remaining values, so it is now in its final position. ${
        swapped ? "" : "No swaps happened this pass, which means the array is already sorted — the early exit fires here and turns the best case into O(n)."
      }`,
      { line: swapped ? 3 : 10, phase: `pass ${a.length - end}`, watch: [w("swaps this pass", swapped ? "yes" : "none", swapped ? "warn" : "good")] },
    );
    if (!swapped) break;
  }

  t.push(
    { values: [...a], marks: sortedTail(a.length, 0) },
    `Sorted with ${comparisons} comparisons and ${swaps} swaps. O(n²) worst and average, O(n) best thanks to the early exit, and stable — equal elements never swap past each other. Nobody uses it in production; interviewers ask about it to see whether you can reason about invariants.`,
    { line: 11, phase: "answer", watch: [w("comparisons", comparisons), w("swaps", swaps)] },
  );

  return capFrames(t.done(`[${a.join(", ")}] — ${comparisons} comparisons, ${swaps} swaps`));
};

// ── selection sort ────────────────────────────────────────────────────────

const SELECTION_CODE = [
  "def selection_sort(a):",
  "    for i in range(len(a)):",
  "        lo = i",
  "        for j in range(i + 1, len(a)):",
  "            if a[j] < a[lo]:",
  "                lo = j              # remember the smallest so far",
  "        a[i], a[lo] = a[lo], a[i]   # ONE swap per pass",
  "    return a",
];

export const selectionSort: ArrayAlgo = (input) => {
  const a = nums(input).length ? nums(input) : DEFAULT;
  const t = tracer<ArrayState>(SELECTION_CODE);
  let comparisons = 0;

  for (let i = 0; i < a.length; i++) {
    let lo = i;
    for (let j = i + 1; j < a.length; j++) {
      comparisons += 1;
      const better = a[j] < a[lo];
      if (better) lo = j;
      t.push(
        {
          values: [...a],
          marks: (() => {
            const m: Record<number, Tone> = {};
            for (let k = 0; k < i; k++) m[k] = "good";
            m[lo] = "warn";
            m[j] = better ? "good" : "active";
            return m;
          })(),
          bands: [{ from: i, to: a.length - 1, label: "unsorted", tone: "info" }],
          pointers: [
            { name: "min", index: lo, tone: "warn" },
            { name: "j", index: j, tone: "active" },
          ],
        },
        better
          ? `${a[j]} is smaller than the current minimum ${a[lo === j ? j : lo]} — remember index ${j} instead.`
          : `${a[j]} is not smaller than the minimum so far. Keep scanning; nothing is written yet.`,
        { line: 5, phase: `pass ${i + 1}`, watch: [w("min", a[lo], "warn"), w("comparisons", comparisons)] },
      );
    }
    if (lo !== i) [a[i], a[lo]] = [a[lo], a[i]];
    t.push(
      {
        values: [...a],
        marks: (() => {
          const m: Record<number, Tone> = {};
          for (let k = 0; k <= i; k++) m[k] = "good";
          return m;
        })(),
      },
      `The scan found the minimum; one swap puts it at index ${i}. This is selection sort's whole selling point: exactly n swaps total, regardless of input — useful when writes are expensive and comparisons are cheap.`,
      { line: 7, phase: `pass ${i + 1}`, watch: [w("swaps so far", i + 1, "good")] },
    );
  }

  t.push(
    { values: [...a], marks: sortedTail(a.length, 0) },
    `Sorted. Always O(n²) comparisons — there is no early exit, because the algorithm cannot know it is done without scanning. Not stable in this form. Contrast with bubble sort: same complexity class, far fewer writes.`,
    { line: 8, phase: "answer", watch: [w("comparisons", comparisons), w("swaps", a.length)] },
  );

  return capFrames(t.done(`[${a.join(", ")}] — ${comparisons} comparisons, ≤${a.length} swaps`));
};

// ── insertion sort ────────────────────────────────────────────────────────

const INSERTION_CODE = [
  "def insertion_sort(a):",
  "    for i in range(1, len(a)):",
  "        key = a[i]",
  "        j = i - 1",
  "        while j >= 0 and a[j] > key:",
  "            a[j + 1] = a[j]        # shift right",
  "            j -= 1",
  "        a[j + 1] = key             # drop it in",
  "    return a",
];

export const insertionSort: ArrayAlgo = (input) => {
  const a = nums(input).length ? nums(input) : DEFAULT;
  const t = tracer<ArrayState>(INSERTION_CODE);
  let shifts = 0;

  t.push(
    { values: [...a], marks: { [0]: "good" }, bands: [{ from: 0, to: 0, label: "sorted", tone: "good" }] },
    `Insertion sort grows a sorted prefix. A single element is trivially sorted, so the prefix starts at length 1 and the loop starts at index 1.`,
    { line: 2, phase: "setup" },
  );

  for (let i = 1; i < a.length; i++) {
    const key = a[i];
    let j = i - 1;
    t.push(
      {
        values: [...a],
        marks: { ...sortedPrefix(i), [i]: "warn" },
        bands: [{ from: 0, to: i - 1, label: "sorted", tone: "good" }],
        pointers: [{ name: "key", index: i, tone: "warn" }],
        chips: [{ label: "key", value: String(key), tone: "warn" }],
      },
      `Take ${key} out of the array and find where it belongs in the sorted prefix. Note it is *held aside* — the slot at index ${i} is now free to be overwritten.`,
      { line: 3, phase: `insert ${key}`, watch: [w("key", key, "warn"), w("shifts", shifts)] },
    );

    while (j >= 0 && a[j] > key) {
      a[j + 1] = a[j];
      shifts += 1;
      t.push(
        {
          values: [...a],
          marks: { ...sortedPrefix(i), [j]: "bad", [j + 1]: "active" },
          bands: [{ from: 0, to: i - 1, label: "sorted", tone: "good" }],
          pointers: [{ name: "j", index: j, tone: "bad" }],
          chips: [{ label: "key", value: String(key), tone: "warn" }],
        },
        `${a[j]} > ${key}, so it must end up to the right of the key — shift it one slot right and keep looking left.`,
        { line: 6, phase: `insert ${key}`, watch: [w("key", key, "warn"), w("shifting", a[j], "bad"), w("shifts", shifts)] },
      );
      j -= 1;
    }
    a[j + 1] = key;
    t.push(
      {
        values: [...a],
        marks: { ...sortedPrefix(i + 1), [j + 1]: "good" },
        bands: [{ from: 0, to: i, label: "sorted", tone: "good" }],
      },
      `Everything left of index ${j + 1} is ≤ ${key}, so that is where it belongs. The sorted prefix is now ${i + 1} long.`,
      { line: 8, phase: `insert ${key}`, watch: [w("shifts", shifts)] },
    );
  }

  t.push(
    { values: [...a], marks: sortedTail(a.length, 0) },
    `Sorted with ${shifts} shifts. O(n²) worst case but **O(n) on nearly-sorted input** — the inner while exits immediately when the key is already in place. That property is why Timsort uses insertion sort for small runs, and why it beats the other quadratic sorts in practice.`,
    { line: 9, phase: "answer", watch: [w("shifts", shifts, "good")] },
  );

  function sortedPrefix(n: number): Record<number, Tone> {
    const m: Record<number, Tone> = {};
    for (let k = 0; k < n; k++) m[k] = "good";
    return m;
  }

  return capFrames(t.done(`[${a.join(", ")}] — ${shifts} shifts`));
};

// ── merge sort ────────────────────────────────────────────────────────────

const MERGE_CODE = [
  "def merge_sort(a):",
  "    if len(a) <= 1:",
  "        return a",
  "    mid = len(a) // 2",
  "    left  = merge_sort(a[:mid])",
  "    right = merge_sort(a[mid:])",
  "    return merge(left, right)",
  "",
  "def merge(x, y):",
  "    out, i, j = [], 0, 0",
  "    while i < len(x) and j < len(y):",
  "        if x[i] <= y[j]:            # <= keeps it STABLE",
  "            out.append(x[i]); i += 1",
  "        else:",
  "            out.append(y[j]); j += 1",
  "    return out + x[i:] + y[j:]",
];

export const mergeSort: ArrayAlgo = (input) => {
  const original = nums(input).length ? nums(input) : DEFAULT;
  const t = tracer<ArrayState>(MERGE_CODE);
  const work = [...original];

  t.push(
    { values: [...work] },
    `Merge sort is bottom-up in effect: split until every piece is length 1 (trivially sorted), then merge sorted pieces pairwise. The merge is where all the work happens.`,
    { line: 4, phase: "setup" },
  );

  /** Sort work[lo..hi] in place, tracing each split and merge. */
  const sort = (lo: number, hi: number, depth: number) => {
    if (hi - lo < 1) return;
    const mid = Math.floor((lo + hi) / 2);

    t.push(
      {
        values: [...work],
        bands: [
          { from: lo, to: mid, label: "left", tone: "active" },
          { from: mid + 1, to: hi, label: "right", tone: "warn" },
        ],
        marks: rangeMarks(lo, hi),
      },
      `Split [${lo}..${hi}] into [${lo}..${mid}] and [${mid + 1}..${hi}]. Recursion depth ${depth}, so the split tree is about log₂(n) deep — that is where the log factor comes from.`,
      { line: 4, phase: `split d${depth}`, watch: [w("range", `${lo}..${hi}`), w("depth", depth)] },
    );

    sort(lo, mid, depth + 1);
    sort(mid + 1, hi, depth + 1);

    // Merge the two sorted halves.
    const merged: number[] = [];
    let i = lo;
    let j = mid + 1;
    while (i <= mid && j <= hi) {
      // `<=` and not `<`: taking from the left on a tie is exactly what makes
      // merge sort stable.
      if (work[i] <= work[j]) merged.push(work[i++]);
      else merged.push(work[j++]);
    }
    while (i <= mid) merged.push(work[i++]);
    while (j <= hi) merged.push(work[j++]);
    for (let k = 0; k < merged.length; k++) work[lo + k] = merged[k];

    t.push(
      {
        values: [...work],
        bands: [{ from: lo, to: hi, label: "merged", tone: "good" }],
        marks: (() => {
          const m: Record<number, Tone> = {};
          for (let k = lo; k <= hi; k++) m[k] = "good";
          return m;
        })(),
      },
      `Merged [${lo}..${hi}] into ${merged.join(", ")}. Each merge touches every element in its range exactly once, so a whole level of the tree costs O(n) — and there are log n levels. Note the merge needs O(n) scratch space; merge sort is not in-place.`,
      { line: 16, phase: `merge d${depth}`, watch: [w("range", `${lo}..${hi}`), w("size", hi - lo + 1, "good")] },
    );
  };

  function rangeMarks(lo: number, hi: number): Record<number, Tone> {
    const m: Record<number, Tone> = {};
    for (let k = 0; k < work.length; k++) if (k < lo || k > hi) m[k] = "muted";
    return m;
  }

  sort(0, work.length - 1, 0);

  t.push(
    { values: [...work], marks: sortedTail(work.length, 0) },
    `Sorted. O(n log n) in every case — best, average and worst, which is merge sort's real selling point over quicksort. Costs O(n) extra space, and is **stable**, which is why it (as Timsort) is Python's built-in sort.`,
    { line: 7, phase: "answer" },
  );

  return capFrames(t.done(`[${work.join(", ")}] — O(n log n) guaranteed`));
};

// ── quick sort (Lomuto partition) ─────────────────────────────────────────

const QUICK_CODE = [
  "def quick_sort(a, lo, hi):",
  "    if lo >= hi:",
  "        return",
  "    p = partition(a, lo, hi)",
  "    quick_sort(a, lo, p - 1)",
  "    quick_sort(a, p + 1, hi)",
  "",
  "def partition(a, lo, hi):",
  "    pivot = a[hi]",
  "    i = lo                      # boundary of the < pivot region",
  "    for j in range(lo, hi):",
  "        if a[j] < pivot:",
  "            a[i], a[j] = a[j], a[i]",
  "            i += 1",
  "    a[i], a[hi] = a[hi], a[i]   # pivot into place",
  "    return i",
];

export const quickSort: ArrayAlgo = (input) => {
  const a = nums(input).length ? nums(input) : DEFAULT;
  const t = tracer<ArrayState>(QUICK_CODE);
  const settled = new Set<number>();

  t.push(
    { values: [...a] },
    `Quicksort picks a pivot, moves everything smaller to its left and everything larger to its right, and then recurses. Unlike merge sort it never merges — after one partition the pivot is already in its final position forever.`,
    { line: 4, phase: "setup" },
  );

  const partition = (lo: number, hi: number): number => {
    const pivot = a[hi];
    let i = lo;

    t.push(
      {
        values: [...a],
        marks: { ...outside(lo, hi), [hi]: "warn" },
        bands: [{ from: lo, to: hi, label: `pivot ${pivot}`, tone: "warn" }],
        pointers: [{ name: "pivot", index: hi, tone: "warn" }],
      },
      `Partition [${lo}..${hi}] around the last element, ${pivot}. Using the last element is simple but fragile: on already-sorted input it produces the worst possible split and O(n²). Randomising the pivot choice is the standard fix, and worth saying out loud in an interview.`,
      { line: 9, phase: "partition", watch: [w("pivot", pivot, "warn"), w("range", `${lo}..${hi}`)] },
    );

    for (let j = lo; j < hi; j++) {
      const small = a[j] < pivot;
      t.push(
        {
          values: [...a],
          marks: { ...outside(lo, hi), [hi]: "warn", [j]: small ? "good" : "bad", [i]: "active" },
          bands: [
            { from: lo, to: i - 1, label: `< ${pivot}`, tone: "good" },
            { from: i, to: j, label: `≥ ${pivot}`, tone: "bad" },
          ],
          pointers: [
            { name: "i", index: i, tone: "active" },
            { name: "j", index: j, tone: small ? "good" : "bad" },
          ],
        },
        small
          ? `${a[j]} < ${pivot}, so it belongs in the left region — swap it to the boundary at ${i} and push the boundary right.`
          : `${a[j]} ≥ ${pivot}, so it can stay where it is. Only j advances; the boundary does not move.`,
        { line: small ? 13 : 12, phase: "partition", watch: [w("i", i, "active"), w("j", j), w("pivot", pivot, "warn")] },
      );
      if (small) {
        [a[i], a[j]] = [a[j], a[i]];
        i += 1;
      }
    }

    [a[i], a[hi]] = [a[hi], a[i]];
    settled.add(i);
    t.push(
      {
        values: [...a],
        marks: { ...outside(lo, hi), ...Object.fromEntries([...settled].map((k) => [k, "good" as Tone])) },
        bands: [
          { from: lo, to: i - 1, label: `< ${pivot}`, tone: "info" },
          { from: i, to: i, label: "final", tone: "good" },
          { from: i + 1, to: hi, label: `≥ ${pivot}`, tone: "info" },
        ],
      },
      `Swap the pivot into the boundary at index ${i}. ${pivot} is now in its **final** position and will never move again — that is the property that makes quicksort in-place and quickselect possible.`,
      { line: 15, phase: "partition", watch: [w("pivot final at", i, "good")] },
    );
    return i;
  };

  function outside(lo: number, hi: number): Record<number, Tone> {
    const m: Record<number, Tone> = {};
    for (let k = 0; k < a.length; k++) if (k < lo || k > hi) m[k] = "muted";
    return m;
  }

  const sort = (lo: number, hi: number) => {
    if (lo >= hi) {
      if (lo === hi) settled.add(lo);
      return;
    }
    const p = partition(lo, hi);
    sort(lo, p - 1);
    sort(p + 1, hi);
  };

  sort(0, a.length - 1);

  t.push(
    { values: [...a], marks: sortedTail(a.length, 0) },
    `Sorted in place. O(n log n) average, O(n²) worst (sorted input with a last-element pivot), O(log n) stack. Faster than merge sort in practice because of cache locality, but not stable and not worst-case-safe — which is why Python ships Timsort instead.`,
    { line: 6, phase: "answer" },
  );

  return capFrames(t.done(`[${a.join(", ")}] — in place, O(n log n) average`));
};

// ── binary search: exact match ────────────────────────────────────────────

const BSEARCH_CODE = [
  "def binary_search(a, target):",
  "    lo, hi = 0, len(a) - 1        # INCLUSIVE bounds",
  "    while lo <= hi:               # so the test is <=",
  "        mid = lo + (hi - lo) // 2",
  "        if a[mid] == target:",
  "            return mid",
  "        if a[mid] < target:",
  "            lo = mid + 1          # discard mid",
  "        else:",
  "            hi = mid - 1          # discard mid",
  "    return -1",
];

export const binarySearch: ArrayAlgo = (input) => {
  const a = (nums(input).length ? nums(input) : [1, 3, 5, 7, 9, 11, 13]).slice().sort((x, y) => x - y);
  const target = input.target ?? 7;
  const t = tracer<ArrayState>(BSEARCH_CODE);

  let lo = 0;
  let hi = a.length - 1;
  let found = -1;
  let steps = 0;

  const marks = (mid?: number): Record<number, Tone> => {
    const m: Record<number, Tone> = {};
    for (let i = 0; i < a.length; i++) m[i] = i < lo || i > hi ? "muted" : "info";
    if (mid !== undefined) m[mid] = "active";
    return m;
  };

  t.push(
    { values: a, marks: marks(), bands: [{ from: 0, to: a.length - 1, label: `${a.length} candidates`, tone: "info" }] },
    `Bounds are inclusive on both sides, which is why the loop test is "lo <= hi" and each branch discards mid with a ±1. Mixing an inclusive bound with an exclusive loop test is the single most common binary-search bug — pick one convention and never deviate.`,
    { line: 2, phase: "setup", watch: [w("target", target, "warn"), w("candidates", a.length)] },
  );

  while (lo <= hi) {
    steps += 1;
    const mid = lo + Math.floor((hi - lo) / 2);
    const cmp = a[mid] === target ? 0 : a[mid] < target ? -1 : 1;

    t.push(
      {
        values: a,
        marks: { ...marks(mid), [mid]: cmp === 0 ? "good" : "active" },
        bands: [{ from: lo, to: hi, label: `${hi - lo + 1} left`, tone: cmp === 0 ? "good" : "info" }],
        pointers: [
          { name: "lo", index: lo, tone: "info" },
          { name: "mid", index: mid, tone: "active" },
          { name: "hi", index: hi, tone: "info" },
        ],
      },
      cmp === 0
        ? `a[${mid}] = ${a[mid]} is the target. Found in ${steps} step${steps === 1 ? "" : "s"} — a linear scan would have taken up to ${a.length}.`
        : cmp < 0
          ? `a[${mid}] = ${a[mid]} < ${target}. Everything at or left of ${mid} is too small, so discard all of it: lo becomes ${mid + 1}. Half the remaining candidates gone in one comparison.`
          : `a[${mid}] = ${a[mid]} > ${target}. Everything at or right of ${mid} is too large, so hi becomes ${mid - 1}.`,
      {
        line: cmp === 0 ? 6 : cmp < 0 ? 8 : 10,
        phase: cmp === 0 ? "found" : "halve",
        watch: [w("mid", `${mid} → ${a[mid]}`, "active"), w("target", target, "warn"), w("candidates", hi - lo + 1)],
      },
    );

    if (cmp === 0) {
      found = mid;
      break;
    }
    if (cmp < 0) lo = mid + 1;
    else hi = mid - 1;
  }

  t.push(
    {
      values: a,
      marks: Object.fromEntries(a.map((_, i) => [i, i === found ? "good" : "muted"])),
    },
    found >= 0
      ? `Found ${target} at index ${found} in ${steps} comparisons. ⌈log₂(${a.length})⌉ = ${Math.ceil(Math.log2(a.length + 1))} is the ceiling, and doubling the input adds exactly one comparison.`
      : `${target} is not present. The bounds crossed after ${steps} comparisons — and note that lo now sits at the index where ${target} *would* be inserted, which is what the lower-bound variant returns deliberately.`,
    { line: 11, phase: "answer", watch: [w("result", found, found >= 0 ? "good" : "bad"), w("comparisons", steps)] },
  );

  return capFrames(t.done(found >= 0 ? `index ${found} (${steps} comparisons)` : `not found (${steps} comparisons)`));
};

// ── binary search: lower bound (bisect_left) ──────────────────────────────

const LOWER_CODE = [
  "def lower_bound(a, target):",
  "    lo, hi = 0, len(a)            # hi is EXCLUSIVE here",
  "    while lo < hi:                # so the test is <",
  "        mid = (lo + hi) // 2",
  "        if a[mid] < target:",
  "            lo = mid + 1",
  "        else:",
  "            hi = mid              # keep mid as a candidate",
  "    return lo   # first index where a[i] >= target",
];

export const lowerBound: ArrayAlgo = (input) => {
  const a = (nums(input).length ? nums(input) : [1, 3, 3, 3, 7, 9]).slice().sort((x, y) => x - y);
  const target = input.target ?? 3;
  const t = tracer<ArrayState>(LOWER_CODE);

  let lo = 0;
  let hi = a.length;
  let steps = 0;

  t.push(
    { values: a, bands: [{ from: 0, to: a.length - 1, label: "search space", tone: "info" }] },
    `The exclusive-upper-bound convention. It looks like a small change from the exact-match version, but it is what makes this variant able to answer "where would it go" rather than "is it there" — and it never returns −1, so callers need no special case.`,
    { line: 2, phase: "setup", watch: [w("target", target, "warn")] },
  );

  while (lo < hi) {
    steps += 1;
    const mid = Math.floor((lo + hi) / 2);
    const tooSmall = a[mid] < target;

    t.push(
      {
        values: a,
        marks: (() => {
          const m: Record<number, Tone> = {};
          for (let i = 0; i < a.length; i++) m[i] = i < lo || i >= hi ? "muted" : "info";
          m[mid] = tooSmall ? "bad" : "good";
          return m;
        })(),
        bands: [{ from: lo, to: Math.max(lo, hi - 1), label: `${hi - lo} left`, tone: "info" }],
        pointers: [
          { name: "lo", index: lo, tone: "info" },
          { name: "mid", index: mid, tone: "active" },
        ],
      },
      tooSmall
        ? `a[${mid}] = ${a[mid]} < ${target}, so index ${mid} cannot be the answer — move lo past it.`
        : `a[${mid}] = ${a[mid]} ≥ ${target}, so ${mid} *is* a candidate. Set hi = mid, **not** mid − 1: discarding mid here would step over the very answer we are looking for.`,
      {
        line: tooSmall ? 6 : 8,
        phase: "narrow",
        watch: [w("mid", `${mid} → ${a[mid]}`, "active"), w("candidate?", tooSmall ? "no" : "yes", tooSmall ? "bad" : "good"), w("window", hi - lo)],
      },
    );

    if (tooSmall) lo = mid + 1;
    else hi = mid;
  }

  const count = a.filter((v) => v === target).length;
  t.push(
    {
      values: a,
      marks: Object.fromEntries(a.map((v, i) => [i, v === target ? "good" : "muted"])),
      pointers: [{ name: "result", index: Math.min(lo, a.length - 1), tone: "good" }],
    },
    `Answer: ${lo} — the first index whose value is ≥ ${target}. ${
      count > 0
        ? `Because ${target} appears ${count} time${count === 1 ? "" : "s"}, this is the start of its run; upper_bound (the same loop with <=) gives the end, and the difference ${count} is the count. That pair is bisect_left and bisect_right.`
        : `${target} is absent, so ${lo} is where it would be inserted to keep the array sorted.`
    }`,
    { line: 9, phase: "answer", watch: [w("lower_bound", lo, "good"), w("occurrences", count)] },
  );

  return capFrames(t.done(`lower_bound = ${lo}`));
};

// ── binary search on a rotated sorted array (LC 33) ───────────────────────

const ROTATED_CODE = [
  "def search_rotated(a, target):",
  "    lo, hi = 0, len(a) - 1",
  "    while lo <= hi:",
  "        mid = (lo + hi) // 2",
  "        if a[mid] == target: return mid",
  "        if a[lo] <= a[mid]:              # LEFT half is sorted",
  "            if a[lo] <= target < a[mid]: hi = mid - 1",
  "            else:                        lo = mid + 1",
  "        else:                            # RIGHT half is sorted",
  "            if a[mid] < target <= a[hi]: lo = mid + 1",
  "            else:                        hi = mid - 1",
  "    return -1",
];

export const binarySearchRotated: ArrayAlgo = (input) => {
  const a = nums(input).length ? nums(input) : [4, 5, 6, 7, 0, 1, 2];
  const target = input.target ?? 0;
  const t = tracer<ArrayState>(ROTATED_CODE);

  let lo = 0;
  let hi = a.length - 1;
  let found = -1;

  t.push
  (
    { values: a, bands: [{ from: 0, to: a.length - 1, label: "rotated", tone: "warn" }] },
    `The array is sorted but rotated, so it is not globally sorted and plain binary search fails. The insight: whatever the rotation, **at least one half of any window is properly sorted**, and you can test which in one comparison.`,
    { line: 2, phase: "setup", watch: [w("target", target, "warn")] },
  );

  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (a[mid] === target) {
      t.push(
        {
          values: a,
          marks: { ...window(lo, hi), [mid]: "good" },
          pointers: [{ name: "mid", index: mid, tone: "good" }],
        },
        `a[${mid}] = ${target}. Found.`,
        { line: 5, phase: "found", watch: [w("index", mid, "good")] },
      );
      found = mid;
      break;
    }

    const leftSorted = a[lo] <= a[mid];
    const inLeft = leftSorted && a[lo] <= target && target < a[mid];
    const inRight = !leftSorted && a[mid] < target && target <= a[hi];
    const goLeft = leftSorted ? inLeft : !inRight;

    t.push(
      {
        values: a,
        marks: { ...window(lo, hi), [mid]: "active" },
        bands: leftSorted
          ? [
              { from: lo, to: mid, label: "sorted", tone: "good" },
              { from: mid + 1, to: hi, label: "contains the pivot", tone: "warn" },
            ]
          : [
              { from: lo, to: mid - 1, label: "contains the pivot", tone: "warn" },
              { from: mid, to: hi, label: "sorted", tone: "good" },
            ],
        pointers: [
          { name: "lo", index: lo, tone: "info" },
          { name: "mid", index: mid, tone: "active" },
          { name: "hi", index: hi, tone: "info" },
        ],
      },
      `a[lo] = ${a[lo]}, a[mid] = ${a[mid]}: the **${leftSorted ? "left" : "right"}** half is the sorted one. In a sorted half you can decide membership by a simple range test, and ${target} ${
        (leftSorted ? inLeft : inRight) ? "is" : "is not"
      } inside it — so search the ${goLeft ? "left" : "right"} half.`,
      {
        line: leftSorted ? 7 : 10,
        phase: "decide",
        watch: [
          w("sorted half", leftSorted ? "left" : "right", "good"),
          w("target in it?", (leftSorted ? inLeft : inRight) ? "yes" : "no", (leftSorted ? inLeft : inRight) ? "good" : "bad"),
          w("go", goLeft ? "left" : "right", "active"),
        ],
      },
    );

    if (goLeft) hi = mid - 1;
    else lo = mid + 1;
  }

  function window(l: number, h: number): Record<number, Tone> {
    const m: Record<number, Tone> = {};
    for (let i = 0; i < a.length; i++) m[i] = i < l || i > h ? "muted" : "info";
    return m;
  }

  t.push(
    { values: a, marks: Object.fromEntries(a.map((_, i) => [i, i === found ? "good" : "muted"])) },
    found >= 0
      ? `Found ${target} at index ${found}, still in O(log n) — the rotation costs one extra comparison per step, not an extra factor. Duplicates break the "a[lo] <= a[mid]" test, which is why LC 81 is a separate, harder problem.`
      : `${target} is not in the array.`,
    { line: 12, phase: "answer", watch: [w("result", found, found >= 0 ? "good" : "bad")] },
  );

  return capFrames(t.done(found >= 0 ? `index ${found}` : "not found"));
};

/**
 * Registry, merged into ALGOS by ./arrays.ts.
 *
 * | key                      | uses                        |
 * |--------------------------|-----------------------------|
 * | bubble-sort              | values                      |
 * | selection-sort           | values                      |
 * | insertion-sort           | values                      |
 * | merge-sort               | values                      |
 * | quick-sort               | values                      |
 * | binary-search            | values (sorted), target     |
 * | binary-search-lower-bound| values (sorted), target     |
 * | binary-search-rotated    | values (rotated), target    |
 */
export const SORT_ALGOS: Record<string, ArrayAlgo> = {
  "bubble-sort": bubbleSort,
  "selection-sort": selectionSort,
  "insertion-sort": insertionSort,
  "merge-sort": mergeSort,
  "quick-sort": quickSort,
  "binary-search": binarySearch,
  "binary-search-lower-bound": lowerBound,
  "binary-search-rotated": binarySearchRotated,
};

/**
 * algos/arrays.ts — traced sequence algorithms for <ArrayStepper>.
 *
 * Every export here is a pure function: inputs in, `Trace<ArrayState>` out.
 * No DOM, no timers, no randomness — so a trace is reproducible, diffable, and
 * testable, and the same algorithm renders identically on the server and the
 * client.
 *
 * ADDING AN ALGORITHM
 * -------------------
 * 1. Write the real algorithm, but push a frame at every step a reader would
 *    want to pause on. Push *before* and *after* a mutation when the mutation
 *    is the point (a swap, a shrink); once is enough for a plain read.
 * 2. Give every frame a caption that names the *decision*, not the mechanics.
 *    "Window sum 9 > 7, so shrink from the left" teaches. "left += 1" does not.
 * 3. Register it in ALGOS at the bottom, and document its required inputs.
 */
import { tracer, capFrames, type Band, type Pointer, type Tone, type Trace, type Watch } from "../frames";
import { SORT_ALGOS } from "./sorting";
import { BIT_ALGOS } from "./bits";
import { STRING_ALGOS } from "./strings";
import { FRONTIER_ALGOS } from "./frontier";
import { DESIGN_ALGOS } from "./design";

/** A secondary row drawn under the main one — prefix sums, dp values, counts. */
export interface AuxRow {
  label: string;
  values: (number | string)[];
  marks?: Record<number, Tone>;
}

/** Snapshot of a sequence visualization. */
export interface ArrayState {
  values: (number | string)[];
  pointers?: Pointer[];
  /** Inclusive index ranges drawn as brackets over the row. */
  bands?: Band[];
  /** Per-index cell tone. */
  marks?: Record<number, Tone>;
  /** Key/value chips — a hash map, a frequency table, a running best. */
  chips?: { label: string; value: string; tone?: Tone }[];
  /** Extra rows under the main sequence. */
  rows?: AuxRow[];
}

/** Everything an algorithm may ask for. Each algorithm documents what it uses. */
export interface ArrayInput {
  /** Numeric sequence. Ignored when `text` is given. */
  values?: number[];
  /** String input — split into characters and used as `values`. */
  text?: string;
  /** Window width / count parameter. */
  k?: number;
  /** Threshold parameter (target sum, allowed replacements, …). */
  target?: number;
  /** Pattern / needle for matching problems. */
  pattern?: string;
}

export type ArrayAlgo = (input: ArrayInput) => Trace<ArrayState>;

// ── helpers ────────────────────────────────────────────────────────────────

const seq = (i: ArrayInput): (number | string)[] =>
  i.text !== undefined ? [...i.text] : (i.values ?? []);

const nums = (i: ArrayInput): number[] =>
  i.values ?? (i.text ? [...i.text].map(Number) : []);

/** Cells before `from` are done; cells after `to` are untouched. */
const windowMarks = (len: number, from: number, to: number): Record<number, Tone> => {
  const m: Record<number, Tone> = {};
  for (let i = 0; i < len; i++) {
    if (i < from) m[i] = "muted";
    else if (i <= to) m[i] = "active";
  }
  return m;
};

const w = (label: string, value: string | number, tone?: Tone): Watch => ({
  label,
  value,
  tone,
});

// ── 1. Fixed-size window (LC 643 · Maximum Average Subarray I) ─────────────

const FIXED_CODE = [
  "def max_sum_fixed(arr, k):",
  "    window = sum(arr[:k])",
  "    best = window",
  "    for right in range(k, len(arr)):",
  "        window += arr[right]        # element enters",
  "        window -= arr[right - k]    # element leaves",
  "        best = max(best, window)",
  "    return best",
];

export const fixedWindow: ArrayAlgo = (input) => {
  const arr = nums(input);
  const k = Math.max(1, Math.min(input.k ?? 3, arr.length));
  const t = tracer<ArrayState>(FIXED_CODE);

  let window = 0;
  for (let i = 0; i < k; i++) window += arr[i];
  let best = window;
  let bestAt = 0;

  t.push(
    {
      values: arr,
      bands: [{ from: 0, to: k - 1, label: `k = ${k}`, tone: "active" }],
      marks: windowMarks(arr.length, 0, k - 1),
    },
    `Seed the first window: sum of the first ${k} elements is ${window}.`,
    { line: 2, phase: "seed", watch: [w("window", window, "active"), w("best", best, "good")] },
  );

  for (let right = k; right < arr.length; right++) {
    const leaving = right - k;
    t.push(
      {
        values: arr,
        bands: [{ from: leaving, to: right, label: "in flight", tone: "warn" }],
        marks: { ...windowMarks(arr.length, leaving, right), [right]: "good", [leaving]: "bad" },
        pointers: [
          { name: "out", index: leaving, tone: "bad" },
          { name: "in", index: right, tone: "good" },
        ],
      },
      `Slide right: ${arr[right]} enters, ${arr[leaving]} leaves. Only two cells change, so the sum costs O(1) to update — not O(k).`,
      {
        line: 5,
        phase: "slide",
        watch: [w("window", window, "muted"), w("+in", arr[right], "good"), w("−out", arr[leaving], "bad")],
      },
    );

    window += arr[right] - arr[leaving];
    const improved = window > best;
    if (improved) {
      best = window;
      bestAt = leaving + 1;
    }

    t.push(
      {
        values: arr,
        bands: [
          { from: leaving + 1, to: right, label: `sum ${window}`, tone: improved ? "good" : "active" },
        ],
        marks: windowMarks(arr.length, leaving + 1, right),
      },
      improved
        ? `Window sum is now ${window} — a new best.`
        : `Window sum is ${window}, which does not beat ${best}. Keep sliding.`,
      {
        line: 7,
        phase: "slide",
        watch: [w("window", window, "active"), w("best", best, "good")],
      },
    );
  }

  t.push(
    {
      values: arr,
      bands: [{ from: bestAt, to: bestAt + k - 1, label: `best ${best}`, tone: "good" }],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < arr.length; i++) m[i] = i >= bestAt && i < bestAt + k ? "good" : "muted";
        return m;
      })(),
    },
    `Every window was visited exactly once, so the whole scan is O(n). Best window sum: ${best}.`,
    { line: 8, phase: "answer", watch: [w("best", best, "good")] },
  );

  return capFrames(t.done(`max window sum = ${best} at indices ${bestAt}..${bestAt + k - 1}`));
};

// ── 2. Variable window on a sum (LC 209 · Minimum Size Subarray Sum) ───────

const VAR_SUM_CODE = [
  "def min_len_at_least(arr, target):",
  "    left = total = 0",
  "    best = float('inf')",
  "    for right in range(len(arr)):",
  "        total += arr[right]              # expand",
  "        while total >= target:           # valid — try to shrink",
  "            best = min(best, right - left + 1)",
  "            total -= arr[left]",
  "            left += 1",
  "    return 0 if best == float('inf') else best",
];

export const variableWindowSum: ArrayAlgo = (input) => {
  const arr = nums(input);
  const target = input.target ?? 7;
  const t = tracer<ArrayState>(VAR_SUM_CODE);

  let left = 0;
  let total = 0;
  let best = Infinity;
  let bestRange: [number, number] | null = null;

  for (let right = 0; right < arr.length; right++) {
    total += arr[right];
    t.push(
      {
        values: arr,
        bands: [{ from: left, to: right, label: `sum ${total}`, tone: total >= target ? "good" : "active" }],
        marks: windowMarks(arr.length, left, right),
        pointers: [
          { name: "left", index: left, tone: "info" },
          { name: "right", index: right, tone: "active" },
        ],
      },
      `Expand: ${arr[right]} joins the window, sum becomes ${total}. ${
        total >= target ? `That reaches the target of ${target}.` : `Still short of ${target}.`
      }`,
      {
        line: 5,
        phase: "expand",
        watch: [w("total", total, total >= target ? "good" : "active"), w("target", target), w("best", best === Infinity ? "∞" : best, "good")],
      },
    );

    while (total >= target) {
      const len = right - left + 1;
      if (len < best) {
        best = len;
        bestRange = [left, right];
      }
      t.push(
        {
          values: arr,
          bands: [{ from: left, to: right, label: `len ${len}`, tone: "good" }],
          marks: windowMarks(arr.length, left, right),
          pointers: [
            { name: "left", index: left, tone: "warn" },
            { name: "right", index: right, tone: "active" },
          ],
        },
        `Window [${left}..${right}] is valid with length ${len}. Record it, then drop ${arr[left]} from the left to see whether a shorter window also works.`,
        {
          line: 7,
          phase: "shrink",
          watch: [w("total", total, "good"), w("len", len, "good"), w("best", best, "good")],
        },
      );
      total -= arr[left];
      left += 1;
      t.push(
        {
          values: arr,
          bands: [{ from: left, to: right, label: `sum ${total}`, tone: total >= target ? "good" : "warn" }],
          marks: windowMarks(arr.length, left, right),
          pointers: [
            { name: "left", index: left, tone: "info" },
            { name: "right", index: right, tone: "active" },
          ],
        },
        total >= target
          ? `Still valid at ${total} — shrink again.`
          : `Sum dropped to ${total}, below ${target}. Stop shrinking and go back to expanding.`,
        {
          line: 9,
          phase: "shrink",
          watch: [w("total", total, total >= target ? "good" : "warn"), w("left", left), w("best", best, "good")],
        },
      );
    }
  }

  const answer = best === Infinity ? 0 : best;
  t.push(
    {
      values: arr,
      bands: bestRange ? [{ from: bestRange[0], to: bestRange[1], label: `len ${best}`, tone: "good" }] : [],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < arr.length; i++) {
          m[i] = bestRange && i >= bestRange[0] && i <= bestRange[1] ? "good" : "muted";
        }
        return m;
      })(),
    },
    bestRange
      ? `Shortest window reaching ${target} is indices ${bestRange[0]}..${bestRange[1]}, length ${best}. Both pointers only ever moved forward, so the scan is O(n) despite the inner while loop.`
      : `No window ever reached ${target}, so the answer is 0.`,
    { line: 10, phase: "answer", watch: [w("answer", answer, "good")] },
  );

  return capFrames(t.done(`min length = ${answer}`));
};

// ── 3. Longest substring without repeating characters (LC 3) ───────────────

const UNIQUE_CODE = [
  "def longest_unique(s):",
  "    seen = {}          # char -> last index",
  "    left = best = 0",
  "    for right, ch in enumerate(s):",
  "        if ch in seen and seen[ch] >= left:",
  "            left = seen[ch] + 1      # jump past the duplicate",
  "        seen[ch] = right",
  "        best = max(best, right - left + 1)",
  "    return best",
];

export const longestUnique: ArrayAlgo = (input) => {
  const chars = seq(input).map(String);
  const t = tracer<ArrayState>(UNIQUE_CODE);

  const seen = new Map<string, number>();
  let left = 0;
  let best = 0;
  let bestRange: [number, number] = [0, -1];

  for (let right = 0; right < chars.length; right++) {
    const ch = chars[right];
    const prev = seen.get(ch);
    const isDup = prev !== undefined && prev >= left;

    if (isDup) {
      t.push(
        {
          values: chars,
          bands: [{ from: left, to: right, label: "duplicate!", tone: "bad" }],
          marks: { ...windowMarks(chars.length, left, right), [prev!]: "bad", [right]: "bad" },
          pointers: [
            { name: "left", index: left, tone: "warn" },
            { name: "right", index: right, tone: "bad" },
          ],
          chips: [...seen.entries()].map(([c, i]) => ({
            label: c,
            value: String(i),
            tone: c === ch ? "bad" : "muted",
          })),
        },
        `'${ch}' already appears at index ${prev} inside the window. Jump left straight to ${prev! + 1} — shrinking one step at a time would be correct but slower.`,
        { line: 6, phase: "jump", watch: [w("dup", `'${ch}' @ ${prev}`, "bad"), w("left", `${left} → ${prev! + 1}`, "warn")] },
      );
      left = prev! + 1;
    }

    seen.set(ch, right);
    const len = right - left + 1;
    const improved = len > best;
    if (improved) {
      best = len;
      bestRange = [left, right];
    }

    t.push(
      {
        values: chars,
        bands: [{ from: left, to: right, label: `len ${len}`, tone: improved ? "good" : "active" }],
        marks: windowMarks(chars.length, left, right),
        pointers: [
          { name: "left", index: left, tone: "info" },
          { name: "right", index: right, tone: "active" },
        ],
        chips: [...seen.entries()].map(([c, i]) => ({
          label: c,
          value: String(i),
          tone: i >= left ? "active" : "muted",
        })),
      },
      improved
        ? `Window "${chars.slice(left, right + 1).join("")}" has ${len} distinct characters — a new best.`
        : `Window "${chars.slice(left, right + 1).join("")}" has length ${len}, not better than ${best}.`,
      {
        line: 8,
        phase: "expand",
        watch: [w("window", chars.slice(left, right + 1).join("") || "∅", "active"), w("best", best, "good")],
      },
    );
  }

  t.push(
    {
      values: chars,
      bands: [{ from: bestRange[0], to: bestRange[1], label: `best ${best}`, tone: "good" }],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < chars.length; i++) {
          m[i] = i >= bestRange[0] && i <= bestRange[1] ? "good" : "muted";
        }
        return m;
      })(),
    },
    `Longest run of distinct characters is "${chars.slice(bestRange[0], bestRange[1] + 1).join("")}", length ${best}.`,
    { line: 9, phase: "answer", watch: [w("best", best, "good")] },
  );

  return capFrames(t.done(`longest distinct run = ${best}`));
};

// ── 4. Longest repeating character replacement (LC 424) ────────────────────

const REPLACE_CODE = [
  "def char_replacement(s, k):",
  "    count = {}",
  "    left = best = max_freq = 0",
  "    for right, ch in enumerate(s):",
  "        count[ch] = count.get(ch, 0) + 1",
  "        max_freq = max(max_freq, count[ch])",
  "        while (right - left + 1) - max_freq > k:",
  "            count[s[left]] -= 1",
  "            left += 1",
  "        best = max(best, right - left + 1)",
  "    return best",
];

export const charReplacement: ArrayAlgo = (input) => {
  const chars = seq(input).map(String);
  const k = input.k ?? input.target ?? 2;
  const t = tracer<ArrayState>(REPLACE_CODE);

  const count = new Map<string, number>();
  let left = 0;
  let best = 0;
  let maxFreq = 0;
  let bestRange: [number, number] = [0, -1];

  const chips = (focus?: string) =>
    [...count.entries()]
      .filter(([, n]) => n > 0)
      .map(([c, n]) => ({ label: c, value: String(n), tone: (c === focus ? "active" : "muted") as Tone }));

  for (let right = 0; right < chars.length; right++) {
    const ch = chars[right];
    count.set(ch, (count.get(ch) ?? 0) + 1);
    maxFreq = Math.max(maxFreq, count.get(ch)!);
    let size = right - left + 1;

    t.push(
      {
        values: chars,
        bands: [{ from: left, to: right, label: `${size - maxFreq} to replace`, tone: size - maxFreq > k ? "warn" : "active" }],
        marks: windowMarks(chars.length, left, right),
        pointers: [
          { name: "left", index: left, tone: "info" },
          { name: "right", index: right, tone: "active" },
        ],
        chips: chips(ch),
      },
      `'${ch}' enters. The window is size ${size} and its most common character appears ${maxFreq} times, so ${size - maxFreq} characters would need replacing.`,
      {
        line: 6,
        phase: "expand",
        watch: [w("size", size), w("maxFreq", maxFreq, "good"), w("toReplace", size - maxFreq, size - maxFreq > k ? "bad" : "good"), w("k", k)],
      },
    );

    while (size - maxFreq > k) {
      const outCh = chars[left];
      count.set(outCh, count.get(outCh)! - 1);
      left += 1;
      size = right - left + 1;
      t.push(
        {
          values: chars,
          bands: [{ from: left, to: right, label: `${size - maxFreq} to replace`, tone: "warn" }],
          marks: windowMarks(chars.length, left, right),
          pointers: [
            { name: "left", index: left, tone: "warn" },
            { name: "right", index: right, tone: "active" },
          ],
          chips: chips(outCh),
        },
        `More than ${k} replacements needed, so drop '${outCh}' from the left. Note that maxFreq is deliberately never decreased — a stale-but-too-large maxFreq can only make the window look worse, so the answer stays correct and the code stays O(n).`,
        {
          line: 9,
          phase: "shrink",
          watch: [w("size", size), w("maxFreq", maxFreq, "muted"), w("toReplace", size - maxFreq, "warn")],
        },
      );
    }

    if (size > best) {
      best = size;
      bestRange = [left, right];
    }
  }

  t.push(
    {
      values: chars,
      bands: [{ from: bestRange[0], to: bestRange[1], label: `best ${best}`, tone: "good" }],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < chars.length; i++) m[i] = i >= bestRange[0] && i <= bestRange[1] ? "good" : "muted";
        return m;
      })(),
    },
    `With at most ${k} replacements the longest uniform run reachable is length ${best}.`,
    { line: 11, phase: "answer", watch: [w("best", best, "good")] },
  );

  return capFrames(t.done(`longest after ≤${k} replacements = ${best}`));
};

// ── 5. Minimum window substring (LC 76) ───────────────────────────────────

const MIN_WINDOW_CODE = [
  "def min_window(s, t):",
  "    need = Counter(t)",
  "    missing = len(t)",
  "    left = 0; best = (0, len(s) + 1)",
  "    for right, ch in enumerate(s):",
  "        if need[ch] > 0: missing -= 1",
  "        need[ch] -= 1",
  "        while missing == 0:                 # valid — shrink",
  "            if right - left < best[1] - best[0]:",
  "                best = (left, right + 1)",
  "            need[s[left]] += 1",
  "            if need[s[left]] > 0: missing += 1",
  "            left += 1",
  "    return s[best[0]:best[1]]",
];

export const minWindow: ArrayAlgo = (input) => {
  const chars = seq(input).map(String);
  const pat = [...(input.pattern ?? "ABC")];
  const t = tracer<ArrayState>(MIN_WINDOW_CODE);

  const need = new Map<string, number>();
  for (const c of pat) need.set(c, (need.get(c) ?? 0) + 1);
  let missing = pat.length;
  let left = 0;
  let bestLo = 0;
  let bestHi = chars.length + 1;

  const chips = () =>
    [...need.entries()].map(([c, n]) => ({
      label: c,
      value: n > 0 ? `need ${n}` : n === 0 ? "met" : `+${-n}`,
      tone: (n > 0 ? "bad" : n === 0 ? "good" : "muted") as Tone,
    }));

  for (let right = 0; right < chars.length; right++) {
    const ch = chars[right];
    const wasNeeded = (need.get(ch) ?? 0) > 0;
    if (wasNeeded) missing -= 1;
    need.set(ch, (need.get(ch) ?? 0) - 1);

    t.push(
      {
        values: chars,
        bands: [{ from: left, to: right, label: missing === 0 ? "covers t" : `${missing} missing`, tone: missing === 0 ? "good" : "active" }],
        marks: windowMarks(chars.length, left, right),
        pointers: [
          { name: "left", index: left, tone: "info" },
          { name: "right", index: right, tone: "active" },
        ],
        chips: chips(),
      },
      wasNeeded
        ? `'${ch}' was still needed — one fewer missing character, ${missing} to go.`
        : `'${ch}' was already covered, so it counts as surplus. Missing stays at ${missing}.`,
      {
        line: 7,
        phase: "expand",
        watch: [w("missing", missing, missing === 0 ? "good" : "bad"), w("window", chars.slice(left, right + 1).join(""), "active")],
      },
    );

    while (missing === 0) {
      if (right - left < bestHi - bestLo) {
        bestLo = left;
        bestHi = right + 1;
        t.push(
          {
            values: chars,
            bands: [{ from: left, to: right, label: `len ${right - left + 1} ★`, tone: "good" }],
            marks: windowMarks(chars.length, left, right),
            pointers: [
              { name: "left", index: left, tone: "good" },
              { name: "right", index: right, tone: "good" },
            ],
            chips: chips(),
          },
          `"${chars.slice(left, right + 1).join("")}" covers every character of the pattern and is the shortest such window so far.`,
          { line: 10, phase: "record", watch: [w("best", chars.slice(bestLo, bestHi).join(""), "good")] },
        );
      }
      const outCh = chars[left];
      need.set(outCh, need.get(outCh)! + 1);
      const nowMissing = need.get(outCh)! > 0;
      if (nowMissing) missing += 1;
      left += 1;
      t.push(
        {
          values: chars,
          bands: [{ from: left, to: right, label: nowMissing ? `${missing} missing` : "still covers", tone: nowMissing ? "warn" : "good" }],
          marks: windowMarks(chars.length, left, right),
          pointers: [
            { name: "left", index: left, tone: nowMissing ? "warn" : "info" },
            { name: "right", index: right, tone: "active" },
          ],
          chips: chips(),
        },
        nowMissing
          ? `Dropping '${outCh}' broke coverage — it is needed again. Back to expanding.`
          : `'${outCh}' was surplus, so the window still covers the pattern. Shrink again.`,
        { line: 13, phase: "shrink", watch: [w("missing", missing, nowMissing ? "bad" : "good")] },
      );
    }
  }

  const answer = bestHi > chars.length ? "" : chars.slice(bestLo, bestHi).join("");
  t.push(
    {
      values: chars,
      bands: answer ? [{ from: bestLo, to: bestHi - 1, label: `"${answer}"`, tone: "good" }] : [],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < chars.length; i++) m[i] = answer && i >= bestLo && i < bestHi ? "good" : "muted";
        return m;
      })(),
    },
    answer
      ? `Smallest window containing "${pat.join("")}" is "${answer}".`
      : `No window contains every character of "${pat.join("")}".`,
    { line: 14, phase: "answer", watch: [w("answer", answer || "∅", "good")] },
  );

  return capFrames(t.done(answer ? `min window = "${answer}"` : "no valid window"));
};

// ── 6. Two pointers on a sorted array (LC 167) ─────────────────────────────

const TWO_SUM_CODE = [
  "def two_sum_sorted(arr, target):",
  "    lo, hi = 0, len(arr) - 1",
  "    while lo < hi:",
  "        total = arr[lo] + arr[hi]",
  "        if total == target: return (lo, hi)",
  "        if total < target: lo += 1     # need more",
  "        else:              hi -= 1     # need less",
  "    return None",
];

export const twoSumSorted: ArrayAlgo = (input) => {
  const arr = nums(input);
  const target = input.target ?? 9;
  const t = tracer<ArrayState>(TWO_SUM_CODE);

  let lo = 0;
  let hi = arr.length - 1;
  let found: [number, number] | null = null;

  while (lo < hi) {
    const total = arr[lo] + arr[hi];
    const tone: Tone = total === target ? "good" : total < target ? "warn" : "bad";
    t.push(
      {
        values: arr,
        marks: { ...windowMarks(arr.length, lo, hi), [lo]: tone, [hi]: tone },
        pointers: [
          { name: "lo", index: lo, tone: "info" },
          { name: "hi", index: hi, tone: "active" },
        ],
        bands: [{ from: lo, to: hi, label: `sum ${total}`, tone }],
      },
      total === target
        ? `${arr[lo]} + ${arr[hi]} = ${target}. Found it.`
        : total < target
          ? `${arr[lo]} + ${arr[hi]} = ${total}, below ${target}. Because the array is sorted, the only way to increase the sum is to move lo right — moving hi left would only make it smaller.`
          : `${arr[lo]} + ${arr[hi]} = ${total}, above ${target}. Move hi left to decrease the sum.`,
      {
        line: total === target ? 5 : total < target ? 6 : 7,
        phase: total === target ? "hit" : "narrow",
        watch: [w("lo", `${lo} → ${arr[lo]}`), w("hi", `${hi} → ${arr[hi]}`), w("sum", total, tone), w("target", target)],
      },
    );
    if (total === target) {
      found = [lo, hi];
      break;
    }
    if (total < target) lo += 1;
    else hi -= 1;
  }

  t.push(
    {
      values: arr,
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < arr.length; i++) m[i] = found && (i === found[0] || i === found[1]) ? "good" : "muted";
        return m;
      })(),
    },
    found
      ? `Answer: indices ${found[0]} and ${found[1]}. Each pointer moved at most n steps, so this is O(n) time and O(1) space — no hash map needed once the array is sorted.`
      : `The pointers met without finding a pair summing to ${target}.`,
    { line: 8, phase: "answer" },
  );

  return capFrames(t.done(found ? `indices ${found[0]}, ${found[1]}` : "no pair found"));
};

// ── 7. Two-pointer in-place reversal ──────────────────────────────────────

const REVERSE_CODE = [
  "def reverse(arr):",
  "    lo, hi = 0, len(arr) - 1",
  "    while lo < hi:",
  "        arr[lo], arr[hi] = arr[hi], arr[lo]",
  "        lo += 1",
  "        hi -= 1",
  "    return arr",
];

export const reverseInPlace: ArrayAlgo = (input) => {
  const arr = [...seq(input)];
  const t = tracer<ArrayState>(REVERSE_CODE);
  let lo = 0;
  let hi = arr.length - 1;

  t.push(
    { values: [...arr], pointers: [{ name: "lo", index: lo, tone: "info" }, { name: "hi", index: hi, tone: "active" }] },
    `Start with pointers at both ends. Reversal swaps ${Math.floor(arr.length / 2)} pairs and allocates nothing.`,
    { line: 2, phase: "setup" },
  );

  while (lo < hi) {
    t.push(
      {
        values: [...arr],
        marks: { [lo]: "warn", [hi]: "warn" },
        pointers: [{ name: "lo", index: lo, tone: "warn" }, { name: "hi", index: hi, tone: "warn" }],
      },
      `About to swap ${arr[lo]} and ${arr[hi]}.`,
      { line: 4, phase: "swap", watch: [w("lo", lo), w("hi", hi)] },
    );
    [arr[lo], arr[hi]] = [arr[hi], arr[lo]];
    t.push(
      {
        values: [...arr],
        marks: { [lo]: "good", [hi]: "good" },
        pointers: [{ name: "lo", index: lo, tone: "good" }, { name: "hi", index: hi, tone: "good" }],
      },
      `Swapped. Both ends are now in their final positions.`,
      { line: 4, phase: "swap" },
    );
    lo += 1;
    hi -= 1;
  }

  t.push(
    { values: [...arr], marks: Object.fromEntries(arr.map((_, i) => [i, "good" as Tone])) },
    `Pointers crossed, so every pair has been swapped. Reversal done in place: O(n) time, O(1) extra space.`,
    { line: 7, phase: "answer" },
  );

  return capFrames(t.done(`[${arr.join(", ")}]`));
};

// ── 8. Dutch national flag / three-way partition (LC 75) ───────────────────

const DUTCH_CODE = [
  "def sort_colors(arr):",
  "    low, mid, high = 0, 0, len(arr) - 1",
  "    while mid <= high:",
  "        if arr[mid] == 0:",
  "            arr[low], arr[mid] = arr[mid], arr[low]",
  "            low += 1; mid += 1",
  "        elif arr[mid] == 1:",
  "            mid += 1",
  "        else:                      # == 2",
  "            arr[mid], arr[high] = arr[high], arr[mid]",
  "            high -= 1              # mid does NOT advance",
];

export const dutchFlag: ArrayAlgo = (input) => {
  const arr = nums(input).length ? [...nums(input)] : [2, 0, 2, 1, 1, 0];
  const t = tracer<ArrayState>(DUTCH_CODE);
  let low = 0;
  let mid = 0;
  let high = arr.length - 1;

  const state = (): ArrayState => ({
    values: [...arr],
    marks: (() => {
      const m: Record<number, Tone> = {};
      for (let i = 0; i < arr.length; i++) {
        if (i < low) m[i] = "good";
        else if (i > high) m[i] = "bad";
        else if (i === mid) m[i] = "active";
        else m[i] = "info";
      }
      return m;
    })(),
    pointers: [
      { name: "low", index: low, tone: "good" },
      { name: "mid", index: mid, tone: "active" },
      { name: "high", index: high, tone: "bad" },
    ],
    bands: [
      { from: 0, to: low - 1, label: "0s", tone: "good" },
      { from: low, to: high, label: "unknown", tone: "info" },
      { from: high + 1, to: arr.length - 1, label: "2s", tone: "bad" },
    ],
  });

  t.push(
    state(),
    `Three regions, one pass: everything left of low is 0, everything right of high is 2, and low..high is still unknown. The loop shrinks the unknown region to nothing.`,
    { line: 2, phase: "setup" },
  );

  while (mid <= high) {
    const v = arr[mid];
    if (v === 0) {
      t.push(state(), `arr[mid] is 0 — swap it into the 0s region and advance both low and mid.`, {
        line: 5,
        phase: "0",
        watch: [w("low", low, "good"), w("mid", mid, "active"), w("high", high, "bad")],
      });
      [arr[low], arr[mid]] = [arr[mid], arr[low]];
      low += 1;
      mid += 1;
    } else if (v === 1) {
      t.push(state(), `arr[mid] is 1 — already in the right region. Just advance mid.`, {
        line: 8,
        phase: "1",
        watch: [w("low", low, "good"), w("mid", mid, "active"), w("high", high, "bad")],
      });
      mid += 1;
    } else {
      t.push(
        state(),
        `arr[mid] is 2 — swap it to the 2s region and pull high left. mid deliberately does NOT advance: the value swapped in from the right has not been examined yet. Advancing here is the classic bug.`,
        { line: 10, phase: "2", watch: [w("low", low, "good"), w("mid", mid, "warn"), w("high", high, "bad")] },
      );
      [arr[mid], arr[high]] = [arr[high], arr[mid]];
      high -= 1;
    }
  }

  t.push(
    { values: [...arr], marks: Object.fromEntries(arr.map((_, i) => [i, "good" as Tone])) },
    `The unknown region is empty, so the array is sorted: one pass, O(n) time, O(1) space, and each element was moved at most twice.`,
    { line: 11, phase: "answer" },
  );

  return capFrames(t.done(`[${arr.join(", ")}]`));
};

// ── 9. Prefix sums ────────────────────────────────────────────────────────

const PREFIX_CODE = [
  "def prefix_sums(arr):",
  "    pre = [0] * (len(arr) + 1)",
  "    for i, v in enumerate(arr):",
  "        pre[i + 1] = pre[i] + v",
  "    return pre",
  "",
  "# range sum of arr[l..r] is pre[r + 1] - pre[l]  →  O(1)",
];

export const prefixSums: ArrayAlgo = (input) => {
  const arr = nums(input);
  const t = tracer<ArrayState>(PREFIX_CODE);
  const pre: number[] = [0];

  t.push(
    { values: arr, rows: [{ label: "pre", values: [...pre] }] },
    `pre[0] = 0 is the empty-prefix sentinel. Keeping it means the range formula never needs a special case for l = 0 — the single most common prefix-sum bug.`,
    { line: 2, phase: "setup" },
  );

  for (let i = 0; i < arr.length; i++) {
    pre.push(pre[i] + arr[i]);
    t.push(
      {
        values: arr,
        marks: { ...windowMarks(arr.length, 0, i), [i]: "active" },
        pointers: [{ name: "i", index: i, tone: "active" }],
        rows: [
          {
            label: "pre",
            values: [...pre],
            marks: { [i + 1]: "good", [i]: "info" },
          },
        ],
      },
      `pre[${i + 1}] = pre[${i}] + arr[${i}] = ${pre[i]} + ${arr[i]} = ${pre[i + 1]}. Note pre is one longer than arr and shifted by one.`,
      { line: 4, phase: "build", watch: [w("i", i), w(`pre[${i + 1}]`, pre[i + 1], "good")] },
    );
  }

  // Demonstrate a query.
  const l = Math.min(1, Math.max(0, arr.length - 1));
  const r = Math.max(l, arr.length - 2 >= l ? arr.length - 2 : l);
  const rangeSum = pre[r + 1] - pre[l];
  t.push(
    {
      values: arr,
      bands: [{ from: l, to: r, label: `sum ${rangeSum}`, tone: "good" }],
      marks: windowMarks(arr.length, l, r),
      rows: [{ label: "pre", values: [...pre], marks: { [l]: "bad", [r + 1]: "good" } }],
    },
    `Any range is now O(1): sum(arr[${l}..${r}]) = pre[${r + 1}] − pre[${l}] = ${pre[r + 1]} − ${pre[l]} = ${rangeSum}. Building cost O(n) once buys unlimited O(1) queries.`,
    { line: 7, phase: "query", watch: [w("l", l), w("r", r), w("sum", rangeSum, "good")] },
  );

  return capFrames(t.done(`pre = [${pre.join(", ")}]`));
};

// ── 10. Kadane's algorithm (LC 53) ────────────────────────────────────────

const KADANE_CODE = [
  "def max_subarray(arr):",
  "    best = cur = arr[0]",
  "    for v in arr[1:]:",
  "        cur = max(v, cur + v)   # extend, or restart at v",
  "        best = max(best, cur)",
  "    return best",
];

export const kadane: ArrayAlgo = (input) => {
  const arr = nums(input);
  const t = tracer<ArrayState>(KADANE_CODE);
  if (arr.length === 0) return t.done("empty input");

  let cur = arr[0];
  let best = arr[0];
  let start = 0;
  let bestLo = 0;
  let bestHi = 0;

  t.push(
    {
      values: arr,
      marks: { [0]: "good" },
      bands: [{ from: 0, to: 0, label: `cur ${cur}`, tone: "active" }],
      pointers: [{ name: "i", index: 0, tone: "active" }],
    },
    `Seed with the first element. Kadane's asks one question per step: is it better to extend the run I am on, or throw it away and start fresh here?`,
    { line: 2, phase: "seed", watch: [w("cur", cur, "active"), w("best", best, "good")] },
  );

  for (let i = 1; i < arr.length; i++) {
    const extend = cur + arr[i];
    const restart = arr[i];
    const restarted = restart > extend;
    if (restarted) start = i;
    cur = Math.max(restart, extend);
    const improved = cur > best;
    if (improved) {
      best = cur;
      bestLo = start;
      bestHi = i;
    }

    t.push(
      {
        values: arr,
        marks: { ...windowMarks(arr.length, start, i), [i]: restarted ? "warn" : "active" },
        bands: [{ from: start, to: i, label: `cur ${cur}`, tone: improved ? "good" : restarted ? "warn" : "active" }],
        pointers: [{ name: "i", index: i, tone: "active" }],
      },
      restarted
        ? `Extending would give ${extend}, but starting over at ${arr[i]} gives ${restart}. The run so far was dragging the total down, so drop it and restart here.`
        : `Extending gives ${extend}, better than restarting at ${arr[i]}. Keep the run alive.${improved ? ` That is also a new best of ${best}.` : ""}`,
      {
        line: 4,
        phase: restarted ? "restart" : "extend",
        watch: [w("extend", extend, restarted ? "bad" : "good"), w("restart", restart, restarted ? "good" : "bad"), w("cur", cur, "active"), w("best", best, "good")],
      },
    );
  }

  t.push(
    {
      values: arr,
      bands: [{ from: bestLo, to: bestHi, label: `sum ${best}`, tone: "good" }],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < arr.length; i++) m[i] = i >= bestLo && i <= bestHi ? "good" : "muted";
        return m;
      })(),
    },
    `Maximum subarray sum is ${best}, from index ${bestLo} to ${bestHi}. One pass, O(1) memory — and unlike a sliding window this works with negative numbers.`,
    { line: 6, phase: "answer", watch: [w("best", best, "good")] },
  );

  return capFrames(t.done(`max subarray sum = ${best} (indices ${bestLo}..${bestHi})`));
};

// ── 11. Cyclic sort (values 1..n) ─────────────────────────────────────────

const CYCLIC_CODE = [
  "def cyclic_sort(arr):",
  "    i = 0",
  "    while i < len(arr):",
  "        home = arr[i] - 1          # value v belongs at index v-1",
  "        if arr[i] != arr[home]:",
  "            arr[i], arr[home] = arr[home], arr[i]",
  "        else:",
  "            i += 1",
  "    return arr",
];

export const cyclicSort: ArrayAlgo = (input) => {
  const arr = nums(input).length ? [...nums(input)] : [3, 1, 5, 4, 2];
  const t = tracer<ArrayState>(CYCLIC_CODE);
  let i = 0;

  const state = (home?: number): ArrayState => ({
    values: [...arr],
    marks: (() => {
      const m: Record<number, Tone> = {};
      for (let j = 0; j < arr.length; j++) {
        if (arr[j] === j + 1) m[j] = "good";
        else if (j === i) m[j] = "active";
        else if (j === home) m[j] = "warn";
        else m[j] = "info";
      }
      return m;
    })(),
    pointers:
      home !== undefined && home !== i
        ? [{ name: "i", index: i, tone: "active" }, { name: "home", index: home, tone: "warn" }]
        : [{ name: "i", index: i, tone: "active" }],
  });

  t.push(
    state(),
    `Cyclic sort exploits a promise the problem makes: the values are exactly 1..n. That means value v has one correct home — index v − 1 — so sorting needs no comparisons, just placement.`,
    { line: 2, phase: "setup" },
  );

  let guard = 0;
  while (i < arr.length && guard++ < 4 * arr.length) {
    const home = arr[i] - 1;
    if (arr[i] !== arr[home]) {
      t.push(
        state(home),
        `arr[${i}] = ${arr[i]}, which belongs at index ${home}. Swap it home. i does not advance — whatever lands at ${i} still needs checking.`,
        { line: 6, phase: "swap", watch: [w("i", i), w("value", arr[i], "active"), w("home", home, "warn")] },
      );
      [arr[i], arr[home]] = [arr[home], arr[i]];
    } else {
      t.push(
        state(home),
        `arr[${i}] = ${arr[i]} is already home (or its home already holds the same value). Move i forward.`,
        { line: 8, phase: "advance", watch: [w("i", `${i} → ${i + 1}`, "good")] },
      );
      i += 1;
    }
  }

  t.push(
    { values: [...arr], marks: Object.fromEntries(arr.map((_, j) => [j, "good" as Tone])) },
    `Sorted in O(n): each swap puts at least one value in its permanent home, so there are at most n swaps total. This is the pattern behind "find the missing / duplicate number in 1..n".`,
    { line: 9, phase: "answer" },
  );

  return capFrames(t.done(`[${arr.join(", ")}]`));
};

// ── 12. Remove duplicates from sorted array (LC 26) — slow/fast writer ─────

const DEDUPE_CODE = [
  "def remove_duplicates(arr):",
  "    write = 1",
  "    for read in range(1, len(arr)):",
  "        if arr[read] != arr[write - 1]:",
  "            arr[write] = arr[read]",
  "            write += 1",
  "    return write        # new logical length",
];

export const removeDuplicates: ArrayAlgo = (input) => {
  const arr = nums(input).length ? [...nums(input)] : [0, 0, 1, 1, 1, 2, 2, 3];
  const t = tracer<ArrayState>(DEDUPE_CODE);
  let write = 1;

  t.push(
    {
      values: [...arr],
      pointers: [{ name: "write", index: write, tone: "good" }, { name: "read", index: 1, tone: "active" }],
      marks: { [0]: "good" },
    },
    `Two indices over one array: read scans everything, write marks where the next kept value goes. The first element is always kept, so write starts at 1.`,
    { line: 2, phase: "setup" },
  );

  for (let read = 1; read < arr.length; read++) {
    const isNew = arr[read] !== arr[write - 1];
    t.push(
      {
        values: [...arr],
        pointers: [{ name: "write", index: write, tone: "good" }, { name: "read", index: read, tone: "active" }],
        marks: (() => {
          const m: Record<number, Tone> = {};
          for (let j = 0; j < arr.length; j++) m[j] = j < write ? "good" : j === read ? (isNew ? "active" : "bad") : "muted";
          return m;
        })(),
        bands: [{ from: 0, to: write - 1, label: "kept", tone: "good" }],
      },
      isNew
        ? `arr[${read}] = ${arr[read]} differs from the last kept value ${arr[write - 1]}, so keep it: copy to index ${write}.`
        : `arr[${read}] = ${arr[read]} equals the last kept value, so it is a duplicate. Skip it — write stays put.`,
      {
        line: isNew ? 5 : 4,
        phase: isNew ? "keep" : "skip",
        watch: [w("read", `${read} → ${arr[read]}`, "active"), w("lastKept", arr[write - 1], "good"), w("write", write)],
      },
    );
    if (isNew) {
      arr[write] = arr[read];
      write += 1;
    }
  }

  t.push(
    {
      values: [...arr],
      bands: [
        { from: 0, to: write - 1, label: `length ${write}`, tone: "good" },
        { from: write, to: arr.length - 1, label: "garbage", tone: "muted" },
      ],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let j = 0; j < arr.length; j++) m[j] = j < write ? "good" : "muted";
        return m;
      })(),
    },
    `The first ${write} slots hold the distinct values. Everything past index ${write - 1} is leftover garbage the caller must ignore — the function returns a length, not a shorter array.`,
    { line: 7, phase: "answer", watch: [w("length", write, "good")] },
  );

  return capFrames(t.done(`k = ${write}, arr[:k] = [${arr.slice(0, write).join(", ")}]`));
};

// ── 13. Container with most water (LC 11) ─────────────────────────────────

const WATER_CODE = [
  "def max_area(h):",
  "    lo, hi, best = 0, len(h) - 1, 0",
  "    while lo < hi:",
  "        best = max(best, (hi - lo) * min(h[lo], h[hi]))",
  "        if h[lo] < h[hi]: lo += 1     # move the shorter wall",
  "        else:             hi -= 1",
  "    return best",
];

export const containerWater: ArrayAlgo = (input) => {
  const h = nums(input).length ? nums(input) : [1, 8, 6, 2, 5, 4, 8, 3, 7];
  const t = tracer<ArrayState>(WATER_CODE);
  let lo = 0;
  let hi = h.length - 1;
  let best = 0;
  let bestPair: [number, number] = [0, h.length - 1];

  while (lo < hi) {
    const area = (hi - lo) * Math.min(h[lo], h[hi]);
    const improved = area > best;
    if (improved) {
      best = area;
      bestPair = [lo, hi];
    }
    const moveLo = h[lo] < h[hi];
    t.push(
      {
        values: h,
        bands: [{ from: lo, to: hi, label: `area ${area}`, tone: improved ? "good" : "active" }],
        marks: {
          ...windowMarks(h.length, lo, hi),
          [lo]: moveLo ? "bad" : "good",
          [hi]: moveLo ? "good" : "bad",
        },
        pointers: [
          { name: "lo", index: lo, tone: moveLo ? "bad" : "info" },
          { name: "hi", index: hi, tone: moveLo ? "info" : "bad" },
        ],
      },
      `Width ${hi - lo} × shorter wall ${Math.min(h[lo], h[hi])} = ${area}.${improved ? " New best." : ""} Move the ${moveLo ? "left" : "right"} wall inward, because it is the shorter one — keeping it can never help: width only shrinks from here, and the shorter wall caps the height.`,
      {
        line: moveLo ? 5 : 6,
        phase: "narrow",
        watch: [w("width", hi - lo), w("height", Math.min(h[lo], h[hi])), w("area", area, improved ? "good" : "active"), w("best", best, "good")],
      },
    );
    if (moveLo) lo += 1;
    else hi -= 1;
  }

  t.push(
    {
      values: h,
      bands: [{ from: bestPair[0], to: bestPair[1], label: `best ${best}`, tone: "good" }],
      marks: (() => {
        const m: Record<number, Tone> = {};
        for (let i = 0; i < h.length; i++) m[i] = i === bestPair[0] || i === bestPair[1] ? "good" : "muted";
        return m;
      })(),
    },
    `Largest container holds ${best}, between indices ${bestPair[0]} and ${bestPair[1]}. The greedy move is safe because discarding the shorter wall can only discard pairs that were already dominated.`,
    { line: 7, phase: "answer", watch: [w("best", best, "good")] },
  );

  return capFrames(t.done(`max area = ${best}`));
};

// ── 14. Trapping rain water, two-pointer (LC 42) ──────────────────────────

const RAIN_CODE = [
  "def trap(h):",
  "    lo, hi = 0, len(h) - 1",
  "    left_max = right_max = water = 0",
  "    while lo < hi:",
  "        if h[lo] <= h[hi]:",
  "            left_max = max(left_max, h[lo])",
  "            water += left_max - h[lo]",
  "            lo += 1",
  "        else:",
  "            right_max = max(right_max, h[hi])",
  "            water += right_max - h[hi]",
  "            hi -= 1",
  "    return water",
];

export const trappingRain: ArrayAlgo = (input) => {
  const h = nums(input).length ? nums(input) : [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1];
  const t = tracer<ArrayState>(RAIN_CODE);
  let lo = 0;
  let hi = h.length - 1;
  let leftMax = 0;
  let rightMax = 0;
  let water = 0;

  t.push(
    {
      values: h,
      pointers: [{ name: "lo", index: lo, tone: "info" }, { name: "hi", index: hi, tone: "active" }],
    },
    `Water above a bar equals min(tallest to its left, tallest to its right) − its own height. The two-pointer trick: whichever side has the shorter bar is the side whose answer is already determined, so it is safe to settle that side now.`,
    { line: 3, phase: "setup" },
  );

  while (lo < hi) {
    if (h[lo] <= h[hi]) {
      leftMax = Math.max(leftMax, h[lo]);
      const add = leftMax - h[lo];
      water += add;
      t.push(
        {
          values: h,
          marks: { ...windowMarks(h.length, lo, hi), [lo]: add > 0 ? "good" : "info", [hi]: "muted" },
          pointers: [{ name: "lo", index: lo, tone: "active" }, { name: "hi", index: hi, tone: "muted" }],
        },
        `h[lo] = ${h[lo]} ≤ h[hi] = ${h[hi]}, so the left bar is the binding constraint. leftMax is ${leftMax}, so this column holds ${add} unit${add === 1 ? "" : "s"} of water. Advance lo.`,
        { line: 7, phase: "left", watch: [w("leftMax", leftMax, "good"), w("+water", add, add ? "good" : "muted"), w("water", water, "active")] },
      );
      lo += 1;
    } else {
      rightMax = Math.max(rightMax, h[hi]);
      const add = rightMax - h[hi];
      water += add;
      t.push(
        {
          values: h,
          marks: { ...windowMarks(h.length, lo, hi), [hi]: add > 0 ? "good" : "info", [lo]: "muted" },
          pointers: [{ name: "lo", index: lo, tone: "muted" }, { name: "hi", index: hi, tone: "active" }],
        },
        `h[hi] = ${h[hi]} < h[lo] = ${h[lo]}, so the right bar binds. rightMax is ${rightMax}, giving ${add} unit${add === 1 ? "" : "s"} of water here. Pull hi left.`,
        { line: 11, phase: "right", watch: [w("rightMax", rightMax, "good"), w("+water", add, add ? "good" : "muted"), w("water", water, "active")] },
      );
      hi -= 1;
    }
  }

  t.push(
    { values: h, marks: Object.fromEntries(h.map((_, i) => [i, "muted" as Tone])) },
    `Total trapped water: ${water}. One pass, O(1) space — no prefix-max arrays required.`,
    { line: 13, phase: "answer", watch: [w("water", water, "good")] },
  );

  return capFrames(t.done(`trapped water = ${water}`));
};

// ── 15. Subarray sum equals K, prefix sum + hash map (LC 560) ─────────────

const SUBARRAY_K_CODE = [
  "def subarray_sum(arr, k):",
  "    seen = {0: 1}      # prefix sum -> how many times seen",
  "    running = count = 0",
  "    for v in arr:",
  "        running += v",
  "        count += seen.get(running - k, 0)",
  "        seen[running] = seen.get(running, 0) + 1",
  "    return count",
];

export const subarraySumK: ArrayAlgo = (input) => {
  const arr = nums(input).length ? nums(input) : [1, 2, 3, -3, 1, 1, 1];
  const k = input.target ?? input.k ?? 3;
  const t = tracer<ArrayState>(SUBARRAY_K_CODE);

  const seen = new Map<number, number>([[0, 1]]);
  let running = 0;
  let count = 0;

  const chips = (focus?: number) =>
    [...seen.entries()].map(([s, n]) => ({
      label: String(s),
      value: `×${n}`,
      tone: (s === focus ? "good" : "muted") as Tone,
    }));

  t.push(
    { values: arr, chips: chips() },
    `Seed the map with {0: 1}. That sentinel represents the empty prefix and is what lets a subarray starting at index 0 be counted — forgetting it is the classic off-by-one here.`,
    { line: 2, phase: "setup", watch: [w("k", k)] },
  );

  for (let i = 0; i < arr.length; i++) {
    running += arr[i];
    const want = running - k;
    const hits = seen.get(want) ?? 0;
    count += hits;
    t.push(
      {
        values: arr,
        marks: { ...windowMarks(arr.length, 0, i), [i]: hits > 0 ? "good" : "active" },
        pointers: [{ name: "i", index: i, tone: "active" }],
        chips: chips(want),
        rows: [{ label: "running", values: arr.map((_, j) => (j <= i ? arr.slice(0, j + 1).reduce((a, b) => a + b, 0) : "·")) }],
      },
      hits > 0
        ? `Running sum is ${running}. A subarray ending here sums to ${k} exactly when some earlier prefix summed to ${want} — and ${want} has been seen ${hits} time${hits === 1 ? "" : "s"}. Add ${hits} to the count.`
        : `Running sum is ${running}. No earlier prefix equals ${want}, so no subarray ending at index ${i} sums to ${k}.`,
      {
        line: 6,
        phase: "scan",
        watch: [w("running", running, "active"), w("running−k", want, hits ? "good" : "muted"), w("hits", hits, hits ? "good" : "muted"), w("count", count, "good")],
      },
    );
    seen.set(running, (seen.get(running) ?? 0) + 1);
  }

  t.push(
    { values: arr, chips: chips(), marks: Object.fromEntries(arr.map((_, i) => [i, "muted" as Tone])) },
    `${count} subarray${count === 1 ? "" : "s"} sum to ${k}. This is the pattern to reach for when a sliding window would be wrong — negative numbers break window monotonicity, but prefix sums do not care about sign.`,
    { line: 8, phase: "answer", watch: [w("count", count, "good")] },
  );

  return capFrames(t.done(`${count} subarrays sum to ${k}`));
};

/**
 * Registry. The `algo` prop of <ArrayStepper> indexes this.
 *
 * | key                   | uses                        |
 * |-----------------------|-----------------------------|
 * | fixed-window          | values, k                   |
 * | variable-window-sum   | values, target              |
 * | longest-unique        | text                        |
 * | char-replacement      | text, k                     |
 * | min-window            | text, pattern               |
 * | two-sum-sorted        | values, target              |
 * | reverse-in-place      | values or text              |
 * | dutch-flag            | values (0/1/2)              |
 * | prefix-sums           | values                      |
 * | kadane                | values                      |
 * | cyclic-sort           | values (a permutation 1..n) |
 * | remove-duplicates     | values (sorted)             |
 * | container-water       | values (heights)            |
 * | trapping-rain         | values (heights)            |
 * | subarray-sum-k        | values, target              |
 */
export const ALGOS: Record<string, ArrayAlgo> = {
  "fixed-window": fixedWindow,
  "variable-window-sum": variableWindowSum,
  "longest-unique": longestUnique,
  "char-replacement": charReplacement,
  "min-window": minWindow,
  "two-sum-sorted": twoSumSorted,
  "reverse-in-place": reverseInPlace,
  "dutch-flag": dutchFlag,
  "prefix-sums": prefixSums,
  kadane: kadane,
  "cyclic-sort": cyclicSort,
  "remove-duplicates": removeDuplicates,
  "container-water": containerWater,
  "trapping-rain": trappingRain,
  "subarray-sum-k": subarraySumK,
  // Sorts and binary searches speak the same ArrayState, so they live in the
  // same registry rather than getting components of their own. See ./sorting.ts
  // for the eight extra keys this adds.
  ...SORT_ALGOS,
  // A machine word is an array of bits, so bit manipulation reuses the same
  // renderer too — pass tag="bits". See ./bits.ts.
  ...BIT_ALGOS,
  // String patterns whose state is "a row plus a frequency map" — the chips in
  // ArrayState are exactly that. See ./strings.ts.
  ...STRING_ALGOS,
  // Three traces added for pages whose subject no existing algorithm showed:
  // a greedy reachability frontier, comparator-key selection, and a sieve.
  // See ./frontier.ts.
  ...FRONTIER_ALGOS,
  // Composition traces for the Phase-14 design problems: an LRU recency order and
  // the array+index-map swap-remove. See ./design.ts.
  ...DESIGN_ALGOS,
};

export type ArrayAlgoName = keyof typeof ALGOS;

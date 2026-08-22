/**
 * algos/strings.ts — string-pattern algorithms, in the ArrayState shape.
 *
 * Three patterns that Phase 05 teaches and had no visualization for. All three
 * are "a row of cells plus some chips", so they reuse `<ArrayStepper>` rather
 * than getting components of their own.
 *
 * The chips are doing real work here: in anagram counting the frequency map *is*
 * the algorithm's state, and watching it reach zero everywhere is what makes the
 * "compare the maps" step concrete.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { ArrayAlgo, ArrayInput, ArrayState } from "./arrays";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ── 1. Find all anagrams of a pattern (LC 438) ────────────────────────────

const ANAGRAM_CODE = [
  "def find_anagrams(s, p):",
  "    need = Counter(p)",
  "    window = Counter()",
  "    out, k = [], len(p)",
  "    for i, ch in enumerate(s):",
  "        window[ch] += 1",
  "        if i >= k:",
  "            left = s[i - k]",
  "            window[left] -= 1",
  "            if window[left] == 0: del window[left]   # keep maps comparable",
  "        if window == need:",
  "            out.append(i - k + 1)",
  "    return out",
];

export const anagramWindow: ArrayAlgo = (input) => {
  const s = [...(input.text ?? "cbaebabacd")];
  const pat = [...(input.pattern ?? "abc")];
  const k = pat.length;
  const t = tracer<ArrayState>(ANAGRAM_CODE);

  const need = new Map<string, number>();
  for (const c of pat) need.set(c, (need.get(c) ?? 0) + 1);
  const win = new Map<string, number>();
  const hits: number[] = [];

  /** Chips show the window map against what is needed, per character. */
  const chips = () =>
    [...new Set([...need.keys(), ...win.keys()])].sort().map((c) => {
      const have = win.get(c) ?? 0;
      const want = need.get(c) ?? 0;
      return {
        label: c,
        value: `${have}/${want}`,
        tone: (have === want ? "good" : have > want ? "bad" : "warn") as Tone,
      };
    });

  const state = (right: number, matched = false): ArrayState => {
    const left = Math.max(0, right - k + 1);
    return {
      values: s,
      bands: right >= k - 1 ? [{ from: left, to: right, label: matched ? "anagram!" : `${k} wide`, tone: matched ? "good" : "active" }] : [],
      marks: Object.fromEntries(
        s.map((_, i) => [i, (i > right ? "info" : i >= left && right >= k - 1 ? (matched ? "good" : "active") : "muted") as Tone]),
      ),
      pointers: [{ name: "right", index: right, tone: "active" }],
      chips: chips(),
    };
  };

  t.push(
    { values: s, chips: chips() },
    `An anagram is a multiset, not an ordering — so the question "is this window an anagram of the pattern" is really "do these two frequency maps match". A fixed-width window of ${k} slides once across the string, and each step changes exactly two counts.`,
    { line: 4, phase: "setup", watch: [w("pattern", pat.join(""), "warn"), w("k", k)] },
  );

  for (let i = 0; i < s.length; i++) {
    win.set(s[i], (win.get(s[i]) ?? 0) + 1);

    if (i >= k) {
      const out = s[i - k];
      win.set(out, win.get(out)! - 1);
      // Deleting the zero entry matters: two Counters with different key sets are
      // unequal in Python even when every count agrees.
      if (win.get(out) === 0) win.delete(out);
      t.push(
        state(i),
        `'${s[i]}' enters and '${out}' leaves. Note the delete when a count hits zero — in Python a Counter with an extra zero-valued key is *not* equal to one without it, so skipping the delete makes the comparison silently fail.`,
        { line: 10, phase: "slide", watch: [w("in", s[i], "good"), w("out", out, "bad")] },
      );
    } else {
      t.push(
        state(i),
        i < k - 1
          ? `Filling the window: '${s[i]}' enters, ${k - 1 - i} more to go before the first comparison.`
          : `Window is now ${k} wide for the first time — ready to compare.`,
        { line: 6, phase: "fill", watch: [w("in", s[i], "good"), w("width", i + 1)] },
      );
    }

    if (i >= k - 1) {
      const same =
        win.size === need.size && [...need].every(([c, n]) => win.get(c) === n);
      if (same) hits.push(i - k + 1);
      t.push(
        state(i, same),
        same
          ? `Every count matches, so "${s.slice(i - k + 1, i + 1).join("")}" is an anagram of "${pat.join("")}" — record start index ${i - k + 1}.`
          : `The maps differ, so this window is not an anagram. Comparing whole maps is $O(26)$, which is $O(1)$ — that is what keeps the whole scan linear.`,
        {
          line: same ? 12 : 11,
          phase: same ? "match" : "compare",
          watch: [w("window", s.slice(i - k + 1, i + 1).join(""), same ? "good" : "active"), w("found", hits.length, "good")],
        },
      );
    }
  }

  t.push(
    { values: s, marks: Object.fromEntries(s.map((_, i) => [i, "muted" as Tone])), chips: chips() },
    `Anagram start indices: ${hits.length ? hits.join(", ") : "none"}. $O(n)$ time and $O(1)$ space (at most 26 keys). A tempting alternative — sort each window and compare strings — costs $O(n \\cdot k \\log k)$ and is the answer to avoid.`,
    { line: 13, phase: "answer", watch: [w("indices", hits.join(",") || "none", "good")] },
  );

  return capFrames(t.done(`anagrams start at [${hits.join(", ")}]`));
};

// ── 2. Longest palindromic substring — expand around centre (LC 5) ────────

const PALINDROME_CODE = [
  "def longest_palindrome(s):",
  "    best = (0, 0)",
  "    for c in range(len(s)):",
  "        for lo, hi in ((c, c), (c, c + 1)):     # odd, then even",
  "            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:",
  "                lo -= 1; hi += 1",
  "            lo, hi = lo + 1, hi - 1             # step back inside",
  "            if hi - lo > best[1] - best[0]:",
  "                best = (lo, hi)",
  "    return s[best[0]:best[1] + 1]",
];

export const expandAroundCentre: ArrayAlgo = (input) => {
  const s = [...(input.text ?? "babad")];
  const t = tracer<ArrayState>(PALINDROME_CODE);

  let bestLo = 0;
  let bestHi = 0;

  const state = (lo: number, hi: number, centre: string, tone: Tone): ArrayState => ({
    values: s,
    bands: hi >= lo ? [{ from: Math.max(0, lo), to: Math.min(s.length - 1, hi), label: centre, tone }] : [],
    marks: Object.fromEntries(
      s.map((_, i) => [
        i,
        (i >= bestLo && i <= bestHi ? "good" : i >= lo && i <= hi ? tone : "muted") as Tone,
      ]),
    ),
    pointers: [
      ...(lo >= 0 ? [{ name: "lo", index: lo, tone }] : []),
      ...(hi < s.length ? [{ name: "hi", index: hi, tone }] : []),
    ],
  });

  t.push(
    { values: s },
    `A palindrome is defined by its **centre**, and there are only $2n - 1$ centres: $n$ single characters (odd lengths) and $n - 1$ gaps between characters (even lengths). Checking every substring is $O(n^3)$; expanding from every centre is $O(n^2)$ with no extra memory.`,
    { line: 3, phase: "setup", watch: [w("centres", 2 * s.length - 1, "info")] },
  );

  for (let c = 0; c < s.length; c++) {
    for (const [startLo, startHi, kind] of [
      [c, c, "odd"],
      [c, c + 1, "even"],
    ] as [number, number, string][]) {
      let lo = startLo;
      let hi = startHi;

      if (hi >= s.length || s[lo] !== s[hi]) {
        t.push(
          state(startLo, Math.min(startHi, s.length - 1), `${kind} centre`, "bad"),
          hi >= s.length
            ? `No ${kind} centre exists at index ${c} — it would run past the end.`
            : `${kind} centre at ${c}: '${s[lo]}' ≠ '${s[hi]}', so nothing expands from here. Both centres must be tried at every index; checking only odd lengths misses "abba" entirely.`,
          { line: 5, phase: kind, watch: [w("centre", c), w("kind", kind, "bad")] },
        );
        continue;
      }

      while (lo >= 0 && hi < s.length && s[lo] === s[hi]) {
        t.push(
          state(lo, hi, `"${s.slice(lo, hi + 1).join("")}"`, "active"),
          `'${s[lo]}' == '${s[hi]}', so "${s.slice(lo, hi + 1).join("")}" is a palindrome. Expand outward.`,
          {
            line: 6,
            phase: kind,
            watch: [w("lo", lo), w("hi", hi), w("length", hi - lo + 1, "active")],
          },
        );
        lo -= 1;
        hi += 1;
      }
      lo += 1;
      hi -= 1;

      const improved = hi - lo > bestHi - bestLo;
      if (improved) {
        bestLo = lo;
        bestHi = hi;
      }

      t.push(
        state(lo, hi, `len ${hi - lo + 1}`, improved ? "good" : "warn"),
        `Expansion stopped. Step back inside the failed comparison — that ±1 is the off-by-one everyone hits — leaving "${s.slice(lo, hi + 1).join("")}", length ${hi - lo + 1}.${improved ? " New best." : ""}`,
        {
          line: 7,
          phase: kind,
          watch: [w("palindrome", s.slice(lo, hi + 1).join(""), improved ? "good" : "muted"), w("best", s.slice(bestLo, bestHi + 1).join(""), "good")],
        },
      );
    }
  }

  t.push(
    {
      values: s,
      bands: [{ from: bestLo, to: bestHi, label: "longest", tone: "good" }],
      marks: Object.fromEntries(s.map((_, i) => [i, (i >= bestLo && i <= bestHi ? "good" : "muted") as Tone])),
    },
    `Longest palindromic substring is "${s.slice(bestLo, bestHi + 1).join("")}". $O(n^2)$ time, $O(1)$ space. Manacher's algorithm does it in $O(n)$ but is rarely expected — knowing it exists and naming it is usually enough.`,
    { line: 10, phase: "answer", watch: [w("answer", s.slice(bestLo, bestHi + 1).join(""), "good")] },
  );

  return capFrames(t.done(`longest palindrome = "${s.slice(bestLo, bestHi + 1).join("")}"`));
};

// ── 3. Sliding window maximum — monotonic deque (LC 239) ──────────────────

const DEQUE_CODE = [
  "from collections import deque",
  "",
  "def max_sliding_window(nums, k):",
  "    dq = deque()          # INDICES, values decreasing front to back",
  "    out = []",
  "    for i, v in enumerate(nums):",
  "        if dq and dq[0] <= i - k:",
  "            dq.popleft()          # front fell out of the window",
  "        while dq and nums[dq[-1]] <= v:",
  "            dq.pop()              # back can never be the max again",
  "        dq.append(i)",
  "        if i >= k - 1:",
  "            out.append(nums[dq[0]])   # front IS the window max",
  "    return out",
];

export const slidingWindowMax: ArrayAlgo = (input) => {
  const a = input.values?.length ? input.values : [1, 3, -1, -3, 5, 3, 6, 7];
  const k = Math.max(1, Math.min(input.k ?? 3, a.length));
  const t = tracer<ArrayState>(DEQUE_CODE);

  const dq: number[] = [];
  const out: number[] = [];

  const state = (i: number, band: Tone = "active"): ArrayState => ({
    values: a,
    bands: i >= k - 1 ? [{ from: i - k + 1, to: i, label: `k = ${k}`, tone: band }] : [],
    marks: Object.fromEntries(
      a.map((_, j) => [
        j,
        (j > i
          ? "info"
          : dq.length && j === dq[0]
            ? "good"
            : dq.includes(j)
              ? "warn"
              : j >= i - k + 1
                ? "active"
                : "muted") as Tone,
      ]),
    ),
    pointers: [{ name: "i", index: i, tone: "active" }],
    chips: dq.map((j, idx) => ({
      label: idx === 0 ? "front" : idx === dq.length - 1 ? "back" : `·`,
      value: `${a[j]}@${j}`,
      tone: (idx === 0 ? "good" : "warn") as Tone,
    })),
    rows: [
      {
        label: "maxes",
        values: a.map((_, j) => (j >= k - 1 && j - k + 1 < out.length ? out[j - k + 1] : "·")),
        marks: Object.fromEntries(a.map((_, j) => [j, (j >= k - 1 && j - k + 1 < out.length ? "good" : "muted") as Tone])),
      },
    ],
  });

  t.push(
    { values: a },
    `A monotonic **deque**, not a stack — because entries can leave from *both* ends. The back is popped when a bigger value arrives (it can never be a maximum again); the front is popped when it slides out of the window. That two-sided eviction is exactly what a stack cannot do.`,
    { line: 4, phase: "setup", watch: [w("k", k, "info")] },
  );

  for (let i = 0; i < a.length; i++) {
    if (dq.length && dq[0] <= i - k) {
      const gone = dq.shift()!;
      t.push(
        state(i, "warn"),
        `Index ${gone} is now outside the window [${i - k + 1}..${i}], so drop it from the **front**. This is the check a plain monotonic stack has no answer for.`,
        { line: 8, phase: "evict front", watch: [w("dropped", `${a[gone]}@${gone}`, "bad")] },
      );
    }

    const popped: number[] = [];
    while (dq.length && a[dq[dq.length - 1]] <= a[i]) popped.push(dq.pop()!);

    if (popped.length) {
      t.push(
        state(i),
        `${a[i]} arrives and is at least as large as ${popped.map((j) => a[j]).join(", ")} sitting at the back. Those can never be the maximum of any future window — ${a[i]} is both bigger *and* later — so pop them.`,
        { line: 10, phase: "evict back", watch: [w("value", a[i], "active"), w("popped", popped.map((j) => a[j]).join(","), "bad")] },
      );
    }

    dq.push(i);
    if (i >= k - 1) out.push(a[dq[0]]);

    t.push(
      state(i, "good"),
      i >= k - 1
        ? `Push index ${i}. The deque front is ${a[dq[0]]}, which is the maximum of window [${i - k + 1}..${i}] — read in $O(1)$, never recomputed.`
        : `Push index ${i}. The window is not yet ${k} wide, so nothing is recorded.`,
      {
        line: i >= k - 1 ? 13 : 11,
        phase: "record",
        watch: [w("deque", dq.map((j) => a[j]).join(","), "warn"), w("max", i >= k - 1 ? a[dq[0]] : "—", "good")],
      },
    );
  }

  t.push(
    { ...state(a.length - 1), bands: [], pointers: [] },
    `Window maxima: ${out.join(", ")}. $O(n)$ — each index is appended once and removed once — and $O(k)$ space. A heap also solves this at $O(n \\log k)$ with lazy deletion; the deque is the $O(n)$ answer and the reason this problem is Hard rather than Medium.`,
    { line: 14, phase: "answer", watch: [w("result", out.join(","), "good")] },
  );

  return capFrames(t.done(`[${out.join(", ")}]`));
};

/**
 * Registry, merged into ALGOS by ./arrays.ts.
 *
 * | key                   | uses            |
 * |-----------------------|-----------------|
 * | anagram-window        | text, pattern   |
 * | expand-around-centre  | text            |
 * | sliding-window-max    | values, k       |
 */
// ── KMP prefix function (LC 28 / 1392 / 214) ─────────────────────────────

const KMP_CODE = [
  "def prefix_function(s):",
  "    pi = [0] * len(s)",
  "    k = 0                          # length of the current border",
  "    for i in range(1, len(s)):",
  "        while k and s[i] != s[k]:",
  "            k = pi[k - 1]          # fall back, never restart at 0",
  "        if s[i] == s[k]:",
  "            k += 1",
  "        pi[i] = k",
  "    return pi",
];

/**
 * `pi[i]` is the length of the longest proper prefix of `s[0..i]` that is also a
 * suffix of it. Two things are invisible in the code and drawn here: the fallback
 * `k = pi[k-1]` (which is why the scan never rewinds `i`), and the prefix table
 * filling in as a second row under the string.
 */
export const kmpPrefix: ArrayAlgo = (input) => {
  const s = (input.text && input.text.length ? input.text : "ababcabab").slice(0, 16);
  const t = tracer<ArrayState>(KMP_CODE);
  const pi = Array<number>(s.length).fill(0);
  let comparisons = 0;

  const state = (i: number, k: number, marks: Record<number, Tone> = {}): ArrayState => ({
    values: [...s],
    pointers: [
      { name: "k", index: k, tone: "warn" },
      { name: "i", index: i, tone: "active" },
    ],
    marks,
    rows: [{ label: "pi", values: pi.map((v, idx) => (idx <= i ? String(v) : "·")) }],
    chips: [{ label: "border", value: String(k), tone: k > 0 ? "good" : "muted" }],
  });

  t.push(
    state(0, 0, { 0: "muted" }),
    `\`pi[i]\` is the length of the longest proper prefix of \`s[0..i]\` that is also a **suffix** of it — its longest *border*. \`pi[0]\` is always 0, because a single character has no proper prefix. The whole point of the table is that on a mismatch you can resume from a border instead of restarting.`,
    { line: 2, phase: "seed", watch: [w("pi[0]", 0), w("border", 0)] },
  );

  let k = 0;
  for (let i = 1; i < s.length; i++) {
    while (k > 0 && s[i] !== s[k]) {
      const from = k;
      k = pi[k - 1];
      comparisons++;
      t.push(
        state(i, k, { [i]: "bad" }),
        `Mismatch: \`s[${i}]\` is '${s[i]}' but \`s[${k === 0 ? from : from}]\` was '${s[from]}'. **Fall back** to \`pi[${from - 1}] = ${k}\` rather than resetting to 0 — everything matched so far still has a border of length ${k}, so that much of the prefix is already known to line up. \`i\` never moves backwards, which is why the whole build is O(n).`,
        { line: 6, phase: `i = ${i}`, watch: [w("i", i, "active"), w("fell back", `${from} → ${k}`, "bad")] },
      );
    }
    comparisons++;
    if (s[i] === s[k]) {
      k++;
      pi[i] = k;
      t.push(
        state(i, k, { [i]: "good" }),
        `\`s[${i}]\` = '${s[i]}' matches \`s[${k - 1}]\`, so the border grows to **${k}**: \`s[0..${k - 1}]\` is both a prefix and a suffix of \`s[0..${i}]\`. Record \`pi[${i}] = ${k}\`.`,
        { line: 8, phase: `i = ${i}`, watch: [w("i", i, "active"), w("border", k, "good"), w("pi[i]", k, "good")] },
      );
    } else {
      pi[i] = 0;
      t.push(
        state(i, 0, { [i]: "muted" }),
        `\`s[${i}]\` = '${s[i]}' does not match \`s[0]\` and the border was already 0, so there is nothing to fall back to: \`pi[${i}] = 0\`.`,
        { line: 9, phase: `i = ${i}`, watch: [w("i", i, "active"), w("pi[i]", 0, "muted")] },
      );
    }
  }

  t.push(
    state(s.length - 1, k),
    `Prefix table: [${pi.join(", ")}]. Built in ${comparisons} character comparisons for a string of length ${s.length} — **O(n)**, because \`i\` only ever advances and each fallback strictly decreases \`k\`, so the total fallback work is bounded by the total growth. Searching a text then reuses this table the same way: on a mismatch, fall back through the pattern instead of rewinding the text.`,
    { line: 10, phase: "done", watch: [w("comparisons", comparisons, "info"), w("n", s.length)] },
  );

  return capFrames(t.done(`pi = [${pi.join(", ")}]`));
};

export const STRING_ALGOS: Record<string, ArrayAlgo> = {
  "anagram-window": anagramWindow,
  "expand-around-centre": expandAroundCentre,
  "sliding-window-max": slidingWindowMax,
  "kmp-prefix": kmpPrefix,
};

/**
 * algos/dp.ts — traced dynamic-programming table fills for <DPTable>.
 *
 * DP is the topic where a step-through earns the most: the table is the answer,
 * the recurrence is one line, and the only hard part is *which earlier cells a
 * cell depends on*. Every algorithm here therefore reports its dependencies per
 * cell, and the renderer draws arrows from them — so "dp[i][j] = dp[i-1][j-1]+1"
 * stops being symbols and becomes a picture.
 *
 * AUTHORING FORMAT
 * ----------------
 *     <DPTable algo="lcs" a="ABCBDAB" b="BDCABA" />
 *     <DPTable algo="coin-change" values={[1, 3, 4]} target={6} />
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

/** One cell of the table. */
export interface DPCell {
  value: string | number;
  tone?: Tone;
}

export interface DPState {
  /** Row-major grid. `null` renders as an untouched cell. */
  grid: (DPCell | null)[][];
  /** Column headers — usually the characters of one input. */
  colLabels?: (string | number)[];
  /** Row headers. */
  rowLabels?: (string | number)[];
  /** Axis captions, e.g. "text b" / "text a". */
  colTitle?: string;
  rowTitle?: string;
  /** The cell being written this step. */
  cursor?: { r: number; c: number };
  /** Cells the cursor reads from — drawn as arrows into the cursor. */
  deps?: { r: number; c: number }[];
  /** Reconstructed answer path, highlighted after the fill completes. */
  path?: { r: number; c: number }[];
}

export interface DPInput {
  /** First string for two-string problems. */
  a?: string;
  /** Second string. */
  b?: string;
  /** Numeric input — coin denominations, item weights, the sequence for LIS. */
  values?: number[];
  /** Item values for 0/1 knapsack. */
  weights?: number[];
  /** Capacity / amount / target. */
  target?: number;
}

export type DPAlgo = (input: DPInput) => Trace<DPState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

/** Deep-copy a grid so each frame keeps its own immutable snapshot. */
const snap = (grid: (DPCell | null)[][]): (DPCell | null)[][] =>
  grid.map((row) => row.map((c) => (c ? { ...c } : null)));

// ── 1. Longest common subsequence (LC 1143) ───────────────────────────────

const LCS_CODE = [
  "def lcs(a, b):",
  "    m, n = len(a), len(b)",
  "    dp = [[0] * (n + 1) for _ in range(m + 1)]",
  "    for i in range(1, m + 1):",
  "        for j in range(1, n + 1):",
  "            if a[i - 1] == b[j - 1]:",
  "                dp[i][j] = dp[i - 1][j - 1] + 1     # diagonal + 1",
  "            else:",
  "                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])",
  "    return dp[m][n]",
];

export const lcs: DPAlgo = (input) => {
  const a = input.a ?? "ABCBDAB";
  const b = input.b ?? "BDCABA";
  const m = a.length;
  const n = b.length;
  const t = tracer<DPState>(LCS_CODE);

  const grid: (DPCell | null)[][] = Array.from({ length: m + 1 }, () =>
    Array.from({ length: n + 1 }, () => null),
  );
  for (let i = 0; i <= m; i++) grid[i][0] = { value: 0, tone: "muted" };
  for (let j = 0; j <= n; j++) grid[0][j] = { value: 0, tone: "muted" };

  const base = {
    colLabels: ["ε", ...b],
    rowLabels: ["ε", ...a],
    colTitle: `b = "${b}"`,
    rowTitle: `a = "${a}"`,
  };

  t.push(
    { grid: snap(grid), ...base },
    `Row 0 and column 0 are all zeros: the longest common subsequence with an empty string is empty. Those sentinels are why the loops can start at 1 and never test for out-of-range indices.`,
    { line: 3, phase: "base case" },
  );

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const match = a[i - 1] === b[j - 1];
      const deps = match
        ? [{ r: i - 1, c: j - 1 }]
        : [
            { r: i - 1, c: j },
            { r: i, c: j - 1 },
          ];

      // Show the read before the write so the dependency arrows are visible.
      const reading = snap(grid);
      for (const d of deps) if (reading[d.r][d.c]) reading[d.r][d.c]!.tone = "warn";
      t.push(
        { grid: reading, ...base, cursor: { r: i, c: j }, deps },
        match
          ? `a[${i - 1}] = '${a[i - 1]}' matches b[${j - 1}] = '${b[j - 1]}'. A match extends the best answer for the two shorter prefixes, so read the diagonal cell and add 1.`
          : `'${a[i - 1]}' ≠ '${b[j - 1]}'. One of the two characters has to be dropped, and we do not know which — so take the better of dropping a's character (cell above) or dropping b's (cell to the left).`,
        {
          line: match ? 7 : 9,
          phase: match ? "match" : "mismatch",
          watch: [
            w("a[i-1]", a[i - 1], match ? "good" : "bad"),
            w("b[j-1]", b[j - 1], match ? "good" : "bad"),
            ...deps.map((d) => w(`dp[${d.r}][${d.c}]`, grid[d.r][d.c]!.value as number, "warn")),
          ],
        },
      );

      const value = match
        ? (grid[i - 1][j - 1]!.value as number) + 1
        : Math.max(grid[i - 1][j]!.value as number, grid[i][j - 1]!.value as number);
      grid[i][j] = { value, tone: match ? "good" : "active" };

      t.push(
        { grid: snap(grid), ...base, cursor: { r: i, c: j } },
        `dp[${i}][${j}] = ${value} — the LCS length of "${a.slice(0, i)}" and "${b.slice(0, j)}".`,
        {
          line: match ? 7 : 9,
          phase: "write",
          watch: [w(`dp[${i}][${j}]`, value, "good")],
        },
      );
    }
  }

  // Reconstruct one optimal subsequence by walking back through the choices.
  const path: { r: number; c: number }[] = [];
  let ri = m;
  let cj = n;
  let sub = "";
  while (ri > 0 && cj > 0) {
    if (a[ri - 1] === b[cj - 1]) {
      path.push({ r: ri, c: cj });
      sub = a[ri - 1] + sub;
      ri -= 1;
      cj -= 1;
    } else if ((grid[ri - 1][cj]!.value as number) >= (grid[ri][cj - 1]!.value as number)) {
      ri -= 1;
    } else {
      cj -= 1;
    }
  }

  t.push(
    { grid: snap(grid), ...base, path },
    `dp[${m}][${n}] = ${grid[m][n]!.value} is the answer. Walking back from the bottom-right — diagonal on a match, otherwise toward the larger neighbour — recovers an actual subsequence: "${sub}". Cost is O(m·n) time and O(m·n) space, reducible to two rows if only the length is needed.`,
    { line: 10, phase: "answer", watch: [w("length", grid[m][n]!.value as number, "good"), w("subsequence", sub, "good")] },
  );

  return capFrames(t.done(`LCS("${a}", "${b}") = ${grid[m][n]!.value} → "${sub}"`));
};

// ── 2. Edit distance (LC 72) ─────────────────────────────────────────────

const EDIT_CODE = [
  "def edit_distance(a, b):",
  "    m, n = len(a), len(b)",
  "    dp = [[0] * (n + 1) for _ in range(m + 1)]",
  "    for i in range(m + 1): dp[i][0] = i     # delete everything",
  "    for j in range(n + 1): dp[0][j] = j     # insert everything",
  "    for i in range(1, m + 1):",
  "        for j in range(1, n + 1):",
  "            if a[i - 1] == b[j - 1]:",
  "                dp[i][j] = dp[i - 1][j - 1]          # free",
  "            else:",
  "                dp[i][j] = 1 + min(dp[i - 1][j - 1],  # replace",
  "                                   dp[i - 1][j],      # delete",
  "                                   dp[i][j - 1])      # insert",
  "    return dp[m][n]",
];

export const editDistance: DPAlgo = (input) => {
  const a = input.a ?? "horse";
  const b = input.b ?? "ros";
  const m = a.length;
  const n = b.length;
  const t = tracer<DPState>(EDIT_CODE);

  const grid: (DPCell | null)[][] = Array.from({ length: m + 1 }, () =>
    Array.from({ length: n + 1 }, () => null),
  );
  for (let i = 0; i <= m; i++) grid[i][0] = { value: i, tone: "muted" };
  for (let j = 0; j <= n; j++) grid[0][j] = { value: j, tone: "muted" };

  const base = {
    colLabels: ["ε", ...b],
    rowLabels: ["ε", ...a],
    colTitle: `to "${b}"`,
    rowTitle: `from "${a}"`,
  };

  t.push(
    { grid: snap(grid), ...base },
    `The edges are not zeros here. Turning a prefix of length i into the empty string costs i deletions, and the reverse costs j insertions — so row 0 and column 0 count up. Getting these wrong is the usual reason an edit-distance solution is off by a constant.`,
    { line: 5, phase: "base case" },
  );

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const match = a[i - 1] === b[j - 1];
      const deps = match
        ? [{ r: i - 1, c: j - 1 }]
        : [
            { r: i - 1, c: j - 1 },
            { r: i - 1, c: j },
            { r: i, c: j - 1 },
          ];

      const reading = snap(grid);
      for (const d of deps) if (reading[d.r][d.c]) reading[d.r][d.c]!.tone = "warn";
      const repl = grid[i - 1][j - 1]!.value as number;
      const del = grid[i - 1][j]!.value as number;
      const ins = grid[i][j - 1]!.value as number;

      t.push(
        { grid: reading, ...base, cursor: { r: i, c: j }, deps },
        match
          ? `'${a[i - 1]}' already matches '${b[j - 1]}', so this character costs nothing — inherit the diagonal unchanged.`
          : `'${a[i - 1]}' ≠ '${b[j - 1]}', so exactly one edit is needed and the only question is which: replace (diagonal, ${repl}), delete (above, ${del}), or insert (left, ${ins}). Take the cheapest and add 1.`,
        {
          line: match ? 9 : 11,
          phase: match ? "free" : "edit",
          watch: match
            ? [w("char", `${a[i - 1]}=${b[j - 1]}`, "good"), w("inherit", repl, "good")]
            : [w("replace", repl), w("delete", del), w("insert", ins), w("min+1", 1 + Math.min(repl, del, ins), "good")],
        },
      );

      const value = match ? repl : 1 + Math.min(repl, del, ins);
      grid[i][j] = { value, tone: match ? "good" : "active" };

      t.push(
        { grid: snap(grid), ...base, cursor: { r: i, c: j } },
        `dp[${i}][${j}] = ${value}: it takes ${value} edit${value === 1 ? "" : "s"} to turn "${a.slice(0, i)}" into "${b.slice(0, j)}".`,
        { line: match ? 9 : 11, phase: "write", watch: [w(`dp[${i}][${j}]`, value, "good")] },
      );
    }
  }

  t.push(
    { grid: snap(grid), ...base, cursor: { r: m, c: n } },
    `Answer: ${grid[m][n]!.value} edits to turn "${a}" into "${b}". O(m·n) time and space; because each row only reads the row above, the space collapses to O(n).`,
    { line: 14, phase: "answer", watch: [w("distance", grid[m][n]!.value as number, "good")] },
  );

  return capFrames(t.done(`edit distance("${a}", "${b}") = ${grid[m][n]!.value}`));
};

// ── 3. 0/1 knapsack ──────────────────────────────────────────────────────

const KNAPSACK_CODE = [
  "def knapsack(weights, values, cap):",
  "    n = len(weights)",
  "    dp = [[0] * (cap + 1) for _ in range(n + 1)]",
  "    for i in range(1, n + 1):",
  "        wt, val = weights[i - 1], values[i - 1]",
  "        for c in range(cap + 1):",
  "            dp[i][c] = dp[i - 1][c]              # skip item i",
  "            if wt <= c:                          # can it fit?",
  "                dp[i][c] = max(dp[i][c],",
  "                               dp[i - 1][c - wt] + val)   # take it",
  "    return dp[n][cap]",
];

export const knapsack: DPAlgo = (input) => {
  const weights = input.weights ?? [1, 3, 4, 5];
  const values = input.values ?? [1, 4, 5, 7];
  const cap = input.target ?? 7;
  const n = Math.min(weights.length, values.length);
  const t = tracer<DPState>(KNAPSACK_CODE);

  const grid: (DPCell | null)[][] = Array.from({ length: n + 1 }, () =>
    Array.from({ length: cap + 1 }, () => null),
  );
  for (let c = 0; c <= cap; c++) grid[0][c] = { value: 0, tone: "muted" };

  const base = {
    colLabels: Array.from({ length: cap + 1 }, (_, c) => c),
    rowLabels: ["∅", ...Array.from({ length: n }, (_, i) => `w${weights[i]}v${values[i]}`)],
    colTitle: "capacity",
    rowTitle: "items considered",
  };

  t.push(
    { grid: snap(grid), ...base },
    `Row 0 means "no items available", so every capacity yields value 0. Each later row adds exactly one item to the pool — the row index is *how many items you are allowed to consider*, not which item you took.`,
    { line: 3, phase: "base case" },
  );

  for (let i = 1; i <= n; i++) {
    const wt = weights[i - 1];
    const val = values[i - 1];
    for (let c = 0; c <= cap; c++) {
      const fits = wt <= c;
      const deps = fits
        ? [
            { r: i - 1, c },
            { r: i - 1, c: c - wt },
          ]
        : [{ r: i - 1, c }];

      const reading = snap(grid);
      for (const d of deps) if (reading[d.r][d.c]) reading[d.r][d.c]!.tone = "warn";
      const skip = grid[i - 1][c]!.value as number;
      const take = fits ? (grid[i - 1][c - wt]!.value as number) + val : -1;

      t.push(
        { grid: reading, ...base, cursor: { r: i, c }, deps },
        fits
          ? `Item ${i} weighs ${wt} and is worth ${val}; capacity ${c} can hold it. Skipping gives ${skip}; taking it frees up ${c} − ${wt} = ${c - wt} of capacity for the earlier items, giving ${grid[i - 1][c - wt]!.value} + ${val} = ${take}. Note both options read row i−1 — that is what makes each item usable at most once.`
          : `Item ${i} weighs ${wt}, more than capacity ${c}, so it cannot be taken at all. Copy the value from the row above.`,
        {
          line: fits ? 10 : 7,
          phase: fits ? "choose" : "too heavy",
          watch: fits
            ? [w("skip", skip, take > skip ? "muted" : "good"), w("take", take, take > skip ? "good" : "muted")]
            : [w("weight", wt, "bad"), w("capacity", c)],
        },
      );

      const value = fits ? Math.max(skip, take) : skip;
      grid[i][c] = { value, tone: fits && take > skip ? "good" : "active" };
    }

    t.push(
      { grid: snap(grid), ...base },
      `Row ${i} complete: with items 1..${i} available, dp[${i}][c] is the best value at each capacity c.`,
      { line: 11, phase: `row ${i}`, watch: [w("best so far", grid[i][cap]!.value as number, "good")] },
    );
  }

  // Recover which items were taken.
  const chosen: number[] = [];
  let ci = cap;
  for (let i = n; i >= 1; i--) {
    if ((grid[i][ci]!.value as number) !== (grid[i - 1][ci]!.value as number)) {
      chosen.unshift(i);
      ci -= weights[i - 1];
    }
  }
  const path = chosen.map((i, k) => ({
    r: i,
    c: chosen.slice(0, k + 1).reduce((acc, j) => acc + weights[j - 1], 0),
  }));

  t.push(
    { grid: snap(grid), ...base, path, cursor: { r: n, c: cap } },
    `Best value at capacity ${cap} is ${grid[n][cap]!.value}, taking item${chosen.length === 1 ? "" : "s"} ${chosen.join(", ")}. Which items were taken is not stored — it is recovered by asking, row by row, "did this row's value differ from the row above?".`,
    { line: 11, phase: "answer", watch: [w("value", grid[n][cap]!.value as number, "good"), w("items", chosen.join(",") || "none", "good")] },
  );

  return capFrames(t.done(`max value = ${grid[n][cap]!.value} (items ${chosen.join(", ") || "none"})`));
};

// ── 4. Coin change — fewest coins (LC 322) ───────────────────────────────

const COIN_CODE = [
  "def coin_change(coins, amount):",
  "    INF = amount + 1",
  "    dp = [0] + [INF] * amount",
  "    for a in range(1, amount + 1):",
  "        for c in coins:",
  "            if c <= a:",
  "                dp[a] = min(dp[a], dp[a - c] + 1)",
  "    return -1 if dp[amount] == INF else dp[amount]",
];

export const coinChange: DPAlgo = (input) => {
  const coins = (input.values ?? [1, 3, 4]).filter((c) => c > 0).sort((x, y) => x - y);
  const amount = input.target ?? 6;
  const t = tracer<DPState>(COIN_CODE);
  const INF = amount + 1;

  const dp = [0, ...Array.from({ length: amount }, () => INF)];
  const fmt = (v: number) => (v >= INF ? "∞" : v);

  const row = (): (DPCell | null)[][] => [
    dp.map((v, i) => ({ value: fmt(v), tone: (i === 0 ? "muted" : v >= INF ? "muted" : "active") as Tone })),
  ];
  const base = {
    colLabels: Array.from({ length: amount + 1 }, (_, i) => i),
    rowLabels: ["coins"],
    colTitle: "amount",
  };

  t.push(
    { grid: row(), ...base },
    `dp[a] is the fewest coins that make amount a. dp[0] = 0 (make nothing with nothing) and everything else starts unreachable. Using amount+1 as the "infinity" sentinel avoids float math and still compares correctly.`,
    { line: 3, phase: "base case", watch: [w("coins", coins.join(", ")), w("INF", INF, "muted")] },
  );

  for (let a = 1; a <= amount; a++) {
    for (const c of coins) {
      if (c > a) continue;
      const candidate = dp[a - c] + 1;
      const improves = candidate < dp[a];
      const reading = row();
      reading[0][a - c]!.tone = "warn";
      t.push(
        { grid: reading, ...base, cursor: { r: 0, c: a }, deps: [{ r: 0, c: a - c }] },
        dp[a - c] >= INF
          ? `Using coin ${c} would leave amount ${a - c}, which is itself unreachable — so this option is useless.`
          : improves
            ? `Using coin ${c} leaves amount ${a - c}, which needs ${dp[a - c]} coin${dp[a - c] === 1 ? "" : "s"}. That totals ${candidate}, better than the current ${fmt(dp[a])}.`
            : `Using coin ${c} would total ${candidate}, no better than the current ${fmt(dp[a])}.`,
        {
          line: 7,
          phase: `amount ${a}`,
          watch: [w("coin", c, "info"), w(`dp[${a - c}]`, fmt(dp[a - c])), w("candidate", fmt(candidate), improves ? "good" : "muted"), w(`dp[${a}]`, fmt(dp[a]))],
        },
      );
      if (improves) dp[a] = candidate;
    }
  }

  const answer = dp[amount] >= INF ? -1 : dp[amount];
  t.push(
    { grid: row(), ...base, cursor: { r: 0, c: amount } },
    answer === -1
      ? `dp[${amount}] never dropped below the sentinel, so ${amount} cannot be made from ${coins.join(", ")} — return −1.`
      : `dp[${amount}] = ${answer}. Every amount is solved once against every coin, so the cost is O(amount × coins). This is *unbounded* — each coin may be reused — which is exactly why the inner loop reads the same dp array it writes.`,
    { line: 8, phase: "answer", watch: [w("answer", answer, answer === -1 ? "bad" : "good")] },
  );

  return capFrames(t.done(`fewest coins for ${amount} = ${answer}`));
};

// ── 5. Longest increasing subsequence, O(n²) (LC 300) ────────────────────

const LIS_CODE = [
  "def lis(arr):",
  "    dp = [1] * len(arr)          # every element alone is a run of 1",
  "    for i in range(len(arr)):",
  "        for j in range(i):",
  "            if arr[j] < arr[i]:",
  "                dp[i] = max(dp[i], dp[j] + 1)",
  "    return max(dp, default=0)",
];

export const lis: DPAlgo = (input) => {
  const arr = input.values ?? [10, 9, 2, 5, 3, 7, 101, 18];
  const t = tracer<DPState>(LIS_CODE);
  const dp = arr.map(() => 1);
  const prev = arr.map(() => -1);

  const grid = (focus?: number, cmp?: number): (DPCell | null)[][] => [
    arr.map((v, i) => ({ value: v, tone: (i === focus ? "active" : i === cmp ? "warn" : "muted") as Tone })),
    dp.map((v, i) => ({ value: v, tone: (i === focus ? "good" : i === cmp ? "warn" : "muted") as Tone })),
  ];
  const base = {
    colLabels: arr.map((_, i) => i),
    rowLabels: ["arr", "dp"],
    colTitle: "index",
  };

  t.push(
    { grid: grid(), ...base },
    `dp[i] is the length of the longest increasing subsequence *ending at* i. Every element is a valid run of length 1 on its own, so that is the floor.`,
    { line: 2, phase: "base case" },
  );

  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < i; j++) {
      const canExtend = arr[j] < arr[i];
      const candidate = dp[j] + 1;
      const improves = canExtend && candidate > dp[i];
      t.push(
        { grid: grid(i, j), ...base, cursor: { r: 1, c: i }, deps: canExtend ? [{ r: 1, c: j }] : [] },
        canExtend
          ? improves
            ? `arr[${j}] = ${arr[j]} < arr[${i}] = ${arr[i]}, so the run ending at ${j} (length ${dp[j]}) can be extended by arr[${i}]. That gives ${candidate}, better than ${dp[i]}.`
            : `arr[${j}] = ${arr[j]} < arr[${i}], so extending is legal, but it would only give ${candidate} — no better than dp[${i}] = ${dp[i]}.`
          : `arr[${j}] = ${arr[j]} is not less than arr[${i}] = ${arr[i]}, so no increasing run through ${j} can end at ${i}.`,
        {
          line: canExtend ? 6 : 5,
          phase: `i = ${i}`,
          watch: [w(`arr[${j}]`, arr[j], canExtend ? "good" : "bad"), w(`arr[${i}]`, arr[i], "active"), w("candidate", canExtend ? candidate : "—", improves ? "good" : "muted"), w(`dp[${i}]`, dp[i])],
        },
      );
      if (improves) {
        dp[i] = candidate;
        prev[i] = j;
      }
    }
  }

  const best = Math.max(0, ...dp);
  let end = dp.indexOf(best);
  const chain: number[] = [];
  while (end !== -1) {
    chain.unshift(end);
    end = prev[end];
  }

  t.push(
    { grid: grid(), ...base, path: chain.map((i) => ({ r: 1, c: i })) },
    `Longest increasing subsequence has length ${best}: ${chain.map((i) => arr[i]).join(" < ")}. Note the answer is max(dp), not dp[last] — the best run does not have to end at the final element. This O(n²) version is the one to explain; the O(n log n) patience-sorting variant is the follow-up.`,
    { line: 7, phase: "answer", watch: [w("length", best, "good"), w("subsequence", chain.map((i) => arr[i]).join(","), "good")] },
  );

  return capFrames(t.done(`LIS length = ${best} → [${chain.map((i) => arr[i]).join(", ")}]`));
};

// ── 6. Unique paths on a grid (LC 62) ────────────────────────────────────

const PATHS_CODE = [
  "def unique_paths(rows, cols):",
  "    dp = [[1] * cols for _ in range(rows)]",
  "    for r in range(1, rows):",
  "        for c in range(1, cols):",
  "            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]",
  "    return dp[rows - 1][cols - 1]",
];

export const uniquePaths: DPAlgo = (input) => {
  const rows = Math.max(1, Math.min(input.target ?? 4, 8));
  const cols = Math.max(1, Math.min(input.values?.[0] ?? 4, 8));
  const t = tracer<DPState>(PATHS_CODE);

  const grid: (DPCell | null)[][] = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => null),
  );
  for (let c = 0; c < cols; c++) grid[0][c] = { value: 1, tone: "muted" };
  for (let r = 0; r < rows; r++) grid[r][0] = { value: 1, tone: "muted" };

  const base = {
    colLabels: Array.from({ length: cols }, (_, c) => c),
    rowLabels: Array.from({ length: rows }, (_, r) => r),
    colTitle: "column",
    rowTitle: "row",
  };

  t.push(
    { grid: snap(grid), ...base },
    `Moves are right and down only, so the entire first row and first column have exactly one path each — you had no choices getting there.`,
    { line: 2, phase: "base case" },
  );

  for (let r = 1; r < rows; r++) {
    for (let c = 1; c < cols; c++) {
      const deps = [
        { r: r - 1, c },
        { r, c: c - 1 },
      ];
      const reading = snap(grid);
      for (const d of deps) if (reading[d.r][d.c]) reading[d.r][d.c]!.tone = "warn";
      const above = grid[r - 1][c]!.value as number;
      const left = grid[r][c - 1]!.value as number;

      t.push(
        { grid: reading, ...base, cursor: { r, c }, deps },
        `Any path arriving at (${r}, ${c}) took its final step either downward from (${r - 1}, ${c}) or rightward from (${r}, ${c - 1}). Those two sets are disjoint and cover everything, so the counts simply add: ${above} + ${left}.`,
        { line: 5, phase: "combine", watch: [w("from above", above, "warn"), w("from left", left, "warn"), w("sum", above + left, "good")] },
      );

      grid[r][c] = { value: above + left, tone: "active" };
    }
  }

  t.push(
    { grid: snap(grid), ...base, cursor: { r: rows - 1, c: cols - 1 } },
    `${grid[rows - 1][cols - 1]!.value} distinct paths across a ${rows}×${cols} grid. The table is Pascal's triangle rotated 45° — the closed form is C(${rows + cols - 2}, ${rows - 1}).`,
    { line: 6, phase: "answer", watch: [w("paths", grid[rows - 1][cols - 1]!.value as number, "good")] },
  );

  return capFrames(t.done(`${grid[rows - 1][cols - 1]!.value} unique paths`));
};

/**
 * Registry. The `algo` prop of <DPTable> indexes this.
 *
 * | key           | uses                          |
 * |---------------|-------------------------------|
 * | lcs           | a, b                          |
 * | edit-distance | a, b                          |
 * | knapsack      | weights, values, target (cap) |
 * | coin-change   | values (coins), target        |
 * | lis           | values                        |
 * | unique-paths  | target (rows), values[0] (cols) |
 */
export const DP_ALGOS: Record<string, DPAlgo> = {
  lcs,
  "edit-distance": editDistance,
  knapsack,
  "coin-change": coinChange,
  lis,
  "unique-paths": uniquePaths,
};

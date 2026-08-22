/**
 * algos/frontier.ts — three traces that were missing when their pages needed them.
 *
 * Each exists because no existing trace showed the page's actual subject:
 *
 * - `jump-game`      a greedy frontier scan. Sliding-window and Kadane traces both
 *                    walk an array, but neither draws the *reachability frontier*,
 *                    which is the entire content of LC 45/55/1306.
 * - `comparator-keys` sorting the SAME array three times under three different keys.
 *                    The sorting traces show sort mechanics; this page is about
 *                    choosing the key, which is a different lesson.
 * - `sieve`          marking composites. Prefix-sums walks an array left to right;
 *                    a sieve strides by i from i*i, and the striding is the point.
 *
 * All three emit ArrayState, so they render through <ArrayStepper> with no new
 * component. Register them in ./arrays.ts.
 */
import { capFrames, tracer, type Tone, type Watch } from "../frames";
import type { ArrayAlgo, ArrayInput, ArrayState } from "./arrays";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ── Jump Game: the reachability frontier (LC 55 / 45) ─────────────────────

const JUMP_CODE = [
  "def can_jump(nums):",
  "    farthest = 0",
  "    for i, n in enumerate(nums):",
  "        if i > farthest:",
  "            return False        # the frontier never reached here",
  "        farthest = max(farthest, i + n)",
  "    return True",
];

/**
 * The frontier is a single number, and drawing it as a band is what makes the
 * greedy obvious: you never choose *which* jump to take, you only ever widen the
 * reachable prefix. A cell beyond the frontier when you arrive at it is the only
 * failure mode.
 */
export const jumpGame: ArrayAlgo = (input) => {
  const arr = input.values?.length ? input.values : [2, 3, 1, 1, 4];
  const t = tracer<ArrayState>(JUMP_CODE);

  let farthest = 0;
  let failedAt = -1;

  const state = (i: number, marks: Record<number, Tone> = {}): ArrayState => ({
    values: arr,
    pointers: [{ name: "i", index: i, tone: "active" }],
    bands: [
      {
        from: 0,
        to: Math.min(farthest, arr.length - 1),
        label: `reachable · farthest = ${farthest}`,
        tone: farthest >= arr.length - 1 ? "good" : "info",
      },
    ],
    marks,
  });

  t.push(
    state(0),
    `The frontier starts at index 0 — before taking any jump, only the first cell is reachable. The greedy never decides *which* jump to take: it only ever widens this band, and the answer is whether the band reaches the last index.`,
    { line: 2, phase: "seed", watch: [w("farthest", 0, "info")] },
  );

  for (let i = 0; i < arr.length; i++) {
    if (i > farthest) {
      failedAt = i;
      t.push(
        state(i, { [i]: "bad" }),
        `Index ${i} sits **beyond** the frontier (${farthest}), so nothing can reach it and neither can anything after it. Return False. This single comparison is the whole failure test — there is no need to try individual jump lengths.`,
        { line: 5, phase: "unreachable", watch: [w("i", i, "bad"), w("farthest", farthest, "warn")] },
      );
      break;
    }

    const reach = i + arr[i];
    const widened = reach > farthest;
    farthest = Math.max(farthest, reach);

    t.push(
      state(i, { [i]: widened ? "good" : "muted" }),
      widened
        ? `From index ${i} you can jump up to ${arr[i]}, reaching ${reach} — that is further than the old frontier, so it widens to ${farthest}. Note that the *value* at ${i} matters only through this one max.`
        : `From index ${i} you reach only ${reach}, which the frontier (${farthest}) already covers. This cell contributes nothing — a shorter jump from an earlier index already did better.`,
      {
        line: 6,
        phase: `i = ${i}`,
        watch: [
          w("i", i, "active"),
          w("jump", arr[i]),
          w("i + n", reach, widened ? "good" : "muted"),
          w("farthest", farthest, "info"),
        ],
      },
    );

    if (farthest >= arr.length - 1) {
      t.push(
        state(i, { [arr.length - 1]: "good" }),
        `The frontier now covers the last index, so the answer is True and the scan can stop early. One pass, one variable, O(n) time and O(1) space — no DP table, and no need to know *which* jumps were used.`,
        { line: 7, phase: "reachable", watch: [w("farthest", farthest, "good")] },
      );
      break;
    }
  }

  return capFrames(t.done(failedAt >= 0 ? `unreachable at index ${failedAt}` : "last index reachable"));
};

// ── Comparator keys: one array, three sort keys, three answers ────────────

const COMPARATOR_CODE = [
  "words = ['bb', 'a', 'ccc', 'dd']",
  "",
  "sorted(words)                       # 1. lexicographic (default)",
  "sorted(words, key=len)              # 2. by length",
  "sorted(words, key=lambda s: (len(s), s))   # 3. length, then alphabet",
];

/**
 * The sorting traces in ./sorting.ts show how a sort moves elements. This page is
 * about something else entirely: the *key* decides the answer, and the algorithm
 * is irrelevant. So this trace sorts one array three times and shows the three
 * different results, rather than animating any single sort.
 */
export const comparatorKeys: ArrayAlgo = (input) => {
  const words = input.text ? input.text.split(",") : ["bb", "a", "ccc", "dd"];
  const t = tracer<ArrayState>(COMPARATOR_CODE);

  const show = (row: string[], marks: Record<number, Tone> = {}): ArrayState => ({
    values: row,
    marks,
    rows: [{ label: "original", values: words }],
  });

  const allGood = (row: string[]): Record<number, Tone> =>
    Object.fromEntries(row.map((_, i) => [i, "good" as Tone]));

  t.push(
    show(words, Object.fromEntries(words.map((_, i) => [i, "info" as Tone]))),
    `One array, three questions. Sorting is $O(n \\log n)$ whichever key you pick, so the algorithm is never the interesting part here — **the key is the answer**. Watch how the same four words land in three different orders.`,
    { line: 1, phase: "input", watch: [w("n", words.length)] },
  );

  const lex = [...words].sort();
  t.push(
    show(lex, allGood(lex)),
    `**Default order** — Python compares strings lexicographically, character by character. Result: ${lex.join(
      ", ",
    )}. Note 'a' comes first despite being shortest; length plays no part.`,
    { line: 3, phase: "key = identity", watch: [w("key", "none", "info")] },
  );

  const byLen = [...words].sort((a, b) => a.length - b.length);
  t.push(
    show(byLen, allGood(byLen)),
    `**key=len** — now only length is compared, and Python's sort is **stable**, so words of equal length keep their original relative order. Result: ${byLen.join(
      ", ",
    )}. That stability is a guarantee, not luck, and it is what lets you sort by one key and then another to get a compound order.`,
    { line: 4, phase: "key = len", watch: [w("key", "len", "warn"), w("stable", "yes", "good")] },
  );

  const tuple = [...words].sort((a, b) => a.length - b.length || (a < b ? -1 : a > b ? 1 : 0));
  t.push(
    show(tuple, allGood(tuple)),
    `**key=(len, s)** — a tuple key compares element by element: length first, and only on a tie does the alphabet break it. Result: ${tuple.join(
      ", ",
    )}. This is how nearly every real comparator is written; a custom \`cmp_to_key\` function is almost never needed.`,
    { line: 5, phase: "key = (len, s)", watch: [w("key", "(len, s)", "good")] },
  );

  return capFrames(t.done(`three keys → ${lex.join(" ")} · ${byLen.join(" ")} · ${tuple.join(" ")}`));
};

// ── Sieve of Eratosthenes ─────────────────────────────────────────────────

const SIEVE_CODE = [
  "def sieve(n):",
  "    is_prime = [True] * (n + 1)",
  "    is_prime[0] = is_prime[1] = False",
  "    for i in range(2, int(n ** 0.5) + 1):",
  "        if is_prime[i]:",
  "            for j in range(i * i, n + 1, i):   # start at i*i, stride by i",
  "                is_prime[j] = False",
  "    return [i for i, p in enumerate(is_prime) if p]",
];

/**
 * Two things are worth seeing and neither is visible in the code: the inner loop
 * *strides* rather than scanning, and starting at `i*i` skips a chunk that a
 * smaller prime has already crossed off. Both are drawn here.
 */
export const sieve: ArrayAlgo = (input) => {
  const n = Math.min(Math.max(input.target ?? 30, 10), 60);
  const t = tracer<ArrayState>(SIEVE_CODE);

  const isPrime = Array<boolean>(n + 1).fill(true);
  isPrime[0] = false;
  if (n >= 1) isPrime[1] = false;
  let marks = 0;

  const labels = Array.from({ length: n + 1 }, (_, i) => String(i));
  const state = (extra: Record<number, Tone> = {}): ArrayState => {
    const m: Record<number, Tone> = {};
    for (let i = 0; i <= n; i++) m[i] = isPrime[i] ? "good" : "muted";
    return { values: labels, marks: { ...m, ...extra } };
  };

  t.push(
    state(),
    `Every number from 0 to ${n} starts assumed prime, except 0 and 1 which are special-cased. The sieve does not test any number for primality — it crosses off multiples, which is why it beats trial division for bulk queries.`,
    { line: 3, phase: "init", watch: [w("n", n), w("marks", 0)] },
  );

  const limit = Math.floor(Math.sqrt(n));
  for (let i = 2; i <= limit; i++) {
    if (!isPrime[i]) {
      t.push(
        state({ [i]: "muted" }),
        `${i} is already crossed off, so it is composite — and every multiple of ${i} is also a multiple of ${i}'s own smallest prime factor, already handled. Skip it entirely.`,
        { line: 5, phase: `i = ${i}`, watch: [w("i", i, "muted"), w("skipped", "composite")] },
      );
      continue;
    }

    const crossed: number[] = [];
    for (let j = i * i; j <= n; j += i) {
      if (isPrime[j]) crossed.push(j);
      isPrime[j] = false;
      marks++;
    }

    t.push(
      state({ [i]: "active", ...Object.fromEntries(crossed.map((j) => [j, "bad" as Tone])) }),
      `${i} is prime, so cross off its multiples — starting at **${i}² = ${
        i * i
      }**, not ${2 * i}. Every smaller multiple of ${i} has a factor below ${i} and was crossed off in an earlier round. Marked this round: ${
        crossed.length ? crossed.join(", ") : "nothing new"
      }.`,
      {
        line: 7,
        phase: `i = ${i}`,
        watch: [w("i", i, "active"), w("from", i * i, "warn"), w("stride", i), w("marks", marks)],
      },
    );
  }

  const primes = labels.map((_, i) => i).filter((i) => isPrime[i]);
  t.push(
    state(),
    `Primes up to ${n}: ${primes.join(", ")}. Total marking operations: **${marks}** — and the outer loop stopped at √${n} = ${limit}, because any composite ≤ ${n} has a factor ≤ √${n} and was therefore already crossed off. O(n log log n), which is close enough to linear to treat as such.`,
    { line: 8, phase: "done", watch: [w("primes", primes.length, "good"), w("marks", marks)] },
  );

  return capFrames(t.done(`${primes.length} primes ≤ ${n}, ${marks} marking operations`));
};

/**
 * Registry fragment, spread into ALGOS in ./arrays.ts.
 *
 * | key             | uses                                   |
 * |-----------------|----------------------------------------|
 * | jump-game       | values (jump lengths)                  |
 * | comparator-keys | text — comma-separated words, optional |
 * | sieve           | target (upper bound, 10..60)           |
 */
export const FRONTIER_ALGOS: Record<string, ArrayAlgo> = {
  "jump-game": jumpGame,
  "comparator-keys": comparatorKeys,
  sieve: sieve,
};

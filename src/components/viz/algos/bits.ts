/**
 * algos/bits.ts — traced bit-manipulation algorithms, in the ArrayState shape.
 *
 * A machine word *is* an array of bits, so `<ArrayStepper tag="bits">` renders
 * these unchanged. That collapses the planned BitBoard component into three
 * registry entries — the same reuse that removed SortRace and BinarySearchDial.
 *
 * Bits are shown most-significant first, left to right, which is how they are
 * written and therefore how a reader expects to see them.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { ArrayAlgo, ArrayInput, ArrayState } from "./arrays";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

/** Fixed width keeps the row from resizing between frames. */
const WIDTH = 8;

const bitsOf = (v: number, width = WIDTH): (0 | 1)[] =>
  Array.from({ length: width }, (_, i) => ((v >> (width - 1 - i)) & 1) as 0 | 1);

const bitLabel = (v: number, width = WIDTH) => bitsOf(v, width).join("");

// ── 1. n & (n - 1) — Brian Kernighan's bit count (LC 191) ─────────────────

const COUNT_CODE = [
  "def count_bits(n):",
  "    count = 0",
  "    while n:",
  "        n &= n - 1        # clears the LOWEST set bit",
  "        count += 1",
  "    return count          # loops once per SET bit, not per bit",
];

export const countSetBits: ArrayAlgo = (input) => {
  const start = input.values?.[0] ?? input.target ?? 156;
  const t = tracer<ArrayState>(COUNT_CODE);

  let n = start & 0xff;
  let count = 0;

  const state = (focus?: number, tone: Tone = "bad"): ArrayState => ({
    values: bitsOf(n),
    marks: Object.fromEntries(
      bitsOf(n).map((b, i) => [i, (i === focus ? tone : b ? "good" : "muted") as Tone]),
    ),
    chips: [
      { label: "n", value: String(n), tone: "active" },
      { label: "binary", value: bitLabel(n), tone: "info" },
      { label: "count", value: String(count), tone: "good" },
    ],
  });

  t.push(
    state(),
    `Counting set bits one position at a time takes 8 iterations here — 32 or 64 on a real word. Kernighan's trick takes one iteration per **set** bit instead, which for sparse values is far fewer.`,
    { line: 2, phase: "setup", watch: [w("n", n, "active"), w("binary", bitLabel(n))] },
  );

  while (n !== 0) {
    const lowest = n & -n;
    const lowestIdx = WIDTH - 1 - Math.log2(lowest);

    t.push(
      state(lowestIdx, "warn"),
      `n − 1 flips the lowest set bit to 0 and turns every zero below it into a 1. ANDing that with n therefore clears exactly the lowest set bit and leaves everything above untouched: ${bitLabel(n)} & ${bitLabel(n - 1)} = ${bitLabel(n & (n - 1))}.`,
      {
        line: 4,
        phase: "clear",
        watch: [w("n", bitLabel(n), "active"), w("n-1", bitLabel(n - 1), "warn"), w("lowest bit", lowest, "bad")],
      },
    );

    n &= n - 1;
    count += 1;

    t.push(
      state(),
      `One set bit gone, count is ${count}. ${n === 0 ? "n is now zero, so the loop ends." : `${bitLabel(n)} remains.`}`,
      { line: 5, phase: "count", watch: [w("n", n), w("count", count, "good")] },
    );
  }

  t.push(
    state(),
    `${start & 0xff} has ${count} set bit${count === 1 ? "" : "s"}, found in ${count} iteration${count === 1 ? "" : "s"}. The same "n & (n - 1)" idiom answers "is this a power of two" in one test — a power of two has exactly one set bit, so clearing it must give zero.`,
    { line: 6, phase: "answer", watch: [w("count", count, "good")] },
  );

  return capFrames(t.done(`${start & 0xff} has ${count} set bits`));
};

// ── 2. XOR to find the single number (LC 136) ─────────────────────────────

const XOR_CODE = [
  "def single_number(nums):",
  "    acc = 0",
  "    for v in nums:",
  "        acc ^= v          # pairs cancel, the loner survives",
  "    return acc",
];

export const xorSingle: ArrayAlgo = (input) => {
  const nums = input.values?.length ? input.values : [4, 1, 2, 1, 2];
  const t = tracer<ArrayState>(XOR_CODE);

  let acc = 0;

  const state = (focus?: number): ArrayState => ({
    values: bitsOf(acc),
    marks: Object.fromEntries(bitsOf(acc).map((b, i) => [i, (b ? "good" : "muted") as Tone])),
    rows: [
      {
        label: "input",
        values: nums.map((v) => v),
        marks: Object.fromEntries(
          nums.map((_, i) => [i, (i === focus ? "active" : i < (focus ?? 0) ? "muted" : "info") as Tone]),
        ),
      },
    ],
    chips: [
      { label: "acc", value: String(acc), tone: "active" },
      { label: "binary", value: bitLabel(acc), tone: "info" },
    ],
  });

  t.push(
    state(),
    `XOR has three properties that combine into a trick: x ^ x = 0, x ^ 0 = x, and it is commutative. So XORing everything makes every duplicated value cancel itself out regardless of order, leaving only the value that appears once.`,
    { line: 2, phase: "setup" },
  );

  for (let i = 0; i < nums.length; i++) {
    const before = acc;
    acc ^= nums[i];
    t.push(
      state(i),
      `acc ^= ${nums[i]}: ${bitLabel(before)} ^ ${bitLabel(nums[i])} = ${bitLabel(acc)}. Each bit position flips only where the incoming value has a 1.`,
      {
        line: 4,
        phase: "xor",
        watch: [w("value", nums[i], "active"), w("acc", acc, "good"), w("binary", bitLabel(acc))],
      },
    );
  }

  t.push(
    state(),
    `Answer: ${acc}. O(n) time and **O(1) space** — a hash set also works and is easier to explain, but costs O(n) memory, and the O(1) requirement is why this problem is asked at all. Note the trick breaks if a value appears three times; that variant needs bit-counting modulo 3.`,
    { line: 5, phase: "answer", watch: [w("single", acc, "good")] },
  );

  return capFrames(t.done(`single number = ${acc}`));
};

// ── 3. Subset enumeration by bitmask ─────────────────────────────────────

const MASK_CODE = [
  "def subsets(nums):",
  "    n = len(nums)",
  "    for mask in range(1 << n):        # 0 .. 2^n - 1",
  "        subset = [nums[i] for i in range(n)",
  "                  if mask & (1 << i)]  # bit i set ⇒ take nums[i]",
  "        yield subset",
];

export const bitmaskSubsets: ArrayAlgo = (input) => {
  const nums = (input.values?.length ? input.values : [3, 5, 7]).slice(0, 4);
  const n = nums.length;
  const t = tracer<ArrayState>(MASK_CODE);
  const found: string[] = [];

  const state = (mask: number, taken: number[]): ArrayState => ({
    values: bitsOf(mask, n),
    marks: Object.fromEntries(
      bitsOf(mask, n).map((b, i) => [i, (b ? "good" : "muted") as Tone]),
    ),
    rows: [
      {
        label: "nums",
        // Bits are shown most-significant first, so the element list is reversed
        // to keep bit i visually above nums[i].
        values: [...nums].reverse(),
        marks: Object.fromEntries(
          [...nums].reverse().map((_, i) => {
            const bitIndex = i; // already reversed, so index lines up with the row
            return [bitIndex, (bitsOf(mask, n)[bitIndex] ? "good" : "muted") as Tone];
          }),
        ),
      },
    ],
    chips: [
      { label: "mask", value: `${mask} = ${bitLabel(mask, n)}`, tone: "active" },
      { label: "subset", value: taken.length ? `{${taken.join(",")}}` : "{}", tone: "good" },
      { label: "found", value: String(found.length), tone: "info" },
    ],
  });

  t.push(
    state(0, []),
    `There are 2^${n} subsets and 2^${n} numbers representable in ${n} bits, so the two can be put in correspondence: treat each integer's bits as "take this element or not". That turns recursion into a flat loop, which is why bitmask enumeration is the standard trick for small n.`,
    { line: 3, phase: "setup", watch: [w("n", n), w("subsets", 1 << n, "info")] },
  );

  for (let mask = 0; mask < 1 << n; mask++) {
    const taken: number[] = [];
    for (let i = 0; i < n; i++) if (mask & (1 << i)) taken.push(nums[i]);
    found.push(taken.length ? `{${taken.join(",")}}` : "{}");

    t.push(
      state(mask, taken),
      `mask = ${mask} (${bitLabel(mask, n)}) selects ${taken.length ? `{${taken.join(", ")}}` : "the empty subset"}. The test is "mask & (1 << i)" — bit i decides element i, independently of every other bit.`,
      {
        line: 5,
        phase: `mask ${mask}`,
        watch: [w("mask", bitLabel(mask, n), "active"), w("size", taken.length), w("found", found.length, "good")],
      },
    );
  }

  t.push(
    state(0, []),
    `All ${found.length} subsets enumerated with no recursion and no explicit backtracking. This is the representation behind bitmask DP: a subset becomes an integer, so it can index an array — which is what makes travelling-salesman-style DP over subsets possible at all.`,
    { line: 6, phase: "answer", watch: [w("total", found.length, "good")] },
  );

  return capFrames(t.done(`${found.length} subsets enumerated`));
};

/**
 * Registry, merged into ALGOS by ./arrays.ts. Use `tag="bits"` on the component.
 *
 * | key               | uses                    |
 * |-------------------|-------------------------|
 * | count-set-bits    | values[0] or target     |
 * | xor-single        | values                  |
 * | bitmask-subsets   | values (≤ 4)            |
 */
export const BIT_ALGOS: Record<string, ArrayAlgo> = {
  "count-set-bits": countSetBits,
  "xor-single": xorSingle,
  "bitmask-subsets": bitmaskSubsets,
};

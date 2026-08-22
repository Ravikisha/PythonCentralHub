/**
 * algos/design.ts — two traces for the Phase-14 design problems.
 *
 * The design pages are about *data-structure composition*: an LRU cache is a hash
 * map plus a recency order, and an O(1) random-access set is an array plus an
 * index map. Neither is an array walk, so none of the existing ArrayStepper
 * algorithms show what they do — but both fit ArrayState cleanly, because it has
 * a `chips` row (the map) underneath the main sequence (the array/order).
 *
 * - `lru-cache`   the recency list, with the map of key → position as chips.
 *                 Shows the two things that make LRU O(1): touching a key moves
 *                 it without shifting, and eviction always takes the same end.
 * - `timestamp-window` the rate limiter's deque of timestamps. The only window trace
 *                 on the site that evicts by **age** rather than by size or by a
 *                 running condition, which is why it is here and not in arrays.ts.
 * - `hash-chaining` the bucket array behind LC 706. Shows the modulo collapse and why
 *                 the *longest chain*, not the key count, is what a lookup pays for.
 * - `swap-remove` the array + index-map trick behind O(1) insert/delete/random.
 *                 Shows why deletion swaps with the LAST element rather than
 *                 shifting, and what that does to the map.
 */
import { capFrames, tracer, type Tone, type Watch } from "../frames";
import type { ArrayAlgo, ArrayState } from "./arrays";

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ── LRU cache ─────────────────────────────────────────────────────────────

const LRU_CODE = [
  "class LRUCache:                      # dict + doubly-linked list",
  "    def get(self, key):",
  "        if key not in self.map: return -1",
  "        self._move_to_front(key)     # O(1): relink, never shift",
  "        return self.map[key].value",
  "",
  "    def put(self, key, value):",
  "        if key in self.map:",
  "            self._move_to_front(key)",
  "        elif len(self.map) == self.cap:",
  "            self._evict_from_back()  # the least recently used end",
  "        self._insert_at_front(key, value)",
];

/**
 * `values` is read as the operation script: a positive number `k` means
 * `put(k)`, a negative `-k` means `get(k)`. `k` (the prop) is the capacity.
 */
export const lruCache: ArrayAlgo = (input) => {
  const ops = input.values?.length ? input.values : [1, 2, 3, -1, 4, -2];
  const cap = Math.max(2, Math.min(input.k ?? 3, 6));
  const t = tracer<ArrayState>(LRU_CODE);

  /** Front of the list is index 0 = most recently used. */
  let order: number[] = [];

  const state = (marks: Record<number, Tone> = {}): ArrayState => ({
    values: order.length ? order.map((k) => `k${k}`) : ["(empty)"],
    marks,
    chips: [
      { label: "capacity", value: String(cap), tone: "info" },
      { label: "size", value: `${order.length}`, tone: order.length === cap ? "warn" : "good" },
      { label: "MRU", value: order.length ? `k${order[0]}` : "—", tone: "good" },
      { label: "LRU", value: order.length ? `k${order[order.length - 1]}` : "—", tone: "bad" },
    ],
  });

  t.push(
    state(),
    `An LRU cache is a hash map for lookup plus an **order** for recency. The row below is that order: front = most recently used, back = next to be evicted. Capacity is ${cap}. Every operation must be O(1), which is why the order is a doubly-linked list rather than an array — a real implementation relinks two pointers where this picture appears to shift cells.`,
    { line: 1, phase: "empty", watch: [w("capacity", cap, "info"), w("size", 0)] },
  );

  for (const op of ops) {
    const key = Math.abs(op);
    const isGet = op < 0;
    const present = order.includes(key);

    if (isGet) {
      if (!present) {
        t.push(
          state(),
          `**get(${key})** — miss. The key is not in the map, so return −1 and touch nothing. A miss must not disturb the recency order.`,
          { line: 3, phase: `get ${key}`, watch: [w("get", key, "bad"), w("result", -1, "bad")] },
        );
        continue;
      }
      order = [key, ...order.filter((x) => x !== key)];
      t.push(
        state({ 0: "good" }),
        `**get(${key})** — hit. The value is returned *and* the key becomes most-recently-used, which is the part people forget: a read mutates the order. In the linked-list implementation this is four pointer writes, not a shift.`,
        { line: 4, phase: `get ${key}`, watch: [w("get", key, "good"), w("MRU", `k${key}`, "good")] },
      );
      continue;
    }

    if (present) {
      order = [key, ...order.filter((x) => x !== key)];
      t.push(
        state({ 0: "good" }),
        `**put(${key})** — the key already exists, so this is an update: overwrite the value and move it to the front. No eviction, because the size did not change.`,
        { line: 9, phase: `put ${key}`, watch: [w("put", key, "active"), w("size", order.length)] },
      );
      continue;
    }

    let evicted: number | null = null;
    if (order.length === cap) {
      evicted = order[order.length - 1];
      order = order.slice(0, -1);
    }
    order = [key, ...order];

    t.push(
      state({ 0: "good" }),
      evicted === null
        ? `**put(${key})** — new key, and there is room. It goes to the front as the most recently used.`
        : `**put(${key})** — new key, but the cache is full, so **k${evicted} is evicted** from the back. That end is always the least recently used, which is the entire reason the order is maintained on every access rather than computed on demand.`,
      {
        line: evicted === null ? 11 : 10,
        phase: `put ${key}`,
        watch: [
          w("put", key, "active"),
          w("evicted", evicted === null ? "—" : `k${evicted}`, evicted === null ? "muted" : "bad"),
          w("size", order.length, order.length === cap ? "warn" : "good"),
        ],
      },
    );
  }

  t.push(
    state(),
    `Final order, most recent first: ${order.map((k) => `k${k}`).join(" → ")}. Every operation here was O(1) — a map lookup plus a constant number of pointer writes. Using a plain list instead makes "move to front" O(n), and using an ordered dict hides the mechanism the interview is asking about.`,
    { line: 1, phase: "done", watch: [w("size", order.length, "good")] },
  );

  return capFrames(t.done(`MRU → LRU: ${order.map((k) => `k${k}`).join(", ")}`));
};

// ── O(1) insert / delete / getRandom ─────────────────────────────────────

const SWAP_REMOVE_CODE = [
  "class RandomizedSet:                 # list + {value: index}",
  "    def insert(self, val):",
  "        self.pos[val] = len(self.items)",
  "        self.items.append(val)       # O(1) amortised",
  "",
  "    def remove(self, val):",
  "        i, last = self.pos[val], self.items[-1]",
  "        self.items[i] = last         # overwrite the hole with the last item",
  "        self.pos[last] = i           # and fix ITS index in the map",
  "        self.items.pop()",
  "        del self.pos[val]",
  "",
  "    def getRandom(self):",
  "        return random.choice(self.items)   # needs a gap-free array",
];

/**
 * `values` is the operation script: positive inserts, negative removes.
 * The point of the picture is the hole-filling swap and the map fix-up that
 * must accompany it.
 */
export const swapRemove: ArrayAlgo = (input) => {
  const ops = input.values?.length ? input.values : [10, 20, 30, 40, -20, 50];
  const t = tracer<ArrayState>(SWAP_REMOVE_CODE);

  const items: number[] = [];
  const pos = new Map<number, number>();

  const state = (marks: Record<number, Tone> = {}): ArrayState => ({
    values: items.length ? items.map(String) : ["(empty)"],
    marks,
    chips: [...pos.entries()]
      .sort((a, b) => a[1] - b[1])
      .map(([v, i]) => ({ label: String(v), value: `→ ${i}`, tone: "info" as Tone })),
  });

  t.push(
    state(),
    `Two structures, one invariant: a **gap-free array** of the items, and a **map from value to its index**. The array being gap-free is what makes \`getRandom\` a single \`random.choice\` — and keeping it gap-free while still deleting in O(1) is the whole trick.`,
    { line: 1, phase: "empty", watch: [w("size", 0)] },
  );

  for (const op of ops) {
    const val = Math.abs(op);
    if (op > 0) {
      pos.set(val, items.length);
      items.push(val);
      t.push(
        state({ [items.length - 1]: "good" }),
        `**insert(${val})** — append to the end and record its index. Both halves must stay in step: the array gains an entry, the map gains the same entry's position.`,
        { line: 4, phase: `insert ${val}`, watch: [w("insert", val, "good"), w("size", items.length)] },
      );
      continue;
    }

    if (!pos.has(val)) {
      t.push(state(), `**remove(${val})** — not present, nothing to do.`, {
        line: 6,
        phase: `remove ${val}`,
        watch: [w("remove", val, "bad")],
      });
      continue;
    }

    const i = pos.get(val)!;
    const last = items[items.length - 1];
    const wasLast = i === items.length - 1;
    items[i] = last;
    pos.set(last, i);
    items.pop();
    pos.delete(val);

    t.push(
      state({ [Math.min(i, Math.max(0, items.length - 1))]: "warn" }),
      wasLast
        ? `**remove(${val})** — it was already the last element, so the swap is a no-op and the pop is enough. Worth handling deliberately: writing \`pos[last] = i\` after deleting \`val\` when they are the same key resurrects the deleted entry, which is the classic bug in this problem.`
        : `**remove(${val})** — it sits at index ${i}, not the end. Shifting everything after it would be O(n), so instead **move the last element (${last}) into the hole**, fix *its* entry in the map to ${i}, pop the tail, and delete ${val}'s key. Four O(1) operations, and the array is still gap-free.`,
      {
        line: 9,
        phase: `remove ${val}`,
        watch: [
          w("remove", val, "bad"),
          w("moved", wasLast ? "—" : String(last), wasLast ? "muted" : "warn"),
          w("size", items.length),
        ],
      },
    );
  }

  t.push(
    state(),
    `Final array: [${items.join(", ")}], with the map pointing at exactly these indices. Order is **not** preserved — the swap scrambles it — and that is the price of O(1) removal. If the problem needs insertion order too, this trick does not apply.`,
    { line: 14, phase: "done", watch: [w("size", items.length, "good")] },
  );

  return capFrames(t.done(`[${items.join(", ")}] · ${pos.size} keys mapped`));
};

// ── timestamp window (rate limiter / hit counter) ──────────────────────────

const WINDOW_CODE = [
  "class RecentCounter:                 # deque of timestamps",
  "    def __init__(self):",
  "        self.q = deque()",
  "",
  "    def ping(self, t):",
  "        self.q.append(t)             # always admit the new event",
  "        while self.q[0] < t - W:     # STRICT <: the window is [t-W, t]",
  "            self.q.popleft()         # expired by AGE, not by count",
  "        return len(self.q)",
];

/**
 * `values` are event timestamps in increasing order; `k` is the window width.
 *
 * The eviction rule is what separates this from every other window trace on the
 * site: the front leaves because it is *older than the cutoff*, never because the
 * window grew past a size. So the row can grow and shrink by any amount in one
 * step, and a long idle gap drains it entirely.
 */
export const timestampWindow: ArrayAlgo = (input) => {
  const stamps = input.values?.length ? input.values : [1, 3, 6, 8, 11];
  const width = Math.max(1, input.k ?? 5);
  const t = tracer<ArrayState>(WINDOW_CODE);

  let q: number[] = [];

  const state = (marks: Record<number, Tone> = {}, cutoff?: number): ArrayState => ({
    values: q.length ? q.map((x) => String(x)) : ["(empty)"],
    marks,
    chips: [
      { label: "window", value: `${width}`, tone: "info" },
      { label: "cutoff", value: cutoff === undefined ? "—" : String(cutoff), tone: "warn" },
      { label: "count", value: `${q.length}`, tone: "good" },
    ],
  });

  t.push(
    state(),
    `A rate limiter keeps the events still inside a moving window of width ${width}. The row is the deque of timestamps, oldest at the left. Unlike every other window on this site, the left edge moves because entries **get old** — not because the window grew past a size — so the row can shrink by any amount in a single step, or not at all.`,
    { line: 2, phase: "empty", watch: [w("window", width, "info"), w("count", 0)] },
  );

  for (const stamp of stamps) {
    const cutoff = stamp - width;

    q = [...q, stamp];
    t.push(
      state({ [q.length - 1]: "active" }, cutoff),
      `**ping(${stamp})** — admit it first, unconditionally. The new event is always inside its own window, so there is never a reason to test it. Everything interesting happens at the *other* end: anything older than the cutoff ${cutoff} must go.`,
      {
        line: 5,
        phase: `ping ${stamp}`,
        watch: [w("t", stamp, "active"), w("cutoff", cutoff, "warn"), w("count", q.length)],
      },
    );

    const dropped: number[] = [];
    while (q.length > 0 && q[0] < cutoff) {
      dropped.push(q[0]);
      q = q.slice(1);
    }

    const onBoundary = q.length > 0 && q[0] === cutoff;
    t.push(
      state(onBoundary ? { 0: "good" } : {}, cutoff),
      dropped.length === 0
        ? onBoundary
          ? `Nothing expires — and the front is **exactly** ${cutoff}, sitting on the cutoff. The window is inclusive, so a timestamp equal to the cutoff still counts. This is the whole reason the test is a strict "<" and not "<=": swap it and this event is wrongly discarded, giving ${q.length - 1} instead of ${q.length}.`
          : `Nothing expires: the oldest entry ${q[0]} is still inside the window. Most calls do no work at all at the left edge, which is why the amortised cost is O(1) even though a single call can be O(n).`
        : `${dropped.length === 1 ? `Timestamp ${dropped[0]} is` : `Timestamps ${dropped.join(", ")} are`} older than the cutoff ${cutoff}, so ${dropped.length === 1 ? "it leaves" : "they leave"} the front. **Answer: ${q.length}.**${onBoundary ? ` And the new front is **exactly** ${cutoff} — on the cutoff, so it stays: the window is inclusive. Change the test to "<=" and this one is discarded too, giving ${q.length - 1}.` : ""} The drop count is unbounded — a long idle gap makes one call drain the whole deque, which is why this is O(1) *amortised* and O(n) worst case.`,
      {
        line: dropped.length === 0 ? 8 : 7,
        phase: `ping ${stamp}`,
        watch: [
          w("t", stamp, "active"),
          w("dropped", dropped.length, dropped.length ? "bad" : "muted"),
          w("count", q.length, "good"),
        ],
      },
    );
  }

  return capFrames(
    t.done(`${q.length} events inside the last ${width} · each timestamp entered once and left at most once`),
  );
};

// ── hash map with separate chaining ────────────────────────────────────────

const HASHMAP_CODE = [
  "class MyHashMap:                     # array of buckets + chaining",
  "    def __init__(self, n_buckets=5):",
  "        self.buckets = [[] for _ in range(n_buckets)]",
  "",
  "    def _index(self, key):",
  "        return key % len(self.buckets)   # the modulo collapse",
  "",
  "    def put(self, key, value):",
  "        chain = self.buckets[self._index(key)]",
  "        for i, (k, _) in enumerate(chain):",
  "            if k == key:",
  "                chain[i] = (key, value)  # update, not append",
  "                return",
  "        chain.append((key, value))       # collision -> chain grows",
];

/**
 * `values` are the keys to `put`, in order; `k` is the bucket count.
 *
 * Each cell of the row is one bucket, showing the chain inside it. What the trace is
 * for is the pair of facts that make a hash map O(1) *average* and not O(1) worst
 * case: many keys collapse onto the same bucket, and a lookup then walks that
 * bucket's chain.
 */
export const hashChaining: ArrayAlgo = (input) => {
  const keys = input.values?.length ? input.values : [1, 6, 11, 2, 7, 3];
  const nb = Math.max(2, Math.min(input.k ?? 5, 12));
  const t = tracer<ArrayState>(HASHMAP_CODE);

  const buckets: number[][] = Array.from({ length: nb }, () => []);

  const size = () => buckets.reduce((a, b) => a + b.length, 0);
  const worst = () => buckets.reduce((a, b) => Math.max(a, b.length), 0);

  const state = (marks: Record<number, Tone> = {}): ArrayState => ({
    values: buckets.map((c, j) => (c.length ? `b${j}: ${c.join(" -> ")}` : `b${j}: -`)),
    marks,
    chips: [
      { label: "buckets", value: String(nb), tone: "info" },
      { label: "size", value: String(size()), tone: "good" },
      { label: "load", value: (size() / nb).toFixed(1), tone: size() > nb ? "warn" : "good" },
      { label: "worst chain", value: String(worst()), tone: worst() > 2 ? "warn" : "good" },
    ],
  });

  t.push(
    state(),
    `A hash map is an **array of buckets** plus a rule for collisions. Each cell below is one bucket and shows the chain inside it. With ${nb} buckets, key k lands in bucket k % ${nb} — which means an unbounded key space collapses onto ${nb} slots, so collisions are not an edge case, they are the normal operating condition.`,
    { line: 2, phase: "empty", watch: [w("buckets", nb, "info"), w("size", 0)] },
  );

  for (const key of keys) {
    const idx = ((key % nb) + nb) % nb;
    const chain = buckets[idx];
    const already = chain.includes(key);
    const before = chain.length;

    t.push(
      state({ [idx]: "active" }),
      `**put(${key})** — ${key} % ${nb} = **${idx}**, so bucket ${idx} is the only one that can hold it. That single arithmetic step is what makes lookup fast: no search is needed to find *where* to look.`,
      {
        line: 5,
        phase: `put ${key}`,
        watch: [w("key", key, "active"), w("bucket", idx, "info"), w("chain len", before)],
      },
    );

    if (already) {
      t.push(
        state({ [idx]: "good" }),
        `${key} is **already in bucket ${idx}**, so this is an update: overwrite its value in place and return. Appending instead would leave two entries with the same key, and every later get would return whichever the scan reached first — a duplicate-key bug that reads as a stale value.`,
        { line: 11, phase: `put ${key}`, watch: [w("key", key, "good"), w("action", "update", "good")] },
      );
      continue;
    }

    chain.push(key);
    t.push(
      state({ [idx]: before > 0 ? "warn" : "good" }),
      before === 0
        ? `Bucket ${idx} was empty, so ${key} goes straight in. One probe to find it later.`
        : `Bucket ${idx} already held ${before === 1 ? "an entry" : `${before} entries`}, so this is a **collision** — and the chain grows to ${chain.length}. Nothing is wrong: a get for ${key} now costs ${chain.length} probes instead of 1, because it must walk the chain comparing keys. The **worst chain length is the real cost**, not the number of keys.`,
      {
        line: 13,
        phase: `put ${key}`,
        watch: [
          w("key", key, "active"),
          w("collision", before > 0 ? "yes" : "no", before > 0 ? "warn" : "good"),
          w("worst chain", worst(), worst() > 2 ? "warn" : "good"),
        ],
      },
    );
  }

  t.push(
    state(),
    `Final state: ${size()} keys in ${nb} buckets, load factor ${(size() / nb).toFixed(1)}, longest chain **${worst()}**. Average lookup is O(1 + load), which is O(1) for a bounded load — and that is exactly why a real implementation **resizes** once the load factor passes about 0.75, rehashing every key into a larger array. Skip the resize and the chains grow without bound until get is O(n).`,
    { line: 1, phase: "done", watch: [w("load", (size() / nb).toFixed(1), size() > nb ? "warn" : "good"), w("worst chain", worst(), "warn")] },
  );

  return capFrames(t.done(`${size()} keys · ${nb} buckets · longest chain ${worst()}`));
};

/**
 * Registry fragment, spread into ALGOS in ./arrays.ts.
 *
 * | key         | uses                                                     |
 * |-------------|----------------------------------------------------------|
 * | lru-cache   | values (+k = put k, −k = get k), k = capacity             |
 * | swap-remove | values (+v = insert, −v = remove)                         |
 * | timestamp-window | values = event timestamps (increasing), k = window width |
 * | hash-chaining | values = keys to put, k = bucket count                     |
 */
export const DESIGN_ALGOS: Record<string, ArrayAlgo> = {
  "lru-cache": lruCache,
  "swap-remove": swapRemove,
  "timestamp-window": timestampWindow,
  "hash-chaining": hashChaining,
};

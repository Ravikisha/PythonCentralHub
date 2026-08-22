/**
 * algos/lists.ts — traced linked-list algorithms for <LinkedListRewire>.
 *
 * Linked-list problems are pointer surgery, and pointer surgery is exactly what
 * prose cannot convey. "Set `nxt = cur.next`, then `cur.next = prev`, then
 * `prev = cur`, then `cur = nxt`" is four assignments whose *order* is the entire
 * difficulty — swap two of them and the list is silently truncated. Seeing the
 * arrows move, one assignment at a time, makes the ordering obvious in a way no
 * amount of explanation does.
 *
 * The state here is therefore not "the list" but "the nodes and the named
 * pointers into them", because the pointers are the subject.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

/** A node box on the rail. */
export interface ListNode {
  id: number;
  value: number | string;
  /** Column position. Nodes keep their slot even as links are rewired. */
  slot: number;
  tone?: Tone;
}

/** A link between two nodes, or to null. `to: null` renders as a ∅ terminator. */
export interface ListLink {
  from: number;
  to: number | null;
  tone?: Tone;
  /** Draw below the rail — for `random` pointers and cycle back-edges. */
  under?: boolean;
  label?: string;
}

/** A named cursor, drawn as a labelled caret above its node. */
export interface ListCursor {
  name: string;
  /** `null` parks the cursor on the ∅ terminator. */
  node: number | null;
  tone?: Tone;
}

export interface ListState {
  nodes: ListNode[];
  links: ListLink[];
  cursors: ListCursor[];
  /** Number of slots to reserve, so the rail does not resize between frames. */
  slots: number;
  /** Optional secondary rail, for merge/split problems. */
  second?: { label: string; nodes: ListNode[]; links: ListLink[] };
}

export interface ListInput {
  /** Node values, head first. */
  values?: number[];
  /** Second list, for merge problems. */
  other?: number[];
  /** Position (0-based) where the tail links back, creating a cycle. -1 for none. */
  cycleAt?: number;
  /** Group size for k-group reversal, or the n in "nth from the end". */
  k?: number;
}

export type ListAlgo = (input: ListInput) => Trace<ListState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

const DEFAULT = [1, 2, 3, 4, 5];

// ── 1. Iterative reversal (LC 206) ────────────────────────────────────────

const REVERSE_CODE = [
  "def reverse(head):",
  "    prev, cur = None, head",
  "    while cur:",
  "        nxt = cur.next        # 1. SAVE the rest of the list",
  "        cur.next = prev       # 2. flip this node's arrow",
  "        prev = cur            # 3. advance prev",
  "        cur = nxt             # 4. advance cur",
  "    return prev               # prev is the new head",
];

export const reverseList: ListAlgo = (input) => {
  const values = input.values ?? DEFAULT;
  const t = tracer<ListState>(REVERSE_CODE);

  // Nodes keep their original slot for the whole trace. Only arrows move, which
  // is exactly the point being taught.
  const nodes: ListNode[] = values.map((v, i) => ({ id: i, value: v, slot: i }));
  const next = new Map<number, number | null>(values.map((_, i) => [i, i + 1 < values.length ? i + 1 : null]));

  const links = (): ListLink[] =>
    [...next.entries()].map(([from, to]) => ({
      from,
      to,
      tone: (to !== null && to < from ? "good" : "muted") as Tone,
    }));

  const state = (cursors: ListCursor[], marks: Record<number, Tone> = {}): ListState => ({
    nodes: nodes.map((n) => ({ ...n, tone: marks[n.id] })),
    links: links(),
    cursors,
    slots: values.length,
  });

  let prev: number | null = null;
  let cur: number | null = 0;

  t.push(
    state([
      { name: "prev", node: null, tone: "muted" },
      { name: "cur", node: cur, tone: "active" },
    ]),
    `Three pointers, and the order of the four assignments inside the loop is everything. prev starts at null because the old head becomes the new tail — its next must end up pointing at nothing.`,
    { line: 2, phase: "setup", watch: [w("prev", "None", "muted"), w("cur", values[0], "active")] },
  );

  while (cur !== null) {
    // Annotated explicitly: `cur = nxt` below makes cur's type depend on nxt's,
    // and nxt's on cur's, which TypeScript reports as a circular inference.
    const nxt: number | null = next.get(cur)!;

    t.push(
      state(
        [
          { name: "prev", node: prev, tone: "good" },
          { name: "cur", node: cur, tone: "active" },
          { name: "nxt", node: nxt, tone: "warn" },
        ],
        { [cur]: "active", ...(nxt !== null ? { [nxt]: "warn" } : {}) },
      ),
      `Step 1 — save "cur.next" in nxt${nxt === null ? " (which is null here, the last node)" : ""}. This has to happen **first**: the very next line overwrites cur.next, and without the save the rest of the list becomes unreachable. This one line is why the reversal is not a one-liner.`,
      {
        line: 4,
        phase: "save",
        watch: [
          w("prev", prev === null ? "None" : values[prev], "good"),
          w("cur", values[cur], "active"),
          w("nxt", nxt === null ? "None" : values[nxt], "warn"),
        ],
      },
    );

    next.set(cur, prev);

    t.push(
      state(
        [
          { name: "prev", node: prev, tone: "good" },
          { name: "cur", node: cur, tone: "good" },
          { name: "nxt", node: nxt, tone: "warn" },
        ],
        { [cur]: "good" },
      ),
      `Step 2 — flip the arrow: ${values[cur]} now points ${prev === null ? "at null, making it the new tail" : `back at ${values[prev]}`}. The list is temporarily broken in two halves, which is fine; nxt is holding the other half.`,
      { line: 5, phase: "flip", watch: [w("flipped", values[cur], "good")] },
    );

    prev = cur;
    cur = nxt;

    t.push(
      state([
        { name: "prev", node: prev, tone: "good" },
        { name: "cur", node: cur, tone: "active" },
      ]),
      `Steps 3 and 4 — walk both pointers forward one node. ${
        cur === null
          ? "cur is now null, so the loop ends and prev is the new head."
          : `prev is ${values[prev]}, cur is ${values[cur]}.`
      }`,
      {
        line: 7,
        phase: "advance",
        watch: [
          w("prev", values[prev], "good"),
          w("cur", cur === null ? "None" : values[cur], "active"),
        ],
      },
    );
  }

  t.push(
    state([{ name: "head", node: prev, tone: "good" }], Object.fromEntries(nodes.map((n) => [n.id, "good" as Tone]))),
    `Reversed in one pass: O(n) time, O(1) space, and no new nodes allocated. Return prev, not head — head is now the tail, and returning it gives you a one-element list, which is the classic wrong answer here.`,
    { line: 8, phase: "answer", watch: [w("new head", values[values.length - 1], "good")] },
  );

  return capFrames(t.done(`[${[...values].reverse().join(" → ")}]`));
};

// ── 2. Floyd's cycle detection (LC 141 / 142) ────────────────────────────

const CYCLE_CODE = [
  "def detect_cycle(head):",
  "    slow = fast = head",
  "    while fast and fast.next:",
  "        slow = slow.next          # one step",
  "        fast = fast.next.next     # two steps",
  "        if slow is fast:",
  "            break                 # they met — a cycle exists",
  "    else:",
  "        return None               # fast fell off the end",
  "    slow = head                   # reset ONE pointer",
  "    while slow is not fast:       # now both move at one step",
  "        slow = slow.next",
  "        fast = fast.next",
  "    return slow                   # the cycle entrance",
];

export const cycleDetection: ListAlgo = (input) => {
  const values = input.values ?? [3, 2, 0, -4];
  const cycleAt = input.cycleAt ?? 1;
  const t = tracer<ListState>(CYCLE_CODE);

  const n = values.length;
  const nodes: ListNode[] = values.map((v, i) => ({ id: i, value: v, slot: i }));
  const nextOf = (i: number): number | null => (i + 1 < n ? i + 1 : cycleAt >= 0 ? cycleAt : null);

  const links: ListLink[] = values.map((_, i) => {
    const to = nextOf(i);
    // The wrap-around edge is drawn under the rail so it never crosses a node.
    return { from: i, to, under: to !== null && to <= i, tone: to !== null && to <= i ? "warn" : "muted" };
  });

  const state = (slow: number | null, fast: number | null, marks: Record<number, Tone> = {}): ListState => ({
    nodes: nodes.map((x) => ({ ...x, tone: marks[x.id] })),
    links,
    cursors: [
      { name: "slow", node: slow, tone: "active" },
      { name: "fast", node: fast, tone: "warn" },
    ],
    slots: n,
  });

  let slow: number | null = 0;
  let fast: number | null = 0;
  let steps = 0;
  let met = false;

  t.push(
    state(slow, fast),
    cycleAt >= 0
      ? `The tail links back to index ${cycleAt}, so this list has a cycle. Both pointers start at the head; the trick is only that one moves twice as fast.`
      : `No cycle here — the tail points at null. Watch fast run off the end.`,
    { line: 2, phase: "setup" },
  );

  while (fast !== null && nextOf(fast) !== null) {
    slow = nextOf(slow!);
    const mid = nextOf(fast)!;
    fast = nextOf(mid);
    steps += 1;

    if (fast === null) break;

    t.push(
      state(slow, fast, { [slow!]: "active", [fast]: "warn" }),
      slow === fast
        ? `slow and fast are on the same node. In a cycle the gap between them closes by exactly one per step, so a meeting is inevitable — and a meeting is only possible if the path loops.`
        : `slow is at ${values[slow!]}, fast at ${values[fast]}. Each step the gap between them changes by one, which is why fast cannot "jump over" slow inside the loop.`,
      {
        line: 5,
        phase: "chase",
        watch: [w("slow", values[slow!], "active"), w("fast", values[fast], "warn"), w("steps", steps)],
      },
    );

    if (slow === fast) {
      met = true;
      break;
    }
  }

  if (!met) {
    t.push(
      state(slow, null, Object.fromEntries(nodes.map((x) => [x.id, "muted" as Tone]))),
      `fast reached the end of the list. Only a null-terminated list lets that happen, so there is no cycle — return None. Note this is why the loop tests both fast and fast.next: skipping either check crashes on an even-length list.`,
      { line: 9, phase: "answer", watch: [w("result", "None", "good")] },
    );
    return capFrames(t.done("no cycle"));
  }

  // Phase 2 — find the entrance.
  t.push(
    state(0, fast, { [0]: "active" }),
    `Now the surprising half. Reset slow to the head and move **both** pointers one step at a time. They will meet exactly at the cycle entrance. The reason: when they met, fast had travelled twice as far, and working through the algebra makes the distance from the head to the entrance equal to the distance from the meeting point to the entrance.`,
    { line: 10, phase: "reset", watch: [w("slow", "reset to head", "active")] },
  );

  slow = 0;
  while (slow !== fast) {
    slow = nextOf(slow!);
    fast = nextOf(fast!);
    t.push(
      state(slow, fast, { [slow!]: "active", [fast!]: "warn" }),
      slow === fast
        ? `They meet at ${values[slow!]} — index ${slow}, the node where the cycle begins.`
        : `Both advance one step: slow at ${values[slow!]}, fast at ${values[fast!]}.`,
      { line: 13, phase: "converge", watch: [w("slow", values[slow!], "active"), w("fast", values[fast!], "warn")] },
    );
  }

  t.push(
    state(slow, fast, { [slow!]: "good" }),
    `Cycle entrance is index ${slow} (value ${values[slow!]}). Whole thing is O(n) time and **O(1) space** — a hash set of visited nodes also works and is easier to explain, but costs O(n) memory, and the O(1) requirement is usually the point of the question.`,
    { line: 14, phase: "answer", watch: [w("entrance", values[slow!], "good")] },
  );

  return capFrames(t.done(`cycle begins at index ${slow} (value ${values[slow!]})`));
};

// ── 3. Merge two sorted lists with a dummy head (LC 21) ──────────────────

const MERGE_CODE = [
  "def merge(a, b):",
  "    dummy = tail = ListNode(0)   # dummy avoids an empty-list special case",
  "    while a and b:",
  "        if a.val <= b.val:       # <= keeps the merge STABLE",
  "            tail.next = a; a = a.next",
  "        else:",
  "            tail.next = b; b = b.next",
  "        tail = tail.next",
  "    tail.next = a or b           # attach whatever is left, in one line",
  "    return dummy.next",
];

export const mergeTwoLists: ListAlgo = (input) => {
  const A = input.values ?? [1, 3, 5];
  const B = input.other ?? [2, 4, 6];
  const t = tracer<ListState>(MERGE_CODE);

  // Node ids: dummy is -1, list A is 0..A.length-1, list B is offset after it.
  const OFF = A.length;
  const label = (id: number) => (id === -1 ? "∅" : id < OFF ? String(A[id]) : String(B[id - OFF]));

  const merged: number[] = [];
  let i = 0;
  let j = 0;

  const state = (focus?: number): ListState => {
    const total = merged.length + 1;
    return {
      nodes: [
        { id: -1, value: "dummy", slot: 0, tone: "muted" },
        ...merged.map((id, k) => ({
          id,
          value: label(id),
          slot: k + 1,
          tone: (id === focus ? "good" : "muted") as Tone,
        })),
      ],
      links: [
        ...[-1, ...merged].slice(0, total).map((id, k) => ({
          from: id,
          to: k < merged.length ? merged[k] : null,
          tone: "good" as Tone,
        })),
      ],
      cursors: [{ name: "tail", node: merged.length ? merged[merged.length - 1] : -1, tone: "active" }],
      slots: A.length + B.length + 1,
      second: {
        label: "remaining",
        nodes: [
          ...A.slice(i).map((v, k) => ({ id: 1000 + k, value: `a:${v}`, slot: k, tone: (k === 0 ? "active" : "info") as Tone })),
          ...B.slice(j).map((v, k) => ({ id: 2000 + k, value: `b:${v}`, slot: A.length - i + k, tone: (k === 0 ? "warn" : "info") as Tone })),
        ],
        links: [],
      },
    };
  };

  t.push(
    state(),
    `The dummy node is the whole technique. Without it, the first append needs a special case ("is the result empty yet?"), and that branch is where linked-list code goes wrong. With it, "tail.next = x" is unconditionally correct, and the real head is just "dummy.next" at the end.`,
    { line: 2, phase: "setup", watch: [w("a", A.join(","), "active"), w("b", B.join(","), "warn")] },
  );

  while (i < A.length && j < B.length) {
    // `<=` rather than `<`: taking from A on a tie is what makes the merge stable.
    const takeA = A[i] <= B[j];
    const id = takeA ? i : OFF + j;
    merged.push(id);
    if (takeA) i += 1;
    else j += 1;

    t.push(
      state(id),
      `${takeA ? A[i - 1] : B[j - 1]} from list ${takeA ? "a" : "b"} is the smaller head, so it is appended and that list advances. The comparison is "<=" and not "<" deliberately: on a tie, taking from a preserves the relative order of equal values, which is what "stable" means.`,
      {
        line: takeA ? 5 : 7,
        phase: "append",
        watch: [
          w("a head", i < A.length ? A[i] : "∅", "active"),
          w("b head", j < B.length ? B[j] : "∅", "warn"),
          w("took", takeA ? A[i - 1] : B[j - 1], "good"),
        ],
      },
    );
  }

  const restFrom = i < A.length ? "a" : j < B.length ? "b" : null;
  while (i < A.length) merged.push(i++);
  while (j < B.length) merged.push(OFF + j++);

  t.push(
    state(),
    restFrom
      ? `One list is exhausted. Because the other is already sorted, its whole remainder can be attached in a single assignment — no loop needed. "tail.next = a or b" handles both cases and the both-empty case at once.`
      : `Both lists ran out at the same time, so there is nothing left to attach.`,
    { line: 9, phase: "attach" },
  );

  const out = merged.map(label);
  t.push(
    state(),
    `Merged: ${out.join(" → ")}. O(m + n) time, O(1) extra space — no nodes were allocated except the dummy, and the result is built by relinking the originals. Returning "dummy" instead of "dummy.next" is the standard off-by-one here.`,
    { line: 10, phase: "answer", watch: [w("length", out.length, "good")] },
  );

  return capFrames(t.done(`[${out.join(" → ")}]`));
};

// ── 4. Remove the nth node from the end (LC 19) ──────────────────────────

const NTH_CODE = [
  "def remove_nth_from_end(head, n):",
  "    dummy = ListNode(0, head)     # so deleting the head needs no special case",
  "    lead = lag = dummy",
  "    for _ in range(n):            # open a gap of exactly n",
  "        lead = lead.next",
  "    while lead.next:              # walk both until lead hits the last node",
  "        lead = lead.next",
  "        lag = lag.next",
  "    lag.next = lag.next.next      # lag is now just BEFORE the target",
  "    return dummy.next",
];

export const removeNthFromEnd: ListAlgo = (input) => {
  const values = input.values ?? DEFAULT;
  const n = Math.max(1, Math.min(input.k ?? 2, values.length));
  const t = tracer<ListState>(NTH_CODE);

  const nodes: ListNode[] = [
    { id: -1, value: "dummy", slot: 0, tone: "muted" },
    ...values.map((v, i) => ({ id: i, value: v, slot: i + 1 })),
  ];
  const next = new Map<number, number | null>([
    [-1, values.length ? 0 : null],
    ...values.map((_, i): [number, number | null] => [i, i + 1 < values.length ? i + 1 : null]),
  ]);

  const links = (): ListLink[] =>
    [...next.entries()].map(([from, to]) => ({ from, to, tone: "muted" as Tone }));

  const label = (id: number | null) => (id === null ? "∅" : id === -1 ? "dummy" : String(values[id]));

  const state = (lead: number | null, lag: number | null, marks: Record<number, Tone> = {}): ListState => ({
    nodes: nodes.map((x) => ({ ...x, tone: marks[x.id] ?? x.tone })),
    links: links(),
    cursors: [
      { name: "lag", node: lag, tone: "active" },
      { name: "lead", node: lead, tone: "warn" },
    ],
    slots: values.length + 1,
  });

  let lead: number | null = -1;
  let lag: number | null = -1;

  t.push(
    state(lead, lag),
    `A single pass, using a fixed gap between two pointers. The dummy matters here more than usual: if the node to remove *is* the head, lag needs somewhere to stand before it.`,
    { line: 3, phase: "setup", watch: [w("n", n, "warn")] },
  );

  for (let k = 0; k < n; k++) {
    lead = next.get(lead!)!;
    t.push(
      state(lead, lag, { ...(lead !== null ? { [lead]: "warn" } : {}) }),
      `Advance lead ${k + 1} of ${n} times. The gap being opened now is exactly n, and it never changes again — that invariant is what makes the second loop land in the right place.`,
      { line: 5, phase: "open gap", watch: [w("gap", k + 1, "warn"), w("lead", label(lead))] },
    );
  }

  while (next.get(lead!) !== null) {
    lead = next.get(lead!)!;
    lag = next.get(lag!)!;
    t.push(
      state(lead, lag, { [lead!]: "warn", [lag!]: "active" }),
      `Both advance together, gap intact. lag is at ${label(lag)}, lead at ${label(lead)}.`,
      { line: 8, phase: "walk", watch: [w("lag", label(lag), "active"), w("lead", label(lead), "warn")] },
    );
  }

  const target = next.get(lag!)!;
  t.push(
    state(lead, lag, { [target]: "bad", [lag!]: "active" }),
    `lead is on the last node, so lag sits exactly n nodes back — which puts it immediately **before** the node to delete, ${label(target)}. Landing *before* the target rather than on it is the reason the gap is opened from the dummy and not the head.`,
    { line: 9, phase: "found", watch: [w("delete", label(target), "bad")] },
  );

  next.set(lag!, next.get(target)!);
  t.push(
    state(null, lag, { [target]: "bad", [lag!]: "good" }),
    `Relink past it. ${label(target)} is now unreachable — in Python that is all "deleting" means; the garbage collector handles the rest.`,
    { line: 9, phase: "unlink" },
  );

  const remaining = values.filter((_, i) => i !== target);
  t.push(
    { ...state(null, null), nodes: nodes.map((x) => ({ ...x, tone: x.id === target ? "muted" : "good" })) },
    `Result: ${remaining.join(" → ")}. One pass, O(1) space. Returning "dummy.next" rather than "head" is what makes removing the first node work — with n equal to the list length, head is the node that just got deleted.`,
    { line: 10, phase: "answer", watch: [w("length", remaining.length, "good")] },
  );

  return capFrames(t.done(`[${remaining.join(" → ")}]`));
};

/**
 * Registry. The `algo` prop of <LinkedListRewire> indexes this.
 *
 * | key                    | uses                    |
 * |------------------------|-------------------------|
 * | reverse                | values                  |
 * | cycle-detection        | values, cycleAt         |
 * | merge-two-lists        | values, other           |
 * | remove-nth-from-end    | values, k (= n)         |
 */
export const LIST_ALGOS: Record<string, ListAlgo> = {
  reverse: reverseList,
  "cycle-detection": cycleDetection,
  "merge-two-lists": mergeTwoLists,
  "remove-nth-from-end": removeNthFromEnd,
};

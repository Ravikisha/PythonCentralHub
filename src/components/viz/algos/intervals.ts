/**
 * algos/intervals.ts — traced interval algorithms for <IntervalTimeline>.
 *
 * Interval problems are the family where the *sort* is the algorithm. Merge
 * intervals, meeting rooms, and non-overlapping selection are all one sort
 * followed by a linear scan, and the only real decision is **what to sort by** —
 * start, end, or a split into separate start and end streams. Choosing wrong
 * gives plausible code that fails on a specific overlap shape.
 *
 * Drawing the intervals on a shared axis makes the choice visible: you can see
 * why sorting by end time is what makes greedy selection optimal.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

export interface IntervalBar {
  start: number;
  end: number;
  label?: string;
  tone?: Tone;
  /** Row to draw on. Overlapping bars must not share a row. */
  row: number;
}

export interface IntervalState {
  bars: IntervalBar[];
  /** Axis extent. Fixed for the whole trace so bars never rescale. */
  min: number;
  max: number;
  /** A vertical sweep line at this coordinate. */
  sweep?: number;
  /** Result bars, drawn in their own band under the axis. */
  result?: IntervalBar[];
  resultLabel?: string;
  legend?: { label: string; value: string; tone?: Tone }[];
}

export interface IntervalInput {
  /** `[[start, end], ...]`. */
  intervals?: [number, number][];
}

export type IntervalAlgo = (input: IntervalInput) => Trace<IntervalState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

const DEFAULT: [number, number][] = [
  [1, 3],
  [2, 6],
  [8, 10],
  [15, 18],
];

/** Pack bars onto rows greedily so no two overlapping bars collide. */
function assignRows(items: [number, number][]): number[] {
  const rowEnds: number[] = [];
  return items.map(([s, e]) => {
    const row = rowEnds.findIndex((end) => end < s);
    if (row === -1) {
      rowEnds.push(e);
      return rowEnds.length - 1;
    }
    rowEnds[row] = e;
    return row;
  });
}

// ── 1. Merge intervals (LC 56) ────────────────────────────────────────────

const MERGE_CODE = [
  "def merge(intervals):",
  "    intervals.sort()                    # by START — this is the algorithm",
  "    out = [intervals[0]]",
  "    for s, e in intervals[1:]:",
  "        if s <= out[-1][1]:             # overlaps the last kept interval",
  "            out[-1][1] = max(out[-1][1], e)",
  "        else:",
  "            out.append([s, e])",
  "    return out",
];

export const mergeIntervals: IntervalAlgo = (input) => {
  const raw = input.intervals?.length ? input.intervals : DEFAULT;
  const t = tracer<IntervalState>(MERGE_CODE);

  const sorted = [...raw].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const rows = assignRows(sorted);
  const min = Math.min(...sorted.map((i) => i[0]));
  const max = Math.max(...sorted.map((i) => i[1]));

  const out: [number, number][] = [];

  const state = (upto: number, focus?: number, mergedIdx?: number): IntervalState => ({
    bars: sorted.map(([s, e], i) => ({
      start: s,
      end: e,
      row: rows[i],
      label: `${s}–${e}`,
      tone: i === focus ? "active" : i < upto ? "muted" : "info",
    })),
    min,
    max,
    result: out.map(([s, e], i) => ({
      start: s,
      end: e,
      row: 0,
      label: `${s}–${e}`,
      tone: i === mergedIdx ? "good" : "warn",
    })),
    resultLabel: "merged",
    legend: [{ label: "merged count", value: String(out.length), tone: "good" }],
  });

  t.push(
    state(0),
    `Sorted by start time. That sort is what makes a single linear pass sufficient: once the intervals are in start order, any interval that overlaps an earlier one must overlap the **most recent** kept interval, so only one comparison per step is needed.`,
    { line: 2, phase: "sorted" },
  );

  out.push([...sorted[0]] as [number, number]);
  t.push(
    state(1, 0, 0),
    `Take ${sorted[0][0]}–${sorted[0][1]} as the first kept interval.`,
    { line: 3, phase: "seed", watch: [w("kept", `${sorted[0][0]}–${sorted[0][1]}`, "good")] },
  );

  for (let i = 1; i < sorted.length; i++) {
    const [s, e] = sorted[i];
    const last = out[out.length - 1];
    const overlaps = s <= last[1];

    if (overlaps) {
      const before = last[1];
      last[1] = Math.max(last[1], e);
      t.push(
        state(i + 1, i, out.length - 1),
        `${s}–${e} starts at ${s}, which is ≤ the current interval's end ${before} — they touch or overlap, so absorb it. The end becomes max(${before}, ${e}) = ${last[1]}; taking max rather than ${e} matters when one interval is fully contained in another.`,
        {
          line: 6,
          phase: "merge",
          watch: [w("start", s, "active"), w("last end", before), w("new end", last[1], "good")],
        },
      );
    } else {
      out.push([s, e]);
      t.push(
        state(i + 1, i, out.length - 1),
        `${s}–${e} starts after the current interval ends at ${last[1]}, so there is a genuine gap. Start a new interval — and because of the sort, nothing later can reach back across that gap.`,
        { line: 8, phase: "new", watch: [w("gap after", last[1], "muted"), w("new interval", `${s}–${e}`, "good")] },
      );
    }
  }

  t.push(
    state(sorted.length),
    `${raw.length} intervals reduced to ${out.length}: ${out.map(([s, e]) => `[${s},${e}]`).join(", ")}. O(n log n) — dominated entirely by the sort, since the scan is O(n). Whenever you see an interval problem, the first question is what to sort by.`,
    { line: 9, phase: "answer", watch: [w("in", raw.length), w("out", out.length, "good")] },
  );

  return capFrames(t.done(out.map(([s, e]) => `[${s},${e}]`).join(", ")));
};

// ── 2. Meeting rooms II — sweep line (LC 253) ─────────────────────────────

const SWEEP_CODE = [
  "def min_meeting_rooms(intervals):",
  "    events = []",
  "    for s, e in intervals:",
  "        events.append((s, +1))          # a meeting starts",
  "        events.append((e, -1))          # a meeting ends",
  "    events.sort()                       # ends sort BEFORE starts at equal time",
  "    rooms = peak = 0",
  "    for _, delta in events:",
  "        rooms += delta",
  "        peak = max(peak, rooms)",
  "    return peak",
];

export const sweepLine: IntervalAlgo = (input) => {
  const raw = input.intervals?.length ? input.intervals : [
    [0, 30],
    [5, 10],
    [15, 20],
    [6, 12],
  ] as [number, number][];
  const t = tracer<IntervalState>(SWEEP_CODE);

  const rows = assignRows([...raw].sort((a, b) => a[0] - b[0]));
  const order = [...raw].map((v, i) => ({ v, i })).sort((a, b) => a.v[0] - b.v[0]);
  const rowOf = new Map(order.map((o, k) => [o.i, rows[k]]));

  const min = Math.min(...raw.map((i) => i[0]));
  const max = Math.max(...raw.map((i) => i[1]));

  /** `-1` before `+1` at equal time: a room freed at t is reusable at t. */
  const events = raw
    .flatMap(([s, e]): [number, number][] => [
      [s, 1],
      [e, -1],
    ])
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);

  let rooms = 0;
  let peak = 0;

  const state = (sweep?: number, focus?: number): IntervalState => ({
    bars: raw.map(([s, e], i) => ({
      start: s,
      end: e,
      row: rowOf.get(i) ?? 0,
      label: `${s}–${e}`,
      tone: sweep !== undefined && s <= sweep && e > sweep ? "active" : "info",
    })),
    min,
    max,
    sweep,
    legend: [
      { label: "rooms in use", value: String(rooms), tone: "active" },
      { label: "peak", value: String(peak), tone: "good" },
    ],
  });

  t.push(
    state(),
    `Forget the intervals as objects. Split each into two **events** — a +1 when it starts and a −1 when it ends — then sort all the events by time. The answer is the maximum the running total ever reaches, and no interval is ever compared with another.`,
    { line: 6, phase: "setup", watch: [w("events", events.length)] },
  );

  for (const [time, delta] of events) {
    rooms += delta;
    peak = Math.max(peak, rooms);
    t.push(
      state(time),
      delta > 0
        ? `t = ${time}: a meeting starts, so rooms in use rises to ${rooms}.${rooms === peak ? ` That is a new peak.` : ""}`
        : `t = ${time}: a meeting ends, so rooms in use falls to ${rooms}. Note the sort puts ends before starts at the same instant — a room vacated at ${time} is available at ${time}, and getting that tie-break wrong inflates the answer by one.`,
      {
        line: delta > 0 ? 9 : 10,
        phase: delta > 0 ? "start" : "end",
        watch: [w("t", time, "active"), w("delta", delta > 0 ? "+1" : "−1", delta > 0 ? "warn" : "good"), w("rooms", rooms, "active"), w("peak", peak, "good")],
      },
    );
  }

  t.push(
    state(),
    `${peak} rooms needed. The sweep never asks "does interval A overlap interval B" — it only counts, which is why it is O(n log n) rather than the O(n²) a pairwise-overlap solution costs. The same event-counting idea solves "maximum concurrent anything".`,
    { line: 11, phase: "answer", watch: [w("answer", peak, "good")] },
  );

  return capFrames(t.done(`${peak} rooms`));
};

// ── 3. Non-overlapping selection — greedy by END time (LC 435) ────────────

const GREEDY_CODE = [
  "def max_non_overlapping(intervals):",
  "    intervals.sort(key=lambda x: x[1])   # by END time — not start",
  "    count, last_end = 0, -inf",
  "    for s, e in intervals:",
  "        if s >= last_end:                # compatible with what we kept",
  "            count += 1",
  "            last_end = e",
  "    return count",
];

export const greedySelect: IntervalAlgo = (input) => {
  const raw = input.intervals?.length ? input.intervals : [
    [1, 4],
    [2, 3],
    [3, 6],
    [5, 7],
    [8, 9],
  ] as [number, number][];
  const t = tracer<IntervalState>(GREEDY_CODE);

  const sorted = [...raw].sort((a, b) => a[1] - b[1]);
  const rows = assignRows(sorted);
  const min = Math.min(...sorted.map((i) => i[0]));
  const max = Math.max(...sorted.map((i) => i[1]));

  const kept: [number, number][] = [];
  let lastEnd = -Infinity;

  const state = (focus?: number, keepIt?: boolean): IntervalState => ({
    bars: sorted.map(([s, e], i) => ({
      start: s,
      end: e,
      row: rows[i],
      label: `${s}–${e}`,
      tone:
        i === focus
          ? keepIt === undefined
            ? "active"
            : keepIt
              ? "good"
              : "bad"
          : kept.some(([ks, ke]) => ks === s && ke === e)
            ? "good"
            : i < (focus ?? 0)
              ? "muted"
              : "info",
    })),
    min,
    max,
    sweep: lastEnd === -Infinity ? undefined : lastEnd,
    result: kept.map(([s, e]) => ({ start: s, end: e, row: 0, label: `${s}–${e}`, tone: "good" })),
    resultLabel: "kept",
    legend: [
      { label: "kept", value: String(kept.length), tone: "good" },
      { label: "last end", value: lastEnd === -Infinity ? "−∞" : String(lastEnd), tone: "warn" },
    ],
  });

  t.push(
    state(),
    `Sorted by **end** time, and that choice is the entire insight. Sorting by start time is the intuitive move and it is wrong: a long interval starting early can block several short ones. Finishing earliest leaves the most room for whatever comes next.`,
    { line: 2, phase: "sorted" },
  );

  for (let i = 0; i < sorted.length; i++) {
    const [s, e] = sorted[i];
    const compatible = s >= lastEnd;

    t.push(
      state(i),
      `Consider ${s}–${e}. It ${compatible ? "starts at or after" : "starts before"} the last kept end (${lastEnd === -Infinity ? "nothing kept yet" : lastEnd}), so it ${compatible ? "is compatible" : "conflicts"}.`,
      {
        line: 5,
        phase: "consider",
        watch: [w("start", s, "active"), w("last end", lastEnd === -Infinity ? "−∞" : lastEnd, "warn"), w("compatible", compatible ? "yes" : "no", compatible ? "good" : "bad")],
      },
    );

    if (compatible) {
      kept.push([s, e]);
      lastEnd = e;
      t.push(
        state(i, true),
        `Keep it. Because it was the earliest-finishing compatible option available, no alternative choice could leave more room — that exchange argument is what makes the greedy provably optimal rather than merely plausible.`,
        { line: 7, phase: "keep", watch: [w("kept", kept.length, "good"), w("last end", lastEnd, "warn")] },
      );
    } else {
      t.push(
        state(i, false),
        `Skip it. Swapping it for what we already kept could not improve the count, since it finishes no earlier.`,
        { line: 4, phase: "skip", watch: [w("kept", kept.length, "good")] },
      );
    }
  }

  t.push(
    state(),
    `${kept.length} non-overlapping intervals kept out of ${raw.length}, so ${raw.length - kept.length} must be removed. O(n log n) for the sort. Sorting by end time is the single fact to remember from this pattern — it also solves activity selection and the "burst balloons with arrows" family.`,
    { line: 8, phase: "answer", watch: [w("kept", kept.length, "good"), w("removed", raw.length - kept.length, "bad")] },
  );

  return capFrames(t.done(`${kept.length} kept, ${raw.length - kept.length} removed`));
};

/**
 * Registry. The `algo` prop of <IntervalTimeline> indexes this.
 *
 * | key             | uses      |
 * |-----------------|-----------|
 * | merge           | intervals |
 * | sweep-line      | intervals |
 * | greedy-select   | intervals |
 */
export const INTERVAL_ALGOS: Record<string, IntervalAlgo> = {
  merge: mergeIntervals,
  "sweep-line": sweepLine,
  "greedy-select": greedySelect,
};

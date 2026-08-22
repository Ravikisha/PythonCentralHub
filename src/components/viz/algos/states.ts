/**
 * algos/states.ts — traced state machines for <StateMachineView>.
 *
 * Some DP problems are far clearer as a state machine than as a table. "Best time
 * to buy and sell stock with cooldown" has three states and five transitions, and
 * once drawn that way the recurrence writes itself — whereas the table form
 * requires holding an arbitrary-looking `dp[i][2]` in your head.
 *
 * Emits GraphState, so `<StateMachineView>` renders through `GraphStage`. A state
 * machine is a directed graph with per-node values; nothing new to draw.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";
import type { GraphEdgeView, GraphLayoutNode, GraphState } from "./graphs";

export interface StateInput {
  /** Daily prices for the stock machines. */
  values?: number[];
  /** Transaction fee for the fee variant; forbidden digit for `digit-dp`. */
  target?: number;
  /** The bound N, as a digit string, for `digit-dp`. */
  text?: string;
}

export type StateAlgo = (input: StateInput) => Trace<GraphState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

const fmt = (v: number) => (v === -Infinity ? "−∞" : String(v));

// ── Stock trading with a cooldown (LC 309) ────────────────────────────────

const COOLDOWN_CODE = [
  "def max_profit(prices):",
  "    hold = -prices[0]      # own a share",
  "    sold = 0               # just sold — must cool down",
  "    rest = 0               # free to buy",
  "    for p in prices[1:]:",
  "        prev_sold = sold",
  "        sold = hold + p            # sell today",
  "        hold = max(hold, rest - p) # keep holding, or buy today",
  "        rest = max(rest, prev_sold)  # stay free, or finish cooling down",
  "    return max(sold, rest)",
];

/** Three states, laid out left to right in the order money flows through them. */
const COOLDOWN_LAYOUT: GraphLayoutNode[] = [
  { id: "rest", x: 0, y: 0 },
  { id: "hold", x: 1, y: 1 },
  { id: "sold", x: 2, y: 0 },
];

const COOLDOWN_EDGES: GraphEdgeView[] = [
  { from: "rest", to: "hold", directed: true, label: "buy −p" },
  { from: "hold", to: "sold", directed: true, label: "sell +p" },
  { from: "sold", to: "rest", directed: true, label: "cooldown" },
  { from: "rest", to: "rest", directed: true, label: "idle" },
  { from: "hold", to: "hold", directed: true, label: "keep" },
];

export const stockCooldown: StateAlgo = (input) => {
  const prices = input.values?.length ? input.values : [1, 2, 3, 0, 2];
  const t = tracer<GraphState>(COOLDOWN_CODE);

  let hold = -prices[0];
  let sold = 0;
  let rest = 0;

  const state = (marks: Record<string, Tone> = {}, day?: number): GraphState => ({
    nodes: COOLDOWN_LAYOUT,
    edges: COOLDOWN_EDGES,
    marks: { rest: "info", hold: "info", sold: "info", ...marks },
    notes: {
      rest: fmt(rest),
      hold: fmt(hold),
      sold: fmt(sold),
    },
    output:
      day === undefined
        ? []
        : prices.map((p, i) => ({
            text: String(p),
            tone: (i === day ? "active" : i < day ? "muted" : "info") as Tone,
          })),
    cols: 3,
    rows: 2,
  });

  t.push(
    state({ hold: "active" }),
    `Three states, and the transitions between them *are* the recurrence. On day 0 the only meaningful choice is to buy or not: holding costs ${prices[0]}, so hold = −${prices[0]}. Being in "sold" or "rest" with no trades yet is worth 0.`,
    { line: 4, phase: "day 0", watch: [w("hold", hold, "active"), w("sold", sold), w("rest", rest)] },
  );

  for (let i = 1; i < prices.length; i++) {
    const p = prices[i];
    const prevSold = sold;
    const prevHold = hold;
    const prevRest = rest;

    sold = prevHold + p;
    hold = Math.max(prevHold, prevRest - p);
    rest = Math.max(prevRest, prevSold);

    t.push(
      state({ hold: "warn", sold: "good", rest: "info" }, i),
      `Day ${i}, price ${p}. **sold** can only be reached by selling today, so sold = hold + ${p} = ${fmt(sold)}. **hold** is either keeping (${fmt(prevHold)}) or buying from rest (${fmt(prevRest)} − ${p}), so ${fmt(hold)}. **rest** is staying free (${fmt(prevRest)}) or arriving from yesterday's sold (${fmt(prevSold)}), so ${fmt(rest)}.`,
      {
        line: 9,
        phase: `day ${i}`,
        watch: [w("price", p, "active"), w("hold", fmt(hold), "warn"), w("sold", fmt(sold), "good"), w("rest", fmt(rest))],
      },
    );

    t.push(
      state({ sold: sold >= rest ? "good" : "muted", rest: rest > sold ? "good" : "muted" }, i),
      `Note that **rest** reads *yesterday's* sold, not today's — the cooldown is exactly that one-day lag, and it is the whole reason a "prev_sold" temporary is needed. Overwrite sold first and the cooldown silently disappears.`,
      { line: 9, phase: `day ${i}`, watch: [w("cooldown lag", "1 day", "warn")] },
    );
  }

  const answer = Math.max(sold, rest);
  t.push(
    state({ [sold >= rest ? "sold" : "rest"]: "good" }),
    `Answer: ${answer}. The final state must not be **hold** — ending while still owning a share means the money was never realised. O(n) time, O(1) space: three numbers, no table. Adding a transaction fee or a trade limit means adding a transition or a dimension, not rethinking the problem, which is the real advantage of the state-machine framing.`,
    { line: 10, phase: "answer", watch: [w("max profit", answer, "good")] },
  );

  return capFrames(t.done(`max profit = ${answer}`));
};

// ── Stock trading with unlimited transactions (LC 122) ───────────────────

const SIMPLE_CODE = [
  "def max_profit(prices):",
  "    hold, free = -prices[0], 0",
  "    for p in prices[1:]:",
  "        hold = max(hold, free - p)   # keep, or buy today",
  "        free = max(free, hold + p)   # stay out, or sell today",
  "    return free",
];

const SIMPLE_LAYOUT: GraphLayoutNode[] = [
  { id: "free", x: 0, y: 0 },
  { id: "hold", x: 1, y: 0 },
];

const SIMPLE_EDGES: GraphEdgeView[] = [
  { from: "free", to: "hold", directed: true, label: "buy −p" },
  { from: "hold", to: "free", directed: true, label: "sell +p" },
  { from: "free", to: "free", directed: true, label: "wait" },
  { from: "hold", to: "hold", directed: true, label: "keep" },
];

export const stockUnlimited: StateAlgo = (input) => {
  const prices = input.values?.length ? input.values : [7, 1, 5, 3, 6, 4];
  const t = tracer<GraphState>(SIMPLE_CODE);

  let hold = -prices[0];
  let free = 0;

  const state = (marks: Record<string, Tone> = {}, day?: number): GraphState => ({
    nodes: SIMPLE_LAYOUT,
    edges: SIMPLE_EDGES,
    marks: { free: "info", hold: "info", ...marks },
    notes: { free: fmt(free), hold: fmt(hold) },
    output:
      day === undefined
        ? []
        : prices.map((p, i) => ({
            text: String(p),
            tone: (i === day ? "active" : i < day ? "muted" : "info") as Tone,
          })),
    cols: 2,
    rows: 1,
  });

  t.push(
    state({ hold: "active" }),
    `Two states only, because with unlimited transactions and no cooldown you are either holding a share or you are not. Every day you choose an edge.`,
    { line: 2, phase: "day 0", watch: [w("hold", hold, "active"), w("free", free)] },
  );

  for (let i = 1; i < prices.length; i++) {
    const p = prices[i];
    const prevHold = hold;
    hold = Math.max(hold, free - p);
    // Reading the just-updated `hold` is safe here — and is what allows a buy and
    // a sell on the same day, which unlimited transactions permits.
    free = Math.max(free, hold + p);

    t.push(
      state({ hold: hold > prevHold ? "good" : "warn", free: "good" }, i),
      `Day ${i}, price ${p}. hold = max(keep ${fmt(prevHold)}, buy ${fmt(free)} − ${p}) = ${fmt(hold)}; free = max(stay ${fmt(free)}, sell ${fmt(hold)} + ${p}) = ${fmt(free)}.`,
      {
        line: 5,
        phase: `day ${i}`,
        watch: [w("price", p, "active"), w("hold", fmt(hold), "warn"), w("free", fmt(free), "good")],
      },
    );
  }

  t.push(
    state({ free: "good" }),
    `Answer: ${free}. Unlike the cooldown version this one has a famous one-liner — sum every positive difference between consecutive days — and the two are equivalent. The state machine is worth knowing anyway, because the moment a fee, a cooldown or a trade limit is added the greedy one-liner stops working and this does not.`,
    { line: 6, phase: "answer", watch: [w("max profit", free, "good")] },
  );

  return capFrames(t.done(`max profit = ${free}`));
};

// ── Digit DP: counting numbers in [0, N] (tight vs free) ─────────────────

const DIGIT_CODE = [
  "def count(N: str, bad: str) -> int:",
  "    tight, free = 1, 0        # one tight prefix: the empty one",
  "    for ch in N:",
  "        d = int(ch)",
  "        below = sum(1 for x in range(d) if str(x) != bad)",
  "        free = free * 9 + tight * below   # free stays free; tight breaks free",
  "        tight = tight if ch != bad else 0",
  "    return tight + free       # + tight counts N itself",
];

/**
 * One column per digit position, two rows: the tight prefix (row 0) and the free
 * prefixes (row 1). Digit DP is genuinely a two-state machine walked left to
 * right, and the whole difficulty of the pattern — "when does tight stop being
 * tight, and why is there only ever one tight prefix" — is a property of this
 * picture rather than of the code.
 */
export const digitDp: StateAlgo = (input) => {
  const digits = (input.text && /^\d+$/.test(input.text) ? input.text : "325").slice(0, 6);
  const bad = String(input.target ?? 4).slice(-1);
  const n = digits.length;
  const t = tracer<GraphState>(DIGIT_CODE);

  const nodes: GraphLayoutNode[] = [];
  for (let i = 0; i <= n; i++) {
    nodes.push({ id: `T${i}`, x: i, y: 0 });
    nodes.push({ id: `F${i}`, x: i, y: 1 });
  }

  // Counts per column, filled in as the walk proceeds. -1 means "not yet reached".
  const tightAt: number[] = Array(n + 1).fill(-1);
  const freeAt: number[] = Array(n + 1).fill(-1);
  tightAt[0] = 1;
  freeAt[0] = 0;

  const edgesFor = (col: number): GraphEdgeView[] => {
    const out: GraphEdgeView[] = [];
    for (let i = 0; i < n; i++) {
      const d = Number(digits[i]);
      const below = Array.from({ length: d }, (_, x) => x).filter((x) => String(x) !== bad).length;
      const live = i === col;
      const blocked = digits[i] === bad;
      out.push({
        from: `T${i}`,
        to: `T${i + 1}`,
        directed: true,
        label: blocked ? `= ${digits[i]} ✗` : `= ${digits[i]}`,
        tone: blocked ? "bad" : live ? "active" : "muted",
      });
      out.push({
        from: `T${i}`,
        to: `F${i + 1}`,
        directed: true,
        label: `< ${digits[i]} (${below})`,
        tone: live ? "good" : "muted",
      });
      out.push({
        from: `F${i}`,
        to: `F${i + 1}`,
        directed: true,
        label: "×9",
        tone: live ? "warn" : "muted",
      });
    }
    return out;
  };

  const state = (col: number, marks: Record<string, Tone> = {}): GraphState => {
    const notes: Record<string, string> = {};
    const base: Record<string, Tone> = {};
    for (let i = 0; i <= n; i++) {
      notes[`T${i}`] = tightAt[i] < 0 ? "·" : String(tightAt[i]);
      notes[`F${i}`] = freeAt[i] < 0 ? "·" : String(freeAt[i]);
      base[`T${i}`] = tightAt[i] < 0 ? "muted" : "info";
      base[`F${i}`] = freeAt[i] < 0 ? "muted" : "info";
    }
    return {
      nodes,
      edges: edgesFor(col),
      marks: { ...base, ...marks },
      notes,
      output: digits.split("").map((ch, i) => ({
        text: ch,
        tone: (i === col ? "active" : i < col ? "muted" : "info") as Tone,
      })),
      cols: n + 1,
      rows: 2,
    };
  };

  t.push(
    state(0, { T0: "active" }),
    `Counting how many integers in [0, ${digits}] contain no digit ${bad}, by scanning the bound **left to right** and tracking only two things: how many prefixes so far are still equal to ${digits}'s prefix (**tight**, row 0) and how many have already dropped below it (**free**, row 1). Before any digit is placed there is exactly one tight prefix — the empty one — and no free prefix.`,
    { line: 2, phase: "start", watch: [w("tight", 1, "active"), w("free", 0), w("forbidden", bad, "bad")] },
  );

  for (let i = 0; i < n; i++) {
    const d = Number(digits[i]);
    const below = Array.from({ length: d }, (_, x) => x).filter((x) => String(x) !== bad).length;
    const prevTight = tightAt[i];
    const prevFree = freeAt[i];

    freeAt[i + 1] = prevFree * 9 + prevTight * below;
    tightAt[i + 1] = digits[i] === bad ? 0 : prevTight;

    t.push(
      state(i, {
        [`F${i + 1}`]: "good",
        [`T${i + 1}`]: tightAt[i + 1] > 0 ? "active" : "bad",
      }),
      `Position ${i}, bound digit **${digits[i]}**. A free prefix may take any of the 9 allowed digits, so it contributes ${prevFree} × 9 = ${prevFree * 9}. The tight prefix may drop below the bound by choosing any allowed digit under ${digits[i]} — there are ${below} of those — which contributes ${prevTight} × ${below} = ${
        prevTight * below
      } and lands in **free**. Total free = ${freeAt[i + 1]}. ${
        digits[i] === bad
          ? `Matching the bound digit here would place a ${bad}, which is forbidden, so the tight branch **dies**: tight = 0. Every remaining count from now on comes from free.`
          : `Matching ${digits[i]} keeps the prefix tight, so tight stays ${tightAt[i + 1]} — there is only ever *one* tight prefix, which is why this is O(n) and not exponential.`
      }`,
      {
        line: 6,
        phase: `digit ${i}`,
        watch: [
          w("bound digit", digits[i], "active"),
          w("allowed below", below, "good"),
          w("tight", tightAt[i + 1], tightAt[i + 1] > 0 ? "active" : "bad"),
          w("free", freeAt[i + 1], "good"),
        ],
      },
    );
  }

  const answer = tightAt[n] + freeAt[n];
  t.push(
    state(n, { [`T${n}`]: tightAt[n] > 0 ? "good" : "muted", [`F${n}`]: "good" }),
    `Answer: ${freeAt[n]} free + ${tightAt[n]} tight = **${answer}**. The surviving tight count is ${digits} itself, which is why the bound is inclusive at no extra cost — and why dropping the "+ tight" is the classic off-by-one. Leading zeros were allowed throughout, so 0 is counted and short numbers are counted as zero-padded strings; a problem that forbids leading zeros needs a third bit of state.`,
    {
      line: 8,
      phase: "answer",
      watch: [w("free", freeAt[n], "good"), w("tight", tightAt[n]), w("answer", answer, "good")],
    },
  );

  return capFrames(t.done(`${answer} numbers in [0, ${digits}] avoid the digit ${bad}`));
};

/**
 * Registry. The `algo` prop of <StateMachineView> indexes this.
 *
 * | key              | uses           |
 * |------------------|----------------|
 * | stock-unlimited  | values         |
 * | stock-cooldown   | values         |
 * | digit-dp         | text, target   |
 */
export const STATE_ALGOS: Record<string, StateAlgo> = {
  "stock-unlimited": stockUnlimited,
  "stock-cooldown": stockCooldown,
  "digit-dp": digitDp,
};

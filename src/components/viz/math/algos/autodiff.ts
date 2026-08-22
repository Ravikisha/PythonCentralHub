/**
 * algos/autodiff.ts — reverse-mode automatic differentiation on a computation
 * graph, one node per frame.
 *
 * §5.6 makes a claim that is easy to state and hard to believe: computing the
 * derivative costs about the same as computing the function, even though the
 * symbolic expression for the derivative is far uglier than the function. The
 * book's own words for Example 5.14 are that "the computation required for
 * calculating the derivative is of similar complexity as the computation of the
 * function itself. This is quite counterintuitive."
 *
 * The way to make it believable is to count. This module records, per frame, how
 * many elementary operations the forward pass has used and how many the reverse
 * sweep has used, so the ratio is on screen rather than asserted.
 *
 * The frame that earns the stepper is the adjoint of `a` in Example 5.14
 * (Eq 5.137). Every other node has one child and its adjoint is one product;
 * `a` feeds both `b` and `c`, so its adjoint is a **sum of two contributions**.
 * That single line is where readers who have only seen the scalar chain rule get
 * stuck, and it is impossible to linger on in an animation.
 *
 * Three independent checks on the final answer:
 *
 *   * the analytic derivative, differentiated by hand;
 *   * a central finite difference, which shares no code with the graph;
 *   * forward-mode AD via a first-order jet, which walks the graph the other way.
 *
 * If reverse mode had a sign or an accumulation wrong, at least two of the three
 * would disagree.
 *
 * Determinism: no randomness. The graph is a fixed list.
 */
import { tracer, capFrames, type Trace } from "../../frames";

/* ------------------------------------------------------------------ graph --- */

export type Op =
  | "input"
  | "square"
  | "exp"
  | "add"
  | "sqrt"
  | "cos"
  | "sin"
  | "mul"
  | "log"
  | "neg"
  | "recip"
  | "tanh";

export interface Node {
  /** Name as the book writes it: x, a, b, c, d, e, f. */
  id: string;
  op: Op;
  /** Indices into the node list. */
  parents: number[];
  /** The elementary rule, as the book prints it in Eq 5.129-5.134. */
  ruleTex: string;
  /** Layout hint: column and row in the drawn graph. */
  col: number;
  row: number;
}

interface GraphSpec {
  name: string;
  tex: string;
  blurb: string;
  nodes: Node[];
  /** Where to evaluate. */
  x: number;
  /** Differentiated by hand, for the check. */
  analytic: (x: number) => number;
  book: string;
}

/** f(x) = sqrt(x^2 + exp(x^2)) + cos(x^2 + exp(x^2)) — Eq 5.122. */
const EXAMPLE_5_14: GraphSpec = {
  name: "example-5-14",
  tex: "f(x) = \\sqrt{x^2 + \\exp(x^2)} + \\cos\\!\\left(x^2 + \\exp(x^2)\\right)",
  blurb:
    "the book's Example 5.14. Six intermediate variables, and one of them feeds two others — which is the whole reason reverse mode needs a SUM rather than a single product",
  nodes: [
    { id: "x", op: "input", parents: [], ruleTex: "", col: 0, row: 1 },
    { id: "a", op: "square", parents: [0], ruleTex: "\\frac{\\partial a}{\\partial x} = 2x", col: 1, row: 1 },
    { id: "b", op: "exp", parents: [1], ruleTex: "\\frac{\\partial b}{\\partial a} = \\exp(a)", col: 2, row: 0 },
    { id: "c", op: "add", parents: [1, 2], ruleTex: "\\frac{\\partial c}{\\partial a} = 1 = \\frac{\\partial c}{\\partial b}", col: 3, row: 1 },
    { id: "d", op: "sqrt", parents: [3], ruleTex: "\\frac{\\partial d}{\\partial c} = \\frac{1}{2\\sqrt{c}}", col: 4, row: 0 },
    { id: "e", op: "cos", parents: [3], ruleTex: "\\frac{\\partial e}{\\partial c} = -\\sin(c)", col: 4, row: 2 },
    { id: "f", op: "add", parents: [4, 5], ruleTex: "\\frac{\\partial f}{\\partial d} = 1 = \\frac{\\partial f}{\\partial e}", col: 5, row: 1 },
  ],
  x: 0.9,
  analytic: (x) => {
    const u = x * x + Math.exp(x * x);
    const dudx = 2 * x * (1 + Math.exp(x * x));
    return (1 / (2 * Math.sqrt(u)) - Math.sin(u)) * dudx;
  },
  book: "Example 5.14, Eq 5.122-5.142",
};

/** The chain from Figure 5.10: x -> a -> b -> y, one path only. */
const FIGURE_5_10: GraphSpec = {
  name: "figure-5-10",
  tex: "y = \\sin\\!\\left(\\log(x^2)\\right)",
  blurb:
    "the book's Figure 5.10, x to y through two intermediates on a single path. With no branching, dy/dx is one product of three factors and forward and reverse mode differ only in the order they multiply them (Eq 5.120 against Eq 5.121)",
  nodes: [
    { id: "x", op: "input", parents: [], ruleTex: "", col: 0, row: 1 },
    { id: "a", op: "square", parents: [0], ruleTex: "\\frac{\\partial a}{\\partial x} = 2x", col: 1, row: 1 },
    { id: "b", op: "log", parents: [1], ruleTex: "\\frac{\\partial b}{\\partial a} = \\frac{1}{a}", col: 2, row: 1 },
    { id: "y", op: "sin", parents: [2], ruleTex: "\\frac{\\partial y}{\\partial b} = \\cos(b)", col: 3, row: 1 },
  ],
  x: 1.7,
  analytic: (x) => Math.cos(Math.log(x * x)) * (1 / (x * x)) * (2 * x),
  book: "Figure 5.10, Eq 5.119-5.121",
};

/** The logistic sigmoid, Exercise 5.2, as a graph. */
const SIGMOID: GraphSpec = {
  name: "sigmoid",
  tex: "f(x) = \\dfrac{1}{1 + \\exp(-x)}",
  blurb:
    "Exercise 5.2 as a graph. Four nodes, and the reverse sweep reproduces the famous f(1 - f) without anyone having to notice the algebraic identity",
  nodes: [
    { id: "x", op: "input", parents: [], ruleTex: "", col: 0, row: 1 },
    { id: "a", op: "neg", parents: [0], ruleTex: "\\frac{\\partial a}{\\partial x} = -1", col: 1, row: 1 },
    { id: "b", op: "exp", parents: [1], ruleTex: "\\frac{\\partial b}{\\partial a} = \\exp(a)", col: 2, row: 1 },
    { id: "c", op: "add1", parents: [2], ruleTex: "\\frac{\\partial c}{\\partial b} = 1", col: 3, row: 1 } as unknown as Node,
    { id: "f", op: "recip", parents: [3], ruleTex: "\\frac{\\partial f}{\\partial c} = -\\frac{1}{c^2}", col: 4, row: 1 },
  ],
  x: 0.6,
  analytic: (x) => {
    const s = 1 / (1 + Math.exp(-x));
    return s * (1 - s);
  },
  book: "Exercise 5.2",
};
// `add1` is not a real op; the sigmoid graph adds the constant 1, which is
// modelled as a unary node so the drawing stays a chain. Patch it to a real op.
SIGMOID.nodes[3].op = "add" as Op;
(SIGMOID.nodes[3] as Node & { constant?: number }).constant = 1;

/** A two-layer scalar network, so the reader sees the shape §5.6.1 is about. */
const TINY_NET: GraphSpec = {
  name: "tiny-net",
  tex: "L = \\left(\\tanh(w_2\\tanh(w_1 x)) - y\\right)^2",
  blurb:
    "a scalar version of §5.6.1's deep network: two tanh layers and a squared loss, with w1 = 1.3, w2 = -0.8 and y = 0.5. The adjoints arriving at each weight are exactly what backpropagation computes",
  nodes: [
    { id: "x", op: "input", parents: [], ruleTex: "", col: 0, row: 1 },
    { id: "z1", op: "mul", parents: [0], ruleTex: "\\frac{\\partial z_1}{\\partial x} = w_1", col: 1, row: 1 },
    { id: "h1", op: "tanh", parents: [1], ruleTex: "\\frac{\\partial h_1}{\\partial z_1} = 1 - h_1^2", col: 2, row: 1 },
    { id: "z2", op: "mul", parents: [2], ruleTex: "\\frac{\\partial z_2}{\\partial h_1} = w_2", col: 3, row: 1 },
    { id: "h2", op: "tanh", parents: [3], ruleTex: "\\frac{\\partial h_2}{\\partial z_2} = 1 - h_2^2", col: 4, row: 1 },
    { id: "r", op: "add", parents: [4], ruleTex: "\\frac{\\partial r}{\\partial h_2} = 1", col: 5, row: 1 },
    { id: "L", op: "square", parents: [5], ruleTex: "\\frac{\\partial L}{\\partial r} = 2r", col: 6, row: 1 },
  ],
  x: 0.7,
  analytic: (x) => {
    const w1 = 1.3;
    const w2 = -0.8;
    const y = 0.5;
    const h1 = Math.tanh(w1 * x);
    const h2 = Math.tanh(w2 * h1);
    const r = h2 - y;
    return 2 * r * (1 - h2 * h2) * w2 * (1 - h1 * h1) * w1;
  },
  book: "§5.6.1",
};
(TINY_NET.nodes[1] as Node & { constant?: number }).constant = 1.3;
(TINY_NET.nodes[3] as Node & { constant?: number }).constant = -0.8;
(TINY_NET.nodes[5] as Node & { constant?: number }).constant = -0.5;

const GRAPHS = {
  "example-5-14": EXAMPLE_5_14,
  "figure-5-10": FIGURE_5_10,
  sigmoid: SIGMOID,
  "tiny-net": TINY_NET,
} as const;

export type GraphName = keyof typeof GRAPHS;
export const GRAPH_NAMES = Object.keys(GRAPHS) as GraphName[];

/* --------------------------------------------------------------- evaluate --- */

type NodeWithConst = Node & { constant?: number };

/** One elementary operation, and how many flops we charge it. */
function apply(op: Op, vals: number[], constant: number | undefined): { v: number; cost: number } {
  switch (op) {
    case "input":
      return { v: vals[0], cost: 0 };
    case "square":
      return { v: vals[0] * vals[0], cost: 1 };
    case "exp":
      return { v: Math.exp(vals[0]), cost: 1 };
    case "sqrt":
      return { v: Math.sqrt(vals[0]), cost: 1 };
    case "cos":
      return { v: Math.cos(vals[0]), cost: 1 };
    case "sin":
      return { v: Math.sin(vals[0]), cost: 1 };
    case "log":
      return { v: Math.log(vals[0]), cost: 1 };
    case "neg":
      return { v: -vals[0], cost: 1 };
    case "recip":
      return { v: 1 / vals[0], cost: 1 };
    case "tanh":
      return { v: Math.tanh(vals[0]), cost: 1 };
    case "mul":
      return vals.length === 2
        ? { v: vals[0] * vals[1], cost: 1 }
        : { v: vals[0] * (constant ?? 1), cost: 1 };
    case "add":
      return vals.length === 2
        ? { v: vals[0] + vals[1], cost: 1 }
        : { v: vals[0] + (constant ?? 0), cost: 1 };
    default:
      return { v: Number.NaN, cost: 0 };
  }
}

/**
 * The local partial d(node)/d(parent k), evaluated at the forward values.
 * These are exactly the book's Eq 5.129-5.134 for Example 5.14.
 */
function localPartial(
  op: Op,
  parentVals: number[],
  own: number,
  k: number,
  constant: number | undefined
): number {
  switch (op) {
    case "square":
      return 2 * parentVals[0];
    case "exp":
      return own;
    case "sqrt":
      return 1 / (2 * own);
    case "cos":
      return -Math.sin(parentVals[0]);
    case "sin":
      return Math.cos(parentVals[0]);
    case "log":
      return 1 / parentVals[0];
    case "neg":
      return -1;
    case "recip":
      return -1 / (parentVals[0] * parentVals[0]);
    case "tanh":
      return 1 - own * own;
    case "add":
      return 1;
    case "mul":
      return parentVals.length === 2 ? parentVals[1 - k] : (constant ?? 1);
    default:
      return Number.NaN;
  }
}

/** Forward-mode AD: carry a first-order jet through the same graph. */
function forwardMode(spec: GraphSpec, x: number): number {
  const vals: number[] = [];
  const dots: number[] = [];
  for (let i = 0; i < spec.nodes.length; i++) {
    const n = spec.nodes[i] as NodeWithConst;
    if (n.op === "input") {
      vals[i] = x;
      dots[i] = 1;
      continue;
    }
    const pv = n.parents.map((p) => vals[p]);
    const { v } = apply(n.op, pv, n.constant);
    vals[i] = v;
    let d = 0;
    n.parents.forEach((p, k) => {
      d += localPartial(n.op, pv, v, k, n.constant) * dots[p];
    });
    dots[i] = d;
  }
  return dots[spec.nodes.length - 1];
}

function evaluate(spec: GraphSpec, x: number): { vals: number[]; cost: number } {
  const vals: number[] = [];
  let cost = 0;
  for (let i = 0; i < spec.nodes.length; i++) {
    const n = spec.nodes[i] as NodeWithConst;
    if (n.op === "input") {
      vals[i] = x;
      continue;
    }
    const pv = n.parents.map((p) => vals[p]);
    const r = apply(n.op, pv, n.constant);
    vals[i] = r.v;
    cost += r.cost;
  }
  return { vals, cost };
}

/* ------------------------------------------------------------------ state --- */

export interface AdCheck {
  label: string;
  value: string;
  ok: boolean;
}

export interface AdNodeView {
  id: string;
  op: Op;
  col: number;
  row: number;
  parents: number[];
  ruleTex: string;
  value: number | null;
  adjoint: number | null;
  /** The individual terms summed into this adjoint, for the branching node. */
  terms: { from: string; local: number; childAdjoint: number; product: number }[] | null;
}

export interface AutodiffState {
  graph: GraphName;
  tex: string;
  x: number;
  phase: "forward" | "reverse" | "done";
  /** Index of the node this frame just resolved. */
  active: number | null;
  nodes: AdNodeView[];
  /** Running flop counts. */
  forwardCost: number;
  reverseCost: number;
  /** Final answer, present once the sweep reaches the input. */
  dfdx: number | null;
  analytic: number;
  checks: AdCheck[];
}

const CODE = [
  "# forward: evaluate every node in topological order",
  "for i in d+1 .. D:  x_i = g_i(x_Pa(i))                       # Eq 5.143",
  "",
  "# reverse: seed the output, then sweep backwards",
  "adj[D] = 1                                                   # Eq 5.144",
  "for i in D-1 .. 1:",
  "    adj[i] = sum over children j of  adj[j] * d x_j / d x_i   # Eq 5.145",
];

export interface AutodiffInput {
  graph?: GraphName;
  x?: number;
}

export function autodiff({ graph = "example-5-14", x }: AutodiffInput = {}): Trace<AutodiffState> {
  const spec = GRAPHS[graph];
  const at = x ?? spec.x;
  const N = spec.nodes.length;

  const { vals } = evaluate(spec, at);
  const analytic = spec.analytic(at);

  // Children of each node, needed for the reverse sweep's sum.
  const children: number[][] = spec.nodes.map(() => []);
  spec.nodes.forEach((n, i) => n.parents.forEach((p) => children[p].push(i)));

  const view = (
    upto: number,
    adj: (number | null)[],
    termsFor: number | null,
    terms: AdNodeView["terms"]
  ): AdNodeView[] =>
    spec.nodes.map((n, i) => ({
      id: n.id,
      op: n.op,
      col: n.col,
      row: n.row,
      parents: n.parents,
      ruleTex: n.ruleTex,
      value: i <= upto ? vals[i] : null,
      adjoint: adj[i] ?? null,
      terms: i === termsFor ? terms : null,
    }));

  const t = tracer<AutodiffState>(CODE);
  const adj: (number | null)[] = spec.nodes.map(() => null);
  let fwdCost = 0;

  /* ---- forward pass, one node per frame ---- */
  for (let i = 0; i < N; i++) {
    const n = spec.nodes[i] as NodeWithConst;
    if (n.op !== "input") {
      fwdCost += apply(n.op, n.parents.map((p) => vals[p]), n.constant).cost;
    }
    const caption =
      n.op === "input"
        ? `Forward pass. The input is x = ${at}.`
        : `Forward: ${n.id} = ${opText(n, spec)} = ${vals[i].toPrecision(8)}. One elementary operation, ${fwdCost} so far.`;
    t.push(
      {
        graph,
        tex: spec.tex,
        x: at,
        phase: "forward",
        active: i,
        nodes: view(i, adj, null, null),
        forwardCost: fwdCost,
        reverseCost: 0,
        dfdx: null,
        analytic,
        checks: [],
      },
      caption,
      { line: 2, watch: [{ label: n.id, value: vals[i].toPrecision(8) }] }
    );
  }

  /* ---- reverse sweep, one node per frame ---- */
  let revCost = 0;
  adj[N - 1] = 1;
  t.push(
    {
      graph,
      tex: spec.tex,
      x: at,
      phase: "reverse",
      active: N - 1,
      nodes: view(N - 1, adj, null, null),
      forwardCost: fwdCost,
      reverseCost: revCost,
      dfdx: null,
      analytic,
      checks: [],
    },
    `Seed the sweep: the output's derivative with respect to itself is 1 (Eq 5.144). Everything below is one application of Eq 5.145.`,
    { line: 5, watch: [{ label: `adj[${spec.nodes[N - 1].id}]`, value: "1" }] }
  );

  for (let i = N - 2; i >= 0; i--) {
    const terms: NonNullable<AdNodeView["terms"]> = [];
    let total = 0;
    for (const j of children[i]) {
      const cn = spec.nodes[j] as NodeWithConst;
      const k = cn.parents.indexOf(i);
      const local = localPartial(cn.op, cn.parents.map((p) => vals[p]), vals[j], k, cn.constant);
      const ca = adj[j] as number;
      terms.push({ from: cn.id, local, childAdjoint: ca, product: local * ca });
      total += local * ca;
      revCost += 2; // one multiply, one add
    }
    adj[i] = total;

    const n = spec.nodes[i];
    const isBranch = children[i].length > 1;
    const sumText = terms
      .map((tm) => `${tm.childAdjoint.toPrecision(6)} × ${tm.local.toPrecision(6)}`)
      .join(" + ");

    const caption = isBranch
      ? `Reverse, and this is the frame that matters: ${n.id} feeds ${children[i].length} nodes (${children[i].map((j) => spec.nodes[j].id).join(" and ")}), so its adjoint is a SUM, not a single product — ${sumText} = ${total.toPrecision(8)}. This is Eq 5.137, and forgetting the second term is the classic backpropagation bug.`
      : `Reverse: adj[${n.id}] = adj[${spec.nodes[children[i][0]].id}] × ∂${spec.nodes[children[i][0]].id}/∂${n.id} = ${sumText} = ${total.toPrecision(8)}.`;

    const isInput = n.op === "input";
    const checks: AdCheck[] = [];
    if (isInput) {
      const fd =
        (evaluateAt(spec, at + 1e-6) - evaluateAt(spec, at - 1e-6)) / 2e-6;
      const fm = forwardMode(spec, at);
      checks.push(
        {
          label: "reverse mode vs the analytic derivative",
          value: Math.abs(total - analytic).toExponential(1),
          ok: Math.abs(total - analytic) < 1e-11 * Math.max(1, Math.abs(analytic)),
        },
        {
          label: "vs forward-mode AD on the same graph",
          value: Math.abs(total - fm).toExponential(1),
          ok: Math.abs(total - fm) < 1e-12 * Math.max(1, Math.abs(analytic)),
        },
        {
          label: "vs a central finite difference (h = 1e-6)",
          value: Math.abs(total - fd).toExponential(1),
          ok: Math.abs(total - fd) < 1e-6 * Math.max(1, Math.abs(analytic)),
        },
        {
          label: "reverse cost / forward cost",
          value: `${revCost} / ${fwdCost} = ${(revCost / Math.max(fwdCost, 1)).toFixed(2)}x`,
          ok: revCost / Math.max(fwdCost, 1) < 4,
        }
      );
    }

    t.push(
      {
        graph,
        tex: spec.tex,
        x: at,
        phase: isInput ? "done" : "reverse",
        active: i,
        nodes: view(N - 1, adj, i, terms),
        forwardCost: fwdCost,
        reverseCost: revCost,
        dfdx: isInput ? total : null,
        analytic,
        checks,
      },
      caption,
      { line: 7, watch: [{ label: `adj[${n.id}]`, value: total.toPrecision(8) }] }
    );
  }

  const dfdx = adj[0] as number;
  return capFrames(
    t.done(
      `df/dx = ${dfdx.toPrecision(8)} at x = ${at}; forward ${fwdCost} ops, reverse ${revCost} ops`
    )
  );
}

function evaluateAt(spec: GraphSpec, x: number): number {
  return evaluate(spec, x).vals[spec.nodes.length - 1];
}

function opText(n: NodeWithConst, spec: GraphSpec): string {
  const p = n.parents.map((i) => spec.nodes[i].id);
  switch (n.op) {
    case "square":
      return `${p[0]}²`;
    case "exp":
      return `exp(${p[0]})`;
    case "sqrt":
      return `√${p[0]}`;
    case "cos":
      return `cos(${p[0]})`;
    case "sin":
      return `sin(${p[0]})`;
    case "log":
      return `log(${p[0]})`;
    case "neg":
      return `−${p[0]}`;
    case "recip":
      return `1/${p[0]}`;
    case "tanh":
      return `tanh(${p[0]})`;
    case "add":
      return p.length === 2 ? `${p[0]} + ${p[1]}` : `${p[0]} + ${n.constant}`;
    case "mul":
      return p.length === 2 ? `${p[0]} · ${p[1]}` : `${n.constant} · ${p[0]}`;
    default:
      return p.join(", ");
  }
}

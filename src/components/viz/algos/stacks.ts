/**
 * algos/stacks.ts — traced stack algorithms for <StackMachine>.
 *
 * The monotonic stack is the pattern this file exists for. Its code is six lines
 * and its behaviour is genuinely counter-intuitive: a `while` loop inside a `for`
 * loop that is nonetheless O(n), and a stack whose contents encode "everything
 * still waiting for an answer". Neither fact is visible in the source.
 *
 * So the stack is drawn as a column beside the input, and the caption names what
 * the stack *means* at each step rather than what the line does.
 */
import { capFrames, tracer, type Tone, type Trace, type Watch } from "../frames";

/** One cell in the input row. */
export interface StackInputCell {
  label: string;
  tone?: Tone;
}

/** One slot in the stack column. Bottom of the array is the bottom of the stack. */
export interface StackSlot {
  label: string;
  tone?: Tone;
  /** Small annotation beside the slot — an index, or a pending count. */
  note?: string;
}

export interface StackState {
  /** The input being scanned, left to right. */
  input: StackInputCell[];
  /** Index currently being read, for the caret. */
  cursor?: number;
  /** Stack contents, bottom first. */
  stack: StackSlot[];
  /** Result being accumulated, aligned to the input where meaningful. */
  output?: StackInputCell[];
  /** Label above the output strip. */
  outputLabel?: string;
  /** Counters under the stack. */
  legend?: { label: string; value: string; tone?: Tone }[];
}

export interface StackInput {
  values?: number[];
  text?: string;
}

export type StackAlgo = (input: StackInput) => Trace<StackState>;

const w = (label: string, value: string | number, tone?: Tone): Watch => ({ label, value, tone });

// ── 1. Next greater element / daily temperatures (LC 739, 496) ────────────

const MONO_CODE = [
  "def daily_temperatures(temps):",
  "    out = [0] * len(temps)",
  "    stack = []                      # indices, temps DECREASING upward",
  "    for i, t in enumerate(temps):",
  "        while stack and temps[stack[-1]] < t:",
  "            j = stack.pop()         # t is j's answer",
  "            out[j] = i - j",
  "        stack.append(i)",
  "    return out                      # anything left has no answer",
];

export const nextGreater: StackAlgo = (input) => {
  const a = input.values?.length ? input.values : [73, 74, 75, 71, 69, 72, 76, 73];
  const t = tracer<StackState>(MONO_CODE);

  const out: (number | null)[] = a.map(() => null);
  const stack: number[] = [];
  let pops = 0;

  const state = (cursor?: number, popped?: number): StackState => ({
    input: a.map((v, i) => ({
      label: String(v),
      tone:
        i === cursor
          ? "active"
          : i === popped
            ? "good"
            : stack.includes(i)
              ? "warn"
              : out[i] !== null
                ? "muted"
                : i < (cursor ?? 0)
                  ? "muted"
                  : "info",
    })),
    cursor,
    stack: stack.map((i) => ({
      label: String(a[i]),
      note: `i=${i}`,
      tone: i === stack[stack.length - 1] ? "active" : "warn",
    })),
    output: a.map((_, i) => ({
      label: out[i] === null ? "·" : String(out[i]),
      tone: out[i] === null ? "muted" : "good",
    })),
    outputLabel: "days to wait",
    legend: [
      { label: "stack", value: String(stack.length), tone: "warn" },
      { label: "total pops", value: String(pops), tone: "good" },
    ],
  });

  t.push(
    state(),
    `The stack holds **indices whose answer is still unknown**, and it is kept decreasing in temperature from bottom to top. That invariant is the whole pattern: a value can only resolve the entries above it, never below.`,
    { line: 3, phase: "setup" },
  );

  for (let i = 0; i < a.length; i++) {
    t.push(
      state(i),
      `Read ${a[i]} at index ${i}. Everything on the stack is waiting for a warmer day — is today it?`,
      { line: 4, phase: "read", watch: [w("i", i), w("value", a[i], "active"), w("stack", stack.length, "warn")] },
    );

    while (stack.length && a[stack[stack.length - 1]] < a[i]) {
      const j = stack.pop()!;
      out[j] = i - j;
      pops += 1;
      t.push(
        state(i, j),
        `${a[i]} > ${a[j]}, so today is the answer for index ${j}: it waited ${i - j} day${i - j === 1 ? "" : "s"}. Pop it — it will never be needed again, and that is why the total number of pops across the whole run is at most n.`,
        {
          line: 7,
          phase: "resolve",
          watch: [w("resolved", `i=${j}`, "good"), w("answer", i - j, "good"), w("total pops", pops)],
        },
      );
    }

    stack.push(i);
    t.push(
      state(i),
      `Push index ${i}. Its own answer is unknown, so it joins the queue of pending entries — and the stack stays decreasing, because everything smaller was just popped.`,
      { line: 8, phase: "push", watch: [w("stack", stack.map((k) => a[k]).join(","), "warn")] },
    );
  }

  t.push(
    state(),
    `Done. ${stack.length} ${stack.length === 1 ? "index is" : "indices are"} still on the stack — those values never saw a warmer day, so their answer stays 0. Total work: n pushes and at most n pops, so **O(n) despite the nested while**. Each element enters and leaves the stack once; that is the amortised argument to say out loud.`,
    { line: 9, phase: "answer", watch: [w("pushes", a.length), w("pops", pops), w("unresolved", stack.length, "muted")] },
  );

  return capFrames(t.done(`[${out.map((v) => v ?? 0).join(", ")}]`));
};

// ── 2. Balanced parentheses (LC 20) ───────────────────────────────────────

const PARENS_CODE = [
  "def is_valid(s):",
  "    pairs = {')': '(', ']': '[', '}': '{'}",
  "    stack = []",
  "    for ch in s:",
  "        if ch not in pairs:",
  "            stack.append(ch)          # an opener",
  "        elif not stack or stack.pop() != pairs[ch]:",
  "            return False              # mismatch, or nothing to close",
  "    return not stack                  # leftovers mean unclosed",
];

export const validParens: StackAlgo = (input) => {
  const s = input.text ?? "([]{})";
  const chars = [...s];
  const t = tracer<StackState>(PARENS_CODE);
  const PAIRS: Record<string, string> = { ")": "(", "]": "[", "}": "{" };

  const stack: string[] = [];
  let verdict: boolean | null = null;
  let failAt = -1;

  const state = (cursor?: number, bad = false): StackState => ({
    input: chars.map((ch, i) => ({
      label: ch,
      tone: i === cursor ? (bad ? "bad" : "active") : i < (cursor ?? 0) ? "muted" : "info",
    })),
    cursor,
    stack: stack.map((ch, i) => ({ label: ch, tone: i === stack.length - 1 ? "active" : "warn" })),
    legend: [{ label: "open", value: String(stack.length), tone: stack.length ? "warn" : "good" }],
  });

  t.push(
    state(),
    `The stack holds openers that have not been closed yet. Its depth is the current nesting level, and the top is always the one that must close next — which is exactly what "properly nested" means.`,
    { line: 3, phase: "setup" },
  );

  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i];
    if (!(ch in PAIRS)) {
      stack.push(ch);
      t.push(
        state(i),
        `'${ch}' is an opener — push it. Nesting depth is now ${stack.length}.`,
        { line: 6, phase: "open", watch: [w("depth", stack.length, "warn"), w("stack", stack.join(""), "warn")] },
      );
      continue;
    }

    if (stack.length === 0) {
      verdict = false;
      failAt = i;
      t.push(
        state(i, true),
        `'${ch}' wants to close something, but the stack is empty — there is nothing open. Invalid. This is the case an unbalanced-counter solution misses: counting brackets is not enough, the *order* matters.`,
        { line: 8, phase: "invalid", watch: [w("stack", "empty", "bad")] },
      );
      break;
    }

    const top = stack.pop()!;
    const ok = top === PAIRS[ch];
    if (!ok) {
      verdict = false;
      failAt = i;
      t.push(
        state(i, true),
        `'${ch}' must close '${PAIRS[ch]}', but the innermost open bracket is '${top}'. Crossed nesting like this is invalid even though the counts might balance.`,
        { line: 8, phase: "invalid", watch: [w("expected", PAIRS[ch], "good"), w("found", top, "bad")] },
      );
      break;
    }

    t.push(
      state(i),
      `'${ch}' closes the '${top}' on top. Popped — depth is back to ${stack.length}.`,
      { line: 7, phase: "close", watch: [w("depth", stack.length), w("stack", stack.join("") || "empty")] },
    );
  }

  if (verdict === null) {
    verdict = stack.length === 0;
    t.push(
      state(),
      verdict
        ? `Every bracket was matched and the stack is empty. Valid.`
        : `The scan finished but ${stack.length} bracket${stack.length === 1 ? "" : "s"} (${stack.join("")}) ${stack.length === 1 ? "is" : "are"} still open. Invalid — and this final emptiness check is the step most often forgotten.`,
      { line: 9, phase: "answer", watch: [w("valid", verdict ? "True" : "False", verdict ? "good" : "bad")] },
    );
  }

  return capFrames(
    t.done(verdict ? "valid" : `invalid${failAt >= 0 ? ` at index ${failAt}` : " — unclosed brackets"}`),
  );
};

// ── 3. Evaluate reverse Polish notation (LC 150) ───────────────────────────

const RPN_CODE = [
  "def eval_rpn(tokens):",
  "    stack = []",
  "    for tok in tokens:",
  "        if tok in '+-*/':",
  "            b = stack.pop()          # SECOND operand pops first",
  "            a = stack.pop()",
  "            stack.append(apply(a, tok, b))",
  "        else:",
  "            stack.append(int(tok))",
  "    return stack[0]",
];

export const evalRpn: StackAlgo = (input) => {
  const tokens = (input.text ?? "2 1 + 3 *").split(/\s+/).filter(Boolean);
  const t = tracer<StackState>(RPN_CODE);
  const OPS = new Set(["+", "-", "*", "/"]);

  const stack: number[] = [];

  const state = (cursor?: number, tone: Tone = "active"): StackState => ({
    input: tokens.map((tk, i) => ({
      label: tk,
      tone: i === cursor ? tone : i < (cursor ?? 0) ? "muted" : "info",
    })),
    cursor,
    stack: stack.map((v, i) => ({
      label: String(v),
      tone: i === stack.length - 1 ? "active" : "warn",
    })),
    legend: [{ label: "depth", value: String(stack.length), tone: "warn" }],
  });

  t.push(
    state(),
    `Postfix notation needs no parentheses and no precedence rules, because the order is already unambiguous. A single stack evaluates it in one pass — which is why compilers convert infix to postfix before evaluating.`,
    { line: 2, phase: "setup" },
  );

  for (let i = 0; i < tokens.length; i++) {
    const tk = tokens[i];
    if (!OPS.has(tk)) {
      stack.push(Number(tk));
      t.push(state(i), `${tk} is a number — push it.`, {
        line: 9,
        phase: "push",
        watch: [w("stack", stack.join(","), "warn")],
      });
      continue;
    }

    const b = stack.pop()!;
    const a = stack.pop()!;
    const v = tk === "+" ? a + b : tk === "-" ? a - b : tk === "*" ? a * b : Math.trunc(a / b);
    stack.push(v);

    t.push(
      state(i, "good"),
      `'${tk}' pops two operands. Order matters: the **second** operand comes off first, so this is ${a} ${tk} ${b} = ${v}, not ${b} ${tk} ${a}. Getting that backwards is invisible for + and *, and wrong for − and /.`,
      {
        line: 7,
        phase: "apply",
        watch: [w("a", a), w("op", tk, "active"), w("b", b), w("=", v, "good")],
      },
    );
  }

  t.push(
    state(),
    `One value left on the stack: ${stack[0]}. That is the answer — a well-formed postfix expression always ends with exactly one. O(n) time, O(n) stack.`,
    { line: 10, phase: "answer", watch: [w("result", stack[0] ?? 0, "good")] },
  );

  return capFrames(t.done(`= ${stack[0] ?? 0}`));
};

/**
 * Registry. The `algo` prop of <StackMachine> indexes this.
 *
 * | key            | uses            |
 * |----------------|-----------------|
 * | next-greater   | values          |
 * | valid-parens   | text            |
 * | eval-rpn       | text (space-separated tokens) |
 */
export const STACK_ALGOS: Record<string, StackAlgo> = {
  "next-greater": nextGreater,
  "valid-parens": validParens,
  "eval-rpn": evalRpn,
};

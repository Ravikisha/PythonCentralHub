/**
 * scripts/dsa-spine-batch1.mjs — bring six Phase-05 pages to the full spine.
 *
 * The mechanical parts of the retrofit (frontmatter, generated ladders) are
 * handled by dsa-frontmatter.mjs and dsa-ladders.mjs. What is left is the part
 * that cannot be generated: the cue that teaches recognition, the hand trace, the
 * pitfalls, the follow-ups, the quiz and the recall card. Those are authored here.
 *
 * Why a script rather than editing the pages directly: the insertion points and
 * the import bookkeeping are identical across pages and easy to get subtly wrong
 * by hand (a missing blank line after an import silently breaks MDX). Keeping the
 * content in one reviewable file also makes the batch diffable.
 *
 * Idempotent: a section already present on a page is skipped.
 *
 * Run: node scripts/dsa-spine-batch1.mjs
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const DOCS = "src/content/docs/DSA with Python";
const P5 = "Phase-05-Patterns-Arrays-and-Strings";

/**
 * Each entry is { file, imports, sections }.
 *
 * \`sections\` is an ordered list of { heading, before, body }:
 *   heading — used to detect "already present" and to skip re-inserting
 *   before   — insert immediately before the first of these headings that exists;
 *              \`null\` means append at the end of the page
 */
const PAGES = [
  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Two Pointers.mdx`,
    imports: ["Quiz"],
    sections: [
      {
        heading: "## The cue",
        before: ["## The template", "## How it works"],
        body: `## The cue

:::tip[You are looking at two pointers when…]
- The input is **sorted** (or you are allowed to sort it) **and** the question asks
  for a pair, triple, or a value satisfying some relation. Sorting turns "search
  everything" into "walk inward from both ends".
- The problem asks you to **partition or compact in place** with $O(1)$ extra
  space — a read pointer scanning and a write pointer marking where the next kept
  value goes.
- Two sequences must be traversed **in step** (merging, checking a subsequence).

**The load-bearing property is monotonicity of the decision.** At each step you
must be able to prove that moving one specific pointer cannot discard the answer.
On a sorted array, if the sum is too small, only moving \`lo\` right can increase
it — moving \`hi\` left makes it strictly worse, so \`hi\`'s current position is
safely eliminated.

**Reach for something else** when the array is unsorted and sorting would destroy
required index information (use a hash map — that is exactly why LC 1 Two Sum is a
hash-map problem while LC 167 is a two-pointer problem), or when the target
subarray must be contiguous *and* the condition is not monotonic (prefix sums).
:::`,
      },
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

LC 167 with \`target = 9\`, \`nums = [2, 7, 11, 15]\`. Write it out this way on a
whiteboard — the elimination column is the part interviewers want to hear.

| Step | \`lo\` | \`hi\` | sum | vs target | move | why that move is safe |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 → 2 | 3 → 15 | 17 | too big | \`hi--\` | 15 is the largest value; paired with the *smallest* remaining it still overshoots, so 15 cannot be in any answer |
| 2 | 0 → 2 | 2 → 11 | 13 | too big | \`hi--\` | same argument eliminates 11 |
| 3 | 0 → 2 | 1 → 7 | 9 | **equal** | stop | found |

Three comparisons for a four-element array, versus six for the brute-force double
loop. The gap widens fast: at $n = 1000$ it is 1,000 steps against 500,000.

Now the failure case — \`target = 100\`, same array:

| Step | \`lo\` | \`hi\` | sum | move |
| --- | --- | --- | --- | --- |
| 1 | 0 | 3 | 17 | \`lo++\` |
| 2 | 1 | 3 | 22 | \`lo++\` |
| 3 | 2 | 3 | 26 | \`lo++\` |
| 4 | 3 | 3 | — | \`lo < hi\` fails, loop ends |

The pointers meet rather than cross, which is why the loop condition is
\`lo < hi\` and not \`lo <= hi\` — with \`<=\` the final iteration would pair an
element with itself, and "you may not use the same element twice" is almost always
part of the problem statement.`,
      },
      {
        heading: "## The variant map",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## The variant map

Four shapes, and recognising which one you have been handed is most of the work.

| Variant | Pointer setup | What decides the move | Canonical problem |
| --- | --- | --- | --- |
| **Converging from the ends** | \`lo = 0\`, \`hi = n - 1\` | compare an aggregate against a target | 167 Two Sum II · 11 Container With Most Water · 42 Trapping Rain Water |
| **Fixed one, converge the rest** | outer loop fixes \`i\`, then two pointers inside | the same comparison, one dimension down | 15 3Sum · 16 3Sum Closest · 18 4Sum |
| **Read / write compaction** | both start at 0, \`write\` lags \`read\` | whether \`read\`'s value is kept | 26 Remove Duplicates · 27 Remove Element · 283 Move Zeroes |
| **Same direction, two sequences** | one pointer per sequence | which sequence advances | 392 Is Subsequence · 88 Merge Sorted Array |

:::note[3Sum is 2Sum with a loop around it — and the dedup is the actual difficulty]
Sort, then for each index \`i\` run the converging two-pointer scan on the
remainder. That is $O(n^2)$, not $O(n^3)$.

The part that fails submissions is duplicate handling. Skip \`i\` when
\`nums[i] == nums[i-1]\`, and after recording a hit advance **both** inner pointers
past their duplicates. A set of tuples also works and is easier to write under
pressure, but say out loud that you are trading memory for simplicity — that
acknowledgement is worth more than the cleaner solution.
:::`,
      },
      {
        heading: "## Pitfalls",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Pitfalls

- **Sorting when indices matter.** LC 1 asks for *indices* in an unsorted array;
  sorting destroys them. That single difference is why LC 1 is a hash-map problem
  and LC 167 is a two-pointer problem, and interviewers ask both to see whether
  you notice.
- **\`lo <= hi\` instead of \`lo < hi\`.** With \`<=\` the last iteration pairs an
  element with itself. Almost every problem forbids that.
- **Moving the wrong pointer in Container With Most Water.** Move the **shorter**
  wall. Keeping it cannot help: width only shrinks from here, and the shorter wall
  already caps the height.
- **Forgetting that the answer is a length, not an array, in compaction problems.**
  LC 26 returns \`k\`; the slots past \`k\` hold leftover garbage the caller must
  ignore. Returning a sliced copy technically answers a different question.
- **Assuming two pointers works on an unsorted array.** Without sortedness there
  is no monotonic argument, and the pointers can walk past the answer. If you
  cannot state *why* a move is safe, the pattern does not apply.`,
      },
      {
        heading: "## Interview follow-ups",
        before: ["## Edge-case checklist", "## Recap"],
        body: `## Interview follow-ups

| They ask | What they're checking | The answer |
| --- | --- | --- |
| "Why is this $O(n)$ and not $O(n^2)$?" | Whether you can justify the pattern | Each pointer only ever moves inward, so together they take at most $n$ steps total — every step eliminates at least one candidate permanently |
| "What if the array is not sorted?" | Whether you know the precondition | Sort first at $O(n \\log n)$ — still better than $O(n^2)$ — unless indices must be preserved, in which case use a hash map |
| "Prove that moving \`hi\` left is safe" | Whether you understand or memorised | If \`sum > target\`, then \`nums[hi]\` paired with the *smallest* remaining value still overshoots, so \`nums[hi]\` appears in no valid pair and can be discarded |
| "Extend it to 4Sum" | Generalisation | Two nested loops around the same converging scan: $O(n^3)$. Beyond that, meet-in-the-middle with a hash map of pair sums beats more nesting |
| "What if duplicates are allowed in the output?" | Care with the dedup logic | Drop the skip conditions — but state that you are doing so deliberately, because it is the opposite of the usual requirement |
| "Do it without sorting, in $O(n)$" | Whether you reach for the right tool | Only possible with a hash map, and only for the pair case — 3Sum has no known $O(n)$ solution |`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Two pointers — self-check"
  questions={[
    {
      q: "Why is LC 1 (Two Sum) a hash-map problem while LC 167 (Two Sum II) is a two-pointer problem?",
      options: [
        "LC 167 is easier, so it gets the simpler technique",
        "LC 167's array is already sorted, and LC 1 requires returning indices that sorting would destroy",
        "Hash maps cannot be used on sorted arrays",
        "Two pointers only works when the target is positive",
      ],
      answer: 1,
      explain:
        "This pair is asked precisely to see whether you notice the difference. Two pointers needs sortedness for its safety argument; LC 1's array is unsorted AND wants original indices, so sorting is not available. That leaves the hash map.",
    },
    {
      q: "In Container With Most Water, which wall do you move inward, and why?",
      options: [
        "The taller one, to look for something even taller",
        "The shorter one, because the width can only shrink and the shorter wall already caps the height",
        "Whichever is closer to the middle",
        "Both, alternately",
      ],
      answer: 1,
      explain:
        "Keeping the shorter wall cannot help: every remaining pair with it is narrower, and its height is still the binding limit. So it can be discarded safely. This is the exchange argument that makes the greedy correct rather than merely plausible.",
    },
    {
      q: "The loop condition is \`lo < hi\` rather than \`lo <= hi\`. What breaks with \`<=\`?",
      options: [
        "Nothing — they are equivalent",
        "The final iteration pairs an element with itself, which problems almost always forbid",
        "It causes an index-out-of-range error",
        "It makes the algorithm O(n²)",
      ],
      answer: 1,
      explain:
        "At lo == hi both pointers sit on the same element. 'You may not use the same element twice' is standard in these problems, so that iteration would produce an invalid answer.",
    },
    {
      q: "What is the time complexity of the standard 3Sum solution, and where does it come from?",
      options: [
        "O(n³) — three nested loops",
        "O(n²) — one outer loop around an O(n) converging scan, after an O(n log n) sort",
        "O(n log n) — dominated by the sort",
        "O(n) — with a hash map",
      ],
      answer: 1,
      explain:
        "Sorting is O(n log n) and is dominated by the O(n²) main phase. There is no known O(n) solution for 3Sum, which is worth saying if asked to go faster.",
    },
    {
      q: "LC 26 removes duplicates in place. What does it return, and what is in the array afterwards?",
      options: [
        "A new shorter array containing only the distinct values",
        "The count k of distinct values; arr[:k] holds them and everything past k is leftover garbage",
        "The number of duplicates removed",
        "None — it mutates in place and returns nothing",
      ],
      answer: 1,
      explain:
        "The write pointer's final position IS the answer. Nothing is truncated, because you cannot shrink an array in place — the contract is that the caller ignores everything from index k onward.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — sorted input (or sortable) **and** a pair/triple relation; or in-place
  compaction with $O(1)$ space; or two sequences walked in step.
- **Invariant** — every pointer move must *provably* eliminate candidates. If you
  cannot state why, the pattern does not apply.
- **Template** — \`lo, hi = 0, n - 1\`; \`while lo < hi\`; compare an aggregate
  against the target and move the pointer whose current value is eliminated.
- **Complexity** — $O(n)$ after sorting, $O(1)$ space. 3Sum is $O(n^2)$; each
  extra fixed element costs another factor of $n$.
- **Fails when** — the array is unsorted and indices must be preserved (hash map),
  or the decision is not monotonic (prefix sums).`,
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Monotonic Stack.mdx`,
    imports: ["Quiz"],
    sections: [
      {
        heading: "## The cue",
        before: ["## Visual intuition", "## The template", "## How it works"],
        body: `## The cue

:::tip[You are looking at a monotonic stack when…]
- The problem asks, for every element, about the **next (or previous) element that
  is greater or smaller** than it. "Days until a warmer temperature", "next
  greater element", "how far until a taller building".
- Or it asks for the **largest rectangle / span** bounded by a smaller value on
  each side — the same question wearing a different hat.
- Or a value's answer becomes knowable only when a **later** value arrives, so
  entries must wait in order.

The stack holds **indices whose answer is still unknown**, kept sorted by value.
When a new element arrives it resolves every waiting entry it beats, and those
entries are then gone for good — which is the whole reason the nested loop is
still linear.

**Reach for something else** when the query is about a *window* rather than a
comparison (that is a [monotonic deque](../monotonic-deque/), which supports
eviction from both ends), or when you need the k-th largest rather than the next
larger (a heap).
:::`,
      },
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

LC 739 with \`temps = [73, 74, 75, 71, 69, 72, 76, 73]\`. The stack column shows
indices; the values are in brackets.

| \`i\` | temp | pops (resolved) | stack after | \`out\` so far |
| --- | --- | --- | --- | --- |
| 0 | 73 | — | \`[0(73)]\` | \`[0,0,0,0,0,0,0,0]\` |
| 1 | 74 | \`0\` → \`out[0]=1\` | \`[1(74)]\` | \`[1,0,…]\` |
| 2 | 75 | \`1\` → \`out[1]=1\` | \`[2(75)]\` | \`[1,1,0,…]\` |
| 3 | 71 | — | \`[2(75), 3(71)]\` | unchanged |
| 4 | 69 | — | \`[2, 3, 4(69)]\` | unchanged |
| 5 | 72 | \`4\` → \`out[4]=1\`, \`3\` → \`out[3]=2\` | \`[2(75), 5(72)]\` | \`[1,1,0,2,1,0,0,0]\` |
| 6 | 76 | \`5\` → \`out[5]=1\`, \`2\` → \`out[2]=4\` | \`[6(76)]\` | \`[1,1,4,2,1,1,0,0]\` |
| 7 | 73 | — | \`[6(76), 7(73)]\` | unchanged |

Two things to read off that table:

- **Total pops: 6. Total pushes: 8.** Fourteen stack operations for an
  eight-element array — not 64. That is the amortised argument, stated concretely,
  and it is the answer to "why is this O(n) when there is a while inside a for".
- **Indices 6 and 7 are still on the stack at the end.** They never saw a warmer
  day, so their answers stay 0. Leftovers on the stack are not a bug; they are the
  "no answer exists" case, and pre-filling \`out\` with zeros is what handles them.

Note step 5 popping **two** entries in one iteration while step 3 pops none. The
work per iteration is wildly uneven; only the total is bounded.`,
      },
      {
        heading: "## The variant map",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## The variant map

One template, four mutations. The direction of the comparison and what you store
are the only things that change.

| Variant | Stack ordering | Pop condition | Canonical problem |
| --- | --- | --- | --- |
| **Next greater** | decreasing | \`stack top < current\` | 739 Daily Temperatures · 496 Next Greater Element I |
| **Next smaller** | increasing | \`stack top > current\` | 1475 Final Prices With Special Discount |
| **Previous greater / smaller** | same, but scan right-to-left | mirror image | 901 Online Stock Span |
| **Span bounded on both sides** | increasing, store indices | pop while \`top >= current\`, and compute width on pop | 84 Largest Rectangle · 42 Trapping Rain Water · 85 Maximal Rectangle |

:::note[Circular arrays: run the loop twice, do not duplicate the array]
For "next greater in a circular array" (LC 503), iterate \`i\` over
\`range(2 * n)\` and index with \`i % n\`, pushing only while \`i < n\`. Physically
concatenating the array also works and costs $O(n)$ extra memory for no benefit —
mentioning the modulo version is a small, cheap signal of fluency.
:::

:::caution[Largest Rectangle needs a sentinel, and it is the whole trick]
In LC 84 a bar still on the stack at the end has no right boundary, so its
rectangle is never computed. The fix is to append a sentinel height of \`0\`, which
is smaller than everything and therefore forces every remaining bar to pop and be
measured. Without it the answer is silently too small on any non-decreasing input.
:::`,
      },
      {
        heading: "## Pitfalls",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Pitfalls

- **Storing values instead of indices.** \`out[j] = i - j\` needs \`j\`. Once you
  have pushed only the value, the position is gone and distance questions become
  unanswerable. Push indices; read values through them.
- **Using \`<\` where \`<=\` belongs, or the reverse.** With equal values, \`<=\`
  pops the earlier equal element and \`<\` keeps it. For "days until *strictly*
  warmer" that choice changes the answer on flat runs like \`[73, 73, 74]\`.
- **Forgetting the leftovers.** Anything still on the stack has no answer. Pre-fill
  the output with the default (0, or −1) rather than trying to handle it afterwards.
- **Omitting the sentinel in span problems.** LC 84 and LC 85 both need it. This
  produces a plausible answer that is wrong only on some inputs, which is the
  hardest kind of bug to spot in an interview.
- **Claiming $O(n)$ without being able to justify it.** The nested \`while\` looks
  quadratic. Be ready to say: each index is pushed exactly once and popped at most
  once, so total stack operations are bounded by $2n$ regardless of how uneven
  individual iterations are.`,
      },
      {
        heading: "## Interview follow-ups",
        before: ["## Edge-case checklist", "## Recap"],
        body: `## Interview follow-ups

| They ask | What they're checking | The answer |
| --- | --- | --- |
| "There's a while inside a for — why is it $O(n)$?" | Amortised reasoning | Each index is pushed once and popped at most once, so total stack operations are at most $2n$. Individual iterations vary wildly; only the total is bounded |
| "What is on the stack, in words?" | Whether you understand the invariant | Every index whose answer is not yet known, kept in decreasing value order — so a new element resolves a prefix of them and never has to look deeper |
| "Make it work on a circular array" | Adaptability | Loop \`i\` over \`2n\` and index \`i % n\`, pushing only while \`i < n\` |
| "Now I want the largest rectangle in the histogram" | Whether you see the same pattern | Increasing stack, compute width on each pop, and append a sentinel 0 so every bar is forced out and measured |
| "Can you do it in $O(1)$ space?" | Whether you know the limits | Not in general — the stack can hold $n$ entries (a strictly decreasing input). For the *count* of pops only, sometimes; for per-element answers, no |
| "Same problem, but as a stream" | Practical modelling | Works unchanged for "previous greater" (LC 901 Stock Span). "Next greater" cannot be answered in a stream at all, because the answer depends on the future |`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Monotonic stack — self-check"
  questions={[
    {
      q: "What do the entries on a monotonic stack represent?",
      options: [
        "The largest values seen so far, in order",
        "Indices whose answer is still unknown, kept in decreasing value order",
        "A sliding window of the last k elements",
        "The answer being built up in reverse",
      ],
      answer: 1,
      explain:
        "This is the invariant the whole pattern rests on. Because entries are ordered by value, a new element resolves a prefix of them and never needs to look deeper — which is what makes the pop loop cheap in aggregate.",
    },
    {
      q: "The pop loop is nested inside the scan loop. Why is the algorithm still O(n)?",
      options: [
        "The inner loop runs at most a constant number of times per iteration",
        "Each index is pushed once and popped at most once, so total stack operations are bounded by 2n",
        "The stack never exceeds a constant size",
        "Python optimises while loops over lists",
      ],
      answer: 1,
      explain:
        "An amortised argument, not a per-iteration one. One iteration may pop five entries and the next may pop none; the bound is on the sum across the whole run.",
    },
    {
      q: "Why push indices rather than values?",
      options: [
        "Indices are smaller integers, so it saves memory",
        "Because distance answers like out[j] = i - j need j, and a value cannot recover its position",
        "Values would break the monotonic ordering",
        "It makes no difference",
      ],
      answer: 1,
      explain:
        "Push indices and read values through them. The moment a problem asks 'how far' rather than 'what value', storing values makes the question unanswerable.",
    },
    {
      q: "In Largest Rectangle in a Histogram, why append a sentinel height of 0?",
      options: [
        "To avoid an empty-stack check",
        "To force every bar still on the stack to pop and have its rectangle measured, since it has no right boundary otherwise",
        "To make the stack strictly increasing",
        "It is an optimisation and can be omitted",
      ],
      answer: 1,
      explain:
        "A bar left on the stack never got a right boundary, so its rectangle is never computed. The sentinel is smaller than every real height, so it forces all of them out. Omitting it gives an answer that is too small on non-decreasing inputs — a wrong answer that passes many tests.",
    },
    {
      q: "The problem is 'next greater element in a circular array'. What is the clean approach?",
      options: [
        "Concatenate the array with itself and run the usual algorithm",
        "Iterate i over 2n and index with i % n, pushing only while i < n",
        "Run the algorithm twice and merge the results",
        "Reverse the array first",
      ],
      answer: 1,
      explain:
        "Both work, but the modulo version uses no extra memory. Concatenating costs O(n) space for no benefit, and mentioning the difference is a cheap signal of fluency.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — "next/previous greater or smaller", or a span bounded by smaller values
  on both sides.
- **Invariant** — the stack holds indices whose answer is unknown, in decreasing
  (or increasing) value order.
- **Template** — for each \`i\`: \`while stack and cmp(a[stack[-1]], a[i]): j = pop; out[j] = f(i, j)\`,
  then \`push(i)\`.
- **Complexity** — $O(n)$ amortised ($\\le 2n$ stack operations), $O(n)$ space worst
  case.
- **Remember** — push **indices**; pre-fill the output for the leftovers; span
  problems need a **sentinel**.
- **Fails when** — the query is about a window (use a monotonic deque) or a k-th
  value (use a heap).`,
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Kadane and Maximum Subarray.mdx`,
    imports: ["Quiz", "ArrayStepper"],
    sections: [
      {
        heading: "## Visual intuition",
        before: ["## The variant map", "## Practice", "## LeetCode problem set"],
        body: `## Visual intuition

One question per step: is it better to extend the run I am on, or throw it away
and start fresh here? Watch the frames where the run restarts.

<ArrayStepper
  client:visible
  algo="kadane"
  values={[-2, 1, -3, 4, -1, 2, 1, -5, 4]}
  title="Extend, or restart — one decision per element"
  lib="LC 53 · O(n) time, O(1) space"
  desc="The restart happens exactly when the running total has gone negative: a negative prefix can only drag down whatever follows, so dropping it is always at least as good. That single observation is the whole algorithm."
/>

## Complexity

| Approach | Time | Space | Note |
| --- | --- | --- | --- |
| Every subarray, summed from scratch | $O(n^3)$ | $O(1)$ | the naive triple loop |
| Every subarray, running sum | $O(n^2)$ | $O(1)$ | fine up to a few thousand |
| Divide and conquer | $O(n \\log n)$ | $O(\\log n)$ | worth mentioning; rarely the intended answer |
| **Kadane** | $O(n)$ | $O(1)$ | one pass, two variables |

Kadane's is optimal: any correct algorithm must read every element at least once,
so $O(n)$ is a lower bound.`,
      },
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

\`nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]\`. The two decision columns are what to
show an interviewer.

| \`i\` | \`nums[i]\` | extend (\`cur + v\`) | restart (\`v\`) | \`cur\` | \`best\` | decision |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | −2 | — | — | −2 | −2 | seed |
| 1 | 1 | −1 | **1** | 1 | 1 | **restart** — the −2 prefix only hurts |
| 2 | −3 | **−2** | −3 | −2 | 1 | extend (both bad; extending is less bad) |
| 3 | 4 | 2 | **4** | 4 | 4 | **restart** |
| 4 | −1 | **3** | −1 | 3 | 4 | extend |
| 5 | 2 | **5** | 2 | 5 | 5 | extend |
| 6 | 1 | **6** | 1 | 6 | **6** | extend — new best |
| 7 | −5 | **1** | −5 | 1 | 6 | extend (still positive, so worth keeping) |
| 8 | 4 | **5** | 4 | 5 | 6 | extend |

Answer 6, from \`[4, -1, 2, 1]\` at indices 3..6.

Two observations worth stating out loud:

- **The restart at \`i = 1\` and \`i = 3\` happens exactly when \`cur\` was negative.**
  That is not a coincidence — \`cur + v < v\` is algebraically the same as
  \`cur < 0\`. Some write it as "if cur < 0: cur = 0", and the two are identical.
- **\`best\` was last updated at \`i = 6\`, three steps before the end.** The maximum
  subarray does not have to end at the last element, which is why \`best\` is a
  separate variable from \`cur\`. Returning \`cur\` is the classic wrong answer.`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Kadane's algorithm — self-check"
  questions={[
    {
      q: "Why are \`cur\` and \`best\` separate variables?",
      options: [
        "For readability only — one variable would work",
        "Because the maximum subarray need not end at the last element, so the running value and the best-ever value differ",
        "Because cur can be negative and best cannot",
        "To handle the empty array case",
      ],
      answer: 1,
      explain:
        "cur is the best subarray ending exactly at i; best is the maximum over all i. Returning cur is the standard wrong answer and it passes any input whose answer happens to end at the last element.",
    },
    {
      q: "The array is all negative: [-3, -1, -4]. What does a correct Kadane return?",
      options: [
        "0, since the empty subarray sums to 0",
        "-1, the largest single element, because the subarray must be non-empty",
        "-8, the total",
        "It is undefined",
      ],
      answer: 1,
      explain:
        "This is the edge case that catches implementations initialised with best = 0. LC 53 requires a non-empty subarray, so seed both cur and best with nums[0], never with 0. If a problem does allow the empty subarray, 0 is right — clarify which.",
    },
    {
      q: "\`cur = max(v, cur + v)\` restarts the run. When exactly does that happen?",
      options: [
        "When v is positive",
        "Exactly when cur is negative, since cur + v < v is equivalent to cur < 0",
        "When v is larger than best",
        "At every local minimum",
      ],
      answer: 1,
      explain:
        "The two formulations — max(v, cur + v) and 'if cur < 0: cur = 0' — are algebraically identical. A negative prefix can only reduce whatever follows it, so discarding it is always at least as good.",
    },
    {
      q: "Now return the subarray itself, not just its sum. What changes?",
      options: [
        "Nothing — the sum determines the subarray",
        "Track a start index that resets on every restart, and record start and end whenever best improves",
        "You must switch to the O(n²) approach",
        "Run Kadane twice, forwards and backwards",
      ],
      answer: 1,
      explain:
        "Three extra variables and no change in complexity. This is the most common follow-up on LC 53, and getting the bookkeeping right — reset start on restart, capture both bounds on improvement — is the whole of it.",
    },
    {
      q: "The array is circular (LC 918). What is the trick?",
      options: [
        "Run Kadane on the array concatenated with itself",
        "The answer is either a normal maximum subarray, or the total minus the minimum subarray — take the larger, guarding the all-negative case",
        "Sort the array first",
        "Use a sliding window of size n",
      ],
      answer: 1,
      explain:
        "A wrapping subarray is exactly the complement of a non-wrapping one, so minimising the middle maximises the wrap. The guard matters: if every element is negative the 'total minus min' branch returns the empty subarray, so fall back to the plain answer.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — "maximum sum / product of a **contiguous** subarray", and negative
  values are allowed (which is what rules out a sliding window).
- **Invariant** — \`cur\` is the best subarray **ending exactly at \`i\`**; \`best\`
  is the maximum over all \`i\`.
- **Template** — \`cur = max(v, cur + v)\`, then \`best = max(best, cur)\`. Seed both
  with \`nums[0]\`, never with 0.
- **Complexity** — $O(n)$ time, $O(1)$ space, and optimal.
- **Remember** — the restart condition is exactly "\`cur\` went negative". Return
  \`best\`, not \`cur\`.
- **Variants** — circular (total − minimum subarray, with an all-negative guard);
  product (track min *and* max, because a negative flips them); return the
  subarray (track \`start\`).`,
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Prefix Sum with HashMap.mdx`,
    imports: ["Quiz", "ArrayStepper"],
    sections: [
      {
        heading: "## Visual intuition",
        before: ["## The variant map", "## Practice", "## LeetCode problem set"],
        body: `## Visual intuition

The chips under the row are the map from prefix sum to how many times it has been
seen. Watch the sentinel \`{0: 1}\` do its work on the very first hit.

<ArrayStepper
  client:visible
  algo="subarray-sum-k"
  values={[1, 2, 3, -3, 1, 1, 1]}
  target={3}
  title="A subarray sums to k exactly when two prefix sums differ by k"
  lib="LC 560 · O(n) time and space"
  desc="The array contains a negative number, which is precisely why a sliding window cannot solve this: shrinking from the left could increase the sum, so 'too big, shrink' is unsound. Prefix sums do not care about sign."
/>

## Complexity

| Approach | Time | Space |
| --- | --- | --- |
| Every subarray, summed from scratch | $O(n^3)$ | $O(1)$ |
| Every subarray, running sum | $O(n^2)$ | $O(1)$ |
| **Prefix sum + hash map** | $O(n)$ | $O(n)$ |

The $O(n)$ space is unavoidable here and worth naming: the map can hold $n$
distinct prefix sums. That is the trade this pattern makes — memory for a factor
of $n$ in time — and it is the answer to "can you do it in $O(1)$ space?"
(you cannot, in general).`,
      },
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

LC 560 with \`k = 3\`, \`nums = [1, 2, 3, -3, 1, 1, 1]\`. The \`want\` column is the
whole idea: a subarray ending here sums to \`k\` exactly when some earlier prefix
equals \`running − k\`.

| \`i\` | \`v\` | \`running\` | \`want = running − k\` | seen count | \`count\` | map after |
| --- | --- | --- | --- | --- | --- | --- |
| — | — | 0 | — | — | 0 | \`{0: 1}\` |
| 0 | 1 | 1 | −2 | 0 | 0 | \`{0:1, 1:1}\` |
| 1 | 2 | 3 | **0** | **1** | **1** | \`{0:1, 1:1, 3:1}\` |
| 2 | 3 | 6 | **3** | **1** | **2** | \`{0:1, 1:1, 3:1, 6:1}\` |
| 3 | −3 | 3 | 0 | 1 | **3** | \`{0:1, 1:1, 3:2, 6:1}\` |
| 4 | 1 | 4 | 1 | 1 | **4** | \`{0:1, 1:1, 3:2, 4:1, 6:1}\` |
| 5 | 1 | 5 | 2 | 0 | 4 | \`… 5:1\` |
| 6 | 1 | 6 | **3** | **2** | **6** | \`… 6:2\` |

Answer: 6 subarrays.

Three things that table makes concrete:

- **The \`{0: 1}\` sentinel earns its keep at \`i = 1\`.** The subarray \`[1, 2]\`
  starts at index 0, so the "earlier prefix" it needs is the *empty* prefix. Omit
  the sentinel and every subarray starting at index 0 is missed — the single most
  common bug in this pattern.
- **At \`i = 3\` the running sum returns to 3, a value already seen.** That is only
  possible because of the negative number, and it is exactly why the map counts
  occurrences rather than storing a boolean.
- **At \`i = 6\`, \`want = 3\` has been seen twice, so the count jumps by 2.** Using
  a set instead of a counter would add 1 and silently undercount.

:::caution[Order matters: look up before you insert]
\`count += seen[running - k]\` must happen **before** \`seen[running] += 1\`. With
\`k = 0\` the two are the same key, and inserting first counts the current prefix
against itself — producing a phantom empty subarray at every index.
:::`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Prefix sum with a hash map — self-check"
  questions={[
    {
      q: "Why is the map seeded with {0: 1}?",
      options: [
        "To avoid a KeyError on the first lookup",
        "It represents the empty prefix, which is what a subarray starting at index 0 needs to match against",
        "Because prefix sums are always non-negative",
        "It is an optimisation and can be omitted",
      ],
      answer: 1,
      explain:
        "A subarray from index 0 to i has sum running[i] − running[-1], and running[-1] is the empty prefix, 0. Without the sentinel every such subarray is missed — and the bug is invisible on inputs whose answers all start later.",
    },
    {
      q: "The array contains negative numbers. Why does that rule out a sliding window?",
      options: [
        "Windows cannot hold negative values",
        "Shrinking from the left could increase the sum, so the 'too big → shrink' decision is no longer sound",
        "The sum would overflow",
        "It does not — a window works fine",
      ],
      answer: 1,
      explain:
        "The window pattern needs the sum to move monotonically as the window grows and shrinks. A negative at the left edge breaks that, and the algorithm silently returns wrong answers. Prefix sums are sign-agnostic, which is exactly why they are the fallback.",
    },
    {
      q: "Why does the map count occurrences instead of storing a set of seen sums?",
      options: [
        "Sets are slower in Python",
        "The same prefix sum can occur several times, and each occurrence is a distinct valid subarray to count",
        "To detect duplicates in the input",
        "It makes no difference for the answer",
      ],
      answer: 1,
      explain:
        "With negatives the running sum can revisit a value. If prefix p occurred three times, there are three distinct subarrays ending here that sum to k. A set would add 1 and undercount.",
    },
    {
      q: "Does the lookup happen before or after inserting the current prefix sum, and why?",
      options: [
        "After, so the current prefix is available",
        "Before — otherwise with k = 0 the current prefix matches itself and counts a phantom empty subarray",
        "Either order works",
        "Before, purely for speed",
      ],
      answer: 1,
      explain:
        "The k = 0 case is what exposes it: running − 0 == running, so inserting first makes every index count itself. Lookup, then insert.",
    },
    {
      q: "Same problem but you need the LONGEST subarray summing to k, not the count. What changes?",
      options: [
        "Nothing — the count already gives the length",
        "Store the FIRST index at which each prefix sum occurred, and do not overwrite it",
        "Sort the prefix sums",
        "Switch to a sliding window",
      ],
      answer: 1,
      explain:
        "For a longest span you want the earliest possible start, so the first occurrence is the useful one — overwriting on a repeat would shorten the answer. That is LC 325, and the not-overwriting detail is the entire difficulty.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — count or measure **contiguous** subarrays with a target sum, **and**
  negatives are possible (which rules out a sliding window).
- **Key identity** — \`sum(i..j) == running[j] − running[i-1]\`. So a subarray
  ending at \`j\` sums to \`k\` exactly when some earlier prefix equals
  \`running[j] − k\`.
- **Template** — \`seen = {0: 1}\`; per element: \`running += v\`;
  \`count += seen.get(running - k, 0)\`; then \`seen[running] += 1\`.
- **Complexity** — $O(n)$ time, $O(n)$ space. The space is unavoidable.
- **Remember** — the \`{0: 1}\` sentinel; **count** occurrences, do not use a set;
  look up **before** inserting.
- **Variants** — longest instead of count (store the *first* index); divisible by
  k (key on \`running % k\`); equal 0s and 1s (map 0 → −1 and look for sum 0).`,
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Stack Parsing and Expression Evaluation.mdx`,
    imports: ["Quiz"],
    sections: [
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

LC 394 Decode String on \`"3[a2[c]]"\` — the nested case that separates a working
solution from one that only handles a single level.

| \`ch\` | action | \`num\` | \`cur\` | stack (bottom → top) |
| --- | --- | --- | --- | --- |
| \`3\` | accumulate digit | 3 | \`""\` | — |
| \`[\` | push \`(cur, num)\`, reset both | 0 | \`""\` | \`[("", 3)]\` |
| \`a\` | append to \`cur\` | 0 | \`"a"\` | \`[("", 3)]\` |
| \`2\` | accumulate digit | 2 | \`"a"\` | \`[("", 3)]\` |
| \`[\` | push \`(cur, num)\`, reset both | 0 | \`""\` | \`[("", 3), ("a", 2)]\` |
| \`c\` | append to \`cur\` | 0 | \`"c"\` | \`[("", 3), ("a", 2)]\` |
| \`]\` | pop \`("a", 2)\`; \`cur = "a" + "c"*2\` | 0 | \`"acc"\` | \`[("", 3)]\` |
| \`]\` | pop \`("", 3)\`; \`cur = "" + "acc"*3\` | 0 | \`"accaccacc"\` | \`[]\` |

Answer \`"accaccacc"\`.

Three details that are the whole problem:

- **The stack stores a *pair*.** Pushing only the multiplier loses the text built
  before the bracket, and \`"a2[c]"\` comes back as \`"cc"\` instead of \`"acc"\`.
- **Digits must accumulate across characters.** \`num = num * 10 + int(ch)\`, not
  \`num = int(ch)\` — otherwise \`"12[a]"\` repeats twice, not twelve times.
- **Both \`num\` and \`cur\` reset on \`[\`.** They belong to the level being entered,
  and forgetting to reset leaks state downward into the nested level.

Compare with LC 224 Basic Calculator on \`"1+(2-(3+4))"\`, where the stack holds a
running result and a sign instead of a string and a count. Same shape, different
payload — that shape is the pattern.`,
      },
      {
        heading: "## Complexity",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Complexity

| Problem shape | Time | Space |
| --- | --- | --- |
| Bracket matching (LC 20) | $O(n)$ | $O(n)$ — the stack, at worst all openers |
| Expression evaluation (LC 150, 224, 227) | $O(n)$ | $O(n)$ |
| Decode String (LC 394) | $O(\\text{output length})$ | $O(\\text{output length})$ |

Two things worth saying out loud:

- **Space is genuinely $O(n)$, not $O(1)$.** A fully nested input like
  \`"((((((..."\` puts every character on the stack. If asked to reduce it: for
  *balance checking only* a counter suffices, but a counter cannot detect crossed
  nesting like \`"([)]"\`, so it answers a weaker question.
- **Decode String is measured against its output, not its input.** \`"10[10[a]]"\`
  is nine characters and expands to a hundred, so quoting $O(n)$ in the input
  length is wrong — and being precise about which $n$ you mean is exactly the kind
  of care these rounds are looking for.`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Stack parsing — self-check"
  questions={[
    {
      q: "A counter of open brackets is simpler than a stack. Why is it not sufficient for LC 20?",
      options: [
        "It is sufficient — the stack is an over-engineering",
        "A counter cannot detect crossed nesting like ([)], where the counts balance but the order is invalid",
        "Counters cannot go negative",
        "It would be O(n²)",
      ],
      answer: 1,
      explain:
        "A counter answers the weaker question 'do the counts balance'. The stack answers 'is the nesting well-formed', because its top is always the bracket that must close next. With one bracket type a counter genuinely is enough — worth saying if asked.",
    },
    {
      q: "In Decode String, what must be pushed onto the stack at each \`[\`?",
      options: [
        "Just the repeat count",
        "Both the string built so far and the repeat count, as a pair",
        "Just the string built so far",
        "The index of the bracket",
      ],
      answer: 1,
      explain:
        "Pushing only the count loses the prefix: 'a2[c]' returns 'cc' rather than 'acc'. Pushing only the string loses the multiplier. The pair is what lets the pop reconstruct prefix + repeated middle.",
    },
    {
      q: "Why is \`num = num * 10 + int(ch)\` rather than \`num = int(ch)\`?",
      options: [
        "For speed",
        "Because multi-digit counts arrive one character at a time, so '12[a]' must repeat twelve times, not two",
        "To handle negative numbers",
        "They are equivalent",
      ],
      answer: 1,
      explain:
        "A single-digit test suite hides this completely. It is the most common reason a Decode String solution passes the samples and fails the hidden tests.",
    },
    {
      q: "In Evaluate Reverse Polish Notation, which operand pops first?",
      options: [
        "The first operand, a",
        "The second operand, b — so the expression is a op b, not b op a",
        "Either, since the operators are commutative",
        "It depends on the operator",
      ],
      answer: 1,
      explain:
        "Stacks are LIFO, so the operand pushed last comes off first, and that is the right-hand operand. The mistake is invisible for + and *, and silently wrong for − and /.",
    },
    {
      q: "What is the space complexity of Decode String, and in terms of what?",
      options: [
        "O(1)",
        "O(n) in the input length",
        "O(output length) — '10[10[a]]' is nine characters and expands to a hundred",
        "O(log n)",
      ],
      answer: 2,
      explain:
        "Quoting O(n) without saying which n is wrong here. Being explicit that the bound is in the output length, and giving the expanding example, is the kind of precision these rounds score.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — nested structure in a string: brackets, parentheses, an expression, a
  path to simplify, a string to decode.
- **Invariant** — the stack holds the **enclosing context**, one entry per level
  currently open. Its depth is the nesting depth.
- **Template** — scan left to right; on an *opener* push the current context and
  reset it; on a *closer* pop and combine the popped context with what was built
  inside.
- **What to push** — a *pair*, almost always: (text so far, repeat count) for
  Decode String; (running result, sign) for Basic Calculator. Pushing one half is
  the standard bug.
- **Complexity** — $O(n)$ time, $O(n)$ space. For Decode String, $O(\\text{output})$
  — say which $n$ you mean.
- **Remember** — accumulate multi-digit numbers with \`num*10 + d\`; reset the
  level's state on the opener; in RPN the **second** operand pops first.`,
      },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════
  {
    file: `${P5}/Trie Patterns.mdx`,
    imports: ["Quiz", "TrieView"],
    sections: [
      {
        heading: "## Visual intuition",
        before: ["## The variant map", "## Practice", "## LeetCode problem set"],
        body: `## Visual intuition

Characters live on **edges**, and every shared prefix is stored exactly once —
which is the property every problem in this family exploits.

<TrieView
  client:visible
  words={["cat", "car", "card", "dog"]}
  query="car"
  title="Prefix sharing, and why the end-of-word flag is separate"
  lib="prefix tree"
  desc="Note that 'car' terminates inside the path to 'card'. Without an explicit end-of-word flag a trie cannot tell a stored word from a mere prefix, and 'is car a word' becomes unanswerable."
/>`,
      },
      {
        heading: "## Dry run",
        before: ["## Interview follow-ups", "## Edge-case checklist", "## Recap"],
        body: `## Dry run

LC 212 Word Search II is the problem this pattern exists for. Grid:

\`\`\`
o a a n
e t a e
i h k r
i f l v
\`\`\`

with \`words = ["oath", "pea", "eat", "rain"]\`.

The naive approach runs a separate DFS per word: 4 words × 16 start cells × up to
4 directions per step. The trie approach walks the grid **once**, carrying a trie
node alongside the position.

| Start cell | trie node after | outcome |
| --- | --- | --- |
| \`(0,0) o\` | root → \`o\` | \`o\` exists (prefix of "oath") — continue |
| \`(0,0)→(1,0) e\` | \`o\` has no child \`e\` | **prune immediately**, whole branch dead |
| \`(0,0)→(0,1) a\` | \`o\` → \`a\` | continue |
| \`… → (1,1) t\` | \`oa\` → \`t\` | continue |
| \`… → (2,1) h\` | \`oat\` → \`h\`, \`is_word\` set | **record "oath"** |
| \`(0,1) a\` | root has no child \`a\`… | actually it does not — prune at depth 1 |
| \`(1,0) e\` | root → \`e\` (prefix of "eat") | continue |
| \`(1,0)→(1,1) t\` | \`e\` → \`t\` | continue |
| \`(1,1)→(1,2) a\` | \`et\` has no child \`a\` | prune |

The point is the second row. A per-word DFS would have explored that entire
subtree four separate times before failing. With a trie, one lookup that returns
\`None\` kills the branch for **every** word simultaneously — and that is the
difference between passing and a time-limit exceeded.

:::tip[The optimisation interviewers actually want to hear]
After recording a match, **delete the word from the trie** (or unset its flag and
prune now-childless nodes). Otherwise a grid containing the same word many times
re-explores it every time. This is the follow-up on LC 212, and it is what turns a
just-passing solution into a comfortable one.
:::`,
      },
      {
        heading: "## Self-check",
        before: ["## Recap"],
        body: `## Self-check

<Quiz
  title="Trie patterns — self-check"
  questions={[
    {
      q: "Why is \`is_word\` a separate flag rather than just 'this node has no children'?",
      options: [
        "For speed",
        "Because a word can terminate inside the path to a longer word — 'car' inside 'card'",
        "To support deletion",
        "It is redundant and can be dropped",
      ],
      answer: 1,
      explain:
        "Leaf-ness and word-ness are different properties. Conflating them makes 'is car a word' unanswerable once 'card' is inserted, and it is the most common trie bug.",
    },
    {
      q: "What does a trie buy over a hash set of words?",
      options: [
        "Faster exact lookup",
        "Prefix queries — 'does any word start with this?' — which a hash set cannot answer without checking every word",
        "Less memory in all cases",
        "Nothing; a hash set is strictly better",
      ],
      answer: 1,
      explain:
        "For exact lookup a hash set is as fast and simpler. The trie earns its place the moment prefixes matter — autocomplete, or pruning a search — and Word Search II is entirely about that pruning.",
    },
    {
      q: "In Word Search II, why is one grid DFS carrying a trie node better than one DFS per word?",
      options: [
        "It uses less memory",
        "A single failed child lookup prunes the branch for every word at once, instead of once per word",
        "It avoids recursion",
        "It handles duplicate letters better",
      ],
      answer: 1,
      explain:
        "This is the whole reason the problem is a trie problem. Per-word DFS re-explores the same dead-end subtrees once per word; the trie collapses all of those failures into one lookup returning None.",
    },
    {
      q: "After finding a word in LC 212, what is the standard optimisation?",
      options: [
        "Restart the search from the next cell",
        "Remove the word from the trie, so a grid containing it many times does not re-explore it",
        "Cache the grid position",
        "Sort the word list",
      ],
      answer: 1,
      explain:
        "Unset the flag and prune now-childless nodes. Without it, a grid with the same word in twenty places pays the full search cost twenty times. This is the follow-up interviewers ask.",
    },
    {
      q: "What is the space complexity of a trie holding n words of average length L?",
      options: [
        "O(n) — one node per word",
        "O(n · L) worst case, but far less when prefixes are shared",
        "O(L) — independent of the word count",
        "O(n log L)",
      ],
      answer: 1,
      explain:
        "The worst case is no shared prefixes at all, giving one node per character. Real dictionaries share heavily, which is the whole point — but quote the worst case and then note the sharing.",
    },
  ]}
/>`,
      },
      {
        heading: "## Recall card",
        before: ["## Recap"],
        body: `## Recall card

- **Cue** — many words plus a **prefix** question: autocomplete, wildcard search,
  or a grid/string search that should prune dead branches early.
- **Structure** — \`children: dict[str, Node]\` plus an \`is_word\` flag. Characters
  are on edges; nodes are positions in the shared prefix tree.
- **Why not a hash set** — a set answers exact membership just as fast. Only a trie
  answers "does *any* word start with this", which is what makes pruning possible.
- **Complexity** — insert and search are $O(L)$, independent of how many words are
  stored. Space is $O(n \\cdot L)$ worst case, much less with shared prefixes.
- **Remember** — \`is_word\` is **not** the same as "no children"; delete matched
  words in LC 212; carry the trie node alongside the DFS position rather than
  re-searching per word.
- **Variants** — wildcard \`.\` (branch to every child at that step, LC 211);
  binary trie over bits for maximum-XOR (LC 421); count-per-node for prefix counts.`,
      },
    ],
  },
];

const IMPORT_LINES = {
  Quiz: 'import Quiz from "../../../../components/Quiz.astro";',
  ArrayStepper: 'import ArrayStepper from "../../../../components/viz/ArrayStepper.tsx";',
  TrieView: 'import TrieView from "../../../../components/viz/TrieView.tsx";',
};

let pagesChanged = 0;
let sectionsAdded = 0;

for (const page of PAGES) {
  const path = join(DOCS, page.file);
  if (!existsSync(path)) {
    console.log(`MISSING  ${page.file}`);
    continue;
  }

  let text = readFileSync(path, "utf8");
  const name = page.file.split("/").pop();
  let added = 0;

  for (const imp of page.imports) {
    const line = IMPORT_LINES[imp];
    if (text.includes(line)) continue;
    const imports = [...text.matchAll(/^import .*?;\s*$/gm)];
    if (imports.length > 0) {
      const at = imports[imports.length - 1].index + imports[imports.length - 1][0].length;
      text = text.slice(0, at) + `\n\n${line}` + text.slice(at);
    } else {
      const fm = text.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
      text = text.slice(0, fm[0].length) + `\n${line}\n` + text.slice(fm[0].length);
    }
  }

  for (const section of page.sections) {
    if (text.includes(section.heading)) continue;

    let inserted = false;
    for (const anchor of section.before ?? []) {
      const idx = text.indexOf(`\n${anchor}`);
      if (idx !== -1) {
        text = text.slice(0, idx + 1) + section.body + "\n\n" + text.slice(idx + 1);
        inserted = true;
        break;
      }
    }
    if (!inserted) {
      text = text.replace(/\s*$/, "\n\n") + section.body + "\n";
    }
    added += 1;
    sectionsAdded += 1;
  }

  // MDX needs a blank line after an import before prose or JSX.
  text = text.replace(/^(import .*?;)\n(?=[^\s\n]|<)/gm, "$1\n\n").replace(/\n{4,}/g, "\n\n\n");

  writeFileSync(path, text, "utf8");
  if (added > 0) pagesChanged += 1;
  console.log(`${added > 0 ? "ok " : "-- "} ${name}  (+${added} sections)`);
}

console.log(`\n${sectionsAdded} section(s) added across ${pagesChanged} page(s).`);

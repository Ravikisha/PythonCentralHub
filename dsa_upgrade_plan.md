# DSA Section Upgrade Plan — "Big-Tech Ready"

> Goal: turn the existing 76-page DSA track from a *good theory reference* into a
> **complete big-tech interview preparation course** — every asking pattern covered,
> every pattern backed by real LeetCode problems, every problem graded in-browser.

---

## 1. Where the section stands today (audit)

| Metric | Today |
|---|---|
| Pages | 76 across 11 phases, ~28,800 lines |
| Theory quality | Strong — intuition, p5 viz, mermaid, KaTeX, complexity tables |
| "LeetCode" sections | 48 headings, **7 different heading spellings**, all bare bullet lists |
| LeetCode problem numbers | **0** |
| Links to leetcode.com | **0** |
| Graded exercises | 197 `DataCampExercise` blocks — but **~95% are fill-in-the-blank `___` puzzles on toy inputs** |
| Problem-set pages (Phase-11) | 5 pages, `# TODO` stubs, **no grading**, no LC numbers/links |
| Named patterns covered | 15 (Phase-05) |
| Named patterns a big-tech loop actually draws from | **~42** |

### The three real gaps

1. **No real problems.** `- **Two Sum** -- Easy` is a name, not a problem. There is no
   number, no link, no statement, no constraints, no test, no editorial. A learner cannot
   *practice* from these pages — only read them.
2. **The "tests" don't test.** `window_sum += arr[right] - arr[right - ___]` grades whether
   you can retype one character. It does not build the skill of going from a blank editor to
   a working `O(n)` solution — which is the only skill the interview measures.
3. **Pattern coverage is ~35%.** Phase-05's 15 patterns are the classic Grokking list. A
   real big-tech loop also draws heavily on families that have **no pattern page at all**:
   design problems (LRU Cache, Min Stack, Iterator), greedy, tree DFS/BFS as patterns,
   grid/island traversal, two heaps (running median), quickselect, monotonic deque,
   sweep line, matrix manipulation, bitwise XOR, palindrome expansion, stack parsing.

---

## 2. The Pattern Catalog — all 42 asking patterns

This is the spine of the upgrade. Every row becomes a page with a template, ≥3 real
LeetCode problems as **graded exercises**, and a wider linked problem set.

Legend: ✅ page exists · 🔧 page exists, needs pattern-ification · 🆕 new page

### Family A — Arrays & Two Pointers (10)
| # | Pattern | Status | Anchor problems (LC #) |
|---|---|---|---|
| A1 | Two Pointers (converging) | ✅ | 167, 15, 11, 42 |
| A2 | Fast & Slow Pointers | ✅ | 141, 142, 202, 287 |
| A3 | Sliding Window — fixed size | ✅ | 643, 1456, 567 |
| A4 | Sliding Window — variable size | ✅ | 3, 209, 424, 76 |
| A5 | Monotonic Deque (window max/min) | 🆕 | 239, 862, 1499 |
| A6 | Prefix Sums & Difference Arrays | ✅ | 303, 304, 1109 |
| A7 | Prefix Sum + HashMap (count subarrays) | 🆕 | 560, 523, 974, 325 |
| A8 | Kadane / Maximum Subarray | 🆕 | 53, 152, 918, 1749 |
| A9 | Cyclic Sort / Index-as-Hash | ✅ | 268, 287, 41, 448 |
| A10 | Matrix & Grid Manipulation | 🆕 | 54, 48, 73, 59, 498 |

### Family B — Sorting, Searching & Selection (7)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| B1 | Binary Search — bounds & variants | ✅ | 704, 35, 34, 278 |
| B2 | Binary Search on Answer | ✅ | 875, 1011, 410, 1482 |
| B3 | Binary Search on Rotated / Peak / 2D | 🆕 | 33, 81, 153, 162, 74, 240 |
| B4 | Quickselect (Nth element) | 🆕 | 215, 973, 347 |
| B5 | Top-K with Heap | ✅ | 215, 347, 703, 1046 |
| B6 | Two Heaps (running median) | 🆕 | 295, 480, 502 |
| B7 | K-way Merge | ✅ | 23, 378, 632, 373 |

### Family C — Intervals & Greedy (5)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| C1 | Merge Intervals | ✅ | 56, 57, 435, 252, 253 |
| C2 | Sweep Line / Event Counting | 🆕 | 253, 1094, 218, 759 |
| C3 | Greedy — interval scheduling | 🆕 | 435, 452, 1024 |
| C4 | Greedy — reachability & jumps | 🆕 | 55, 45, 134, 861 |
| C5 | Sorting + Custom Comparator | 🆕 | 179, 937, 1029, 406 |

### Family D — Linked Lists (3)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| D1 | In-place Reversal | ✅ | 206, 92, 25, 234 |
| D2 | Dummy-head Rewiring & Merging | 🆕 | 21, 2, 24, 19, 61, 86 |
| D3 | Copy / Flatten / Multilevel | 🆕 | 138, 430, 143 |

### Family E — Stacks & Strings (5)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| E1 | Monotonic Stack | ✅ | 496, 503, 739, 84, 42, 907 |
| E2 | Stack Parsing / Expression Eval | 🆕 | 20, 150, 224, 227, 394, 71 |
| E3 | Palindrome — expand & DP | 🆕 | 5, 647, 131, 516 |
| E4 | Frequency / Anagram Counting | 🆕 | 242, 49, 438, 383, 451 |
| E5 | Trie-driven problems | 🔧 | 208, 211, 212, 648, 1268 |

### Family F — Trees (6)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| F1 | Tree DFS — root-to-leaf & path sums | 🆕 | 112, 113, 124, 543, 129 |
| F2 | Tree BFS — level order | 🆕 | 102, 103, 199, 116, 515 |
| F3 | BST Properties (inorder, kth, validate) | 🔧 | 98, 230, 700, 701, 450, 108 |
| F4 | Lowest Common Ancestor | 🆕 | 236, 235, 1650, 1123 |
| F5 | Tree Construction from Traversals | 🆕 | 105, 106, 889, 654 |
| F6 | Serialize / Compare / Subtree | 🆕 | 297, 100, 572, 652, 617 |

### Family G — Graphs (7)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| G1 | Graph BFS (shortest steps) | ✅ | 127, 752, 1091, 433 |
| G2 | Graph DFS (paths, components) | ✅ | 133, 797, 1443 |
| G3 | Grid DFS/BFS — islands & flood fill | 🆕 | 200, 695, 130, 417, 1020 |
| G4 | Multi-source BFS | 🆕 | 542, 994, 1162, 286 |
| G5 | Topological Sort | 🔧 | 207, 210, 269, 310, 1136 |
| G6 | Union-Find problems | 🔧 | 547, 684, 721, 990, 1319 |
| G7 | Dijkstra / weighted shortest path | 🔧 | 743, 787, 1631, 1514 |

### Family H — Recursion, Backtracking & D&C (4)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| H1 | Subsets & Combinations | ✅ | 78, 90, 39, 40, 77, 216 |
| H2 | Permutations & Arrangements | 🆕 | 46, 47, 31, 60 |
| H3 | Constrained Backtracking (board search) | ✅ | 51, 37, 79, 212, 22, 131 |
| H4 | Divide & Conquer | 🆕 | 912, 148, 241, 4, 493 |

### Family I — Dynamic Programming (7)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| I1 | 1D DP / linear decisions | ✅ | 70, 198, 213, 322, 91, 139 |
| I2 | 0/1 Knapsack & subset-sum family | ✅ | 416, 494, 474, 1049 |
| I3 | Unbounded Knapsack / coin family | 🔧 | 322, 518, 377, 279 |
| I4 | Grid DP | ✅ | 62, 63, 64, 120, 221 |
| I5 | String DP (LCS / edit distance / LIS) | ✅ | 1143, 72, 300, 583, 115 |
| I6 | Interval DP | ✅ | 312, 546, 1000, 375 |
| I7 | Bitmask & Tree DP | ✅ | 847, 1125, 337, 968 |

### Family J — Bit Manipulation & Math (4)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| J1 | Bitwise XOR tricks | 🆕 | 136, 137, 260, 268, 421 |
| J2 | Bit counting & masks | 🔧 | 191, 338, 190, 78 |
| J3 | Number theory (primes, GCD, modpow) | 🔧 | 204, 50, 172, 1071 |
| J4 | Math & Geometry | 🆕 | 66, 43, 149, 963, 587 |

### Family K — Design Problems (5) — **entirely missing today**
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| K1 | Design with HashMap + Linked List (LRU/LFU) | 🆕 | 146, 460, 432 |
| K2 | Design with auxiliary stacks/queues | 🆕 | 155, 232, 225, 622 |
| K3 | Design iterators & flatteners | 🆕 | 173, 341, 284, 251 |
| K4 | Design with randomization | 🆕 | 380, 381, 528, 384, 398 |
| K5 | Design systems-flavoured (feed, counter, tracker) | 🆕 | 355, 362, 1352, 359 |

### Family L — Simulation & Implementation (1)
| # | Pattern | Status | Anchor problems |
|---|---|---|---|
| L1 | Simulation / stateful iteration | 🆕 | 289, 1041, 874, 68, 6 |

**Totals: 42 patterns → 20 existing pattern pages, 6 need pattern-ification, 26 new pages.**

---

## 3. The new standard page spec

Every pattern page gets this spine. Sections marked **NEW** don't exist today.

1. Hook + "What you'll learn" *(keep)*
2. **The cue** — a boxed "you're looking at this pattern when…" **NEW**
3. Intuition + p5/mermaid visual *(keep)*
4. The template (runnable python) *(keep)*
5. Complexity table + Python constant-factor note *(keep)*
6. **Variant map** — the 3–5 mutations interviewers apply to the base template **NEW**
7. Common pitfalls `:::caution` *(keep)*
8. **`## Practice — real LeetCode problems`** — **≥3 graded exercises**, each a real LC
   problem *(replaces the `___` drills)*
9. **`## Full problem set`** — a numbered, linked, difficulty-tagged table **NEW**
10. **`## Interview follow-ups`** — the "what if…" questions that actually get asked **NEW**
11. **`## Edge-case checklist`** — what to say out loud before coding **NEW**
12. Recap + next-page pointer *(keep)*

### The graded-exercise format (the core change)

Each of the ≥3 practice problems per page becomes:

````mdx
### LC 3 — Longest Substring Without Repeating Characters · Medium

**Problem.** Given a string `s`, return the length of the longest substring
without repeating characters.
**Constraints.** `0 <= len(s) <= 5 * 10^4`, `s` is ASCII.
**Examples.** `"abcabcbb" -> 3` · `"bbbbb" -> 1` · `"pwwkew" -> 3`

<DataCampExercise
  lang="python"
  hint={`Expand right always. When s[right] is already inside the window, jump left to one past its previous index.`}
  code={`class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # TODO: variable-size sliding window, O(n)
        pass

# LeetCode's own examples -- all three must print correctly.
sol = Solution()
print(sol.lengthOfLongestSubstring("abcabcbb"))   # 3
print(sol.lengthOfLongestSubstring("bbbbb"))      # 1
print(sol.lengthOfLongestSubstring("pwwkew"))     # 3`}
  solution={`...full reference solution...`}
  sct={`test_output_contains("3")
test_output_contains("1")
success_msg("O(n) with O(min(n, charset)) space. Now do it on leetcode.com to hit the hidden tests.")`}
  height={280}
/>

<details>
<summary>Editorial — approach, complexity, follow-ups</summary>
...why it works, O() analysis, the 2 follow-ups an interviewer adds...
</details>
````

Key properties:
- **Real LeetCode signature** (`class Solution:` + camelCase method) so the code pastes
  straight into leetcode.com.
- **LeetCode's own examples** as the tests — the learner sees the real acceptance bar.
- Blank body (`# TODO`), not a one-character blank. This is the actual skill.
- `sct` grades on printed output; `solution` powers the built-in "Solution" tab.
- Editorial in `<details>` so the page still reads as a tutorial.

### Linking policy (accuracy guardrail)

LeetCode URLs are `https://leetcode.com/problems/<title-slug>/`. Slugs are mechanical
(lowercase, hyphens) but numbers/titles must be right. Implementation will
**verify a sample of the number↔slug pairs against leetcode.com** rather than trusting
recall for all ~350 problems, and any pair that can't be verified gets listed by title
only (no fabricated number or link).

Deliberately **not** included: per-company frequency tags ("asked at X 47 times"). That
data is behind LeetCode Premium and would have to be invented.

---

## 4. Structural decision

The DSA section is **untracked in git** — never committed, never deployed. So folder
renames are free (no live URLs to preserve). Only 41 internal cross-page links exist,
all matching `../../phase-NN-.../`, so a rename is a scripted find-and-replace.

**Recommended structure** — patterns split into family groups instead of one 40-page
sidebar entry:

```
Phase-01-Foundations                      6   (keep)
Phase-02-Python-for-DSA-and-CP            4   (keep)
Phase-03-Core-Data-Structures            11   (keep + real LC sets)
Phase-04-Sorting-and-Searching            8   (keep + real LC sets)
Phase-05-Patterns-Arrays-and-Strings     14   Family A + E
Phase-06-Patterns-Search-and-Selection    7   Family B
Phase-07-Patterns-Intervals-and-Greedy    5   Family C
Phase-08-Patterns-Linked-Lists            3   Family D
Phase-09-Patterns-Trees                   6   Family F
Phase-10-Patterns-Graphs                  7   Family G
Phase-11-Recursion-and-Backtracking       4   Family H
Phase-12-Dynamic-Programming              7   Family I  (existing 6 + 1)
Phase-13-Bit-Manipulation-and-Math        4   Family J
Phase-14-Design-Problems                  5   Family K   ← new territory
Phase-15-Simulation-and-Implementation    1   Family L
Phase-16-Advanced-CP-Topics               8   (keep)
Phase-17-Templates-and-Cheatsheets        4   (keep + pattern→problem index)
Phase-18-Interview-and-Contest-Strategy   4   (keep + expand)
Phase-19-Problem-Sets                     8   (rebuild: graded, LC-numbered)
```

**Alternative (lower churn):** keep today's 11 phase numbers and pile all 26 new pattern
pages into `Phase-05-Interview-Patterns` (→ 41 pages in one sidebar group), with Design
and Greedy squeezed in there too. Less moving, worse navigation.

---

## 5. Build order (shippable slices)

| Slice | Content | Output |
|---|---|---|
| **0** | Restructure folders, fix cross-links, normalise all LC headings, verify build | Clean skeleton |
| **1** | **Reference pages**: build 2 exemplar pages end-to-end (Sliding Window, Tree BFS) at full new spec | Locks the format |
| **2** | Family A + E — arrays, strings, stacks (14 pages: 5 new, 9 upgraded) | Highest-volume interview surface |
| **3** | Family B + C — search/selection, intervals/greedy (12 pages: 8 new) | |
| **4** | Family F + G — trees, graphs (13 pages: 8 new) | Biggest gap today |
| **5** | Family D + H + I + J — lists, backtracking, DP, bits/math (18 pages: 5 new) | |
| **6** | Family K + L — design + simulation (6 new pages) | Entirely new territory |
| **7** | Phase-03/04 data-structure pages: add real LC sets; Phase-19 problem sets rebuilt as graded, LC-numbered ladders (Blind-75 / Neetcode-150 style) | |
| **8** | Cross-cutting: pattern→problem master index, updated Pattern Recognition Guide (42 rows), 8/12-week study plans keyed to real LC numbers | |

Every slice ends with `npm run build` green and a spot-check in `npm run dev`.

### Scale, honestly

- 26 new pages × ~450 lines ≈ **12,000 new lines**
- ~50 existing pages edited (LC sections + follow-ups + real exercises)
- ~350 distinct LeetCode problems referenced; ~130 written out as graded exercises with
  reference solutions

This is a multi-session build. Slices are independently shippable — the site stays
buildable and better after every one.

---

## 6. Verification per slice

- `npm run build` clean (watch MDX brace escaping and `${` inside `code={\`…\`}`).
- No route slug contains `---` (no `" - "` in any filename).
- Every `<DataCampExercise>`: editor loads, Run executes, `sct` passes with `solution`.
- Every reference solution actually produces the printed expected output (run the
  solutions through Python locally as a batch check, not by eye).
- Every leetcode.com link resolves (batch HEAD check).
- Sidebar order and dark/light rendering spot-checked.

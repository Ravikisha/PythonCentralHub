/**
 * scripts/dsa-frontmatter.mjs — add interview metadata to DSA page frontmatter.
 *
 * The spine needs `patterns`, `difficulty`, `prereqs`, `sheets` and `companies`
 * on every topic page: `<ProblemLadder>` matches on `patterns`, the sheet
 * trackers cross-reference `sheets`, and the audit checks all of it. That is 165
 * pages of metadata, and typing it into each file by hand would be both slow and
 * a guaranteed source of typos in slugs that then silently match nothing.
 *
 * So the metadata lives here, in one reviewable table, and this script writes it.
 * Re-running is safe: existing keys are replaced, unrelated frontmatter is left
 * alone, and a page absent from the table is skipped rather than stripped.
 *
 * The canonical pattern slug is always the page's own filename slug — that is the
 * one identifier guaranteed to resolve. Extra entries are aliases.
 *
 * Run: node scripts/dsa-frontmatter.mjs
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const DOCS = "src/content/docs/DSA with Python";

/**
 * Per-page metadata. Keys are paths relative to DOCS.
 *
 * `difficulty` is the tier of the page's *material*, not of its hardest problem.
 * `sheets` records where this topic sits in each public sheet — the section name,
 * or `true` for a sheet with no sections. `companies` is crowd-reported; see the
 * caveat at the top of src/data/dsa/companies.yaml.
 */
const META = {
  // ── Phase 03 · core data structures ──────────────────────────────────────
  "Phase-03-Core-Data-Structures/Arrays and Dynamic Arrays.mdx": {
    patterns: ["arrays-and-dynamic-arrays"],
    difficulty: "easy",
    prereqs: ["big-o-and-complexity-deep-dive"],
    sheets: { neetcode150: "Arrays & Hashing", striver_a2z: "step-03", lc_top_interview_150: "Array / String" },
    companies: ["amazon", "microsoft", "apple", "bloomberg"],
  },
  "Phase-03-Core-Data-Structures/Strings.mdx": {
    patterns: ["strings"],
    difficulty: "easy",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Arrays & Hashing", striver_a2z: "step-05", lc_top_interview_150: "Array / String" },
    companies: ["microsoft", "amazon", "apple", "bloomberg"],
  },
  "Phase-03-Core-Data-Structures/Linked Lists.mdx": {
    patterns: ["linked-lists"],
    difficulty: "easy",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Linked List", blind75: true, striver_a2z: "step-06", lc_top_interview_150: "Linked List" },
    companies: ["amazon", "microsoft", "apple", "bloomberg", "meta"],
  },
  "Phase-03-Core-Data-Structures/Stacks and Queues.mdx": {
    patterns: ["stacks-and-queues"],
    difficulty: "easy",
    prereqs: ["arrays-and-dynamic-arrays", "linked-lists"],
    sheets: { neetcode150: "Stack", blind75: true, striver_a2z: "step-09", lc_top_interview_150: "Stack" },
    companies: ["amazon", "google", "meta", "bloomberg"],
  },
  "Phase-03-Core-Data-Structures/Hash Tables.mdx": {
    patterns: ["hash-tables"],
    difficulty: "easy",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Arrays & Hashing", blind75: true, striver_a2z: "step-01", lc_top_interview_150: "Hashmap" },
    companies: ["amazon", "google", "meta", "microsoft", "bloomberg"],
  },
  "Phase-03-Core-Data-Structures/Heaps and Priority Queues.mdx": {
    patterns: ["heaps-and-priority-queues"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays", "big-o-and-complexity-deep-dive"],
    sheets: { neetcode150: "Heap / Priority Queue", blind75: true, striver_a2z: "step-11", lc_top_interview_150: "Heap" },
    companies: ["amazon", "google", "meta", "uber", "bytedance"],
  },
  "Phase-03-Core-Data-Structures/Binary Trees and BST.mdx": {
    patterns: ["binary-trees-and-bst"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-13", lc_top_interview_150: "Binary Tree General" },
    companies: ["amazon", "meta", "microsoft", "google", "apple"],
  },
  "Phase-03-Core-Data-Structures/Balanced Trees Overview.mdx": {
    patterns: ["balanced-trees-overview"],
    difficulty: "hard",
    prereqs: ["binary-trees-and-bst"],
    sheets: { striver_a2z: "step-14" },
    companies: ["google", "bloomberg"],
  },
  "Phase-03-Core-Data-Structures/Tries.mdx": {
    patterns: ["tries"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst", "hash-tables"],
    sheets: { neetcode150: "Tries", blind75: true, striver_a2z: "step-17", lc_top_interview_150: "Trie" },
    companies: ["google", "amazon", "bloomberg", "bytedance"],
  },
  "Phase-03-Core-Data-Structures/Union-Find (Disjoint Set Union).mdx": {
    patterns: ["union-find-disjoint-set-union"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays", "graph-representations"],
    sheets: { neetcode150: "Graphs", blind75: true, striver_a2z: "step-15" },
    companies: ["google", "amazon", "uber", "bytedance"],
  },
  "Phase-03-Core-Data-Structures/Graph Representations.mdx": {
    patterns: ["graph-representations"],
    difficulty: "medium",
    prereqs: ["hash-tables", "arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Graphs", striver_a2z: "step-15", lc_top_interview_150: "Graph General" },
    companies: ["google", "amazon", "meta", "uber"],
  },

  // ── Phase 05 · array and string patterns ─────────────────────────────────
  "Phase-05-Patterns-Arrays-and-Strings/Two Pointers.mdx": {
    patterns: ["two-pointers"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Two Pointers", blind75: true, striver_a2z: "step-10", lc_top_interview_150: "Two Pointers" },
    companies: ["meta", "amazon", "microsoft", "bloomberg"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Prefix Sums and Difference Arrays.mdx": {
    patterns: ["prefix-sums-and-difference-arrays"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Arrays & Hashing", striver_a2z: "step-03" },
    companies: ["amazon", "google", "microsoft"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Prefix Sum with HashMap.mdx": {
    patterns: ["prefix-sum-with-hashmap"],
    difficulty: "medium",
    prereqs: ["prefix-sums-and-difference-arrays", "hash-tables"],
    sheets: { neetcode150: "Arrays & Hashing", striver_a2z: "step-03" },
    companies: ["amazon", "google", "meta", "bytedance"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Kadane and Maximum Subarray.mdx": {
    patterns: ["kadane-and-maximum-subarray"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Greedy", blind75: true, striver_a2z: "step-03", lc_top_interview_150: "Kadane's Algorithm" },
    companies: ["amazon", "microsoft", "bloomberg", "apple"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Cyclic Sort.mdx": {
    patterns: ["cyclic-sort"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Arrays & Hashing", striver_a2z: "step-03" },
    companies: ["amazon", "microsoft"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Monotonic Stack.mdx": {
    patterns: ["monotonic-stack"],
    difficulty: "medium",
    prereqs: ["stacks-and-queues"],
    sheets: { neetcode150: "Stack", striver_a2z: "step-09" },
    companies: ["amazon", "google", "meta", "bloomberg", "bytedance"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Monotonic Deque.mdx": {
    patterns: ["monotonic-deque"],
    difficulty: "hard",
    prereqs: ["monotonic-stack", "sliding-window"],
    sheets: { neetcode150: "Sliding Window", striver_a2z: "step-09" },
    companies: ["amazon", "google", "bytedance"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Frequency and Anagram Counting.mdx": {
    patterns: ["frequency-and-anagram-counting"],
    difficulty: "easy",
    prereqs: ["hash-tables", "strings"],
    sheets: { neetcode150: "Arrays & Hashing", blind75: true, striver_a2z: "step-05", lc_top_interview_150: "Hashmap" },
    companies: ["amazon", "meta", "uber", "bloomberg"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Palindrome Patterns.mdx": {
    patterns: ["palindrome-patterns"],
    difficulty: "medium",
    prereqs: ["two-pointers", "strings"],
    sheets: { neetcode150: "1-D Dynamic Programming", blind75: true, striver_a2z: "step-05" },
    companies: ["amazon", "microsoft", "meta", "bloomberg"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Matrix and Grid Manipulation.mdx": {
    patterns: ["matrix-and-grid-manipulation"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { neetcode150: "Math & Geometry", blind75: true, striver_a2z: "step-03", lc_top_interview_150: "Matrix" },
    companies: ["amazon", "microsoft", "apple", "bytedance"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Stack Parsing and Expression Evaluation.mdx": {
    patterns: ["stack-parsing-and-expression-evaluation"],
    difficulty: "medium",
    prereqs: ["stacks-and-queues"],
    sheets: { neetcode150: "Stack", blind75: true, striver_a2z: "step-09", lc_top_interview_150: "Stack" },
    companies: ["meta", "amazon", "google", "bloomberg"],
  },
  "Phase-05-Patterns-Arrays-and-Strings/Trie Patterns.mdx": {
    patterns: ["trie-patterns"],
    difficulty: "hard",
    prereqs: ["tries", "backtracking"],
    sheets: { neetcode150: "Tries", blind75: true, striver_a2z: "step-17", lc_top_interview_150: "Trie" },
    companies: ["google", "amazon", "bytedance"],
  },
  // ── Phase 09 · tree patterns ─────────────────────────────────────────────
  "Phase-09-Patterns-Trees/Tree DFS Paths and Sums.mdx": {
    patterns: ["tree-dfs-paths-and-sums"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst", "python-recursion-and-iterative-conversion"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-13", lc_top_interview_150: "Binary Tree General" },
    companies: ["meta", "amazon", "google", "microsoft"],
  },
  "Phase-09-Patterns-Trees/BST Patterns.mdx": {
    patterns: ["bst-patterns"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-14", lc_top_interview_150: "Binary Search Tree" },
    companies: ["amazon", "microsoft", "meta", "bloomberg"],
  },
  "Phase-09-Patterns-Trees/Lowest Common Ancestor.mdx": {
    patterns: ["lowest-common-ancestor"],
    difficulty: "medium",
    prereqs: ["tree-dfs-paths-and-sums"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-13", lc_top_interview_150: "Binary Tree General" },
    companies: ["meta", "amazon", "microsoft", "apple"],
  },
  "Phase-09-Patterns-Trees/Tree Construction from Traversals.mdx": {
    patterns: ["tree-construction-from-traversals"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst", "hash-tables"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-13", lc_top_interview_150: "Binary Tree General" },
    companies: ["amazon", "google", "microsoft"],
  },
  "Phase-09-Patterns-Trees/Serialize Compare and Subtree.mdx": {
    patterns: ["serialize-compare-and-subtree"],
    difficulty: "medium",
    prereqs: ["tree-dfs-paths-and-sums", "tree-bfs-and-level-order"],
    sheets: { neetcode150: "Trees", blind75: true, striver_a2z: "step-13" },
    companies: ["meta", "amazon", "google", "bloomberg"],
  },

  // ── Phase 10 · graph patterns ────────────────────────────────────────────
  "Phase-10-Patterns-Graphs/Breadth First Search.mdx": {
    patterns: ["breadth-first-search"],
    difficulty: "medium",
    prereqs: ["graph-representations", "stacks-and-queues"],
    sheets: { neetcode150: "Graphs", striver_a2z: "step-15", lc_top_interview_150: "Graph BFS" },
    companies: ["amazon", "google", "meta", "microsoft", "bytedance"],
  },
  "Phase-10-Patterns-Graphs/Depth First Search.mdx": {
    patterns: ["depth-first-search"],
    difficulty: "medium",
    prereqs: ["graph-representations", "python-recursion-and-iterative-conversion"],
    sheets: { neetcode150: "Graphs", striver_a2z: "step-15", lc_top_interview_150: "Graph General" },
    companies: ["amazon", "google", "meta", "microsoft"],
  },
  "Phase-10-Patterns-Graphs/Graph Traversal and Connected Components.mdx": {
    patterns: ["graph-traversal-and-connected-components"],
    difficulty: "medium",
    prereqs: ["breadth-first-search", "depth-first-search"],
    sheets: { neetcode150: "Graphs", blind75: true, striver_a2z: "step-15" },
    companies: ["amazon", "google", "meta"],
  },
  "Phase-10-Patterns-Graphs/Topological Sort.mdx": {
    patterns: ["topological-sort"],
    difficulty: "medium",
    prereqs: ["graph-representations", "breadth-first-search"],
    sheets: { neetcode150: "Graphs", blind75: true, striver_a2z: "step-15", lc_top_interview_150: "Graph General" },
    companies: ["google", "amazon", "meta", "bytedance"],
  },
  "Phase-10-Patterns-Graphs/Cycle Detection and Bipartite Checking.mdx": {
    patterns: ["cycle-detection-and-bipartite-checking"],
    difficulty: "medium",
    prereqs: ["depth-first-search", "topological-sort"],
    sheets: { neetcode150: "Graphs", striver_a2z: "step-15" },
    companies: ["google", "amazon", "meta"],
  },
  "Phase-10-Patterns-Graphs/Shortest Paths Dijkstra Bellman-Ford and Floyd-Warshall.mdx": {
    patterns: ["shortest-paths-dijkstra-bellman-ford-and-floyd-warshall"],
    difficulty: "hard",
    prereqs: ["breadth-first-search", "heaps-and-priority-queues"],
    sheets: { neetcode150: "Advanced Graphs", striver_a2z: "step-15" },
    companies: ["google", "uber", "amazon", "bytedance"],
  },
  "Phase-10-Patterns-Graphs/Grid Traversal Islands and Flood Fill.mdx": {
    patterns: ["grid-traversal-islands-and-flood-fill"],
    difficulty: "medium",
    prereqs: ["breadth-first-search", "depth-first-search"],
    sheets: { neetcode150: "Graphs", blind75: true, striver_a2z: "step-15", lc_top_interview_150: "Graph General" },
    companies: ["amazon", "google", "meta", "microsoft", "bytedance"],
  },
  "Phase-10-Patterns-Graphs/Multi-source BFS.mdx": {
    patterns: ["multi-source-bfs"],
    difficulty: "medium",
    prereqs: ["breadth-first-search", "grid-traversal-islands-and-flood-fill"],
    sheets: { neetcode150: "Graphs", striver_a2z: "step-15" },
    companies: ["amazon", "microsoft", "bytedance"],
  },
  "Phase-10-Patterns-Graphs/Union-Find Problem Patterns.mdx": {
    patterns: ["union-find-problem-patterns"],
    difficulty: "medium",
    prereqs: ["union-find-disjoint-set-union"],
    sheets: { neetcode150: "Graphs", blind75: true, striver_a2z: "step-15" },
    companies: ["google", "amazon", "uber"],
  },

  // ── Phase 12 · dynamic programming ───────────────────────────────────────
  "Phase-12-Dynamic-Programming/From Recursion to DP.mdx": {
    patterns: ["from-recursion-to-dp"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { neetcode150: "1-D Dynamic Programming", blind75: true, striver_a2z: "step-16", lc_top_interview_150: "1D DP" },
    companies: ["google", "amazon", "meta", "microsoft"],
  },
  "Phase-12-Dynamic-Programming/One Dimensional DP.mdx": {
    patterns: ["one-dimensional-dp"],
    difficulty: "medium",
    prereqs: ["from-recursion-to-dp"],
    sheets: { neetcode150: "1-D Dynamic Programming", blind75: true, striver_a2z: "step-16", lc_top_interview_150: "1D DP" },
    companies: ["amazon", "google", "meta", "microsoft", "bloomberg"],
  },
  "Phase-12-Dynamic-Programming/Two Dimensional DP and Knapsack.mdx": {
    patterns: ["two-dimensional-dp-and-knapsack"],
    difficulty: "hard",
    prereqs: ["one-dimensional-dp"],
    sheets: { neetcode150: "2-D Dynamic Programming", blind75: true, striver_a2z: "step-16", lc_top_interview_150: "Multidimensional DP" },
    companies: ["google", "amazon", "microsoft", "bytedance"],
  },
  "Phase-12-Dynamic-Programming/Knapsack Variants and Subset Sum.mdx": {
    patterns: ["knapsack-variants-and-subset-sum"],
    difficulty: "hard",
    prereqs: ["two-dimensional-dp-and-knapsack"],
    sheets: { neetcode150: "1-D Dynamic Programming", striver_a2z: "step-16" },
    companies: ["google", "amazon", "bytedance"],
  },
  "Phase-12-Dynamic-Programming/DP on Grids and Intervals.mdx": {
    patterns: ["dp-on-grids-and-intervals"],
    difficulty: "hard",
    prereqs: ["two-dimensional-dp-and-knapsack"],
    sheets: { neetcode150: "2-D Dynamic Programming", blind75: true, striver_a2z: "step-16", lc_top_interview_150: "Multidimensional DP" },
    companies: ["google", "amazon", "bytedance"],
  },
  "Phase-12-Dynamic-Programming/Bitmask and Tree DP.mdx": {
    patterns: ["bitmask-and-tree-dp"],
    difficulty: "hard",
    prereqs: ["two-dimensional-dp-and-knapsack", "bit-manipulation-tricks"],
    sheets: { striver_a2z: "step-16" },
    companies: ["google", "bytedance"],
  },


  // ═══════════════════════════════════════════════════════════════════════════
  // Generated block: Phases 04, 06, 07, 08, 11, 13, 14, 15, 16, 17 and 20.
  //
  // Derived rather than hand-typed, so the slugs cannot drift:
  //   patterns    the page's own filename slug (the canonical convention)
  //   sheets      striver_a2z / striver_sde only -- those are the two sheets whose
  //               steps map PATTERNS in sheets.yaml. neetcode150 / blind75 /
  //               lc_top_interview_150 index by problem title, so a topic page's
  //               "section" could only be guessed from its problems, and that guess
  //               is wrong whenever the problems sit elsewhere (merge sort's are
  //               filed under "Linked List"). Those three are shown per-problem by
  //               <ProblemLadder>, which is the honest place for them.
  //   companies   the most frequent tags across the problems carrying this pattern
  //               -- crowd-reported, per the caveat in companies.yaml
  //   difficulty  the modal tier of those problems, then hand-corrected on five
  //               pages where the ladder's tier is not the material's tier
  //               (merge sort, fast/slow pointers, the two design pages, sparse
  //               tables)
  //   prereqs     one decision per phase
  //
  // Every pattern here already carries problems, so no page gets an empty ladder.
  // Pages deliberately absent: Phase-01/02 (conceptual -- no LeetCode ladder
  // exists for "Setup for CP"), Phase-04's four sort pages, Maximum Flow, and
  // Phase-18/19 (cheatsheets and strategy). Those need problems tagged in
  // overrides.yaml first, or they would each raise an "empty ladder" warning.
  // ═══════════════════════════════════════════════════════════════════════════
  // ── Phase-04-Sorting-and-Searching ──────────────────────────────
  "Phase-04-Sorting-and-Searching/Binary Search Template and Variants.mdx": {
    patterns: ["binary-search-template-and-variants"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays", "big-o-and-complexity-deep-dive"],
    sheets: { striver_a2z: "step-04", striver_sde: "day-11" },
    companies: ["amazon", "bloomberg", "bytedance", "google"],
  },
  "Phase-04-Sorting-and-Searching/Elementary Sorts.mdx": {
    patterns: ["elementary-sorts"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays", "big-o-and-complexity-deep-dive"],
    sheets: { striver_a2z: "step-02" },
  },
  "Phase-04-Sorting-and-Searching/Merge Sort.mdx": {
    patterns: ["merge-sort"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays", "big-o-and-complexity-deep-dive"],
    sheets: { striver_a2z: "step-02" },
    companies: ["amazon", "apple", "bloomberg", "microsoft"],
  },

  // ── Phase-06-Patterns-Search-and-Selection ──────────────────────
  "Phase-06-Patterns-Search-and-Selection/Binary Search on Answer.mdx": {
    patterns: ["binary-search-on-answer"],
    difficulty: "medium",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-04", striver_sde: "day-11" },
    companies: ["amazon", "bytedance", "google"],
  },
  "Phase-06-Patterns-Search-and-Selection/Binary Search on Rotated Arrays and Matrices.mdx": {
    patterns: ["binary-search-on-rotated-arrays-and-matrices"],
    difficulty: "medium",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-04" },
    companies: ["amazon", "bloomberg", "meta", "microsoft"],
  },
  "Phase-06-Patterns-Search-and-Selection/K-way Merge.mdx": {
    patterns: ["k-way-merge"],
    difficulty: "medium",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-11" },
  },
  "Phase-06-Patterns-Search-and-Selection/Quickselect and Nth Element.mdx": {
    patterns: ["quickselect-and-nth-element"],
    difficulty: "medium",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-04" },
    companies: ["amazon", "bytedance", "meta", "uber"],
  },
  "Phase-06-Patterns-Search-and-Selection/Top K Elements.mdx": {
    patterns: ["top-k-elements"],
    difficulty: "medium",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-11", striver_sde: "day-12" },
    companies: ["amazon", "bytedance", "meta", "uber"],
  },
  "Phase-06-Patterns-Search-and-Selection/Two Heaps and Running Median.mdx": {
    patterns: ["two-heaps-and-running-median"],
    difficulty: "hard",
    prereqs: ["binary-search-template-and-variants", "heaps-and-priority-queues"],
    sheets: { striver_a2z: "step-11", striver_sde: "day-12" },
    companies: ["amazon", "bloomberg", "google", "meta"],
  },

  // ── Phase-07-Patterns-Intervals-and-Greedy ──────────────────────
  "Phase-07-Patterns-Intervals-and-Greedy/Greedy Interval Scheduling.mdx": {
    patterns: ["greedy-interval-scheduling"],
    difficulty: "medium",
    prereqs: ["sorting-with-custom-comparators", "arrays-and-dynamic-arrays"],
    sheets: { striver_a2z: "step-12", striver_sde: "day-08" },
    companies: ["amazon", "meta", "uber"],
  },
  "Phase-07-Patterns-Intervals-and-Greedy/Greedy Reachability and Jumps.mdx": {
    patterns: ["greedy-reachability-and-jumps"],
    difficulty: "medium",
    prereqs: ["sorting-with-custom-comparators", "arrays-and-dynamic-arrays"],
    sheets: { striver_a2z: "step-12", striver_sde: "day-08" },
  },
  "Phase-07-Patterns-Intervals-and-Greedy/Merge Intervals.mdx": {
    patterns: ["merge-intervals"],
    difficulty: "medium",
    prereqs: ["sorting-with-custom-comparators", "arrays-and-dynamic-arrays"],
    sheets: { striver_a2z: "step-12", striver_sde: "day-02" },
    companies: ["amazon", "bloomberg", "google", "meta"],
  },
  "Phase-07-Patterns-Intervals-and-Greedy/Sorting with Custom Comparators.mdx": {
    patterns: ["sorting-with-custom-comparators"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
    sheets: { striver_a2z: "step-12" },
  },
  "Phase-07-Patterns-Intervals-and-Greedy/Sweep Line and Event Counting.mdx": {
    patterns: ["sweep-line-and-event-counting"],
    difficulty: "medium",
    prereqs: ["sorting-with-custom-comparators", "arrays-and-dynamic-arrays"],
    sheets: { striver_a2z: "step-12" },
  },

  // ── Phase-08-Patterns-Linked-Lists ──────────────────────────────
  "Phase-08-Patterns-Linked-Lists/Copy Flatten and Reorder.mdx": {
    patterns: ["copy-flatten-and-reorder"],
    difficulty: "medium",
    prereqs: ["linked-lists", "two-pointers"],
    sheets: { striver_a2z: "step-06", striver_sde: "day-06" },
    companies: ["amazon", "bloomberg", "meta", "apple"],
  },
  "Phase-08-Patterns-Linked-Lists/Dummy Head Rewiring and Merging.mdx": {
    patterns: ["dummy-head-rewiring-and-merging"],
    difficulty: "medium",
    prereqs: ["linked-lists", "two-pointers"],
    sheets: { striver_a2z: "step-06", striver_sde: "day-05" },
    companies: ["amazon", "apple", "bloomberg", "microsoft"],
  },
  "Phase-08-Patterns-Linked-Lists/Fast and Slow Pointers.mdx": {
    patterns: ["fast-and-slow-pointers"],
    difficulty: "medium",
    prereqs: ["linked-lists", "two-pointers"],
    sheets: { striver_a2z: "step-06", striver_sde: "day-06" },
    companies: ["amazon", "bloomberg", "microsoft"],
  },
  "Phase-08-Patterns-Linked-Lists/In-place Linked List Reversal.mdx": {
    patterns: ["in-place-linked-list-reversal"],
    difficulty: "medium",
    prereqs: ["linked-lists", "two-pointers"],
    sheets: { striver_a2z: "step-06", striver_sde: "day-05" },
    companies: ["amazon", "apple", "bloomberg", "meta"],
  },

  // ── Phase-11-Recursion-and-Backtracking ─────────────────────────
  "Phase-11-Recursion-and-Backtracking/Backtracking.mdx": {
    patterns: ["backtracking"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { striver_a2z: "step-07", striver_sde: "day-10" },
  },
  "Phase-11-Recursion-and-Backtracking/Divide and Conquer.mdx": {
    patterns: ["divide-and-conquer"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { striver_a2z: "step-07" },
    companies: ["amazon", "bytedance", "google", "microsoft"],
  },
  "Phase-11-Recursion-and-Backtracking/Permutations and Arrangements.mdx": {
    patterns: ["permutations-and-arrangements"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { striver_a2z: "step-07", striver_sde: "day-09" },
  },
  "Phase-11-Recursion-and-Backtracking/Subsets and Combinations.mdx": {
    patterns: ["subsets-and-combinations"],
    difficulty: "medium",
    prereqs: ["python-recursion-and-iterative-conversion"],
    sheets: { striver_a2z: "step-07", striver_sde: "day-09" },
  },

  // ── Phase-13-Bit-Manipulation-and-Math ──────────────────────────
  "Phase-13-Bit-Manipulation-and-Math/Bit Manipulation Tricks.mdx": {
    patterns: ["bit-manipulation-tricks"],
    difficulty: "easy",
    prereqs: ["big-o-and-complexity-deep-dive"],
    sheets: { striver_a2z: "step-08" },
  },
  "Phase-13-Bit-Manipulation-and-Math/Bitwise XOR Patterns.mdx": {
    patterns: ["bitwise-xor-patterns"],
    difficulty: "easy",
    prereqs: ["big-o-and-complexity-deep-dive"],
    sheets: { striver_a2z: "step-08" },
  },
  "Phase-13-Bit-Manipulation-and-Math/Math and Geometry Problems.mdx": {
    patterns: ["math-and-geometry-problems"],
    difficulty: "medium",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },
  "Phase-13-Bit-Manipulation-and-Math/Number Theory for Competitive Programming.mdx": {
    patterns: ["number-theory-for-competitive-programming"],
    difficulty: "medium",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },

  // ── Phase-14-Design-Problems ────────────────────────────────────
  "Phase-14-Design-Problems/Design Iterators and Flatteners.mdx": {
    patterns: ["design-iterators-and-flatteners"],
    difficulty: "medium",
    prereqs: ["hash-tables", "linked-lists"],
  },
  "Phase-14-Design-Problems/Design LRU and LFU Caches.mdx": {
    patterns: ["design-lru-and-lfu-caches"],
    difficulty: "medium",
    prereqs: ["hash-tables", "linked-lists"],
    companies: ["amazon", "bloomberg", "google", "microsoft"],
  },
  "Phase-14-Design-Problems/Design Trackers and Feeds.mdx": {
    patterns: ["design-trackers-and-feeds"],
    difficulty: "medium",
    prereqs: ["hash-tables", "linked-lists"],
  },
  "Phase-14-Design-Problems/Design with Randomization.mdx": {
    patterns: ["design-with-randomization"],
    difficulty: "medium",
    prereqs: ["hash-tables", "linked-lists"],
    companies: ["amazon", "bloomberg", "meta"],
  },
  "Phase-14-Design-Problems/Design with Stacks and Queues.mdx": {
    patterns: ["design-with-stacks-and-queues"],
    difficulty: "medium",
    prereqs: ["hash-tables", "linked-lists"],
    sheets: { striver_a2z: "step-09", striver_sde: "day-14" },
  },

  // ── Phase-15-Simulation-and-Implementation ──────────────────────
  "Phase-15-Simulation-and-Implementation/Simulation and Stateful Iteration.mdx": {
    patterns: ["simulation-and-stateful-iteration"],
    difficulty: "medium",
    prereqs: ["arrays-and-dynamic-arrays"],
  },

  // ── Phase-16-Advanced-Graph-Algorithms ──────────────────────────
  "Phase-16-Advanced-Graph-Algorithms/Minimum Spanning Trees Kruskal and Prim.mdx": {
    patterns: ["minimum-spanning-trees-kruskal-and-prim"],
    difficulty: "medium",
    prereqs: ["graph-traversal-and-connected-components", "union-find-problem-patterns"],
    sheets: { striver_a2z: "step-15", striver_sde: "day-24" },
    companies: ["amazon", "uber"],
  },
  "Phase-16-Advanced-Graph-Algorithms/Strongly Connected Components and Bridges.mdx": {
    patterns: ["strongly-connected-components-and-bridges"],
    difficulty: "hard",
    prereqs: ["graph-traversal-and-connected-components", "union-find-problem-patterns"],
    sheets: { striver_a2z: "step-15" },
  },

  // ── Phase-17-Advanced-CP-Topics ─────────────────────────────────
  "Phase-17-Advanced-CP-Topics/Advanced DP Optimizations.mdx": {
    patterns: ["advanced-dp-optimizations"],
    difficulty: "hard",
    prereqs: ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
    sheets: { striver_a2z: "step-16" },
  },
  "Phase-17-Advanced-CP-Topics/Fenwick Tree (Binary Indexed Tree).mdx": {
    patterns: ["fenwick-tree-binary-indexed-tree"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
  },
  "Phase-17-Advanced-CP-Topics/Segment Trees and Lazy Propagation.mdx": {
    patterns: ["segment-trees-and-lazy-propagation"],
    difficulty: "hard",
    prereqs: ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
  },
  "Phase-17-Advanced-CP-Topics/Sparse Tables and RMQ.mdx": {
    patterns: ["sparse-tables-and-rmq"],
    difficulty: "hard",
    prereqs: ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
    companies: ["amazon", "bytedance", "google"],
  },
  "Phase-17-Advanced-CP-Topics/String Algorithms KMP Z and Rabin-Karp.mdx": {
    patterns: ["string-algorithms-kmp-z-and-rabin-karp"],
    difficulty: "medium",
    prereqs: ["binary-trees-and-bst", "prefix-sums-and-difference-arrays"],
    sheets: { striver_a2z: "step-18", striver_sde: "day-16" },
  },

  // ── Phase-20-Problem-Sets ───────────────────────────────────────
  "Phase-20-Problem-Sets/Arrays and Strings Problem Set.mdx": {
    patterns: ["arrays-and-strings-problem-set"],
    difficulty: "medium",
    prereqs: ["pattern-recognition-guide"],
    companies: ["amazon", "meta", "bloomberg", "google"],
  },
  "Phase-20-Problem-Sets/Dynamic Programming Problem Set.mdx": {
    patterns: ["dynamic-programming-problem-set"],
    difficulty: "medium",
    prereqs: ["pattern-recognition-guide"],
    companies: ["amazon", "google", "bytedance", "microsoft"],
  },
  "Phase-20-Problem-Sets/Getting Started Problem Set.mdx": {
    patterns: ["getting-started-problem-set"],
    difficulty: "easy",
    prereqs: ["pattern-recognition-guide"],
    companies: ["amazon", "bloomberg", "microsoft", "apple"],
  },
  "Phase-20-Problem-Sets/Hard Mix Problem Set.mdx": {
    patterns: ["hard-mix-problem-set"],
    difficulty: "hard",
    prereqs: ["pattern-recognition-guide"],
    companies: ["amazon", "google", "bytedance", "bloomberg"],
  },
  "Phase-20-Problem-Sets/Trees and Graphs Problem Set.mdx": {
    patterns: ["trees-and-graphs-problem-set"],
    difficulty: "medium",
    prereqs: ["pattern-recognition-guide"],
    companies: ["amazon", "bytedance", "google", "meta"],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Phase-18 (cheatsheets) and Phase-19 (strategy).
  //
  // These pages teach no pattern of their own, so `gen-dsa-meta.mjs` skips them:
  // a slug like `algorithm-templates` carries no problems and declaring it would
  // raise an "empty ladder" warning. But they are *about* other pages' patterns,
  // so they declare THOSE slugs as aliases — every one already carries problems,
  // and <ProblemLadder pattern={[...]} /> accepts the array. That is honest (the
  // page really does cover those patterns) and it gives each page a real ladder.
  //
  // The slugs below are the ones each page actually contains a template or a
  // recommendation for — not a wishlist. Keep it that way when editing.
  // ═══════════════════════════════════════════════════════════════════════════
  // Phase-04: four pages nobody is asked to *implement* in an interview (quicksort,
  // heap sort, Timsort, counting/radix). Patterns are ALIASES of slugs whose problems
  // exercise the same machinery — each checked against the DB for a non-empty ladder.
  "Phase-04-Sorting-and-Searching/Quick Sort.mdx": {
    patterns: ["quickselect-and-nth-element", "elementary-sorts"],
    difficulty: "medium",
    prereqs: ["elementary-sorts", "recursion-fundamentals"],
  },
  "Phase-04-Sorting-and-Searching/Heap Sort.mdx": {
    patterns: ["heaps-and-priority-queues", "elementary-sorts"],
    difficulty: "medium",
    prereqs: ["heaps-and-priority-queues", "elementary-sorts"],
  },
  "Phase-04-Sorting-and-Searching/Python Sorting and Timsort.mdx": {
    patterns: ["sorting-with-custom-comparators", "merge-sort"],
    difficulty: "medium",
    prereqs: ["merge-sort", "big-o-and-complexity-deep-dive"],
  },
  "Phase-04-Sorting-and-Searching/Counting Radix and Bucket Sort.mdx": {
    patterns: ["top-k-elements", "cyclic-sort", "elementary-sorts"],
    difficulty: "medium",
    prereqs: ["elementary-sorts", "big-o-and-complexity-deep-dive"],
  },
  // Max flow has no canonical LeetCode problem of its own (see the page's own
  // caution), so these patterns are ALIASES of the pages whose problems exercise
  // the same reasoning: bipartite structure, connectivity, and union-find.
  "Phase-16-Advanced-Graph-Algorithms/Maximum Flow.mdx": {
    patterns: [
      "cycle-detection-and-bipartite-checking",
      "graph-traversal-and-connected-components",
      "union-find-problem-patterns",
    ],
    difficulty: "hard",
    prereqs: ["graph-traversal-and-connected-components", "cycle-detection-and-bipartite-checking"],
  },
  "Phase-18-Templates-and-Cheatsheets/Algorithm Templates.mdx": {
    patterns: [
      "binary-search-template-and-variants",
      "binary-search-on-answer",
      "number-theory-for-competitive-programming",
      "string-algorithms-kmp-z-and-rabin-karp",
    ],
    difficulty: "mixed",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },
  "Phase-18-Templates-and-Cheatsheets/Data Structure Templates.mdx": {
    patterns: [
      "union-find-problem-patterns",
      "segment-trees-and-lazy-propagation",
      "fenwick-tree-binary-indexed-tree",
      "trie-patterns",
    ],
    difficulty: "mixed",
    prereqs: ["arrays-and-dynamic-arrays", "binary-trees-and-bst"],
  },
  "Phase-18-Templates-and-Cheatsheets/Graph Algorithm Templates.mdx": {
    patterns: [
      "breadth-first-search",
      "depth-first-search",
      "shortest-paths-dijkstra-bellman-ford-and-floyd-warshall",
      "minimum-spanning-trees-kruskal-and-prim",
      "topological-sort",
      "union-find-problem-patterns",
    ],
    difficulty: "mixed",
    prereqs: ["graph-representations"],
  },
  "Phase-18-Templates-and-Cheatsheets/Master Complexity Cheatsheet.mdx": {
    patterns: [
      "arrays-and-dynamic-arrays",
      "hash-tables",
      "heaps-and-priority-queues",
      "binary-search-template-and-variants",
      "merge-sort",
    ],
    difficulty: "mixed",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },
  "Phase-19-Interview-and-Contest-Strategy/Pattern Recognition Guide.mdx": {
    patterns: [
      "sliding-window",
      "two-pointers",
      "binary-search-template-and-variants",
      "breadth-first-search",
      "backtracking",
      "one-dimensional-dp",
      "monotonic-stack",
      "top-k-elements",
    ],
    difficulty: "mixed",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },
  "Phase-19-Interview-and-Contest-Strategy/Study Plans and Roadmap.mdx": {
    patterns: [
      "sliding-window",
      "two-pointers",
      "binary-search-template-and-variants",
      "breadth-first-search",
      "depth-first-search",
      "topological-sort",
      "backtracking",
      "one-dimensional-dp",
    ],
    difficulty: "mixed",
    prereqs: ["pattern-recognition-guide"],
  },
  "Phase-19-Interview-and-Contest-Strategy/Contest Strategy.mdx": {
    patterns: [
      "binary-search-on-answer",
      "heaps-and-priority-queues",
      "two-pointers",
      "number-theory-for-competitive-programming",
    ],
    difficulty: "mixed",
    prereqs: ["big-o-and-complexity-deep-dive"],
  },
  "Phase-19-Interview-and-Contest-Strategy/FAANG Interview Playbook.mdx": {
    patterns: ["two-pointers", "hash-tables", "heaps-and-priority-queues", "one-dimensional-dp"],
    difficulty: "mixed",
    prereqs: ["pattern-recognition-guide"],
  },

};

/** Emit a YAML value using the block style the rest of the frontmatter uses. */
function yamlLines(key, value, indent = "") {
  if (Array.isArray(value)) {
    return [`${indent}${key}:`, ...value.map((v) => `${indent}  - ${v}`)];
  }
  if (typeof value === "object") {
    return [`${indent}${key}:`, ...Object.entries(value).map(([k, v]) => `${indent}  ${k}: ${v}`)];
  }
  return [`${indent}${key}: ${value}`];
}

const MANAGED = ["patterns", "difficulty", "prereqs", "sheets", "companies"];

let written = 0;
let skipped = 0;

for (const [rel, meta] of Object.entries(META)) {
  const path = join(DOCS, rel);
  if (!existsSync(path)) {
    console.log(`MISSING  ${rel}`);
    continue;
  }

  const text = readFileSync(path, "utf8");
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) {
    console.log(`NO FRONTMATTER  ${rel}`);
    continue;
  }

  const fmLines = m[1].split(/\r?\n/);

  // Drop any managed key we are about to rewrite, along with its indented block.
  // Everything else — title, description, sidebar — is preserved verbatim.
  const kept = [];
  let dropping = false;
  for (const line of fmLines) {
    const topLevel = /^[A-Za-z_][\w-]*:/.test(line);
    if (topLevel) {
      const key = line.slice(0, line.indexOf(":"));
      dropping = MANAGED.includes(key);
      if (dropping) continue;
    } else if (dropping) {
      continue; // an indented continuation of a dropped key
    }
    kept.push(line);
  }

  const added = MANAGED.filter((k) => meta[k] !== undefined).flatMap((k) => yamlLines(k, meta[k]));

  const rebuilt = `---\n${[...kept, ...added].join("\n")}\n---`;
  const next = text.slice(0, m.index) + rebuilt + text.slice(m.index + m[0].length);

  if (next === text) {
    skipped += 1;
    continue;
  }

  writeFileSync(path, next, "utf8");
  written += 1;
  console.log(`ok  ${rel.split("/").pop()}`);
}

console.log(`\n${written} page(s) updated, ${skipped} already current.`);
console.log(`${Object.keys(META).length} page(s) in the metadata table.`);

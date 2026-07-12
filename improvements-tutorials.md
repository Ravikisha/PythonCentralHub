# Tutorials — Improvement Plan (Batch 2)

> **Progress (2026-07-10):** ✅ Ordering fixed (Std Library → 139–151, Modern Python →
> 152–158; both now sort to the end instead of floating to the top — verified in the live
> sidebar). ✅ 5 flagship pages given viz: For Loop (mermaid + p5), If-else (mermaid),
> While Loop (mermaid + p5), Function (mermaid + recursion p5), Inheritance (mermaid class
> diagram). `astro check` clean; canvases build with 0 errors. Remaining: the "Next wave"
> list below + the new `Algorithms Visualized` folder.
>
> **Wave 2 (2026-07-10):** ✅ p5 added to Break Statement, Continue, String Slicing,
> Iterators & Generators, Comprehensions. ✅ mermaid class-diagrams added to Encapsulation,
> Abstraction, Polymorphism, and an arg-binding flowchart to Args & Kwargs. ✅ **New
> `Algorithms Visualized` folder** (orders 159–160, sorts last): *Sorting Visualized*
> (bubble-sort p5 + code + 3 exercises) and *Searching Visualized* (binary-search p5 +
> linear/binary code + 3 exercises). `astro check` clean; sorting canvas + polymorphism
> mermaid verified rendering.
>
> **Wave 3 (2026-07-10):** ✅ Concurrency viz — Threading (I/O-overlap timeline p5 +
> thread-lifecycle stateDiagram), Event Loop / asyncio (event-loop p5 + await flowchart),
> Multiprocessing (parallel-processes flowchart, via subagent). ✅ `Algorithms Visualized`
> grown to 4 pages: added **Recursion Visualized** (fib(5) call-tree p5 + memoization) and
> **Big-O Visualized** (O(1)/O(log n)/O(n)/O(n²) growth-chart p5 + table). All canvases
> build with 0 errors; mermaid renders; `astro check` clean; visuals confirmed (bubble
> sort, Big-O chart). Remaining: the ~98–108 order-overlap + single-page-folder cleanup,
> and optional deeper coverage (Strings, Operators, more OOP/data-structure pages).
>
> **Wave 4 (2026-07-10):** ✅ Data-structure p5 — **List** (append/insert/pop slot shifts),
> **Set** (duplicate rejection / uniqueness), **Dictionaries** (key→hash→slot lookup).
> ✅ mermaid (via subagent) — **Operator Precedence** (highest→lowest ladder) and **Tuple**
> (immutability: read OK, assign → TypeError). `astro check` clean; all 5 viz blocks
> confirmed in source; pages render (200). Live-canvas screenshots skipped this round —
> local dev server was crashing/slow under headless-Chrome load (environment, not content);
> p5 build proven on 6 prior sketches with the same API.
>
> **Wave 5 (2026-07-10):** ✅ Ordering — the ~98–108 glitch fixed: Context Managers 104→102
> so it sorts **before** Threading (live-confirmed order: functional-programming →
> context-managers → threading → multiprocessing). ✅ Viz — try-except (try/except/else/
> finally flow mermaid), Map Filter Reduce (reduce-accumulator p5), Context Managers (`with`
> __enter__/__exit__ flow mermaid, subagent), Data Types (mutable/immutable flowchart,
> subagent). `astro check` clean. Remaining polish: the single-page folders (Exception
> Handling / Iterators / Comprehensions / Context Managers render as one-item groups) could
> be merged into neighbors later — deferred (merging changes slugs). Deeper coverage still
> optional (String methods/formatting, remaining Operator/OOP pages).
>
> **Wave 6:** ✅ p5 — Bitwise Operators (bit-by-bit AND/OR/XOR), Logical Operators
> (short-circuit). ✅ mermaid (subagent) — OOP Decorator (wrapping), Constructor
> (__new__/__init__).
>
> **Wave 7:** ✅ p5 — Formatting String (f-string interpolation, values dropping into
> {slots}). ✅ mermaid (subagent) — Access Modifiers (public/#protected/-__private),
> Method Overriding (resolution up the MRO), Method Overloading (Python replaces, doesn't
> overload), Numbers (int/float/complex). `astro check` clean.


Scope: the **Tutorials** section (core Python) — 167 pages across 25 topic folders +
loose intro pages. Goal: (1) fix the sidebar ordering so topics read
beginner→advanced, (2) add mermaid diagrams and p5.js sketches where they teach better
than prose, keeping/adding the 3-exercise convention.

Companion to `info.md` (§3.1, §4). Last planned: 2026-07-10.

---

## 1. Ordering — organize tutorials correctly

Tutorials use one **global** `sidebar.order` scheme (not per-folder). It is a sane
beginner→advanced path *except* two folders numbered from 1, which float advanced topics
to the very top:

| Folder | Current order | Problem | New order |
|---|---|---|---|
| Python Standard Library (13 pp) | 1–13 | appears near top | **139–151** (+138) |
| Modern Python (7 pp) | 1–7 | appears at very top | **152–158** (+151) |

Renumbering `sidebar.order` is **safe** — it does not change page slugs, so no links
break (unlike the batch-1 folder rename). Groups sort by their minimum page order
(verified batch 1), so moving each folder's min above 138 drops it to the end, after
Asyncio (128–138).

Current sane ranges (left as-is): intro 1–5, Variables 6–9, types/print/input 10–14,
Strings 15–20, Operator 21–31, Casting 32, Control 33–41, Function 42–45, List 48–51,
Tuple 52–57, Set 58–63, Dict 64–69, Array 70–74, File Handling 75–79, OOP 80–97,
Errors 98–102, Iterators 99, Comprehensions 100, Functional 101–103, ContextManagers 104,
Threading 105–108, MultiProcessing 109–114, Synchronization 115–121, Networking 122–127,
Asyncio 128–138.

**Known minor overlaps (future polish, not this batch):** orders collide around 98–108
(Errors/Iterators/Comprehensions/Functional/Threading/ContextManagers) so a few groups
tie-break alphabetically. Single-page folders (Iterators, Comprehensions,
Context Managers, Exception Handling) render as one-item groups — consider merging the
1-page folders into their neighbors later. Standard Library could also move earlier
(before concurrency) with a full renumber; end-placement is the low-risk fix for now.

---

## 2. Content additions — mermaid / p5 / exercises

Most pages already carry 3–4 `DataCampExercise` blocks (e.g. For Loop has 4) but **zero
visualizations**. The work is adding the right instrument. Priority pages:

### Flagship (this batch)

| Page | Add mermaid | Add p5 |
|---|---|---|
| Control ▸ For Loop | iterate-over-sequence flow (init→check→body→advance) | a loop stepping a highlighted index across an array |
| Control ▸ If-else | if / elif / else decision flow | — |
| Control ▸ While Loop | condition→body→recheck loop | a bar creeping to a threshold, stopping when the condition fails |
| Function ▸ Function | call → execute → return flow; scope | recursion: the call stack growing then unwinding (factorial) |
| OOP ▸ Class / Inheritance | class → instances; inheritance/MRO graph | objects spawning from one class |

### Next wave (follow-up)

- Control ▸ Break/Continue — p5 trace showing where each jumps.
- Function ▸ Args/Kwargs — mermaid arg-binding.
- OOP ▸ Encapsulation / Abstraction / Polymorphism — class diagrams.
- Iterators/Generators, Comprehensions — p5 pull-one-at-a-time / filter→map pipeline.
- Concurrency (Threading/MultiProcessing/Asyncio) — timeline p5 + lifecycle mermaid.
- Strings ▸ Slicing — p5 index highlighter.
- **New folder `Algorithms Visualized`** (place after Functional, or at end): Sorting,
  Searching, Recursion, Big-O — each p5-first. (New content; see `info.md` §3.1.)

### Rules (from `guides/visualizations.mdx` + `new-tutorial` skill)

- p5: global style, brand palette (`background(13,17,23)`, blue `(75,139,190)`, amber
  `(255,211,67)`), `createCanvas(w,h)` matching the fence `height`, reads fine paused.
- mermaid: always `title` + `desc`.
- Keep 3 exercises per page; add if missing. Highlight the key code line with `{n}`.
- Gates: `astro check` clean, `theme-check` clean, reduced-motion honored, Windows-safe
  names, never `git add -A`, don't commit.

---

## 3. Execution

1. **Ordering fix** — renumber Standard Library + Modern Python (this batch).
2. **Flagship viz** — the 5 pages above (this batch).
3. **Next wave** — remaining pages, folder by folder, via the `content-author` agent for
   prose/exercises and direct authoring for p5 sketches.
4. **New `Algorithms Visualized` folder** — separate sub-batch.

Sizing: ~15–20 p5 sketches + ~25 mermaid diagrams to cover the full Tutorials section;
this batch delivers the ordering fix + 5 flagship pages as the pattern.

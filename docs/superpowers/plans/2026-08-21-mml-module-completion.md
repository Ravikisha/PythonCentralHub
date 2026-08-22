# Mathematics for Machine Learning — Module Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take `src/content/docs/Mathematics for Machine Learning` from 43 pages covering 5 of the book's 12 chapters to 118 pages covering all 12 plus a prerequisite bridge, every concept page built to Page Spec v2-math with in-canvas-controlled p5 sketches, React math labs, matplotlib figures, quizzes, five exercises, and flashcard-feeding recall cards.

**Architecture:** Vertical slices, one chapter per phase. Each phase authors its pages, its matplotlib figure module, and any React lab first needed by those pages, then runs the verification gate before the next phase starts. Interactive work rides on three existing tracks with no new dependencies: p5 fences through `public/scripts/p5-viz.js` (instance mode, in-canvas controls), React labs through `src/components/viz/VizPlayer.tsx` and the `Frame`/`Trace` contract in `src/components/viz/frames.ts`, and committed theme-pair SVGs through `scripts/figures/build.py`.

**Tech Stack:** Astro 5 + Starlight, MDX, `remark-math` + `rehype-katex`, mermaid (`lib/mermaid/render-diagram.ts`), p5.js 1.9.4 from CDN, React islands (`client:visible`), Python + matplotlib for figures, Node scripts for linting and deck generation.

**Spec:** `docs/superpowers/specs/2026-08-21-mml-module-completion-design.md`

## Global Constraints

Copied verbatim from the spec. Every task's requirements implicitly include this section.

- **Never commit.** The repo author commits. Do not run `git commit`, `git add`, `git push`, or `git checkout`. Never run `git add -A` — it would stage deletion of ~11 files with Windows-invalid names that Git cannot check out here.
- **No full `astro build`.** It takes ~2 h and exceeds the task limit. Verify with `node scripts/mdxcheck.mjs` and the linters instead. **A green `mdxcheck` does not mean `astro build` passes** — it does not parse GFM tables. Eyeball every table.
- **Filenames:** plain ASCII, spaces allowed, **never** `" : * ? < > | \ /`.
- **Folder naming:** `Chapter NN - Title`.
- **Starlight slugs:** lowercase, each space → `-`. `Chapter 07 - Continuous Optimization` → `chapter-07---continuous-optimization` (three hyphens). Links always end with a trailing slash.
- **Import depth from a chapter page is exactly four levels:** `../../../../components/…`. Count, never guess.
- **p5 palette:** background `(13, 17, 23)`, blue `(75, 139, 190)`, amber `(255, 211, 67)`, red `(232, 110, 110)`, green `(120, 200, 140)`, grid `(32, 44, 58)`.
- **p5 controls are drawn on the canvas.** Never `createSlider` or any other p5 DOM element.
- **React islands require `client:visible`.** Without it the island renders frame 0 and never hydrates.
- **`<Figure src>` takes no extension and no theme suffix.** Pass `/images/mml/<page-slug>/<name>`.
- **Math never renders inside JSX props.** Quiz options, AlgorithmCard fields, Figure captions: words, not KaTeX.
- **Braces in prose are escaped by `remarkEscapeBraces`.** Keep `{}` out of ordinary text; inside `$…$` they are safe because `remarkMath` runs first.
- **Every number a page claims comes from actually running the code that produced it.**
- **`sidebar.order` values follow the spec's blocks** and are unique within the module.
- **`:::tip[From the book]` is required on every concept page**, citing exact section, definition, theorem and equation numbers from `mml-book.pdf`.

---

## File Structure

### New directories

| path | responsibility |
| --- | --- |
| `src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/` | 7 prerequisite-bridge pages |
| `.../Chapter 01 - Introduction and Motivation/` | 3 pages |
| `.../Chapter 07 - Continuous Optimization/` | 10 pages |
| `.../Chapter 08 - When Models Meet Data/` | 9 pages |
| `.../Chapter 09 - Linear Regression/` | 8 pages |
| `.../Chapter 10 - Principal Component Analysis/` | 10 pages |
| `.../Chapter 11 - Gaussian Mixture Models/` | 7 pages |
| `.../Chapter 12 - Support Vector Machines/` | 8 pages |
| `src/components/viz/math/` | 19 React math labs |
| `src/components/viz/math/algos/` | pure trace generators for those labs |
| `scripts/figures/mml/` | one Python module per page needing plots |
| `src/data/mml/` | generated recall deck + query helpers |
| `public/images/mml/` | committed theme-pair SVGs (output of `npm run figures`) |

### New shared files

| path | responsibility |
| --- | --- |
| `scripts/gen-mml-recall.mjs` | walk the module, parse `## Recall card` bullets, write `src/data/mml/recall.yaml` |
| `src/data/mml/index.ts` | `buildDeck({ chapters })`, `recallChapters` |
| `src/components/MathDrillDeck.astro` | build-time filter wrapper around the existing `dsa/DrillDeck.tsx` island |
| `scripts/figures/mml/_data.py` | shared synthetic + real datasets for the module's figures |

### Modified files

| path | change |
| --- | --- |
| `package.json` | add `"mml:recall": "node scripts/gen-mml-recall.mjs"` |
| `.../Mathematics for Machine Learning.mdx` | full rewrite of the module index (currently omits Chapter 6) |
| all 42 existing chapter pages | full rewrite to Page Spec v2-math, `sidebar.order` renumbered |

### Files deliberately untouched

`src/content/docs/Machine Learning/**` — cross-linked, never edited (spec non-goal).

---

## Reference recipes

These are copied into the tasks that need them. They exist once here so the tasks can say "use the knob idiom" without repeating 30 lines.

### Recipe A — the p5 in-canvas knob

Every interactive sketch declares these two helpers locally (fences are self-contained by design; there is no shared p5 module and adding one would mean touching the remark plugin).

```js
// ---- in-canvas control: one draggable knob on a hairline track ----
// Register each knob in KNOBS during setup so mousePressed can hit-test them.
let KNOBS = [];
let dragging = null;

function knob(id, x, y, w, value, min, max, label, fmt) {
  KNOBS.push({ id, x, y, w, min, max });
  const t = (value - min) / (max - min);
  stroke(60, 74, 92); strokeWeight(2); line(x, y, x + w, y);          // track
  noStroke(); fill(255, 211, 67); ellipse(x + t * w, y, 12, 12);      // handle
  fill(190, 200, 212); textSize(12); textAlign(LEFT, CENTER);
  text(`${label} ${fmt ? fmt(value) : value.toFixed(2)}`, x + w + 12, y);
}

function knobHit(mx, my) {
  for (const k of KNOBS) {
    if (my > k.y - 12 && my < k.y + 12 && mx > k.x - 12 && mx < k.x + k.w + 12) return k;
  }
  return null;
}

function knobValue(k, mx) {
  const t = Math.min(1, Math.max(0, (mx - k.x) / k.w));
  return k.min + t * (k.max - k.min);
}

function mousePressed() { dragging = knobHit(mouseX, mouseY); }
function mouseReleased() { dragging = null; }
function mouseDragged() {
  if (!dragging) return;
  // assign into the sketch's own parameter variables by dragging.id
  if (dragging.id === "sigma") sigma = knobValue(dragging, mouseX);
  if (!isLooping()) redraw();   // a paused sketch must still respond
}
```

Rules that come with the idiom:

1. `KNOBS = []` at the top of `draw()` before any `knob()` call, so the registry does not grow every frame.
2. Every draggable thing gets a filled amber handle and a live numeric readout — a canvas offers no cursor affordance.
3. Drag handlers end with `if (!isLooping()) redraw();`.
4. `mouseDragged` never mutates anything but declared parameter variables.

### Recipe B — a matplotlib figure module

Confirmed against `scripts/figures/_style.py` and `scripts/figures/ml/phase-03-regression/gradient-descent-explained.py`.

```python
# scripts/figures/mml/<page-slug>.py
"""Figures for *<Page Title>*."""

import numpy as np

from _style import Palette, figure


def condition_number_error(fig, ax, p: Palette) -> None:
    """Relative solve error against κ(A) for random ill-conditioned systems."""
    rng = np.random.default_rng(0)
    ...
    ax.plot(kappa, err_solve, color=p.blue, label="np.linalg.solve")
    ax.plot(kappa, err_inv, color=p.red, label="inv(A) @ b")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"condition number $\kappa(A)$")
    ax.set_ylabel("relative error")
    ax.legend()


FIGURES = [figure("condition-number-error", condition_number_error, size=(7.2, 3.8))]
```

The real API, verbatim:

- `from _style import Palette, figure` — `_style` is importable because `build.py` puts `scripts/figures/` on `sys.path`.
- Draw signature is `(fig: plt.Figure, ax, p: Palette) -> None`. `ax` is `fig.add_subplot(111)` unless the figure is declared `axes=False`, in which case `ax` is `None` and the draw function builds its own layout.
- `figure(name, draw, size=(8.0, 4.6), axes=True)`; `FIGURES` is a flat list of those.
- `Palette` fields: `name bg fg muted grid blue amber green purple red`, plus `.cycle`. Use these, never literal hex.
- `render` writes `<out_dir>/<name>-dark.svg` and `-light.svg`; `build.py` sets `out_dir = public/images/<group>/<slug>/`. Group is the directory under `scripts/figures/`, slug is the module filename — so `scripts/figures/mml/norms.py` → `public/images/mml/norms/`.
- Grid, spine and tick styling come from the rc context. Do not restyle them.
- Axis labels take matplotlib **mathtext**, not KaTeX: `r"$\kappa(A)$"` works, `\lVert` does not — use `r"$\|x\|_p$"`.
- `build.py` skips files whose names start with `_`, so `_data.py` is a safe shared helper and a smoke module must **not** be `_`-prefixed.
- Builds serialise on `.figure-build.lock`; a concurrent run waits rather than racing.

Render with `python scripts/figures/build.py mml`.

### Recipe C — a React math lab

Confirmed against `src/components/viz/VizPlayer.tsx` and `src/components/viz/ComplexityChart.tsx`.

`VizPlayerProps<S>` is exactly:

```ts
{
  frames: Frame<S>[];                                        // required, non-empty
  renderStage: (frame: Frame<S>, index: number) => ReactNode; // pure
  title: string;                                             // required
  tag: VizTag;                                               // required, constrained union
  lib?: string;
  desc?: string;
  code?: string[];        // frame.line indexes into this, 1-based
  result?: string;
  ms?: number;            // default 900
  autoPlay?: boolean;     // default true; forced false under reduced motion
}
```

So a lab is:

```tsx
// src/components/viz/math/ElimStepper.tsx
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { elimination, type ElimInput, type ElimState } from "./algos/elimination";

export interface ElimStepperProps extends ElimInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

export default function ElimStepper({ matrix, rhs, reduced, ...rest }: ElimStepperProps) {
  const trace = useMemo(() => elimination({ matrix, rhs, reduced }), [matrix, rhs, reduced]);
  const renderStage = (f: Frame<ElimState>) => (/* pure SVG of f.state */);
  return <VizPlayer frames={trace.frames} renderStage={renderStage} tag="matrix"
                    code={trace.code} result={trace.result} {...rest} />;
}
```

The algos module is pure, returns `Trace<ElimState>` built with `tracer<ElimState>(CODE)` from `frames.ts`, never touches the DOM and never sets a timer. Every frame carries a `caption` — one present-tense sentence. `Watch` entries go in `frame.watch`.

`tag` is a **closed union** in `VizPlayer.tsx` today (`array tree graph grid list search stack heap interval sort trie dsu chart bits segtree state`). Task 1 extends it additively with six math tags — `matrix vector field dist opt fit` — and adds their colour and glyph rules in a new `src/styles/math-viz.css`, registered in `astro.config.mjs` after `dsa-viz.css`. Reusing `grid` for a matrix lab is rejected: the tag string is rendered in the pill, so a mislabelled tag is visible to the reader.

Tag assignment: `matrix` (MatrixLab, ElimStepper, EigenLab, SVDLab), `vector` (SpanExplorer, NormBall, ProjectionLab), `field` (SurfaceGrad, TaylorLab, AutodiffGraph), `dist` (DistributionLab, BayesLab), `opt` (DescentLab, ConstraintLab, ConvexLab), `fit` (RegressionLab, PCALab, EMLab, MarginLab).

### Recipe D — the Page Spec v2-math skeleton

```mdx
---
title: <Human Title>
description: <one sentence, SEO-worthy>
sidebar:
  order: <int from the spec's block table>
---

import DataCampExercise from "../../../../components/DataCampExercise.astro";
import Quiz from "../../../../components/Quiz.astro";
import Figure from "../../../../components/Figure.astro";

<one-paragraph hook: what this page buys the reader>

## What you'll learn
## Intuition
## The math
## Worked example by hand
## See it move
## From scratch
## On real data
## Reading the plot
:::tip[From the book]
## Pitfalls
## Compare
<Quiz questions={[…4 MCQ…]} />
## 🧪 Try It Yourself
### Exercise 1 – … (×5, easy → hard)
## Recall card
## Next
```

`## With scikit-learn` is added for Chapters 9–12 only. `<AlgorithmCard>` is added for Chapters 9–12 only.

### Recipe E — Recall card shapes

The heading is `## Recall card`, matching the DSA convention exactly, so `gen-mml-recall.mjs` stays a near-copy of `gen-recall-deck.mjs` and the two decks cannot diverge in parsing behaviour. (The spec's prose says `## Recall`; `## Recall card` is the binding form — it is what the generator matches with `/^## Recall card\s*$/m`.)

```md
## Recall card

- **Cue** — the content the cue should retrieve.
- **The error is always orthogonal to the subspace**: which is why the projection is the least-error point of U.
```

Classification is not a choice the author makes; the generator decides from the bold run:

- **aspect** — bold is ≤ 28 characters, ≤ 4 words, and does not end in `. : ; ,`. Front = the bold, back = the rest.
- **cloze** — anything longer. Front = `____ — <rest>`, back = the bold claim.
- **fact** — bold with no trailing text. Front = `<page title> — recall the point`.

Authoring consequences, each learned from the generator's source:

1. Write 4–7 bullets, mixing both shapes. A page whose bullets are all short aspects produces a deck of trivia; all cloze produces a deck of paragraphs.
2. Bold must be followed by `—`, `–`, `:` or `-`. The regex is `/^\*\*(.+?)\*\*\s*[—–:-]?\s*(.*)$/` — a bullet whose bold is not at the very start contributes nothing and is silently dropped.
3. Inline KaTeX is stripped to its source text (`$\kappa(A)$` → `\kappa(A)`), so a bullet that leans on a rendered formula reads badly on a card. Put the words in the bullet and the formula on the page.
4. Backslash-heavy LaTeX inside a Recall bullet is the known way to corrupt the generated YAML. Keep `\alpha`-style commands out of Recall bullets entirely.
5. Continuation lines must be indented to fold into the preceding bullet.
6. A blank line inside the section closes the current bullet.

### Recipe F — the per-phase verification gate

Run all of these at the end of every phase. Every one must be clean before the next phase starts.

```bash
node scripts/mdxcheck.mjs "src/content/docs/Mathematics for Machine Learning"
node scripts/lint-p5.mjs
node scripts/lint-mermaid.mjs
python scripts/figures/build.py mml
node scripts/gen-mml-recall.mjs
```

Then the check that actually catches what those miss — **added after Task 2, where all seven pages
returned HTTP 500 on a green `mdxcheck`**:

```bash
npx astro dev --port 44xx &            # a spare port, backgrounded
curl -s -o /dev/null -w "%{http_code}
"   "http://localhost:44xx/mathematics-for-machine-learning/<chapter-slug>/<page-slug>/"
```

Fetch every page the phase touched and require **200** on all of them, then stop the server. Anything
under 30 kB of HTML is a rendered error page, not a page. Two failure classes only this catches:

1. **Invalid frontmatter YAML.** An unquoted `: ` in a `description` throws
   `YAMLException: incomplete explicit mapping pair`, and because Astro fails the whole content
   collection, *every page in the module* 500s and the dev server exits. `mdxcheck` does not parse
   frontmatter, so it reports 0 failures. Audit with:

   ```bash
   python -c "
   import io,re,glob
   for f in glob.glob('src/content/docs/Mathematics for Machine Learning/**/*.mdx',recursive=True):
       m=re.match(r'---?
(.*?)?
---', io.open(f,encoding='utf-8',newline='').read(), re.S)
       for line in (m.group(1).split('
') if m else []):
           km=re.match(r'^(\w[\w-]*):\s(.*)$', line.rstrip(''))
           if km and km.group(2)[:1] not in '\"'' and ': ' in km.group(2): print(f, km.group(1))
   "
   ```

2. **Control characters from a botched edit.** Writing LaTeX through a shell heredoc collapses
   `	imes` into a tab and `arepsilon` into a vertical tab. Scan for any byte under 32 that is not
   `` or `
` across the module's `.mdx` files after any scripted edit.

Then, by hand:

- Every GFM table in the phase's pages read once, top to bottom, for a missing `|` or a stray `-`.
- Every `<Figure src>` in the phase's pages resolves to a committed pair under `public/images/mml/`.
- `sidebar.order` unique within the module: `grep -rh "order:" "src/content/docs/Mathematics for Machine Learning" | sort | uniq -d` prints nothing.
- Import `../` depth counted, not guessed, on every new file.
- Every claimed numeric output traced to a code block that was actually run.

---

## Task 1: Infrastructure — figure group, recall deck, first four labs, module index

**Files:**
- Read first: `scripts/figures/_style.py`, `scripts/figures/build.py`, one module under `scripts/figures/ml/`, `scripts/gen-recall-deck.mjs`, `src/data/dsa/index.ts`, `src/components/dsa/DrillDeck.astro`, `src/components/dsa/DrillDeck.tsx`, `src/components/viz/VizPlayer.tsx`, `src/components/viz/frames.ts`, `src/components/viz/algos/complexity.ts`, `src/components/viz/ComplexityChart.tsx`
- Create: `scripts/figures/mml/_data.py`
- Create: `scripts/gen-mml-recall.mjs`
- Create: `src/data/mml/index.ts`
- Create: `src/components/MathDrillDeck.astro`
- Create: `src/components/viz/math/algos/matrix.ts`, `.../algos/elimination.ts`, `.../algos/distributions.ts`, `.../algos/descent.ts`
- Create: `src/components/viz/math/MatrixLab.tsx`, `ElimStepper.tsx`, `DistributionLab.tsx`, `DescentLab.tsx`
- Create: `src/components/viz/math/README.md`
- Create: `src/styles/math-viz.css` — colour + glyph rules for the six new tag pills
- Modify: `src/components/viz/VizPlayer.tsx` — extend the `VizTag` union additively with `matrix vector field dist opt fit`. No other change; the transport is untouched.
- Modify: `src/components/dsa/DrillDeck.tsx` — two additive optional props, `groupNoun?: string` (default `"phase"`) and `formatGroup?: (s: string) => string` (default the existing `phaseLabel`), so the filter control reads "Every chapter" on the math deck. Defaults preserve DSA behaviour exactly.
- Modify: `astro.config.mjs` — register `"./src/styles/math-viz.css"` in `customCss` immediately after `"./src/styles/dsa-viz.css"` (it extends the same `.pch-vz__tag` chassis, so order matters)
- Modify: `package.json` — add `"mml:recall"`

**Decision recorded during Step 1:** `useDrill` is left alone. Its store key `pch:dsa:drill:v1` is a module constant and the hook takes no arguments, but math and DSA card keys are derived from disjoint page slugs, so one shared review history across the site is correct rather than a collision.
- Modify: `src/content/docs/Mathematics for Machine Learning/Mathematics for Machine Learning.mdx` — full rewrite

**Interfaces:**
- Consumes: `frames.ts` — `Frame<S>`, `Trace<S>`, `tracer<S>(code?)`, `Tone`, `Pointer`, `Band`, `Watch`. `VizPlayer` default export and its props (`title`, `desc`, `lib`, `showCode`, `ms`, `autoPlay`, frames, stage renderer) — read the file for the exact contract before writing a lab.
- Produces:
  - `scripts/figures/mml/_data.py` → `gaussian_blobs(n, k, seed)`, `polynomial_data(n, degree, noise, seed)`, `two_moons(n, noise, seed)`, `digit_matrix()` returning `np.ndarray`; `linnerud_like(seed)` for regression pages. Every later figure module imports from here.
  - `scripts/gen-mml-recall.mjs` → writes `src/data/mml/recall.yaml` with records `{ key, kind, label, text, cardId, cardTitle, chapter, url }`.
  - `src/data/mml/index.ts` → `buildDeck(opts: { chapters?: string[] }): DeckItem[]` and `recallChapters: string[]`, where `DeckItem = { key, kind, label, text, cardId, cardTitle, phase, url }` — note `phase`, not `chapter`, because the reused island reads `phase`.
  - `src/components/MathDrillDeck.astro` → props `{ chapters?: string[] }`.
  - `src/components/viz/math/MatrixLab.tsx` → props `{ algo?: string; matrix?: number[][]; title: string; desc?: string; lib?: string; ms?: number; autoPlay?: boolean }`.
  - `src/components/viz/math/ElimStepper.tsx` → props `{ matrix: number[][]; rhs?: number[]; reduced?: boolean; title: string; desc?: string; lib?: string; ms?: number; autoPlay?: boolean }`.
  - `src/components/viz/math/DistributionLab.tsx` → props `{ dist: "gaussian" | "gaussian-2d" | "bernoulli" | "binomial" | "beta" | "gamma"; params?: Record<string, number>; showCdf?: boolean; conditioning?: boolean; title: string; desc?: string; lib?: string }`.
  - `src/components/viz/math/DescentLab.tsx` → props `{ surface: "quadratic" | "rosenbrock" | "ill-conditioned" | "saddle"; method: "gd" | "momentum" | "sgd" | "newton"; lr?: number; beta?: number; steps?: number; start?: [number, number]; title: string; desc?: string; lib?: string }`.

- [ ] **Step 1: Read the eleven reference files listed above**

No edits. Produce, in the working notes, the exact signatures of: `_style.py`'s render/axis helpers, `build.py`'s `FIGURES` record shape, `gen-recall-deck.mjs`'s two card regexes, `src/data/dsa/index.ts`'s `buildDeck` shape, `DrillDeck.tsx`'s props, `VizPlayer`'s props and stage-renderer signature. Recipes B and C above are illustrative; the real signatures replace them.

- [ ] **Step 2: Write `scripts/figures/mml/_data.py`**

Five dataset helpers, each seeded and deterministic. No plotting. Docstring on each saying which pages use it.

- [ ] **Step 3: Write one throwaway figure module and render it**

Create `scripts/figures/mml/_smoke.py` exporting one `FIGURES` entry that plots `y = x²`. Run:

```bash
python scripts/figures/build.py mml
```

Expected: two SVGs at `public/images/mml/_smoke/`. This proves the group is discovered (`build.py` walks `scripts/figures/<group>/` and skips `_`-prefixed files — confirm which, since `_smoke.py` may be skipped for that reason; if skipped, name it `smoke-check.py` instead). Delete the module and its output once green.

- [ ] **Step 4: Write `scripts/gen-mml-recall.mjs`**

Port `gen-recall-deck.mjs` with `ROOT = "src/content/docs/Mathematics for Machine Learning"`, `OUT = "src/data/mml/recall.yaml"`, section heading `## Recall card` (unchanged from the DSA generator), and `chapter` derived from the containing folder name. Keep both card shapes.

- [ ] **Step 5: Run it against the module as it stands**

```bash
node scripts/gen-mml-recall.mjs
```

Expected: it finds zero cards, because existing pages use `## Recap`, not `## Recall card`, and writes an empty deck without crashing. That empty-but-valid output is the pass condition for this step; the deck fills up as chapters are rewritten.

- [ ] **Step 6: Write `src/data/mml/index.ts` and `src/components/MathDrillDeck.astro`**

Mirror `src/data/dsa/index.ts` and `src/components/dsa/DrillDeck.astro`. Map the deck's `chapter` onto the island's `phase` prop. Render the existing `dsa/DrillDeck.tsx` island unchanged with `client:visible`.

- [ ] **Step 7: Add the npm script**

In `package.json`, after `"viz:mermaid"`, add:

```json
"mml:recall": "node scripts/gen-mml-recall.mjs",
```

- [ ] **Step 8: Write `src/components/viz/math/README.md`**

Document the contract for the other 15 labs: algos module returns `Trace<S>`, component is a thin stage renderer, `client:visible` required, prop conventions, which chapter each lab serves. Copy the structure of `src/components/viz/README.md`.

- [ ] **Step 9: Write the four algos modules**

`matrix.ts`, `elimination.ts`, `distributions.ts`, `descent.ts`. Each exports an `*_ALGOS` registry, its `*Input` and `*State` types, and pure generators using `tracer`. Every frame gets a `caption` — one present-tense sentence, which is what turns the animation into a lesson.

- [ ] **Step 10: Write the four lab components**

`MatrixLab`, `ElimStepper`, `DistributionLab`, `DescentLab`. SVG stage renderers, pure functions of one frame. No timers, no DOM writes.

- [ ] **Step 11: Rewrite the module index**

`Mathematics for Machine Learning.mdx`, `sidebar.order: 500`. Full 12-chapter map (mermaid), the four-pillars diagram kept, a "start here" path for readers with no calculus pointing at Chapter 0, one table per chapter with a one-line big idea per page, and the notation page and Recall Drill linked. Every chapter listed — the current version omits Chapter 6, which is the bug that started this.

- [ ] **Step 12: Verification gate (Recipe F)**

`python scripts/figures/build.py mml` may report "no modules" once `_smoke` is deleted; that is expected until Task 2.

- [ ] **Step 13: Report to the author**

State: files created, what the smoke figure proved about `build.py`'s discovery rules, whether `DrillDeck.tsx` was reusable unchanged or needed a prop shim, and the four labs' final prop signatures. Do not commit.

---

## Task 2: Chapter 0 — Getting Ready (7 pages, orders 501–507)

**Files:**
- Create: `.../Chapter 00 - Getting Ready/Getting Ready Overview.mdx` (501)
- Create: `.../Chapter 00 - Getting Ready/Notation and Symbols.mdx` (502)
- Create: `.../Chapter 00 - Getting Ready/Sums Products and Set Notation.mdx` (503)
- Create: `.../Chapter 00 - Getting Ready/Functions Limits and Continuity.mdx` (504)
- Create: `.../Chapter 00 - Getting Ready/Single-Variable Calculus Refresher.mdx` (505)
- Create: `.../Chapter 00 - Getting Ready/Complex Numbers in One Page.mdx` (506)
- Create: `.../Chapter 00 - Getting Ready/NumPy for Mathematics.mdx` (507)
- Create: `scripts/figures/mml/functions-limits-and-continuity.py`, `single-variable-calculus-refresher.py`, `numpy-for-mathematics.py`

**Interfaces:**
- Consumes: Recipes A, B, D, E, F. `Quiz`, `DataCampExercise`, `Figure` components.
- Produces: the notation page at slug `/mathematics-for-machine-learning/chapter-00---getting-ready/notation-and-symbols/`, linked from every later chapter overview.

- [ ] **Step 1: Read `mml-book.pdf` pages 7–10 for the notation table**

Read with the `pages` parameter, max 20 pages per call. Transcribe the notation table faithfully — this page's whole value is that it matches the book.

- [ ] **Step 2: Write the Notation and Symbols page (502)**

Variant: pure reference. KaTeX rows grouped — scalars/vectors/matrices, sets and set operations, probability, calculus, ML-specific. One "where you meet it" column naming the chapter. No p5, no exercises, one `Quiz` of 4 questions on reading notation.

- [ ] **Step 3: Write the overview page (501)**

Overview variant: chapter map, a 10-question self-test (`Quiz`) that tells the reader which of 503–507 they can skip, time estimate, page table.

- [ ] **Step 4: Write pages 503–507 to Recipe D**

Each: 5–7 learning bullets, an analogy, a mermaid map, KaTeX with every symbol defined, a hand-worked numeric table verified against NumPy, 2–3 p5 sketches with knob controls per Recipe A, a from-scratch NumPy block with printed output, a `<Figure>` where a plot earns its place, a `From the book` tip citing the front matter and the sections that assume this material, 3–5 pitfalls, a compare table, a 4-question `Quiz`, 5 `DataCampExercise` blocks easy → hard, `## Recall card` bullets in both shapes, and a `## Next` link.

Concrete per-page content anchors, so no page drifts into generic filler:

- **503 Sums, Products, and Set Notation** — Σ/Π index manipulation, swapping the order of a double sum, telescoping, set-builder, ∈ ⊆ ∪ ∩ ×, the indicator function, and why `np.sum(A, axis=0)` is the Σ the book writes. p5: an index-walker that highlights which terms a given Σ collects.
- **504 Functions, Limits, and Continuity** — domain/codomain/image, injective/surjective/bijective (the book leans on these in §2.7), limits from both sides, continuity, differentiability implies continuity but not the reverse (ReLU at 0). p5: a secant line whose two points you drag together into a tangent. Figure: three functions, one continuous-not-differentiable, one discontinuous, one smooth.
- **505 Single-Variable Calculus Refresher** — power/product/quotient/chain rules derived not just stated, higher derivatives, integration as antiderivative and as area, the fundamental theorem, and why every one of these reappears in Chapter 5. p5: a Riemann-sum knob for the number of rectangles. Figure: convergence of the Riemann sum to the integral as n grows.
- **506 Complex Numbers in One Page** — a + bi, the complex plane, modulus and argument, Euler's formula, conjugates, and the one reason the module needs them: a real matrix can have complex eigenvalues (a rotation matrix does). p5: a draggable point on the complex plane showing modulus/argument and the effect of multiplying by another complex number.
- **507 NumPy for Mathematics** — arrays as vectors and matrices, `@` vs `*`, broadcasting rules, `axis`, `np.linalg` (`solve`, `inv`, `det`, `eig`, `svd`, `norm`, `matrix_rank`, `cond`), `float64` vs `float32`, why `np.allclose` and not `==`, and the catastrophic-cancellation demo. Figure: relative error of `inv(A) @ b` vs `solve(A, b)` as κ(A) grows.

- [ ] **Step 5: Write the three figure modules and render**

```bash
python scripts/figures/build.py mml
```

Expected: SVG pairs under `public/images/mml/functions-limits-and-continuity/`, `.../single-variable-calculus-refresher/`, `.../numpy-for-mathematics/`. Any page claiming a number from these plots gets it from the actual render.

- [ ] **Step 6: Verification gate (Recipe F)**

- [ ] **Step 7: Report to the author**

Pages written, figures rendered, `mml:recall` card count, anything the gate flagged. Do not commit.

---

## Task 3: Chapter 1 — Introduction and Motivation (3 pages, orders 510–512)

**Files:**
- Create: `.../Chapter 01 - Introduction and Motivation/Introduction and Motivation Overview.mdx` (510)
- Create: `.../Chapter 01 - Introduction and Motivation/Finding Words for Intuitions.mdx` (511)
- Create: `.../Chapter 01 - Introduction and Motivation/Two Ways to Read This Book.mdx` (512)

**Interfaces:**
- Consumes: Recipes A, D, E, F.
- Produces: the module's canonical concept map, reused by later chapter overviews.

- [ ] **Step 1: Read `mml-book.pdf` pages 11–18**

Chapter 1 in full, plus the foreword's audience framing already read.

- [ ] **Step 2: Write 511 Finding Words for Intuitions**

§1.1. The vocabulary problem the book opens with: **data** as vectors, **model** in its two senses (a function, or a probability distribution), **learning** in its two senses (parameter estimation, and non-parametric memorisation), and the three things "algorithm" means — predictor, training procedure, and the numerical method inside. Table of every overloaded term with the two or three meanings and which chapter uses which. p5: a single dataset re-labelled as the reader drags through the three framings.

- [ ] **Step 3: Write 512 Two Ways to Read This Book**

§1.2–1.3. Bottom-up (foundations then models) vs top-down (model first, foundations on demand), the four pillars, the dependency graph of the book's own chapters as a mermaid DAG, where this module's Chapter 0 sits outside the book, and how to use the exercise pages. Include the "which reading order fits you" `Quiz`.

- [ ] **Step 4: Write 510 the overview**

Overview variant. Links to 511, 512, and forward to Chapter 2.

- [ ] **Step 5: Verification gate (Recipe F)**

- [ ] **Step 6: Report to the author**

---

## Tasks 4–14: one chapter per task

Every one of these tasks has the identical step shape. It is written out once here in full; each task below then carries only its own page list, content anchors, figures, and new labs. This is not a "similar to Task N" placeholder — the step list *is* the following seven steps, verbatim, and each task's specific content is fully enumerated in its own section.

- [ ] **Step 1: Read the chapter in `mml-book.pdf`**

Use the `pages` parameter, at most 20 pages per call. Read the whole chapter including its exercises before writing any page. Note every numbered definition, theorem, example and equation — the `From the book` tips cite them exactly, and that citation is the module's signature.

- [ ] **Step 2: Write or rewrite each concept page to Recipe D**

For a rewrite, open the existing page first and carry forward its analogy, its `From the book` tip and its worked examples. The strongest material in the module is already there — the pencil-shadow analogy for projections, the production-plan framing for linear systems. A rewrite that loses those is a regression. Rename `## Recap` to `## Recall card` and reshape its bullets into the two card shapes of Recipe E. Renumber `sidebar.order` to the spec's block.

- [ ] **Step 3: Write the chapter's figure modules and render**

```bash
python scripts/figures/build.py mml
```

- [ ] **Step 4: Write any new React lab this chapter is the first to need**

Algos module + component per Recipe C. Design its props against the page that consumes it, not speculatively.

- [ ] **Step 5: Write the Exercises and Solutions page**

Exercises variant. For Chapters 2–7 the problems are the book's own, at the page given in the task, restated in this module's notation rather than copied verbatim, with independently worked solutions behind `<details>` and a NumPy verification block whose printed output is real. For Chapters 8–12 the problems are authored in the book's style, because the book ships none.

- [ ] **Step 6: Write the Formula Sheet page**

Formula-sheet variant: KaTeX tables grouped by topic, a "when you use it" line per entry, a back-link to the page that derives it. No prose, no p5, no exercises.

- [ ] **Step 7: Verification gate (Recipe F), then report**

Report pages written, figures rendered, labs added, recall-card count for the chapter, and anything the gate flagged. Do not commit.

---

### Task 4: Chapter 2 — Linear Algebra (11 pages, 520–530)

**Book:** pp. 17–69. Exercises p. 64.

**Files:** rewrite all 9 existing pages in `Chapter 02 - Linear Algebra/`; create `Chapter 2 Exercises and Solutions.mdx` (529) and `Chapter 2 Formula Sheet.mdx` (530). Create `scripts/figures/mml/` modules for `systems-of-linear-equations`, `matrices`, `solving-systems-of-linear-equations`, `basis-and-rank`, `linear-mappings`.

**New lab:** `SpanExplorer` — `src/components/viz/math/algos/span.ts` + `SpanExplorer.tsx`. Props `{ vectors: number[][]; dim?: 2 | 3; title: string; desc?: string; lib?: string }`. Frames walk the span construction: add vector, test dependence against the current span, extend or reject, report the basis and rank.

**Content anchors per page:**

- **520 Overview** — chapter map, why linear algebra is the first pillar, page table, links to 529/530 and the notation page.
- **521 Systems of Linear Equations (§2.1)** — the book's chemical/production example, geometry of solutions in 2-D (one point, a line, empty), particular vs general solution. `ElimStepper` for a 3×4 system. p5: two draggable lines whose intersection is the solution, going parallel as the system becomes inconsistent.
- **522 Matrices (§2.2)** — matrix as data grid *and* as map, multiplication as composition (and why it is not element-wise), identity, inverse, transpose, the four Kronecker/scalar properties, `A` invertible ⟺ `Ax = b` uniquely solvable. `MatrixLab` for a 2×2 acting on the unit square. Figure: multiplication cost vs n for the naive triple loop against `@`.
- **523 Solving Systems of Linear Equations (§2.3)** — particular solution, elementary row operations, row echelon and reduced row echelon form, pivots, the minus-1 trick, Moore-Penrose pseudo-inverse, and the honest note that Gaussian elimination is not what a library uses at scale. `ElimStepper` in `reduced` mode. Figure: solve accuracy vs κ(A).
- **524 Vector Spaces (§2.4)** — groups, vector space axioms, subspaces, and why every axiom is load-bearing (a counterexample per axiom). p5: closure under addition demonstrated by dragging two vectors inside and outside a candidate subspace.
- **525 Linear Independence (§2.5)** — definition, the elimination test, why independence is a property of a set and not of a vector. `SpanExplorer` with three near-dependent vectors.
- **526 Basis and Rank (§2.6)** — generating set, basis, dimension, rank, rank-nullity, full rank vs rank deficient, and rank as "how much information the matrix really carries". Figure: singular-value spectrum of a rank-deficient matrix with numerical noise, showing why `matrix_rank` needs a tolerance.
- **527 Linear Mappings (§2.7)** — homomorphism, injective/surjective/bijective (calling back to page 504), transformation matrix, basis change, image and kernel. `MatrixLab` with a basis-change overlay.
- **528 Affine Spaces (§2.8)** — affine subspace, affine mapping, why a neural network layer is affine and not linear, and why the bias term is exactly the support point. p5: a line through the origin dragged off it, with the span/affine distinction labelled live.
- **529 Exercises** — book Exercises 2.1–2.20, p. 64.
- **530 Formula Sheet.**

### Task 5: Chapter 3 — Analytic Geometry (12 pages, 540–551)

**Book:** pp. 70–97. Exercises p. 96.

**Files:** rewrite all 10 existing pages in `Chapter 03 - Analytic Geometry/`; create Exercises (550) and Formula Sheet (551). Figure modules for `norms`, `inner-products`, `angles-and-orthogonality`, `orthogonal-projections`, `rotations`.

**New labs:** `NormBall` (`algos/norms.ts`, props `{ ps?: number[]; dim?: 2; title; desc?; lib? }`) and `ProjectionLab` (`algos/projection.ts`, props `{ mode: "line" | "plane" | "gram-schmidt"; vectors?: number[][]; target?: number[]; title; desc?; lib? }`).

**Content anchors:** norms as rulers with the p-slider (`NormBall`, plus a p5 unit-ball morph); inner products as generalised dot products with the bilinear/symmetric/positive-definite checklist and a non-standard inner product worked by hand; lengths and distances derived from the inner product; angles, Cauchy-Schwarz, and cosine similarity on real text vectors (Figure); orthonormal bases and Gram-Schmidt step-by-step (`ProjectionLab` in `gram-schmidt` mode); orthogonal complement and the normal vector of a plane; inner product of functions with the Fourier connection (Figure: the first four Legendre polynomials and their pairwise inner products, showing orthogonality numerically); orthogonal projections — keep the existing pencil-shadow analogy verbatim, add `ProjectionLab` in `plane` mode and a Figure of reconstruction error vs subspace dimension on a real dataset; rotations, the rotation matrix, `Rᵀ = R⁻¹`, complex eigenvalues (calling back to page 506), and rotations in ℝⁿ via Givens.

### Task 6: Chapter 4 — Matrix Decompositions (10 pages, 560–569)

**Book:** pp. 98–138. Exercises p. 137.

**Files:** rewrite all 8 existing pages; create Exercises (568) and Formula Sheet (569). Figure modules for `determinant-and-trace`, `eigenvalues-and-eigenvectors`, `singular-value-decomposition`, `matrix-approximation`, `cholesky-decomposition`.

**New labs:** `EigenLab` (`algos/eigen.ts`, props `{ matrix: number[][]; method?: "power" | "characteristic"; iterations?: number; title; desc?; lib? }`) and `SVDLab` (`algos/svd.ts`, props `{ matrix?: number[][]; image?: "digit" | "checker"; maxRank?: number; title; desc?; lib? }`).

**Content anchors:** determinant as signed volume with the `MatrixLab` area overlay and the Laplace expansion worked by hand; trace, invariance under similarity, characteristic polynomial; eigenvalues/eigenvectors with `EigenLab` power iteration, geometric vs algebraic multiplicity, defective matrices, and the spectral theorem for symmetric matrices; Cholesky as the covariance square root, with the sampling application (draw correlated Gaussians from `L @ z`) and a Figure of the resulting scatter; eigendecomposition `A = PDP⁻¹`, diagonalisability, and matrix powers made cheap; SVD `A = UΣVᵗ` for any matrix, the rotation-scale-rotation reading, and the relation to eigendecomposition of `AᵗA`; matrix approximation with `SVDLab`'s rank slider on a real digit image, Eckart–Young, and a Figure of Frobenius error vs rank; matrix phylogeny as the taxonomy mermaid, kept and extended.

### Task 7: Chapter 5 — Vector Calculus (11 pages, 580–590)

**Book:** pp. 139–171. Exercises p. 170.

**Files:** rewrite all 9 existing pages; create Exercises (589) and Formula Sheet (590). Figure modules for `differentiation-of-univariate-functions`, `partial-differentiation-and-gradients`, `higher-order-derivatives`, `linearization-and-multivariate-taylor-series`, `backpropagation-and-automatic-differentiation`.

**New labs:** `SurfaceGrad` (`algos/surface.ts`, props `{ fn: "bowl" | "saddle" | "rosenbrock" | "ravine"; showField?: boolean; showDirectional?: boolean; title; desc?; lib? }`), `TaylorLab` (`algos/taylor.ts`, props `{ fn: "sin" | "exp" | "log1p" | "sigmoid"; maxOrder?: number; center?: number; title; desc?; lib? }`), `AutodiffGraph` (`algos/autodiff.ts`, props `{ expression: string; inputs: Record<string, number>; title; desc?; lib? }` — frames walk the forward pass node by node, then the reverse pass accumulating adjoints).

**Content anchors:** difference quotient to derivative with a p5 secant-to-tangent knob; the rules derived; Taylor series with `TaylorLab`; partial derivatives, the gradient as a row vector (the book's convention — state it and stick to it), the chain rule for multivariate functions, gradient as steepest ascent with `SurfaceGrad`; Jacobians of vector-valued functions and the Jacobian determinant as a volume factor (a Figure of area distortion under a nonlinear map); gradients of matrices and the shape bookkeeping that trips everyone, with a table of every gradient shape; the identity cheat sheet plus numerical gradient checking as runnable code; backprop and reverse-mode autodiff with `AutodiffGraph` and a from-scratch 30-line reverse-mode engine whose gradients match `numpy` finite differences; Hessians, curvature, minima/maxima/saddles with `SurfaceGrad` on the saddle; multivariate Taylor with a Figure of first- vs second-order approximation error.

### Task 8: Chapter 6 — Probability and Distributions (10 pages, 600–609)

**Book:** pp. 172–224. Exercises p. 222.

**Files:** rewrite the 6 existing pages; **create** `Conjugacy and the Exponential Family.mdx` (606) and `Change of Variables and Inverse Transform.mdx` (607); create Exercises (608) and Formula Sheet (609). Figure modules for `discrete-and-continuous-probabilities`, `gaussian-distribution`, `summary-statistics-and-independence`, `conjugacy-and-the-exponential-family`, `change-of-variables-and-inverse-transform`.

**New lab:** `BayesLab` (`algos/bayes.ts`, props `{ model: "beta-bernoulli" | "gaussian-known-variance" | "gamma-poisson"; observations: number[]; prior?: Record<string, number>; title; desc?; lib? }` — one frame per observation, prior → posterior sequentially).

**Content anchors:** sample space, event space, probability measure, random variable as a *function*, and the three-way name collision the book warns about; pmf/pdf/cdf with `DistributionLab`, and the trap that a pdf value is not a probability; sum rule, product rule, Bayes with `BayesLab` and the medical-test worked example whose numbers are computed, not asserted; mean, variance, covariance, correlation, empirical vs population, independence vs conditional independence vs zero correlation (with the standard counterexample and a Figure of four datasets sharing a correlation coefficient); the Gaussian — marginals, conditionals, product of Gaussians, sums, affine transforms, all with `DistributionLab` in `gaussian-2d` conditioning mode and a Figure of the conditional slice; **§6.6** conjugacy, the exponential-family form, natural parameters, sufficient statistics, and the table of conjugate pairs, with `BayesLab` showing why the posterior stays in the family; **§6.7** change of variables, the Jacobian factor in a density, inverse-transform sampling implemented from scratch and validated against `np.random` with a histogram Figure.

### Task 9: Chapter 7 — Continuous Optimization (10 pages, 620–629, all new)

**Book:** pp. 225–248. Exercises p. 247.

**Files:** create the folder and all 10 pages per the spec's table. Figure modules for `optimization-using-gradient-descent`, `momentum-and-stochastic-gradient-descent`, `constrained-optimization-and-lagrange-multipliers`, `convex-sets-and-convex-functions`, `linear-programming`, `quadratic-programming`.

**New labs:** `ConstraintLab` (`algos/constraint.ts`, props `{ objective: "quadratic" | "linear"; constraint: "circle" | "line" | "box"; title; desc?; lib? }`) and `ConvexLab` (`algos/convex.ts`, props `{ fn: string; showChord?: boolean; showEpigraph?: boolean; showJensen?: boolean; title; desc?; lib? }`).

**Content anchors:** the optimization framing of learning; gradient descent with `DescentLab`, the step-size dilemma, a Figure of loss curves at five learning rates showing crawl / converge / oscillate / diverge, and κ(A) as the reason a ravine is slow; momentum as a low-pass filter on the gradient and SGD's variance/cost trade-off, with a Figure of full-batch vs minibatch trajectories; constrained optimization — indicator-function framing, the Lagrangian, the dual, weak and strong duality, complementary slackness — with `ConstraintLab` showing the tangency condition and λ read off as the ratio of gradient magnitudes; convex sets and functions, Jensen, the first- and second-order conditions, and why convexity is the property that makes the algorithms above trustworthy, with `ConvexLab`; LP standard form, the dual LP, and the feasible polytope Figure; QP, the KKT conditions written out, and the forward reference to the SVM dual in Chapter 12; the Legendre–Fenchel transform as the supporting-hyperplane description of a convex function, with the conjugate of a quadratic worked by hand.

### Task 10: Chapter 8 — When Models Meet Data (9 pages, 640–648, all new)

**Book:** pp. 251–288. No exercise set — Exercises page (647) carries authored problems.

**Files:** create the folder and all 9 pages. Figure modules for `empirical-risk-minimization`, `parameter-estimation-mle-and-map`, `model-selection`, `probabilistic-modeling-and-inference`.

**Content anchors:** data as vectors and the feature-map framing; models as functions vs models as distributions, and the three phases (prediction, training, model selection); ERM — hypothesis class, loss, empirical vs expected risk, regularization as a constraint on the class, generalization, and a Figure of train/test error vs capacity showing the classic U; MLE and MAP with the negative-log-likelihood algebra done in full, MAP as regularized MLE derived rather than asserted, and a Figure of the likelihood surface with the MLE and MAP marked for the same data under three prior strengths; probabilistic modelling, joint/marginal/conditional, the marginal likelihood integral and why it is hard, posterior predictive; directed graphical models with plate notation as mermaid diagrams, conditional independence read off the graph, and d-separation worked on three canonical triples; model selection — nested cross-validation implemented from scratch, Bayesian evidence, Occam's razor made quantitative, and a Figure of evidence vs polynomial degree peaking at the true degree.

### Task 11: Chapter 9 — Linear Regression (8 pages, 660–667, all new)

**Book:** pp. 289–316.

**Files:** create the folder and all 8 pages. Figure modules for `problem-formulation`, `parameter-estimation`, `overfitting-and-model-selection-in-regression`, `bayesian-linear-regression`, `maximum-likelihood-as-orthogonal-projection`.

**New lab:** `RegressionLab` (`algos/regression.ts`, props `{ data?: number[][]; degree?: number; lambda?: number; mode: "ols" | "ridge-path" | "bayesian"; title; desc?; lib? }`).

**Extras required for Chapters 9–12:** `## With scikit-learn` section and `<AlgorithmCard>` on every concept page. The scikit-learn result must match the from-scratch result to floating-point tolerance, and the page must print the comparison.

**Content anchors:** the Gaussian-noise likelihood and why least squares falls out of it rather than being assumed; MLE, the normal equations, feature maps making a linear model fit curves, MAP as ridge with λ = σ²/b² derived; overfitting with a Figure of RMSE train/test vs polynomial degree on the book's own setup; Bayesian linear regression — parameter posterior, predictive distribution, error bars that widen away from the data — with `RegressionLab` in `bayesian` mode and a Figure of the predictive band; and §9.4 re-reading the MLE as the orthogonal projection of Chapter 3, closing the loop the projections page opened.

### Task 12: Chapter 10 — Principal Component Analysis (10 pages, 680–689, all new)

**Book:** pp. 317–347.

**Files:** create the folder and all 10 pages. Figure modules for `problem-setting`, `maximum-variance-perspective`, `projection-perspective`, `eigenvector-computation-and-low-rank-approximations`, `pca-in-high-dimensions`, `key-steps-of-pca-in-practice`, `latent-variable-perspective`.

**New lab:** `PCALab` (`algos/pca.ts`, props `{ data?: number[][]; components?: number; view: "variance" | "projection" | "scree" | "reconstruction"; title; desc?; lib? }`).

**Content anchors:** the compression problem setting; maximum-variance derivation with the Lagrange multiplier from Chapter 7 doing the work; projection perspective and the equivalence of the two objectives proved, not stated; eigenvector computation, power iteration reused from `EigenLab`, and the SVD route; PCA in high dimensions via the `n < d` kernel trick on `XXᵗ`; the practical recipe — centre, standardise, eigendecompose, project, reconstruct — with a Figure of scree and cumulative variance on a real dataset and a reconstruction grid at several component counts; probabilistic PCA as the latent-variable model, with the generative story and its EM connection forward to Chapter 11.

### Task 13: Chapter 11 — Gaussian Mixture Models (7 pages, 700–706, all new)

**Book:** pp. 348–369.

**Files:** create the folder and all 7 pages. Figure modules for `gaussian-mixture-model`, `parameter-learning-via-maximum-likelihood`, `em-algorithm`, `latent-variable-perspective`.

**New lab:** `EMLab` (`algos/em.ts`, props `{ data?: number[][]; k?: number; iterations?: number; init?: "random" | "kmeans" | "bad"; title; desc?; lib? }` — one frame per E-step and per M-step, with the log-likelihood in the watch panel so the reader sees it climb monotonically).

**Content anchors:** the mixture density and why one Gaussian is not enough (Figure: a bimodal dataset with the single-Gaussian fit overlaid); the MLE responsibilities and the circular dependency that motivates EM, with the derivative conditions for means, covariances and mixing weights each derived; EM itself — E-step, M-step, monotone likelihood, convergence to a local optimum, and the initialisation sensitivity shown by `EMLab` with `init="bad"`; the latent-variable view, the ELBO, and the link back to §8.4 and probabilistic PCA.

### Task 14: Chapter 12 — Support Vector Machines (8 pages, 720–727, all new)

**Book:** pp. 370–394.

**Files:** create the folder and all 8 pages. Figure modules for `separating-hyperplanes`, `primal-support-vector-machine`, `dual-support-vector-machine`, `kernels`, `numerical-solution`.

**New lab:** `MarginLab` (`algos/svm.ts`, props `{ data?: number[][]; labels?: number[]; C?: number; kernel?: "linear" | "poly" | "rbf"; view: "margin" | "dual" | "kernel"; title; desc?; lib? }`).

**Content anchors:** the hyperplane, the margin, and the scaling convention that makes the margin `1/‖w‖`; the primal problem, hinge loss, soft margin, C as the regularization dial, and the ERM reading from Chapter 8; the dual via the Lagrangian of Chapter 7, KKT and complementary slackness explaining exactly why only support vectors matter (with a Figure marking them); kernels — the trick, Mercer's condition, the feature space you never build, and a Figure of decision boundaries for linear/poly/rbf on `two_moons`; numerical solution as the QP of §7.3.2, with a from-scratch projected-gradient dual solver whose support vectors match `sklearn.svm.SVC` on the same data.

---

## Task 15: Recall Drill page, deck regeneration, and cross-link audit

**Files:**
- Create: `.../Recall Drill.mdx` (730)
- Modify: every chapter overview — embed `<MathDrillDeck chapters={["Chapter NN - Title"]} />`
- Modify: `.../Mathematics for Machine Learning.mdx` — final pass
- Regenerate: `src/data/mml/recall.yaml`

- [ ] **Step 1: Write the Recall Drill page**

`<MathDrillDeck />` over the whole module, with an explanation of spaced retrieval and how to use the chapter filter.

- [ ] **Step 2: Regenerate the deck**

```bash
node scripts/gen-mml-recall.mjs
```

Expected: cards from all 12 chapters. Any concept page contributing zero cards has a malformed `## Recall card` section — fix the page, not the generator.

- [ ] **Step 3: Add the per-chapter deck to each chapter overview**

- [ ] **Step 4: Cross-link audit**

Every `## Next` link resolves. Every forward reference ("we return to this in Chapter 7") points at a real slug with a trailing slash. Chapters 9–12 link to their ML-module counterparts and those links resolve. Run:

```bash
node scripts/mdxcheck.mjs "src/content/docs/Mathematics for Machine Learning"
```

- [ ] **Step 5: Final module index pass**

All 12 chapters plus Chapter 0 listed, page counts accurate, the reading paths (no-calculus, book-parallel, ML-first) each spelled out.

- [ ] **Step 6: Full verification gate (Recipe F) plus a module-wide count**

Report final page count, word count, p5 sketch count, lab count, figure count, quiz count, exercise count against the spec's target table. Report every shortfall honestly rather than rounding up.

- [ ] **Step 7: Report to the author. Do not commit.**

---

## Self-review notes

**Spec coverage.** Every spec section maps to a task: page inventory → Tasks 2–14; Page Spec v2-math → Recipe D, applied in every task; Track A p5 → Recipe A, Global Constraints; Track B labs → Recipe C, with all 19 assigned (4 in Task 1, `SpanExplorer` T4, `NormBall`/`ProjectionLab` T5, `EigenLab`/`SVDLab` T6, `SurfaceGrad`/`TaylorLab`/`AutodiffGraph` T7, `BayesLab` T8, `ConstraintLab`/`ConvexLab` T9, `RegressionLab` T11, `PCALab` T12, `EMLab` T13, `MarginLab` T14 — 19 total); Track C figures → per-task figure modules; flashcard plumbing → Task 1 + Task 15; notation page → Task 2; verification → Recipe F in every task; build order → task order.

**Deviation from the skill's default, stated deliberately.** The skill's task template ends every task with a `git commit` step. This plan has none, because the author explicitly reserved committing. It also replaces the TDD cycle with the repo's real verification loop: these are 118 MDX content pages with no test framework, and `mdxcheck` + the p5/mermaid linters + an actual figure render are what "the test" means here. The React labs and the recall generator are the only executable code, and their pass condition is stated inline (Task 1 Steps 3 and 5).

**Known unknown, flagged rather than papered over.** Recipes B and C use illustrative signatures for `_style.py`, `build.py`'s `FIGURES` record and `VizPlayer`'s props. Task 1 Step 1 exists specifically to replace them with the real ones before any dependent code is written. No later task may proceed on the illustrative versions.

# Mathematics for Machine Learning — Module Completion & Upgrade

Date: 2026-08-21
Module: `src/content/docs/Mathematics for Machine Learning`
Source book: *Mathematics for Machine Learning* — Deisenroth, Faisal & Ong (Cambridge UP, 2020),
draft 2019-12-11, `mml-book.pdf` at repo root, 417 pages.
Status: approved, in implementation

## Problem

The module covers Chapters 2–6 of a 12-chapter book, and covers Chapter 6 only to §6.5. Six of the
book's twelve chapters have no pages at all. Measured today:

| metric | value |
| --- | --- |
| pages | 43 |
| words | 58,798 |
| KaTeX expressions | ~1,153 |
| mermaid diagrams | 42 |
| p5 sketches | 37 |
| DataCamp exercises | 111 |
| `<Quiz>` blocks | **0** |
| `<Figure>` matplotlib plots | **0** |
| `<AlgorithmCard>` | **0** |

Three gaps:

1. **Coverage.** Chapter 1, §6.6–6.7, and Chapters 7–12 are absent. A reader following the book
   runs out of site at page 197 of 417. Continuous Optimization (Ch 7) is missing entirely, which
   means the module teaches gradients but never gradient descent, Lagrange multipliers, or
   convexity — the machinery every training loop rests on.
2. **Page depth.** The 43 existing pages predate the repo's **Page Spec v2** (in force for the
   Machine Learning module, documented in `2026-08-02-ml-content-upgrade-design.md` and
   `.claude/skills/new-tutorial/SKILL.md`). They average 1,400 words with one mermaid diagram, one
   p5 sketch and three exercises. They have no `## What you'll learn`, no worked-by-hand numeric
   table, no self-assessment quiz, no real-data plot, no pitfalls section.
3. **Learning surfaces.** Nothing supports revision or retrieval practice: no notation reference,
   no formula sheets, no end-of-chapter exercise work, no flashcards. The book's own
   end-of-chapter Exercises (pp. 64, 96, 137, 170, 222, 247) are never touched.

The module's own index page compounds this: it advertises Chapters 2–5 and does not mention
Chapter 6, which exists.

## Goals

Make this module a self-sufficient path through the entire book: a reader with high-school algebra
can start at Chapter 0 and finish Chapter 12 without leaving the site.

| | now | target |
| --- | --- | --- |
| pages | 43 | 118 |
| words | 59k | ~400k |
| chapters covered | 5 of 12 (one partial) | 12 of 12 + prereq bridge |
| p5 sketches | 37 | ~245 |
| React math labs | 0 | 19 |
| matplotlib figures | 0 | ~120 |
| mermaid | 42 | ~230 |
| quizzes | 0 | ~93 |
| DataCamp exercises | 111 | ~430 |
| book exercise pages | 0 | 11 |
| formula sheets | 0 | 11 |
| flashcard deck | none | 1 filtered deck |

## Non-goals

- No full `astro build` as an inner loop (~2 h; see `no-full-site-builds` memory).
- No edits to the Machine Learning module. Chapters 9–12 are built here **math-first** (derivations,
  proofs, the projection/eigen/EM/KKT arguments) and cross-link to the ML module's applied pages;
  the ML pages are left as they are. Duplication of *framing* is accepted; the two modules answer
  different questions ("why is this the estimator" vs "how do I fit it").
- No new runtime dependencies. Everything reuses `p5-viz.js`, `VizPlayer`, `Quiz.astro`,
  `Figure.astro`, `DataCampExercise.astro`, `AlgorithmCard.astro`, `dsa/DrillDeck.tsx`.
- No renaming of existing files (Windows-invalid-filename hazard; see `repo-gotchas`). Sidebar
  `order` values are renumbered, filenames are not.

## Page inventory

Sidebar `order` is scoped per `autogenerate` group in `astro.config.mjs`, so values collide freely
across modules and this module can be renumbered without touching any other. Blocks leave gaps for
later insertion.

### Chapter 0 — Getting Ready (new, 7 pages, 501–507)

Prerequisite bridge. The book assumes "high school mathematics and physics"; these pages make that
assumption checkable rather than aspirational.

| order | page | covers |
| --- | --- | --- |
| 501 | Getting Ready Overview | what you need, self-test, how to skip ahead |
| 502 | Notation and Symbols | the book's notation table (pp. 8 ff.), rendered and searchable |
| 503 | Sums, Products, and Set Notation | Σ, Π, index gymnastics, set-builder, ∈/⊆/×, indicator |
| 504 | Functions, Limits, and Continuity | domain/codomain/image, limits, continuity, why it matters for gradients |
| 505 | Single-Variable Calculus Refresher | derivative rules, chain rule, integration, FTC |
| 506 | Complex Numbers in One Page | needed for complex eigenvalues (Ch 4) and rotations |
| 507 | NumPy for Mathematics | arrays as vectors/matrices, `@`, broadcasting, `linalg`, dtype/precision traps |

### Chapter 1 — Introduction and Motivation (new, 3 pages, 510–512)

Book Ch 1, pp. 11–16.

| order | page | covers |
| --- | --- | --- |
| 510 | Introduction and Motivation Overview | why math for ML, the book's structure |
| 511 | Finding Words for Intuitions | §1.1 — data/model/learning; the three senses of "algorithm"; predictor vs training |
| 512 | Two Ways to Read This Book | §1.2–1.3 — bottom-up vs top-down, the four pillars, the module's own map, how to use exercises |

### Chapter 2 — Linear Algebra (11 pages, 520–530)

Rewrite of 9 existing pages + 2 new.

| order | page | status |
| --- | --- | --- |
| 520 | Linear Algebra Overview | rewrite |
| 521 | Systems of Linear Equations (§2.1) | rewrite |
| 522 | Matrices (§2.2) | rewrite |
| 523 | Solving Systems of Linear Equations (§2.3) | rewrite |
| 524 | Vector Spaces (§2.4) | rewrite |
| 525 | Linear Independence (§2.5) | rewrite |
| 526 | Basis and Rank (§2.6) | rewrite |
| 527 | Linear Mappings (§2.7) | rewrite |
| 528 | Affine Spaces (§2.8) | rewrite |
| 529 | Chapter 2 Exercises and Solutions | new — book Exercises 2.1–2.20, p. 64 |
| 530 | Chapter 2 Formula Sheet | new |

### Chapter 3 — Analytic Geometry (12 pages, 540–551)

Rewrite of 10 existing + 2 new. Sections 3.1–3.9 keep their current one-page-per-section split;
exercises page covers p. 96.

### Chapter 4 — Matrix Decompositions (10 pages, 560–569)

Rewrite of 8 existing + 2 new. Sections 4.1–4.7; exercises page covers p. 137.

### Chapter 5 — Vector Calculus (11 pages, 580–590)

Rewrite of 9 existing + 2 new. Sections 5.1–5.8; exercises page covers p. 170.

### Chapter 6 — Probability and Distributions (10 pages, 600–609)

| order | page | status |
| --- | --- | --- |
| 600 | Probability and Distributions Overview | rewrite |
| 601 | Construction of a Probability Space (§6.1) | rewrite |
| 602 | Discrete and Continuous Probabilities (§6.2) | rewrite |
| 603 | Sum Rule, Product Rule, and Bayes Theorem (§6.3) | rewrite |
| 604 | Summary Statistics and Independence (§6.4) | rewrite |
| 605 | Gaussian Distribution (§6.5) | rewrite |
| 606 | Conjugacy and the Exponential Family (§6.6) | **new** — conjugate priors, sufficient statistics, natural parameters |
| 607 | Change of Variables and Inverse Transform (§6.7) | **new** — Jacobian in densities, inverse-transform sampling |
| 608 | Chapter 6 Exercises and Solutions | new — p. 222 |
| 609 | Chapter 6 Formula Sheet | new |

### Chapter 7 — Continuous Optimization (all new, 10 pages, 620–629)

The largest single gap. Book Ch 7, pp. 225–248.

| order | page | covers |
| --- | --- | --- |
| 620 | Continuous Optimization Overview | the optimization view of learning; unconstrained vs constrained vs convex |
| 621 | Optimization Using Gradient Descent (§7.1) | step size, convergence, condition number, ill-conditioning |
| 622 | Momentum and Stochastic Gradient Descent (§7.1.1–7.1.2) | momentum, minibatch noise, why SGD scales |
| 623 | Constrained Optimization and Lagrange Multipliers (§7.2) | Lagrangian, dual problem, weak/strong duality |
| 624 | Convex Sets and Convex Functions (§7.3) | definitions, Jensen, first/second-order conditions |
| 625 | Linear Programming (§7.3.1) | standard form, dual LP, feasible polytope |
| 626 | Quadratic Programming (§7.3.2) | QP form, KKT conditions, the SVM connection |
| 627 | Legendre-Fenchel Transform and Convex Conjugate (§7.3.3) | supporting hyperplanes, conjugate duality |
| 628 | Chapter 7 Exercises and Solutions | book Exercises 7.1–7.4, p. 247 |
| 629 | Chapter 7 Formula Sheet | new |

### Chapter 8 — When Models Meet Data (all new, 9 pages, 640–648)

| order | page | covers |
| --- | --- | --- |
| 640 | When Models Meet Data Overview | §8.0 — the three meanings of "model", the four-pillar payoff |
| 641 | Data, Models, and Learning (§8.1) | data as vectors, model as function vs distribution, learning as three phases |
| 642 | Empirical Risk Minimization (§8.2) | hypothesis class, loss, regularization, generalization, cross-validation |
| 643 | Parameter Estimation: MLE and MAP (§8.3) | likelihood, negative log-likelihood, priors, MAP as regularized MLE |
| 644 | Probabilistic Modeling and Inference (§8.4) | joint distributions, marginal likelihood, posterior predictive, latent variables |
| 645 | Directed Graphical Models (§8.5) | plate notation, conditional independence, d-separation |
| 646 | Model Selection (§8.6) | nested cross-validation, Bayesian evidence, Occam's razor |
| 647 | Chapter 8 Exercises and Solutions | new |
| 648 | Chapter 8 Formula Sheet | new |

### Chapter 9 — Linear Regression (all new, 8 pages, 660–667)

| order | page | covers |
| --- | --- | --- |
| 660 | Linear Regression Overview | why this is the book's first worked ML problem |
| 661 | Problem Formulation (§9.1) | likelihood with Gaussian noise, feature maps |
| 662 | Parameter Estimation: MLE, MAP, Regularization (§9.2) | normal equations, MLE with features, MAP = ridge |
| 663 | Overfitting and Model Selection in Regression (§9.2.3–9.2.4) | polynomial degree, RMSE train/test, marginal likelihood |
| 664 | Bayesian Linear Regression (§9.3) | parameter posterior, predictive distribution, error bars |
| 665 | Maximum Likelihood as Orthogonal Projection (§9.4) | the Ch 3 projection re-read as regression |
| 666 | Chapter 9 Exercises and Solutions | new |
| 667 | Chapter 9 Formula Sheet | new |

### Chapter 10 — Principal Component Analysis (all new, 10 pages, 680–689)

Overview (680), Problem Setting §10.1 (681), Maximum Variance Perspective §10.2 (682), Projection
Perspective §10.3 (683), Eigenvector Computation and Low-Rank Approximations §10.4 (684), PCA in
High Dimensions §10.5 (685), Key Steps of PCA in Practice §10.6 (686), Latent Variable Perspective
and Probabilistic PCA §10.7 (687), Exercises and Solutions (688), Formula Sheet (689).

The book ships no exercise set for Chapters 10–12, so those Exercises pages carry problems authored
in the book's style and difficulty rather than restatements.

### Chapter 11 — Density Estimation with Gaussian Mixture Models (all new, 7 pages, 700–706)

Overview (700), Gaussian Mixture Model §11.1 (701), Parameter Learning via Maximum Likelihood
§11.2 (702), EM Algorithm §11.3 (703), Latent-Variable Perspective §11.4 (704), Exercises (705),
Formula Sheet (706).

### Chapter 12 — Classification with Support Vector Machines (all new, 8 pages, 720–727)

Overview (720), Separating Hyperplanes §12.1 (721), Primal Support Vector Machine §12.2 (722),
Dual Support Vector Machine §12.3 (723), Kernels §12.4 (724), Numerical Solution §12.5 (725),
Exercises (726), Formula Sheet (727).

### Module-wide (2 pages)

| order | page |
| --- | --- |
| 500 | Mathematics for Machine Learning (module index) — rewrite; currently omits Chapter 6 |
| 730 | Recall Drill — module-wide flashcard deck with chapter filter |

### Numbering reconciliation

Blocks, authoritative:

```
500        module index
501–507    Ch 0  Getting Ready              (7)
510–512    Ch 1  Introduction              (3)
520–530    Ch 2  Linear Algebra            (11)
540–551    Ch 3  Analytic Geometry         (12)
560–569    Ch 4  Matrix Decompositions     (10)
580–590    Ch 5  Vector Calculus           (11)
600–609    Ch 6  Probability               (10)
620–629    Ch 7  Continuous Optimization   (10)
640–648    Ch 8  When Models Meet Data     (9)
660–667    Ch 9  Linear Regression         (8)
680–689    Ch 10 PCA                       (10)
700–706    Ch 11 GMM                       (7)
720–727    Ch 12 SVM                       (8)
730        Recall Drill                    (1)
```

Total 118 pages. Chapter 10 is 10 pages (680–689): overview, §10.1–10.7 (7 pages), Exercises,
Formula Sheet.

Every chapter block gets **one Exercises and Solutions page** and **one Formula Sheet page**.
Chapters 0 and 1 get neither (Ch 0 is itself remedial; Ch 1 is prose).

## Page Spec v2-math

Every concept page. Sections scale to the topic; a section is skipped only when it genuinely does
not apply (e.g. no real-data plot for §2.8 Affine Spaces — a p5 sketch carries it instead).

```
frontmatter: title, description, sidebar.order
## What you'll learn         5–7 bullets
## Intuition                 real-life analogy + mermaid concept map
## The math                  KaTeX, derivation stepped, every symbol defined on first use
## Worked example by hand     6–8 row table, arithmetic shown, verified against NumPy
## See it move               2–3 p5 sketches with in-canvas controls, or a React math lab
## From scratch              numpy implementation, printed output block
## On real data              <Figure> matplotlib plot            (where data makes sense)
## Reading the plot          what the reader should take from the figure
:::tip[From the book]        exact section / definition / theorem / equation numbers
## Pitfalls                  3–5 :::caution — singular matrices, ill-conditioning, sign
                             conventions, floating-point, off-by-one in index notation
## Compare                   table against sibling ideas
<Quiz />                     4 MCQ, hidden answers + explanations
## 🧪 Try It Yourself        5 DataCampExercise blocks, easy → hard, each with its own ###
## Recall                    bullet cards — the source the flashcard generator reads
## Next                      link to the following page
```

Deliberate deviations from the ML module's v2:

- **`:::tip[From the book]` is retained and required.** It is this module's signature: it lets a
  reader hold the PDF open beside the page. Every concept page cites the exact section and the
  numbered definitions/equations it covers.
- **`## With scikit-learn` is dropped** for Chapters 0–7 (there is no estimator to call) and
  **required** for Chapters 9–12, where it demonstrates that the from-scratch derivation reproduces
  the library result to floating-point tolerance.
- **`<AlgorithmCard>`** appears only on Chapters 9–12 concept pages, where there is an algorithm to
  summarize.
- **`## Recall`** replaces the current `## Recap`. Same content role, new heading, because the
  flashcard generator keys off it. Bullets follow the two DSA card shapes so the existing generator
  logic ports without change:
  - `- **Cue** — content` (aspect front, content back)
  - `- **The claim is X**: elaboration` (cloze: claim blanked on the front)

Existing pages are rewritten, not discarded: their analogies (the pencil shadow for projections,
the production-plan framing for linear systems) and their `From the book` blocks are the strongest
material in the module and carry forward verbatim where they still fit.

### Variant — chapter overview page

No math derivation. Chapter map (mermaid), prerequisites, learning outcomes, time estimate, page
table with a one-line "big idea" per page, link to the chapter's formula sheet and exercises.
~900–1,200 words.

### Variant — Exercises and Solutions page

```
## How to use this page      work it before reading the solution
## Exercise N.M              problem statement restated in KaTeX
  <details> solution         full worked solution, every step
  ```python``` verification  NumPy check with printed output
## Where you got stuck       common wrong turns per exercise
## Recall
```

For Chapters 2–7 the problems are the book's own (pp. 64, 96, 137, 170, 222, 247), restated — not
copied verbatim — with independently authored solutions. For Chapters 8–12, which have no exercise
sets in the book, problems are authored in the same style and difficulty.

### Variant — Formula Sheet page

Pure reference: KaTeX tables grouped by topic, one line of "when you use it" per entry, no prose,
no exercises, no p5. Links back to the page that derives each result. Target ~600 words plus
tables.

## Interactive layer

Three tracks, all on existing infrastructure.

### Track A — p5 sketches with in-canvas controls

Target ~245 sketches, ~3 per concept page (from 37 total today).

The loader (`public/scripts/p5-viz.js`) builds each fence in **p5 instance mode** —
`new p5(factory, stage)` with the source evaluated inside `with (p) { … }` — and re-binds these
hooks onto the instance: `preload setup draw mousePressed mouseReleased mouseClicked mouseMoved
mouseDragged doubleClicked mouseWheel keyPressed keyReleased keyTyped touchStarted touchMoved
touchEnded windowResized`.

**Controls are drawn on the canvas and driven by those hooks — never `createSlider`.** Reasons:

1. `createSlider` appears nowhere in the repo today, so the DOM-element path through the loader,
   the `.pch-p5` panel CSS, and `viz-fullscreen.js` is untested.
2. DOM sliders inherit no panel styling and would need new CSS on a shared component.
3. `restartBtn` calls `instance.remove()` and rebuilds; orphaned DOM elements are a known p5
   instance-mode hazard.
4. In-canvas controls survive fullscreen, theme, and restart with zero extra surface.

Convention for every interactive sketch:

- A `knob(x, y, w, value, min, max, label)` draw helper and a `hit()` test in `mousePressed` /
  `mouseDragged`, both local to the sketch (fences are self-contained by design).
- Drag handlers end with `if (!isLooping()) redraw();` so a paused sketch still responds to input.
- Palette fixed by the design system: background `(13, 17, 23)`, blue `(75, 139, 190)`, amber
  `(255, 211, 67)`, red `(232, 110, 110)`, green `(120, 200, 140)`, grid `(32, 44, 58)`.
- Every fence carries `title`, `desc`, `height`.
- Draggable elements are visibly draggable (filled handle + hairline track) and labelled with their
  live numeric value, because there is no cursor affordance on a canvas.

### Track B — React math labs on `VizPlayer`

New `src/components/viz/math/` with algorithm modules under `src/components/viz/math/algos/`,
speaking the existing `Frame`/`Trace` contract from `src/components/viz/frames.ts`:

```
algorithm (pure)  ──▶  Frame[]  ──▶  VizPlayer (transport)  ──▶  stage renderer
```

`VizPlayer` already owns play/pause/step±1/scrub/speed/reset, keyboard, reduced-motion, the code
line-highlight and the watch panel. That is exactly what *iterative* mathematics needs and exactly
what a p5 animation cannot give: the reader stops on the elimination step, the EM iteration, the
descent step they do not understand, and steps backwards.

Embedded with `client:visible` (required — without it the island renders frame 0 and never
hydrates). Every component takes `title` (required), `desc`, `lib`, `showCode`, `ms`, `autoPlay`.

| component | algos | used by |
| --- | --- | --- |
| `MatrixLab` | 2×2/3×3 transform, drag entries, grid deformation, det as signed area | §2.2, §2.7, §4.1 |
| `ElimStepper` | Gaussian elimination → row echelon → reduced row echelon, pivot by pivot | §2.3 |
| `SpanExplorer` | span of 1/2/3 vectors, dependence detection, basis extraction | §2.4–2.6 |
| `NormBall` | unit balls for p = 1, 1.5, 2, 4, ∞ | §3.1 |
| `ProjectionLab` | projection onto line/plane, Gram-Schmidt step by step | §3.5–3.8 |
| `EigenLab` | power iteration, eigenvector convergence, characteristic polynomial roots | §4.2, §4.4 |
| `SVDLab` | rank-k reconstruction with a k slider, singular-value spectrum | §4.5–4.6 |
| `SurfaceGrad` | contour + gradient field + directional derivative | §5.2–5.3 |
| `TaylorLab` | Taylor polynomial order 0…6 around a movable point | §5.8 |
| `AutodiffGraph` | computation graph, forward pass then reverse pass, node by node | §5.6 |
| `DistributionLab` | pdf/cdf with parameter controls, sampling, Gaussian conditioning/marginals | §6.2, §6.5 |
| `BayesLab` | prior × likelihood → posterior, sequential conjugate updates | §6.3, §6.6 |
| `DescentLab` | GD, momentum, SGD, Newton on selectable surfaces; one frame per step | §7.1–7.2 |
| `ConstraintLab` | level sets tangent to a constraint curve, multiplier as tangency scale | §7.2 |
| `ConvexLab` | convex vs non-convex, epigraph, chord test, Jensen | §7.3 |
| `RegressionLab` | least squares, ridge path, Bayesian predictive band | Ch 9 |
| `PCALab` | max-variance vs projection views, scree plot, reconstruction error | Ch 10 |
| `EMLab` | E-step responsibilities then M-step updates, iteration by iteration | Ch 11 |
| `MarginLab` | margin, support vectors, C slider, kernel choice, dual coefficients | Ch 12 |

19 components. Each is a thin renderer plus one algos module; the transport is inherited.

### Track C — matplotlib figures

New figure group `scripts/figures/mml/<page-slug>.py`, each exporting `FIGURES`, rendered by
`python scripts/figures/build.py mml` into committed theme-pair SVGs at
`public/images/mml/<page-slug>/`. Target ~120 figures.

Reserved for what neither p5 nor mermaid can do: real numbers on real data. Condition-number vs
error curves, singular-value spectra of an actual image, MNIST PCA scree and reconstructions,
convergence curves at several learning rates, GMM density contours over a real 2-D dataset,
SVM decision boundaries per kernel, RMSE-vs-degree overfitting curves.

Embedded via `<Figure src="/images/mml/<page-slug>/<name>" alt … title … caption />` — `src`
without the `-dark.svg` / `-light.svg` suffix.

## Extras plumbing

### Flashcard deck

- `scripts/gen-mml-recall.mjs` — modeled on `scripts/gen-recall-deck.mjs`. Walks the module,
  extracts `## Recall` bullets, handles both card shapes (aspect and cloze), writes
  `src/data/mml/recall.yaml`.
- `src/data/mml/index.ts` — `buildDeck({ chapters })` and `recallChapters`, mirroring
  `src/data/dsa/index.ts`.
- `src/components/MathDrillDeck.astro` — resolves filter props at build time and hands
  `dsa/DrillDeck.tsx` its `items` / `phases` props. The island's props are already generic
  (`key, kind, label, text, cardId, cardTitle, phase, url`), so it is reused unchanged; `phase`
  carries the chapter folder name.
- `package.json` gains `"mml:recall": "node scripts/gen-mml-recall.mjs"`.
- Page 730 renders `<MathDrillDeck />` over the whole module; each chapter overview embeds
  `<MathDrillDeck chapters={["Chapter 07 - Continuous Optimization"]} />`.

Generated, not authored: a second hand-written copy of the same facts would drift silently.

### Notation page

Page 502 mirrors the book's notation table as searchable KaTeX rows, grouped (scalars/vectors/
matrices, sets, probability, calculus). Every chapter overview links to it. This is the single
reference that makes the rest of the module readable to someone who has not read the book's front
matter.

## Naming and links

- Filenames: plain ASCII, spaces allowed, **never** `" : * ? < > | \ /` (the repo already carries
  ~11 files Git cannot check out on Windows — no more).
- Folders: `Chapter NN - Title`, matching the five that exist.
- Links use the real Starlight slug — lowercase, each space → `-`, so
  `Chapter 07 - Continuous Optimization` → `chapter-07---continuous-optimization` (three hyphens) —
  with a trailing slash.
- Import depth from a chapter page is four levels: `../../../../components/…`. Counted, not guessed.

## Verification

Per chapter, before moving on:

| check | command |
| --- | --- |
| MDX/JSX/brace/template-literal errors | `node scripts/mdxcheck.mjs "src/content/docs/Mathematics for Machine Learning"` |
| mermaid syntax | `npm run viz:mermaid` |
| p5 fences parse | `node scripts/lint-p5.mjs` |
| figures render | `python scripts/figures/build.py mml` |
| every `<Figure src>` has committed SVGs | glob check against `public/images/mml/` |
| `sidebar.order` unique within the module | grep + sort |
| import `../` depth | counted per file |
| GFM tables | **eyeballed** — mdxcheck does not catch table errors that break `astro build` |

No full `astro build`. `git add -A` is never used (it would stage deletion of the Windows-invalid
files). **Nothing is committed** — the author commits.

Every number a page claims comes from actually running the code that produces it.

## Build order

Vertical slices. One chapter per slice, each slice complete and verified before the next, so every
stopping point is a shippable state.

| phase | contents |
| --- | --- |
| 1 | Infra: `scripts/figures/mml/` group, `viz/math/` base + `MatrixLab` `ElimStepper` `DistributionLab` `DescentLab`, recall generator + `src/data/mml/` + `MathDrillDeck.astro`, `npm run mml:recall`, module index rewrite (500), this spec |
| 2 | Ch 0 Getting Ready (501–507) |
| 3 | Ch 1 Introduction (510–512) |
| 4 | Ch 2 Linear Algebra (520–530) — 9 rewrites + 2 new; `SpanExplorer` |
| 5 | Ch 3 Analytic Geometry (540–551) — 10 rewrites + 2 new; `NormBall`, `ProjectionLab` |
| 6 | Ch 4 Matrix Decompositions (560–569) — 8 rewrites + 2 new; `EigenLab`, `SVDLab` |
| 7 | Ch 5 Vector Calculus (580–590) — 9 rewrites + 2 new; `SurfaceGrad`, `TaylorLab`, `AutodiffGraph` |
| 8 | Ch 6 Probability (600–609) — 6 rewrites + 4 new; `BayesLab` |
| 9 | Ch 7 Continuous Optimization (620–629) — all new; `ConstraintLab`, `ConvexLab` |
| 10 | Ch 8 When Models Meet Data (640–648) — all new |
| 11 | Ch 9 Linear Regression (660–667) — all new; `RegressionLab` |
| 12 | Ch 10 PCA (680–689) — all new; `PCALab` |
| 13 | Ch 11 GMM (700–706) — all new; `EMLab` |
| 14 | Ch 12 SVM (720–727) — all new; `MarginLab` |
| 15 | Recall Drill page (730), regenerate deck, module index final pass, cross-link audit |

A React lab is built in the phase that first needs it, not up front, so its interface is designed
against a real page.

## Risks

| risk | mitigation |
| --- | --- |
| Scope: ~400k words, 245 sketches, 19 components, 120 figures — many sessions | Vertical slices; report after each chapter; never mark a phase done that is not verified |
| `astro build` breaks on something mdxcheck misses (GFM tables) | Eyeball every table; keep table syntax simple; no full build as inner loop |
| In-canvas p5 controls are fiddly to author 245 times | One `knob`/`hit` idiom, established in phase 1's first sketches and copied |
| 19 React islands inflate the client bundle | All `client:visible`; each is a thin renderer over shared `VizPlayer`; no new dependencies |
| Renumbering 43 files' `sidebar.order` churns the diff | The files are being fully rewritten anyway |
| Chapters 9–12 duplicate the ML module | Different question per module (why the estimator vs how to fit it); explicit cross-links both ways |
| Figures need Python + matplotlib at author time | Already required by `npm run figures`; SVGs are committed so the Astro build stays Python-free |

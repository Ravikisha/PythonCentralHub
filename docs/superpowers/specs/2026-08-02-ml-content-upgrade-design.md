# Machine Learning Module Content Upgrade — Design

Date: 2026-08-02
Module: `src/content/docs/Machine Learning`
Status: approved, in implementation

## Problem

The ML module has 65 pages / 88k words built on a rigid template: one mermaid diagram, one p5
sketch, two Python blocks and three fill-in-the-blank exercises per page. Measured against the
`Mathematics for Machine Learning` module in the same repo, three gaps stand out:

| metric | ML (65 pages) | Math for ML (43 pages) |
| --- | --- | --- |
| words | 88,146 | 58,798 |
| mermaid diagrams | 80 | 42 |
| p5 sketches | 42 | 37 |
| DataCamp exercises | 173 | 111 |
| **KaTeX expressions** | **2** | **1,153** |
| tables | 12 | 31 |
| python blocks | 146 | 37 |

1. **No rendered math.** `remark-math` + `rehype-katex` are configured in `astro.config.mjs` and
   used heavily elsewhere, but ML pages write formulas as inline code —
   `` `σ(t) = 1 / (1 + exp(-t))` `` — so no derivation is readable as mathematics.
2. **Uniform shallow structure.** Every page follows the same shape regardless of topic. No worked
   numeric examples, no from-scratch implementations, no comparison tables, no self-assessment.
3. **Curriculum ends at Phase 08.** No interpretability, no imbalanced data, no time series, no
   experiment tracking, no capstone projects.

## Goals

Bring all 65 pages to a textbook-grade standard and add 24 pages of missing curriculum.

| | now | target |
| --- | --- | --- |
| pages | 65 | 89 |
| words | 88k | ~270k |
| KaTeX expressions | 2 | ~1,400 |
| mermaid | 80 | ~200 |
| p5 interactive | 42 | ~110 |
| generated static plots | 0 | ~180 |
| python blocks | 146 | ~500 |
| exercises | 173 | ~440 |
| quizzes | 0 | 89 |
| tables | 12 | ~250 |

## Page Spec v2

Every concept page follows this skeleton. Overview pages and MLOps pages take the noted variants.

```
frontmatter: title, description, sidebar.order
## What you'll learn          — 5-7 bullets
## Intuition                  — analogy + mermaid concept diagram
## The math                   — KaTeX, derivation stepped, symbols defined
## Worked example by hand     — 6-8 row table, arithmetic shown, verified vs sklearn
## See it move                — p5 sketch with controls
## From scratch               — numpy implementation (~25 lines)
## With scikit-learn          — idiomatic API, same result
## On real data               — dataset -> fit -> generated SVG figure
## Reading the plot           — interpretation of the figure
<AlgorithmCard />             — assumptions, complexity, hyperparams, sklearn class,
                                use when / avoid when
## Pitfalls                   — 3-5 :::caution asides, real failure modes
## Compare                    — table against sibling algorithms
<Quiz />                      — 4 MCQ with hidden answers + explanations
## Try It Yourself            — 5 DataCampExercise blocks, easy to hard
## Recap
## Next
```

Variants:

- **Phase overview pages**: skip math/code sections; use phase map, prerequisites, outcomes,
  time estimate, page table. Target ~900 words.
- **MLOps / engineering pages**: replace `## The math` with `## The architecture`; replace
  `## Worked example by hand` with a runnable end-to-end walkthrough.
- **Capstone pages**: problem framing, EDA, baseline, iteration, error analysis, deployment;
  checkpoint exercises between stages.

### Math conventions

Follow the `Mathematics for Machine Learning` module exactly: inline `$...$`, display `$$...$$`.
Define every symbol on first use. Cross-link derivations to the corresponding chapter in the
Mathematics module.

### Figure conventions

- Interactive intuition -> p5 (`ino` fence with `title` / `desc` / `height`).
- Structure, flow, taxonomy -> mermaid.
- Real data plots (ROC, learning curves, PCA scatter, dendrograms) -> matplotlib generated at
  author time, committed as SVG under `public/images/ml/<phase-slug>/`, rendered via `Figure.astro`
  which serves a dark and a light variant.
- Small numeric artifacts (confusion matrices, tensor shapes, iteration traces) -> markdown tables.

## Components (Phase 0)

Three new Astro components, styled with existing `theme.css` tokens and the `.pch-viz` chassis:

1. `Quiz.astro` — `questions` prop: `[{ q, options: string[], answer: number, explain: string }]`.
   Vanilla JS, no framework. Answer hidden until selection; explanation revealed after.
2. `AlgorithmCard.astro` — structured summary box.
3. `Figure.astro` — theme-aware static figure with caption and fullscreen affordance.

Starlight's built-in `<Tabs>` / `<TabItem>` covers the Intuition | Math | Code pattern; no new
component needed.

## Figure pipeline

- `scripts/figures/_style.py` — shared matplotlib style matching the site palette, plus a
  `save(fig, slug, name)` helper emitting `-dark.svg` and `-light.svg`.
- `scripts/figures/<phase>/<page-slug>.py` — one module per page that needs plots.
- `scripts/figures/build.py` — discovers and runs every figure module.
- `npm run figures` — runs the builder. SVGs are committed; the site build has no Python
  dependency.

## Rollout

Twelve waves, one phase each, foundations first so later cross-links resolve.

| wave | phase | pages | type |
| --- | --- | --- | --- |
| 1 | 03 Regression | 9 | upgrade |
| 2 | 04 Classification | 10 | upgrade |
| 3 | 02 Preprocessing | 9 | upgrade |
| 4 | 07 Optimization | 7 | upgrade |
| 5 | 05 Ensembles | 6 | upgrade |
| 6 | 06 Unsupervised | 9 | upgrade |
| 7 | 01 Foundation | 8 | upgrade |
| 8 | 08 MLOps | 6 | upgrade |
| 9 | 09 Interpretability & Responsible ML | 6 | new |
| 10 | 10 Applied ML Problems | 7 | new |
| 11 | 11 ML Engineering | 5 | new |
| 12 | 12 Capstones | 6 | new |

New pages take `sidebar.order` 313-399 (existing ML occupies 247-312; Deep Learning starts at 400).

A final pass converts bold sibling references into real links, cross-links the Mathematics module,
rewrites the eight thin phase overviews and the module landing page, and runs full verification.

## Verification

Per wave:

1. `node scripts/mdxcheck.mjs "src/content/docs/Machine Learning"` — seconds; catches JSX, brace and
   template-literal breakage without the ~30-minute full build.
2. `sidebar.order` uniqueness across the module.
3. Every referenced `public/images/ml/**` file exists.
4. Python blocks execute in a scratch environment and produce the output the page claims.
5. `npm run build` at wave end.

Filename rule: never use `" : * ? < > | \ /` in page filenames — the repo already carries ~11 files
Git cannot check out on Windows.

## Risks

- `remarkEscapeBraces` in `astro.config.mjs` rewrites `{`/`}` in text nodes. The Mathematics module
  renders correctly under the same pipeline, so ordering is safe, but verify on the first converted
  ML page before mass conversion.
- Build time is already ~30 minutes. Committed SVGs and short p5 sketches keep the increase bounded.
- 440 exercises means 440 untested SCT graders. Sample-verify per wave.
- Total authoring volume is ~250k words. The work is sequential across twelve waves, not one pass.

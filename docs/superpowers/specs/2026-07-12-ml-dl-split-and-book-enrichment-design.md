# ML/DL Split + Book Enrichment — from *Hands-On Machine Learning* (Géron, 2nd ed)

**Date:** 2026-07-12
**Status:** Approved (shape), executing
**Source:** `Hands-On_Machine_Learning_..._2nd-Edition-Aurelien-Geron.pdf` (572 pg, 19 ch;
text extracted per chapter to `scratchpad/book/chNN.txt`)

## Goal

Two things:

1. **Split** the single "Machine Learning" section into **two top-level sections** mirroring the
   book's two parts:
   - **Machine Learning** = classic ML (Book Part I, Ch1–9)
   - **Deep Learning** = neural nets & DL (Book Part II, Ch10–19) — **NEW section**
2. **Enrich** every page with the book's beginner-friendly explanations plus the site's viz surfaces
   (mermaid, p5.js, runnable code, DataCamp exercises), and **fill curriculum gaps** with new pages.

## Target structure

### Section A — Machine Learning (Book Part I)
| Phase | Book ch | Status |
|-------|---------|--------|
| P01 The ML Foundation | Ch1 | exists — enrich |
| **P02 Data Preprocessing & Feature Engineering** | Ch2 | **NEW** — cleaning, categorical encoding, feature scaling, transformation pipelines, end-to-end project frame, data snooping |
| P03 Supervised Learning – Regression | Ch4 | exists — enrich deep |
| P04 Supervised Learning – Classification | Ch3, Ch5 SVM, Ch6 Trees | exists — enrich deep |
| P05 Ensemble Learning | Ch7 | exists — enrich deep |
| P06 Unsupervised Learning + **Dimensionality Reduction** | Ch9 + **Ch8 PCA (new pages)** | exists + new |
| P07 Model Optimization & Tuning | Ch2/Ch4 | exists — enrich |
| P08 Model Deployment (MLOps) | Ch19 (generic serving) | **renamed from P10** |

### Section B — Deep Learning (Book Part II) — NEW top-level section
| Phase | Book ch | Source |
|-------|---------|--------|
| P01 Neural Network Foundations | Ch10 | moved: Perceptron, MLP, Activation Functions |
| P02 Training Deep Neural Networks | Ch11 | moved: Backprop & Optimizers + NEW: vanishing/exploding gradients, batch norm, dropout, LR scheduling |
| P03 Computer Vision with CNNs | Ch14 | moved: CNN intro, Transfer Learning + NEW: pooling, architectures (LeNet→ResNet), object detection intro |
| P04 Sequence Models with RNNs | Ch15 | moved: RNN intro + NEW: LSTM/GRU, time-series forecasting |
| P05 NLP & Transformers | Ch16 | moved: all 6 NLP pages + NEW: attention, Transformer intro |
| P06 Generative Deep Learning | Ch17 | **NEW**: autoencoders, VAEs, GANs |
| P07 Reinforcement Learning | Ch18 | **NEW**: RL intro, Q-learning, policy gradients |
| P08 Scaling & Deploying Deep Models | Ch12/13/19 | **NEW**: tf.data pipelines, TF Serving, GPU/distributed training |

## Moves (git mv, keep history)
- ML `Phase 08 - Deep Learning & Neural Networks/` 7 content pages → DL P01/P02/P03/P04
- ML `Phase 09 - Natural Language Processing (NLP)/` 6 content pages → DL P05
- ML `Phase 10 - Model Deployment (MLOps)/` → ML `Phase 08 - Model Deployment (MLOps)/`
- Old P08/P09 index pages discarded; new phase index pages authored.

## Sidebar / ordering
- `astro.config.mjs`: add `{ label: "Deep Learning", autogenerate: { directory: "Deep Learning" } }`
  right after the Machine Learning entry.
- Each top-level section autogenerates independently → `sidebar.order` sorts **within** a section only.
- ML keeps existing orders (248–298); new P02 inserted 257–264; MLOps renumbered to ~305 block
  (vacated by moved P08/P09).
- DL section uses a fresh block (index 400, phase P0N base 40N*10, pages increment).
- Import path for `DataCampExercise` is depth-identical between `Machine Learning/Phase X/` and
  `Deep Learning/Phase X/` (`../../../../components/...`) → moved pages keep working imports.

## Per-page enrichment kit (additive — keep strong content, replace weak)
1. **Intro** — what + why in the book's plain, beginner voice.
2. **Concept sections** — book explanations, simplified.
3. **Mermaid diagram** — 1 flow/concept in `.pch-viz` chassis.
4. **Code blocks** — runnable, `title=`'d, `showLineNumbers{1}`; scikit-learn / Keras.
5. **p5.js viz** — *only where genuinely visual* (~40%): gradient descent, decision boundaries,
   SVM margin, K-Means iterations, DBSCAN density, PCA projection, neuron/activation, CNN filters,
   confusion matrix, bias-variance, GAN generator-vs-discriminator, RL agent-environment loop.
6. **"From the book" callout** — one Géron insight/gotcha (`:::tip` / `:::note`).
7. **DataCamp exercises** — 2–3 fill-in-the-blank (`lang`, `hint`, `code`, `solution`, `sct`, `height`).
8. **Next** pointer.

Mermaid + book-insight + exercises on every touched page; p5 only where the concept is spatial/visual.

## Conventions & gotchas (from repo memory)
- **Mermaid labels** with `()` `<` `>` `/` `:` **must be quoted** (`A["Underfit (too simple)"]`),
  else client-side render error. `<br/>` stays unquoted.
- **p5 fences**: ` ```p5 title="" desc="" height="" ` → global-style sketch, instance-mode runtime,
  reduced-motion aware (starts paused). Editor-ink background `background(13, 17, 23)`.
- **DataCampExercise import** path relative + depth-correct (`../../../../components/DataCampExercise.astro`).
- **Filenames**: no `"` `<` `>` (Windows-invalid). Keep `sidebar.order`.
- Code fences use `title="..."` and `showLineNumbers{1}`.
- This restructure DOES touch `astro.config.mjs` (new section) — that is in scope here (unlike the
  Data Analytics pass). No theme/component code changes.

## Execution
- Structural moves + config + new phase index pages: done directly on the main thread.
- Enrichment + new content pages: dispatched to **`content-author`** subagents, **one phase per agent**,
  parallel batches. Each agent receives this kit, the relevant `chNN.txt`, and its page list.
- **Order:** restructure first → ML enrich (P03→P04→P05→P06→P02→P01→P07→P08) → DL enrich
  (P01→P02→P03→P04→P05→P06→P07→P08).
- `starlight-ui` consulted only if a new viz needs CSS (unlikely — `.pch-viz` chassis exists).

## Verification
- `astro check` clean.
- Mermaid label-quoting scan: no unquoted `()`/`<`/`>` in labels.
- Spot-render enriched + moved pages in dev; confirm both sidebar sections render.

## Out of scope
- Theming / component code (chassis exists).
- Large uncommitted Phase-rename working state on current branch (untouched; targeted commits only).

## Deliverables
- 2 sidebar sections (ML + DL).
- ~68 existing pages enriched; ~25–30 new pages (P02 preprocessing, PCA, DL generative/RL/scaling + gap pages).
- New mermaid on every touched page, ~50 p5 sketches, ~300+ DataCamp exercises.

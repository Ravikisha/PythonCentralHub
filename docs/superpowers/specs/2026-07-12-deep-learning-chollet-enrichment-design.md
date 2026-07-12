# Deep Learning Section Enrichment — from Chollet's *Deep Learning with Python* (2nd ed)

**Date:** 2026-07-12
**Status:** Approved (full scope), spec-then-build
**Source:** `Deep Learning with Python.pdf` (Chollet, 2nd ed; text → `scratchpad/dlp.txt`, chapters → `scratchpad/dlpbook/chNN.txt`)
**Not committed** (user commits themselves — see memory `commit-preference`).

## Goal

Enhance the existing Deep Learning section (`src/content/docs/Deep Learning/`, 8 phases, ~33 content
pages built from Gerón) with Chollet's Keras-first material: add new-topic pages and enrich existing
ones with clearer explanations, Keras code, diagrams, and visualizations. Fills the 3 gaps found
earlier (Transformer, image segmentation, seq2seq).

## Why Chollet complements the existing (Gerón-based) section

Chollet uniquely adds: tensor/gradient foundations, the universal ML workflow, canonical first
examples (IMDB/Reuters/house-prices), convnet interpretability (Grad-CAM), a full Keras Transformer
+ seq2seq, and generative art (text generation, DeepDream, neural style transfer), plus KerasTuner
and mixed-precision/multi-GPU. Chollet is Keras-first, matching the section's existing TF/Keras code.

## New pages (🆕) + enrichment (✨) by phase

**Phase 01 — Neural Network Foundations** (Chollet Ch2–4)
- 🆕 Tensors & Tensor Operations (data representations, broadcasting, reshape, dot). p5: reshape/broadcast geometry.
- 🆕 How Networks Learn: Gradient-Based Optimization (derivatives→gradient→SGD→backprop; GradientTape). p5: loss surface.
- 🆕 First Examples: IMDB (binary), Reuters (multiclass), House Prices (regression) — 1–3 walkthrough pages.
- ✨ enrich Perceptron / MLP / Activations / Keras-building.

**Phase 02 — Training Deep Neural Networks** (Ch5–7)
- 🆕 The Universal Workflow of ML (define → develop → deploy). mermaid pipeline.
- 🆕 Evaluation & Generalization (hold-out / K-fold / iterated validation; overfitting curve). p5: train vs val loss.
- 🆕 Callbacks & TensorBoard (Ch7).
- ✨ enrich batchnorm / optimizers / LR scheduling / regularization.

**Phase 03 — Computer Vision with CNNs** (Ch8–9) — fills segmentation gap
- 🆕 Data Augmentation for Small Datasets.
- 🆕 Image Segmentation.
- 🆕 Interpreting Convnets: Filter Visualization & Grad-CAM. Strong p5/heatmap.
- ✨ enrich CNN intro / pooling / architectures (residual, depthwise-separable) / transfer learning.

**Phase 04 — Sequence Models with RNNs** (Ch10)
- 🆕 Timeseries Forecasting: Temperature (baselines → RNN full walkthrough).
- ✨ enrich RNN / LSTM-GRU (recurrent dropout, stacking, bidirectional).

**Phase 05 — NLP & Transformers** (Ch11) — fills the big gap
- 🆕 The Transformer Architecture (self-attention, multi-head, positional encoding, Keras build). p5: attention heatmap.
- 🆕 Sequence-to-Sequence Learning (encoder–decoder translation).
- ✨ enrich text-prep / BoW-vs-sequence / embeddings.

**Phase 06 — Generative Deep Learning** (Ch12)
- 🆕 Text Generation (sampling / temperature). p5: temperature→randomness.
- 🆕 DeepDream. Visual.
- 🆕 Neural Style Transfer. Visual.
- ✨ enrich VAE / GANs with Chollet's Keras implementations.

**Phase 07 — Reinforcement Learning** — Chollet doesn't cover RL. Skip.

**Phase 08 — Scaling & Deploying** (Ch13)
- 🆕 Hyperparameter Tuning with KerasTuner.
- 🆕 Mixed Precision & Multi-GPU Training (or fold into existing Distributed Training).
- ✨ enrich tf.data / custom training loops.

**Optional capstone** (Ch14): Limitations & Future of Deep Learning.

Total: ~15–17 new pages + enrichment of ~15 existing.

## Per-page kit (additive, non-destructive)

Book-simplified prose, 1 mermaid, p5 where genuinely visual, "From the book (Chollet)" callout,
2–3 DataCampExercise (exact expected output; Keras kept tiny / numpy-illustrated where training is
heavy so exercises run offline in the browser sandbox), Next pointer. Keep existing good content.

## Conventions & gotchas (from repo memory)

- Mermaid labels with `()` `<` `>` `/` `:` MUST be double-quoted; `<br/>` ok.
- p5 fences: ` ```p5 title="" desc="" height="" `; background `background(13,17,23)`; amber #ffd343 / blue #4b8bbe.
- **DataCampExercise `hint`/`code`/`solution`/`sct` are JS template literals — inline backticks MUST be escaped `\``** (this bug breaks the MDX build; `astro check` won't catch it).
- Import depth `../../../../components/DataCampExercise.astro` (verify vs sibling).
- New files: frontmatter title/description/sidebar.order (next free order in phase folder; DL uses 400s).
- Never rename files; content .mdx only; no build-config edits.
- Route slugs: `" - "` → `---`, `" & "`/`&` stripped (double hyphen). See memory `mdx-authoring-gotchas`.

## Execution

`content-author` subagents, one per phase, parallel waves. Each gets: this spec's kit, its Chollet
chapter file(s), and its new/enrich page list. Order new pages logically within each phase.

## Verification

- Per-file MDX compile sweep with `@mdx-js/mdx` (catches hint-backtick + JSX errors `astro check` misses).
- `astro check` 0 errors.
- Mermaid label-quoting scan.
- Dev-server render spot-check of new pages (HTTP 200 + p5/viz panels).
- No commit.

## Out of scope

RL (not in book), build config, component code, the Machine Learning section.

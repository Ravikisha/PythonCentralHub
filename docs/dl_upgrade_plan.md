# Deep Learning module — enhancement plan

Status: **complete.** All nine waves shipped, plus every candidate page in §3
and the PyTorch gap from §1. `torch 2.13.0+cpu` was installed on 2026-08-08 so
page 405.9 could measure framework agreement rather than assert it; every number
on that page comes from both libraries running on this machine.
Baseline measured 2026-08-04 with `python scripts/dl_audit.py`.

---

## 1. Where the module stands today

| Measure | Deep Learning (now) | Machine Learning (shipped) |
| --- | --- | --- |
| Pages | 63 (55 concept + 8 overview/landing) | 89 (76 concept + 13) |
| Words | 113,535 | 377,532 |
| Words per concept page | ~2,000 | ~4,300 |
| Exercises | 165 (3 per page, fixed) | 440 (5–6 per page) |
| Quizzes | **0** | 89 |
| Generated figures (`<Figure>`) | **0** | 213 (422 committed SVGs) |
| KaTeX display math | **0** | 330 |
| KaTeX inline math | **0** | thousands |
| p5 sketches | 40 (on 55 concept pages) | 85 |
| mermaid diagrams | 74 | 98 |
| `## Pitfalls` sections | **0** | 76 |
| `## Recap` sections | **0** | 76 |
| Framework coverage | Keras/TF only (1,233 Keras refs, **0 PyTorch**) | n/a |

Sidebar orders are unique and use a fractional convention (`401.5`, `473.3`), so
new pages insert without renumbering neighbours.

### The five real gaps

1. **No mathematics at all.** Deep learning is the most derivation-heavy topic in
   the site and there is not one `$…$` span in 63 pages. Backprop is explained
   with a prose chain rule; softmax, cross-entropy, attention, the ELBO and the
   diffusion objective appear only as code.
2. **No measured evidence.** Pages assert ("ReLU trains faster", "batch norm
   helps") without a number attached. Sections titled *Visualize it* (39 of them)
   describe a plot in prose instead of showing one — there is no figure pipeline
   output for this module.
3. **No self-check.** Zero quizzes; no Pitfalls or Recap sections. The
   Mini-checkpoint sections (48) are prose questions with no answers.
4. **Thin exercises.** Exactly 3 per page, and most are configuration echoes —
   *set `momentum=0.9`, print `momentum`* — rather than a computation that
   teaches something. Every one does carry an expected-output block, so the
   format is right and only the content needs raising.
5. ~~**Single framework.** Everything is `tf.keras`. PyTorch is the dominant
   research and jobs framework and appears nowhere.~~ **Closed** by page 405.9,
   *The Same Network in PyTorch*: the same architecture built in both libraries,
   given identical weights, agreeing on gradients to 7.45e-09 and on test
   accuracy to four decimal places. The module stays Keras-first deliberately —
   the page's job is to show what transfers, and to measure the three defaults
   (initialiser spread 2.27x apart, zeroed against random biases, Adam epsilon
   1e-7 against 1e-8) that make two "identical" models diverge.

---

## 2. Target shape for a Deep Learning concept page

Same contract the ML module now meets, adapted to the subject:

- `## What you'll learn` — 4–6 bullets naming the measurements on the page.
- Intuition, then **the maths**: forward pass, loss, and gradient written out in
  KaTeX with every symbol defined. Derivations end in something checkable.
- **A worked example by hand** with small numbers, followed by the same
  computation in code so the two agree to 4 decimals.
- **From scratch in NumPy**, then the framework version — with a
  `np.allclose` / gradient-check that proves they match.
- 2–4 **generated figures** (`<Figure>`, dark + light SVG from
  `scripts/figures/dl/…`) and 1–2 **p5 sketches** for anything with a knob:
  learning rate, temperature, receptive field, attention weights.
- One **mermaid diagram** for shapes/data flow (tensor shapes through a network,
  a training loop, an attention head, a serving path).
- `## Pitfalls`, `## Recap`, one `<Quiz>` of 4–5 questions, 5–6 exercises whose
  expected output was produced by running the solution, `## Next`.
- Every reported number is measured on this machine and reproducible; when a
  technique fails to help, the page says so with the number.

**Honesty rules carried over from ML.** Report seed spread, not single runs
(`_dl.repeat` exists for exactly this). Never quote a training curve without
saying how many epochs and rows produced it. Where a famous claim does not
reproduce at laptop scale, state that plainly rather than repeating folklore.

---

## 3. Waves

Each wave = one phase, ending with `dl_audit.py` clean for those pages, both
checkers passing (`node scripts/mdxcheck.mjs`, `python scripts/check_docs.py`), and
figures rendered and committed.

| Wave | Phase | Pages | Headline work |
| --- | --- | --- | --- |
| 0 | Infrastructure | — | **done** (§5) |
| 1 | 01 Neural Network Foundations | 9 + overview | Perceptron limit proof, softmax/cross-entropy derivation, tensor-shape diagrams, activation-depth measurements |
| 2 | 02 Training Deep Networks | 8 + overview | Backprop derived and gradient-checked, optimiser comparison across seeds, BN/dropout ablations, LR-schedule sweep |
| 3 | 03 Computer Vision | 8 + overview | Convolution arithmetic ($O$, padding, stride, receptive field), parameter-count tables, augmentation ablation, Grad-CAM from scratch |
| 4 | 04 Sequence Models | 4 + overview | BPTT unrolled, gradient decay measured per timestep, LSTM gate walkthrough, honest baseline comparison for forecasting |
| 5 | 05 NLP & Transformers | 7 + overview | Attention from scratch with the $QK^\top/\sqrt{d_k}$ derivation, positional encoding, multi-head shapes, tokenizer internals |
| 6 | 06 Generative | 7 + overview | Autoencoder bottleneck measurements, VAE ELBO derived, GAN training dynamics, diffusion forward/reverse process |
| 7 | 07 Reinforcement Learning | 3 + overview | Bellman equations, tabular Q-learning on a hand-written gridworld, policy-gradient derivation, DQN stability ablations |
| 8 | 08 Scaling & Deploying | 8 + overview | Throughput/latency measurements, mixed-precision numerics, quantisation error, serving contract tests |
| 9 | Landing + cross-links | 1 | Module landing rebuilt with a per-phase measured number, phase dependency graph, module quiz |

### Candidate new pages

Only the ones that close a teaching gap rather than pad the count:

| Order | Page | Why |
| --- | --- | --- |
| 405.7 | Autograd from Scratch (reverse-mode in 60 lines) | Makes `GradientTape`/`backward()` stop being magic |
| 411.5 | Loss Functions and What They Assume | MSE vs cross-entropy vs focal, and the gradient each implies |
| 423.5 | Normalisation Beyond Batch (Layer, Group, RMS) | Batch norm alone cannot explain transformers |
| 428.5 | Vision Transformers | The current default architecture is absent |
| 434.5 | Attention Before Transformers (additive/Bahdanau) | The bridge Phase 04 → 05 is missing |
| 446.5 | Attention from Scratch (single head, NumPy) | The transformer page currently starts at `MultiHeadAttention` |
| 447.5 | Fine-Tuning and Parameter-Efficient Tuning (LoRA) | How anyone actually uses a pretrained model in 2026 |
| 447.7 | Tokenizers (BPE from scratch) | Every LLM number depends on it |
| 457.5 | Evaluating Generative Models | FID/perplexity/human eval, and what each misses |
| 463.5 | Actor-Critic and PPO (intro) | RL phase stops one step too early |
| 476.5 | Inference Cost: Quantisation, Distillation, Batching | The deployment phase never prices a forward pass |
| 477 | Capstone: MNIST-to-Deployment, measured end to end | Phase 12 of ML is the most useful phase; DL has no capstone |
| 477.3 | Capstone: Fine-Tune a Small Text Classifier | Decision-first, cost-aware |
| 477.6 | Capstone: A Tiny Diffusion Model | Generative end-to-end at laptop scale |

That is **14 new pages**; the wave plan works with any subset.

---

## 4. What can be measured on this machine

Verified 2026-08-04 (TF 2.21.0, Keras 3.15, CPU only, no GPU):

| Workload | Wall clock |
| --- | --- |
| `import tensorflow` | 4.7s |
| MNIST load (cached after first run) | 3.7s |
| 64-unit MLP, 10k rows, 3 epochs | 1.2s |
| 16-filter CNN, 6k rows, 2 epochs | 1.2s |
| 18-run activation × depth study (the proof figure) | 98s |

Installed: `numpy 2.4.6`, `scipy 1.17.1`, `sklearn 1.9.0`, `pandas 3.0.3`,
`matplotlib 3.11.0`, `tensorflow 2.21.0`, `keras 3.15.0`, `PIL 12.2.0`.
**Missing:** `torch`, `transformers`, `gymnasium`, `jax`, `cv2`.

Consequences for the plan:

- Everything in Phases 01–04, 06 and 08 is measurable today at MNIST/CIFAR-10
  scale, in seconds per run.
- **Transformers/NLP** pages need no Hugging Face: attention, positional
  encoding and BPE are written from scratch in NumPy, which is the better lesson
  anyway. A page that wants a pretrained checkpoint would need `transformers`.
- **RL** pages use a hand-written gridworld and a NumPy CartPole rather than
  `gymnasium`, so they stay reproducible and installable-free.
- **PyTorch coverage required installing `torch`.** Done on 2026-08-08: the CPU
  wheel is 117 MB and `torch 2.13.0+cpu` coexists with TensorFlow 2.21 in the
  same interpreter, so page 405.9 runs both frameworks in one process and
  compares them directly. `torch.get_num_threads()` reports 4.

---

## 5. Setup already in place

```
scripts/dl_audit.py                          # targets + per-page gap report
scripts/figures/dl/_dl.py                    # seeding, datasets, train/repeat,
                                             # softmax/CE, numeric_gradient
scripts/figures/dl/phase-01-foundations/     # 8 phase folders, one per DL phase
scripts/figures/dl/phase-02-training/
scripts/figures/dl/phase-03-vision/
scripts/figures/dl/phase-04-sequences/
scripts/figures/dl/phase-05-nlp-transformers/
scripts/figures/dl/phase-06-generative/
scripts/figures/dl/phase-07-rl/
scripts/figures/dl/phase-08-scaling/
public/images/dl/phase-01-foundations/activation-functions/   # 4 SVGs, rendered
```

`_dl.py` deliberately returns plain Python from every helper — no live TensorFlow
objects reach a figure module, so figures stay reproducible and cheap to re-render.

**Pipeline proven end to end** with
`scripts/figures/dl/phase-01-foundations/activation-functions.py`:
`npm run figures` (or `python scripts/figures/build.py dl`) renders
`activation-curves` and `activation-depth` as dark + light SVG pairs. The second
figure is a real 18-run study (3 activations × 2 depths × 3 seeds), which is the
template every later figure follows: compare distributions, print the numbers on
the bars, and let the result be whatever it is.

Its output, MNIST validation accuracy after 4 epochs on 8,000 rows:

| Activation | 2 hidden layers | 8 hidden layers |
| --- | --- | --- |
| sigmoid | 0.7402 (0.7295–0.7590) | **0.1563** (0.1025–0.1865) |
| tanh | 0.8773 (0.8745–0.8815) | **0.8782** (0.8670–0.8865) |
| ReLU | 0.8803 (0.8785–0.8815) | 0.8502 (0.8295–0.8625) |

Three findings the current page asserts none of, and one that contradicts the
usual story: sigmoid at depth 8 collapses to **0.1563** — barely above the 0.10
you get by guessing — which is the vanishing-gradient claim as a number rather
than a warning. tanh at depth 8 does *not* degrade (0.8782 against 0.8773
shallow) and at that depth it beats ReLU (0.8502). "Always use ReLU" is folklore
at this scale, and the honest page says so with the spread attached.

Reusable components already on the site: `Figure.astro`, `Quiz.astro`,
`AlgorithmCard.astro`, `DataCampExercise.astro`, p5 via ` ```p5 ` fences,
mermaid via ` ```mermaid ` fences, KaTeX via `remark-math` + `rehype-katex`.

### Two checker bugs fixed while establishing the baseline

`scripts/check_docs.py` reported six problems against this module and all six
were false alarms — the kind that makes a team stop trusting its own gate:

1. **Fractional sidebar orders rejected.** The rule matched `order:\s*(\d+)`, so
   the four pages numbered `401.5`, `405.5`, `473.3` and `473.6` were reported as
   having no order at all. Now parsed as floats, and duplicate detection still
   works across them.
2. **Indented code fences not stripped.** A fence inside a numbered list item
   starts at column 3, so `^```` missed it and the `showLineNumbers{1}` on that
   fence was reported as a prose brace (twice on *Transfer Learning*). The strip
   now tolerates leading whitespace.

Verified against every module: Deep Learning 6 problems → **0**; Machine Learning
0 → 0; Mathematics 13 → 13 and DSA 12 → 12, both unchanged, so neither fix hides
anything. (Those remaining findings are pre-existing and belong to those modules'
own cleanups — DSA has three genuine duplicate sidebar orders.)

---

## 6. Per-wave definition of done

1. `python scripts/dl_audit.py --gaps` lists none of the wave's pages.
2. `node scripts/mdxcheck.mjs "src/content/docs/Deep Learning"` — 0 failures.
3. `python scripts/check_docs.py "src/content/docs/Deep Learning"` — no problems.
4. Every p5 block parses (`node --check` on each extracted sketch).
5. Figures rendered, both themes present, and *looked at* before committing.
6. Every exercise solution run; expected output pasted from the real run.
7. Numbers in prose traceable to a script in `scripts/figures/dl/…`.

---

## 7. Decisions (settled 2026-08-04)

1. **Scope** — upgrade all 55 existing concept pages **and** add all 14 new pages.
   Final module: 69 concept pages + 8 phase overviews + 1 landing = **78 pages**.
2. **Framework** — **Keras/TensorFlow only.** No `torch` install, so every line
   of code on every page can be run and verified on this machine. Where the
   framework hides the mechanism, the page adds a **from-scratch NumPy**
   implementation with a gradient check rather than a second framework.
3. **Depth** — **full ML-grade**: ~2,500–3,500 words, KaTeX derivations,
   hand-worked numeric example, 2–4 generated figures, 1–2 p5 sketches, mermaid,
   pitfalls, recap, quiz, 5–6 verified exercises per page.
4. **Order** — **foundations first, Phase 01 → 08**, then the landing page.
   Backprop is derived and gradient-checked before anything builds on it.

### Projected end state

| Measure | Now | Target |
| --- | --- | --- |
| Pages | 63 | 78 |
| Words | 113,535 | ~230,000 |
| Exercises | 165 | ~380 |
| Quizzes | 0 | 70 |
| `<Figure>` / committed SVGs | 0 / 0 | ~160 / ~320 |
| p5 sketches | 40 | ~85 |
| mermaid | 74 | ~120 |
| KaTeX display math | 0 | ~250 |

Per-wave cost is dominated by figure rendering, since several figures train
models: budget seconds per run and a few minutes per phase build, and keep any
study that needs longer out of the build and in the prose as a reported number
with its script named.

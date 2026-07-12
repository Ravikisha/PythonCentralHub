# Content Plan — Python Central Hub

**Goal:** improve existing pages and add new content that *shows, not just tells* —
using the site's visualization system (mermaid diagrams, p5.js sketches, framed
code blocks) — and put every page in a deliberate, correct order.

Owner: content + UI. Last planned: 2026-07-10.

---

## 1. Where we are today

| Section | Pages | Phases | mermaid | p5.js |
|---|---:|---:|---|---|
| Projects | 203 | Beginners / Intermediate / Advance | some | 0 |
| Tutorials (core Python) | 167 | 25 topic folders | some | 0 |
| Data Analytics | 120 | 10 phases | some | 0 |
| Flask Tutorials | 98 | 9 phases | some | 0 |
| Machine Learning | 68 | 10 phases (Phase 2 missing locally — see §7) | some | 0 |
| Software Testing & Quality | 57 | 7 phases + projects | some | 0 |
| Automation & Scripting | 51 | 6 phases | some | 0 |
| Guides | 8 | — | — | 1 |
| Reference | 1 | — | — | 0 |
| **Total** | **777** | | **120 files** | **1 file** |

**Signal:** mermaid is already used widely (120 files); **p5.js is used on exactly one
page** (the new `guides/visualizations.mdx`). The biggest, cheapest win is adding
interactive p5 sketches to the pages where a live model beats a static image —
algorithms, data structures, ML, and data-analytics visualization.

The visualization system (instrument-panel chassis: mermaid + p5 + code) is built and
documented — see the `design-system` memory and `src/styles/viz.css`. This plan is about
*using* it across the library.

---

## 1b. Bug fix — broken mermaid sweep (2026-07-12)

Discovered live "Syntax error in text (mermaid 10.9.6)" on pages with **unquoted special
characters in mermaid node labels** — `A[Underfit (too simple)]`, `[Feature <= threshold?]`,
`[path => anomaly]`. astro check does NOT catch these (client-render errors only). Swept all
mermaid blocks and fixed **21 files (~24 diagrams)** by quoting labels → `A["Underfit (too
simple)"]`. `<br/>` line-breaks left intact (valid). See the `repo-gotchas` memory for the
scan/fix method. Rule going forward: quote any label with `()`, `<`, `>`, `/`, `:`.

## 2. Conventions (apply everywhere)

Pick the right instrument for the job:

- **Code block** — the exact syntax being taught. Always. Highlight the line that matters
  with `{n}` / `{n-m}` (renders the blue rail).
- **mermaid** — *structure and flow*: control flow, class/inheritance graphs, request
  lifecycles, pipelines, state machines, decision trees, ER diagrams. Anything where the
  reader needs to see how parts connect.
- **p5.js** — *behavior over time or space*: anything that moves, iterates, or is spatial.
  Sorting/search animations, recursion trees drawing themselves, gradient descent walking
  downhill, k-means re-clustering, a physics loop, a distribution filling in as samples
  arrive. If a static picture would need a "imagine this animating" caption, use p5.
- **DataCampExercise** — hands-on practice (see the `new-tutorial` skill). Keep 3 per
  tutorial page.

Authoring syntax lives in `guides/visualizations.mdx`. Every sketch must:
run in ordinary global p5 style, use the brand palette (`background(13,17,23)`, blue
`(75,139,190)`, amber `(255,211,67)`), be sized `createCanvas(w, h)` with `h` matching the
fence `height`, and read fine paused (reduced-motion starts paused).

**Quality gates for every batch:** `npx astro check` (0 errors), `theme-check` (tokens
only), reduced-motion honored, Windows-safe filenames (no `" : * ? < > |`), and **never
`git add -A`** (would stage the deletion of the ML Phase-2 quote files). Do not commit
unless asked.

---

## 3. Per-section plan

Each section lists: **improve** (what to strengthen on existing pages) and **add** (new
pages and the viz that justifies them).

### 3.1 Tutorials — core Python (167 pages) — *highest priority for p5*

**Improve:** add a `## Visualize it` block with one p5 sketch to the pages where behavior is
the lesson; add a mermaid flow to control-flow and OOP pages; ensure every page ends with 3
exercises.

| Topic folder | Add mermaid | Add p5.js sketch |
|---|---|---|
| Python Control Statement | if/elif/else + loop flowcharts | loop counter stepping; `break`/`continue` trace |
| Python Function | call/return flow, scope diagram | recursion tree drawing itself (factorial/fib) |
| Python OOPS | class/inheritance/MRO graphs | object instances spawning; composition vs inheritance |
| Python List / Tuple / Set / Dict | — | list vs set membership (O(n) scan vs hash); dict bucket viz |
| Python Iterators & Generators | lazy pipeline flow | values pulled one-at-a-time on demand |
| Python Comprehensions | — | filter→map pipeline animating over a list |
| Python Threading / MultiProcessing / Asyncio | thread lifecycle + GIL, event-loop diagram | concurrent tasks on a timeline; event loop scheduler |
| Python Strings | — | slicing indices highlighting a string |
| Python Errors/Exceptions | try/except/finally flow | exception propagation up the call stack |
| Modern Python | — | (code-heavy; keep diagrams) |

**New pages to add** (each with a p5 sketch as the hero):
- *Sorting visualized* — bubble/insertion/merge/quick, animated, side-by-side.
- *Searching visualized* — linear vs binary search on a sorted array.
- *Recursion visualized* — the call stack growing and unwinding.
- *Big-O, felt* — operation counts growing as `n` grows, plotted live.

### 3.2 Data Analytics (120 pages) — *p5 fits the viz phases natively*

**Improve:** Phases 5–7 (Matplotlib / Seaborn / Plotly) teach charts — add a p5 sketch that
builds the same chart type interactively so readers grasp the *encoding* before the library
API. Phase 8 (Statistics) is the richest p5 target.

| Phase | Add |
|---|---|
| 4 — Preprocessing/Cleaning | mermaid: cleaning pipeline (load→impute→encode→scale) |
| 5 — Matplotlib | ✅ p5: chart anatomy, pie slices, histogram binning (Anatomy of a Plot, Pie Chart, Histogram) |
| 6 — Seaborn | p5: a distribution histogram filling as samples arrive |
| 7 — Plotly | mermaid: interactivity event flow |
| 8 — Statistics | ✅ p5: **CLT** (sample-means bell), 3 distributions (normal/binomial/Poisson), correlation scatter; hypothesis-testing decision mermaid |
| 9 — SQL | ✅ mermaid: INNER vs LEFT join (Joins for Analytics) |

### 3.3 Machine Learning (68 pages) — *strongest p5 payoff*

**Improve:** algorithm pages currently rely on prose/static images; ML concepts are motion.

| Phase | Add |
|---|---|
| 1 — Foundation | ✅ mermaid: the ML lifecycle (data→train→eval→deploy→monitor loop) (The ML Lifecycle) |
| 3 — Regression | ✅ p5: **gradient descent** down the loss curve + **line-of-best-fit** fitting live (Gradient Descent Explained, Simple Linear Regression) |
| 4 — Classification | ✅ p5: **k-NN** neighborhood vote (K-Nearest Neighbors); decision-tree split mermaid (Decision Trees) |
| 5 — Ensemble | mermaid: bagging vs boosting; p5: many weak trees voting |
| 6 — Unsupervised | ✅ p5: **k-means** re-assigning + moving centroids (K-Means Clustering Algorithm) |
| 7 — Optimization | ✅ p5: underfit / good-fit / overfit comparison (Underfitting vs Overfitting) |
| 8 — Deep Learning | ✅ p5: **perceptron** (weighted sum → activate), **activation-function** curves (ReLU/sigmoid/tanh); MLP topology mermaid |
| 9 — NLP | mermaid: tokenize→embed→model pipeline |
| 10 — MLOps | mermaid: CI/CD + model-serving architecture |

*Restore Phase 2 (Data Preprocessing) first — see §7 — then add a scaling/normalization p5.*

### 3.4 Flask Tutorials (98 pages)

Flask is request/response flow → **mermaid-heavy**, minimal p5.

**✅ DONE (batch 5, 2026-07-10)** — all 9 phases given a mermaid diagram (one key page each):

| Phase | Add mermaid |
|---|---|
| 1 — Fundamentals | ✅ WSGI request lifecycle (First Flask Application) |
| 2 — Routing | ✅ URL → view resolution (Basic Routing) |
| 3 — Jinja2 | ✅ template render pipeline (Introduction to Jinja2) |
| 4 — Forms | ✅ Post/Redirect/Get (Form Validation) |
| 5 — SQLAlchemy | ✅ User/Post ER classDiagram (Creating Database Models) |
| 6 — Auth | ✅ login/cookie sequenceDiagram (Introduction to Flask-Login) |
| 7 — Architecture | ✅ create_app() factory flow (Application Factory Pattern) |
| 8 — REST APIs | ✅ HTTP methods → CRUD (Introduction to REST) |
| 9 — Deployment | ✅ Nginx → Gunicorn → Flask topology (Gunicorn Web Server) |

### 3.5 Software Testing & Quality (57 pages)

**✅ DONE (batch 5b, 2026-07-10)** — 7 phases, one mermaid each:

| Phase | Add |
|---|---|
| 1 — Fundamentals | ✅ STLC flow (Intro to SQA) |
| 2 — Levels | ✅ the test pyramid (Test Pyramid Strategy) |
| 3 — unittest | ✅ setUp→test→tearDown lifecycle (Intro to unittest) |
| 4 — pytest | ✅ fixture setup→yield→teardown (Pytest Fixtures) |
| 5 — API/Web | ✅ request→assert loop (API Testing Fundamentals) |
| 6 — Static analysis | ✅ format→lint→typecheck gate (Intro to Code Linting) |
| 7 — CI/CD | ✅ push→install→lint→test→build→deploy (Intro to CI) |

### 3.6 Automation & Scripting (51 pages)

Mostly code + mermaid flow (file ops, scraping pipelines, scheduling).

**✅ DONE (batch 5c, 2026-07-10)** — 6 phases, one mermaid each:

| Phase | Add mermaid |
|---|---|
| 1 — OS/Filesystem | ✅ scan→select→zip→store (Automating File Backups) |
| 2 — Office | ✅ read→build→save .docx (Word Documents with python-docx) |
| 3 — Web/Scraping | ✅ fetch→parse→extract→store + retry (Price Tracker Bot) |
| 4 — Communication | ✅ compose→connect→login→send (Sending Emails with smtplib) |
| 5 — GUI/System | ✅ locate→move→click→verify (Controlling Mouse) |
| 6 — Scheduling | ✅ try→log→retry/backoff→give up (Handling Errors in Long-Running Scripts) |

### 3.7 Projects (203 pages)

Too many to touch all. **Improve** the flagship projects per tier with an architecture
mermaid diagram + a `FileCode` of the entry point, and add a p5 sketch to any project that
is itself visual (games, generators, simulations, data dashboards).

**✅ STARTED (batch 6, 2026-07-10)** — architecture mermaid added to 9 flagship projects:
- Beginners: basicwebscrapper (scrape flow), calculatorgui (GUI event loop), currencyconverter (API flow).
- Intermediate: chat-application-socket (client/server sockets), file-encryption-tool (encrypt/decrypt), ecommerce-website (Flask→SQLAlchemy).
- Advance: advanced_password_manager (KDF→encrypted vault), advanced_chatbot_with_nlp (NLP pipeline), advanced_recommendation_system (collaborative filtering).

**Interactive p5 game demos (2026-07-10):** added *playable* p5 to visual projects —
**paint** (`## Try it here`: click-drag to draw, colour swatches, C to clear) and
**multiplayer-tic-tac-toe** (click cells, X/O alternate, win detection, click to reset).
These use event hooks (mousePressed/mouseDragged/keyPressed) + redraw() so they work even
when the sketch isn't looping.

More interactive demos (2026-07-10): **binarytodecimal** (click bits to flip → live decimal
with place values), **rockpaperscissors** (click a move, play the CPU, running score),
**dicerolling** (click to roll two pip dice + total). All `## Try it here`, noLoop+redraw.

More interactive demos (round 2): **guessthenumber** (click a 1–100 bar, higher/lower,
narrowing range), **calculatorgui** (a *working* button calculator — pairs with its
architecture mermaid). 10 interactive demos now (paint, tic-tac-toe, binary, RPS, dice, guess, calculator,
anagram, **blackjack** playable hand, **analog clock** live-ticking). Live canvas-build
confirmed on tic-tac-toe and the clock (canvas:1, 0 errors).

Remaining: the other ~187 project pages (sampling done; extend as desired), + more p5 game
demos (blackjack, hangman, snake-style, simulations).

### 3.8 Guides + Reference

- Keep `visualizations.mdx` as the canonical how-to (already done).
- **Add** a *"Reading this site"* guide explaining the panels, exercises, and playground.
- Reference: expand beyond `contact` — add a *viz cookbook* (copy-paste p5 + mermaid
  recipes for authors).

---

## 4. Page ordering

### 4.1 Top-level section order (fixed in `astro.config.mjs` sidebar array — correct)

`Guides → Tutorials → Flask Tutorials → Automation → Data Analytics → Machine Learning →
Testing → Projects → Reference`

Recommended tweak: this ordering is roughly beginner→advanced except Automation sits before
Data Analytics/ML. Keep as-is (it groups "scripting" with core skills); revisit only if
analytics/ML should lead.

### 4.2 Guides — FIX the collision (applied as part of this setup)

Current orders have `3` duplicated (Courses + Youtube) and `7` missing. Canonical order:

| order | page |
|---:|---|
| 1 | Welcome to Python Central Hub (Home) |
| 2 | The Python Library (Book) |
| 3 | The Python Courses (Courses) |
| 4 | Python Youtube Channels (Youtube) |
| 5 | Visual Studio Code Setup (VSCode) |
| 6 | Python Roadmap (Roadmap) |
| 7 | Python Cheat Sheet (CheetSheet) |
| 8 | Interactive Visualizations |

### 4.3 Phase folder ordering — DONE (batch 1, 2026-07-10)

**How Starlight actually orders autogenerated groups** (verified empirically, not by docs):
a group's position = the **minimum `sidebar.order`** among its pages; ties break
**alphabetically by slug**. So the "Phase-10 before Phase-2" problem was really the
alphabetical tie-break on equal min-orders: `phase-1`, `phase-10`, `phase-2`, … Zero-padding
the folder names fixes the tie-break (`phase-01` … `phase-10` sort numerically).

Applied to **Data Analytics** and **Machine Learning** only (the two sections that reach
Phase 10). Flask/Testing/Automation stop at 9 → single digits already sort correctly → left
alone to avoid needless slug churn.

- DA: `Phase-1-…` → `Phase-01-…` (hyphen format). ML: `Phase 1 - …` → `Phase 01 - …`
  (space format). Phase-10 unchanged. Filesystem `mv` (not `git mv`) to keep the index clean.
- **Second bug found + fixed:** DA Phase-06 had a rogue overview page at `order: 0`, making
  its group float out of place (all other phases have min-order 1). Shifted Phase-06 pages
  `+1` (overview now `order: 1`) so its min matches the rest. Result: DA groups now render
  `phase-01 … phase-10` in perfect numeric order (confirmed against the live sidebar); ML
  likewise.
- Only inbound link needing a fix was `index.mdx` (DA phase-1 anaconda link) → repointed to
  `phase-01-…`. Grep confirms no other absolute or relative phase links remain unpadded.
- ML **Phase 02** is still absent locally (Windows quote-file constraint, §7); when restored
  on Linux, name it `Phase 02 - …` to keep the scheme.

*Remaining ordering work (future):* the 5 pages with no `order` (§4.4) and any per-phase
renumbering as content is added. Do NOT pad the ≤9-phase sections — no bug there.

### 4.4 Within-phase page ordering

Pages already use `sidebar.order` (772/777). Convention going forward: **order = position
within its phase**, starting at 1, no gaps, overview page = 1. When inserting a page, renumber
the tail rather than using fractional/─gap orders. The 5 pages missing `order` should get one.

### 4.5 New pages — where they slot

- Tutorials "Sorting/Searching/Recursion/Big-O visualized" → new folder
  `tutorials/Algorithms Visualized/` placed after "Python Functional Programming",
  orders 1–4.
- Each section's new mermaid/p5 additions go *inside existing pages*, no new order needed.
- ML restored Phase 2 keeps its original position (order 2 among phases).

---

## 5. Execution plan (incremental batches)

Each batch is independently shippable and ends with the quality gates in §2.

1. **Ordering fixes** (this pass): guides order (done), then phase-folder zero-padding +
   link re-check. Small, high-value, low-risk.
2. **Tutorials p5 wave** — the four new "visualized" pages + control-flow/function/OOP/
   recursion sketches. Highest learner payoff.
3. **ML p5 wave** — gradient descent, k-means, decision boundary, neuron/forward-pass.
   Restore Phase 2 first.
4. **Data Analytics** — statistics (CLT, regression), chart-encoding sketches, SQL join
   diagrams.
5. **Flask + Testing + Automation mermaid wave** — flow/architecture diagrams per phase.
6. **Projects** — architecture diagrams for flagship projects; p5 for visual ones.
7. **Guides/Reference** — "Reading this site" + viz cookbook.

Rough sizing: batches 2–4 are the bulk of new p5 authoring (~25–35 sketches). Batch 5 is
~40 mermaid diagrams. Use the `content-author` agent for prose/exercise work and
`starlight-ui` for any component/style needs; author sketches directly and verify each with
the dev server + a screenshot.

---

## 6. Definition of done (per page touched)

- Right instrument used (code / mermaid / p5) per §2.
- p5 sketch: brand palette, sized to fence, reads paused, no console errors.
- mermaid: has `title` + `desc`; renders on the themed panel.
- Code: key line highlighted; runs in the playground.
- 3 DataCampExercises if it's a tutorial page.
- `astro check` clean; `theme-check` clean; reduced-motion honored.

---

## 7. Known constraint — ML Phase 2 (Windows)

`Machine Learning/Phase 2 - Data Preprocessing (The "Real" Work)/` and one Phase-6 file have
literal `"` in their names. Git cannot check them out on Windows; they build on Linux CI.
Before adding Phase-2 content: restore them on a Linux runner (or rename to Windows-safe
titles — a content decision), and **never `git add -A`** on Windows or you will stage their
deletion. See the `repo-gotchas` memory.

# Data Analytics Section Enrichment — from *Python for Data Analysis* (Wes McKinney, 3rd ed)

**Date:** 2026-07-12
**Status:** Approved (shape), executing
**Source:** `Python-for-Data-Analysis.pdf` (condensed 3rd ed, all 13 chapters; text extracted to `scratchpad/book/chNN.txt`)

## Goal

Enrich the 117-page Data Analytics section (`src/content/docs/Data Analytics/`, 10 phases) with
the book's beginner-friendly explanations plus the site's visualization surfaces. Learners should
understand concepts better through simple prose, diagrams, live visualizations, runnable code, and
practice exercises.

## Source-to-phase mapping (book coverage is uneven → tiered treatment)

| Tier | Phases | Book chapters | Treatment |
|------|--------|---------------|-----------|
| **A — deep, book-driven** | P01 Setup, P02 NumPy, P03 Pandas, P04 Cleaning, P05 Matplotlib, P10 Projects | Ch1, 4, 5, 6, 7, 8, 9, 10, 11, 13 | Rebuild prose in book's plain voice + full enrichment kit. Replace weak/thin existing content. |
| **B — enrich, general + book scraps** | P06 Seaborn, P07 Plotly, P08 Stats, P09 SQL | Ch9 (seaborn light), Ch12 (stats light); rest thin | Apply template + viz kit. Book where it touches, standard knowledge elsewhere. |

## Per-page enrichment kit (additive — keep strong existing content, replace weak)

Consistent template per page:

1. **Intro** — what + why in simple terms (book's beginner framing).
2. **Concept sections** — book explanations, simplified for learners.
3. **Mermaid diagram** — 1 concept/flow diagram in `.pch-viz` chassis.
4. **Code blocks** — runnable, `title=`'d, book-style examples.
5. **p5.js visualization** — *only where genuinely visual* (~40% of pages): array shape/broadcasting,
   dtype memory layout, distributions, plot anatomy, groupby split-apply-combine, merge/join,
   time resampling, outliers/IQR. Skip where viz adds nothing.
6. **"From the book" callout** — one McKinney insight/gotcha (`:::tip` / `:::note`).
7. **DataCamp exercises** — 2–3 fill-in-the-blank (`lang`, `hint`, `code`, `solution`, `sct`, `height`).
8. **Next** pointer.

Mermaid + book-insight + exercises on every touched page; p5 only where the concept is spatial/visual.

## Conventions & gotchas to honor (from repo memory)

- **Mermaid labels** containing `()`, `<`, `>`, `/`, `:` **must be quoted** (`A["Underfit (too simple)"]`),
  else client-side render error. `<br/>` stays unquoted.
- **p5 fences**: ` ```p5 title="" desc="" height="" ` → global-style sketch, instance-mode runtime,
  reduced-motion aware (starts paused). Background `background(13, 17, 23)` = editor ink.
- **DataCampExercise import** path is relative and depth-correct
  (`../../../../components/DataCampExercise.astro` from a Phase page).
- **Filenames**: no `"` `<` `>` (Windows-invalid). Editing existing files only → safe. Keep `sidebar.order`.
- Content edits only — no `astro.config.mjs` / build-config changes.
- Code fences use `title="..."` and `showLineNumbers{1}`.

## Execution

- Dispatched to **`content-author`** subagents, **one phase per agent**, parallel batches.
- Each agent receives: this enrichment kit, the relevant `scratchpad/book/chNN.txt` chapter text,
  and the list of that phase's page files.
- **Order:** Tier A (P02 → P03 → P04 → P05 → P01 → P10) then Tier B (P08 → P06 → P07 → P09).
- `starlight-ui` consulted only if a new viz needs CSS (unlikely — `.pch-viz` chassis already exists).

## Verification

- `astro check` clean.
- Mermaid label-quoting scanner grep (from repo-gotchas) returns no unquoted `()`/`<`/`>` in labels.
- Spot-render a few enriched pages in dev.

## Out of scope

- Build config, theming, component code (chassis already exists).
- The large uncommitted Phase-rename working state on the current branch (untouched; targeted commits only).

## Deliverables

- ~117 pages enriched (Tier A rebuilt, Tier B templated).
- ~117 new mermaid diagrams, ~45 p5 sketches, ~250+ DataCamp exercises.

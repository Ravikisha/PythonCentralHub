# Design Spec — Finish the Instrument-Panel System

**Date:** 2026-07-12
**Author:** Ravi Kishan (with Claude)
**Scope:** Audit-driven visual polish of Python Central Hub. Refine the existing
"Interactive Shell" identity — do **not** re-theme or reinvent it.

---

## 1. Context

Python Central Hub (Astro + Starlight docs site) already ships a strong, coherent
design system — the **"Interactive Shell"**: a live-typing REPL hero, brand tokens
(`--pch-blue`, `--pch-amber`, `--pch-ink`), and an "instrument panel" chassis
(`.pch-viz`) that wraps mermaid diagrams and p5 sketches in a terminal frame
(traffic dots + `>>>` mono tag + branded top rail + editor-ink stage + caption).

A live audit (5 surfaces, desktop + mobile, real rendered screenshots) confirmed the
system is well-executed **except** that it is *incomplete and inconsistent on the
interactive code surfaces*, plus a mobile layout bug and loose landing rhythm.

This spec fixes those defects under one unifying theme: **every code surface shares
the same terminal chassis.** That is the signature move — refining, not reinventing.

## 2. Audit findings (evidence-backed)

| # | Severity | Surface | Defect |
|---|----------|---------|--------|
| 1 | High | Code blocks | Three different chromes coexist. p5 / mermaid / `command` blocks get the dark terminal bar (dots + `>>>` tag). Python **playground** blocks get a light-gray toolbar with generic gray/blue buttons (`--sl-color-accent-high #2563eb`, not brand). The stated "one shared chassis" is broken. |
| 2 | High | Landing (mobile ~400px) | Real horizontal overflow. Media queries fire (bento stacks) yet eyebrow / tagline / code lines / eco-chips bleed past the right edge → horizontal scroll. |
| 3 | Med | Landing (desktop) | Section vertical rhythm is loose — large, uneven gaps between `.pch-section`s dilute the pace. |
| 4 | Med | DataCamp exercises | Vendor light-theme IDE widget clashes with the dark page. Inner iframe is CDN content (not restylable across the boundary); wrapper has only a thin brand rail, no terminal header. |
| 5 | Low | Doc pages (`Feedback.astro`) | "Was this page helpful?" PNG emoji faces read as low-fi against the polished UI. |

**Explicitly out of scope / leave alone:** landing hero + REPL terminal, bento,
tracks grid, mermaid panels, p5 panels, asides, comparison tables. These are strong.

## 3. Approved decisions

- **Tier:** All 5 fixes.
- **Code-chrome unification:** **Full terminal bar** — *every* fenced code block gets
  the dark bar (traffic dots + `>>>` tag), matching p5/mermaid exactly. Accepted
  blast radius: all 300+ doc pages.

## 4. Design

### 4.1 Fix #1 — Unify code-block chrome (the signature move)

**Goal:** code blocks, Python playgrounds, p5 sketches, and mermaid diagrams all read
as one instrument-panel family.

**Header treatment (target = existing `.pch-viz__bar`):**
- Background `#10151c`, bottom hairline, `Source Code Pro` mono.
- Traffic dots (`#ff5f57` / `#febc2e` / `#28c840`).
- A `>>>`-prefixed uppercase tag pill in `--pch-blue`, e.g. `>>> PYTHON`, `>>> TEXT`,
  derived from the block's `data-language`.
- Filename (when present) sits as the bar title, ellipsized.

**Every block gets a bar — including title-less ones.** rehype-pretty-code only emits
`[data-rehype-pretty-code-title]` when a filename/title is set. Recommended mechanism:
a small rehype step (or extension of the existing playground head script) that
guarantees a `.pch-code__bar` header element on every `[data-rehype-pretty-code-figure]`,
carrying the language for the tag. viz.css then styles it. A CSS-only pseudo-element
fallback is acceptable for read-only blocks (no controls to host), but the generated
header is preferred for robustness and to host the playground toolbar consistently.

**Playground toolbar rebrand:** in `src/styles/python-playground.css`, replace the
generic Starlight tokens on `.py-playground__btn`, `.py-playground__icon-btn`, and
`--primary` variants with brand tokens — buttons use `--pch-blue` border / `--pch-surface`
fill, hover → `--pch-amber`, mirroring `.pch-viz__btn`. The toolbar continues to mount
into the bar (`python-playground.js:614`, class `py-playground__toolbar--in-title`);
only its appearance changes, not its mount logic.

**Constraint:** the Python playground's editor/output panels (Monaco, run output) keep
their current structure — only the header bar and control buttons are re-skinned. Do
not rebuild the interactive layer.

**Light theme:** the bar stays dark ("shell output"), consistent with the existing
`.pch-viz` light-theme rule.

### 4.2 Fix #2 — Mobile horizontal overflow

1. **Measure first.** Use CDP `Emulation.setDeviceMetricsOverride` (mobile=true, 390px),
   compare `documentElement.scrollWidth` vs `innerWidth`, and identify the offending
   node(s) via a scan for elements wider than the viewport. (Headless `--window-size`
   crops rather than reflows — do not diagnose from a narrow screenshot alone.)
2. **Fix** the specific culprit — likely candidates: the `.pch-terminal` card min-width,
   un-wrapped `pre`/code lines in the hero terminal, or the `.pch-ecosystem` marquee row.
   Apply `max-width:100%` / `min-width:0` / `overflow` containment as needed; never a
   blanket `overflow-x:hidden` on `body` (that hides the symptom).
3. **Verify** post-fix: `scrollWidth === innerWidth` at 360/390/414px.

### 4.3 Fix #3 — Landing section rhythm

Tune the vertical scale in `src/styles/landing.css`. `.pch-section` currently uses a flat
`padding-block: var(--step)`. Establish a firmer, more even rhythm: a consistent
section gap with a slightly tighter value, and normalize `.pch-section-head` bottom
margin so inter-section space doesn't stack unevenly. Target: sections read as a steady
cadence, not drifting apart. No content or structural change.

### 4.4 Fix #4 — DataCamp exercise frame

Wrap the existing `.datacamp-exercise-iframe` in the `.pch-viz` terminal header chassis:
a `.pch-viz__bar` with dots + `>>> EXERCISE` tag + the derived title, above the iframe.
Keep the existing brand rail and auto-resize/postMessage logic untouched. The inner
vendor iframe stays as-is (CDN light theme, not restylable); the header makes the block
read as part of the instrument-panel family. Keep the fullscreen button.

### 4.5 Fix #5 — Feedback reaction buttons

In `src/components/Feedback.astro`, replace the PNG emoji faces with clean,
brand-consistent reaction controls (e.g. a small labeled scale or icon buttons using
`currentColor` SVGs + brand hover), matching the site's button language. Preserve
existing behavior (whatever the faces currently submit) and the email/comment form.
Confirm `Feedback.astro` is the sole owner before editing.

## 5. Quality floor (applies to all fixes)

- Responsive down to 360px; no new horizontal overflow.
- `prefers-reduced-motion` respected on any new transition (mirror existing off-switches).
- Visible keyboard focus on any new/restyled interactive control.
- Light + dark themes both verified.
- All new colors/fonts come from brand tokens — no hardcoded hex outside the token set.
- Re-screenshot each touched surface (desktop + mobile) after the change and compare.

## 6. Files in play

- `src/styles/viz.css` — bar treatment, extend to code figures.
- `src/styles/python-playground.css` — rebrand toolbar buttons.
- `public/scripts/python-playground.js` (+ `src/` mirror) — header injection if the
  generated-header mechanism is chosen.
- `lib/mermaid/remake.ts` / a code rehype step / `astro.config.mjs` — only if a
  build-time header step is chosen.
- `src/styles/landing.css` — section rhythm + mobile overflow.
- `src/content/docs/index.mdx` — only if the overflow culprit is markup-level.
- `src/components/DataCampExercise.astro` — terminal header wrap.
- `src/components/Feedback.astro` — reaction controls.

## 7. Risks

- **Blast radius:** full-terminal-bar touches every code block. Mitigate by verifying on
  a spread of page types (tutorial snippet, playground, `command`/text block, project
  page) before considering done.
- **Public/ mirror drift:** `python-playground.css`/`.js` exist in both `src/styles` and
  `public/`. Keep them in sync; `public/` scripts referenced by URL need `is:inline`
  (per repo gotchas), processed scripts importing npm must NOT.
- **DataCamp iframe:** header must not break the postMessage auto-resize height math.

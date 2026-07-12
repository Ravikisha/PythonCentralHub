---
name: theme-check
description: Verify UI/styling changes use Python Central Hub design tokens instead of hardcoded colors/fonts, and follow the Starlight theming rules. Use when adding or editing Astro components, CSS, or landing-page styles.
---

# Theme Check

Keep UI consistent with the **"Interactive Shell"** design system.

## Palette — use tokens, not hex

Tokens live in `src/styles/theme.css` `:root`:

- `--pch-blue` `#4b8bbe` (Python blue) — primary accent
- `--pch-amber` `#ffd343` (Python yellow) — secondary accent
- `--pch-ink` `#0d1117` — matches github-dark-dimmed code theme
- `--pch-surface` `#161b22`

Site-wide accent/gray ramps are set in `tailwind.config.mjs` (feeds starlight-tailwind → Starlight CSS vars) with overrides in `theme.css`. Changing those retheme all 300+ doc pages — intended for global changes only.

**Flag any new hardcoded color** that duplicates a token. Reference `var(--pch-*)` or the Tailwind accent classes instead.

## Type roles (all 4 faces already loaded — do NOT add fonts)

- Atkinson Hyperlegible → display / headings
- Poppins → body
- Source Code Pro → structural mono accent (`>>>` prompts, eyebrows)
- Fira → code blocks

## Signature motif

`>>>` REPL prompt as recurring structural marker; live-typing REPL hero via `public/scripts/repl-type.js` (must stay reduced-motion aware).

## Scoping rules

- Landing styles are namespaced `.pch-*` in `src/styles/landing.css` so nothing leaks to doc pages. Keep landing CSS there and prefixed.
- Landing (`src/content/docs/index.mdx`) uses splash template + custom hero, no `hero:` frontmatter.
- Effects (aurora glow, bento hover-glow, CTA shimmer) are pure CSS. React libraries (shadcn/aceternity/magicui) DO run as islands via `@astrojs/react` — but only on custom pages, never in Starlight's chrome. Island animation stays CSS keyframes where possible; site-wide motion is vanilla `gsap`/`motion` bundled through a processed (non-`is:inline`) `<script>` in `Footer.astro`.

## Gotchas

- `<script src="/scripts/*.js">` pointing at `public/` assets MUST have `is:inline`, else Vite throws Internal Server Error + `@vite/client` overlay on every page.
- Respect `prefers-reduced-motion` — disable infinite animations there (also unblocks headless screenshots).

## Checklist

1. New colors reference `var(--pch-*)` / Tailwind accent, not raw hex.
2. No new font imports.
3. Landing CSS stays in `landing.css`, `.pch-*` prefixed.
4. `public/` script tags have `is:inline`.
5. Animations are reduced-motion aware.

See project memory `design-system` and `repo-gotchas`.

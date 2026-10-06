# Next.js migration plan

Rewrite of Python Central Hub from Astro 7 + Starlight onto Next.js 16, with a
new design and the server-side work folded into the same app.

Baseline commit: `8581cac`. Working tree clean at the time of writing.

## Decisions

| Decision | Choice |
| --- | --- |
| Docs machinery | **fumadocs-core / fumadocs-mdx (headless) + our own UI** |
| Locales at launch | **English only**; `hi`, `es`, `ja`, `zh-cn` follow after cutover |
| Visual direction | **Evolve "Interactive Shell"** — Python blue/amber on editor ink, `>>>` motif |
| Repo layout | **Branch in this repo**, Next app replaces `src/` progressively |

Versions at time of planning: Next **16.3.6**, React **19.3.0**,
fumadocs-ui **16.15.13**, velite 0.4.0.

Headless Fumadocs rather than its shipped theme: it solves the parts that are
tedious and invisible (content source, slug/tree generation, TOC extraction,
search indexing, i18n routing) while leaving every rendered pixel ours. Its
theme would have saved perhaps two weeks and given the site a recognisably
Fumadocs shape — which defeats the point of the rewrite.

## What the repo actually contains

Measured, not estimated:

| Surface | Count |
| --- | --- |
| Content pages (`.md`/`.mdx`) | 1190 |
| Content files importing a custom component | 1062 |
| `.astro` components | 36 |
| `.tsx` components (already React) | 39 |
| Custom remark/rehype plugins | 4 |
| Build/lint scripts | 29 |
| Stylesheets | 16 |
| Vanilla JS in `public/scripts` | 12 |

**The content coupling is concentrated, which is the single most important
fact in this plan.** Five components cover the overwhelming majority of it:

| Component | Files importing it |
| --- | --- |
| `DataCampExercise.astro` | 792 |
| `Quiz.astro` | 595 |
| `Figure.astro` | 292 |
| `FileCode.astro` | 203 |
| `ProblemLadder.astro` | 118 |

Everything else is in the tens or single digits, and 39 components are already
React. So the content migration is not "rewrite 1062 files" — it is "port five
components faithfully, then adjust imports in bulk".

## Target architecture

```
app/
  (docs)/[[...slug]]/page.tsx     1190 content pages
  (app)/dashboard/page.tsx        learner surfaces
  (app)/profile/…  certificates/…  leaderboard/…  exam/[module]/…
  (auth)/login/…  signup/…  reset-password/…  verify-email/…
  verify/page.tsx                 public certificate check
  api/
    grade-exam/route.ts           ports from api/grade-exam.js
    issue-certificate/route.ts
    publish-leaderboard/route.ts
    send-digest/route.ts          Vercel Cron target
  layout.tsx  not-found.tsx  sitemap.ts  robots.ts
content/docs/**                   the 1190 .mdx files, moved as-is
components/
  docs/       sidebar, TOC, pager, search, breadcrumbs
  learn/      DataCampExercise, Quiz, Figure, FileCode, ProblemLadder
  viz/        the 39 existing .tsx, largely unchanged
  ui/         design-system primitives
lib/
  firebase/   ports unchanged
  progress/   ports unchanged
  auth/       ports unchanged
  server/     admin SDK, token verification (from api/_lib/admin.js)
source.config.ts                  fumadocs-mdx: collections, schema, plugins
```

## What survives, what changes

**Ports essentially unchanged** — framework-agnostic TypeScript, no Astro
imports:

- `src/lib/progress/*` (ids, local, sync, awards)
- `src/lib/auth/*` (hint, messages)
- `src/lib/firebase/*` (config, client, auth) — `callApi` keeps working, the
  endpoints keep their paths
- `api/_lib/admin.js` logic → `lib/server/admin.ts`, same verification
- `firebase/firestore.rules` — untouched, already deployed
- 39 `.tsx` viz components
- 16 stylesheets (Tailwind v4 is already a dependency here)
- `src/data/**`, `src/content/i18n/*.json`, `public/**`
- Most of the 29 scripts; `gen-progress-manifest.mjs` needs its content path
  changed and nothing else

**Rewritten:**

- 36 `.astro` components → React. Each carries an inline `<script>` and
  `<style>`; those become client components and CSS. The nine auth/progress
  pages are the bulk of it.
- Starlight's chrome: sidebar, TOC, search UI, pagination, theme toggle,
  language picker, 404.
- `astro.config.mjs` → `next.config.ts` + `source.config.ts`.

**Dropped:** Starlight itself, `@astrojs/*`, Pagefind (Fumadocs indexes at
build time instead).

## The five components that matter

These decide whether 1062 files migrate cleanly. Each is ported deliberately,
with its existing behaviour preserved:

1. **DataCampExercise** — loads `dcl-react.js` from a CDN and is driven by
   props containing Python source. Its template-literal hazards are already
   documented and must survive the port: backticks and `${` in props break it,
   and `sct` has to grade order-independently.
2. **Quiz** — self-check MCQ. Already dispatches `pch:quiz-complete`, which the
   progress layer listens for; that contract stays.
3. **Figure** — image/figure wrapper.
4. **FileCode** — filename-captioned code block, tied to rehype-pretty-code.
5. **ProblemLadder** — reads the DSA YAML data and the page's frontmatter
   `patterns`.

A codemod (`scripts/migrate-imports.mjs`) rewrites the import paths across
1190 files in one pass; the five components are hand-verified against a
sample of real pages before it runs.

## Content pipeline

`source.config.ts` declares the docs collection with a zod schema carrying
over today's frontmatter: `title`, `description`, plus the optional DSA block
(`patterns`, `difficulty`, `prereqs`, `sheets`, `companies`). Every field stays
optional — ~700 pages set none of them, and a required field fails their build.

Markdown plugins carry over nearly intact, since they are plain unified
plugins: `rehype-pretty-code` (with the existing theme and line options),
`remark-math` + `rehype-katex`, `remark-default-code-meta`, and the mermaid and
p5 "remake" plugins in `lib/`.

One Astro-specific hack goes away: `remarkEscapeBraces`, which escapes `{`/`}`
so MDX does not read them as JSX. MDX in Next has the same constraint, so the
plugin ports as-is rather than being dropped — renaming it would be the only
change.

## URLs and SEO — the real risk

There are 1116 indexed English URLs. **Any slug that changes loses its
ranking.** Starlight derives slugs from file paths (lowercase, spaces to
dashes, so `DSA with Python/Phase-01-Foundations/x.mdx` →
`/dsa-with-python/phase-01-foundations/x`). Fumadocs derives from file paths
too, but the two are not guaranteed to agree on every edge case.

Mitigation, built before any content moves:

- `scripts/verify-routes.mjs` — diffs the routes the new build emits against
  `dist/sitemap-0.xml` from the current Astro build. **Zero missing routes is
  a release gate, not a nice-to-have.**
- Anything that cannot be matched exactly gets a permanent redirect in
  `next.config.ts`, not a shrug.
- `app/sitemap.ts` reproduces the current sitemap shape.

English stays unprefixed at the root. That is why English ships first: the
other four locales are additive (`/hi/…` etc.) and cannot disturb an indexed
URL, so they carry far less risk and can follow at leisure.

## Design

Evolving "Interactive Shell" rather than restarting. What carries over:

- Brand tokens: Python blue `#4b8bbe`, amber `#ffd343`, editor ink `#0d1117`,
  and the syntax-token accents.
- Type roles: Atkinson Hyperlegible for headings, Poppins for body, Source Code
  Pro for the structural mono accent, Fira for code.
- The `>>>` prompt marker as the state glyph, already used for progress.

What gets fixed, now that there is no Starlight CSS to fight:

- The docs shell is designed, not overridden. Today's sidebar, TOC and header
  are patches on someone else's layout; several of the bugs found in browser
  testing (prose link styling bleeding into app UI, inverted theme tokens) were
  caused by that.
- One coherent design system in `components/ui`, rather than five stylesheets
  that each re-derive buttons.
- A real design pass on the docs reading experience — the part 1190 pages
  actually live in — using the `frontend-design` skill before implementation.

## Learner platform port

Phases 0–4 (auth, progress, exams, certificates, engagement) move with
minimal change, because the hard parts are already framework-agnostic:

- `lib/**` — unchanged.
- `api/*.js` → `app/api/*/route.ts`. **Node runtime, not Edge:** `firebase-admin`
  needs Node APIs. Same `FIREBASE_SERVICE_ACCOUNT` and `CRON_SECRET` env vars,
  same Vercel Cron entry.
- The nine `.astro` pages → React. Their logic is already imperative DOM code
  in `<script>` blocks; as React components they get simpler, not harder.
- `MarkComplete` and the sidebar tick painter become React components reading
  the same store, so the `subscribe()` contract is unchanged.

## Build performance

Today: **16 minutes for 5940 routes.** English-only is ~1190 pages plus assets,
which should land well inside Vercel's 45-minute Hobby build ceiling. When the
other locales return, options in order of preference:

1. `generateStaticParams` for English, ISR for the rest.
2. Partial prerendering for the app surfaces.
3. If builds approach the ceiling, move non-English to on-demand revalidation.

Build time is a release gate too: if the English build exceeds ~25 minutes, the
strategy changes before more locales are added, not after.

## Status

| # | Phase | State |
| --- | --- | --- |
| 0 | Scaffold | **done** — Next 16.3.6 / React 19.3, fumadocs headless, Tailwind v4 |
| 1 | Route parity harness | **done** — `npm run routes:verify`, 0 missing / 0 extra |
| 2 | Design system + docs shell | **done** — header, progress-spine sidebar, TOC, pager, ⌘K search, theme toggle, footer |
| 3 | The five components | **done** |
| 4 | Content cutover | **partly** — content still read in place from `src/content/docs`; imports codemodded |
| 5 | Learner platform | **done** — 10 pages, the account menu and the per-page progress controls |
| 6 | Remaining components | **done** — all 17 ported, 33 visualisations re-exported |
| 7 | Search, sitemap, SEO | **done** — search index, `sitemap.xml`, `robots.txt`, `/rss.xml`, OpenGraph |
| 8 | Cutover | not started — Vercel project still builds the Astro site from `main` |
| 9 | Locales | **decided** — locale-prefixed URLs 308 to the English page; see `next.config.ts` |

The landing page is no longer an interim: it is a REPL transcript whose output
lines are the twelve modules, with page counts read from the same manifest the
sidebar and the dashboard use, so the front page cannot drift from the course.

Astro is no longer part of this branch: `astro.config.mjs` moved to
`migration/astro-legacy/`, and twelve Astro packages left `package.json`. The
`.astro` components stay as the source `scripts/extract-learn-css.mjs` reads.

**Latest production build: 1205/1205 pages, exit 0.** (1186 content pages, the
ten learner pages, the exam route, sitemap, robots and the feed.)

**First production build passed: 1192/1192 pages, 9.6 min generation, ~12 min
total.** The built HTML was checked against the import counts across the whole
corpus rather than a sample: DataCampExercise appears on 793 pages (792 files
import it), Quiz on 595 (595), AlgorithmCard on 22 (22).

**Build time is now the top risk, and it is worse than the Astro baseline.**
Astro produced 5935 routes in ~12 minutes; Next produces 1192 in the same
time — roughly five times slower per page. Restoring the four locales means
5935 routes again, which at this rate lands near 48 minutes and over Vercel's
45-minute Hobby ceiling. The locale phase therefore cannot be "generate the
fallbacks statically"; it needs ISR, or a rewrite that serves one English page
under every prefix instead of copying it 4740 times.

Things found along the way that were not in the original plan:

- **Fumadocs ignores `sidebar.order`.** 1264 pages carry one -- the author's
  own sequence, which Starlight honoured -- so every folder came out in
  filename order and the twelve modules came out alphabetical. `lib/order.ts`
  restores it: modules follow the learning path the Astro sidebar was
  configured with, pages follow their frontmatter, ties fall back to a natural
  sort so "Phase 2" precedes "Phase 10". The sidebar, the mobile drawer and the
  pager all walk that one tree, and the progress manifest is sorted the same
  way so the landing page and the dashboard agree with it.
- **Content images were never published.** The Astro asset pipeline resolved
  `![](../../assets/x.png)` without the file existing under a public URL;
  Next serves static files as they are. Sixteen images were broken.
  `scripts/sync-content-assets.mjs` copies what the content references into
  `public/assets/` and runs as part of `npm run build`.

- **Locale URLs redirect rather than regenerate.** Only four of the 4740
  locale-prefixed pages were ever translated; the rest were Starlight
  *fallbacks* serving English text under a Spanish or Japanese address.
  `/:locale/:path+` now 308s to the English page and the four real translations
  keep their own routes, which keeps the build at 1205 pages instead of ~5900.
- **Client-side navigation broke the runtime scripts.** mermaid, p5, the
  fullscreen control and the Python playground all did their work on
  `DOMContentLoaded`, which never fires again after the first page. Each one now
  exposes an idempotent entry point and `components/docs/ContentRuntime.tsx`
  calls it on every path change -- and loads each script only on a page whose
  markup needs it.
- **A heading inside a heading broke hydration.** One page ends with an `<h2>`
  containing a link; the TOC entry is itself a link, so the server markup and
  the client tree disagreed and the page re-rendered on an error. `Toc.tsx`
  strips anchors out of heading text.
- **Eighteen pages had a paragraph promoted to a heading.** A line of `---`
  directly under a paragraph is a setext `<h2>` in CommonMark, so whole
  paragraphs were rendering as headings and filling the contents list. Fixed in
  the content with a blank line.

- **1190 MDX files cannot be bundled.** The default collection emits one import
  per file and Turbopack did not finish compiling them in eight minutes.
  `dynamic: true` removes the static import graph entirely (1192 imports → 2).
- **Fumadocs does not slugify.** Its defaults would have relocated all 1183
  content URLs. `lib/slug.mjs` reproduces Starlight's rule; see that file for
  the edge cases, which are load-bearing.
- **Fumadocs' Shiki step had to be replaced** with the site's own
  rehype-pretty-code, because every code-block rule in `global.css` targets the
  latter's markup.
- **MDX rejects raw HTML from remark plugins**, which is what the mermaid and
  p5 plugins emit; `rehype-raw` with `passThrough` for MDX node types fixes it.
- **Vite's `?raw` YAML imports** have no Turbopack equivalent; the two data
  modules now read from disk.
- `trailingSlash: true`, because all 1195 baseline URLs end in one.

## Phases

Estimates assume focused work and include verification, not just typing.

| # | Phase | Output | Estimate |
| --- | --- | --- | --- |
| 0 | Scaffold | Branch, Next 16 + React 19, Tailwind v4, fumadocs-core/mdx wired, one page rendering | 2–3 days |
| 1 | Route parity harness | `verify-routes.mjs` green against the current sitemap on a 50-page sample | 2 days |
| 2 | Design system | Tokens, primitives, docs shell (header, sidebar, TOC, pager, search) designed and built | 1.5–2 weeks |
| 3 | The five components | DataCampExercise, Quiz, Figure, FileCode, ProblemLadder, each verified against real pages | 1 week |
| 4 | Content cutover | Move 1190 files, run the import codemod, full route diff at zero missing | 1 week |
| 5 | Learner platform | lib/** + 9 pages + 4 API routes ported, browser-walked | 1 week |
| 6 | Remaining components | 31 other `.astro` components, viz wiring, scripts | 1 week |
| 7 | Search, sitemap, SEO, 404s, redirects | Release gates green | 3–4 days |
| 8 | Cutover | Vercel project switched, redirects live, monitoring | 2 days |
| 9 | Locales | hi, es, ja, zh-cn restored | 1–1.5 weeks |

**English live: 6–7 weeks. All five locales: 7.5–8.5 weeks.**

## Risks

| Risk | Mitigation |
| --- | --- |
| **Slug drift breaks indexed URLs** | `verify-routes.mjs` as a hard gate; redirects for anything unmatched |
| DataCampExercise breaks on 792 pages | Port first, verify against a sample before the codemod; its template-literal hazards are known |
| Build time exceeds Vercel's ceiling | English-only first; ISR for locales; measured at phase 4, not at the end |
| Scope creep from redesigning while porting | Design is phase 2 and is finished before content moves |
| Losing the Astro site as a reference | It stays on `main` and keeps deploying until cutover |

## Definition of done

1. `verify-routes.mjs` reports zero missing routes against the current sitemap.
2. Build completes inside the Vercel ceiling.
3. `npm run smoke` passes: a sample of content pages plus all fourteen
   application routes, each checked for a marker rather than only for HTTP 200.
4. Lighthouse on a representative content page is no worse than today.
5. All five components render correctly on a hand-picked sample of real pages
   from each module.
6. `main` still deploys the Astro site until the moment of cutover.

## Open items inherited from the current build

These do not block the migration but travel with it:

- 8 of 12 exam banks are unwritten. Four exist -- `tutorials`,
  `dsa-with-python`, `flask-tutorials`, `data-analytics`, twelve questions
  each. `npm run exams:check` validates them; seeding still needs the service
  account. Without a bank a module cannot issue a certificate.
- The Vercel API endpoints have never executed — no service account is
  configured yet.
- GitHub OAuth has no client secret.
- reCAPTCHA tokens are collected but never verified.
- Account deletion now cascades the documents the client is allowed to delete
  (`users/{uid}/progress/*`, the five `stats` docs, the profile) and clears the
  browser's own copy. `examAttempts`, issued `certificates` and any leaderboard
  row are out of reach of the rules and still need an Admin SDK endpoint.

# Handoff log

Session-to-session context for Python Central Hub. Newest entry at the bottom.

---

## Handoff: 2026-09-29 12:07 IST

### Current Task State

Astro → **Next.js 16 migration on branch `nextjs-migration`** (HEAD `8581cac`), plus a full
UI/UX redesign on top of it. Nothing is committed — the working tree holds the whole
migration (1125 modified, 29 untracked paths). **Commits are the user's alone; never run
`git commit` here.**

Green as of this session's last build:

- `npm run build` → **1208/1208 static pages, exit 0** (~7–10 min)
- `npm run smoke` → 12/12 sampled content pages + 14/14 app routes
- `npm run routes:verify` → 0 missing / 0 extra against the pre-migration sitemap
- `npm run typecheck`, `npm run i18n:check` → clean

Phases 0–7 of `docs/nextjs-migration-plan.md` are done. Phase 8 (cutover) has not started:
Vercel still builds the Astro site from `main`.

### Key Decisions

- **Fumadocs headless + own UI**, not fumadocs-ui: the design is the point of the rewrite.
- **`dynamic: true` collection mode**: 1190 MDX files cannot be bundled (1192 imports → 2).
  The entry point is `.source/dynamic.ts`, not `server.ts`.
- **`lib/slug.mjs` reproduces Starlight's slug rule** and is imported by both the app and
  `verify-routes.mjs` so they cannot drift. 1116 indexed URLs depend on it. Whitespace → one
  dash, never collapsed; punctuation stripped after; underscores survive, dots don't.
- **Locale URLs 308-redirect to English** (`next.config.ts`). Only 4 of 4740 were ever
  translated; the rest were Starlight fallbacks. Generating them would push the build past
  Vercel's 45-minute ceiling.
- **Reading order comes from `sidebar.order` frontmatter** (1264 pages carry one), not from
  the filesystem — `lib/order.ts`. Module order mirrors the old Astro sidebar; ties use a
  natural sort so "Phase 2" precedes "Phase 10".
- **Guests stay in localStorage**; no anonymous Firebase Auth records, ever.
- **Server side runs on Vercel Functions** (`api/`), not Cloud Functions — no Blaze plan.
- **Design**: "Interactive Shell" — Python blue + the Shiki function-name violet + amber,
  the blue→violet→amber gradient in exactly three places (wordmark, level number, active
  module rail). Bricolage Grotesque display / Atkinson Hyperlegible body / Fira Code UI.
  **Poppins was dropped** deliberately.
- **shadcn/ui + lucide + simple-icons + anime.js + sonner**; Font Awesome removed (~260 KB).
  magicui/aceternity ports already in `src/components/react/` are reused (BorderBeam,
  NumberTicker). GSAP deliberately unused — one animation engine is enough.

### Modified Files

Migration core:

- `source.config.ts` — fumadocs collection, remark/rehype chain, typed `sidebar` frontmatter
- `lib/source.ts` — loader + `courseTree()` (filters locale roots and loose top-level pages)
- `lib/slug.mjs`, `lib/order.ts`, `lib/site.ts`, `lib/last-modified.ts`, `lib/strings.ts`
- `lib/rehype/code-chrome.ts` — per-block header (language + copy) and the long-block fold
- `lib/rehype/heading-anchors.ts` — empty `#` anchors, drawn in CSS
- `next.config.ts` — `trailingSlash`, locale redirects, `serverExternalPackages`
- `app/layout.tsx`, `app/globals.css`, `app/carried-tokens.css`, `app/(docs)/…`, `app/(app)/…`
- `app/page.tsx` + `app/home.css` — landing page (self-typing REPL transcript)
- `app/sitemap.ts`, `app/robots.ts`, `app/rss.xml/route.ts`

Chrome and content UI:

- `components/docs/` — Header, Sidebar, Toc, Pager, Search (shadcn Command), ThemeToggle,
  UserMenu, Footer, Feedback, ContentRuntime, `docs.css`, `chrome.css`, `code.css`
- `components/progress/PageProgress.tsx` — mark complete / bookmark / private note
- `components/auth/` — session helpers, gates, `app.css`, `dash.css`, `profile.css`
- `components/ui/` — shadcn primitives; `sonner.tsx` publishes `window.toast`

Learner platform (10 pages): `app/(app)/{login,signup,reset-password,verify-email,profile,
dashboard,certificates,leaderboard,verify,exam/[module]}`.

Runtime scripts (static, no rebuild needed to change):

- `public/scripts/python-playground.js` — Run/Edit/Reset, REPL echo, trimmed tracebacks,
  stateful output panel, busy Run button
- `public/scripts/viz-fullscreen.js`, `mermaid.js`, `p5-viz.js` — idempotent entry points
  called again after every client-side navigation

Generators: `scripts/{gen-progress-manifest,gen-search-index,sync-content-assets,
smoke-routes,verify-routes}.mjs`. Exams: `src/data/exams/{tutorials,dsa-with-python,
flask-tutorials,data-analytics}.yaml`.

Deleted: `deploy-static.sh` (would ship a `dist/` that no longer exists and drop `api/`),
`src/env.d.ts`. Moved: `astro.config.mjs` → `migration/astro-legacy/`.

### Blockers / Open Questions

All need the user; none block further local work.

1. **Firebase service-account key** on Vercel (`FIREBASE_SERVICE_ACCOUNT`). Until then
   `npm run exams:seed` cannot run, so **no exam exists in Firestore** and `api/grade-exam`,
   `api/issue-certificate`, `api/publish-leaderboard`, `api/send-digest` have never executed.
2. **GitHub OAuth client secret** — the button returns `auth/operation-not-allowed`. Hide it
   with `NEXT_PUBLIC_AUTH_GITHUB=off` until set.
3. **Firebase authorized domains** for the Vercel preview + production hosts.
4. **`CRON_SECRET`** on Vercel, guarding `/api/send-digest`.
5. **Trigger Email extension** — the digest writes mail documents nothing sends.
6. **Cutover decision**: point the Vercel project at this branch.

### Next Steps

1. **8 exam banks left** — machine-learning, deep-learning, mathematics-for-machine-learning,
   software-testing-and-quality, python-automation-and-scripting, projects, guides, reference.
   12 questions each, house style in `src/data/exams/tutorials.yaml`; validate with
   `npm run exams:check`. Needs nothing from the user.
2. **Admin-side deletion endpoint** in `api/`: `examAttempts`, issued `certificates` and the
   leaderboard row survive account deletion because the rules give the client no delete.
3. **reCAPTCHA is collected but never verified** — verifying means routing contact/feedback
   through `api/`, which breaks both forms until item 1 exists. Deliberately left alone.
4. **Lighthouse pass** on a content page (definition-of-done #4, never measured on Next).
5. Optional cleanups: `public/fontawesome/` (28 MB, now unused), the 36 `.astro` components
   (still the source `scripts/extract-learn-css.mjs` reads), `migration/` (keep until cutover).

### Critical Context

- **Never `git commit`.** The user commits. Leave work in the tree.
- **Windows + Git Bash**: `file.path` uses `\`; split on `/[\\/]/`. Heredocs collapse `\\`
  to `\` — this bit three times; prefer the Write/Edit tools or Python for anything with
  escapes. Playwright paths need `MSYS_NO_PATHCONV=1` or `/foo` becomes `C:/Program Files/foo`.
- **One `next dev` at a time.** A second refuses to start ("Another next dev server is
  already running") and `TaskStop` does not always kill the node process — `taskkill //IM
  node.exe //F` between runs. Stop every dev server before `npm run build`.
- **`npm run build` takes 7–10 minutes.** Changes under `public/` (the playground scripts,
  stylesheets) are served straight from disk — no rebuild needed; restart `next start` so it
  re-reads the directory.
- **Next is ~5× slower per page than Astro.** This is the constraint behind the locale
  redirect decision.
- **The Astro pipeline hid two whole classes of bug**: KaTeX's stylesheet and the content
  images were loaded by Starlight/`customCss`, never by Next. `scripts/sync-content-assets.mjs`
  now runs in `npm run build` so images cannot drift again; `katex/dist/katex.min.css` is
  imported in `app/layout.tsx`.
- **Carried stylesheets** (`src/styles/*.css`, `public/styles/*.css`) still style content,
  the playground and the fullscreen window. `app/carried-tokens.css` republishes the ~30
  `--sl-*` / `--pch-*` variables they read, defined *from* the new tokens.
- **`scripts/check-i18n.mjs` reads source for literal `t("pch.…")` calls** — a key built by
  template string is reported unused, and a `t(...)` inside a comment is reported missing.
- **Verification loop that works**: `npm run typecheck` → `npm run build` → `npx next start`
  → `npm run smoke` → Playwright screenshot. Screenshots caught most of the real bugs.

### Model Summary

- Goal: finish the Next.js 16 rewrite of a 1,190-page Python course and redesign its UI.
- Phases 0–7 done; build green at 1208/1208; route parity exact against the old sitemap.
- Astro removed from the branch: config moved to `migration/astro-legacy/`, 12 packages gone.
- Locale URLs redirect rather than regenerate — the only way to stay inside Vercel's ceiling.
- Sidebar/pager/landing/dashboard all read one reading order from `lib/order.ts`.
- Design system rebuilt on shadcn + three brand hues; the gradient appears in three places.
- Code blocks are a three-part instrument: header, code, stateful output panel.
- In-page Python (Pyodide) verified running on tutorials, numpy and DSA pages.
- Learner platform is 10 ported pages; the profile was rebuilt with reading analytics.
- Blocked on the user for: service-account key, GitHub secret, authorized domains, cutover.
- Next unblocked work: 8 exam banks, the admin deletion endpoint, a Lighthouse pass.
- Nothing is committed, by instruction.

### Handoff Context (paste into next session)

Repo `D:\PythonCentralHub`, branch `nextjs-migration`, HEAD `8581cac`. Everything is
uncommitted — do not commit; the user does that.

Start by reading `docs/nextjs-migration-plan.md` (status table near the bottom) and this
handoff. Then confirm the tree is still green:

    npm run typecheck        # fast
    npm run i18n:check
    npm run routes:verify    # 0 missing / 0 extra, hard gate
    npm run build            # 7-10 min, expect 1208/1208 exit 0
    npx next start --port 3400
    npm run smoke -- --base http://localhost:3400 --n 12

Kill stray servers with `taskkill //IM node.exe //F` before building; only one `next dev`
can run at a time. Playwright scripts live in the session scratchpad — prefix `MSYS_NO_PATHCONV=1`.

Highest-value next task with no external blocker: write the remaining 8 exam banks into
`src/data/exams/<module>.yaml`, 12 questions each, following `tutorials.yaml`; validate with
`npm run exams:check` and regenerate `npm run progress:manifest` so `hasExam` picks them up.

Do not: commit, regenerate locale pages statically, reimplement the slug rule, or move
`src/content/docs` (churn with no user-visible gain).
---

## Handoff: 2026-10-05T06:03:33Z (auto-saved before compaction)

### Compaction Metadata
- Trigger: (unknown)
- Custom instructions: (none)
- Transcript: (unknown)
- CWD: (unknown)

### Last User Message (transcript tail)
(unavailable - transcript missing)

### Last Assistant Message (transcript tail)
(unavailable - transcript missing)

### Git Snapshot
- Branch: nextjs-migration
- Status:
 M .env.example
MM .gitignore
A  AGENTS.md
A  CLAUDE.md
 D api/_lib/admin.js
 D api/grade-exam.js
 D api/issue-certificate.js
 D api/publish-leaderboard.js
 D api/send-digest.js
AM app/(docs)/[...slug]/page.tsx
AM app/globals.css
AM app/layout.tsx
 D deploy-static.sh
 M docs/auth.md
AM docs/nextjs-migration-plan.md
 M firebase/firestore.rules
 M lib/mermaid/remake.ts
 M lib/mermaid/render-diagram.ts
A  lib/slug.mjs
AM lib/source.ts
R  astro.config.mjs -> migration/astro-legacy/astro.config.mjs
R  src/pages/certificates.astro -> migration/astro-pages/certificates.astro
R  src/pages/dashboard.astro -> migration/astro-pages/dashboard.astro
R  src/pages/exam/[module].astro -> migration/astro-pages/exam/[module].astro
R  src/pages/leaderboard.astro -> migration/astro-pages/leaderboard.astro
R  src/pages/login.astro -> migration/astro-pages/login.astro
R  src/pages/profile.astro -> migration/astro-pages/profile.astro
R  src/pages/reset-password.astro -> migration/astro-pages/reset-password.astro
R  src/pages/rss.xml.js -> migration/astro-pages/rss.xml.js
R  src/pages/signup.astro -> migration/astro-pages/signup.astro
R  src/pages/verify-email.astro -> migration/astro-pages/verify-email.astro
R  src/pages/verify.astro -> migration/astro-pages/verify.astro
A  migration/routes-baseline-en.txt
A  migration/routes-baseline.txt
AM next.config.ts
MM package-lock.json
MM package.json
A  postcss.config.mjs
 D public/fontawesome/LICENSE.txt
 D public/fontawesome/css/all.css
 D public/fontawesome/css/all.min.css
 D public/fontawesome/css/brands.css
 D public/fontawesome/css/brands.min.css
 D public/fontawesome/css/fontawesome.css
 D public/fontawesome/css/fontawesome.min.css
 D public/fontawesome/css/regular.css
 D public/fontawesome/css/regular.min.css
 D public/fontawesome/css/solid.css
 D public/fontawesome/css/solid.min.css
 D public/fontawesome/css/svg-with-js.css
 D public/fontawesome/css/svg-with-js.min.css
 D public/fontawesome/css/v4-font-face.css
 D public/fontawesome/css/v4-font-face.min.css
 D public/fontawesome/css/v4-shims.css
 D public/fontawesome/css/v4-shims.min.css
 D public/fontawesome/css/v5-font-face.css
 D public/fontawesome/css/v5-font-face.min.css
 D public/fontawesome/js/all.js
 D public/fontawesome/js/all.min.js
 D public/fontawesome/js/brands.js
 D public/fontawesome/js/brands.min.js
 D public/fontawesome/js/conflict-detection.js
 D public/fontawesome/js/conflict-detection.min.js
 D public/fontawesome/js/fontawesome.js
 D public/fontawesome/js/fontawesome.min.js
 D public/fontawesome/js/regular.js
 D public/fontawesome/js/regular.min.js
 D public/fontawesome/js/solid.js
 D public/fontawesome/js/solid.min.js
 D public/fontawesome/js/v4-shims.js
 D public/fontawesome/js/v4-shims.min.js
 D public/fontawesome/less/_animated.less
 D public/fontawesome/less/_bordered-pulled.less
 D public/fontawesome/less/_core.less
 D public/fontawesome/less/_fixed-width.less
 D public/fontawesome/less/_icons.less
 D public/fontawesome/less/_list.less
 D public/fontawesome/less/_mixins.less
 D public/fontawesome/less/_rotated-flipped.less
 D public/fontawesome/less/_screen-reader.less
 D public/fontawesome/less/_shims.less
 D public/fontawesome/less/_sizing.less
 D public/fontawesome/less/_stacked.less
 D public/fontawesome/less/_variables.less
 D public/fontawesome/less/brands.less
 D public/fontawesome/less/fontawesome.less
 D public/fontawesome/less/regular.less
 D public/fontawesome/less/solid.less
 D public/fontawesome/less/v4-shims.less
 D public/fontawesome/metadata/categories.yml
 D public/fontawesome/metadata/icon-families.json
 D public/fontawesome/metadata/icon-families.yml
 D public/fontawesome/metadata/icons.json
 D public/fontawesome/metadata/icons.yml
 D public/fontawesome/metadata/shims.json
 D public/fontawesome/metadata/shims.yml
 D public/fontawesome/metadata/sponsors.yml
 D public/fontawesome/scss/_animated.scss
 D public/fontawesome/scss/_bordered-pulled.scss
 D public/fontawesome/scss/_core.scss
 D public/fontawesome/scss/_fixed-width.scss
 D public/fontawesome/scss/_functions.scss
 D public/fontawesome/scss/_icons.scss
 D public/fontawesome/scss/_list.scss
 D public/fontawesome/scss/_mixins.scss
 D public/fontawesome/scss/_rotated-flipped.scss
 D public/fontawesome/scss/_screen-reader.scss
 D public/fontawesome/scss/_shims.scss
 D public/fontawesome/scss/_sizing.scss
 D public/fontawesome/scss/_stacked.scss
 D public/fontawesome/scss/_variables.scss
 D public/fontawesome/scss/brands.scss
 D public/fontawesome/scss/fontawesome.scss
 D public/fontawesome/scss/regular.scss
 D public/fontawesome/scss/solid.scss
 D public/fontawesome/scss/v4-shims.scss
 D public/fontawesome/sprites/brands.svg
 D public/fontawesome/sprites/regular.svg
 D public/fontawesome/sprites/solid.svg
 D public/fontawesome/svgs/brands/42-group.svg
 D public/fontawesome/svgs/brands/500px.svg
 D public/fontawesome/svgs/brands/accessible-icon.svg
 D public/fontawesome/svgs/brands/accusoft.svg
 D public/fontawesome/svgs/brands/adn.svg
 D public/fontawesome/svgs/brands/adversal.svg
 D public/fontawesome/svgs/brands/affiliatetheme.svg
 D public/fontawesome/svgs/brands/airbnb.svg
 D public/fontawesome/svgs/brands/algolia.svg
 D public/fontawesome/svgs/brands/alipay.svg
 D public/fontawesome/svgs/brands/amazon-pay.svg
 D public/fontawesome/svgs/brands/amazon.svg
 D public/fontawesome/svgs/brands/amilia.svg
 D public/fontawesome/svgs/brands/android.svg
 D public/fontawesome/svgs/brands/angellist.svg
 D public/fontawesome/svgs/brands/angrycreative.svg
 D public/fontawesome/svgs/brands/angular.svg
 D public/fontawesome/svgs/brands/app-store-ios.svg
 D public/fontawesome/svgs/brands/app-store.svg
 D public/fontawesome/svgs/brands/apper.svg
 D public/fontawesome/svgs/brands/apple-pay.svg
 D public/fontawesome/svgs/brands/apple.svg
 D public/fontawesome/svgs/brands/artstation.svg
 D public/fontawesome/svgs/brands/asymmetrik.svg
 D public/fontawesome/svgs/brands/atlassian.svg
 D public/fontawesome/svgs/brands/audible.svg
 D public/fontawesome/svgs/brands/autoprefixer.svg
 D public/fontawesome/svgs/brands/avianex.svg
 D public/fontawesome/svgs/brands/aviato.svg
 D public/fontawesome/svgs/brands/aws.svg
 D public/fontawesome/svgs/brands/bandcamp.svg
 D public/fontawesome/svgs/brands/battle-net.svg
 D public/fontawesome/svgs/brands/behance.svg
 D public/fontawesome/svgs/brands/bilibili.svg
 D public/fontawesome/svgs/brands/bimobject.svg
 D public/fontawesome/svgs/brands/bitbucket.svg
 D public/fontawesome/svgs/brands/bitcoin.svg
 D public/fontawesome/svgs/brands/bity.svg
 D public/fontawesome/svgs/brands/black-tie.svg
 D public/fontawesome/svgs/brands/blackberry.svg
 D public/fontawesome/svgs/brands/blogger-b.svg
 D public/fontawesome/svgs/brands/blogger.svg
 D public/fontawesome/svgs/brands/bluetooth-b.svg
 D public/fontawesome/svgs/brands/bluetooth.svg
 D public/fontawesome/svgs/brands/bootstrap.svg
 D public/fontawesome/svgs/brands/bots.svg
 D public/fontawesome/svgs/brands/btc.svg
 D public/fontawesome/svgs/brands/buffer.svg
 D public/fontawesome/svgs/brands/buromobelexperte.svg
 D public/fontawesome/svgs/brands/buy-n-large.svg
 D public/fontawesome/svgs/brands/buysellads.svg
 D public/fontawesome/svgs/brands/canadian-maple-leaf.svg
 D public/fontawesome/svgs/brands/cc-amazon-pay.svg
 D public/fontawesome/svgs/brands/cc-amex.svg
 D public/fontawesome/svgs/brands/cc-apple-pay.svg
 D public/fontawesome/svgs/brands/cc-diners-club.svg
 D public/fontawesome/svgs/brands/cc-discover.svg
 D public/fontawesome/svgs/brands/cc-jcb.svg
 D public/fontawesome/svgs/brands/cc-mastercard.svg
 D public/fontawesome/svgs/brands/cc-paypal.svg
 D public/fontawesome/svgs/brands/cc-stripe.svg
 D public/fontawesome/svgs/brands/cc-visa.svg
 D public/fontawesome/svgs/brands/centercode.svg
 D public/fontawesome/svgs/brands/centos.svg
 D public/fontawesome/svgs/brands/chrome.svg
 D public/fontawesome/svgs/brands/chromecast.svg
 D public/fontawesome/svgs/brands/cloudflare.svg
 D public/fontawesome/svgs/brands/cloudscale.svg
 D public/fontawesome/svgs/brands/cloudsmith.svg
 D public/fontawesome/svgs/brands/cloudversify.svg
 D public/fontawesome/svgs/brands/cmplid.svg
 D public/fontawesome/svgs/brands/codepen.svg
 D public/fontawesome/svgs/brands/codiepie.svg
 D public/fontawesome/svgs/brands/confluence.svg
 D public/fontawesome/svgs/brands/connectdevelop.svg
 D public/fontawesome/svgs/brands/contao.svg
 D public/fontawesome/svgs/brands/cotton-bureau.svg
 D public/fontawesome/svgs/brands/cpanel.svg
 D public/fontawesome/svgs/brands/creative-commons-by.svg
 D public/fontawesome/svgs/brands/creative-commons-nc-eu.svg
 D public/fontawesome/svgs/brands/creative-commons-nc-jp.svg
 D public/fontawesome/svgs/brands/creative-commons-nc.svg
 D public/fontawesome/svgs/brands/creative-commons-nd.svg
 D public/fontawesome/svgs/brands/creative-commons-pd-alt.svg
 D public/fontawesome/svgs/brands/creative-commons-pd.svg
 D public/fontawesome/svgs/brands/creative-commons-remix.svg
 D public/fontawesome/svgs/brands/creative-commons-sa.svg
 D public/fontawesome/svgs/brands/creative-commons-sampling-plus.svg
 D public/fontawesome/svgs/brands/creative-commons-sampling.svg
 D public/fontawesome/svgs/brands/creative-commons-share.svg
 D public/fontawesome/svgs/brands/creative-commons-zero.svg
 D public/fontawesome/svgs/brands/creative-commons.svg
 D public/fontawesome/svgs/brands/critical-role.svg
 D public/fontawesome/svgs/brands/css3-alt.svg
 D public/fontawesome/svgs/brands/css3.svg
 D public/fontawesome/svgs/brands/cuttlefish.svg
 D public/fontawesome/svgs/brands/d-and-d-beyond.svg
 D public/fontawesome/svgs/brands/d-and-d.svg
 D public/fontawesome/svgs/brands/dailymotion.svg
 D public/fontawesome/svgs/brands/dashcube.svg
 D public/fontawesome/svgs/brands/debian.svg
 D public/fontawesome/svgs/brands/deezer.svg
 D public/fontawesome/svgs/brands/delicious.svg
 D public/fontawesome/svgs/brands/deploydog.svg
 D public/fontawesome/svgs/brands/deskpro.svg
 D public/fontawesome/svgs/brands/dev.svg
 D public/fontawesome/svgs/brands/deviantart.svg
 D public/fontawesome/svgs/brands/dhl.svg
 D public/fontawesome/svgs/brands/diaspora.svg
 D public/fontawesome/svgs/brands/digg.svg
 D public/fontawesome/svgs/brands/digital-ocean.svg
 D public/fontawesome/svgs/brands/discord.svg
 D public/fontawesome/svgs/brands/discourse.svg
 D public/fontawesome/svgs/brands/dochub.svg
 D public/fontawesome/svgs/brands/docker.svg
 D public/fontawesome/svgs/brands/draft2digital.svg
 D public/fontawesome/svgs/brands/dribbble.svg
 D public/fontawesome/svgs/brands/dropbox.svg
 D public/fontawesome/svgs/brands/drupal.svg
 D public/fontawesome/svgs/brands/dyalog.svg
 D public/fontawesome/svgs/brands/earlybirds.svg
 D public/fontawesome/svgs/brands/ebay.svg
 D public/fontawesome/svgs/brands/edge-legacy.svg
 D public/fontawesome/svgs/brands/edge.svg
 D public/fontawesome/svgs/brands/elementor.svg
 D public/fontawesome/svgs/brands/ello.svg
 D public/fontawesome/svgs/brands/ember.svg
 D public/fontawesome/svgs/brands/empire.svg
 D public/fontawesome/svgs/brands/envira.svg
 D public/fontawesome/svgs/brands/erlang.svg
 D public/fontawesome/svgs/brands/ethereum.svg
 D public/fontawesome/svgs/brands/etsy.svg
 D public/fontawesome/svgs/brands/evernote.svg
 D public/fontawesome/svgs/brands/expeditedssl.svg
 D public/fontawesome/svgs/brands/facebook-f.svg
 D public/fontawesome/svgs/brands/facebook-messenger.svg
 D public/fontawesome/svgs/brands/facebook.svg
 D public/fontawesome/svgs/brands/fantasy-flight-games.svg
 D public/fontawesome/svgs/brands/fedex.svg
 D public/fontawesome/svgs/brands/fedora.svg
 D public/fontawesome/svgs/brands/figma.svg
 D public/fontawesome/svgs/brands/firefox-browser.svg
 D public/fontawesome/svgs/brands/firefox.svg
 D public/fontawesome/svgs/brands/first-order-alt.svg
 D public/fontawesome/svgs/brands/first-order.svg
 D public/fontawesome/svgs/brands/firstdraft.svg
 D public/fontawesome/svgs/brands/flickr.svg
 D public/fontawesome/svgs/brands/flipboard.svg
 D public/fontawesome/svgs/brands/fly.svg
 D public/fontawesome/svgs/brands/font-awesome.svg
 D public/fontawesome/svgs/brands/fonticons-fi.svg
 D public/fontawesome/svgs/brands/fonticons.svg
 D public/fontawesome/svgs/brands/fort-awesome-alt.svg
 D public/fontawesome/svgs/brands/fort-awesome.svg
 D public/fontawesome/svgs/brands/forumbee.svg
 D public/fontawesome/svgs/brands/foursquare.svg
 D public/fontawesome/svgs/brands/free-code-camp.svg
 D public/fontawesome/svgs/brands/freebsd.svg
 D public/fontawesome/svgs/brands/fulcrum.svg
 D public/fontawesome/svgs/brands/galactic-republic.svg
 D public/fontawesome/svgs/brands/galactic-senate.svg
 D public/fontawesome/svgs/brands/get-pocket.svg
 D public/fontawesome/svgs/brands/gg-circle.svg
 D public/fontawesome/svgs/brands/gg.svg
 D public/fontawesome/svgs/brands/git-alt.svg
 D public/fontawesome/svgs/brands/git.svg
 D public/fontawesome/svgs/brands/github-alt.svg
 D public/fontawesome/svgs/brands/github.svg
 D public/fontawesome/svgs/brands/gitkraken.svg
 D public/fontawesome/svgs/brands/gitlab.svg
 D public/fontawesome/svgs/brands/gitter.svg
 D public/fontawesome/svgs/brands/glide-g.svg
 D public/fontawesome/svgs/brands/glide.svg
 D public/fontawesome/svgs/brands/gofore.svg
 D public/fontawesome/svgs/brands/golang.svg
 D public/fontawesome/svgs/brands/goodreads-g.svg
 D public/fontawesome/svgs/brands/goodreads.svg
 D public/fontawesome/svgs/brands/google-drive.svg
 D public/fontawesome/svgs/brands/google-pay.svg
 D public/fontawesome/svgs/brands/google-play.svg
 D public/fontawesome/svgs/brands/google-plus-g.svg
 D public/fontawesome/svgs/brands/google-plus.svg
 D public/fontawesome/svgs/brands/google-wallet.svg
 D public/fontawesome/svgs/brands/google.svg
 D public/fontawesome/svgs/brands/gratipay.svg
 D public/fontawesome/svgs/brands/grav.svg
 D public/fontawesome/svgs/brands/gripfire.svg
 D public/fontawesome/svgs/brands/grunt.svg
 D public/fontawesome/svgs/brands/guilded.svg
 D public/fontawesome/svgs/brands/gulp.svg
 D public/fontawesome/svgs/brands/hacker-news.svg
 D public/fontawesome/svgs/brands/hackerrank.svg
 D public/fontawesome/svgs/brands/hashnode.svg
 D public/fontawesome/svgs/brands/hips.svg
 D public/fontawesome/svgs/brands/hire-a-helper.svg
 D public/fontawesome/svgs/brands/hive.svg
 D public/fontawesome/svgs/brands/hooli.svg
 D public/fontawesome/svgs/brands/hornbill.svg
 D public/fontawesome/svgs/brands/hotjar.svg
 D public/fontawesome/svgs/brands/houzz.svg
 D public/fontawesome/svgs/brands/html5.svg
 D public/fontawesome/svgs/brands/hubspot.svg
 D public/fontawesome/svgs/brands/ideal.svg
 D public/fontawesome/svgs/brands/imdb.svg
 D public/fontawesome/svgs/brands/instagram.svg
 D public/fontawesome/svgs/brands/instalod.svg
 D public/fontawesome/svgs/brands/intercom.svg
 D public/fontawesome/svgs/brands/internet-explorer.svg
 D public/fontawesome/svgs/brands/invision.svg
 D public/fontawesome/svgs/brands/ioxhost.svg
 D public/fontawesome/svgs/brands/itch-io.svg
 D public/fontawesome/svgs/brands/itunes-note.svg
 D public/fontawesome/svgs/brands/itunes.svg
 D public/fontawesome/svgs/brands/java.svg
 D public/fontawesome/svgs/brands/jedi-order.svg
 D public/fontawesome/svgs/brands/jenkins.svg
 D public/fontawesome/svgs/brands/jira.svg
 D public/fontawesome/svgs/brands/joget.svg
 D public/fontawesome/svgs/brands/joomla.svg
 D public/fontawesome/svgs/brands/js.svg
 D public/fontawesome/svgs/brands/jsfiddle.svg
 D public/fontawesome/svgs/brands/kaggle.svg
 D public/fontawesome/svgs/brands/keybase.svg
 D public/fontawesome/svgs/brands/keycdn.svg
 D public/fontawesome/svgs/brands/kickstarter-k.svg
 D public/fontawesome/svgs/brands/kickstarter.svg
 D public/fontawesome/svgs/brands/korvue.svg
 D public/fontawesome/svgs/brands/laravel.svg
 D public/fontawesome/svgs/brands/lastfm.svg
 D public/fontawesome/svgs/brands/leanpub.svg
 D public/fontawesome/svgs/brands/less.svg
 D public/fontawesome/svgs/brands/line.svg
 D public/fontawesome/svgs/brands/linkedin-in.svg
 D public/fontawesome/svgs/brands/linkedin.svg
 D public/fontawesome/svgs/brands/linode.svg
 D public/fontawesome/svgs/brands/linux.svg
 D public/fontawesome/svgs/brands/lyft.svg
 D public/fontawesome/svgs/brands/magento.svg
 D public/fontawesome/svgs/brands/mailchimp.svg
 D public/fontawesome/svgs/brands/mandalorian.svg
 D public/fontawesome/svgs/brands/markdown.svg
 D public/fontawesome/svgs/brands/mastodon.svg
 D public/fontawesome/svgs/brands/maxcdn.svg
 D public/fontawesome/svgs/brands/mdb.svg
 D public/fontawesome/svgs/brands/medapps.svg
 D public/fontawesome/svgs/brands/medium.svg
 D public/fontawesome/svgs/brands/medrt.svg
 D public/fontawesome/svgs/brands/meetup.svg
 D public/fontawesome/svgs/brands/megaport.svg
 D public/fontawesome/svgs/brands/mendeley.svg
 D public/fontawesome/svgs/brands/meta.svg
 D public/fontawesome/svgs/brands/microblog.svg
 D public/fontawesome/svgs/brands/microsoft.svg
 D public/fontawesome/svgs/brands/mix.svg
 D public/fontawesome/svgs/brands/mixcloud.svg
 D public/fontawesome/svgs/brands/mixer.svg
 D public/fontawesome/svgs/brands/mizuni.svg
 D public/fontawesome/svgs/brands/modx.svg
 D public/fontawesome/svgs/brands/monero.svg
 D public/fontawesome/svgs/brands/napster.svg
 D public/fontawesome/svgs/brands/neos.svg
 D public/fontawesome/svgs/brands/nfc-directional.svg
 D public/fontawesome/svgs/brands/nfc-symbol.svg
 D public/fontawesome/svgs/brands/nimblr.svg
 D public/fontawesome/svgs/brands/node-js.svg
 D public/fontawesome/svgs/brands/node.svg
 D public/fontawesome/svgs/brands/npm.svg
 D public/fontawesome/svgs/brands/ns8.svg
 D public/fontawesome/svgs/brands/nutritionix.svg
 D public/fontawesome/svgs/brands/octopus-deploy.svg
 D public/fontawesome/svgs/brands/odnoklassniki.svg
 D public/fontawesome/svgs/brands/odysee.svg
 D public/fontawesome/svgs/brands/old-republic.svg
 D public/fontawesome/svgs/brands/opencart.svg
 D public/fontawesome/svgs/brands/openid.svg
 D public/fontawesome/svgs/brands/opera.svg
 D public/fontawesome/svgs/brands/optin-monster.svg
 D public/fontawesome/svgs/brands/orcid.svg
 D public/fontawesome/svgs/brands/osi.svg
 D public/fontawesome/svgs/brands/padlet.svg
 D public/fontawesome/svgs/brands/page4.svg
 D public/fontawesome/svgs/brands/pagelines.svg
 D public/fontawesome/svgs/brands/palfed.svg
 D public/fontawesome/svgs/brands/patreon.svg
 D public/fontawesome/svgs/brands/paypal.svg
 D public/fontawesome/svgs/brands/perbyte.svg
 D public/fontawesome/svgs/brands/periscope.svg
 D public/fontawesome/svgs/brands/phabricator.svg
 D public/fontawesome/svgs/brands/phoenix-framework.svg
 D public/fontawesome/svgs/brands/phoenix-squadron.svg
 D public/fontawesome/svgs/brands/php.svg
 D public/fontawesome/svgs/brands/pied-piper-alt.svg
 D public/fontawesome/svgs/brands/pied-piper-hat.svg
 D public/fontawesome/svgs/brands/pied-piper-pp.svg
 D public/fontawesome/svgs/brands/pied-piper.svg
 D public/fontawesome/svgs/brands/pinterest-p.svg
 D public/fontawesome/svgs/brands/pinterest.svg
 D public/fontawesome/svgs/brands/pix.svg
 D public/fontawesome/svgs/brands/playstation.svg
 D public/fontawesome/svgs/brands/product-hunt.svg
 D public/fontawesome/svgs/brands/pushed.svg
 D public/fontawesome/svgs/brands/python.svg
 D public/fontawesome/svgs/brands/qq.svg
 D public/fontawesome/svgs/brands/quinscape.svg
 D public/fontawesome/svgs/brands/quora.svg
 D public/fontawesome/svgs/brands/r-project.svg
 D public/fontawesome/svgs/brands/raspberry-pi.svg
 D public/fontawesome/svgs/brands/ravelry.svg
 D public/fontawesome/svgs/brands/react.svg
 D public/fontawesome/svgs/brands/reacteurope.svg
 D public/fontawesome/svgs/brands/readme.svg
 D public/fontawesome/svgs/brands/rebel.svg
 D public/fontawesome/svgs/brands/red-river.svg
 D public/fontawesome/svgs/brands/reddit-alien.svg
 D public/fontawesome/svgs/brands/reddit.svg
 D public/fontawesome/svgs/brands/redhat.svg
 D public/fontawesome/svgs/brands/renren.svg
 D public/fontawesome/svgs/brands/replyd.svg
 D public/fontawesome/svgs/brands/researchgate.svg
 D public/fontawesome/svgs/brands/resolving.svg
 D public/fontawesome/svgs/brands/rev.svg
 D public/fontawesome/svgs/brands/rocketchat.svg
 D public/fontawesome/svgs/brands/rockrms.svg
 D public/fontawesome/svgs/brands/rust.svg
 D public/fontawesome/svgs/brands/safari.svg
 D public/fontawesome/svgs/brands/salesforce.svg
 D public/fontawesome/svgs/brands/sass.svg
 D public/fontawesome/svgs/brands/schlix.svg
 D public/fontawesome/svgs/brands/screenpal.svg
 D public/fontawesome/svgs/brands/scribd.svg
 D public/fontawesome/svgs/brands/searchengin.svg
 D public/fontawesome/svgs/brands/sellcast.svg
 D public/fontawesome/svgs/brands/sellsy.svg
 D public/fontawesome/svgs/brands/servicestack.svg
 D public/fontawesome/svgs/brands/shirtsinbulk.svg
 D public/fontawesome/svgs/brands/shopify.svg
 D public/fontawesome/svgs/brands/shopware.svg
 D public/fontawesome/svgs/brands/simplybuilt.svg
 D public/fontawesome/svgs/brands/sistrix.svg
 D public/fontawesome/svgs/brands/sith.svg
 D public/fontawesome/svgs/brands/sitrox.svg
 D public/fontawesome/svgs/brands/sketch.svg
 D public/fontawesome/svgs/brands/skyatlas.svg
 D public/fontawesome/svgs/brands/skype.svg
 D public/fontawesome/svgs/brands/slack.svg
 D public/fontawesome/svgs/brands/slideshare.svg
 D public/fontawesome/svgs/brands/snapchat.svg
 D public/fontawesome/svgs/brands/soundcloud.svg
 D public/fontawesome/svgs/brands/sourcetree.svg
 D public/fontawesome/svgs/brands/space-awesome.svg
 D public/fontawesome/svgs/brands/speakap.svg
 D public/fontawesome/svgs/brands/speaker-deck.svg
 D public/fontawesome/svgs/brands/spotify.svg
 D public/fontawesome/svgs/brands/square-behance.svg
 D public/fontawesome/svgs/brands/square-dribbble.svg
 D public/fontawesome/svgs/brands/square-facebook.svg
 D public/fontawesome/svgs/brands/square-font-awesome-stroke.svg
 D public/fontawesome/svgs/brands/square-font-awesome.svg
 D public/fontawesome/svgs/brands/square-git.svg
 D public/fontawesome/svgs/brands/square-github.svg
 D public/fontawesome/svgs/brands/square-gitlab.svg
 D public/fontawesome/svgs/brands/square-google-plus.svg
 D public/fontawesome/svgs/brands/square-hacker-news.svg
 D public/fontawesome/svgs/brands/square-instagram.svg
 D public/fontawesome/svgs/brands/square-js.svg
 D public/fontawesome/svgs/brands/square-lastfm.svg
 D public/fontawesome/svgs/brands/square-odnoklassniki.svg
 D public/fontawesome/svgs/brands/square-pied-piper.svg
 D public/fontawesome/svgs/brands/square-pinterest.svg
 D public/fontawesome/svgs/brands/square-reddit.svg
 D public/fontawesome/svgs/brands/square-snapchat.svg
 D public/fontawesome/svgs/brands/square-steam.svg
 D public/fontawesome/svgs/brands/square-threads.svg
 D public/fontawesome/svgs/brands/square-tumblr.svg
 D public/fontawesome/svgs/brands/square-twitter.svg
 D public/fontawesome/svgs/brands/square-viadeo.svg
 D public/fontawesome/svgs/brands/square-vimeo.svg
 D public/fontawesome/svgs/brands/square-whatsapp.svg
 D public/fontawesome/svgs/brands/square-x-twitter.svg
 D public/fontawesome/svgs/brands/square-xing.svg
 D public/fontawesome/svgs/brands/square-youtube.svg
 D public/fontawesome/svgs/brands/squarespace.svg
 D public/fontawesome/svgs/brands/stack-exchange.svg
 D public/fontawesome/svgs/brands/stack-overflow.svg
 D public/fontawesome/svgs/brands/stackpath.svg
 D public/fontawesome/svgs/brands/staylinked.svg
 D public/fontawesome/svgs/brands/steam-symbol.svg
 D public/fontawesome/svgs/brands/steam.svg
 D public/fontawesome/svgs/brands/sticker-mule.svg
 D public/fontawesome/svgs/brands/strava.svg
 D public/fontawesome/svgs/brands/stripe-s.svg
 D public/fontawesome/svgs/brands/stripe.svg
 D public/fontawesome/svgs/brands/stubber.svg
 D public/fontawesome/svgs/brands/studiovinari.svg
 D public/fontawesome/svgs/brands/stumbleupon-circle.svg
 D public/fontawesome/svgs/brands/stumbleupon.svg
 D public/fontawesome/svgs/brands/superpowers.svg
 D public/fontawesome/svgs/brands/supple.svg
 D public/fontawesome/svgs/brands/suse.svg
 D public/fontawesome/svgs/brands/swift.svg
 D public/fontawesome/svgs/brands/symfony.svg
 D public/fontawesome/svgs/brands/teamspeak.svg
 D public/fontawesome/svgs/brands/telegram.svg
 D public/fontawesome/svgs/brands/tencent-weibo.svg
 D public/fontawesome/svgs/brands/the-red-yeti.svg
 D public/fontawesome/svgs/brands/themeco.svg
 D public/fontawesome/svgs/brands/themeisle.svg
 D public/fontawesome/svgs/brands/think-peaks.svg
 D public/fontawesome/svgs/brands/threads.svg
 D public/fontawesome/svgs/brands/tiktok.svg
 D public/fontawesome/svgs/brands/trade-federation.svg
 D public/fontawesome/svgs/brands/trello.svg
 D public/fontawesome/svgs/brands/tumblr.svg
 D public/fontawesome/svgs/brands/twitch.svg
 D public/fontawesome/svgs/brands/twitter.svg
 D public/fontawesome/svgs/brands/typo3.svg
 D public/fontawesome/svgs/brands/uber.svg
 D public/fontawesome/svgs/brands/ubuntu.svg
 D public/fontawesome/svgs/brands/uikit.svg
 D public/fontawesome/svgs/brands/umbraco.svg
 D public/fontawesome/svgs/brands/uncharted.svg
 D public/fontawesome/svgs/brands/uniregistry.svg
 D public/fontawesome/svgs/brands/unity.svg
 D public/fontawesome/svgs/brands/unsplash.svg
 D public/fontawesome/svgs/brands/untappd.svg
 D public/fontawesome/svgs/brands/ups.svg
 D public/fontawesome/svgs/brands/usb.svg
 D public/fontawesome/svgs/brands/usps.svg
 D public/fontawesome/svgs/brands/ussunnah.svg
 D public/fontawesome/svgs/brands/vaadin.svg
 D public/fontawesome/svgs/brands/viacoin.svg
 D public/fontawesome/svgs/brands/viadeo.svg
 D public/fontawesome/svgs/brands/viber.svg
 D public/fontawesome/svgs/brands/vimeo-v.svg
 D public/fontawesome/svgs/brands/vimeo.svg
 D public/fontawesome/svgs/brands/vine.svg
 D public/fontawesome/svgs/brands/vk.svg
 D public/fontawesome/svgs/brands/vnv.svg
 D public/fontawesome/svgs/brands/vuejs.svg
 D public/fontawesome/svgs/brands/watchman-monitoring.svg
 D public/fontawesome/svgs/brands/waze.svg
 D public/fontawesome/svgs/brands/weebly.svg
 D public/fontawesome/svgs/brands/weibo.svg
 D public/fontawesome/svgs/brands/weixin.svg
 D public/fontawesome/svgs/brands/whatsapp.svg
 D public/fontawesome/svgs/brands/whmcs.svg
 D public/fontawesome/svgs/brands/wikipedia-w.svg
 D public/fontawesome/svgs/brands/windows.svg
 D public/fontawesome/svgs/brands/wirsindhandwerk.svg
 D public/fontawesome/svgs/brands/wix.svg
 D public/fontawesome/svgs/brands/wizards-of-the-coast.svg
 D public/fontawesome/svgs/brands/wodu.svg
 D public/fontawesome/svgs/brands/wolf-pack-battalion.svg
 D public/fontawesome/svgs/brands/wordpress-simple.svg
 D public/fontawesome/svgs/brands/wordpress.svg
 D public/fontawesome/svgs/brands/wpbeginner.svg
 D public/fontawesome/svgs/brands/wpexplorer.svg
 D public/fontawesome/svgs/brands/wpforms.svg
 D public/fontawesome/svgs/brands/wpressr.svg
 D public/fontawesome/svgs/brands/x-twitter.svg
 D public/fontawesome/svgs/brands/xbox.svg
 D public/fontawesome/svgs/brands/xing.svg
 D public/fontawesome/svgs/brands/y-combinator.svg
 D public/fontawesome/svgs/brands/yahoo.svg
 D public/fontawesome/svgs/brands/yammer.svg
 D public/fontawesome/svgs/brands/yandex-international.svg
 D public/fontawesome/svgs/brands/yandex.svg
 D public/fontawesome/svgs/brands/yarn.svg
 D public/fontawesome/svgs/brands/yelp.svg
 D public/fontawesome/svgs/brands/yoast.svg
 D public/fontawesome/svgs/brands/youtube.svg
 D public/fontawesome/svgs/brands/zhihu.svg
 D public/fontawesome/svgs/regular/address-book.svg
 D public/fontawesome/svgs/regular/address-card.svg
 D public/fontawesome/svgs/regular/bell-slash.svg
 D public/fontawesome/svgs/regular/bell.svg
 D public/fontawesome/svgs/regular/bookmark.svg
 D public/fontawesome/svgs/regular/building.svg
 D public/fontawesome/svgs/regular/calendar-check.svg
 D public/fontawesome/svgs/regular/calendar-days.svg
 D public/fontawesome/svgs/regular/calendar-minus.svg
 D public/fontawesome/svgs/regular/calendar-plus.svg
 D public/fontawesome/svgs/regular/calendar-xmark.svg
 D public/fontawesome/svgs/regular/calendar.svg
 D public/fontawesome/svgs/regular/chart-bar.svg
 D public/fontawesome/svgs/regular/chess-bishop.svg
 D public/fontawesome/svgs/regular/chess-king.svg
 D public/fontawesome/svgs/regular/chess-knight.svg
 D public/fontawesome/svgs/regular/chess-pawn.svg
 D public/fontawesome/svgs/regular/chess-queen.svg
 D public/fontawesome/svgs/regular/chess-rook.svg
 D public/fontawesome/svgs/regular/circle-check.svg
 D public/fontawesome/svgs/regular/circle-dot.svg
 D public/fontawesome/svgs/regular/circle-down.svg
 D public/fontawesome/svgs/regular/circle-left.svg
 D public/fontawesome/svgs/regular/circle-pause.svg
 D public/fontawesome/svgs/regular/circle-play.svg
 D public/fontawesome/svgs/regular/circle-question.svg
 D public/fontawesome/svgs/regular/circle-right.svg
 D public/fontawesome/svgs/regular/circle-stop.svg
 D public/fontawesome/svgs/regular/circle-up.svg
 D public/fontawesome/svgs/regular/circle-user.svg
 D public/fontawesome/svgs/regular/circle-xmark.svg
 D public/fontawesome/svgs/regular/circle.svg
 D public/fontawesome/svgs/regular/clipboard.svg
 D public/fontawesome/svgs/regular/clock.svg
 D public/fontawesome/svgs/regular/clone.svg
 D public/fontawesome/svgs/regular/closed-captioning.svg
 D public/fontawesome/svgs/regular/comment-dots.svg
 D public/fontawesome/svgs/regular/comment.svg
 D public/fontawesome/svgs/regular/comments.svg
 D public/fontawesome/svgs/regular/compass.svg
 D public/fontawesome/svgs/regular/copy.svg
 D public/fontawesome/svgs/regular/copyright.svg
 D public/fontawesome/svgs/regular/credit-card.svg
 D public/fontawesome/svgs/regular/envelope-open.svg
 D public/fontawesome/svgs/regular/envelope.svg
 D public/fontawesome/svgs/regular/eye-slash.svg
 D public/fontawesome/svgs/regular/eye.svg
 D public/fontawesome/svgs/regular/face-angry.svg
 D public/fontawesome/svgs/regular/face-dizzy.svg
 D public/fontawesome/svgs/regular/face-flushed.svg
 D public/fontawesome/svgs/regular/face-frown-open.svg
 D public/fontawesome/svgs/regular/face-frown.svg
 D public/fontawesome/svgs/regular/face-grimace.svg
 D public/fontawesome/svgs/regular/face-grin-beam-sweat.svg
 D public/fontawesome/svgs/regular/face-grin-beam.svg
 D public/fontawesome/svgs/regular/face-grin-hearts.svg
 D public/fontawesome/svgs/regular/face-grin-squint-tears.svg
 D public/fontawesome/svgs/regular/face-grin-squint.svg
 D public/fontawesome/svgs/regular/face-grin-stars.svg
 D public/fontawesome/svgs/regular/face-grin-tears.svg
 D public/fontawesome/svgs/regular/face-grin-tongue-squint.svg
 D public/fontawesome/svgs/regular/face-grin-tongue-wink.svg
 D public/fontawesome/svgs/regular/face-grin-tongue.svg
 D public/fontawesome/svgs/regular/face-grin-wide.svg
 D public/fontawesome/svgs/regular/face-grin-wink.svg
 D public/fontawesome/svgs/regular/face-grin.svg
 D public/fontawesome/svgs/regular/face-kiss-beam.svg
 D public/fontawesome/svgs/regular/face-kiss-wink-heart.svg
 D public/fontawesome/svgs/regular/face-kiss.svg
 D public/fontawesome/svgs/regular/face-laugh-beam.svg
 D public/fontawesome/svgs/regular/face-laugh-squint.svg
 D public/fontawesome/svgs/regular/face-laugh-wink.svg
 D public/fontawesome/svgs/regular/face-laugh.svg
 D public/fontawesome/svgs/regular/face-meh-blank.svg
 D public/fontawesome/svgs/regular/face-meh.svg
 D public/fontawesome/svgs/regular/face-rolling-eyes.svg
 D public/fontawesome/svgs/regular/face-sad-cry.svg
 D public/fontawesome/svgs/regular/face-sad-tear.svg
 D public/fontawesome/svgs/regular/face-smile-beam.svg
 D public/fontawesome/svgs/regular/face-smile-wink.svg
 D public/fontawesome/svgs/regular/face-smile.svg
 D public/fontawesome/svgs/regular/face-surprise.svg
 D public/fontawesome/svgs/regular/face-tired.svg
 D public/fontawesome/svgs/regular/file-audio.svg
 D public/fontawesome/svgs/regular/file-code.svg
 D public/fontawesome/svgs/regular/file-excel.svg
 D public/fontawesome/svgs/regular/file-image.svg
 D public/fontawesome/svgs/regular/file-lines.svg
 D public/fontawesome/svgs/regular/file-pdf.svg
 D public/fontawesome/svgs/regular/file-powerpoint.svg
 D public/fontawesome/svgs/regular/file-video.svg
 D public/fontawesome/svgs/regular/file-word.svg
 D public/fontawesome/svgs/regular/file-zipper.svg
 D public/fontawesome/svgs/regular/file.svg
 D public/fontawesome/svgs/regular/flag.svg
 D public/fontawesome/svgs/regular/floppy-disk.svg
 D public/fontawesome/svgs/regular/folder-closed.svg
 D public/fontawesome/svgs/regular/folder-open.svg
 D public/fontawesome/svgs/regular/folder.svg
 D public/fontawesome/svgs/regular/font-awesome.svg
 D public/fontawesome/svgs/regular/futbol.svg
 D public/fontawesome/svgs/regular/gem.svg
 D public/fontawesome/svgs/regular/hand-back-fist.svg
 D public/fontawesome/svgs/regular/hand-lizard.svg
 D public/fontawesome/svgs/regular/hand-peace.svg
 D public/fontawesome/svgs/regular/hand-point-down.svg
 D public/fontawesome/svgs/regular/hand-point-left.svg
 D public/fontawesome/svgs/regular/hand-point-right.svg
 D public/fontawesome/svgs/regular/hand-point-up.svg
 D public/fontawesome/svgs/regular/hand-pointer.svg
 D public/fontawesome/svgs/regular/hand-scissors.svg
 D public/fontawesome/svgs/regular/hand-spock.svg
 D public/fontawesome/svgs/regular/hand.svg
 D public/fontawesome/svgs/regular/handshake.svg
 D public/fontawesome/svgs/regular/hard-drive.svg
 D public/fontawesome/svgs/regular/heart.svg
 D public/fontawesome/svgs/regular/hospital.svg
 D public/fontawesome/svgs/regular/hourglass-half.svg
 D public/fontawesome/svgs/regular/hourglass.svg
 D public/fontawesome/svgs/regular/id-badge.svg
 D public/fontawesome/svgs/regular/id-card.svg
 D public/fontawesome/svgs/regular/image.svg
 D public/fontawesome/svgs/regular/images.svg
 D public/fontawesome/svgs/regular/keyboard.svg
 D public/fontawesome/svgs/regular/lemon.svg
 D public/fontawesome/svgs/regular/life-ring.svg
 D public/fontawesome/svgs/regular/lightbulb.svg
 D public/fontawesome/svgs/regular/map.svg
 D public/fontawesome/svgs/regular/message.svg
 D public/fontawesome/svgs/regular/money-bill-1.svg
 D public/fontawesome/svgs/regular/moon.svg
 D public/fontawesome/svgs/regular/newspaper.svg
 D public/fontawesome/svgs/regular/note-sticky.svg
 D public/fontawesome/svgs/regular/object-group.svg
 D public/fontawesome/svgs/regular/object-ungroup.svg
 D public/fontawesome/svgs/regular/paper-plane.svg
 D public/fontawesome/svgs/regular/paste.svg
 D public/fontawesome/svgs/regular/pen-to-square.svg
 D public/fontawesome/svgs/regular/rectangle-list.svg
 D public/fontawesome/svgs/regular/rectangle-xmark.svg
 D public/fontawesome/svgs/regular/registered.svg
 D public/fontawesome/svgs/regular/share-from-square.svg
 D public/fontawesome/svgs/regular/snowflake.svg
 D public/fontawesome/svgs/regular/square-caret-down.svg
 D public/fontawesome/svgs/regular/square-caret-left.svg
 D public/fontawesome/svgs/regular/square-caret-right.svg
 D public/fontawesome/svgs/regular/square-caret-up.svg
 D public/fontawesome/svgs/regular/square-check.svg
 D public/fontawesome/svgs/regular/square-full.svg
 D public/fontawesome/svgs/regular/square-minus.svg
 D public/fontawesome/svgs/regular/square-plus.svg
 D public/fontawesome/svgs/regular/square.svg
 D public/fontawesome/svgs/regular/star-half-stroke.svg
 D public/fontawesome/svgs/regular/star-half.svg
 D public/fontawesome/svgs/regular/star.svg
 D public/fontawesome/svgs/regular/sun.svg
 D public/fontawesome/svgs/regular/thumbs-down.svg
 D public/fontawesome/svgs/regular/thumbs-up.svg
 D public/fontawesome/svgs/regular/trash-can.svg
 D public/fontawesome/svgs/regular/user.svg
 D public/fontawesome/svgs/regular/window-maximize.svg
 D public/fontawesome/svgs/regular/window-minimize.svg
 D public/fontawesome/svgs/regular/window-restore.svg
 D public/fontawesome/svgs/solid/0.svg
 D public/fontawesome/svgs/solid/1.svg
 D public/fontawesome/svgs/solid/2.svg
 D public/fontawesome/svgs/solid/3.svg
 D public/fontawesome/svgs/solid/4.svg
 D public/fontawesome/svgs/solid/5.svg
 D public/fontawesome/svgs/solid/6.svg
 D public/fontawesome/svgs/solid/7.svg
 D public/fontawesome/svgs/solid/8.svg
 D public/fontawesome/svgs/solid/9.svg
 D public/fontawesome/svgs/solid/a.svg
 D public/fontawesome/svgs/solid/address-book.svg
 D public/fontawesome/svgs/solid/address-card.svg
 D public/fontawesome/svgs/solid/align-center.svg
 D public/fontawesome/svgs/solid/align-justify.svg
 D public/fontawesome/svgs/solid/align-left.svg
 D public/fontawesome/svgs/solid/align-right.svg
 D public/fontawesome/svgs/solid/anchor-circle-check.svg
 D public/fontawesome/svgs/solid/anchor-circle-exclamation.svg
 D public/fontawesome/svgs/solid/anchor-circle-xmark.svg
 D public/fontawesome/svgs/solid/anchor-lock.svg
 D public/fontawesome/svgs/solid/anchor.svg
 D public/fontawesome/svgs/solid/angle-down.svg
 D public/fontawesome/svgs/solid/angle-left.svg
 D public/fontawesome/svgs/solid/angle-right.svg
 D public/fontawesome/svgs/solid/angle-up.svg
 D public/fontawesome/svgs/solid/angles-down.svg
 D public/fontawesome/svgs/solid/angles-left.svg
 D public/fontawesome/svgs/solid/angles-right.svg
 D public/fontawesome/svgs/solid/angles-up.svg
 D public/fontawesome/svgs/solid/ankh.svg
 D public/fontawesome/svgs/solid/apple-whole.svg
 D public/fontawesome/svgs/solid/archway.svg
 D public/fontawesome/svgs/solid/arrow-down-1-9.svg
 D public/fontawesome/svgs/solid/arrow-down-9-1.svg
 D public/fontawesome/svgs/solid/arrow-down-a-z.svg
 D public/fontawesome/svgs/solid/arrow-down-long.svg
 D public/fontawesome/svgs/solid/arrow-down-short-wide.svg
 D public/fontawesome/svgs/solid/arrow-down-up-across-line.svg
 D public/fontawesome/svgs/solid/arrow-down-up-lock.svg
 D public/fontawesome/svgs/solid/arrow-down-wide-short.svg
 D public/fontawesome/svgs/solid/arrow-down-z-a.svg
 D public/fontawesome/svgs/solid/arrow-down.svg
 D public/fontawesome/svgs/solid/arrow-left-long.svg
 D public/fontawesome/svgs/solid/arrow-left.svg
 D public/fontawesome/svgs/solid/arrow-pointer.svg
 D public/fontawesome/svgs/solid/arrow-right-arrow-left.svg
 D public/fontawesome/svgs/solid/arrow-right-from-bracket.svg
 D public/fontawesome/svgs/solid/arrow-right-long.svg
 D public/fontawesome/svgs/solid/arrow-right-to-bracket.svg
 D public/fontawesome/svgs/solid/arrow-right-to-city.svg
 D public/fontawesome/svgs/solid/arrow-right.svg
 D public/fontawesome/svgs/solid/arrow-rotate-left.svg
 D public/fontawesome/svgs/solid/arrow-rotate-right.svg
 D public/fontawesome/svgs/solid/arrow-trend-down.svg
 D public/fontawesome/svgs/solid/arrow-trend-up.svg
 D public/fontawesome/svgs/solid/arrow-turn-down.svg
 D public/fontawesome/svgs/solid/arrow-turn-up.svg
 D public/fontawesome/svgs/solid/arrow-up-1-9.svg
 D public/fontawesome/svgs/solid/arrow-up-9-1.svg
 D public/fontawesome/svgs/solid/arrow-up-a-z.svg
 D public/fontawesome/svgs/solid/arrow-up-from-bracket.svg
 D public/fontawesome/svgs/solid/arrow-up-from-ground-water.svg
 D public/fontawesome/svgs/solid/arrow-up-from-water-pump.svg
 D public/fontawesome/svgs/solid/arrow-up-long.svg
 D public/fontawesome/svgs/solid/arrow-up-right-dots.svg
 D public/fontawesome/svgs/solid/arrow-up-right-from-square.svg
 D public/fontawesome/svgs/solid/arrow-up-short-wide.svg
 D public/fontawesome/svgs/solid/arrow-up-wide-short.svg
 D public/fontawesome/svgs/solid/arrow-up-z-a.svg
 D public/fontawesome/svgs/solid/arrow-up.svg
 D public/fontawesome/svgs/solid/arrows-down-to-line.svg
 D public/fontawesome/svgs/solid/arrows-down-to-people.svg
 D public/fontawesome/svgs/solid/arrows-left-right-to-line.svg
 D public/fontawesome/svgs/solid/arrows-left-right.svg
 D public/fontawesome/svgs/solid/arrows-rotate.svg
 D public/fontawesome/svgs/solid/arrows-spin.svg
 D public/fontawesome/svgs/solid/arrows-split-up-and-left.svg
 D public/fontawesome/svgs/solid/arrows-to-circle.svg
 D public/fontawesome/svgs/solid/arrows-to-dot.svg
 D public/fontawesome/svgs/solid/arrows-to-eye.svg
 D public/fontawesome/svgs/solid/arrows-turn-right.svg
 D public/fontawesome/svgs/solid/arrows-turn-to-dots.svg
 D public/fontawesome/svgs/solid/arrows-up-down-left-right.svg
 D public/fontawesome/svgs/solid/arrows-up-down.svg
 D public/fontawesome/svgs/solid/arrows-up-to-line.svg
 D public/fontawesome/svgs/solid/asterisk.svg
 D public/fontawesome/svgs/solid/at.svg
 D public/fontawesome/svgs/solid/atom.svg
 D public/fontawesome/svgs/solid/audio-description.svg
 D public/fontawesome/svgs/solid/austral-sign.svg
 D public/fontawesome/svgs/solid/award.svg
 D public/fontawesome/svgs/solid/b.svg
 D public/fontawesome/svgs/solid/baby-carriage.svg
 D public/fontawesome/svgs/solid/baby.svg
 D public/fontawesome/svgs/solid/backward-fast.svg
 D public/fontawesome/svgs/solid/backward-step.svg
 D public/fontawesome/svgs/solid/backward.svg
 D public/fontawesome/svgs/solid/bacon.svg
 D public/fontawesome/svgs/solid/bacteria.svg
 D public/fontawesome/svgs/solid/bacterium.svg
 D public/fontawesome/svgs/solid/bag-shopping.svg
 D public/fontawesome/svgs/solid/bahai.svg
 D public/fontawesome/svgs/solid/baht-sign.svg
 D public/fontawesome/svgs/solid/ban-smoking.svg
 D public/fontawesome/svgs/solid/ban.svg
 D public/fontawesome/svgs/solid/bandage.svg
 D public/fontawesome/svgs/solid/bangladeshi-taka-sign.svg
 D public/fontawesome/svgs/solid/barcode.svg
 D public/fontawesome/svgs/solid/bars-progress.svg
 D public/fontawesome/svgs/solid/bars-staggered.svg
 D public/fontawesome/svgs/solid/bars.svg
 D public/fontawesome/svgs/solid/baseball-bat-ball.svg
 D public/fontawesome/svgs/solid/baseball.svg
 D public/fontawesome/svgs/solid/basket-shopping.svg
 D public/fontawesome/svgs/solid/basketball.svg
 D public/fontawesome/svgs/solid/bath.svg
 D public/fontawesome/svgs/solid/battery-empty.svg
 D public/fontawesome/svgs/solid/battery-full.svg
 D public/fontawesome/svgs/solid/battery-half.svg
 D public/fontawesome/svgs/solid/battery-quarter.svg
 D public/fontawesome/svgs/solid/battery-three-quarters.svg
 D public/fontawesome/svgs/solid/bed-pulse.svg
 D public/fontawesome/svgs/solid/bed.svg
 D public/fontawesome/svgs/solid/beer-mug-empty.svg
 D public/fontawesome/svgs/solid/bell-concierge.svg
 D public/fontawesome/svgs/solid/bell-slash.svg
 D public/fontawesome/svgs/solid/bell.svg
 D public/fontawesome/svgs/solid/bezier-curve.svg
 D public/fontawesome/svgs/solid/bicycle.svg
 D public/fontawesome/svgs/solid/binoculars.svg
 D public/fontawesome/svgs/solid/biohazard.svg
 D public/fontawesome/svgs/solid/bitcoin-sign.svg
 D public/fontawesome/svgs/solid/blender-phone.svg
 D public/fontawesome/svgs/solid/blender.svg
 D public/fontawesome/svgs/solid/blog.svg
 D public/fontawesome/svgs/solid/bold.svg
 D public/fontawesome/svgs/solid/bolt-lightning.svg
 D public/fontawesome/svgs/solid/bolt.svg
 D public/fontawesome/svgs/solid/bomb.svg
 D public/fontawesome/svgs/solid/bone.svg
 D public/fontawesome/svgs/solid/bong.svg
 D public/fontawesome/svgs/solid/book-atlas.svg
 D public/fontawesome/svgs/solid/book-bible.svg
 D public/fontawesome/svgs/solid/book-bookmark.svg
 D public/fontawesome/svgs/solid/book-journal-whills.svg
 D public/fontawesome/svgs/solid/book-medical.svg
 D public/fontawesome/svgs/solid/book-open-reader.svg
 D public/fontawesome/svgs/solid/book-open.svg
 D public/fontawesome/svgs/solid/book-quran.svg
 D public/fontawesome/svgs/solid/book-skull.svg
 D public/fontawesome/svgs/solid/book-tanakh.svg
 D public/fontawesome/svgs/solid/book.svg
 D public/fontawesome/svgs/solid/bookmark.svg
 D public/fontawesome/svgs/solid/border-all.svg
 D public/fontawesome/svgs/solid/border-none.svg
 D public/fontawesome/svgs/solid/border-top-left.svg
 D public/fontawesome/svgs/solid/bore-hole.svg
 D public/fontawesome/svgs/solid/bottle-droplet.svg
 D public/fontawesome/svgs/solid/bottle-water.svg
 D public/fontawesome/svgs/solid/bowl-food.svg
 D public/fontawesome/svgs/solid/bowl-rice.svg
 D public/fontawesome/svgs/solid/bowling-ball.svg
 D public/fontawesome/svgs/solid/box-archive.svg
 D public/fontawesome/svgs/solid/box-open.svg
 D public/fontawesome/svgs/solid/box-tissue.svg
 D public/fontawesome/svgs/solid/box.svg
 D public/fontawesome/svgs/solid/boxes-packing.svg
 D public/fontawesome/svgs/solid/boxes-stacked.svg
 D public/fontawesome/svgs/solid/braille.svg
 D public/fontawesome/svgs/solid/brain.svg
 D public/fontawesome/svgs/solid/brazilian-real-sign.svg
 D public/fontawesome/svgs/solid/bread-slice.svg
 D public/fontawesome/svgs/solid/bridge-circle-check.svg
 D public/fontawesome/svgs/solid/bridge-circle-exclamation.svg
 D public/fontawesome/svgs/solid/bridge-circle-xmark.svg
 D public/fontawesome/svgs/solid/bridge-lock.svg
 D public/fontawesome/svgs/solid/bridge-water.svg
 D public/fontawesome/svgs/solid/bridge.svg
 D public/fontawesome/svgs/solid/briefcase-medical.svg
 D public/fontawesome/svgs/solid/briefcase.svg
 D public/fontawesome/svgs/solid/broom-ball.svg
 D public/fontawesome/svgs/solid/broom.svg
 D public/fontawesome/svgs/solid/brush.svg
 D public/fontawesome/svgs/solid/bucket.svg
 D public/fontawesome/svgs/solid/bug-slash.svg
 D public/fontawesome/svgs/solid/bug.svg
 D public/fontawesome/svgs/solid/bugs.svg
 D public/fontawesome/svgs/solid/building-circle-arrow-right.svg
 D public/fontawesome/svgs/solid/building-circle-check.svg
 D public/fontawesome/svgs/solid/building-circle-exclamation.svg
 D public/fontawesome/svgs/solid/building-circle-xmark.svg
 D public/fontawesome/svgs/solid/building-columns.svg
 D public/fontawesome/svgs/solid/building-flag.svg
 D public/fontawesome/svgs/solid/building-lock.svg
 D public/fontawesome/svgs/solid/building-ngo.svg
 D public/fontawesome/svgs/solid/building-shield.svg
 D public/fontawesome/svgs/solid/building-un.svg
 D public/fontawesome/svgs/solid/building-user.svg
 D public/fontawesome/svgs/solid/building-wheat.svg
 D public/fontawesome/svgs/solid/building.svg
 D public/fontawesome/svgs/solid/bullhorn.svg
 D public/fontawesome/svgs/solid/bullseye.svg
 D public/fontawesome/svgs/solid/burger.svg
 D public/fontawesome/svgs/solid/burst.svg
 D public/fontawesome/svgs/solid/bus-simple.svg
 D public/fontawesome/svgs/solid/bus.svg
 D public/fontawesome/svgs/solid/business-time.svg
 D public/fontawesome/svgs/solid/c.svg
 D public/fontawesome/svgs/solid/cable-car.svg
 D public/fontawesome/svgs/solid/cake-candles.svg
 D public/fontawesome/svgs/solid/calculator.svg
 D public/fontawesome/svgs/solid/calendar-check.svg
 D public/fontawesome/svgs/solid/calendar-day.svg
 D public/fontawesome/svgs/solid/calendar-days.svg
 D public/fontawesome/svgs/solid/calendar-minus.svg
 D public/fontawesome/svgs/solid/calendar-plus.svg
 D public/fontawesome/svgs/solid/calendar-week.svg
 D public/fontawesome/svgs/solid/calendar-xmark.svg
 D public/fontawesome/svgs/solid/calendar.svg
 D public/fontawesome/svgs/solid/camera-retro.svg
 D public/fontawesome/svgs/solid/camera-rotate.svg
 D public/fontawesome/svgs/solid/camera.svg
 D public/fontawesome/svgs/solid/campground.svg
 D public/fontawesome/svgs/solid/candy-cane.svg
 D public/fontawesome/svgs/solid/cannabis.svg
 D public/fontawesome/svgs/solid/capsules.svg
 D public/fontawesome/svgs/solid/car-battery.svg
 D public/fontawesome/svgs/solid/car-burst.svg
 D public/fontawesome/svgs/solid/car-on.svg
 D public/fontawesome/svgs/solid/car-rear.svg
 D public/fontawesome/svgs/solid/car-side.svg
 D public/fontawesome/svgs/solid/car-tunnel.svg
 D public/fontawesome/svgs/solid/car.svg
 D public/fontawesome/svgs/solid/caravan.svg
 D public/fontawesome/svgs/solid/caret-down.svg
 D public/fontawesome/svgs/solid/caret-left.svg
 D public/fontawesome/svgs/solid/caret-right.svg
 D public/fontawesome/svgs/solid/caret-up.svg
 D public/fontawesome/svgs/solid/carrot.svg
 D public/fontawesome/svgs/solid/cart-arrow-down.svg
 D public/fontawesome/svgs/solid/cart-flatbed-suitcase.svg
 D public/fontawesome/svgs/solid/cart-flatbed.svg
 D public/fontawesome/svgs/solid/cart-plus.svg
 D public/fontawesome/svgs/solid/cart-shopping.svg
 D public/fontawesome/svgs/solid/cash-register.svg
 D public/fontawesome/svgs/solid/cat.svg
 D public/fontawesome/svgs/solid/cedi-sign.svg
 D public/fontawesome/svgs/solid/cent-sign.svg
 D public/fontawesome/svgs/solid/certificate.svg
 D public/fontawesome/svgs/solid/chair.svg
 D public/fontawesome/svgs/solid/chalkboard-user.svg
 D public/fontawesome/svgs/solid/chalkboard.svg
 D public/fontawesome/svgs/solid/champagne-glasses.svg
 D public/fontawesome/svgs/solid/charging-station.svg
 D public/fontawesome/svgs/solid/chart-area.svg
 D public/fontawesome/svgs/solid/chart-bar.svg
 D public/fontawesome/svgs/solid/chart-column.svg
 D public/fontawesome/svgs/solid/chart-gantt.svg
 D public/fontawesome/svgs/solid/chart-line.svg
 D public/fontawesome/svgs/solid/chart-pie.svg
 D public/fontawesome/svgs/solid/chart-simple.svg
 D public/fontawesome/svgs/solid/check-double.svg
 D public/fontawesome/svgs/solid/check-to-slot.svg
 D public/fontawesome/svgs/solid/check.svg
 D public/fontawesome/svgs/solid/cheese.svg
 D public/fontawesome/svgs/solid/chess-bishop.svg
 D public/fontawesome/svgs/solid/chess-board.svg
 D public/fontawesome/svgs/solid/chess-king.svg
 D public/fontawesome/svgs/solid/chess-knight.svg
 D public/fontawesome/svgs/solid/chess-pawn.svg
 D public/fontawesome/svgs/solid/chess-queen.svg
 D public/fontawesome/svgs/solid/chess-rook.svg
 D public/fontawesome/svgs/solid/chess.svg
 D public/fontawesome/svgs/solid/chevron-down.svg
 D public/fontawesome/svgs/solid/chevron-left.svg
 D public/fontawesome/svgs/solid/chevron-right.svg
 D public/fontawesome/svgs/solid/chevron-up.svg
 D public/fontawesome/svgs/solid/child-combatant.svg
 D public/fontawesome/svgs/solid/child-dress.svg
 D public/fontawesome/svgs/solid/child-reaching.svg
 D public/fontawesome/svgs/solid/child.svg
 D public/fontawesome/svgs/solid/children.svg
 D public/fontawesome/svgs/solid/church.svg
 D public/fontawesome/svgs/solid/circle-arrow-down.svg
 D public/fontawesome/svgs/solid/circle-arrow-left.svg
 D public/fontawesome/svgs/solid/circle-arrow-right.svg
 D public/fontawesome/svgs/solid/circle-arrow-up.svg
 D public/fontawesome/svgs/solid/circle-check.svg
 D public/fontawesome/svgs/solid/circle-chevron-down.svg
 D public/fontawesome/svgs/solid/circle-chevron-left.svg
 D public/fontawesome/svgs/solid/circle-chevron-right.svg
 D public/fontawesome/svgs/solid/circle-chevron-up.svg
 D public/fontawesome/svgs/solid/circle-dollar-to-slot.svg
 D public/fontawesome/svgs/solid/circle-dot.svg
 D public/fontawesome/svgs/solid/circle-down.svg
 D public/fontawesome/svgs/solid/circle-exclamation.svg
 D public/fontawesome/svgs/solid/circle-h.svg
 D public/fontawesome/svgs/solid/circle-half-stroke.svg
 D public/fontawesome/svgs/solid/circle-info.svg
 D public/fontawesome/svgs/solid/circle-left.svg
 D public/fontawesome/svgs/solid/circle-minus.svg
 D public/fontawesome/svgs/solid/circle-nodes.svg
 D public/fontawesome/svgs/solid/circle-notch.svg
 D public/fontawesome/svgs/solid/circle-pause.svg
 D public/fontawesome/svgs/solid/circle-play.svg
 D public/fontawesome/svgs/solid/circle-plus.svg
 D public/fontawesome/svgs/solid/circle-question.svg
 D public/fontawesome/svgs/solid/circle-radiation.svg
 D public/fontawesome/svgs/solid/circle-right.svg
 D public/fontawesome/svgs/solid/circle-stop.svg
 D public/fontawesome/svgs/solid/circle-up.svg
 D public/fontawesome/svgs/solid/circle-user.svg
 D public/fontawesome/svgs/solid/circle-xmark.svg
 D public/fontawesome/svgs/solid/circle.svg
 D public/fontawesome/svgs/solid/city.svg
 D public/fontawesome/svgs/solid/clapperboard.svg
 D public/fontawesome/svgs/solid/clipboard-check.svg
 D public/fontawesome/svgs/solid/clipboard-list.svg
 D public/fontawesome/svgs/solid/clipboard-question.svg
 D public/fontawesome/svgs/solid/clipboard-user.svg
 D public/fontawesome/svgs/solid/clipboard.svg
 D public/fontawesome/svgs/solid/clock-rotate-left.svg
 D public/fontawesome/svgs/solid/clock.svg
 D public/fontawesome/svgs/solid/clone.svg
 D public/fontawesome/svgs/solid/closed-captioning.svg
 D public/fontawesome/svgs/solid/cloud-arrow-down.svg
 D public/fontawesome/svgs/solid/cloud-arrow-up.svg
 D public/fontawesome/svgs/solid/cloud-bolt.svg
 D public/fontawesome/svgs/solid/cloud-meatball.svg
 D public/fontawesome/svgs/solid/cloud-moon-rain.svg
 D public/fontawesome/svgs/solid/cloud-moon.svg
 D public/fontawesome/svgs/solid/cloud-rain.svg
 D public/fontawesome/svgs/solid/cloud-showers-heavy.svg
 D public/fontawesome/svgs/solid/cloud-showers-water.svg
 D public/fontawesome/svgs/solid/cloud-sun-rain.svg
 D public/fontawesome/svgs/solid/cloud-sun.svg
 D public/fontawesome/svgs/solid/cloud.svg
 D public/fontawesome/svgs/solid/clover.svg
 D public/fontawesome/svgs/solid/code-branch.svg
 D public/fontawesome/svgs/solid/code-commit.svg
 D public/fontawesome/svgs/solid/code-compare.svg
 D public/fontawesome/svgs/solid/code-fork.svg
 D public/fontawesome/svgs/solid/code-merge.svg
 D public/fontawesome/svgs/solid/code-pull-request.svg
 D public/fontawesome/svgs/solid/code.svg
 D public/fontawesome/svgs/solid/coins.svg
 D public/fontawesome/svgs/solid/colon-sign.svg
 D public/fontawesome/svgs/solid/comment-dollar.svg
 D public/fontawesome/svgs/solid/comment-dots.svg
 D public/fontawesome/svgs/solid/comment-medical.svg
 D public/fontawesome/svgs/solid/comment-slash.svg
 D public/fontawesome/svgs/solid/comment-sms.svg
 D public/fontawesome/svgs/solid/comment.svg
 D public/fontawesome/svgs/solid/comments-dollar.svg
 D public/fontawesome/svgs/solid/comments.svg
 D public/fontawesome/svgs/solid/compact-disc.svg
 D public/fontawesome/svgs/solid/compass-drafting.svg
 D public/fontawesome/svgs/solid/compass.svg
 D public/fontawesome/svgs/solid/compress.svg
 D public/fontawesome/svgs/solid/computer-mouse.svg
 D public/fontawesome/svgs/solid/computer.svg
 D public/fontawesome/svgs/solid/cookie-bite.svg
 D public/fontawesome/svgs/solid/cookie.svg
 D public/fontawesome/svgs/solid/copy.svg
 D public/fontawesome/svgs/solid/copyright.svg
 D public/fontawesome/svgs/solid/couch.svg
 D public/fontawesome/svgs/solid/cow.svg
 D public/fontawesome/svgs/solid/credit-card.svg
 D public/fontawesome/svgs/solid/crop-simple.svg
 D public/fontawesome/svgs/solid/crop.svg
 D public/fontawesome/svgs/solid/cross.svg
 D public/fontawesome/svgs/solid/crosshairs.svg
 D public/fontawesome/svgs/solid/crow.svg
 D public/fontawesome/svgs/solid/crown.svg
 D public/fontawesome/svgs/solid/crutch.svg
 D public/fontawesome/svgs/solid/cruzeiro-sign.svg
 D public/fontawesome/svgs/solid/cube.svg
 D public/fontawesome/svgs/solid/cubes-stacked.svg
 D public/fontawesome/svgs/solid/cubes.svg
 D public/fontawesome/svgs/solid/d.svg
 D public/fontawesome/svgs/solid/database.svg
 D public/fontawesome/svgs/solid/delete-left.svg
 D public/fontawesome/svgs/solid/democrat.svg
 D public/fontawesome/svgs/solid/desktop.svg
 D public/fontawesome/svgs/solid/dharmachakra.svg
 D public/fontawesome/svgs/solid/diagram-next.svg
 D public/fontawesome/svgs/solid/diagram-predecessor.svg
 D public/fontawesome/svgs/solid/diagram-project.svg
 D public/fontawesome/svgs/solid/diagram-successor.svg
 D public/fontawesome/svgs/solid/diamond-turn-right.svg
 D public/fontawesome/svgs/solid/diamond.svg
 D public/fontawesome/svgs/solid/dice-d20.svg
 D public/fontawesome/svgs/solid/dice-d6.svg
 D public/fontawesome/svgs/solid/dice-five.svg
 D public/fontawesome/svgs/solid/dice-four.svg
 D public/fontawesome/svgs/solid/dice-one.svg
 D public/fontawesome/svgs/solid/dice-six.svg
 D public/fontawesome/svgs/solid/dice-three.svg
 D public/fontawesome/svgs/solid/dice-two.svg
 D public/fontawesome/svgs/solid/dice.svg
 D public/fontawesome/svgs/solid/disease.svg
 D public/fontawesome/svgs/solid/display.svg
 D public/fontawesome/svgs/solid/divide.svg
 D public/fontawesome/svgs/solid/dna.svg
 D public/fontawesome/svgs/solid/dog.svg
 D public/fontawesome/svgs/solid/dollar-sign.svg
 D public/fontawesome/svgs/solid/dolly.svg
 D public/fontawesome/svgs/solid/dong-sign.svg
 D public/fontawesome/svgs/solid/door-closed.svg
 D public/fontawesome/svgs/solid/door-open.svg
 D public/fontawesome/svgs/solid/dove.svg
 D public/fontawesome/svgs/solid/down-left-and-up-right-to-center.svg
 D public/fontawesome/svgs/solid/down-long.svg
 D public/fontawesome/svgs/solid/download.svg
 D public/fontawesome/svgs/solid/dragon.svg
 D public/fontawesome/svgs/solid/draw-polygon.svg
 D public/fontawesome/svgs/solid/droplet-slash.svg
 D public/fontawesome/svgs/solid/droplet.svg
 D public/fontawesome/svgs/solid/drum-steelpan.svg
 D public/fontawesome/svgs/solid/drum.svg
 D public/fontawesome/svgs/solid/drumstick-bite.svg
 D public/fontawesome/svgs/solid/dumbbell.svg
 D public/fontawesome/svgs/solid/dumpster-fire.svg
 D public/fontawesome/svgs/solid/dumpster.svg
 D public/fontawesome/svgs/solid/dungeon.svg
 D public/fontawesome/svgs/solid/e.svg
 D public/fontawesome/svgs/solid/ear-deaf.svg
 D public/fontawesome/svgs/solid/ear-listen.svg
 D public/fontawesome/svgs/solid/earth-africa.svg
 D public/fontawesome/svgs/solid/earth-americas.svg
 D public/fontawesome/svgs/solid/earth-asia.svg
 D public/fontawesome/svgs/solid/earth-europe.svg
 D public/fontawesome/svgs/solid/earth-oceania.svg
 D public/fontawesome/svgs/solid/egg.svg
 D public/fontawesome/svgs/solid/eject.svg
 D public/fontawesome/svgs/solid/elevator.svg
 D public/fontawesome/svgs/solid/ellipsis-vertical.svg
 D public/fontawesome/svgs/solid/ellipsis.svg
 D public/fontawesome/svgs/solid/envelope-circle-check.svg
 D public/fontawesome/svgs/solid/envelope-open-text.svg
 D public/fontawesome/svgs/solid/envelope-open.svg
 D public/fontawesome/svgs/solid/envelope.svg
 D public/fontawesome/svgs/solid/envelopes-bulk.svg
 D public/fontawesome/svgs/solid/equals.svg
 D public/fontawesome/svgs/solid/eraser.svg
 D public/fontawesome/svgs/solid/ethernet.svg
 D public/fontawesome/svgs/solid/euro-sign.svg
 D public/fontawesome/svgs/solid/exclamation.svg
 D public/fontawesome/svgs/solid/expand.svg
 D public/fontawesome/svgs/solid/explosion.svg
 D public/fontawesome/svgs/solid/eye-dropper.svg
 D public/fontawesome/svgs/solid/eye-low-vision.svg
 D public/fontawesome/svgs/solid/eye-slash.svg
 D public/fontawesome/svgs/solid/eye.svg
 D public/fontawesome/svgs/solid/f.svg
 D public/fontawesome/svgs/solid/face-angry.svg
 D public/fontawesome/svgs/solid/face-dizzy.svg
 D public/fontawesome/svgs/solid/face-flushed.svg
 D public/fontawesome/svgs/solid/face-frown-open.svg
 D public/fontawesome/svgs/solid/face-frown.svg
 D public/fontawesome/svgs/solid/face-grimace.svg
 D public/fontawesome/svgs/solid/face-grin-beam-sweat.svg
 D public/fontawesome/svgs/solid/face-grin-beam.svg
 D public/fontawesome/svgs/solid/face-grin-hearts.svg
 D public/fontawesome/svgs/solid/face-grin-squint-tears.svg
 D public/fontawesome/svgs/solid/face-grin-squint.svg
 D public/fontawesome/svgs/solid/face-grin-stars.svg
 D public/fontawesome/svgs/solid/face-grin-tears.svg
 D public/fontawesome/svgs/solid/face-grin-tongue-squint.svg
 D public/fontawesome/svgs/solid/face-grin-tongue-wink.svg
 D public/fontawesome/svgs/solid/face-grin-tongue.svg
 D public/fontawesome/svgs/solid/face-grin-wide.svg
 D public/fontawesome/svgs/solid/face-grin-wink.svg
 D public/fontawesome/svgs/solid/face-grin.svg
 D public/fontawesome/svgs/solid/face-kiss-beam.svg
 D public/fontawesome/svgs/solid/face-kiss-wink-heart.svg
 D public/fontawesome/svgs/solid/face-kiss.svg
 D public/fontawesome/svgs/solid/face-laugh-beam.svg
 D public/fontawesome/svgs/solid/face-laugh-squint.svg
 D public/fontawesome/svgs/solid/face-laugh-wink.svg
 D public/fontawesome/svgs/solid/face-laugh.svg
 D public/fontawesome/svgs/solid/face-meh-blank.svg
 D public/fontawesome/svgs/solid/face-meh.svg
 D public/fontawesome/svgs/solid/face-rolling-eyes.svg
 D public/fontawesome/svgs/solid/face-sad-cry.svg
 D public/fontawesome/svgs/solid/face-sad-tear.svg
 D public/fontawesome/svgs/solid/face-smile-beam.svg
 D public/fontawesome/svgs/solid/face-smile-wink.svg
 D public/fontawesome/svgs/solid/face-smile.svg
 D public/fontawesome/svgs/solid/face-surprise.svg
 D public/fontawesome/svgs/solid/face-tired.svg
 D public/fontawesome/svgs/solid/fan.svg
 D public/fontawesome/svgs/solid/faucet-drip.svg
 D public/fontawesome/svgs/solid/faucet.svg
 D public/fontawesome/svgs/solid/fax.svg
 D public/fontawesome/svgs/solid/feather-pointed.svg
 D public/fontawesome/svgs/solid/feather.svg
 D public/fontawesome/svgs/solid/ferry.svg
 D public/fontawesome/svgs/solid/file-arrow-down.svg
 D public/fontawesome/svgs/solid/file-arrow-up.svg
 D public/fontawesome/svgs/solid/file-audio.svg
 D public/fontawesome/svgs/solid/file-circle-check.svg
 D public/fontawesome/svgs/solid/file-circle-exclamation.svg
 D public/fontawesome/svgs/solid/file-circle-minus.svg
 D public/fontawesome/svgs/solid/file-circle-plus.svg
 D public/fontawesome/svgs/solid/file-circle-question.svg
 D public/fontawesome/svgs/solid/file-circle-xmark.svg
 D public/fontawesome/svgs/solid/file-code.svg
 D public/fontawesome/svgs/solid/file-contract.svg
 D public/fontawesome/svgs/solid/file-csv.svg
 D public/fontawesome/svgs/solid/file-excel.svg
 D public/fontawesome/svgs/solid/file-export.svg
 D public/fontawesome/svgs/solid/file-image.svg
 D public/fontawesome/svgs/solid/file-import.svg
 D public/fontawesome/svgs/solid/file-invoice-dollar.svg
 D public/fontawesome/svgs/solid/file-invoice.svg
 D public/fontawesome/svgs/solid/file-lines.svg
 D public/fontawesome/svgs/solid/file-medical.svg
 D public/fontawesome/svgs/solid/file-pdf.svg
 D public/fontawesome/svgs/solid/file-pen.svg
 D public/fontawesome/svgs/solid/file-powerpoint.svg
 D public/fontawesome/svgs/solid/file-prescription.svg
 D public/fontawesome/svgs/solid/file-shield.svg
 D public/fontawesome/svgs/solid/file-signature.svg
 D public/fontawesome/svgs/solid/file-video.svg
 D public/fontawesome/svgs/solid/file-waveform.svg
 D public/fontawesome/svgs/solid/file-word.svg
 D public/fontawesome/svgs/solid/file-zipper.svg
 D public/fontawesome/svgs/solid/file.svg
 D public/fontawesome/svgs/solid/fill-drip.svg
 D public/fontawesome/svgs/solid/fill.svg
 D public/fontawesome/svgs/solid/film.svg
 D public/fontawesome/svgs/solid/filter-circle-dollar.svg
 D public/fontawesome/svgs/solid/filter-circle-xmark.svg
 D public/fontawesome/svgs/solid/filter.svg
 D public/fontawesome/svgs/solid/fingerprint.svg
 D public/fontawesome/svgs/solid/fire-burner.svg
 D public/fontawesome/svgs/solid/fire-extinguisher.svg
 D public/fontawesome/svgs/solid/fire-flame-curved.svg
 D public/fontawesome/svgs/solid/fire-flame-simple.svg
 D public/fontawesome/svgs/solid/fire.svg
 D public/fontawesome/svgs/solid/fish-fins.svg
 D public/fontawesome/svgs/solid/fish.svg
 D public/fontawesome/svgs/solid/flag-checkered.svg
 D public/fontawesome/svgs/solid/flag-usa.svg
 D public/fontawesome/svgs/solid/flag.svg
 D public/fontawesome/svgs/solid/flask-vial.svg
 D public/fontawesome/svgs/solid/flask.svg
 D public/fontawesome/svgs/solid/floppy-disk.svg
 D public/fontawesome/svgs/solid/florin-sign.svg
 D public/fontawesome/svgs/solid/folder-closed.svg
 D public/fontawesome/svgs/solid/folder-minus.svg
 D public/fontawesome/svgs/solid/folder-open.svg
 D public/fontawesome/svgs/solid/folder-plus.svg
 D public/fontawesome/svgs/solid/folder-tree.svg
 D public/fontawesome/svgs/solid/folder.svg
 D public/fontawesome/svgs/solid/font-awesome.svg
 D public/fontawesome/svgs/solid/font.svg
 D public/fontawesome/svgs/solid/football.svg
 D public/fontawesome/svgs/solid/forward-fast.svg
 D public/fontawesome/svgs/solid/forward-step.svg
 D public/fontawesome/svgs/solid/forward.svg
 D public/fontawesome/svgs/solid/franc-sign.svg
 D public/fontawesome/svgs/solid/frog.svg
 D public/fontawesome/svgs/solid/futbol.svg
 D public/fontawesome/svgs/solid/g.svg
 D public/fontawesome/svgs/solid/gamepad.svg
 D public/fontawesome/svgs/solid/gas-pump.svg
 D public/fontawesome/svgs/solid/gauge-high.svg
 D public/fontawesome/svgs/solid/gauge-simple-high.svg
 D public/fontawesome/svgs/solid/gauge-simple.svg
 D public/fontawesome/svgs/solid/gauge.svg
 D public/fontawesome/svgs/solid/gavel.svg
 D public/fontawesome/svgs/solid/gear.svg
 D public/fontawesome/svgs/solid/gears.svg
 D public/fontawesome/svgs/solid/gem.svg
 D public/fontawesome/svgs/solid/genderless.svg
 D public/fontawesome/svgs/solid/ghost.svg
 D public/fontawesome/svgs/solid/gift.svg
 D public/fontawesome/svgs/solid/gifts.svg
 D public/fontawesome/svgs/solid/glass-water-droplet.svg
 D public/fontawesome/svgs/solid/glass-water.svg
 D public/fontawesome/svgs/solid/glasses.svg
 D public/fontawesome/svgs/solid/globe.svg
 D public/fontawesome/svgs/solid/golf-ball-tee.svg
 D public/fontawesome/svgs/solid/gopuram.svg
 D public/fontawesome/svgs/solid/graduation-cap.svg
 D public/fontawesome/svgs/solid/greater-than-equal.svg
 D public/fontawesome/svgs/solid/greater-than.svg
 D public/fontawesome/svgs/solid/grip-lines-vertical.svg
 D public/fontawesome/svgs/solid/grip-lines.svg
 D public/fontawesome/svgs/solid/grip-vertical.svg
 D public/fontawesome/svgs/solid/grip.svg
 D public/fontawesome/svgs/solid/group-arrows-rotate.svg
 D public/fontawesome/svgs/solid/guarani-sign.svg
 D public/fontawesome/svgs/solid/guitar.svg
 D public/fontawesome/svgs/solid/gun.svg
 D public/fontawesome/svgs/solid/h.svg
 D public/fontawesome/svgs/solid/hammer.svg
 D public/fontawesome/svgs/solid/hamsa.svg
 D public/fontawesome/svgs/solid/hand-back-fist.svg
 D public/fontawesome/svgs/solid/hand-dots.svg
 D public/fontawesome/svgs/solid/hand-fist.svg
 D public/fontawesome/svgs/solid/hand-holding-dollar.svg
 D public/fontawesome/svgs/solid/hand-holding-droplet.svg
 D public/fontawesome/svgs/solid/hand-holding-hand.svg
 D public/fontawesome/svgs/solid/hand-holding-heart.svg
 D public/fontawesome/svgs/solid/hand-holding-medical.svg
 D public/fontawesome/svgs/solid/hand-holding.svg
 D public/fontawesome/svgs/solid/hand-lizard.svg
 D public/fontawesome/svgs/solid/hand-middle-finger.svg
 D public/fontawesome/svgs/solid/hand-peace.svg
 D public/fontawesome/svgs/solid/hand-point-down.svg
 D public/fontawesome/svgs/solid/hand-point-left.svg
 D public/fontawesome/svgs/solid/hand-point-right.svg
 D public/fontawesome/svgs/solid/hand-point-up.svg
 D public/fontawesome/svgs/solid/hand-pointer.svg
 D public/fontawesome/svgs/solid/hand-scissors.svg
 D public/fontawesome/svgs/solid/hand-sparkles.svg
 D public/fontawesome/svgs/solid/hand-spock.svg
 D public/fontawesome/svgs/solid/hand.svg
 D public/fontawesome/svgs/solid/handcuffs.svg
 D public/fontawesome/svgs/solid/hands-asl-interpreting.svg
 D public/fontawesome/svgs/solid/hands-bound.svg
 D public/fontawesome/svgs/solid/hands-bubbles.svg
 D public/fontawesome/svgs/solid/hands-clapping.svg
 D public/fontawesome/svgs/solid/hands-holding-child.svg
 D public/fontawesome/svgs/solid/hands-holding-circle.svg
 D public/fontawesome/svgs/solid/hands-holding.svg
 D public/fontawesome/svgs/solid/hands-praying.svg
 D public/fontawesome/svgs/solid/hands.svg
 D public/fontawesome/svgs/solid/handshake-angle.svg
 D public/fontawesome/svgs/solid/handshake-simple-slash.svg
 D public/fontawesome/svgs/solid/handshake-simple.svg
 D public/fontawesome/svgs/solid/handshake-slash.svg
 D public/fontawesome/svgs/solid/handshake.svg
 D public/fontawesome/svgs/solid/hanukiah.svg
 D public/fontawesome/svgs/solid/hard-drive.svg
 D public/fontawesome/svgs/solid/hashtag.svg
 D public/fontawesome/svgs/solid/hat-cowboy-side.svg
 D public/fontawesome/svgs/solid/hat-cowboy.svg
 D public/fontawesome/svgs/solid/hat-wizard.svg
 D public/fontawesome/svgs/solid/head-side-cough-slash.svg
 D public/fontawesome/svgs/solid/head-side-cough.svg
 D public/fontawesome/svgs/solid/head-side-mask.svg
 D public/fontawesome/svgs/solid/head-side-virus.svg
 D public/fontawesome/svgs/solid/heading.svg
 D public/fontawesome/svgs/solid/headphones-simple.svg
 D public/fontawesome/svgs/solid/headphones.svg
 D public/fontawesome/svgs/solid/headset.svg
 D public/fontawesome/svgs/solid/heart-circle-bolt.svg
 D public/fontawesome/svgs/solid/heart-circle-check.svg
 D public/fontawesome/svgs/solid/heart-circle-exclamation.svg
 D public/fontawesome/svgs/solid/heart-circle-minus.svg
 D public/fontawesome/svgs/solid/heart-circle-plus.svg
 D public/fontawesome/svgs/solid/heart-circle-xmark.svg
 D public/fontawesome/svgs/solid/heart-crack.svg
 D public/fontawesome/svgs/solid/heart-pulse.svg
 D public/fontawesome/svgs/solid/heart.svg
 D public/fontawesome/svgs/solid/helicopter-symbol.svg
 D public/fontawesome/svgs/solid/helicopter.svg
 D public/fontawesome/svgs/solid/helmet-safety.svg
 D public/fontawesome/svgs/solid/helmet-un.svg
 D public/fontawesome/svgs/solid/highlighter.svg
 D public/fontawesome/svgs/solid/hill-avalanche.svg
 D public/fontawesome/svgs/solid/hill-rockslide.svg
 D public/fontawesome/svgs/solid/hippo.svg
 D public/fontawesome/svgs/solid/hockey-puck.svg
 D public/fontawesome/svgs/solid/holly-berry.svg
 D public/fontawesome/svgs/solid/horse-head.svg
 D public/fontawesome/svgs/solid/horse.svg
 D public/fontawesome/svgs/solid/hospital-user.svg
 D public/fontawesome/svgs/solid/hospital.svg
 D public/fontawesome/svgs/solid/hot-tub-person.svg
 D public/fontawesome/svgs/solid/hotdog.svg
 D public/fontawesome/svgs/solid/hotel.svg
 D public/fontawesome/svgs/solid/hourglass-end.svg
 D public/fontawesome/svgs/solid/hourglass-half.svg
 D public/fontawesome/svgs/solid/hourglass-start.svg
 D public/fontawesome/svgs/solid/hourglass.svg
 D public/fontawesome/svgs/solid/house-chimney-crack.svg
 D public/fontawesome/svgs/solid/house-chimney-medical.svg
 D public/fontawesome/svgs/solid/house-chimney-user.svg
 D public/fontawesome/svgs/solid/house-chimney-window.svg
 D public/fontawesome/svgs/solid/house-chimney.svg
 D public/fontawesome/svgs/solid/house-circle-check.svg
 D public/fontawesome/svgs/solid/house-circle-exclamation.svg
 D public/fontawesome/svgs/solid/house-circle-xmark.svg
 D public/fontawesome/svgs/solid/house-crack.svg
 D public/fontawesome/svgs/solid/house-fire.svg
 D public/fontawesome/svgs/solid/house-flag.svg
 D public/fontawesome/svgs/solid/house-flood-water-circle-arrow-right.svg
 D public/fontawesome/svgs/solid/house-flood-water.svg
 D public/fontawesome/svgs/solid/house-laptop.svg
 D public/fontawesome/svgs/solid/house-lock.svg
 D public/fontawesome/svgs/solid/house-medical-circle-check.svg
 D public/fontawesome/svgs/solid/house-medical-circle-exclamation.svg
 D public/fontawesome/svgs/solid/house-medical-circle-xmark.svg
 D public/fontawesome/svgs/solid/house-medical-flag.svg
 D public/fontawesome/svgs/solid/house-medical.svg
 D public/fontawesome/svgs/solid/house-signal.svg
 D public/fontawesome/svgs/solid/house-tsunami.svg
 D public/fontawesome/svgs/solid/house-user.svg
 D public/fontawesome/svgs/solid/house.svg
 D public/fontawesome/svgs/solid/hryvnia-sign.svg
 D public/fontawesome/svgs/solid/hurricane.svg
 D public/fontawesome/svgs/solid/i-cursor.svg
 D public/fontawesome/svgs/solid/i.svg
 D public/fontawesome/svgs/solid/ice-cream.svg
 D public/fontawesome/svgs/solid/icicles.svg
 D public/fontawesome/svgs/solid/icons.svg
 D public/fontawesome/svgs/solid/id-badge.svg
 D public/fontawesome/svgs/solid/id-card-clip.svg
 D public/fontawesome/svgs/solid/id-card.svg
 D public/fontawesome/svgs/solid/igloo.svg
 D public/fontawesome/svgs/solid/image-portrait.svg
 D public/fontawesome/svgs/solid/image.svg
 D public/fontawesome/svgs/solid/images.svg
 D public/fontawesome/svgs/solid/inbox.svg
 D public/fontawesome/svgs/solid/indent.svg
 D public/fontawesome/svgs/solid/indian-rupee-sign.svg
 D public/fontawesome/svgs/solid/industry.svg
 D public/fontawesome/svgs/solid/infinity.svg
 D public/fontawesome/svgs/solid/info.svg
 D public/fontawesome/svgs/solid/italic.svg
 D public/fontawesome/svgs/solid/j.svg
 D public/fontawesome/svgs/solid/jar-wheat.svg
 D public/fontawesome/svgs/solid/jar.svg
 D public/fontawesome/svgs/solid/jedi.svg
 D public/fontawesome/svgs/solid/jet-fighter-up.svg
 D public/fontawesome/svgs/solid/jet-fighter.svg
 D public/fontawesome/svgs/solid/joint.svg
 D public/fontawesome/svgs/solid/jug-detergent.svg
 D public/fontawesome/svgs/solid/k.svg
 D public/fontawesome/svgs/solid/kaaba.svg
 D public/fontawesome/svgs/solid/key.svg
 D public/fontawesome/svgs/solid/keyboard.svg
 D public/fontawesome/svgs/solid/khanda.svg
 D public/fontawesome/svgs/solid/kip-sign.svg
 D public/fontawesome/svgs/solid/kit-medical.svg
 D public/fontawesome/svgs/solid/kitchen-set.svg
 D public/fontawesome/svgs/solid/kiwi-bird.svg
 D public/fontawesome/svgs/solid/l.svg
 D public/fontawesome/svgs/solid/land-mine-on.svg
 D public/fontawesome/svgs/solid/landmark-dome.svg
 D public/fontawesome/svgs/solid/landmark-flag.svg
 D public/fontawesome/svgs/solid/landmark.svg
 D public/fontawesome/svgs/solid/language.svg
 D public/fontawesome/svgs/solid/laptop-code.svg
 D public/fontawesome/svgs/solid/laptop-file.svg
 D public/fontawesome/svgs/solid/laptop-medical.svg
 D public/fontawesome/svgs/solid/laptop.svg
 D public/fontawesome/svgs/solid/lari-sign.svg
 D public/fontawesome/svgs/solid/layer-group.svg
 D public/fontawesome/svgs/solid/leaf.svg
 D public/fontawesome/svgs/solid/left-long.svg
 D public/fontawesome/svgs/solid/left-right.svg
 D public/fontawesome/svgs/solid/lemon.svg
 D public/fontawesome/svgs/solid/less-than-equal.svg
 D public/fontawesome/svgs/solid/less-than.svg
 D public/fontawesome/svgs/solid/life-ring.svg
 D public/fontawesome/svgs/solid/lightbulb.svg
 D public/fontawesome/svgs/solid/lines-leaning.svg
 D public/fontawesome/svgs/solid/link-slash.svg
 D public/fontawesome/svgs/solid/link.svg
 D public/fontawesome/svgs/solid/lira-sign.svg
 D public/fontawesome/svgs/solid/list-check.svg
 D public/fontawesome/svgs/solid/list-ol.svg
 D public/fontawesome/svgs/solid/list-ul.svg
 D public/fontawesome/svgs/solid/list.svg
 D public/fontawesome/svgs/solid/litecoin-sign.svg
 D public/fontawesome/svgs/solid/location-arrow.svg
 D public/fontawesome/svgs/solid/location-crosshairs.svg
 D public/fontawesome/svgs/solid/location-dot.svg
 D public/fontawesome/svgs/solid/location-pin-lock.svg
 D public/fontawesome/svgs/solid/location-pin.svg
 D public/fontawesome/svgs/solid/lock-open.svg
 D public/fontawesome/svgs/solid/lock.svg
 D public/fontawesome/svgs/solid/locust.svg
 D public/fontawesome/svgs/solid/lungs-virus.svg
 D public/fontawesome/svgs/solid/lungs.svg
 D public/fontawesome/svgs/solid/m.svg
 D public/fontawesome/svgs/solid/magnet.svg
 D public/fontawesome/svgs/solid/magnifying-glass-arrow-right.svg
 D public/fontawesome/svgs/solid/magnifying-glass-chart.svg
 D public/fontawesome/svgs/solid/magnifying-glass-dollar.svg
 D public/fontawesome/svgs/solid/magnifying-glass-location.svg
 D public/fontawesome/svgs/solid/magnifying-glass-minus.svg
 D public/fontawesome/svgs/solid/magnifying-glass-plus.svg
 D public/fontawesome/svgs/solid/magnifying-glass.svg
 D public/fontawesome/svgs/solid/manat-sign.svg
 D public/fontawesome/svgs/solid/map-location-dot.svg
 D public/fontawesome/svgs/solid/map-location.svg
 D public/fontawesome/svgs/solid/map-pin.svg
 D public/fontawesome/svgs/solid/map.svg
 D public/fontawesome/svgs/solid/marker.svg
 D public/fontawesome/svgs/solid/mars-and-venus-burst.svg
 D public/fontawesome/svgs/solid/mars-and-venus.svg
 D public/fontawesome/svgs/solid/mars-double.svg
 D public/fontawesome/svgs/solid/mars-stroke-right.svg
 D public/fontawesome/svgs/solid/mars-stroke-up.svg
 D public/fontawesome/svgs/solid/mars-stroke.svg
 D public/fontawesome/svgs/solid/mars.svg
 D public/fontawesome/svgs/solid/martini-glass-citrus.svg
 D public/fontawesome/svgs/solid/martini-glass-empty.svg
 D public/fontawesome/svgs/solid/martini-glass.svg
 D public/fontawesome/svgs/solid/mask-face.svg
 D public/fontawesome/svgs/solid/mask-ventilator.svg
 D public/fontawesome/svgs/solid/mask.svg
 D public/fontawesome/svgs/solid/masks-theater.svg
 D public/fontawesome/svgs/solid/mattress-pillow.svg
 D public/fontawesome/svgs/solid/maximize.svg
 D public/fontawesome/svgs/solid/medal.svg
 D public/fontawesome/svgs/solid/memory.svg
 D public/fontawesome/svgs/solid/menorah.svg
 D public/fontawesome/svgs/solid/mercury.svg
 D public/fontawesome/svgs/solid/message.svg
 D public/fontawesome/svgs/solid/meteor.svg
 D public/fontawesome/svgs/solid/microchip.svg
 D public/fontawesome/svgs/solid/microphone-lines-slash.svg
 D public/fontawesome/svgs/solid/microphone-lines.svg
 D public/fontawesome/svgs/solid/microphone-slash.svg
 D public/fontawesome/svgs/solid/microphone.svg
 D public/fontawesome/svgs/solid/microscope.svg
 D public/fontawesome/svgs/solid/mill-sign.svg
 D public/fontawesome/svgs/solid/minimize.svg
 D public/fontawesome/svgs/solid/minus.svg
 D public/fontawesome/svgs/solid/mitten.svg
 D public/fontawesome/svgs/solid/mobile-button.svg
 D public/fontawesome/svgs/solid/mobile-retro.svg
 D public/fontawesome/svgs/solid/mobile-screen-button.svg
 D public/fontawesome/svgs/solid/mobile-screen.svg
 D public/fontawesome/svgs/solid/mobile.svg
 D public/fontawesome/svgs/solid/money-bill-1-wave.svg
 D public/fontawesome/svgs/solid/money-bill-1.svg
 D public/fontawesome/svgs/solid/money-bill-transfer.svg
 D public/fontawesome/svgs/solid/money-bill-trend-up.svg
 D public/fontawesome/svgs/solid/money-bill-wave.svg
 D public/fontawesome/svgs/solid/money-bill-wheat.svg
 D public/fontawesome/svgs/solid/money-bill.svg
 D public/fontawesome/svgs/solid/money-bills.svg
 D public/fontawesome/svgs/solid/money-check-dollar.svg
 D public/fontawesome/svgs/solid/money-check.svg
 D public/fontawesome/svgs/solid/monument.svg
 D public/fontawesome/svgs/solid/moon.svg
 D public/fontawesome/svgs/solid/mortar-pestle.svg
 D public/fontawesome/svgs/solid/mosque.svg
 D public/fontawesome/svgs/solid/mosquito-net.svg
 D public/fontawesome/svgs/solid/mosquito.svg
 D public/fontawesome/svgs/solid/motorcycle.svg
 D public/fontawesome/svgs/solid/mound.svg
 D public/fontawesome/svgs/solid/mountain-city.svg
 D public/fontawesome/svgs/solid/mountain-sun.svg
 D public/fontawesome/svgs/solid/mountain.svg
 D public/fontawesome/svgs/solid/mug-hot.svg
 D public/fontawesome/svgs/solid/mug-saucer.svg
 D public/fontawesome/svgs/solid/music.svg
 D public/fontawesome/svgs/solid/n.svg
 D public/fontawesome/svgs/solid/naira-sign.svg
 D public/fontawesome/svgs/solid/network-wired.svg
 D public/fontawesome/svgs/solid/neuter.svg
 D public/fontawesome/svgs/solid/newspaper.svg
 D public/fontawesome/svgs/solid/not-equal.svg
 D public/fontawesome/svgs/solid/notdef.svg
 D public/fontawesome/svgs/solid/note-sticky.svg
 D public/fontawesome/svgs/solid/notes-medical.svg
 D public/fontawesome/svgs/solid/o.svg
 D public/fontawesome/svgs/solid/object-group.svg
 D public/fontawesome/svgs/solid/object-ungroup.svg
 D public/fontawesome/svgs/solid/oil-can.svg
 D public/fontawesome/svgs/solid/oil-well.svg
 D public/fontawesome/svgs/solid/om.svg
 D public/fontawesome/svgs/solid/otter.svg
 D public/fontawesome/svgs/solid/outdent.svg
 D public/fontawesome/svgs/solid/p.svg
 D public/fontawesome/svgs/solid/pager.svg
 D public/fontawesome/svgs/solid/paint-roller.svg
 D public/fontawesome/svgs/solid/paintbrush.svg
 D public/fontawesome/svgs/solid/palette.svg
 D public/fontawesome/svgs/solid/pallet.svg
 D public/fontawesome/svgs/solid/panorama.svg
 D public/fontawesome/svgs/solid/paper-plane.svg
 D public/fontawesome/svgs/solid/paperclip.svg
 D public/fontawesome/svgs/solid/parachute-box.svg
 D public/fontawesome/svgs/solid/paragraph.svg
 D public/fontawesome/svgs/solid/passport.svg
 D public/fontawesome/svgs/solid/paste.svg
 D public/fontawesome/svgs/solid/pause.svg
 D public/fontawesome/svgs/solid/paw.svg
 D public/fontawesome/svgs/solid/peace.svg
 D public/fontawesome/svgs/solid/pen-clip.svg
 D public/fontawesome/svgs/solid/pen-fancy.svg
 D public/fontawesome/svgs/solid/pen-nib.svg
 D public/fontawesome/svgs/solid/pen-ruler.svg
 D public/fontawesome/svgs/solid/pen-to-square.svg
 D public/fontawesome/svgs/solid/pen.svg
 D public/fontawesome/svgs/solid/pencil.svg
 D public/fontawesome/svgs/solid/people-arrows.svg
 D public/fontawesome/svgs/solid/people-carry-box.svg
 D public/fontawesome/svgs/solid/people-group.svg
 D public/fontawesome/svgs/solid/people-line.svg
 D public/fontawesome/svgs/solid/people-pulling.svg
 D public/fontawesome/svgs/solid/people-robbery.svg
 D public/fontawesome/svgs/solid/people-roof.svg
 D public/fontawesome/svgs/solid/pepper-hot.svg
 D public/fontawesome/svgs/solid/percent.svg
 D public/fontawesome/svgs/solid/person-arrow-down-to-line.svg
 D public/fontawesome/svgs/solid/person-arrow-up-from-line.svg
 D public/fontawesome/svgs/solid/person-biking.svg
 D public/fontawesome/svgs/solid/person-booth.svg
 D public/fontawesome/svgs/solid/person-breastfeeding.svg
 D public/fontawesome/svgs/solid/person-burst.svg
 D public/fontawesome/svgs/solid/person-cane.svg
 D public/fontawesome/svgs/solid/person-chalkboard.svg
 D public/fontawesome/svgs/solid/person-circle-check.svg
 D public/fontawesome/svgs/solid/person-circle-exclamation.svg
 D public/fontawesome/svgs/solid/person-circle-minus.svg
 D public/fontawesome/svgs/solid/person-circle-plus.svg
 D public/fontawesome/svgs/solid/person-circle-question.svg
 D public/fontawesome/svgs/solid/person-circle-xmark.svg
 D public/fontawesome/svgs/solid/person-digging.svg
 D public/fontawesome/svgs/solid/person-dots-from-line.svg
 D public/fontawesome/svgs/solid/person-dress-burst.svg
 D public/fontawesome/svgs/solid/person-dress.svg
 D public/fontawesome/svgs/solid/person-drowning.svg
 D public/fontawesome/svgs/solid/person-falling-burst.svg
 D public/fontawesome/svgs/solid/person-falling.svg
 D public/fontawesome/svgs/solid/person-half-dress.svg
 D public/fontawesome/svgs/solid/person-harassing.svg
 D public/fontawesome/svgs/solid/person-hiking.svg
 D public/fontawesome/svgs/solid/person-military-pointing.svg
 D public/fontawesome/svgs/solid/person-military-rifle.svg
 D public/fontawesome/svgs/solid/person-military-to-person.svg
 D public/fontawesome/svgs/solid/person-praying.svg
 D public/fontawesome/svgs/solid/person-pregnant.svg
 D public/fontawesome/svgs/solid/person-rays.svg
 D public/fontawesome/svgs/solid/person-rifle.svg
 D public/fontawesome/svgs/solid/person-running.svg
 D public/fontawesome/svgs/solid/person-shelter.svg
 D public/fontawesome/svgs/solid/person-skating.svg
 D public/fontawesome/svgs/solid/person-skiing-nordic.svg
 D public/fontawesome/svgs/solid/person-skiing.svg
 D public/fontawesome/svgs/solid/person-snowboarding.svg
 D public/fontawesome/svgs/solid/person-swimming.svg
 D public/fontawesome/svgs/solid/person-through-window.svg
 D public/fontawesome/svgs/solid/person-walking-arrow-loop-left.svg
 D public/fontawesome/svgs/solid/person-walking-arrow-right.svg
 D public/fontawesome/svgs/solid/person-walking-dashed-line-arrow-right.svg
 D public/fontawesome/svgs/solid/person-walking-luggage.svg
 D public/fontawesome/svgs/solid/person-walking-with-cane.svg
 D public/fontawesome/svgs/solid/person-walking.svg
 D public/fontawesome/svgs/solid/person.svg
 D public/fontawesome/svgs/solid/peseta-sign.svg
 D public/fontawesome/svgs/solid/peso-sign.svg
 D public/fontawesome/svgs/solid/phone-flip.svg
 D public/fontawesome/svgs/solid/phone-slash.svg
 D public/fontawesome/svgs/solid/phone-volume.svg
 D public/fontawesome/svgs/solid/phone.svg
 D public/fontawesome/svgs/solid/photo-film.svg
 D public/fontawesome/svgs/solid/piggy-bank.svg
 D public/fontawesome/svgs/solid/pills.svg
 D public/fontawesome/svgs/solid/pizza-slice.svg
 D public/fontawesome/svgs/solid/place-of-worship.svg
 D public/fontawesome/svgs/solid/plane-arrival.svg
 D public/fontawesome/svgs/solid/plane-circle-check.svg
 D public/fontawesome/svgs/solid/plane-circle-exclamation.svg
 D public/fontawesome/svgs/solid/plane-circle-xmark.svg
 D public/fontawesome/svgs/solid/plane-departure.svg
 D public/fontawesome/svgs/solid/plane-lock.svg
 D public/fontawesome/svgs/solid/plane-slash.svg
 D public/fontawesome/svgs/solid/plane-up.svg
 D public/fontawesome/svgs/solid/plane.svg
 D public/fontawesome/svgs/solid/plant-wilt.svg
 D public/fontawesome/svgs/solid/plate-wheat.svg
 D public/fontawesome/svgs/solid/play.svg
 D public/fontawesome/svgs/solid/plug-circle-bolt.svg
 D public/fontawesome/svgs/solid/plug-circle-check.svg
 D public/fontawesome/svgs/solid/plug-circle-exclamation.svg
 D public/fontawesome/svgs/solid/plug-circle-minus.svg
 D public/fontawesome/svgs/solid/plug-circle-plus.svg
 D public/fontawesome/svgs/solid/plug-circle-xmark.svg
 D public/fontawesome/svgs/solid/plug.svg
 D public/fontawesome/svgs/solid/plus-minus.svg
 D public/fontawesome/svgs/solid/plus.svg
 D public/fontawesome/svgs/solid/podcast.svg
 D public/fontawesome/svgs/solid/poo-storm.svg
 D public/fontawesome/svgs/solid/poo.svg
 D public/fontawesome/svgs/solid/poop.svg
 D public/fontawesome/svgs/solid/power-off.svg
 D public/fontawesome/svgs/solid/prescription-bottle-medical.svg
 D public/fontawesome/svgs/solid/prescription-bottle.svg
 D public/fontawesome/svgs/solid/prescription.svg
 D public/fontawesome/svgs/solid/print.svg
 D public/fontawesome/svgs/solid/pump-medical.svg
 D public/fontawesome/svgs/solid/pump-soap.svg
 D public/fontawesome/svgs/solid/puzzle-piece.svg
 D public/fontawesome/svgs/solid/q.svg
 D public/fontawesome/svgs/solid/qrcode.svg
 D public/fontawesome/svgs/solid/question.svg
 D public/fontawesome/svgs/solid/quote-left.svg
 D public/fontawesome/svgs/solid/quote-right.svg
 D public/fontawesome/svgs/solid/r.svg
 D public/fontawesome/svgs/solid/radiation.svg
 D public/fontawesome/svgs/solid/radio.svg
 D public/fontawesome/svgs/solid/rainbow.svg
 D public/fontawesome/svgs/solid/ranking-star.svg
 D public/fontawesome/svgs/solid/receipt.svg
 D public/fontawesome/svgs/solid/record-vinyl.svg
 D public/fontawesome/svgs/solid/rectangle-ad.svg
 D public/fontawesome/svgs/solid/rectangle-list.svg
 D public/fontawesome/svgs/solid/rectangle-xmark.svg
 D public/fontawesome/svgs/solid/recycle.svg
 D public/fontawesome/svgs/solid/registered.svg
 D public/fontawesome/svgs/solid/repeat.svg
 D public/fontawesome/svgs/solid/reply-all.svg
 D public/fontawesome/svgs/solid/reply.svg
 D public/fontawesome/svgs/solid/republican.svg
 D public/fontawesome/svgs/solid/restroom.svg
 D public/fontawesome/svgs/solid/retweet.svg
 D public/fontawesome/svgs/solid/ribbon.svg
 D public/fontawesome/svgs/solid/right-from-bracket.svg
 D public/fontawesome/svgs/solid/right-left.svg
 D public/fontawesome/svgs/solid/right-long.svg
 D public/fontawesome/svgs/solid/right-to-bracket.svg
 D public/fontawesome/svgs/solid/ring.svg
 D public/fontawesome/svgs/solid/road-barrier.svg
 D public/fontawesome/svgs/solid/road-bridge.svg
 D public/fontawesome/svgs/solid/road-circle-check.svg
 D public/fontawesome/svgs/solid/road-circle-exclamation.svg
 D public/fontawesome/svgs/solid/road-circle-xmark.svg
 D public/fontawesome/svgs/solid/road-lock.svg
 D public/fontawesome/svgs/solid/road-spikes.svg
 D public/fontawesome/svgs/solid/road.svg
 D public/fontawesome/svgs/solid/robot.svg
 D public/fontawesome/svgs/solid/rocket.svg
 D public/fontawesome/svgs/solid/rotate-left.svg
 D public/fontawesome/svgs/solid/rotate-right.svg
 D public/fontawesome/svgs/solid/rotate.svg
 D public/fontawesome/svgs/solid/route.svg
 D public/fontawesome/svgs/solid/rss.svg
 D public/fontawesome/svgs/solid/ruble-sign.svg
 D public/fontawesome/svgs/solid/rug.svg
 D public/fontawesome/svgs/solid/ruler-combined.svg
 D public/fontawesome/svgs/solid/ruler-horizontal.svg
 D public/fontawesome/svgs/solid/ruler-vertical.svg
 D public/fontawesome/svgs/solid/ruler.svg
 D public/fontawesome/svgs/solid/rupee-sign.svg
 D public/fontawesome/svgs/solid/rupiah-sign.svg
 D public/fontawesome/svgs/solid/s.svg
 D public/fontawesome/svgs/solid/sack-dollar.svg
 D public/fontawesome/svgs/solid/sack-xmark.svg
 D public/fontawesome/svgs/solid/sailboat.svg
 D public/fontawesome/svgs/solid/satellite-dish.svg
 D public/fontawesome/svgs/solid/satellite.svg
 D public/fontawesome/svgs/solid/scale-balanced.svg
 D public/fontawesome/svgs/solid/scale-unbalanced-flip.svg
 D public/fontawesome/svgs/solid/scale-unbalanced.svg
 D public/fontawesome/svgs/solid/school-circle-check.svg
 D public/fontawesome/svgs/solid/school-circle-exclamation.svg
 D public/fontawesome/svgs/solid/school-circle-xmark.svg
 D public/fontawesome/svgs/solid/school-flag.svg
 D public/fontawesome/svgs/solid/school-lock.svg
 D public/fontawesome/svgs/solid/school.svg
 D public/fontawesome/svgs/solid/scissors.svg
 D public/fontawesome/svgs/solid/screwdriver-wrench.svg
 D public/fontawesome/svgs/solid/screwdriver.svg
 D public/fontawesome/svgs/solid/scroll-torah.svg
 D public/fontawesome/svgs/solid/scroll.svg
 D public/fontawesome/svgs/solid/sd-card.svg
 D public/fontawesome/svgs/solid/section.svg
 D public/fontawesome/svgs/solid/seedling.svg
 D public/fontawesome/svgs/solid/server.svg
 D public/fontawesome/svgs/solid/shapes.svg
 D public/fontawesome/svgs/solid/share-from-square.svg
 D public/fontawesome/svgs/solid/share-nodes.svg
 D public/fontawesome/svgs/solid/share.svg
 D public/fontawesome/svgs/solid/sheet-plastic.svg
 D public/fontawesome/svgs/solid/shekel-sign.svg
 D public/fontawesome/svgs/solid/shield-cat.svg
 D public/fontawesome/svgs/solid/shield-dog.svg
 D public/fontawesome/svgs/solid/shield-halved.svg
 D public/fontawesome/svgs/solid/shield-heart.svg
 D public/fontawesome/svgs/solid/shield-virus.svg
 D public/fontawesome/svgs/solid/shield.svg
 D public/fontawesome/svgs/solid/ship.svg
 D public/fontawesome/svgs/solid/shirt.svg
 D public/fontawesome/svgs/solid/shoe-prints.svg
 D public/fontawesome/svgs/solid/shop-lock.svg
 D public/fontawesome/svgs/solid/shop-slash.svg
 D public/fontawesome/svgs/solid/shop.svg
 D public/fontawesome/svgs/solid/shower.svg
 D public/fontawesome/svgs/solid/shrimp.svg
 D public/fontawesome/svgs/solid/shuffle.svg
 D public/fontawesome/svgs/solid/shuttle-space.svg
 D public/fontawesome/svgs/solid/sign-hanging.svg
 D public/fontawesome/svgs/solid/signal.svg
 D public/fontawesome/svgs/solid/signature.svg
 D public/fontawesome/svgs/solid/signs-post.svg
 D public/fontawesome/svgs/solid/sim-card.svg
 D public/fontawesome/svgs/solid/sink.svg
 D public/fontawesome/svgs/solid/sitemap.svg
 D public/fontawesome/svgs/solid/skull-crossbones.svg
 D public/fontawesome/svgs/solid/skull.svg
 D public/fontawesome/svgs/solid/slash.svg
 D public/fontawesome/svgs/solid/sleigh.svg
 D public/fontawesome/svgs/solid/sliders.svg
 D public/fontawesome/svgs/solid/smog.svg
 D public/fontawesome/svgs/solid/smoking.svg
 D public/fontawesome/svgs/solid/snowflake.svg
 D public/fontawesome/svgs/solid/snowman.svg
 D public/fontawesome/svgs/solid/snowplow.svg
 D public/fontawesome/svgs/solid/soap.svg
 D public/fontawesome/svgs/solid/socks.svg
 D public/fontawesome/svgs/solid/solar-panel.svg
 D public/fontawesome/svgs/solid/sort-down.svg
 D public/fontawesome/svgs/solid/sort-up.svg
 D public/fontawesome/svgs/solid/sort.svg
 D public/fontawesome/svgs/solid/spa.svg
 D public/fontawesome/svgs/solid/spaghetti-monster-flying.svg
 D public/fontawesome/svgs/solid/spell-check.svg
 D public/fontawesome/svgs/solid/spider.svg
 D public/fontawesome/svgs/solid/spinner.svg
 D public/fontawesome/svgs/solid/splotch.svg
 D public/fontawesome/svgs/solid/spoon.svg
 D public/fontawesome/svgs/solid/spray-can-sparkles.svg
 D public/fontawesome/svgs/solid/spray-can.svg
 D public/fontawesome/svgs/solid/square-arrow-up-right.svg
 D public/fontawesome/svgs/solid/square-caret-down.svg
 D public/fontawesome/svgs/solid/square-caret-left.svg
 D public/fontawesome/svgs/solid/square-caret-right.svg
 D public/fontawesome/svgs/solid/square-caret-up.svg
 D public/fontawesome/svgs/solid/square-check.svg
 D public/fontawesome/svgs/solid/square-envelope.svg
 D public/fontawesome/svgs/solid/square-full.svg
 D public/fontawesome/svgs/solid/square-h.svg
 D public/fontawesome/svgs/solid/square-minus.svg
 D public/fontawesome/svgs/solid/square-nfi.svg
 D public/fontawesome/svgs/solid/square-parking.svg
 D public/fontawesome/svgs/solid/square-pen.svg
 D public/fontawesome/svgs/solid/square-person-confined.svg
 D public/fontawesome/svgs/solid/square-phone-flip.svg
 D public/fontawesome/svgs/solid/square-phone.svg
 D public/fontawesome/svgs/solid/square-plus.svg
 D public/fontawesome/svgs/solid/square-poll-horizontal.svg
 D public/fontawesome/svgs/solid/square-poll-vertical.svg
 D public/fontawesome/svgs/solid/square-root-variable.svg
 D public/fontawesome/svgs/solid/square-rss.svg
 D public/fontawesome/svgs/solid/square-share-nodes.svg
 D public/fontawesome/svgs/solid/square-up-right.svg
 D public/fontawesome/svgs/solid/square-virus.svg
 D public/fontawesome/svgs/solid/square-xmark.svg
 D public/fontawesome/svgs/solid/square.svg
 D public/fontawesome/svgs/solid/staff-snake.svg
 D public/fontawesome/svgs/solid/stairs.svg
 D public/fontawesome/svgs/solid/stamp.svg
 D public/fontawesome/svgs/solid/stapler.svg
 D public/fontawesome/svgs/solid/star-and-crescent.svg
 D public/fontawesome/svgs/solid/star-half-stroke.svg
 D public/fontawesome/svgs/solid/star-half.svg
 D public/fontawesome/svgs/solid/star-of-david.svg
 D public/fontawesome/svgs/solid/star-of-life.svg
 D public/fontawesome/svgs/solid/star.svg
 D public/fontawesome/svgs/solid/sterling-sign.svg
 D public/fontawesome/svgs/solid/stethoscope.svg
 D public/fontawesome/svgs/solid/stop.svg
 D public/fontawesome/svgs/solid/stopwatch-20.svg
 D public/fontawesome/svgs/solid/stopwatch.svg
 D public/fontawesome/svgs/solid/store-slash.svg
 D public/fontawesome/svgs/solid/store.svg
 D public/fontawesome/svgs/solid/street-view.svg
 D public/fontawesome/svgs/solid/strikethrough.svg
 D public/fontawesome/svgs/solid/stroopwafel.svg
 D public/fontawesome/svgs/solid/subscript.svg
 D public/fontawesome/svgs/solid/suitcase-medical.svg
 D public/fontawesome/svgs/solid/suitcase-rolling.svg
 D public/fontawesome/svgs/solid/suitcase.svg
 D public/fontawesome/svgs/solid/sun-plant-wilt.svg
 D public/fontawesome/svgs/solid/sun.svg
 D public/fontawesome/svgs/solid/superscript.svg
 D public/fontawesome/svgs/solid/swatchbook.svg
 D public/fontawesome/svgs/solid/synagogue.svg
 D public/fontawesome/svgs/solid/syringe.svg
 D public/fontawesome/svgs/solid/t.svg
 D public/fontawesome/svgs/solid/table-cells-large.svg
 D public/fontawesome/svgs/solid/table-cells.svg
 D public/fontawesome/svgs/solid/table-columns.svg
 D public/fontawesome/svgs/solid/table-list.svg
 D public/fontawesome/svgs/solid/table-tennis-paddle-ball.svg
 D public/fontawesome/svgs/solid/table.svg
 D public/fontawesome/svgs/solid/tablet-button.svg
 D public/fontawesome/svgs/solid/tablet-screen-button.svg
 D public/fontawesome/svgs/solid/tablet.svg
 D public/fontawesome/svgs/solid/tablets.svg
 D public/fontawesome/svgs/solid/tachograph-digital.svg
 D public/fontawesome/svgs/solid/tag.svg
 D public/fontawesome/svgs/solid/tags.svg
 D public/fontawesome/svgs/solid/tape.svg
 D public/fontawesome/svgs/solid/tarp-droplet.svg
 D public/fontawesome/svgs/solid/tarp.svg
 D public/fontawesome/svgs/solid/taxi.svg
 D public/fontawesome/svgs/solid/teeth-open.svg
 D public/fontawesome/svgs/solid/teeth.svg
 D public/fontawesome/svgs/solid/temperature-arrow-down.svg
 D public/fontawesome/svgs/solid/temperature-arrow-up.svg
 D public/fontawesome/svgs/solid/temperature-empty.svg
 D public/fontawesome/svgs/solid/temperature-full.svg
 D public/fontawesome/svgs/solid/temperature-half.svg
 D public/fontawesome/svgs/solid/temperature-high.svg
 D public/fontawesome/svgs/solid/temperature-low.svg
 D public/fontawesome/svgs/solid/temperature-quarter.svg
 D public/fontawesome/svgs/solid/temperature-three-quarters.svg
 D public/fontawesome/svgs/solid/tenge-sign.svg
 D public/fontawesome/svgs/solid/tent-arrow-down-to-line.svg
 D public/fontawesome/svgs/solid/tent-arrow-left-right.svg
 D public/fontawesome/svgs/solid/tent-arrow-turn-left.svg
 D public/fontawesome/svgs/solid/tent-arrows-down.svg
 D public/fontawesome/svgs/solid/tent.svg
 D public/fontawesome/svgs/solid/tents.svg
 D public/fontawesome/svgs/solid/terminal.svg
 D public/fontawesome/svgs/solid/text-height.svg
 D public/fontawesome/svgs/solid/text-slash.svg
 D public/fontawesome/svgs/solid/text-width.svg
 D public/fontawesome/svgs/solid/thermometer.svg
 D public/fontawesome/svgs/solid/thumbs-down.svg
 D public/fontawesome/svgs/solid/thumbs-up.svg
 D public/fontawesome/svgs/solid/thumbtack.svg
 D public/fontawesome/svgs/solid/ticket-simple.svg
 D public/fontawesome/svgs/solid/ticket.svg
 D public/fontawesome/svgs/solid/timeline.svg
 D public/fontawesome/svgs/solid/toggle-off.svg
 D public/fontawesome/svgs/solid/toggle-on.svg
 D public/fontawesome/svgs/solid/toilet-paper-slash.svg
 D public/fontawesome/svgs/solid/toilet-paper.svg
 D public/fontawesome/svgs/solid/toilet-portable.svg
 D public/fontawesome/svgs/solid/toilet.svg
 D public/fontawesome/svgs/solid/toilets-portable.svg
 D public/fontawesome/svgs/solid/toolbox.svg
 D public/fontawesome/svgs/solid/tooth.svg
 D public/fontawesome/svgs/solid/torii-gate.svg
 D public/fontawesome/svgs/solid/tornado.svg
 D public/fontawesome/svgs/solid/tower-broadcast.svg
 D public/fontawesome/svgs/solid/tower-cell.svg
 D public/fontawesome/svgs/solid/tower-observation.svg
 D public/fontawesome/svgs/solid/tractor.svg
 D public/fontawesome/svgs/solid/trademark.svg
 D public/fontawesome/svgs/solid/traffic-light.svg
 D public/fontawesome/svgs/solid/trailer.svg
 D public/fontawesome/svgs/solid/train-subway.svg
 D public/fontawesome/svgs/solid/train-tram.svg
 D public/fontawesome/svgs/solid/train.svg
 D public/fontawesome/svgs/solid/transgender.svg
 D public/fontawesome/svgs/solid/trash-arrow-up.svg
 D public/fontawesome/svgs/solid/trash-can-arrow-up.svg
 D public/fontawesome/svgs/solid/trash-can.svg
 D public/fontawesome/svgs/solid/trash.svg
 D public/fontawesome/svgs/solid/tree-city.svg
 D public/fontawesome/svgs/solid/tree.svg
 D public/fontawesome/svgs/solid/triangle-exclamation.svg
 D public/fontawesome/svgs/solid/trophy.svg
 D public/fontawesome/svgs/solid/trowel-bricks.svg
 D public/fontawesome/svgs/solid/trowel.svg
 D public/fontawesome/svgs/solid/truck-arrow-right.svg
 D public/fontawesome/svgs/solid/truck-droplet.svg
 D public/fontawesome/svgs/solid/truck-fast.svg
 D public/fontawesome/svgs/solid/truck-field-un.svg
 D public/fontawesome/svgs/solid/truck-field.svg
 D public/fontawesome/svgs/solid/truck-front.svg
 D public/fontawesome/svgs/solid/truck-medical.svg
 D public/fontawesome/svgs/solid/truck-monster.svg
 D public/fontawesome/svgs/solid/truck-moving.svg
 D public/fontawesome/svgs/solid/truck-pickup.svg
 D public/fontawesome/svgs/solid/truck-plane.svg
 D public/fontawesome/svgs/solid/truck-ramp-box.svg
 D public/fontawesome/svgs/solid/truck.svg
 D public/fontawesome/svgs/solid/tty.svg
 D public/fontawesome/svgs/solid/turkish-lira-sign.svg
 D public/fontawesome/svgs/solid/turn-down.svg
 D public/fontawesome/svgs/solid/turn-up.svg
 D public/fontawesome/svgs/solid/tv.svg
 D public/fontawesome/svgs/solid/u.svg
 D public/fontawesome/svgs/solid/umbrella-beach.svg
 D public/fontawesome/svgs/solid/umbrella.svg
 D public/fontawesome/svgs/solid/underline.svg
 D public/fontawesome/svgs/solid/universal-access.svg
 D public/fontawesome/svgs/solid/unlock-keyhole.svg
 D public/fontawesome/svgs/solid/unlock.svg
 D public/fontawesome/svgs/solid/up-down-left-right.svg
 D public/fontawesome/svgs/solid/up-down.svg
 D public/fontawesome/svgs/solid/up-long.svg
 D public/fontawesome/svgs/solid/up-right-and-down-left-from-center.svg
 D public/fontawesome/svgs/solid/up-right-from-square.svg
 D public/fontawesome/svgs/solid/upload.svg
 D public/fontawesome/svgs/solid/user-astronaut.svg
 D public/fontawesome/svgs/solid/user-check.svg
 D public/fontawesome/svgs/solid/user-clock.svg
 D public/fontawesome/svgs/solid/user-doctor.svg
 D public/fontawesome/svgs/solid/user-gear.svg
 D public/fontawesome/svgs/solid/user-graduate.svg
 D public/fontawesome/svgs/solid/user-group.svg
 D public/fontawesome/svgs/solid/user-injured.svg
 D public/fontawesome/svgs/solid/user-large-slash.svg
 D public/fontawesome/svgs/solid/user-large.svg
 D public/fontawesome/svgs/solid/user-lock.svg
 D public/fontawesome/svgs/solid/user-minus.svg
 D public/fontawesome/svgs/solid/user-ninja.svg
 D public/fontawesome/svgs/solid/user-nurse.svg
 D public/fontawesome/svgs/solid/user-pen.svg
 D public/fontawesome/svgs/solid/user-plus.svg
 D public/fontawesome/svgs/solid/user-secret.svg
 D public/fontawesome/svgs/solid/user-shield.svg
 D public/fontawesome/svgs/solid/user-slash.svg
 D public/fontawesome/svgs/solid/user-tag.svg
 D public/fontawesome/svgs/solid/user-tie.svg
 D public/fontawesome/svgs/solid/user-xmark.svg
 D public/fontawesome/svgs/solid/user.svg
 D public/fontawesome/svgs/solid/users-between-lines.svg
 D public/fontawesome/svgs/solid/users-gear.svg
 D public/fontawesome/svgs/solid/users-line.svg
 D public/fontawesome/svgs/solid/users-rays.svg
 D public/fontawesome/svgs/solid/users-rectangle.svg
 D public/fontawesome/svgs/solid/users-slash.svg
 D public/fontawesome/svgs/solid/users-viewfinder.svg
 D public/fontawesome/svgs/solid/users.svg
 D public/fontawesome/svgs/solid/utensils.svg
 D public/fontawesome/svgs/solid/v.svg
 D public/fontawesome/svgs/solid/van-shuttle.svg
 D public/fontawesome/svgs/solid/vault.svg
 D public/fontawesome/svgs/solid/vector-square.svg
 D public/fontawesome/svgs/solid/venus-double.svg
 D public/fontawesome/svgs/solid/venus-mars.svg
 D public/fontawesome/svgs/solid/venus.svg
 D public/fontawesome/svgs/solid/vest-patches.svg
 D public/fontawesome/svgs/solid/vest.svg
 D public/fontawesome/svgs/solid/vial-circle-check.svg
 D public/fontawesome/svgs/solid/vial-virus.svg
 D public/fontawesome/svgs/solid/vial.svg
 D public/fontawesome/svgs/solid/vials.svg
 D public/fontawesome/svgs/solid/video-slash.svg
 D public/fontawesome/svgs/solid/video.svg
 D public/fontawesome/svgs/solid/vihara.svg
 D public/fontawesome/svgs/solid/virus-covid-slash.svg
 D public/fontawesome/svgs/solid/virus-covid.svg
 D public/fontawesome/svgs/solid/virus-slash.svg
 D public/fontawesome/svgs/solid/virus.svg
 D public/fontawesome/svgs/solid/viruses.svg
 D public/fontawesome/svgs/solid/voicemail.svg
 D public/fontawesome/svgs/solid/volcano.svg
 D public/fontawesome/svgs/solid/volleyball.svg
 D public/fontawesome/svgs/solid/volume-high.svg
 D public/fontawesome/svgs/solid/volume-low.svg
 D public/fontawesome/svgs/solid/volume-off.svg
 D public/fontawesome/svgs/solid/volume-xmark.svg
 D public/fontawesome/svgs/solid/vr-cardboard.svg
 D public/fontawesome/svgs/solid/w.svg
 D public/fontawesome/svgs/solid/walkie-talkie.svg
 D public/fontawesome/svgs/solid/wallet.svg
 D public/fontawesome/svgs/solid/wand-magic-sparkles.svg
 D public/fontawesome/svgs/solid/wand-magic.svg
 D public/fontawesome/svgs/solid/wand-sparkles.svg
 D public/fontawesome/svgs/solid/warehouse.svg
 D public/fontawesome/svgs/solid/water-ladder.svg
 D public/fontawesome/svgs/solid/water.svg
 D public/fontawesome/svgs/solid/wave-square.svg
 D public/fontawesome/svgs/solid/weight-hanging.svg
 D public/fontawesome/svgs/solid/weight-scale.svg
 D public/fontawesome/svgs/solid/wheat-awn-circle-exclamation.svg
 D public/fontawesome/svgs/solid/wheat-awn.svg
 D public/fontawesome/svgs/solid/wheelchair-move.svg
 D public/fontawesome/svgs/solid/wheelchair.svg
 D public/fontawesome/svgs/solid/whiskey-glass.svg
 D public/fontawesome/svgs/solid/wifi.svg
 D public/fontawesome/svgs/solid/wind.svg
 D public/fontawesome/svgs/solid/window-maximize.svg
 D public/fontawesome/svgs/solid/window-minimize.svg
 D public/fontawesome/svgs/solid/window-restore.svg
 D public/fontawesome/svgs/solid/wine-bottle.svg
 D public/fontawesome/svgs/solid/wine-glass-empty.svg
 D public/fontawesome/svgs/solid/wine-glass.svg
 D public/fontawesome/svgs/solid/won-sign.svg
 D public/fontawesome/svgs/solid/worm.svg
 D public/fontawesome/svgs/solid/wrench.svg
 D public/fontawesome/svgs/solid/x-ray.svg
 D public/fontawesome/svgs/solid/x.svg
 D public/fontawesome/svgs/solid/xmark.svg
 D public/fontawesome/svgs/solid/xmarks-lines.svg
 D public/fontawesome/svgs/solid/y.svg
 D public/fontawesome/svgs/solid/yen-sign.svg
 D public/fontawesome/svgs/solid/yin-yang.svg
 D public/fontawesome/svgs/solid/z.svg
 D public/fontawesome/webfonts/fa-brands-400.ttf
 D public/fontawesome/webfonts/fa-brands-400.woff2
 D public/fontawesome/webfonts/fa-regular-400.ttf
 D public/fontawesome/webfonts/fa-regular-400.woff2
 D public/fontawesome/webfonts/fa-solid-900.ttf
 D public/fontawesome/webfonts/fa-solid-900.woff2
 D public/fontawesome/webfonts/fa-v4compatibility.ttf
 D public/fontawesome/webfonts/fa-v4compatibility.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-100.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-100italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-200.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-200italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-300.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-300italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-500.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-500italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-600.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-600italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-700.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-700italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-800.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-800italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-900.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-900italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-italic.woff2
 D public/fonts/poppins/poppins-v20-devanagari_latin_latin-ext-regular.woff2
 D public/images/dl/phase-01-foundations/autograd-from-scratch/xor-training-dark.svg
 D public/images/dl/phase-01-foundations/autograd-from-scratch/xor-training-light.svg
 D public/images/dl/phase-01-foundations/introduction-to-neural-networks-the-perceptron/xor-ceiling-dark.svg
 D public/images/dl/phase-01-foundations/introduction-to-neural-networks-the-perceptron/xor-ceiling-light.svg
 D public/images/dl/phase-03-vision/image-segmentation/segmentation-samples-dark.svg
 D public/images/dl/phase-03-vision/image-segmentation/segmentation-samples-light.svg
 D public/images/dl/phase-06-generative/diffusion/schedule-comparison-dark.svg
 D public/images/dl/phase-06-generative/diffusion/schedule-comparison-light.svg
 D public/images/dl/phase-06-generative/diffusion/what-fixed-it-dark.svg
 D public/images/dl/phase-06-generative/diffusion/what-fixed-it-light.svg
 D public/images/dl/phase-06-generative/gans/samples-dark.svg
 D public/images/dl/phase-06-generative/gans/samples-light.svg
 D public/images/dl/phase-06-generative/variational-autoencoders/latent-structure-dark.svg
 D public/images/dl/phase-06-generative/variational-autoencoders/latent-structure-light.svg
 D public/images/dl/phase-09-capstones/generative-project/latent-dark.svg
 D public/images/dl/phase-09-capstones/generative-project/latent-light.svg
 D public/images/ml/phase-02-preprocessing/eda-correlations/geographic-scatter-dark.svg
 D public/images/ml/phase-02-preprocessing/eda-correlations/geographic-scatter-light.svg
 D public/images/ml/phase-02-preprocessing/eda-correlations/income-vs-value-dark.svg
 D public/images/ml/phase-02-preprocessing/eda-correlations/income-vs-value-light.svg
 D public/images/ml/phase-02-preprocessing/end-to-end/residual-analysis-dark.svg
 D public/images/ml/phase-02-preprocessing/end-to-end/residual-analysis-light.svg
 D public/images/ml/phase-05-ensembles/bagging/variance-reduction-dark.svg
 D public/images/ml/phase-05-ensembles/bagging/variance-reduction-light.svg
 D public/images/ml/phase-06-unsupervised/hierarchical-clustering-dendrograms/linkage-on-moons-dark.svg
 D public/images/ml/phase-06-unsupervised/hierarchical-clustering-dendrograms/linkage-on-moons-light.svg
 D public/images/ml/phase-06-unsupervised/introduction-to-clustering/cluster-shapes-dark.svg
 D public/images/ml/phase-06-unsupervised/introduction-to-clustering/cluster-shapes-light.svg
 D public/images/ml/phase-06-unsupervised/k-means-clustering-algorithm/where-kmeans-fails-dark.svg
 D public/images/ml/phase-06-unsupervised/k-means-clustering-algorithm/where-kmeans-fails-light.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/pca-vs-tsne-digits-dark.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/pca-vs-tsne-digits-light.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/perplexity-sweep-dark.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/perplexity-sweep-light.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/swiss-roll-unrolled-dark.svg
 D public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/swiss-roll-unrolled-light.svg
 D public/images/ml/phase-09-interpretability/partial-dependence-and-ice-plots/centred-ice-dark.svg
 D public/images/ml/phase-09-interpretability/partial-dependence-and-ice-plots/centred-ice-light.svg
 D public/images/ml/phase-10-applied/anomaly-and-outlier-detection/two-kinds-dark.svg
 D public/images/ml/phase-10-applied/anomaly-and-outlier-detection/two-kinds-light.svg
 D public/images/mml/cholesky-decomposition/cholesky-sampling-dark.svg
 D public/images/mml/cholesky-decomposition/cholesky-sampling-light.svg
 D public/images/mml/complex-numbers-in-one-page/conjugate-pairs-and-the-axis-dark.svg
 D public/images/mml/complex-numbers-in-one-page/conjugate-pairs-and-the-axis-light.svg
 D public/images/mml/determinant-and-trace/trace-invariant-under-basis-change-dark.svg
 D public/images/mml/determinant-and-trace/trace-invariant-under-basis-change-light.svg
 D public/images/mml/directed-graphical-models/the-collider-effect-dark.svg
 D public/images/mml/directed-graphical-models/the-collider-effect-light.svg
 D public/images/mml/eigendecomposition-and-diagonalization/pdp-three-steps-dark.svg
 D public/images/mml/eigendecomposition-and-diagonalization/pdp-three-steps-light.svg
 D public/images/mml/eigenvalues-and-eigenvectors/five-mappings-dark.svg
 D public/images/mml/eigenvalues-and-eigenvectors/five-mappings-light.svg
 D public/images/mml/inner-products/spd-or-not-dark.svg
 D public/images/mml/inner-products/spd-or-not-light.svg
 D public/images/mml/lengths-and-distances/cauchy-schwarz-dark.svg
 D public/images/mml/lengths-and-distances/cauchy-schwarz-light.svg
 D public/images/mml/linear-and-quadratic-programming/an-lp-optimum-is-a-vertex-dark.svg
 D public/images/mml/linear-and-quadratic-programming/an-lp-optimum-is-a-vertex-light.svg
 D public/images/mml/maximum-likelihood-estimation-for-linear-regression/one-quadratic-one-solution-dark.svg
 D public/images/mml/maximum-likelihood-estimation-for-linear-regression/one-quadratic-one-solution-light.svg
 D public/images/mml/orthogonal-complement/pythagoras-in-five-dimensions-dark.svg
 D public/images/mml/orthogonal-complement/pythagoras-in-five-dimensions-light.svg
 D public/images/mml/separating-hyperplanes/many-separators-one-margin-dark.svg
 D public/images/mml/separating-hyperplanes/many-separators-one-margin-light.svg
 D public/images/mml/singular-value-decomposition/svd-three-stages-dark.svg
 D public/images/mml/singular-value-decomposition/svd-three-stages-light.svg
 D public/images/mml/summary-statistics-and-independence/mean-median-mode-dark.svg
 D public/images/mml/summary-statistics-and-independence/mean-median-mode-light.svg
 D public/images/mml/summary-statistics-and-independence/same-variance-different-covariance-dark.svg
 D public/images/mml/summary-statistics-and-independence/same-variance-different-covariance-light.svg
 D public/images/mml/summary-statistics-and-independence/uncorrelated-is-not-independent-dark.svg
 D public/images/mml/summary-statistics-and-independence/uncorrelated-is-not-independent-light.svg
 M public/images/projects/real_time_image_generation.png
 M public/manifest.json
 M public/scripts/editor-fullscreen.js
 M public/scripts/mermaid.js
 M public/scripts/p5-viz.js
 D public/scripts/python-playground-cm.js
 M public/scripts/python-playground.js
 M public/scripts/viz-fullscreen.js
 M public/sw.js
 M scripts/check-i18n.mjs
 M scripts/gen-progress-manifest.mjs
AM scripts/verify-routes.mjs
AM source.config.ts
 M src/assets/cheatsheet1.jpg
 M src/assets/cheatsheet2.jpg
 M src/assets/pluralsightpython.png
 M src/assets/udacitypython.png
 M src/components/YoutuberCard.astro
 M src/components/dsa/DrillDeck.tsx
 M src/components/dsa/MockInterview.tsx
 M src/components/dsa/ProblemTable.tsx
 M src/components/react/AnimatedShinyText.tsx
 M src/components/react/BorderBeam.tsx
 M src/components/react/Marquee.tsx
 M src/components/react/Meteors.tsx
 M src/components/react/NumberTicker.tsx
 M src/components/react/Spotlight.tsx
 M src/components/viz/ArrayStepper.tsx
 M src/components/viz/ComplexityChart.tsx
 M src/components/viz/DPTable.tsx
 M src/components/viz/DSUView.tsx
 M src/components/viz/GraphTraversal.tsx
 M src/components/viz/GridPathfinder.tsx
 M src/components/viz/HeapView.tsx
 M src/components/viz/IntervalTimeline.tsx
 M src/components/viz/LinkedListRewire.tsx
 M src/components/viz/RecursionTree.tsx
 M src/components/viz/SegmentTreeView.tsx
 M src/components/viz/StackMachine.tsx
 M src/components/viz/StateMachineView.tsx
 M src/components/viz/TreeWalker.tsx
 M src/components/viz/TrieView.tsx
 M src/components/viz/VizPlayer.tsx
 M src/components/viz/math/AutodiffGraph.tsx
 M src/components/viz/math/DescentLab.tsx
 M src/components/viz/math/DistributionLab.tsx
 M src/components/viz/math/EigenLab.tsx
 M src/components/viz/math/ElimStepper.tsx
 M src/components/viz/math/HessianLab.tsx
 M src/components/viz/math/MatrixLab.tsx
 M src/components/viz/math/NormBall.tsx
 M src/components/viz/math/ProjectionLab.tsx
 M src/components/viz/math/SVDLab.tsx
 M src/components/viz/math/SpanExplorer.tsx
 M src/components/viz/math/SurfaceGrad.tsx
 M src/components/viz/math/TaylorLab.tsx
 M src/components/viz/math/stage.tsx
 M src/content/docs/404.mdx
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/How to Use This Course.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Sheet - Blind 75.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Sheet - LeetCode Top Interview 150.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Sheet - NeetCode 150.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Sheet - Strivers A2Z DSA Sheet.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Sheet - Strivers SDE Sheet.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/The Sheets, Mapped.mdx"
 M "src/content/docs/DSA with Python/Phase-00-Start-Here/Your DSA Interview Roadmap.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Big-O and Complexity Deep Dive.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Introduction to DSA with Python.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Python Recursion and Iterative Conversion.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Recurrences and the Master Theorem.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Setup for CP and Interviews.mdx"
 M "src/content/docs/DSA with Python/Phase-01-Foundations/Space Complexity and the Call Stack.mdx"
 M "src/content/docs/DSA with Python/Phase-02-Python-for-DSA-and-CP/Fast IO and Beating TLE.mdx"
 M "src/content/docs/DSA with Python/Phase-02-Python-for-DSA-and-CP/Python Data Model Speed Reality.mdx"
 M "src/content/docs/DSA with Python/Phase-02-Python-for-DSA-and-CP/Python Idioms and Tricks for CP.mdx"
 M "src/content/docs/DSA with Python/Phase-02-Python-for-DSA-and-CP/stdlib Power Tools for DSA.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Arrays and Dynamic Arrays.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Balanced Trees Overview.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Binary Trees and BST.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Graph Representations.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Hash Tables.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Heaps and Priority Queues.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Linked Lists.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Ordered Structures in Python.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Stacks and Queues.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Strings.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Tries.mdx"
 M "src/content/docs/DSA with Python/Phase-03-Core-Data-Structures/Union-Find (Disjoint Set Union).mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Binary Search Template and Variants.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Counting Radix and Bucket Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Elementary Sorts.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Heap Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Merge Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Python Sorting and Timsort.mdx"
 M "src/content/docs/DSA with Python/Phase-04-Sorting-and-Searching/Quick Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Cyclic Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Dutch National Flag and In-place Partitioning.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Frequency and Anagram Counting.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Kadane and Maximum Subarray.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Matrix and Grid Manipulation.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Monotonic Deque.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Monotonic Stack.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Palindrome Patterns.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Prefix Sum with HashMap.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Prefix Sums and Difference Arrays.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Sliding Window.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Stack Parsing and Expression Evaluation.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Trie Patterns.mdx"
 M "src/content/docs/DSA with Python/Phase-05-Patterns-Arrays-and-Strings/Two Pointers.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/Binary Search on Answer.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/Binary Search on Rotated Arrays and Matrices.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/K-way Merge.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/Quickselect and Nth Element.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/Top K Elements.mdx"
 M "src/content/docs/DSA with Python/Phase-06-Patterns-Search-and-Selection/Two Heaps and Running Median.mdx"
 M "src/content/docs/DSA with Python/Phase-07-Patterns-Intervals-and-Greedy/Greedy Interval Scheduling.mdx"
 M "src/content/docs/DSA with Python/Phase-07-Patterns-Intervals-and-Greedy/Greedy Reachability and Jumps.mdx"
 M "src/content/docs/DSA with Python/Phase-07-Patterns-Intervals-and-Greedy/Merge Intervals.mdx"
 M "src/content/docs/DSA with Python/Phase-07-Patterns-Intervals-and-Greedy/Sorting with Custom Comparators.mdx"
 M "src/content/docs/DSA with Python/Phase-07-Patterns-Intervals-and-Greedy/Sweep Line and Event Counting.mdx"
 M "src/content/docs/DSA with Python/Phase-08-Patterns-Linked-Lists/Copy Flatten and Reorder.mdx"
 M "src/content/docs/DSA with Python/Phase-08-Patterns-Linked-Lists/Dummy Head Rewiring and Merging.mdx"
 M "src/content/docs/DSA with Python/Phase-08-Patterns-Linked-Lists/Fast and Slow Pointers.mdx"
 M "src/content/docs/DSA with Python/Phase-08-Patterns-Linked-Lists/In-place Linked List Reversal.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/BST Patterns.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Binary Lifting and Sparse LCA.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Lowest Common Ancestor.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Morris Traversal and O(1)-Space Tree Walks.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Serialize Compare and Subtree.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Tree BFS and Level Order.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Tree Construction from Traversals.mdx"
 M "src/content/docs/DSA with Python/Phase-09-Patterns-Trees/Tree DFS Paths and Sums.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/0-1 BFS and Deque Shortest Paths.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/BFS and Dijkstra with Extra State.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Breadth First Search.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Cycle Detection and Bipartite Checking.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Depth First Search.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Eulerian Paths and Reconstruct Itinerary.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Graph Traversal and Connected Components.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Grid Traversal Islands and Flood Fill.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Multi-source BFS.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Shortest Paths Dijkstra Bellman-Ford and Floyd-Warshall.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Topological Sort.mdx"
 M "src/content/docs/DSA with Python/Phase-10-Patterns-Graphs/Union-Find Problem Patterns.mdx"
 M "src/content/docs/DSA with Python/Phase-11-Recursion-and-Backtracking/Backtracking.mdx"
 M "src/content/docs/DSA with Python/Phase-11-Recursion-and-Backtracking/Divide and Conquer.mdx"
 M "src/content/docs/DSA with Python/Phase-11-Recursion-and-Backtracking/Permutations and Arrangements.mdx"
 M "src/content/docs/DSA with Python/Phase-11-Recursion-and-Backtracking/Subsets and Combinations.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Bitmask and Tree DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Classic DP LIS LCS and Edit Distance.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/DP on Grids and Intervals.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/DP on Stocks.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Digit DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/From Recursion to DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Knapsack Variants and Subset Sum.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/LIS Variants and Patience Sorting.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/One Dimensional DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Partition DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/String DP.mdx"
 M "src/content/docs/DSA with Python/Phase-12-Dynamic-Programming/Two Dimensional DP and Knapsack.mdx"
 M "src/content/docs/DSA with Python/Phase-13-Bit-Manipulation-and-Math/Bit Manipulation Tricks.mdx"
 M "src/content/docs/DSA with Python/Phase-13-Bit-Manipulation-and-Math/Bitwise XOR Patterns.mdx"
 M "src/content/docs/DSA with Python/Phase-13-Bit-Manipulation-and-Math/Math and Geometry Problems.mdx"
 M "src/content/docs/DSA with Python/Phase-13-Bit-Manipulation-and-Math/Number Theory for Competitive Programming.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design HashMap and Skiplist.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design Iterators and Flatteners.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design LRU and LFU Caches.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design Rate Limiter and Hit Counter.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design Trackers and Feeds.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design with Randomization.mdx"
 M "src/content/docs/DSA with Python/Phase-14-Design-Problems/Design with Stacks and Queues.mdx"
 M "src/content/docs/DSA with Python/Phase-15-Simulation-and-Implementation/Simulation and Stateful Iteration.mdx"
 M "src/content/docs/DSA with Python/Phase-16-Advanced-Graph-Algorithms/Maximum Flow.mdx"
 M "src/content/docs/DSA with Python/Phase-16-Advanced-Graph-Algorithms/Minimum Spanning Trees Kruskal and Prim.mdx"
 M "src/content/docs/DSA with Python/Phase-16-Advanced-Graph-Algorithms/Strongly Connected Components and Bridges.mdx"
 M "src/content/docs/DSA with Python/Phase-17-Advanced-CP-Topics/Advanced DP Optimizations.mdx"
 M "src/content/docs/DSA with Python/Phase-17-Advanced-CP-Topics/Fenwick Tree (Binary Indexed Tree).mdx"
 M "src/content/docs/DSA with Python/Phase-17-Advanced-CP-Topics/Segment Trees and Lazy Propagation.mdx"
 M "src/content/docs/DSA with Python/Phase-17-Advanced-CP-Topics/Sparse Tables and RMQ.mdx"
 M "src/content/docs/DSA with Python/Phase-17-Advanced-CP-Topics/String Algorithms KMP Z and Rabin-Karp.mdx"
 M "src/content/docs/DSA with Python/Phase-18-Templates-and-Cheatsheets/Algorithm Templates.mdx"
 M "src/content/docs/DSA with Python/Phase-18-Templates-and-Cheatsheets/Data Structure Templates.mdx"
 M "src/content/docs/DSA with Python/Phase-18-Templates-and-Cheatsheets/Graph Algorithm Templates.mdx"
 M "src/content/docs/DSA with Python/Phase-18-Templates-and-Cheatsheets/Master Complexity Cheatsheet.mdx"
 M "src/content/docs/DSA with Python/Phase-19-Interview-and-Contest-Strategy/Contest Strategy.mdx"
 M "src/content/docs/DSA with Python/Phase-19-Interview-and-Contest-Strategy/FAANG Interview Playbook.mdx"
 M "src/content/docs/DSA with Python/Phase-19-Interview-and-Contest-Strategy/Mock Interviews and Spaced Repetition.mdx"
 M "src/content/docs/DSA with Python/Phase-19-Interview-and-Contest-Strategy/Pattern Recognition Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-19-Interview-and-Contest-Strategy/Study Plans and Roadmap.mdx"
 M "src/content/docs/DSA with Python/Phase-20-Problem-Sets/Arrays and Strings Problem Set.mdx"
 M "src/content/docs/DSA with Python/Phase-20-Problem-Sets/Dynamic Programming Problem Set.mdx"
 M "src/content/docs/DSA with Python/Phase-20-Problem-Sets/Getting Started Problem Set.mdx"
 M "src/content/docs/DSA with Python/Phase-20-Problem-Sets/Hard Mix Problem Set.mdx"
 M "src/content/docs/DSA with Python/Phase-20-Problem-Sets/Trees and Graphs Problem Set.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Amazon Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Apple Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Bloomberg Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/ByteDance Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Company Comparison Matrix.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Google Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Meta Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Microsoft Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Netflix Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-21-Company-Guides/Uber Interview Guide.mdx"
 M "src/content/docs/DSA with Python/Phase-22-Low-Level-Design/Design a Deck of Cards.mdx"
 M "src/content/docs/DSA with Python/Phase-22-Low-Level-Design/Design a Library System.mdx"
 M "src/content/docs/DSA with Python/Phase-22-Low-Level-Design/Design a Parking Lot.mdx"
 M "src/content/docs/DSA with Python/Phase-22-Low-Level-Design/Design an Elevator System.mdx"
 M "src/content/docs/DSA with Python/Phase-22-Low-Level-Design/The OOD Round.mdx"
 M "src/content/docs/DSA with Python/Phase-23-Concurrency/Bounded Buffers and Deadlock.mdx"
 M "src/content/docs/DSA with Python/Phase-23-Concurrency/Thread Ordering and Signalling.mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Anaconda Distribution Setup.mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Google Colab Walkthrough.mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Installing Data Science Libraries (pip & conda).mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Jupyter Notebook Interface.mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Jupyter Shortcuts & Magic Commands.mdx"
 M "src/content/docs/Data Analytics/Phase-01-Environment-and-Setup/Virtual Environments for Data Science.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Broadcasting in NumPy.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Conditional Logic, Sorting and Set Logic (where, sort, unique).mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Indexing and Slicing Arrays.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Introduction to NumPy.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Linear Algebra with NumPy.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/NumPy Arithmetic Operations.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/NumPy Array Creation.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/NumPy Data Types (dtypes).mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/NumPy Random Module.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/NumPy Universal Functions (ufuncs).mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Saving and Loading NumPy Data.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Shape Manipulation & Reshape.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Staking and Splitting Arrays.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Statistical Functions in NumPy.mdx"
 M "src/content/docs/Data Analytics/Phase-02-Numerical-Computing-NumPy/Structured Arrays and Random Walks.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Advanced GroupBy (transform, filter, named agg).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Applying Functions (apply, map, applymap).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Binary Formats and Web APIs (Parquet, pickle, requests).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Cleaning Data (astype, duplicates, string cleaning).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Correlation and Covariance.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Cross-Tabulation and Pivot Table Depth.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Data Inspection (head, tail, info, describe).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Date Ranges, Frequencies and Shifting.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Filtering with Conditions (and, or, isin, query).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Grouping and Aggregations (groupby, agg).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Handling Missing Data (isna, fillna, dropna).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Hierarchical Indexing (MultiIndex).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Indexing and Selecting Data (loc, iloc).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Introduction to Pandas.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Merging and Joining Data (merge, join, concat).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Periods and Period Arithmetic.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Reading and Writing Data (CSV, Excel, JSON).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Reindexing and Data Alignment.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Resampling and Frequency Conversion.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Reshaping Data (pivot, pivot_table, melt).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Rolling and Moving Window Functions.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Series and DataFrames.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Sorting and Ranking.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Text and String Methods (str accessor and regex).mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Time Zone Handling.mdx"
 M "src/content/docs/Data Analytics/Phase-03-Data-Manipulation-with-Pandas/Working with Dates and Times (to_datetime, dt accessor).mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Binning and Discretization.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Categorical Data Type (memory and performance).mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Data Type Conversion and Validation.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Feature Engineering Basics.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Feature Scaling (MinMax vs Standard).mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Handling Outliers.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Label Encoding.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/One-Hot Encoding.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Outlier Detection (IQR Method).mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Preprocessing Pipeline (scikit-learn).mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Train-Test Split Concepts.mdx"
 M "src/content/docs/Data Analytics/Phase-04-Data-Preprocessing-and-Cleaning/Understanding Data Quality.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Anatomy of a Plot.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Axis Labels and Titles.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Bar Chart and Horizontal Bar.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Histogram.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Introduction to Matplotlib.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Legends and Colors.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Line Plot.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Matplotlib Mini Project (EDA charts pack).mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Pie Chart.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Saving Plots as Images.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Scatter Plot.mdx"
 M "src/content/docs/Data Analytics/Phase-05-Data-Visualization-with-Matplotlib/Subplots and Figure Size.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Bar Plots in Seaborn.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Box Plots and Whiskers.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Count Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Distribution Plots (displot, histplot).mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Facet Grids.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Heatmaps for Correlation.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Introduction to Seaborn.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Joint Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Kernel Density Estimation (KDE).mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Pair Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/README (Seaborn Phase Overview).mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Regression Plots (lmplot, regplot).mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Seaborn vs Matplotlib.mdx"
 M "src/content/docs/Data Analytics/Phase-06-Statistical-Visualization-with-Seaborn/Violin Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/3D Scatter Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Animations in Plotly.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Bubble Charts.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Choropleth Maps.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Creating Dashboards with Plotly.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Interactive Bar Charts.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Interactive Histograms and Distributions.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Interactive Line Charts.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Interactive Scatter Plots.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Introduction to Plotly Express.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Plotly Subplots and Facets.mdx"
 M "src/content/docs/Data Analytics/Phase-07-Interactive-Visualization-with-Plotly/Sunburst Charts.mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/A-B Testing Basics.mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/ANOVA (one-way).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Chi-Square Test (categorical association).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Confidence Intervals (CI).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Correlation vs Causation (Pearson, Spearman).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Descriptive Statistics (mean, median, variance).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Distributions (normal, binomial, Poisson).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Hypothesis Testing (p-value, alpha, errors).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Introduction to Statistics for Data Analytics.mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Linear Regression with statsmodels (OLS and formulas).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Non-Parametric Tests (Mann-Whitney, Wilcoxon).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Probability Basics (events, conditional probability).md"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Sampling and the Central Limit Theorem (CLT).md"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/Statistics Mini Project (Analyze a Marketing Campaign).mdx"
 M "src/content/docs/Data Analytics/Phase-08-Statistics-for-Data-Analytics/t-test (independent and paired).mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/Aggregations (COUNT, SUM, AVG) and GROUP BY.mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/CTEs (WITH) and Subqueries.mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/Date and Time Analytics in SQL.mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/Introduction to SQL for Data Analytics.mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/Joins (INNER, LEFT) for Analytics.mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/SQL Basics (SELECT, WHERE, ORDER BY, LIMIT).mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/SQL Mini Project (Build a KPI Dashboard Query Set).mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/SQL from Python (pandas + sqlite3).mdx"
 M "src/content/docs/Data Analytics/Phase-09-SQL-for-Data-Analytics/Window Functions (OVER, PARTITION BY).mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Covid-19 Data Analysis & Visualization.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Credit Card Fraud Detection.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Customer Churn Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/E-commerce Sales Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Exploratory Data Analysis (EDA) on Titanic.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Global Terrorism Database Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/HR Analytics Dashboard.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Housing Price Prediction (Regression).mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Iris Flower Classification.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Netflix Movies & TV Shows Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Olympics Data Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Spotify Song Popularity Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Stock Market Analysis (Finance).mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Twitter Sentiment Analysis.mdx"
 M "src/content/docs/Data Analytics/Phase-10-Data-Analytics-Projects/Uber Ride Data Analysis.mdx"
 M "src/content/docs/Deep Learning/Deep Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Activation Functions (ReLU, Sigmoid, Softmax).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Autograd from Scratch.mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Building Neural Networks with Keras (Sequential and Functional API).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/First Example Classifying Movie Reviews (IMDB, Binary).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/First Example Classifying Newswires (Reuters, Multiclass).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/First Example Predicting House Prices (Regression).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/How Neural Networks Learn (Gradient-Based Optimization).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Introduction to Neural Networks (The Perceptron).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Multi-Layer Perceptron (MLP).mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Phase 1 - Neural Network Foundations.mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/Tensors and Tensor Operations.mdx"
 M "src/content/docs/Deep Learning/Phase 01 - Neural Network Foundations/The Same Network in PyTorch.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Backpropagation and Optimizers (Adam, SGD).mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Batch Normalization.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Callbacks and TensorBoard.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Evaluating Models - Generalization and Validation.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Learning Rate Scheduling.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Loss Functions - Choosing What to Minimise.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Phase 2 - Training Deep Neural Networks.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Regularization & Dropout.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/The Universal Workflow of Machine Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 02 - Training Deep Neural Networks/Vanishing & Exploding Gradients.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Data Augmentation for Small Datasets.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Famous CNN Architectures (LeNet to ResNet).mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Fine-Tuning and Parameter-Efficient Tuning (LoRA).mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Image Segmentation.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Interpreting What Convnets Learn (Grad-CAM).mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Intro to Convolutional Neural Networks (CNN) for Images.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Normalisation Beyond Batch - Layer, Group and Instance.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Object Detection (Bounding Boxes and YOLO).mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Phase 3 - Computer Vision with CNNs.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Pooling & CNN Architecture.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Transfer Learning Using Pre-trained Models.mdx"
 M "src/content/docs/Deep Learning/Phase 03 - Computer Vision with CNNs/Vision Transformers (ViT).mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Advanced Recurrent Layers (Dropout, Stacking, Bidirectional).mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Attention Before Transformers (Additive and Bahdanau).mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Intro to Recurrent Neural Networks (RNN) for Sequences.mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/LSTM & GRU Networks.mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Padding, Masking and Variable-Length Sequences.mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Phase 4 - Sequence Models with RNNs.mdx"
 M "src/content/docs/Deep Learning/Phase 04 - Sequence Models with RNNs/Time Series Forecasting with RNNs.mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Attention from Scratch (Queries, Keys and Values).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Bag of Words (BoW) & TF-IDF.mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Evaluating Language Models (Perplexity and BLEU).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Named Entity Recognition (NER).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Phase 5 - NLP & Transformers.mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Sentiment Analysis Tutorial.mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Sequence-to-Sequence Learning (Machine Translation).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Subword Tokenization (BPE and WordPiece).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Text Preprocessing (Tokenization, Stemming, Lemmatization).mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/The Transformer Architecture.mdx"
 M "src/content/docs/Deep Learning/Phase 05 - NLP & Transformers/Word Embeddings (Word2Vec, GloVe).mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Autoencoders.mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/DeepDream.mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Diffusion Models (Introduction).mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Evaluating Generative Models (FID, Coverage and Memorisation).mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Generative Adversarial Networks (GANs).mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Neural Style Transfer.mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Phase 6 - Generative Deep Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Text Generation with Language Models.mdx"
 M "src/content/docs/Deep Learning/Phase 06 - Generative Deep Learning/Variational Autoencoders (VAE).mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Actor-Critic and PPO (Intro).mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Exploration vs Exploitation (Bandits and Epsilon Schedules).mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Introduction to Reinforcement Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Phase 7 - Reinforcement Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Policy Gradients (Intro).mdx"
 M "src/content/docs/Deep Learning/Phase 07 - Reinforcement Learning/Q-Learning & Deep Q-Networks.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Custom Models and Training Loops (TensorFlow).mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Deploying to Mobile & Edge with TensorFlow Lite.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Distributed Training with tf.distribute.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Hyperparameter Tuning with KerasTuner.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Limitations and the Future of Deep Learning.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Loading & Preprocessing Data with tf.data.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Mixed Precision and Multi-GPU Training.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Model Compression (Pruning, Quantisation and Distillation).mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Phase 8 - Scaling & Deploying Deep Models.mdx"
 M "src/content/docs/Deep Learning/Phase 08 - Scaling & Deploying Deep Models/Serving Models with TensorFlow Serving.mdx"
 M "src/content/docs/Deep Learning/Phase 09 - Capstone Projects/Capstone 1 - An Image Classifier End to End.mdx"
 M "src/content/docs/Deep Learning/Phase 09 - Capstone Projects/Capstone 2 - A Text Classifier End to End.mdx"
 M "src/content/docs/Deep Learning/Phase 09 - Capstone Projects/Capstone 3 - A Generative Model You Can Defend.mdx"
 M "src/content/docs/Deep Learning/Phase 09 - Capstone Projects/Phase 9 - Capstone Projects.mdx"
 M "src/content/docs/Flask Tutorials/Flask Tutorials.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Debug Mode in Flask.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/First Flask Application (Hello World).mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Flask Command Line Interface (CLI).mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Flask Directory Structure.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Flask vs Django.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Installing Flask.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Introduction to Web Frameworks.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Phase 1 - Flask Fundamentals.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Running the Dev Server.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/Setting up Virtual Environment.mdx"
 M "src/content/docs/Flask Tutorials/Phase 1 - Flask Fundamentals/WSGI Concepts.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Basic Routing.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Custom Error Pages (404, 500).mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/HTTP Methods (GET vs POST).mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Handling Query Parameters.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Phase 2 - Routing and Views.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Redirects and Errors.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Returning JSON Data.mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/URL Building (url_for).mdx"
 M "src/content/docs/Flask Tutorials/Phase 2 - Routing and Views/Variable Rules (Dynamic URLs).mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Control Structures (If-Else, Loops).mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Custom Filters.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Including Partials.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Introduction to Jinja2.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Jinja2 Delimiters.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Jinja2 Filters.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Linking Static Files (CSS-JS).mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Passing Variables to Templates.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Phase 3 - Templating (Jinja2).mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Rendering Templates.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Template Blocks.mdx"
 M "src/content/docs/Flask Tutorials/Phase 3 - Templating (Jinja2)/Template Inheritance (Extends).mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/CSRF Protection.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Creating Form Classes.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/File Uploading.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Flash Messages.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Form Field Types.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Form Validation.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Handling Form Data.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Introduction to Flask-WTF.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Phase 4 - Forms and User Input.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Rendering Forms in Templates.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/Secure Filenames.mdx"
 M "src/content/docs/Flask Tutorials/Phase 4 - Forms and User Input/The Request Object.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/CRUD - Create Record.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/CRUD - Delete Record.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/CRUD - Read Record.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/CRUD - Update Record.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Configuring Database URI.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Creating Database Models.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Creating the Database (db.create_all).mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Database Migrations (Flask-Migrate).mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Executing Raw SQL.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Introduction to ORMs.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Many-to-Many Relationships.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/One-to-Many Relationships.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Phase 5 - Databases (Flask-SQLAlchemy).mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Primary Keys and Column Types.mdx"
 M "src/content/docs/Flask Tutorials/Phase 5 - Databases (Flask-SQLAlchemy)/Setting up Flask-SQLAlchemy.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Cookies vs Sessions.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Introduction to Flask-Login.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Login View.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Logout View.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Password Hashing (Werkzeug).mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Phase 6 - User Authentication.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Protecting Routes (@login_required).mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Remember Me Functionality.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/User Loader Function.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/User Registration Flow.mdx"
 M "src/content/docs/Flask Tutorials/Phase 6 - User Authentication/Using Flask Sessions.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Application Factory Pattern.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Context Processors.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Flask Extensions Overview.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Flask-Admin Interface.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Flask-Mail (Sending Emails).mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Handling Configuration (config.py).mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Introduction to Blueprints.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Phase 7 - Advanced Flask Architecture.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Registering Blueprints.mdx"
 M "src/content/docs/Flask Tutorials/Phase 7 - Advanced Flask Architecture/Request Hooks (before_request).mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/API Rate Limiting.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Building a Simple API.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Flask-RESTful vs Plain Flask.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Introduction to REST.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/JSON Serialization.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Phase 8 - REST APIs with Flask.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Testing APIs with Postman.mdx"
 M "src/content/docs/Flask Tutorials/Phase 8 - REST APIs with Flask/Token-Based Authentication (JWT).mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Deploying to AWS EC2.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Deploying to PythonAnywhere.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Deploying to Render.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Dockerizing Flask App.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Environment Variables (.env).mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Gunicorn Web Server.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Phase 9 - Deployment.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Preparing for Production.mdx"
 M "src/content/docs/Flask Tutorials/Phase 9 - Deployment/Using Nginx as Reverse Proxy.mdx"
 M "src/content/docs/Machine Learning/Machine Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/Artificial Intelligence vs Machine Learning vs Deep Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/ML vs Traditional Programming.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/Phase 1 - The ML Foundation.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/Setting up the ML Environment (Scikit-Learn, TensorFlow, PyTorch).mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/The ML Lifecycle From Data to Deployment.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/The Machine Learning Roadmap.mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/Types of Machine Learning (Supervised, Unsupervised, Reinforcement).mdx"
 M "src/content/docs/Machine Learning/Phase 01 - The ML Foundation/What is Machine Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Creating a Test Set (Avoiding Data Snooping).mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Data Cleaning & Handling Missing Values.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/End-to-End Machine Learning Project (California Housing).mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Exploratory Data Analysis & Correlations.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Feature Scaling (Normalization & Standardization).mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Framing an ML Problem & Getting the Data.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Handling Text & Categorical Attributes.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Phase 2 - Data Preprocessing & Feature Engineering.mdx"
 M "src/content/docs/Machine Learning/Phase 02 - Data Preprocessing & Feature Engineering/Transformation Pipelines & Custom Transformers.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Cost Functions Mean Squared Error (MSE).mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Gradient Descent Explained.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Introduction to Regression Analysis.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Metrics R-Squared and Adjusted R-Squared.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Multiple Linear Regression.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Phase 3 - Supervised Learning - Regression.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Polynomial Regression.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Regularization Ridge and Lasso Regression.mdx"
 M "src/content/docs/Machine Learning/Phase 03 - Supervised Learning - Regression/Simple Linear Regression.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Decision Trees Entropy and Gini Impurity.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Evaluation Metrics Confusion Matrix.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Introduction to Classification.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/K-Nearest Neighbors (KNN).mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Logistic Regression (Binary vs Multiclass).mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Na\303\257ve Bayes Classifier.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Phase 4 - Supervised Learning - Classification.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Precision, Recall, and F1-Score.mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/Support Vector Machines (SVM).mdx"
 M "src/content/docs/Machine Learning/Phase 04 - Supervised Learning - Classification/The ROC Curve and AUC.mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/Bagging Random Forest Regressor Classifier.mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/Boosting Introduction to AdaBoost.mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/Gradient Boosting (XGBoost, LightGBM, CatBoost).mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/Phase 5 - Ensemble Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/Stacking and Voting Classifiers.mdx"
 M "src/content/docs/Machine Learning/Phase 05 - Ensemble Learning/The Power of Ensembles Why Combine Models.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Anomaly Detection with Isolation Forests.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Association Rule Learning (Apriori Algorithm).mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/DBSCAN Density-Based Clustering.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Hierarchical Clustering (Dendrograms).mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Introduction to Clustering.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/K-Means Clustering Algorithm.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Phase 6 - Unsupervised Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/Principal Component Analysis (PCA).mdx"
 M "src/content/docs/Machine Learning/Phase 06 - Unsupervised Learning & Dimensionality Reduction/t-SNE and Manifold Learning.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/Bias vs Variance Tradeoff.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/Hyperparameter Tuning with GridSearchCV.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/K-Fold Cross-Validation.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/Phase 7 - Model Optimization & Tuning.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/RandomizedSearchCV for Large Parameter Spaces.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/The ML Pipeline Automating the Workflow.mdx"
 M "src/content/docs/Machine Learning/Phase 07 - Model Optimization & Tuning/Underfitting vs Overfitting.mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Building an ML API with Flask FastAPI.mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Deploying ML Models to Streamlit.mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Dockerizing an ML Application.mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Monitoring Model Drift.mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Phase 8 - Model Deployment (MLOps).mdx"
 M "src/content/docs/Machine Learning/Phase 08 - Model Deployment (MLOps)/Saving and Loading Models (Pickle, Joblib).mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/Fairness Metrics and Bias Auditing.mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/Feature Importance and Its Traps.mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/Partial Dependence and ICE Plots.mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/Phase 9 - Interpretability & Responsible ML.mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/SHAP Values from Scratch.mdx"
 M "src/content/docs/Machine Learning/Phase 09 - Interpretability & Responsible ML/Why Interpretability Matters.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Anomaly and Outlier Detection.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Cost-Sensitive Learning and Decision Thresholds.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Imbalanced Classification and Fraud Detection.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Phase 10 - Applied ML Problems.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Recommender Systems from Scratch.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Text Classification with TF-IDF.mdx"
 M "src/content/docs/Machine Learning/Phase 10 - Applied ML Problems/Time Series Forecasting Fundamentals.mdx"
 M "src/content/docs/Machine Learning/Phase 11 - ML Engineering/Data Validation and Schema Contracts.mdx"
 M "src/content/docs/Machine Learning/Phase 11 - ML Engineering/Experiment Tracking and Reproducibility.mdx"
 M "src/content/docs/Machine Learning/Phase 11 - ML Engineering/Feature Stores and Training-Serving Skew.mdx"
 M "src/content/docs/Machine Learning/Phase 11 - ML Engineering/Phase 11 - ML Engineering.mdx"
 M "src/content/docs/Machine Learning/Phase 11 - ML Engineering/Testing ML Code.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Capstone 1 - Fraud Screening End to End.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Capstone 2 - Churn with Point-in-Time Features.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Capstone 3 - Demand Forecasting for Ordering.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Capstone 4 - Ticket Triage with Text.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Capstone 5 - A Recommender with an Honest Evaluation.mdx"
 M "src/content/docs/Machine Learning/Phase 12 - Capstone Projects/Phase 12 - Capstone Projects.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Complex Numbers in One Page.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Functions Limits and Continuity.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Getting Ready Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Notation and Symbols.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/NumPy for Mathematics.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Single-Variable Calculus Refresher.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 00 - Getting Ready/Sums Products and Set Notation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 01 - Introduction and Motivation/Finding Words for Intuitions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 01 - Introduction and Motivation/Introduction and Motivation Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 01 - Introduction and Motivation/Two Ways to Read This Book.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Affine Spaces.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Basis and Rank.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Chapter 2 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Chapter 2 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Linear Algebra Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Linear Independence.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Linear Mappings.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Matrices.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Solving Systems of Linear Equations.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Systems of Linear Equations.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 02 - Linear Algebra/Vector Spaces.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Analytic Geometry Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Angles and Orthogonality.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Chapter 3 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Chapter 3 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Inner Product of Functions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Inner Products.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Lengths and Distances.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Norms.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Orthogonal Complement.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Orthogonal Projections.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Orthonormal Basis.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 03 - Analytic Geometry/Rotations.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Chapter 4 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Chapter 4 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Cholesky Decomposition.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Determinant and Trace.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Eigendecomposition and Diagonalization.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Eigenvalues and Eigenvectors.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Matrix Approximation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Matrix Decompositions Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Matrix Phylogeny.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 04 - Matrix Decompositions/Singular Value Decomposition.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Backpropagation and Automatic Differentiation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Chapter 5 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Chapter 5 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Differentiation of Univariate Functions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Gradients of Matrices.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Gradients of Vector-Valued Functions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Higher-Order Derivatives.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Linearization and Multivariate Taylor Series.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Partial Differentiation and Gradients.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Useful Identities for Computing Gradients.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 05 - Vector Calculus/Vector Calculus Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Change of Variables Inverse Transform.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Chapter 6 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Chapter 6 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Conjugacy and the Exponential Family.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Construction of a Probability Space.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Discrete and Continuous Probabilities.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Gaussian Distribution.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Probability and Distributions Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Sum Rule, Product Rule, and Bayes Theorem.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 06 - Probability and Distributions/Summary Statistics and Independence.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Chapter 7 Exercises and Solutions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Chapter 7 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Constrained Optimization and Lagrange Multipliers.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Continuous Optimization Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Convex Sets and Convex Functions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Legendre-Fenchel Transform and Convex Conjugate.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Linear and Quadratic Programming.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Momentum and Stochastic Gradient Descent.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 07 - Continuous Optimization/Optimization Using Gradient Descent.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Chapter 8 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Chapter 8 Worked Problems.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Data Models and Learning.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Directed Graphical Models.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Empirical Risk Minimization.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/MAP Estimation and Model Fitting.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Maximum Likelihood Estimation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Model Selection.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Probabilistic Modeling and Inference.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/Regularization and Cross-Validation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 08 - When Models Meet Data/When Models Meet Data Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Bayesian Linear Regression.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Chapter 9 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Chapter 9 Worked Problems.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Computing the Marginal Likelihood.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Linear Regression Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/MAP Estimation and Regularization.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Maximum Likelihood Estimation for Linear Regression.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Maximum Likelihood as Orthogonal Projection.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Overfitting in Linear Regression.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Posterior Predictions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/Problem Formulation.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 09 - Linear Regression/The Parameter Posterior.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Chapter 10 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Chapter 10 Worked Problems.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Dimensionality Reduction Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Eigenvector Computation and Low-Rank Approximations.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Finding the Principal Subspace.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Key Steps of PCA in Practice.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/PCA in High Dimensions.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/Problem Setting.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/The Latent Variable Perspective.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/The Maximum Variance Perspective.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 10 - Dimensionality Reduction with PCA/The Projection Perspective.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Chapter 11 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Chapter 11 Worked Problems.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Density Estimation Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Maximum Likelihood and Its Obstacle.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Responsibilities.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/The EM Algorithm.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/The Gaussian Mixture Model.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/The Latent Variable Perspective.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Updating the Covariances.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Updating the Means.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 11 - Density Estimation with GMM/Updating the Mixture Weights.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Chapter 12 Formula Sheet.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Chapter 12 Worked Problems.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Classification Overview.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Kernels.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Numerical Solution.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Separating Hyperplanes.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/The Concept of the Margin.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/The Convex Hull View.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/The Dual Support Vector Machine.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/The Hinge Loss.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/The Soft Margin SVM.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Chapter 12 - Classification with Support Vector Machines/Why the Margin Can Be Set to One.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Mathematics for Machine Learning.mdx"
 M "src/content/docs/Mathematics for Machine Learning/Recall Drill.mdx"
 M "src/content/docs/Python Automation and Scripting/Automation and Scripting.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Automating File Backups.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Batch Renaming Files Script.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Compressing Files (Zip and Tar archives).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Managing Paths with pathlib.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Monitoring File System Changes (Watchdog).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Pattern Matching with glob.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/Searching Files by Content or Extension.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/The Power of Scripting Why Automate.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/The os Module Navigating Directories.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 1 - OS & File System Automation/The shutil Module Copying Moving and Deleting.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Automating Excel Formulas and Charts.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Automating Google Sheets API.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Creating Word Documents with python-docx.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Extracting Text from PDFs.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Generating Automated Reports.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/PDF Manipulation Merging and Splitting.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Processing CSV Data with the csv Module.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 2 - Office & Productivity Automation/Working with Excel openpyxl Basics.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Automating Browser Tasks (Headless Mode).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Building a Price Tracker Bot.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/CSS Selectors vs XPath.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Downloading Images and Media in Bulk.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/HTTP Requests with the requests Library.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Handling Web Forms and Buttons.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Introduction to Selenium WebDriver.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Introduction to Web Scraping Ethics and robots.txt.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Parsing HTML with BeautifulSoup.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Scraping Dynamic JavaScript Websites.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 3 - Web Automation & Scraping/Wait Times Implicit vs Explicit Waits.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Automating Discord Messages.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Automating Outlook with pywin32.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Sending Emails with smtplib.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Sending HTML Emails and Attachments.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Sending SMS with Twilio API.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Slack Webhooks for System Alerts.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 4 - Communication Automation/Telegram Bot Integration for Notifications.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Automating Desktop Applications.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Controlling Mouse Movements and Clicks.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Creating Simple Message Box Alerts.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Introduction to pyautogui.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Keyboard Automation Typing and Hotkeys.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 5 - GUI & System Control/Screen Recognition (Locating Images on Screen).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Handling Errors in Long-Running Scripts.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Logging for Automation Scripts (logging module).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Running Scripts from the Command Line.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Scheduling Scripts on Linux and Mac (Cron Jobs).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Scheduling Scripts on Windows (Task Scheduler).mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Using Arguments with argparse.mdx"
 M "src/content/docs/Python Automation and Scripting/Phase 6 - Task Scheduling & Deployment/Using the schedule Library for Python.mdx"
 M "src/content/docs/Python Automation and Scripting/Safety Warning (Dry Runs and Backups).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Black Box White Box and Grey Box Testing.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Introduction to Software Quality Assurance (SQA).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Manual vs Automated Testing When to Choose.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Principles of Software Testing (Pesticide Paradox etc).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Software Development Life Cycle (SDLC) vs STLC.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/The Cost of a Bug Why Testing Matters.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/The V-Model in Software Testing.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 1 - Testing Fundamentals (QA Theory)/Verification vs Validation.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/Integration Testing Testing Module Interactions.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/Regression Testing Ensuring Old Features Still Work.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/Smoke and Sanity Testing.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/System Testing Testing the Whole Product.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/The Test Pyramid Strategy.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/Unit Testing Testing Individual Components.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 2 - Levels of Testing/User Acceptance Testing (UAT).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Class-level Setup setUpClass and tearDownClass.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Introduction to Python\342\200\231s unittest Library.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Organizing Tests into Test Suites.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Skipping Tests and Expected Failures.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Test Discovery and Running Tests.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/The Test Lifecycle setUp and tearDown.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Using assertEqual and Other Assertions.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 3 - Unit Testing with Python (unittest)/Writing Your First Test Case.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Generating HTML Test Reports.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Measuring Code Coverage with coverage.py.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Mocking and Patching with unittest.mock.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Parameterized Testing Running Tests with Multiple Data Sets.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Pytest Fixtures Managing Test Dependencies.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Pytest Markers Custom Tags and Filtering.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Why Choose pytest over unittest.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 4 - Modern Testing with pytest/Writing Concise Tests with Plain assert.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/API Testing Fundamentals.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/Automating UI Tests with Selenium & Python.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/Behavior Driven Development (BDD) with behave.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/Introduction to Playwright for Python.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/Testing REST APIs with the requests Library.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/The Page Object Model (POM) Pattern.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 5 - API & Web Testing Automation/Writing Tests in Gherkin (Given-When-Then).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Automated Refactoring with Black.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Complexity Analysis with Radon.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Finding Security Vulnerabilities with Bandit.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Introduction to Code Linting.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Static Type Checking with Mypy.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Using Flake8 for Style Checks.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 6 - Static Analysis & Code Quality/Using Pylint to Enforce Standards.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Automating Tests with GitHub Actions.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Defect Life Cycle (Bug Statuses).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Introduction to Continuous Integration (CI).mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Setting up Pre-commit Hooks.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Test-Driven Development (TDD) Workflow.mdx"
 M "src/content/docs/Software Testing and Quality/Phase 7 - CI - CD & Professional QA Workflow/Writing a Bug Report Best Practices.mdx"
 M "src/content/docs/Software Testing and Quality/Software Testing and Quality.mdx"
 M "src/content/docs/Software Testing and Quality/Suggested Testing Projects/Automated API Validation for a Weather Service.mdx"
 M "src/content/docs/Software Testing and Quality/Suggested Testing Projects/Building a CI CD Pipeline for a Flask App.mdx"
 M "src/content/docs/Software Testing and Quality/Suggested Testing Projects/Building a Test Suite for a Calculator App.mdx"
 M "src/content/docs/Software Testing and Quality/Suggested Testing Projects/E-commerce Checkout Flow UI Test.mdx"
 M "src/content/docs/Software Testing and Quality/Suggested Testing Projects/Refactoring Dirty Code using TDD.mdx"
 M src/content/docs/es/index.mdx
 M src/content/docs/guides/Book.mdx
 M src/content/docs/guides/Courses.mdx
 M src/content/docs/guides/Home.mdx
 M src/content/docs/guides/Youtube.mdx
 M src/content/docs/hi/index.mdx
 M src/content/docs/index.mdx
 M src/content/docs/ja/index.mdx
 M src/content/docs/policy.mdx
 M src/content/docs/projects/Advance/advanced_chatbot_with_nlp.mdx
 M src/content/docs/projects/Advance/advanced_image_captioning.mdx
 M src/content/docs/projects/Advance/advanced_image_processing_with_opencv.mdx
 M src/content/docs/projects/Advance/advanced_network_traffic_monitor.mdx
 M src/content/docs/projects/Advance/advanced_ocr_with_deep_learning.mdx
 M src/content/docs/projects/Advance/advanced_ocr_with_tesseract.mdx
 M src/content/docs/projects/Advance/advanced_password_manager.mdx
 M src/content/docs/projects/Advance/advanced_recommendation_system.mdx
 M src/content/docs/projects/Advance/advanced_spam_detection_system.mdx
 M src/content/docs/projects/Advance/ai_based_chess_game.mdx
 M src/content/docs/projects/Advance/ai_based_image_captioning.mdx
 M src/content/docs/projects/Advance/ai_based_language_translation.mdx
 M src/content/docs/projects/Advance/ai_based_news_summarizer.mdx
 M src/content/docs/projects/Advance/ai_based_predictive_analytics.mdx
 M src/content/docs/projects/Advance/ai_based_speech_synthesis.mdx
 M src/content/docs/projects/Advance/ai_based_voice_recognition.mdx
 M src/content/docs/projects/Advance/ai_driven_medical_diagnosis_system.mdx
 M src/content/docs/projects/Advance/ai_powered_chat_translation.mdx
 M src/content/docs/projects/Advance/ai_powered_customer_support_chatbot.mdx
 M src/content/docs/projects/Advance/ai_powered_document_search.mdx
 M src/content/docs/projects/Advance/ai_powered_fraud_detection_system.mdx
 M src/content/docs/projects/Advance/ai_powered_personal_assistant.mdx
 M src/content/docs/projects/Advance/ai_powered_recommendation_system.mdx
 M src/content/docs/projects/Advance/ai_powered_stock_market_predictor.mdx
 M src/content/docs/projects/Advance/ai_powered_traffic_prediction.mdx
 M src/content/docs/projects/Advance/ai_powered_video_summarizer.mdx
 M src/content/docs/projects/Advance/anomaly_detection_system.mdx
 M src/content/docs/projects/Advance/ar_augmented_reality_game.mdx
 M src/content/docs/projects/Advance/automated_code_review_system.mdx
 M src/content/docs/projects/Advance/automated_code_review_tool.mdx
 M src/content/docs/projects/Advance/automated_news_aggregator.mdx
 M src/content/docs/projects/Advance/automated_resume_screening_nlp.mdx
 M src/content/docs/projects/Advance/autonomous_drone_navigation.mdx
 M src/content/docs/projects/Advance/autonomous_robot_simulation_pygame.mdx
 M src/content/docs/projects/Advance/autonomous_vehicle_simulation.mdx
 M src/content/docs/projects/Advance/bioinformatics_data_analysis.mdx
 M src/content/docs/projects/Advance/blockchain_based_voting_system.mdx
 M src/content/docs/projects/Advance/chatbot_with_machine_learning.mdx
 M src/content/docs/projects/Advance/cloud_storage_manager.mdx
 M src/content/docs/projects/Advance/credit_card_fraud_detection.mdx
 M src/content/docs/projects/Advance/customer_segmentation_ml.mdx
 M src/content/docs/projects/Advance/data_encryption_tool.mdx
 M src/content/docs/projects/Advance/data_visualization_dashboard.mdx
 M src/content/docs/projects/Advance/deep_learning_image_classifier.mdx
 M src/content/docs/projects/Advance/document_search_engine.mdx
 M src/content/docs/projects/Advance/email_automation_system.mdx
 M src/content/docs/projects/Advance/face_recognition_system.mdx
 M src/content/docs/projects/Advance/gesture_recognition_system.mdx
 M src/content/docs/projects/Advance/handwriting_recognition.mdx
 M src/content/docs/projects/Advance/handwriting_recognition_system.mdx
 M src/content/docs/projects/Advance/image_caption_generator.mdx
 M src/content/docs/projects/Advance/image_segmentation.mdx
 M src/content/docs/projects/Advance/intelligent_personal_assistant.mdx
 M src/content/docs/projects/Advance/intrusion_detection_system.mdx
 M src/content/docs/projects/Advance/language_translation_app.mdx
 M src/content/docs/projects/Advance/machine_learning_recommendation_system.mdx
 M src/content/docs/projects/Advance/medical_diagnosis_ai.mdx
 M src/content/docs/projects/Advance/nlp_text_summarizer.mdx
 M src/content/docs/projects/Advance/object_detection_system.mdx
 M src/content/docs/projects/Advance/object_detection_tensorflow.mdx
 M src/content/docs/projects/Advance/optical_character_recognition.mdx
 M src/content/docs/projects/Advance/predictive_maintenance_system.mdx
 M src/content/docs/projects/Advance/real_time_air_quality_monitoring.mdx
 M src/content/docs/projects/Advance/real_time_anomaly_detection.mdx
 M src/content/docs/projects/Advance/real_time_churn_prediction.mdx
 M src/content/docs/projects/Advance/real_time_credit_scoring.mdx
 M src/content/docs/projects/Advance/real_time_customer_segmentation.mdx
 M src/content/docs/projects/Advance/real_time_demand_forecasting.mdx
 M src/content/docs/projects/Advance/real_time_emotion_detection.mdx
 M src/content/docs/projects/Advance/real_time_face_mask_detection.mdx
 M src/content/docs/projects/Advance/real_time_fraud_detection.mdx
 M src/content/docs/projects/Advance/real_time_gesture_detection.mdx
 M src/content/docs/projects/Advance/real_time_handwriting_detection.mdx
 M src/content/docs/projects/Advance/real_time_image_classification.mdx
 M src/content/docs/projects/Advance/real_time_image_extraction.mdx
 M src/content/docs/projects/Advance/real_time_image_generation.mdx
 M src/content/docs/projects/Advance/real_time_image_segmentation.mdx
 M src/content/docs/projects/Advance/real_time_image_translation.mdx
 M src/content/docs/projects/Advance/real_time_inventory_management.mdx
 M src/content/docs/projects/Advance/real_time_network_intrusion_detection.mdx
 M src/content/docs/projects/Advance/real_time_object_tracking.mdx
 M src/content/docs/projects/Advance/real_time_price_optimization.mdx
 M src/content/docs/projects/Advance/real_time_product_classification.mdx
 M src/content/docs/projects/Advance/real_time_recommendation_system.mdx
 M src/content/docs/projects/Advance/real_time_risk_assessment.mdx
 M src/content/docs/projects/Advance/real_time_sales_forecasting.mdx
 M src/content/docs/projects/Advance/real_time_sentiment_analysis.mdx
 M src/content/docs/projects/Advance/real_time_sentiment_classification.mdx
 M src/content/docs/projects/Advance/real_time_sign_language_detection.mdx
 M src/content/docs/projects/Advance/real_time_speech_recognition.mdx
 M src/content/docs/projects/Advance/real_time_stock_price_prediction.mdx
 M src/content/docs/projects/Advance/real_time_text_classification.mdx
 M src/content/docs/projects/Advance/real_time_text_extraction.mdx
 M src/content/docs/projects/Advance/real_time_text_generation.mdx
 M src/content/docs/projects/Advance/real_time_text_summarization.mdx
 M src/content/docs/projects/Advance/real_time_text_translation.mdx
 M src/content/docs/projects/Advance/real_time_topic_modeling.mdx
 M src/content/docs/projects/Advance/real_time_vehicle_detection.mdx
 M src/content/docs/projects/Advance/real_time_video_classification.mdx
 M src/content/docs/projects/Advance/real_time_video_extraction.mdx
 M src/content/docs/projects/Advance/real_time_video_generation.mdx
 M src/content/docs/projects/Advance/real_time_video_segmentation.mdx
 M src/content/docs/projects/Advance/real_time_video_translation.mdx
 M src/content/docs/projects/Advance/real_time_weather_forecasting.mdx
 M src/content/docs/projects/Advance/realtime_object_tracking.mdx
 M src/content/docs/projects/Advance/sentiment_analysis_model.mdx
 M src/content/docs/projects/Advance/speech_emotion_recognition.mdx
 M src/content/docs/projects/Advance/speech_to_text_converter.mdx
 M src/content/docs/projects/Advance/stock_price_prediction_model.mdx
 M src/content/docs/projects/Advance/time_series_forecasting.mdx
 M src/content/docs/projects/Advance/video_processing_tool.mdx
 M src/content/docs/projects/Advance/virtual_reality_game_pygame.mdx
 M src/content/docs/projects/Advance/weather_forecasting_app.mdx
 M src/content/docs/projects/Advance/web_scraping_automation.mdx
 M src/content/docs/projects/Advance/webapp_security_scanner.mdx
 M src/content/docs/projects/Advance/youtube_video_downloader.mdx
 M src/content/docs/projects/Advance/zodiac_sign_predictor.mdx
 M src/content/docs/projects/Beginners/asciiartgenerator.mdx
 M src/content/docs/projects/Beginners/automatedfilemover.mdx
 M src/content/docs/projects/Beginners/basic-calendar-app.mdx
 M src/content/docs/projects/Beginners/basic-text-editor.mdx
 M src/content/docs/projects/Beginners/basicalarmclock.mdx
 M src/content/docs/projects/Beginners/basicchatbot.mdx
 M src/content/docs/projects/Beginners/basicmusicplayer.mdx
 M src/content/docs/projects/Beginners/basicwebcrawler.mdx
 M src/content/docs/projects/Beginners/basicwebscrapper.mdx
 M src/content/docs/projects/Beginners/basicwebserver.mdx
 M src/content/docs/projects/Beginners/binarytodecimal.mdx
 M src/content/docs/projects/Beginners/blackjack.mdx
 M src/content/docs/projects/Beginners/calculatorgui.mdx
 M src/content/docs/projects/Beginners/currencyconverter.mdx
 M src/content/docs/projects/Beginners/currencyexchnageratecalculator.mdx
 M src/content/docs/projects/Beginners/dicerolling.mdx
 M src/content/docs/projects/Beginners/emailsender.mdx
 M src/content/docs/projects/Beginners/fibonaccisequence.mdx
 M src/content/docs/projects/Beginners/fileexplorer.mdx
 M src/content/docs/projects/Beginners/guessthenumber.mdx
 M src/content/docs/projects/Beginners/hangman.mdx
 M src/content/docs/projects/Beginners/helloworld.mdx
 M src/content/docs/projects/Beginners/json-data-validator.mdx
 M src/content/docs/projects/Beginners/morsecodetranslator.mdx
 M src/content/docs/projects/Beginners/movie-recommendation-system.mdx
 M src/content/docs/projects/Beginners/numberguessingwithai.mdx
 M src/content/docs/projects/Beginners/paint.mdx
 M src/content/docs/projects/Beginners/passwordstrengthchecker.mdx
 M src/content/docs/projects/Beginners/personaldiary.mdx
 M src/content/docs/projects/Beginners/quizapp.mdx
 M src/content/docs/projects/Beginners/randompasswordgenerator.mdx
 M src/content/docs/projects/Beginners/reversestring.mdx
 M src/content/docs/projects/Beginners/rockpaperscissors.mdx
 M src/content/docs/projects/Beginners/rssfeedreader.mdx
 M src/content/docs/projects/Beginners/simple-blog-system.mdx
 M src/content/docs/projects/Beginners/simplecalculator.mdx
 M src/content/docs/projects/Beginners/simplereminderapp.mdx
 M src/content/docs/projects/Beginners/simplestopwatch.mdx
 M src/content/docs/projects/Beginners/tempconv.mdx
 M src/content/docs/projects/Beginners/textbasedadventuregame.mdx
 M src/content/docs/projects/Beginners/todo.mdx
 M src/content/docs/projects/Beginners/todolist.mdx
 M src/content/docs/projects/Beginners/urlshorter.mdx
 M src/content/docs/projects/Beginners/webpagecontentdownloader.mdx
 M src/content/docs/projects/Beginners/webpagescrapernotifications.mdx
 M src/content/docs/projects/Beginners/wordcounter.mdx
 M src/content/docs/projects/intermediate/advanced-web-scraping.mdx
 M src/content/docs/projects/intermediate/ai-task-manager.mdx
 M src/content/docs/projects/intermediate/anagram-game.mdx
 M src/content/docs/projects/intermediate/automated-email-sender.mdx
 M src/content/docs/projects/intermediate/basic-chatroom-app.mdx
 M src/content/docs/projects/intermediate/basic-file-version-control-system.mdx
 M src/content/docs/projects/intermediate/basic_ocr_with_tesseract.mdx
 M src/content/docs/projects/intermediate/chat-application-socket.mdx
 M src/content/docs/projects/intermediate/content-management-system.mdx
 M src/content/docs/projects/intermediate/cryptocurrency-portfolio-tracker.mdx
 M src/content/docs/projects/intermediate/data-visualization-suite.mdx
 M src/content/docs/projects/intermediate/ecommerce-analytics.mdx
 M src/content/docs/projects/intermediate/ecommerce-website.mdx
 M src/content/docs/projects/intermediate/file-encryption-tool.mdx
 M src/content/docs/projects/intermediate/file-synchronization-tool.mdx
 M src/content/docs/projects/intermediate/github-profile-viewer.mdx
 M src/content/docs/projects/intermediate/gui-sql-database-viewer.mdx
 M src/content/docs/projects/intermediate/hangman-database-game.mdx
 M src/content/docs/projects/intermediate/image-recognition-with-opencv.mdx
 M src/content/docs/projects/intermediate/interactive-periodic-table.mdx
 M src/content/docs/projects/intermediate/ml-model-trainer.mdx
 M src/content/docs/projects/intermediate/morse-code-audio-player.mdx
 M src/content/docs/projects/intermediate/multiplayer-tic-tac-toe.mdx
 M src/content/docs/projects/intermediate/news-aggregator.mdx
 M src/content/docs/projects/intermediate/personal-finance-tracker.mdx
 M src/content/docs/projects/intermediate/portfolio-website.mdx
 M src/content/docs/projects/intermediate/qr-code-attendance-system.mdx
 M src/content/docs/projects/intermediate/quiz-game-with-timer.mdx
 M src/content/docs/projects/intermediate/real-time-chat-application.mdx
 M src/content/docs/projects/intermediate/realtime-chat.mdx
 M src/content/docs/projects/intermediate/rest-api-auth.mdx
 M src/content/docs/projects/intermediate/rest-api-server.mdx
 M src/content/docs/projects/intermediate/simple-blog-with-flask.mdx
 M src/content/docs/projects/intermediate/simple-weather-forecast-app.mdx
 M src/content/docs/projects/intermediate/social-media-analytics.mdx
 M src/content/docs/projects/intermediate/url-expander.mdx
 M src/content/docs/projects/intermediate/url-shortener-analytics.mdx
 M src/content/docs/projects/intermediate/weather-app-gui.mdx
 M src/content/docs/projects/intermediate/weather-app-with-voice-commands.mdx
 M src/content/docs/projects/intermediate/web-scraping-pipeline.mdx
 M src/content/docs/reference/contact.mdx
 D src/content/docs/src/env.d.ts
 M "src/content/docs/tutorials/Algorithms Visualized/Big-O Visualized.mdx"
 M "src/content/docs/tutorials/Algorithms Visualized/Recursion Visualized.mdx"
 M "src/content/docs/tutorials/Algorithms Visualized/Searching Visualized.mdx"
 M "src/content/docs/tutorials/Algorithms Visualized/Sorting Visualized.mdx"
 M src/content/docs/tutorials/Boolean.mdx
 M src/content/docs/tutorials/Comment.mdx
 M src/content/docs/tutorials/DataType.mdx
 M "src/content/docs/tutorials/Datatype Casting.mdx"
 M src/content/docs/tutorials/GetStarted.mdx
 M src/content/docs/tutorials/Input.mdx
 M src/content/docs/tutorials/Installation.mdx
 M src/content/docs/tutorials/Introduction.mdx
 M "src/content/docs/tutorials/Modern Python/Concurrency.mdx"
 M "src/content/docs/tutorials/Modern Python/Dataclasses.mdx"
 M "src/content/docs/tutorials/Modern Python/F-Strings Deep Dive.mdx"
 M "src/content/docs/tutorials/Modern Python/Networking.mdx"
 M "src/content/docs/tutorials/Modern Python/Type Hints and typing.mdx"
 M "src/content/docs/tutorials/Modern Python/Virtual Environments and pip.mdx"
 M "src/content/docs/tutorials/Modern Python/Walrus Operator.mdx"
 M src/content/docs/tutorials/Numbers.mdx
 M src/content/docs/tutorials/Print.mdx
 M "src/content/docs/tutorials/Python Array/Access the Array.mdx"
 M "src/content/docs/tutorials/Python Array/Add and Remove in Array.mdx"
 M "src/content/docs/tutorials/Python Array/Array Methods.mdx"
 M "src/content/docs/tutorials/Python Array/Array Operations.mdx"
 M "src/content/docs/tutorials/Python Array/Python Array.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Async Context Managers and Async Generators.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Async HTTP with aiohttp.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Async Queues (producer-consumer).mdx"
 M "src/content/docs/tutorials/Python Asyncio/Asyncio Mini Project (Concurrent URL checker).mdx"
 M "src/content/docs/tutorials/Python Asyncio/Asyncio Synchronization (Lock, Semaphore).mdx"
 M "src/content/docs/tutorials/Python Asyncio/Asyncio in Python.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Coroutines and await.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Event Loop and asyncio.run.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Structured Concurrency with TaskGroup.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Tasks (create_task) and gather.mdx"
 M "src/content/docs/tutorials/Python Asyncio/Timeouts and Cancellation.mdx"
 M "src/content/docs/tutorials/Python Comprehensions/Comprehensions.mdx"
 M "src/content/docs/tutorials/Python Context Managers/Context Managers.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Assert.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Break Statement.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Continue.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Control Statement.mdx"
 M "src/content/docs/tutorials/Python Control Statement/For Loop.mdx"
 M "src/content/docs/tutorials/Python Control Statement/If-else.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Match Case.mdx"
 M "src/content/docs/tutorials/Python Control Statement/Pass.mdx"
 M "src/content/docs/tutorials/Python Control Statement/While Loop.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Access the Dictionary.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Add and Remove in Dictionary.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Dictionary Methods.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Dictionary Operations.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Nested Dictionary.mdx"
 M "src/content/docs/tutorials/Python Dictionaries/Python Dictionaries.mdx"
 M "src/content/docs/tutorials/Python Errors and Exceptions/Debugging Tracebacks.mdx"
 M "src/content/docs/tutorials/Python Errors and Exceptions/Errors and Exceptions.mdx"
 M "src/content/docs/tutorials/Python Errors and Exceptions/else-finally.mdx"
 M "src/content/docs/tutorials/Python Errors and Exceptions/raise-and-custom-exceptions.mdx"
 M "src/content/docs/tutorials/Python Errors and Exceptions/try-except.mdx"
 M "src/content/docs/tutorials/Python Exception Handling/Exception Handling.mdx"
 M "src/content/docs/tutorials/Python File Handling/File Handling.mdx"
 M "src/content/docs/tutorials/Python File Handling/File Methods.mdx"
 M "src/content/docs/tutorials/Python File Handling/File Operations.mdx"
 M "src/content/docs/tutorials/Python File Handling/OS Methods.mdx"
 M "src/content/docs/tutorials/Python File Handling/Write and Read File.mdx"
 M "src/content/docs/tutorials/Python Function/Args and Kwargs.mdx"
 M "src/content/docs/tutorials/Python Function/Function Annotations.mdx"
 M "src/content/docs/tutorials/Python Function/Function.mdx"
 M "src/content/docs/tutorials/Python Function/Lambda Function.mdx"
 M "src/content/docs/tutorials/Python Function/Python Module/Built-in Module.mdx"
 M "src/content/docs/tutorials/Python Function/Python Module/Module.mdx"
 M "src/content/docs/tutorials/Python Function/Typeofarg.mdx"
 M "src/content/docs/tutorials/Python Functional Programming/Closures and Scope.mdx"
 M "src/content/docs/tutorials/Python Functional Programming/Map Filter Reduce.mdx"
 M "src/content/docs/tutorials/Python Functional Programming/Recursion.mdx"
 M "src/content/docs/tutorials/Python Iterators and Generators/Iterators and Generators.mdx"
 M "src/content/docs/tutorials/Python List/Access the list.mdx"
 M "src/content/docs/tutorials/Python List/List Methods.mdx"
 M "src/content/docs/tutorials/Python List/List Operations.mdx"
 M "src/content/docs/tutorials/Python List/Python List.mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Common Pitfalls (pickling, __main__).mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Mini Project (Parallel Number Processing).mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Multiprocessing in Python.mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Process (create, start, join).mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Process Pool (Pool, map, starmap).mdx"
 M "src/content/docs/tutorials/Python MultiProcessing/Sharing Data (Queue, Pipe, Manager).mdx"
 M "src/content/docs/tutorials/Python Networking/Building a Simple HTTP Server.mdx"
 M "src/content/docs/tutorials/Python Networking/HTTP Requests with requests.mdx"
 M "src/content/docs/tutorials/Python Networking/Networking Errors and Timeouts.mdx"
 M "src/content/docs/tutorials/Python Networking/Networking in Python.mdx"
 M "src/content/docs/tutorials/Python Networking/Sockets (TCP Client and Server).mdx"
 M "src/content/docs/tutorials/Python Networking/Working with JSON APIs.mdx"
 M "src/content/docs/tutorials/Python OOPS/Abstraction.mdx"
 M "src/content/docs/tutorials/Python OOPS/Access Modifiers.mdx"
 M "src/content/docs/tutorials/Python OOPS/Anonymous Class.mdx"
 M "src/content/docs/tutorials/Python OOPS/Class.mdx"
 M "src/content/docs/tutorials/Python OOPS/Constructor.mdx"
 M "src/content/docs/tutorials/Python OOPS/Decorator.mdx"
 M "src/content/docs/tutorials/Python OOPS/Dynamic Binding and Typing.mdx"
 M "src/content/docs/tutorials/Python OOPS/Encapsulation.mdx"
 M "src/content/docs/tutorials/Python OOPS/Enum.mdx"
 M "src/content/docs/tutorials/Python OOPS/Inheritance.mdx"
 M "src/content/docs/tutorials/Python OOPS/Inner Class.mdx"
 M "src/content/docs/tutorials/Python OOPS/Interfaces.mdx"
 M "src/content/docs/tutorials/Python OOPS/Method Overloading.mdx"
 M "src/content/docs/tutorials/Python OOPS/Method Overriding.mdx"
 M "src/content/docs/tutorials/Python OOPS/Methods.mdx"
 M "src/content/docs/tutorials/Python OOPS/Polymorphism.mdx"
 M "src/content/docs/tutorials/Python OOPS/Reflection.mdx"
 M "src/content/docs/tutorials/Python OOPS/python oops.mdx"
 M "src/content/docs/tutorials/Python Operator/Arithmetic Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Assignment Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Bitwise Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Identity Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Logical Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Membership Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Operator Function.mdx"
 M "src/content/docs/tutorials/Python Operator/Operator Precedence.mdx"
 M "src/content/docs/tutorials/Python Operator/Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Relational Operators.mdx"
 M "src/content/docs/tutorials/Python Operator/Ternary Operator.mdx"
 M "src/content/docs/tutorials/Python Set/Access the Set.mdx"
 M "src/content/docs/tutorials/Python Set/Add and Remove in Set.mdx"
 M "src/content/docs/tutorials/Python Set/Frozen Set.mdx"
 M "src/content/docs/tutorials/Python Set/Python Set.mdx"
 M "src/content/docs/tutorials/Python Set/Set Methods.mdx"
 M "src/content/docs/tutorials/Python Set/Set Operations.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Argparse and sys.argv.mdx"
 M "src/content/docs/tutorials/Python Standard Library/CSV.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Collections.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Date and Time.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Itertools and Functools.mdx"
 M "src/content/docs/tutorials/Python Standard Library/JSON.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Logging.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Math Random Statistics.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Pathlib.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Pickle.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Regular Expressions.mdx"
 M "src/content/docs/tutorials/Python Standard Library/SQLite3.mdx"
 M "src/content/docs/tutorials/Python Standard Library/Testing with unittest and pytest.mdx"
 M "src/content/docs/tutorials/Python Strings/Concatenation.mdx"
 M "src/content/docs/tutorials/Python Strings/Escape String.mdx"
 M "src/content/docs/tutorials/Python Strings/Formatting String.mdx"
 M "src/content/docs/tutorials/Python Strings/Modify String.mdx"
 M "src/content/docs/tutorials/Python Strings/String Methods.mdx"
 M "src/content/docs/tutorials/Python Strings/String Slicing.mdx"
 M "src/content/docs/tutorials/Python Strings/String.mdx"
 M "src/content/docs/tutorials/Python Synchronization/Barrier (start together).mdx"
 M "src/content/docs/tutorials/Python Synchronization/Condition Variables.mdx"
 M "src/content/docs/tutorials/Python Synchronization/Deadlocks and How to Avoid Them.mdx"
 M "src/content/docs/tutorials/Python Synchronization/Events (signal between threads).mdx"
 M "src/content/docs/tutorials/Python Synchronization/Locks (Lock vs RLock).mdx"
 M "src/content/docs/tutorials/Python Synchronization/Semaphores (limit concurrency).mdx"
 M "src/content/docs/tutorials/Python Synchronization/Synchronization in Python.mdx"
 M "src/content/docs/tutorials/Python Threading/Creating and Starting Threads.mdx"
 M "src/content/docs/tutorials/Python Threading/Daemon Threads.mdx"
 M "src/content/docs/tutorials/Python Threading/Thread Communication (Queue).mdx"
 M "src/content/docs/tutorials/Python Threading/Thread Pool with concurrent.futures.mdx"
 M "src/content/docs/tutorials/Python Threading/Thread Synchronization with Lock.mdx"
 M "src/content/docs/tutorials/Python Threading/Threading in Python.mdx"
 M "src/content/docs/tutorials/Python Tuple/Access the Tuple.mdx"
 M "src/content/docs/tutorials/Python Tuple/Python Tuple.mdx"
 M "src/content/docs/tutorials/Python Tuple/Tuple Methods.mdx"
 M "src/content/docs/tutorials/Python Tuple/Tuple Operations.mdx"
 M "src/content/docs/tutorials/Python Tuple/Unpack the Tuple.mdx"
 M "src/content/docs/tutorials/Python Tuple/Update the Tuple.mdx"
 M "src/content/docs/tutorials/Python Variables/Global Variables.mdx"
 M "src/content/docs/tutorials/Python Variables/Multiple Assignment.mdx"
 M "src/content/docs/tutorials/Python Variables/Naming Convention.mdx"
 M "src/content/docs/tutorials/Python Variables/Variable Assignment.mdx"
 M src/content/docs/tutorials/Syntax.mdx
 M src/content/docs/zh-cn/index.mdx
 M src/data/dsa/index.ts
 M src/data/mml/index.ts
 D src/env.d.ts
 M src/lib/auth/hint.ts
 M src/lib/firebase/auth.ts
 M src/lib/firebase/client.ts
 M src/lib/firebase/config.ts
 M src/lib/progress/awards.ts
 M src/lib/progress/ids.ts
 M src/lib/progress/local.ts
 M src/lib/progress/sync.ts
 D src/lib/utils.ts
 M src/styles/global.css
 D src/styles/poppins.css
 M src/styles/progress.css
 D src/styles/tailwind.css
 M src/styles/viz.css
M  tsconfig.json
?? app/(app)/
?? app/(courses)/
?? app/(docs)/layout.tsx
?? app/api/
?? app/carried-tokens.css
?? app/error.tsx
?? app/global-error.tsx
?? app/home.css
?? app/not-found.tsx
?? app/page.tsx
?? app/robots.ts
?? app/rss.xml/
?? app/sitemap.ts
?? components.json
?? components/
?? docs/handoff/
?? firebase.json
?? firebase/firestore.indexes.json
?? firebase/functions/package.json
?? instrumentation.ts
?? lib/courses.data.mjs
?? lib/courses.ts
?? lib/last-modified.ts
?? lib/order.ts
?? lib/rehype/
?? lib/report-error.ts
?? lib/server/
?? lib/site.ts
?? lib/strings.ts
?? lib/utils.ts
?? mdx-components.tsx
?? migration/mdx-component-list.json
?? public/images/dl/phase-01-foundations/autograd-from-scratch/xor-training-dark.webp
?? public/images/dl/phase-01-foundations/autograd-from-scratch/xor-training-light.webp
?? public/images/dl/phase-01-foundations/introduction-to-neural-networks-the-perceptron/xor-ceiling-dark.webp
?? public/images/dl/phase-01-foundations/introduction-to-neural-networks-the-perceptron/xor-ceiling-light.webp
?? public/images/dl/phase-03-vision/image-segmentation/segmentation-samples-dark.webp
?? public/images/dl/phase-03-vision/image-segmentation/segmentation-samples-light.webp
?? public/images/dl/phase-06-generative/diffusion/schedule-comparison-dark.webp
?? public/images/dl/phase-06-generative/diffusion/schedule-comparison-light.webp
?? public/images/dl/phase-06-generative/diffusion/what-fixed-it-dark.webp
?? public/images/dl/phase-06-generative/diffusion/what-fixed-it-light.webp
?? public/images/dl/phase-06-generative/gans/samples-dark.webp
?? public/images/dl/phase-06-generative/gans/samples-light.webp
?? public/images/dl/phase-06-generative/variational-autoencoders/latent-structure-dark.webp
?? public/images/dl/phase-06-generative/variational-autoencoders/latent-structure-light.webp
?? public/images/dl/phase-09-capstones/generative-project/latent-dark.webp
?? public/images/dl/phase-09-capstones/generative-project/latent-light.webp
?? public/images/ml/phase-02-preprocessing/eda-correlations/geographic-scatter-dark.webp
?? public/images/ml/phase-02-preprocessing/eda-correlations/geographic-scatter-light.webp
?? public/images/ml/phase-02-preprocessing/eda-correlations/income-vs-value-dark.webp
?? public/images/ml/phase-02-preprocessing/eda-correlations/income-vs-value-light.webp
?? public/images/ml/phase-02-preprocessing/end-to-end/residual-analysis-dark.webp
?? public/images/ml/phase-02-preprocessing/end-to-end/residual-analysis-light.webp
?? public/images/ml/phase-05-ensembles/bagging/variance-reduction-dark.webp
?? public/images/ml/phase-05-ensembles/bagging/variance-reduction-light.webp
?? public/images/ml/phase-06-unsupervised/hierarchical-clustering-dendrograms/linkage-on-moons-dark.webp
?? public/images/ml/phase-06-unsupervised/hierarchical-clustering-dendrograms/linkage-on-moons-light.webp
?? public/images/ml/phase-06-unsupervised/introduction-to-clustering/cluster-shapes-dark.webp
?? public/images/ml/phase-06-unsupervised/introduction-to-clustering/cluster-shapes-light.webp
?? public/images/ml/phase-06-unsupervised/k-means-clustering-algorithm/where-kmeans-fails-dark.webp
?? public/images/ml/phase-06-unsupervised/k-means-clustering-algorithm/where-kmeans-fails-light.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/pca-vs-tsne-digits-dark.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/pca-vs-tsne-digits-light.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/perplexity-sweep-dark.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/perplexity-sweep-light.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/swiss-roll-unrolled-dark.webp
?? public/images/ml/phase-06-unsupervised/t-sne-and-manifold-learning/swiss-roll-unrolled-light.webp
?? public/images/ml/phase-09-interpretability/partial-dependence-and-ice-plots/centred-ice-dark.webp
?? public/images/ml/phase-09-interpretability/partial-dependence-and-ice-plots/centred-ice-light.webp
?? public/images/ml/phase-10-applied/anomaly-and-outlier-detection/two-kinds-dark.webp
?? public/images/ml/phase-10-applied/anomaly-and-outlier-detection/two-kinds-light.webp
?? public/images/mml/cholesky-decomposition/cholesky-sampling-dark.webp
?? public/images/mml/cholesky-decomposition/cholesky-sampling-light.webp
?? public/images/mml/complex-numbers-in-one-page/conjugate-pairs-and-the-axis-dark.webp
?? public/images/mml/complex-numbers-in-one-page/conjugate-pairs-and-the-axis-light.webp
?? public/images/mml/determinant-and-trace/trace-invariant-under-basis-change-dark.webp
?? public/images/mml/determinant-and-trace/trace-invariant-under-basis-change-light.webp
?? public/images/mml/directed-graphical-models/the-collider-effect-dark.webp
?? public/images/mml/directed-graphical-models/the-collider-effect-light.webp
?? public/images/mml/eigendecomposition-and-diagonalization/pdp-three-steps-dark.webp
?? public/images/mml/eigendecomposition-and-diagonalization/pdp-three-steps-light.webp
?? public/images/mml/eigenvalues-and-eigenvectors/five-mappings-dark.webp
?? public/images/mml/eigenvalues-and-eigenvectors/five-mappings-light.webp
?? public/images/mml/inner-products/spd-or-not-dark.webp
?? public/images/mml/inner-products/spd-or-not-light.webp
?? public/images/mml/lengths-and-distances/cauchy-schwarz-dark.webp
?? public/images/mml/lengths-and-distances/cauchy-schwarz-light.webp
?? public/images/mml/linear-and-quadratic-programming/an-lp-optimum-is-a-vertex-dark.webp
?? public/images/mml/linear-and-quadratic-programming/an-lp-optimum-is-a-vertex-light.webp
?? public/images/mml/maximum-likelihood-estimation-for-linear-regression/one-quadratic-one-solution-dark.webp
?? public/images/mml/maximum-likelihood-estimation-for-linear-regression/one-quadratic-one-solution-light.webp
?? public/images/mml/orthogonal-complement/pythagoras-in-five-dimensions-dark.webp
?? public/images/mml/orthogonal-complement/pythagoras-in-five-dimensions-light.webp
?? public/images/mml/separating-hyperplanes/many-separators-one-margin-dark.webp
?? public/images/mml/separating-hyperplanes/many-separators-one-margin-light.webp
?? public/images/mml/singular-value-decomposition/svd-three-stages-dark.webp
?? public/images/mml/singular-value-decomposition/svd-three-stages-light.webp
?? public/images/mml/summary-statistics-and-independence/mean-median-mode-dark.webp
?? public/images/mml/summary-statistics-and-independence/mean-median-mode-light.webp
?? public/images/mml/summary-statistics-and-independence/same-variance-different-covariance-dark.webp
?? public/images/mml/summary-statistics-and-independence/same-variance-different-covariance-light.webp
?? public/images/mml/summary-statistics-and-independence/uncorrelated-is-not-independent-dark.webp
?? public/images/mml/summary-statistics-and-independence/uncorrelated-is-not-independent-light.webp
?? public/scripts/exercise-worker.js
?? scripts/check-mdx.mjs
?? scripts/extract-learn-css.mjs
?? scripts/gen-mdx-components.mjs
?? scripts/gen-search-index.mjs
?? scripts/migrate-imports.mjs
?? scripts/rasterize-figures.mjs
?? scripts/smoke-routes.mjs
?? scripts/sync-content-assets.mjs
?? src/content/i18n/
?? src/data/exams/data-analytics.yaml
?? src/data/exams/deep-learning.yaml
?? src/data/exams/dsa-with-python.yaml
?? src/data/exams/flask-tutorials.yaml
?? src/data/exams/machine-learning.yaml
?? src/data/exams/mathematics-for-machine-learning.yaml
?? src/data/exams/projects.yaml
?? src/data/exams/python-automation-and-scripting.yaml
?? src/data/exams/software-testing-and-quality.yaml
?? src/lib/forms.ts
?? tsconfig.tsbuildinfo
?? types/
?? vercel.json
- Recent commits:
8581cac adding the login and other things
b4df2ad adding the machine learning maths fully
fa10ccc adding languages
c3c13af updating the astro and starlight version
4f22a8a fixing the error

### Model Summary
(TODO: fill after compaction — 8–12 bullets)

### Handoff Context (paste into next session)
(TODO: fill after compaction — 10–20 lines of concrete resume instructions)

---

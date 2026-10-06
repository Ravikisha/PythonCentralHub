# Launch checklist

These steps happen outside the code: in Vercel, Firebase, GitHub, or your
email provider. The code already handles each case, and anything not set up
degrades without breaking. Work down the list.

## 1. Vercel environment variables

Set these under Project → Settings → Environment Variables (Production).
`.env.example` documents each one.

| Variable | Needed for | Without it |
|---|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | Every `/api/*` route except search and client-error | Exams, certificates, the leaderboard, account deletion and forms answer 503 |
| `RECAPTCHA_SECRET` | Contact and feedback forms (server path) | Forms fall back to direct Firestore writes (see step 3) |
| `CRON_SECRET` | Weekly digest cron | The digest refuses to run |
| `RESEND_API_KEY` + `EMAIL_FROM` | Sending the digest directly | Digest mail is queued in Firestore `mail/` and only sent if the Trigger Email extension is installed |
| `ADMIN_EMAILS` | `/admin/` | Nobody can open the admin page |
| `ERROR_WEBHOOK_URL` | Optional: error alerts in Slack or Discord | Errors are only in Vercel's function logs (filter on `pythoncentralhub:error`) |
| `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` | Rate limits shared by every server instance (search, forms, error reports). Add Vercel's Upstash integration and it sets both | Each instance keeps its own count, so limits are per instance only |
| `NEXT_PUBLIC_SITE_URL` | Forcing the primary address | Leave unset: Vercel's production domain is used (see section 4) |

## 2. Vercel features

- **Analytics** and **Speed Insights**: switch both on in the Vercel
  dashboard. The components are already in `app/layout.tsx`, and they send
  nothing until the features are on.
- **Cron**: `vercel.json` schedules `/api/send-digest/` for Mondays at 09:00 UTC.
  Vercel sends `CRON_SECRET` with each call.
- **Firewall**: in Project → Firewall, add a rate-limit rule for
  `/api/*` (for example 120 requests per minute per IP). It stops floods
  before they reach a function, which the in-code limits cannot do.
- **Content-Security-Policy**: it ships as *Report-Only*. After a week in
  production, filter the logs on `csp` (reports come through
  `/api/csp-report/`). Add anything legitimate to the policy in
  `next.config.ts`, then rename the header to `Content-Security-Policy` so it
  is enforced.

## 3. Firebase

- **Deploy the rules and indexes**: `npm run firebase:rules` and
  `npm run firebase:indexes`. The index is needed by course reviews. This version
  adds `stats/exercises`, which records exercise passes. Until you deploy,
  passes stay in the browser. The code writes that document separately, so
  nothing else breaks.
- **Lock the forms** after `RECAPTCHA_SECRET` is set in Vercel: in
  `firebase/firestore.rules`, change `allow create` on `contact/` and
  `feedback/` to `allow create: if false;`, then deploy the rules again. Do
  this only after `/api/submit-form/` is confirmed working, since the forms
  rely on the direct write until then.
- **Authorised domains**: add the production domain under Authentication →
  Settings.
- **Email**: either set the Resend variables from step 1 and verify the
  sending domain in Resend, or install the "Trigger Email from Firestore"
  extension pointed at the `mail` collection. You only need one of the two.

## 4. Brand and domains

The site is **Python Central Hub**: the name, the GitHub repository and the
Firebase project all match. The logo is drawn in
`components/brand/Wordmark.tsx`; after changing it, run
`node scripts/brand-icons.mjs` to regenerate the favicon, app icons and the
default share image.

It is served on two addresses, and both work:

- **python-central-hub.vercel.app**: live now.
- **pythoncentralhub.live**: the domain the 1,116 indexed lesson URLs were
  published under. As of 2026-10-06 it does not resolve (no DNS records), so
  it needs reconnecting:
  1. Make sure the domain registration is active at the registrar.
  2. Vercel → Project → Settings → Domains → add `pythoncentralhub.live` and
     `www.pythoncentralhub.live`; set the DNS records Vercel shows (A record to
     Vercel for the apex, CNAME for www).
  3. Mark `pythoncentralhub.live` as the **primary** domain and redirect `www`
     to it. Leave `python-central-hub.vercel.app` serving.
  4. Redeploy. Canonical links, the sitemap, the feed and emails switch to
     the primary domain automatically (`lib/site.ts`), so search engines keep
     one copy of each page.

On **each** address the site is served on:

- Firebase console → Authentication → Settings → **Authorized domains**: add
  `python-central-hub.vercel.app`, `pythoncentralhub.live` and
  `www.pythoncentralhub.live`, or sign-in fails there.
- reCAPTCHA admin → the v3 key → **Domains**: add the same three.
- Resend: verify `pythoncentralhub.live` as a sending domain before using an
  `@pythoncentralhub.live` address in `EMAIL_FROM` (it needs the domain's DNS).
- **Ad files**: `public/ads.txt` and `ads2.txt` have been removed; the site
  shows no ads.

## 5. Tests

- `npm test`: unit tests (grading, certificates, rate limits, slugs, progress).
- `npm run test:rules`: Firestore rules against the emulator. Needs Java; CI
  runs it.
- `npm run test:e2e`: guest flows in Chromium. `npm run test:e2e:full` adds
  sign-up → assessment → certificate → verification against the Auth and
  Firestore emulators.

## 6. Before announcing

- Run `npm run build` locally or let CI run it, then check `/`, a course
  page, a lesson with an exercise, `/login/` and `/verify/`.
- Sign up with a real address, verify it, finish a course with a test account,
  sit the assessment, and check that both certificate kinds show at `/verify/`.
- Run a Lighthouse pass on the home page and one lesson, and save the numbers.
  Speed Insights then tracks real visitors from launch day. Watch LCP on
  lessons in particular: locally it measured 4-9 s under mobile throttling,
  which needs confirming on the real deployment and CDN.

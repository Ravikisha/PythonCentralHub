# Authentication, accounts & progress

Phases 0–4 of the learning-platform work: Firebase foundation, auth, progress
tracking, server-graded assessments with certificates, and the engagement layer
(XP, badges, private notes, leaderboard, email digests).

## Why it is shaped this way

The site is **statically generated** — `astro.config.mjs` declares no adapter
and `vercel.json` ships `dist/` as static files. There is no server, no
session cookie and no middleware. Everything below therefore runs in the
browser, and anything that must be trusted (certificate issuance, exam
grading) has to move to a Cloud Function later rather than into page JS.

The second constraint is scale: `Feedback.astro` renders inside the Footer
override, so it is on all ~1190 pages. Anything it imports is shipped
site-wide. That is why the Firebase SDK is loaded through dynamic `import()`
everywhere and why the header does not ask Firebase who is signed in.

## Files

| File | Role |
| --- | --- |
| `src/lib/firebase/config.ts` | Web config, `PUBLIC_FIREBASE_*` overrides with committed public defaults |
| `src/lib/firebase/client.ts` | Lazy `FirebaseApp`, `getDb()`, `getAuthClient()`, idle-deferred Analytics |
| `src/lib/firebase/auth.ts` | Sign-in/up/out, profile doc, data export, account deletion, error→key mapping |
| `src/lib/auth/hint.ts` | Firebase-free localStorage mirror of "who is signed in" |
| `src/lib/auth/messages.ts` | Client lookup of translated errors, status line, safe `?next=` handling |
| `src/components/UserMenu.astro` | Header account control |
| `src/components/SocialIcons.astro` | Starlight override that mounts the menu in the header |
| `src/components/auth/AuthProviders.astro` | Google / GitHub buttons |
| `src/components/auth/AuthMessages.astro` | Ships the translated `pch.authErr*` table to the browser |
| `src/pages/{login,signup,reset-password,verify-email,profile}.astro` | The auth pages |
| `firebase/firestore.rules` | Deny-by-default rules; `users/{uid}` is owner-only |
| `src/lib/progress/ids.ts` | URL → stable, locale-independent page id |
| `src/lib/progress/local.ts` | localStorage store, change notification, debounced flush queue |
| `src/lib/progress/sync.ts` | Firestore push/pull and the local↔cloud merge (accounts only) |
| `src/components/progress/MarkComplete.astro` | Per-page complete + bookmark buttons, quiz listener |
| `src/pages/dashboard.astro` | Streaks, per-module bars, bookmarks |
| `scripts/gen-progress-manifest.mjs` | Build-time module page counts → `public/progress-manifest.json` |
| `lib/server/admin.ts` | Admin SDK init, ID-token verification (revocation checked), real-lesson counting, error handling |
| `app/api/grade-exam/route.ts` | Marks an assessment against the hidden key; score only on a fail; cooldown in a transaction |
| `app/api/issue-certificate/route.ts` | Issues a certificate, counting only real lessons of the course |
| `app/api/publish-leaderboard/route.ts` | Recomputes a public leaderboard entry from real lessons and issued certificates |
| `app/api/send-digest/route.ts` | Weekly digest, run by Vercel Cron, to the verified Auth address only |
| `app/api/delete-account/route.ts` | Deletes an account, its data, attempts and leaderboard row (needs a recent sign-in) |
| `app/api/submit-form/route.ts` | Contact and feedback forms, reCAPTCHA verified server-side |
| `src/data/exams/*.yaml` | Question banks, one file per module |
| `scripts/seed-exams.mjs` | Splits each bank into `exams/` + `examKeys/` and uploads |
| `app/(app)/exam/[module]/` | Sits the assessment |
| `app/(app)/certificates/` | The learner's own certificates (assessment and completion) |
| `app/(app)/verify/` | Public certificate check |
| `src/lib/progress/awards.ts` | XP, levels and badge thresholds — all derived |
| `app/(app)/leaderboard/` | Opt-in public standings |

## Engagement layer (Phase 4)

**XP and badges are derived, never stored.** `awards.ts` is a pure function of
the progress already in the store. A stored XP total is exactly the number that
has to be recomputed the moment the formula changes, and a second copy of the
truth can only drift from the first. Weights say what the site values: a page
is 10, a quiz 5, a certificate 250. Levels widen — level *n* costs 100·n — so
later levels stay meaningful without a cap.

**Notes** live per page in the same store, synced to `users/{uid}/stats/notes`
for accounts and local-only for guests, like everything else. An emptied note
is deleted rather than stored blank. On merge the local copy wins, because
there is no per-note timestamp and losing a note is worse than keeping a stale
one.

**The leaderboard is opt-in and server-computed.** `publishLeaderboard`
recalculates pages and certificates from Firestore rather than believing the
request — a self-reported ranking is worthless, since being wrong is the whole
problem on that particular surface. Quiz scores are deliberately excluded from
the public number: their answers ship in the page source, so they are not
evidence. `leaderboard/{uid}` is world-readable and client-unwritable; opting
out deletes the row rather than hiding it.

**Digests** run weekly via `sendDigests`, and only for people who opted in
*and* are within five pages of a certificate — a reminder, not a newsletter.
Delivery goes through the Firebase "Trigger Email from Firestore" extension:
the function writes to `mail/`, the extension sends. That keeps SMTP
credentials out of this repo entirely, and without the extension installed the
documents simply pile up unsent — a visible failure rather than a silent one.
`mail/` is closed to every client, since those documents hold subscribers'
addresses.

## Assessments and certificates (Phase 3)

The rule that shapes all of it: **a client may report what it has read, but
never what it has earned.** Page completions stay self-reported — they are the
learner's notes to themselves. Exam answers and certificates are not, so they
live in collections no client can read or write and are only ever touched by
the Admin SDK in `firebase/functions/index.js`.

`scripts/seed-exams.mjs` splits every `src/data/exams/*.yaml` in two:

```
exams/{module}      title, pass mark, questions WITHOUT answers   (account-readable)
examKeys/{module}   answer indexes + explanations                 (readable by nobody)
attempts/{uid}_{m}  graded result                                 (owner get, function write)
certificates/{id}   issued certificate                            (public get, no list)
config/modules      page counts, the certificate denominator      (public read)
```

The split is the point. `exams/*` must be readable to render the paper; if the
answers travelled with it, "server-graded" would mean nothing — anyone could
read the key from the network tab.

**What `gradeExam` returns depends on the result.** Passed: every explanation,
since there is nothing left to game. Failed: only which questions were wrong.
Explanations routinely state the correct answer, and handing them over would
make the retry a formality. Attempts are rate-limited to one per ten minutes;
without that, a 12-question paper is a brute force.

**`issueCertificate` trusts nothing but the module name.** Completion comes
from `users/{uid}/progress/{module}`, the denominator from `config/modules`,
the score from `attempts/` — which only the grader can write. It needs 90% of
the pages and a pass, refuses to issue twice for the same module, and requires
a verified email address, because a certificate names one.

**`certificates` allows `get` but not `list`.** Public `get` is what makes a
certificate checkable by whoever is handed the id; denying `list` stops the
collection being swept for holders' names and addresses. A learner's own
certificates are indexed under `users/{uid}/stats/certificates` instead.

Certificate ids use an alphabet without I, O, 0 or 1 — they get read aloud and
retyped.

### Running it

```bash
npm run exams:check    # validate the YAML, no credentials needed
npm run exams:seed     # upload (needs GOOGLE_APPLICATION_CREDENTIALS)
npm run firebase:rules
```

Seeding needs a service account key: Firebase console → Project settings →
Service accounts → Generate new private key. Keep it outside the repo.

### The server runs on Vercel, not Firebase

Cloud Functions need the Blaze plan. This project is on Spark, so the four
endpoints live in `app/api/*/route.ts` as **Vercel Functions**, which the site's existing
free hosting runs at no cost. The trust boundary is unchanged: exam keys,
graded attempts and certificates are still only touched by code the browser
cannot run.

What moved:

- `httpsCallable` became `callApi()` in `src/lib/firebase/client.ts`, which
  POSTs to `/api/<endpoint>` with a Firebase ID token in the Authorization
  header. `requireVerifiedCaller` verifies that token against Google's public
  keys, so a forged or expired one fails at the door.
- The weekly digest is a Vercel Cron entry in `vercel.json` rather than a
  scheduled function. It is guarded by `CRON_SECRET`; without that check the
  endpoint would be an open trigger for anyone who found the URL.
- `firebase.json` no longer deploys functions, and the superseded
  `firebase/functions/` copy has been removed.

**Deploying.** Vercel builds from git on every push. `npm run deploy` runs
`vercel deploy --prod` by hand, and `npm run deploy:preview` makes a preview.
There is no static-only path any more: the site needs its route handlers.

Environment variables on the Vercel project:

| Variable | Purpose |
| --- | --- |
| `FIREBASE_SERVICE_ACCOUNT` | Service account JSON, on one line. Full admin credentials — `.gitignore` blocks the usual filenames, but it belongs in Vercel's env, never the repo. |
| `CRON_SECRET` | Any long random string. Guards `/api/send-digest`. |

### Still open

- **The digest needs the "Trigger Email from Firestore" extension** installed
  before any mail actually leaves.
- **Vercel's Hobby tier is for non-commercial use.** This site carries a
  "Buy me a coffee" link; if that ever becomes real revenue, the plan needs a
  look.
- **Eleven of twelve modules have no exam.** `tutorials.yaml` is the reference
  bank; the format and the guidance for writing more are at the top of it.
- Certificates print via the browser's own "Save as PDF" (print CSS, one per
  sheet) rather than a rendered image — selectable, scalable, no canvas
  pipeline to maintain.

## Progress tracking (Phase 2)

Local first, cloud second. Every interaction writes to `localStorage` and
repaints immediately; a 1.5 s debounce then flushes to Firestore. Marking a
page complete cannot wait on an auth round trip plus a database write, and a
reader with no account still gets working progress tracking.

**Page ids** are derived from `window.location.pathname` at runtime, with the
locale prefix stripped — finishing a page in Hindi and in English is one
achievement, not two. They are never baked in at build time, so they cannot
drift from the routes Starlight emits.

**Firestore shape**, all under `users/{uid}` and covered by the existing
owner-only rule:

```
progress/{moduleSlug}   { completed: string[], updatedAt }
stats/summary           { streak, longest, lastActive, totalCompleted }
stats/bookmarks         { pages: string[] }
stats/quizzes           { [encodedKey]: { correct, total, at } }
```

One document per module, not per page. A reader can finish hundreds of pages;
a document each would make the dashboard hundreds of reads. Twelve module
documents cover the whole curriculum. Completions use `arrayUnion` /
`arrayRemove` so two devices editing different pages of one module merge
instead of overwriting each other.

**Merging** is always a union, never a replacement — picking a winner by
timestamp would silently discard one device's work. Un-marking is the one
thing a union cannot express, so it only sticks once flushed.

**Guests never reach Firestore.** Progress for a signed-out reader is complete
in localStorage and stays on the device. Only a real account — Google, GitHub
or email+password — syncs. The client checks this from the Firebase-free auth
hint, so a page where the answer is "no" loads no SDK at all, and
`firestore.rules` refuses anonymous providers outright.

**Counts**: the sidebar's "n/m" badges count the links in each group from the
DOM — the group already lists exactly its own pages. Only the dashboard needs
`progress-manifest.json`, which carries counts and labels but no page ids:
counts survive slug drift, a second slug implementation would not.

**Quiz scores** are recorded for the learner's own dashboard only. `Quiz.astro`
puts the answer index in the page source, so they can never gate a
certificate — Phase 3's exams are graded server-side for that reason.

## The auth hint

The header must show either "Sign in" or an avatar, on every page. Asking
Firebase would mean shipping the Auth SDK everywhere, including to the
majority of readers who never sign in.

Instead `syncHint()` mirrors the signed-in identity into `localStorage` on
every auth-state change, and `UserMenu.astro` renders straight from it —
synchronously, no network, no SDK, no layout shift. When a hint exists the
menu then loads the SDK at idle to confirm it, which is what catches a session
that expired or was revoked elsewhere.

**The hint is display state, never authorisation.** Editing it by hand changes
the avatar in the corner and nothing else; every read and write is still
checked by Firestore rules on the server.

## Guests vs. accounts

Nothing in the site creates an anonymous Auth record. A guest gets the full
feature set — mark complete, bookmarks, streaks, quiz scores, dashboard —
entirely out of localStorage. Signing in is what turns that into a synced
account, and the sign-in handlers call `resync()` so everything collected
beforehand is merged in rather than lost.

Two independent enforcement points, deliberately:

- `local.ts` refuses to queue or flush a write without a real account, from
  the auth hint alone (no SDK, no network);
- `firestore.rules` rejects `sign_in_provider == 'anonymous'`, which is the
  half that cannot be edited by whoever is holding the browser.

`signedInAccount()` never triggers a sign-in — it resolves whatever session
already exists — so content pages can call it safely. The anonymous-linking
branches in `auth.ts` are kept for anyone still carrying an anonymous session
from an earlier build: signing in links it rather than stranding it.

## Email verification

Verification is not a wall. Every tutorial is readable without it. It gates
certificate issuance only (Phase 3), so a certificate names an address its
holder controls.

## Account enumeration

`/reset-password` reports the same "a reset link is on its way" whether or not
the address has an account, and `AUTH_ERROR_KEYS` maps
`auth/user-not-found` and `auth/wrong-password` to a single "email and
password do not match" message. Distinguishing them would give anyone a free
way to test which email addresses are registered.

## Firebase console setup

The web config is public by design, so the checked-in defaults work as-is.
These console steps are not in the repo and must be done by hand:

1. **Authentication → Sign-in method**: enable Google and Email/Password.
   *(done)* The Anonymous provider is not required — guests are handled
   entirely in localStorage and never authenticate.
2. **GitHub**: create a GitHub OAuth app and paste its client ID and secret.
   Until the secret is set, the provider returns
   `auth/operation-not-allowed`, which surfaces as "that sign-in method is
   not available yet". Set `PUBLIC_AUTH_GITHUB=off` to hide the button
   entirely in the meantime.
3. **Authentication → Settings → Authorized domains**: add
   `pythoncentralhub.live` (and any Vercel preview domain you sign in from).
   OAuth fails on an unlisted domain.
4. **Account linking**: "one account per email address" is what makes Google
   sign-in link to an existing password account instead of erroring.
5. Deploy the rules: `npm run firebase:rules`.

## Deferred

- **Localised auth pages.** Content pages localise automatically; custom
  `src/pages/*.astro` do not. The five auth pages are English-only at the site
  root for now — their strings are already translated in all five
  dictionaries, so the remaining work is routing.
- **Subcollection cleanup on delete.** `deleteAccount()` removes the profile
  document and the Auth user. Firestore does not cascade, so the per-user
  subcollections added in Phase 2 will need a Cloud Function or the
  "Delete User Data" extension.
- **Custom email templates** for verification and password reset.

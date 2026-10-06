# Python Central Hub

Free, self-paced courses in programming, data, machine learning and the
mathematics behind it, with code you run in the page.

Python Central Hub is a learning platform built on Next.js. Each top-level folder of
`src/content/docs` is a course, and each MDX file in it is a lesson. Lessons
carry runnable Python (Pyodide, in the browser), graded exercises, quizzes,
diagrams and interactive visualisations. Learners can track progress without an
account; with one, progress syncs, and they can sit final assessments for a
verifiable certificate.

## Courses

| Code | Course |
|---|---|
| PY 101 | Python Programming |
| PY 150 | Python Projects |
| PY 180 | Automation and Scripting |
| DATA 110 | Data Analytics with Python |
| MATH 120 | Mathematics for Machine Learning |
| ML 210 | Machine Learning |
| DL 310 | Deep Learning |
| CS 220 | Data Structures and Algorithms |
| WEB 201 | Web Development with Flask |
| SE 230 | Software Testing and Quality |

The catalogue, course codes and learning paths live in `lib/courses.data.mjs`.

## Stack

- **Next.js 16** (App Router) with **Fumadocs** for the content pipeline
- **Firebase** Authentication and Cloud Firestore for accounts and progress
- **Vercel** for hosting, route handlers (`app/api/*`), cron, analytics
- **Pyodide** in a Web Worker for exercises and the in-page Python playground
- Tailwind CSS v4 and shadcn/ui components

## Getting started

```bash
npm install
npm run dev            # http://localhost:3000
```

The site runs without any environment variables: Firebase falls back to the
public web config, and the server routes answer "not configured" until their
secrets are set. See `.env.example` for every variable.

## Useful scripts

| Script | What it does |
|---|---|
| `npm run build` | Full production build (about 12 minutes, 1,200+ pages) |
| `npm run typecheck` | TypeScript |
| `npm run content:check` | Compiles every lesson and checks every exercise's props |
| `npm run routes:verify` | Proves no indexed lesson URL has moved |
| `npm run i18n:check` | UI strings complete in every locale |
| `npm run smoke -- --base http://localhost:3000` | Renders a sample of pages and every app route |
| `npm test` | Unit tests |
| `npm run test:rules` | Firestore rules tests (needs the Firebase emulator) |
| `npm run test:e2e` | Playwright end-to-end tests |
| `npm run deploy` | `vercel deploy --prod` |

## Writing content

- One lesson per `.mdx` file. The file and folder names are the URL, and
  1,100+ lesson URLs are indexed: never rename them. The slug rule is in
  `lib/slug.mjs`.
- Components (`DataCampExercise`, `Quiz`, `Figure`, `FileCode`, …) are
  available in every lesson without an import (`mdx-components.tsx`).
- Exercises run on Pyodide (Python 3.13, numpy, pandas, scipy, scikit-learn,
  matplotlib). They are graded with `test_output_contains(...)` and
  `success_msg(...)` only.
- Run `npm run content:check` before pushing; CI runs it too.

## Deploying

Vercel builds every push. Before the first production launch, work through
[`docs/launch-checklist.md`](docs/launch-checklist.md): environment variables,
Firestore rules, email, analytics and the domain.

## Contributing

Issues and pull requests are welcome. For lesson fixes, edit the MDX file and
open a pull request; `npm run content:check` must pass.

## License

MIT. See [LICENSE](LICENSE). Contact:
[ravikishan63392@gmail.com](mailto:ravikishan63392@gmail.com).

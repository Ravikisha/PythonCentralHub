---
name: new-tutorial
description: Scaffold a new Python Central Hub tutorial .mdx page with correct frontmatter, DataCampExercise blocks, and site conventions. Use when the user wants to add a new tutorial/doc page under src/content/docs.
---

# New Tutorial Page

Scaffold a Starlight `.mdx` tutorial that matches this repo's conventions.

## Location & filename

- Pages live under `src/content/docs/<Module>/<Phase N - ...>/<Title>.mdx`.
- **Windows-invalid filenames:** NEVER put `" : * ? < > | \ /` in a filename. The repo already has ~11 files with literal `"` that Git cannot check out on Windows — do not create more. Use plain ASCII, spaces allowed.
- A phase folder usually has an overview `.mdx` named after the folder itself.

## Frontmatter (required)

```yaml
---
title: <Human Title>
description: <one sentence, SEO-worthy>
sidebar:
  order: <int — controls sidebar position within module>
---
```

Section-overview pages use only `title` + `description` (+ order). Landing (`index.mdx`) is special — do not mimic it.

## Page Spec v2 — body structure

Concept pages follow this order. Scale each section to the topic; skip a section only when it genuinely does not apply.

```
## What you'll learn          5-7 bullets
## Intuition                  analogy + mermaid concept diagram
## The math                   KaTeX, stepped derivation, every symbol defined
## Worked example by hand     6-8 row table, arithmetic shown, verified vs library
## See it move                p5 sketch with controls
## From scratch               numpy implementation (~25 lines)
## With scikit-learn          idiomatic API, same result as the hand example
## On real data               dataset -> fit -> <Figure> plot
## Reading the plot           what the reader should take from the figure
<AlgorithmCard />             assumptions, cost, hyperparams, use/avoid
## Pitfalls                   3-5 :::caution / :::danger asides, real failure modes
## Compare                    table against sibling approaches
<Quiz />                      4 MCQ, hidden answers + explanations
## 🧪 Try It Yourself         5 DataCampExercise blocks, easy -> hard
## Recap                      bullet summary
## Next                       link to the following page
```

Variants:

- **Phase overview pages** — skip math/code. Phase map (mermaid), prerequisites, outcomes, time estimate, page table. Target ~900 words.
- **MLOps / engineering pages** — `## The architecture` replaces `## The math`; a runnable end-to-end walkthrough replaces the hand example.
- **Capstone pages** — framing, EDA, baseline, iteration, error analysis, deployment; checkpoint exercises between stages.

## Imports

All imports go directly under the frontmatter, before the first heading. The `../` depth is
the number of folders from `src/content/docs` to the file, plus one:

```mdx
import DataCampExercise from "../../../../components/DataCampExercise.astro";
import AlgorithmCard from "../../../../components/AlgorithmCard.astro";
import Figure from "../../../../components/Figure.astro";
import Quiz from "../../../../components/Quiz.astro";
```

Count the depth — do not guess.

## Math

`remark-math` + `rehype-katex` are configured site-wide. Use real math, never backticked
pseudo-math:

- inline: `$\hat{y} = wx + b$`
- display: `$$ ... $$` on its own lines

Define every symbol on first use. Braces inside math survive the `remarkEscapeBraces` plugin
because `remarkMath` runs first — but braces in *prose* are escaped, so keep `{}` out of
ordinary text.

Math does **not** render inside JSX props (Quiz options, AlgorithmCard fields). Write those in
words.

## Internal links

Starlight slugifies the file path by lowercasing and replacing each space with `-`. A folder
named `Phase 03 - Supervised Learning - Regression` becomes
`phase-03---supervised-learning---regression` (three hyphens), and `&` disappears leaving two.
Build links from the real slug, with a trailing slash:

```md
[Multiple Linear Regression](/machine-learning/phase-03---supervised-learning---regression/multiple-linear-regression/)
```

## Figures

- **mermaid** — structure, flow, taxonomy.
- **p5** — interactive intuition. Fence with `title` / `desc` / `height`; canvas background
  `background(13, 17, 23)`, blue `(75, 139, 190)`, amber `(255, 211, 67)`, red `(232, 110, 110)`.
- **matplotlib** — real data plots. Add a module under `scripts/figures/<group>/<page-slug>.py`
  exporting `FIGURES`, run `npm run figures`, then embed:

  ```mdx
  <Figure
    src="/images/<group>/<page-slug>/<figure-name>"
    alt="<what the plot shows>"
    title="<header text>"
    caption="<what to take away>"
  />
  ```

  Pass `src` without the `-dark.svg` / `-light.svg` suffix; the component swaps them with the theme.
- **tables** — confusion matrices, iteration traces, comparison matrices.

## Code samples

Fenced with a filename and line numbers:

````
```python title="example.py" showLineNumbers{1}
````

Put the expected output in a trailing comment on the `print` line. Every number a page claims
must come from actually running the code.

## Interactive exercises (DataCampExercise)

Five blocks under `## 🧪 Try It Yourself`, graded easy to hard, each with its own `###` heading.

```mdx
<DataCampExercise
  lang="python"
  hint={`Use \`fn()\` to ...`}
  code={`# Task: <title>
import os
files = os.___( "." )   # blank for learner to fill
print("Found files:", len(files) > 0)`}
  solution={`import os
files = os.listdir(".")
print("Found files:", len(files) > 0)`}
  sct={`test_output_contains("Found files: True")
success_msg("Nice!")`}
  height={125}
/>
```

Rules: backticks inside template literals must be escaped `` \` ``. `code` has a fill-in-the-blank
(`___`), `solution` is complete, `sct` uses DataCamp SCT helpers (`test_output_contains`,
`success_msg`, `test_function`). Tune `height` to content (~120-190). Avoid box-drawing characters
in the expected-output comment; plain `--` rules render more reliably.

## Verify

- `node scripts/mdxcheck.mjs "src/content/docs/<Module>"` — seconds, catches JSX / brace /
  template-literal errors. The full build takes ~30 minutes; do not use it as an inner loop.
- Bump/renumber `sidebar.order` if inserting between existing pages, and keep it unique.
- Confirm the import `../` depth by counting, not guessing.
- Confirm every `<Figure src>` has committed SVGs under `public/`.
- Do not run `git add -A` (would stage deletion of the Windows-invalid files). Do not commit.

The full design rationale lives in `docs/superpowers/specs/2026-08-02-ml-content-upgrade-design.md`.
See project memory `design-system` and `repo-gotchas`.

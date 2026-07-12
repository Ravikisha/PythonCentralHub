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

## Body structure

1. `## What you'll learn` — bullet list.
2. Concept prose (Poppins body). Headings are `##` / `###`.
3. Code samples use fenced blocks with a filename + line numbers:
   ````
   ```python title="example.py" showLineNumbers{1}
   ````
4. Signature motif: use the `>>>` REPL prompt as a structural marker where a shell interaction is shown.

## Interactive exercises (DataCampExercise)

Append a `## 🧪 Try It Yourself` section with 3 `<DataCampExercise>` blocks.

**Import path is depth-relative.** Count folders from `src/content/docs` to the file, then:
`import DataCampExercise from "<../ × depth>components/DataCampExercise.astro";`
(e.g. a file 3 folders deep → `../../../../components/DataCampExercise.astro`).

Each block:

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

Rules: backticks inside template literals must be escaped `\``. `code` has a fill-in-the-blank (`___`), `solution` is complete, `sct` uses DataCamp SCT helpers (`test_output_contains`, `success_msg`, `test_function`). Tune `height` to content (~120–160).

## Verify

- Bump/renumber `sidebar.order` if inserting between existing pages.
- Confirm the import `../` depth by counting, not guessing.
- Do not run `git add -A` (would stage deletion of the Windows-invalid files). Do not commit.

See project memory `design-system` and `repo-gotchas`.

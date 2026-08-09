# Projects section — progress log

Regenerate with `python scripts/projects_audit.py --progress`. One row per run; the plan is in
`docs/projects_upgrade_plan.md`.

| Date | Pages | At target | Stale snippets | Page ahead | Page behind | Pages that run | Figures | Quizzes | Exercises | mermaid | p5 | Dup orders |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-08 baseline (wave 0) | 203 | 0 | 570 | — | — | 60 | 0 | 0 | 0 | 41 | 10 | 16 |
| 2026-08-08 wave 1+2 | 203 | 0 | 336 | 42 | 26 | 61 | 0 | 0 | 0 | 41 | 10 | 0 |
| 2026-08-08 wave 3a | 203 | 0 | 330 | 41 | 27 | 67 | 31 | 0 | 0 | 41 | 10 | 0 |
| 2026-08-08 wave 3b | 203 | 0 | 330 | 41 | 27 | 67 | 31 | 2 | 2 | 62 | 10 | 0 |
| 2026-08-08 wave 3c | 203 | 0 | 330 | 41 | 27 | 71 | 31 | 5 | 5 | 64 | 10 | 0 |
| 2026-08-08 wave 3d | 203 | 0 | 330 | 41 | 27 | 74 | 31 | 5 | 5 | 64 | 10 | 0 |
| 2026-08-08 wave 3e | 203 | 0 | 330 | 40 | 28 | 80 | 34 | 5 | 5 | 64 | 10 | 0 |
| 2026-08-09 wave 4 | 203 | 0 | 330 | 40 | 28 | 80 | 34 | 8 | 8 | 193 | 10 | 0 |

Notes on the columns, so later rows stay comparable:

- **Stale snippets** — walkthrough code blocks defining a function or class that
  the shipped `.py` does not contain. Wave 1 rewrote the 117 templated Advance
  walkthroughs from their source files, taking 570 to 336.
- **Page ahead / page behind** — the direction the remaining drift runs in.
  *Page ahead* means the page teaches more than the file implements, so the fix
  is to write the code; *page behind* means the file has moved on. Wave 0 did
  not separate these, hence the dashes.
- **Dup orders** — `sidebar.order` collisions **within one folder**, which is
  the only kind Starlight can act on. The wave-0 row said 86 because the audit
  counted collisions across folders too; the real figure at baseline was 16,
  and that is what is shown here.
- **Artifacts** are not a column but are worth recording: the wave-0 run
  produced 1 artifact from 60 successful runs because every matplotlib project
  called `plt.show()`. After wave 2 the same run produces **31**, and wave 3a
  captured 30 of them into `public/images/projects/` for the pages to show.

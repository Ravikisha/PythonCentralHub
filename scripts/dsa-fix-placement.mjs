/**
 * scripts/dsa-fix-placement.mjs — relocate sections that landed in the wrong place.
 *
 * Two placement bugs from the batch scripts, both worth understanding because the
 * audit could not catch either — it checks that a section *exists*, not that it is
 * somewhere a reader would find it.
 *
 * 1. **The cue landed after Recap.** The batch inserts sections in array order and
 *    anchors each one to the first heading that already exists. "## The cue" was
 *    processed first, before its preferred anchor ("## Visual intuition") had been
 *    inserted by a later section — so it fell through to append-at-end. Eight
 *    pages ended with a recognition guide sitting past the summary.
 *
 * 2. **A ladder was skipped by a substring collision.** The idempotency guard is
 *    `text.includes(heading)`, and "## Practice" is a substring of the existing
 *    "## Practice -- real LeetCode problems". The section was treated as already
 *    present and never inserted.
 *
 * The lesson for future batches: anchor on headings that exist in the *original*
 * page, and match headings on a whole line rather than as a substring.
 *
 * Run: node scripts/dsa-fix-placement.mjs
 */
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

const DOCS = "src/content/docs/DSA with Python";

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

/** Start offsets of every level-2 heading, plus a sentinel at end-of-text. */
function headingOffsets(text) {
  return [...text.matchAll(/^## .*$/gm)].map((m) => ({ at: m.index, line: m[0] }));
}

/** Extract the block starting at `heading` and running to the next level-2 heading. */
function cutSection(text, heading) {
  const start = text.indexOf(`\n${heading}\n`);
  if (start === -1) return null;
  const from = start + 1;
  const rest = text.slice(from + heading.length);
  const next = rest.match(/^## /m);
  const to = next ? from + heading.length + next.index : text.length;
  return { body: text.slice(from, to).replace(/\s*$/, "\n"), rest: text.slice(0, from) + text.slice(to) };
}

let cuesMoved = 0;
let laddersFixed = 0;

for (const file of walk(DOCS)) {
  const name = relative(DOCS, file).split(sep).pop();
  let text = readFileSync(file, "utf8");
  let touched = false;

  // ── 1. Relocate a cue that sits after Recap ──────────────────────────────
  const cueAt = text.indexOf("\n## The cue\n");
  const recapAt = text.indexOf("\n## Recap");
  if (cueAt !== -1 && recapAt !== -1 && cueAt > recapAt) {
    const cut = cutSection(text, "## The cue");
    if (cut) {
      const headings = headingOffsets(cut.rest);
      // Place it after "What you'll learn" if present — that is the reader's
      // natural entry point — otherwise before the second heading.
      const learnIdx = headings.findIndex((h) => /What you'?ll learn/i.test(h.line));
      const target =
        learnIdx !== -1 && headings[learnIdx + 1]
          ? headings[learnIdx + 1].at
          : (headings[1]?.at ?? headings[0]?.at ?? cut.rest.length);

      text = cut.rest.slice(0, target) + cut.body + "\n" + cut.rest.slice(target);
      cuesMoved += 1;
      touched = true;
      console.log(`moved cue   ${name}`);
    }
  }

  // ── 2. Insert a missing ladder into an existing Practice section ──────────
  if (text.includes("dsa/ProblemLadder.astro") && !/<ProblemLadder\b/.test(text)) {
    const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    const pattern = fm?.[1].match(/^patterns:\r?\n\s+-\s+(.+?)\s*$/m)?.[1];
    const practice = text.match(/^## Practice.*$/m);
    if (pattern && practice) {
      const at = practice.index + practice[0].length;
      const block =
        `\n\nProblems from the database that exercise this material. Progress is saved\n` +
        `in this browser.\n\n<ProblemLadder pattern="${pattern}" />\n`;
      text = text.slice(0, at) + block + text.slice(at);
      laddersFixed += 1;
      touched = true;
      console.log(`added ladder ${name}`);
    }
  }

  if (touched) {
    writeFileSync(file, text.replace(/\n{4,}/g, "\n\n\n"), "utf8");
  }
}

console.log(`\n${cuesMoved} cue(s) relocated, ${laddersFixed} ladder(s) inserted.`);

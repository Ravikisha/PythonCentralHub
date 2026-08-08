/**
 * scripts/lint-mermaid.mjs — structural checks on every ```mermaid block.
 *
 * WHY THIS EXISTS
 * ---------------
 * Same failure mode as the p5 sketches: nothing on the build path parses a
 * mermaid block. It goes to the browser, and a syntax error renders as an error
 * box or a blank space that only a human scrolling the page will notice. There
 * are 585 of them on this site.
 *
 * WHAT IT DELIBERATELY DOES NOT CHECK — read this before adding a rule
 * --------------------------------------------------------------------
 * The first version of this script reported 548 problems. Every one was the
 * checker being wrong, not the corpus:
 *
 *   · "odd number of quotes on this line" — 208 hits. Mermaid node labels may
 *     span several lines: A["1. Why interpretability\nadfit against …"]. The
 *     opening quote is on one line and the closing quote on the next, so
 *     per-line counting is meaningless. Quotes are now counted per BLOCK.
 *
 *   · "unbalanced curly brackets" — 90 hits, all `class Item {` in a
 *     classDiagram, where the body legitimately spans lines. Bracket checking
 *     is now skipped for class/state/ER diagrams entirely.
 *
 *   · "no title on the fence" — 250 hits. That is a convention the DSA section
 *     follows and the Deep Learning / ML sections do not. A style difference is
 *     not a defect; it is now counted and reported, never failed on.
 *
 * The lesson, for the second time on this project: a rule that fires on a large
 * fraction of a working corpus is almost certainly the broken thing. Verify one
 * finding by hand before believing the report.
 *
 * Run: npm run viz:mermaid
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = process.argv[2] ?? "src/content/docs";

const TYPES = [
  "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram-v2",
  "stateDiagram", "erDiagram", "journey", "gantt", "pie", "gitGraph",
  "mindmap", "timeline", "quadrantChart", "requirementDiagram", "C4Context",
  "block-beta", "sankey-beta", "xychart-beta",
];

/** Diagram types whose bodies use braces structurally — skip bracket checks. */
const BRACE_BODIED = new Set(["classDiagram", "stateDiagram-v2", "stateDiagram", "erDiagram"]);

/** In a sequenceDiagram these open a region closed by `end`. */
const BLOCK_OPENERS = /^(alt|opt|loop|par|critical|rect|box)\b/;

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

export function checkBlock(code, meta = "") {
  const problems = [];
  const lines = code.split("\n").filter((l) => l.trim() !== "");
  if (lines.length === 0) return ["the block is empty"];

  const first = lines[0].trim();
  const type = TYPES.find((t) => first.startsWith(t));
  if (!type) return [`first line "${first.slice(0, 40)}" is not a known diagram type`];

  if ((type === "flowchart" || type === "graph") &&
      !/^(flowchart|graph)\s+(TD|TB|BT|LR|RL)\b/.test(first)) {
    problems.push(`"${first}" has no direction (expected TD, TB, BT, LR or RL)`);
  }

  // balanced subgraph / alt / end
  let subgraphs = 0;
  let seqBlocks = 0;
  for (const raw of lines.slice(1)) {
    const l = raw.trim();
    if (l.startsWith("%%")) continue;
    if (/^subgraph\b/.test(l)) subgraphs += 1;
    else if (type === "sequenceDiagram" && BLOCK_OPENERS.test(l)) seqBlocks += 1;
    else if (l === "end") {
      if (subgraphs > 0) subgraphs -= 1;
      else if (seqBlocks > 0) seqBlocks -= 1;
      else problems.push('an "end" with nothing open');
    }
  }
  if (subgraphs > 0) problems.push(`${subgraphs} unclosed subgraph(s)`);
  if (seqBlocks > 0) problems.push(`${seqBlocks} unclosed alt/opt/loop/par block(s)`);

  // quotes counted across the WHOLE block, because labels may span lines
  const body = lines.filter((l) => !l.trim().startsWith("%%")).join("\n");
  if ((body.match(/"/g) ?? []).length % 2 !== 0) {
    problems.push("odd number of double quotes across the block — a label is unclosed");
  }

  // brackets, block-wide, and only where braces are not structural
  if (!BRACE_BODIED.has(type)) {
    const bare = body.replace(/"[^"]*"/gs, "");
    for (const [open, close, name] of [["[", "]", "square"], ["(", ")", "round"]]) {
      const a = bare.split(open).length - 1;
      const b = bare.split(close).length - 1;
      if (a !== b) problems.push(`unbalanced ${name} brackets across the block (${a} vs ${b})`);
    }
  }
  return problems;
}

// Only sweep the tree when run directly; checkBlock is imported by the self-test.
const RUN_DIRECTLY = import.meta.url === pathToFileURL(process.argv[1] ?? "").href;

const problems = [];
let blocks = 0;
let files = 0;
let untitled = 0;

if (RUN_DIRECTLY) {

for (const file of walk(ROOT)) {
  const text = readFileSync(file, "utf8").replace(/\r\n/g, "\n");
  if (!text.includes("```mermaid")) continue;
  files += 1;
  const rel = relative(process.cwd(), file);

  const re = /^```mermaid([^\n]*)\n([\s\S]*?)^```/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    blocks += 1;
    const line = text.slice(0, m.index).split("\n").length;
    if (!/title="/.test(m[1])) untitled += 1;
    for (const p of checkBlock(m[2], m[1])) problems.push(`${rel}:${line} — ${p}`);
  }
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`mermaid lint — ${blocks} diagrams across ${files} pages under ${ROOT}`);
console.log(bar);
console.log(`\n  ${untitled} diagram(s) have no title= on the fence (a style difference, not a defect)`);

if (problems.length === 0) {
  console.log("\nOK — every diagram is structurally well-formed.\n");
  process.exit(0);
}
console.log(`\n${problems.length} problem(s):`);
for (const p of problems) console.log(`  · ${p}`);
console.log();
process.exit(1);
}

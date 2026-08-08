/**
 * scripts/gen-project-diagrams.mjs — derive a call-flow diagram for each project
 * page from the project's ACTUAL source, and (with --write) insert it.
 *
 * Input:  scratch/project-analysis.json  (python3 scripts/analyse_projects.py)
 * Usage:  node scripts/gen-project-diagrams.mjs           # report only
 *         node scripts/gen-project-diagrams.mjs --write   # insert into pages
 *
 * WHY THERE IS A REFUSAL RULE
 * ---------------------------
 * A call graph is worth drawing only when it says something a reader would not
 * get from skimming the file. A three-function script whose graph reads
 * "main calls a, b, c" is a picture of the table of contents. Emitting one on all
 * 185 project pages would close the coverage gap on paper and teach nothing --
 * which is worse than leaving them alone, because it hides the gap.
 *
 * So a source qualifies only if it has >= 4 definitions, >= 3 resolved call
 * edges, and more than one distinct caller. Everything else is reported with its
 * reason and left untouched.
 *
 * The edges themselves come from a deliberately conservative resolver -- see the
 * docstring in scripts/analyse_projects.py. It only claims a call it can justify,
 * because an invented edge is worse than a missing one.
 *
 * ON TRUNCATION
 * -------------
 * Some sources are large (one has 127 edges). A 127-edge flowchart is a hairball,
 * so the diagram keeps at most MAX_EDGES and says on the page that it is showing
 * a subset -- silent truncation would misrepresent the program. It keeps the
 * edges from the RAREST callers, not the busiest: the entry point calls nearly
 * everything, so ranking by degree would preserve exactly the uninformative
 * arrows and drop the structural ones.
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const WRITE = process.argv.includes("--write");
const REPORT = process.argv.find((a) => a.endsWith(".json")) ?? "scratch/project-analysis.json";

const MIN_DEFS = 4;
const MIN_EDGES = 3;
const MAX_EDGES = 22;

let data;
try {
  data = JSON.parse(readFileSync(REPORT, "utf8"));
} catch (err) {
  console.error(`Cannot read ${REPORT}: ${err.message}`);
  console.error("Run: python3 scripts/analyse_projects.py");
  process.exit(1);
}

// ── map every project page to the source it shows ──────────────────────────
const PAGES = "src/content/docs/projects";
function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const f = join(dir, e);
    if (statSync(f).isDirectory()) out.push(...walk(f));
    else if (e.endsWith(".mdx")) out.push(f);
  }
  return out;
}
const pageBySrc = new Map();
for (const page of walk(PAGES)) {
  const text = readFileSync(page, "utf8");
  const m = /<FileCode\s+file="([^"]+)"/.exec(text);
  if (m) pageBySrc.set(m[1].replace(/\\/g, "/"), page);
}

// ── mermaid ────────────────────────────────────────────────────────────────
const short = (n) => n.replace(/^__main__$/, "start").split(".").pop();
const idOf = (() => {
  const seen = new Map();
  let i = 0;
  return (n) => {
    if (!seen.has(n)) seen.set(n, `n${i++}`);
    return seen.get(n);
  };
})();

function buildMermaid(row) {
  let edges = row.edges;
  let trimmed = false;
  if (edges.length > MAX_EDGES) {
    // Keep STRUCTURAL edges, not the busiest ones. The entry point calls almost
    // everything, so ranking by degree keeps exactly the arrows that carry no
    // information ("main calls each feature") and drops the ones that do
    // ("every mutator calls save_data"). Rank by how rare the caller is instead.
    const outDeg = {};
    for (const [a] of edges) outDeg[a] = (outDeg[a] ?? 0) + 1;
    edges = [...edges].sort((x, y) => outDeg[x[0]] - outDeg[y[0]]).slice(0, MAX_EDGES);
    trimmed = true;
  }

  // group by owning class so the picture matches the file's structure
  const owner = (n) => (n === "__main__" ? null : n.includes(".") ? n.split(".")[0] : null);
  const nodes = new Set(edges.flat());
  const groups = new Map();
  for (const n of nodes) {
    const g = owner(n) ?? "";
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(n);
  }

  const lines = ["flowchart TD"];
  for (const [g, members] of [...groups].sort((a, b) => a[0].localeCompare(b[0]))) {
    if (g) {
      lines.push(`  subgraph ${g}`);
      for (const n of members.sort()) lines.push(`    ${idOf(n)}["${short(n)}()"]`);
      lines.push("  end");
    } else {
      for (const n of members.sort()) {
        lines.push(n === "__main__" ? `  ${idOf(n)}(["script start"])` : `  ${idOf(n)}["${short(n)}()"]`);
      }
    }
  }
  for (const [a, b] of edges) lines.push(`  ${idOf(a)} --> ${idOf(b)}`);

  const title = trimmed
    ? `call flow (${MAX_EDGES} of ${row.edges.length} calls)`
    : "how the pieces call each other";
  const desc = trimmed
    ? `Derived from ${row.src} by parsing it. The file has ${row.defs} definitions and ${row.edges.length} internal calls, too many to draw legibly, so this shows ${MAX_EDGES} of them, chosen to keep the structural calls rather than the entry point fanning out. Only calls the parser could resolve with certainty are drawn -- library calls are left out.`
    : `Derived from ${row.src} by parsing it, not by hand. Arrows are calls between the file's own functions and methods; library calls are left out, and only calls the parser could resolve with certainty are shown.`;

  return "```mermaid title=\"" + title + "\" desc=\"" + desc + "\"\n" + lines.join("\n") + "\n```";
}

// ── qualify ────────────────────────────────────────────────────────────────
const qualify = [];
const skip = [];
for (const row of data) {
  const callers = new Set(row.edges.map((e) => e[0]));
  if (!pageBySrc.has(row.src)) skip.push([row, "no project page references this source"]);
  else if (row.defs < MIN_DEFS) skip.push([row, `only ${row.defs} definitions`]);
  else if (row.edges.length < MIN_EDGES) skip.push([row, `only ${row.edges.length} resolved call edges`]);
  else if (callers.size < 2) skip.push([row, "a single caller — the graph is a flat list"]);
  else {
    // Refuse star graphs. If one caller owns most of the edges the picture is
    // "main calls every feature", which is the table of contents with arrows.
    // What earns a diagram is structure BETWEEN the parts.
    const out = {};
    for (const [a] of row.edges) out[a] = (out[a] ?? 0) + 1;
    const busiest = Math.max(...Object.values(out));
    const structural = row.edges.length - busiest;
    if (busiest / row.edges.length >= 0.7 || structural < 3) {
      skip.push([row, "a star — one caller owns most of the edges, so the graph adds nothing"]);
    } else qualify.push(row);
  }
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`project diagrams — ${data.length} sources, ${pageBySrc.size} pages reference one`);
console.log(bar);
console.log(`\n  ${qualify.length} qualify`);
console.log(`  ${skip.length} do not`);
const reasons = {};
for (const [, why] of skip) {
  const k = why.replace(/\d+/g, "N");
  reasons[k] = (reasons[k] ?? 0) + 1;
}
console.log("\nwhy skipped:");
for (const [why, n] of Object.entries(reasons).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(4)}  ${why}`);
}

// --preview <substring> prints the diagram that WOULD be written, so it can be
// read before 80 pages are touched.
const previewArg = process.argv.indexOf("--preview");
if (previewArg !== -1) {
  const needle = process.argv[previewArg + 1] ?? "";
  const row = qualify.find((r) => r.src.includes(needle));
  if (!row) {
    console.log(`\nno qualifying source matching "${needle}"\n`);
    process.exit(1);
  }
  console.log(`\n--- ${row.src} -> ${pageBySrc.get(row.src)}\n`);
  console.log(buildMermaid(row));
  console.log();
  process.exit(0);
}

if (!WRITE) {
  console.log("\n(report only — pass --write to insert, --preview <name> to see one)\n");
  process.exit(0);
}

// ── insert ─────────────────────────────────────────────────────────────────
let wrote = 0;
let already = 0;
const noAnchor = [];
for (const row of qualify) {
  const page = pageBySrc.get(row.src);
  let text = readFileSync(page, "utf8");
  if (text.includes("```mermaid")) {
    already += 1;
    continue;
  }
  const nl = text.includes("\r\n") ? "\r\n" : "\n";
  let body = text.replace(/\r\n/g, "\n");

  // Before "Write the Code" is the right spot: the reader has the premise and is
  // about to meet the file, so the shape of it is useful right there.
  const anchor = ["## Write the Code", "## Getting Started", "## Prerequisites"].find((a) =>
    body.includes(a),
  );
  if (!anchor) {
    noAnchor.push(page);
    continue;
  }
  body = body.replace(anchor, buildMermaid(row) + "\n\n" + anchor);
  writeFileSync(page, body.replace(/\n/g, nl), "utf8");
  wrote += 1;
}

console.log(`\ninserted into ${wrote} page(s)`);
if (already) console.log(`${already} already had a mermaid block — left alone`);
if (noAnchor.length) {
  console.log(`${noAnchor.length} had no usable anchor:`);
  for (const p of noAnchor.slice(0, 5)) console.log(`  · ${p}`);
}
console.log();

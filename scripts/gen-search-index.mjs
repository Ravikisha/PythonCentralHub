// Build the search index the ⌘K dialog loads.
//
//   node scripts/gen-search-index.mjs
//
// Titles, descriptions and URLs for every English page, written to
// public/search-index.json.
//
// The browser index is deliberately not full-text: at 1192 pages the title,
// description and heading index is a few hundred KB, fetched once on first
// ⌘K, and finds the page people are usually looking for.
//
// The lesson text goes to .search/fulltext.json instead, which never reaches
// the browser: app/api/search/ reads it on the server (next.config.ts traces
// it into that function) and answers the "In lesson text" part of the dialog.
import { readdirSync, statSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, relative } from "node:path";
import { routeFor, slugify as segmentSlug } from "../lib/slug.mjs";
import { courseInfo } from "../lib/courses.data.mjs";

const DOCS = "src/content/docs";
const OUT = "public/search-index.json";
const FULLTEXT = ".search/fulltext.json";
/** Characters of text kept per lesson; the long ones are mostly code. */
const FULLTEXT_MAX = 30000;
const LOCALE_DIRS = new Set(["es", "hi", "ja", "zh-cn"]);

/** Pages that exist as routes but are not somewhere a reader wants to land. */
const NOT_A_RESULT = new Set(["/", "/404/", "/not-found/"]);

/** Module label from the top-level directory name, as authored. */
/** The course a page belongs to, by its course title where it has one. */
function moduleLabel(relPath) {
  const first = relPath.split(/[\\/]/)[0];
  if (first.endsWith(".mdx") || first.endsWith(".md")) return "";
  return courseInfo(segmentSlug(first))?.title ?? first;
}

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) {
      if (dir === DOCS && LOCALE_DIRS.has(entry)) continue;
      walk(p, out);
    } else if (/\.mdx?$/.test(entry)) {
      out.push(p);
    }
  }
  return out;
}

/** Pull `title` and `description` out of the frontmatter without a YAML parse. */
function frontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};

  const out = {};
  for (const line of match[1].split(/\r?\n/)) {
    const m = line.match(/^(title|description):\s*(.*)$/);
    if (!m) continue;
    out[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

/**
 * A lesson's section headings, the words a learner is most likely to type.
 *
 * Titles alone missed most searches: "list comprehension" lives in a heading
 * inside the Lists lesson, not in any title. Full text would make the index
 * several megabytes; the headings are a few words each and carry most of the
 * signal. Code fences are skipped so a `# comment` line is not read as one.
 */
const BOILERPLATE =
  /^(what you('|’)ll learn|the cue|conclusion|summary|key takeaways|introduction|overview|try it\b.*|exercise\s*\d.*|recall card|pitfalls|common (pitfalls|mistakes)|interview follow-ups|self-check|practice.*|dry run|further reading|next steps?|references|quiz|visual intuition|visualize it|prerequisites|output|example\s*\d*)$/i;

function headings(source) {
  const body = source.replace(/```[\s\S]*?```/g, "");
  const out = [];
  for (const m of body.matchAll(/^#{2,3}\s+(.+?)\s*#*\s*$/gm)) {
    const text = m[1]
      .replace(/`([^`]*)`/g, "$1")
      .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/[*_]/g, "")
      .replace(/\{#[^}]*\}/g, "")
      .trim();
    // Headings every lesson has say nothing about this one, and would make a
    // search for "summary" match 800 pages.
    if (BOILERPLATE.test(text)) continue;
    if (text && !out.includes(text)) out.push(text);
    if (out.length >= 14) break;
  }
  return out.join(" | ");
}

/**
 * A lesson as plain text: prose, inline code and code blocks, without
 * frontmatter, imports, component props or Markdown syntax.
 */
function plainText(source) {
  return source
    .replace(/^---\r?\n[\s\S]*?\r?\n---/, "")
    .replace(/^(import|export) .*$/gm, "")
    // Exercises carry their code in props; the starter and solution would
    // match every search for a function they happen to call.
    .replace(/<DataCampExercise\b[\s\S]*?\/>/g, "")
    .replace(/```[^\n]*\n/g, "\n")
    .replace(/```/g, "")
    .replace(/<\/?[A-Za-z][^>]*>/g, " ")
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[*_`>|]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, FULLTEXT_MAX);
}

const entries = [];
const fulltext = [];

for (const file of walk(DOCS)) {
  const rel = relative(DOCS, file).split("\\").join("/");
  const source = readFileSync(file, "utf8");
  const { title, description } = frontmatter(source);
  if (!title) continue;

  const url = routeFor(rel);
  if (NOT_A_RESULT.has(url)) continue;

  entries.push({
    t: title,
    d: description ?? "",
    u: url,
    m: moduleLabel(rel),
    h: headings(source),
  });
  fulltext.push({ u: url, t: title, m: moduleLabel(rel), x: plainText(source) });
}

entries.sort((a, b) => a.u.localeCompare(b.u));

mkdirSync("public", { recursive: true });
writeFileSync(OUT, JSON.stringify(entries));

const bytes = Buffer.byteLength(JSON.stringify(entries));
console.log(`${OUT}: ${entries.length} page(s), ${(bytes / 1024).toFixed(0)} KB`);

mkdirSync(".search", { recursive: true });
const full = JSON.stringify(fulltext.sort((a, b) => a.u.localeCompare(b.u)));
writeFileSync(FULLTEXT, full);
console.log(
  `${FULLTEXT}: ${fulltext.length} page(s), ${(Buffer.byteLength(full) / 1048576).toFixed(1)} MB`,
);

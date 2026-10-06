// Prove the Next.js build reproduces every URL the Astro site serves.
//
//   node scripts/verify-routes.mjs
//
// 1116 of these URLs are indexed. A slug that changes silently is a ranking
// lost, and there is no way to notice by looking at the site -- the page still
// renders, just at a different address. So the check is mechanical and the
// result is a release gate: zero missing routes, or the migration is not done.
//
// The baseline in migration/routes-baseline-en.txt was extracted from the
// Astro build's sitemap before any code moved. It is the only artefact that
// can say what the URLs *were*, so it is committed rather than regenerated.
//
// The slug rule itself lives in lib/slug.mjs, which the Next app also imports,
// so this verifies the rule in production rather than a lookalike.
import { readdirSync, statSync, readFileSync, existsSync } from "node:fs";
import { join, relative } from "node:path";
// The same module the Next app uses, so this verifies the rule in production
// rather than a lookalike.
import { routeFor } from "../lib/slug.mjs";

const DOCS = "src/content/docs";
const BASELINE = "migration/routes-baseline-en.txt";
const LOCALE_DIRS = new Set(["es", "hi", "ja", "zh-cn"]);

/** Every English content file, as a repo-relative path. */
function contentFiles(dir = DOCS, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) {
      if (dir === DOCS && LOCALE_DIRS.has(entry)) continue; // translations
      contentFiles(p, out);
    } else if (/\.mdx?$/.test(entry)) {
      out.push(relative(DOCS, p).split("\\").join("/"));
    }
  }
  return out;
}

if (!existsSync(BASELINE)) {
  console.error(`${BASELINE} is missing — it is the only record of the old URLs.`);
  process.exit(1);
}

const baseline = new Set(
  readFileSync(BASELINE, "utf8")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
);

/**
 * Routes the app serves itself rather than from a content file: the learner
 * platform pages and Astro's special pages. They are in the baseline because
 * the old site built them, but no .mdx produces them, so comparing them
 * against the content tree would report permanent false failures.
 *
 * They still have to exist in the new app -- phase 5 of the migration plan
 * ports them -- they are simply verified by their own route files, not here.
 */
const APP_ROUTES = new Set([
  // The landing page. src/content/docs/index.mdx still exists (the locales
  // reference it), but app/page.tsx serves "/" — see that file for why the
  // Astro splash was not transliterated.
  "/",
  "/dashboard/",
  "/certificates/",
  "/leaderboard/",
  "/login/",
  "/signup/",
  "/profile/",
  "/reset-password/",
  "/verify-email/",
  "/verify/",
  "/exam/tutorials/",
  "/404/",
  "/not-found/",
]);

const generated = new Map();
for (const file of contentFiles()) generated.set(routeFor(file), file);

const missing = [...baseline]
  .filter((r) => !generated.has(r) && !APP_ROUTES.has(r))
  .sort();
const extra = [...generated.keys()]
  .filter((r) => !baseline.has(r) && !APP_ROUTES.has(r))
  .sort();

console.log(`baseline:  ${baseline.size} route(s)`);
console.log(`generated: ${generated.size} route(s)`);
console.log(`missing:   ${missing.length}`);
console.log(`extra:     ${extra.length}`);

if (missing.length) {
  console.log("\n--- in the live site but NOT generated (these lose rankings) ---");
  for (const r of missing.slice(0, 40)) console.log(`  ${r}`);
  if (missing.length > 40) console.log(`  ...and ${missing.length - 40} more`);
}

if (extra.length) {
  console.log("\n--- generated but not in the live site ---");
  for (const r of extra.slice(0, 40)) console.log(`  ${r}  <- ${generated.get(r)}`);
  if (extra.length > 40) console.log(`  ...and ${extra.length - 40} more`);
}

console.log(missing.length === 0 ? "\nOK — every live route is reproduced." : "\nFAIL");
process.exit(missing.length === 0 ? 0 : 1);

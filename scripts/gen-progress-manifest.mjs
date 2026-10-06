// Generate the progress manifest: how many pages each module contains.
//
//   node scripts/gen-progress-manifest.mjs
//
// The dashboard needs a denominator ("18 of 240 pages") and a human label for
// every module. Neither can be derived in the browser: the site is static, and
// a page only ever knows about itself. Counting at build time and shipping a
// single small JSON file is cheaper than any runtime alternative -- the
// obvious one, reading every page id out of Firestore, would cost a query per
// module per visit for data that never changes between deploys.
//
// Deliberately NOT included: the list of page ids in each module. Page ids are
// derived in the browser from `window.location.pathname`, which is always
// right by construction, whereas a build-time copy of them would be a second
// slug implementation to keep in sync with Starlight's. Counts and labels are
// robust to slug drift; a page list would not be.
//
// Output: public/progress-manifest.json (served as a static asset, fetched
// once by the dashboard).
import {
  readdirSync,
  statSync,
  writeFileSync,
  mkdirSync,
  existsSync,
} from "node:fs";
import { join, relative } from "node:path";
import { routeFor, slugify as segmentSlug } from "../lib/slug.mjs";
import { courseInfo } from "../lib/courses.data.mjs";

const DOCS = "src/content/docs";
const EXAMS = "src/data/exams";
const OUT = "public/progress-manifest.json";

/** Locale directories hold translations of the same pages, not new ones. */
const LOCALE_DIRS = new Set(["es", "hi", "ja", "zh-cn"]);

/** Directories that are not learning modules. */
const SKIP_DIRS = new Set(["src"]);

const PAGE_RE = /\.mdx?$/;

/**
 * A module folder's URL segment -- "DSA with Python" -> "dsa-with-python".
 * The shared rule in lib/slug.mjs, not a local copy: a second copy of the
 * slug rule is exactly what verify-routes exists to stop drifting.
 */
function slugify(name) {
  return segmentSlug(name);
}

/**
 * Where a module opens.
 *
 * A module is a folder of phases, so `/dsa-with-python/` is not a page: every
 * surface that offered it as a link -- the landing page, the dashboard -- was
 * sending readers to a 404. The first page in walk order is the honest
 * default, and three modules name their own opening page because the file that
 * sorts first is not where anyone should begin.
 */
const OPENS_AT = {
  tutorials: "/tutorials/introduction/",
  projects: "/projects/beginners/asciiartgenerator/",
  guides: "/guides/home/",
};

function firstPage(dir) {
  for (const entry of readdirSync(dir).sort()) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) {
      const found = firstPage(p);
      if (found) return found;
    } else if (PAGE_RE.test(entry)) {
      return p;
    }
  }
  return null;
}

/** Count .md/.mdx files under a directory, recursively. */
function countPages(dir) {
  let n = 0;
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) n += countPages(p);
    else if (PAGE_RE.test(entry)) n += 1;
  }
  return n;
}

const modules = [];

for (const entry of readdirSync(DOCS)) {
  const p = join(DOCS, entry);
  if (!statSync(p).isDirectory()) continue; // index.mdx, policy.mdx, 404.mdx
  if (LOCALE_DIRS.has(entry) || SKIP_DIRS.has(entry)) continue;

  const count = countPages(p);
  if (!count) continue;

  const slug = slugify(entry);
  // `hasExam` saves the dashboard a probe per module: without it, offering a
  // "sit the assessment" link would mean testing twelve URLs to find the one
  // or two that exist.
  const hasExam =
    existsSync(join(EXAMS, `${slug}.yaml`)) ||
    existsSync(join(EXAMS, `${slug}.yml`));

  // The directory name is the label, except that two of them ("tutorials",
  // "projects") are lowercase on disk while the sidebar shows them capitalised.
  // The dashboard sits beside that sidebar, so they match there too.
  const label =
    /^[a-z]/.test(entry) && !entry.includes(" ")
      ? entry.charAt(0).toUpperCase() + entry.slice(1)
      : entry;

  const opening = firstPage(p);
  const entryUrl =
    OPENS_AT[slug] ??
    (opening
      ? routeFor(relative(DOCS, opening).split("\\").join("/"))
      : `/${slug}/`);

  // A catalogued course is labelled by its course title everywhere the
  // manifest reaches -- the dashboard, certificates, the verifier -- and its
  // home is its course page rather than its first lesson.
  const course = courseInfo(slug);
  modules.push({
    slug,
    label: course?.title ?? label,
    count,
    hasExam,
    entry: entryUrl,
    ...(course ? { course: true, href: `/courses/${slug}/`, code: course.code } : {}),
  });
}

/**
 * The learning path, mirroring MODULE_ORDER in lib/order.ts.
 *
 * The manifest used to be sorted by page count, which put Projects first on
 * the landing page and the dashboard while the sidebar opened with Guides.
 * Three surfaces, three different answers to "where do I start".
 */
const PATH = [
  "guides",
  "tutorials",
  "flask-tutorials",
  "python-automation-and-scripting",
  "data-analytics",
  "mathematics-for-machine-learning",
  "machine-learning",
  "deep-learning",
  "dsa-with-python",
  "software-testing-and-quality",
  "projects",
  "reference",
];

const rank = (slug) => {
  const i = PATH.indexOf(slug);
  return i === -1 ? PATH.length : i;
};

modules.sort((a, b) => rank(a.slug) - rank(b.slug) || b.count - a.count);

mkdirSync("public", { recursive: true });
writeFileSync(
  OUT,
  JSON.stringify({ generatedAt: new Date().toISOString(), modules }, null, 2) +
    "\n",
);

const total = modules.reduce((sum, m) => sum + m.count, 0);
console.log(`${OUT}: ${modules.length} module(s), ${total} page(s)`);
for (const m of modules) {
  console.log(
    `  ${String(m.count).padStart(5)}  ${m.slug}${m.hasExam ? "  (exam)" : ""}`,
  );
}

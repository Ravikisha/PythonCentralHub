// Request a spread of real routes against a running dev server.
//
//   node scripts/smoke-routes.mjs [--base http://localhost:3180] [--n 40]
//
// `verify-routes.mjs` proves the URLs are generated; this proves they render.
// The two are different failures: a slug can be right while the page throws on
// a component, a code fence, or a plugin that has not been ported.
//
// Samples evenly across the baseline so every module is represented rather
// than whichever pages happen to sort first.
import { readFileSync } from "node:fs";

const args = process.argv.slice(2);
const base = args.includes("--base") ? args[args.indexOf("--base") + 1] : "http://localhost:3180";
const n = args.includes("--n") ? Number(args[args.indexOf("--n") + 1]) : 40;

const routes = readFileSync("migration/routes-baseline-en.txt", "utf8")
  .split("\n")
  .map((l) => l.trim())
  .filter(Boolean);

const step = Math.max(1, Math.floor(routes.length / n));
const sample = routes.filter((_, i) => i % step === 0).slice(0, n);

/**
 * The pages that are not content: the landing page, the learner platform and
 * the machine-readable files. Always checked, never sampled -- there are only
 * a dozen of them and each one is a different failure from a content page.
 *
 * They are checked for a marker too. Every one of these renders a shell that
 * fills in from the browser, so "HTTP 200" alone would pass even if the page
 * came back empty.
 */
const APP_ROUTES = [
  ["/", /class="catalog__grid"/],
  ["/courses/", /class="catalog__grid"/],
  ["/courses/tutorials/", /class="syllabus"/],
  ["/login/", /pch-auth__providers/],
  ["/signup/", /pch-auth__providers/],
  ["/reset-password/", /pch-reset-email|pch-auth__submit/],
  ["/verify-email/", /pch-auth__intro/],
  ["/profile/", /app__loading|pch-profile__meta/],
  ["/dashboard/", /pch-dash|app__loading/],
  ["/certificates/", /pch-certs/],
  ["/leaderboard/", /assess__facts/],
  ["/verify/", /verify__form/],
  ["/exam/tutorials/", /assess__course/],
  ["/saved/", /app__loading|saved__/],
  ["/admin/", /app__loading|admin__/],
  ["/robots.txt", /Sitemap:/],
  ["/sitemap.xml", /<urlset/],
  ["/rss.xml", /<rss/],
];

/** Markers that tell us a ported component actually rendered. */
const MARKERS = {
  exercise: /class="ex"/,
  quiz: /pch-quiz/,
  figure: /pch-figure/,
  mermaid: /mermaid-diagram/,
  p5: /pch-p5|data-p5-stage/,
  ladder: /pch-pl__|pch-pt|problem-table/,
  /* The header the playground and the fullscreen control mount into. Its
     absence is how "Run stopped working" looked the last time. */
  codebar: /class="code__bar"/,
};

const failures = [];
const seen = Object.fromEntries(Object.keys(MARKERS).map((k) => [k, 0]));
let ok = 0;

for (const route of sample) {
  let status = 0;
  let body = "";
  try {
    const res = await fetch(base + route, { signal: AbortSignal.timeout(120_000) });
    status = res.status;
    body = await res.text();
  } catch (err) {
    failures.push([route, `fetch failed: ${err.message}`]);
    continue;
  }

  if (status !== 200) {
    failures.push([route, `HTTP ${status}`]);
    continue;
  }
  ok++;
  for (const [name, re] of Object.entries(MARKERS)) if (re.test(body)) seen[name]++;
}

console.log(`${ok}/${sample.length} content page(s) rendered`);

/* ---- the application's own pages ---- */
let appOk = 0;
for (const [route, marker] of APP_ROUTES) {
  try {
    const res = await fetch(base + route, { signal: AbortSignal.timeout(120_000) });
    const body = await res.text();

    if (res.status !== 200) failures.push([route, `HTTP ${res.status}`]);
    else if (!marker.test(body)) failures.push([route, "rendered without its content"]);
    else appOk++;
  } catch (err) {
    failures.push([route, `fetch failed: ${err.message}`]);
  }
}
console.log(`${appOk}/${APP_ROUTES.length} app route(s) rendered`);
console.log("\ncomponents seen across the sample:");
for (const [name, count] of Object.entries(seen)) {
  console.log(`  ${name.padEnd(10)} ${count} page(s)`);
}

if (failures.length) {
  console.log(`\n${failures.length} failure(s):`);
  for (const [route, why] of failures) console.log(`  ${why.padEnd(16)} ${route}`);
}

process.exit(failures.length ? 1 : 0);

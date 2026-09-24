// Verify the site's own UI strings are complete in every locale.
//
// Starlight translates its own chrome, but every `Astro.locals.t('pch.…')`
// call in `src/components/` resolves against `src/content/i18n/<lang>.json`.
// i18next has no "missing key" failure mode: an absent key renders as the key
// itself, so a typo or a language that never got a new string ships a live
// page reading `pch.feedbackEmailPlaceholder` instead of a placeholder.
//
// This script makes that a build-time failure instead:
//
//   node scripts/check-i18n.mjs
//
// Checks, in order:
//   1. every locale in src/i18n/locales.ts has a dictionary file
//   2. every `t('pch.…')` key used in src/ is declared in en.json
//   3. every key in en.json is actually used somewhere (catches dead strings)
//   4. every non-English dictionary has every en.json key, non-empty
//   5. no dictionary carries a key en.json does not have (catches renames)
//
// Rule 4 is a warning, not an error: i18next falls back to English for a
// missing key, so a half-translated language still renders. It is listed so
// adding a language tells you exactly what is left to write.
import { readdirSync, statSync, readFileSync } from "node:fs";
import { join } from "node:path";

const DICT_DIR = "src/content/i18n";
const SRC_DIR = "src";
const DEFAULT_LANG = "en";

/** Langs declared in src/i18n/locales.ts, read without a TS toolchain. */
function declaredLangs() {
  const src = readFileSync("src/i18n/locales.ts", "utf8");
  const block = src.slice(src.indexOf("export const LOCALES"));
  return [...block.matchAll(/lang:\s*'([^']+)'/g)].map((m) => m[1]);
}

/** Every source file that could hold a `t('pch.…')` call. */
function walk(dir) {
  let out = [];
  for (const e of readdirSync(dir)) {
    if (e === "content") continue; // .mdx prose has no t() calls
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out = out.concat(walk(p));
    else if (/\.(astro|ts|tsx|js|jsx)$/.test(e)) out.push(p);
  }
  return out;
}

const langs = declaredLangs();
const dicts = new Map();
for (const f of readdirSync(DICT_DIR).filter((f) => f.endsWith(".json"))) {
  dicts.set(f.replace(/\.json$/, ""), JSON.parse(readFileSync(join(DICT_DIR, f), "utf8")));
}

const used = new Set();
for (const f of walk(SRC_DIR)) {
  const src = readFileSync(f, "utf8");
  for (const m of src.matchAll(/\bt\(\s*['"`](pch\.[A-Za-z0-9_]+)['"`]/g)) used.add(m[1]);
}

const en = dicts.get(DEFAULT_LANG);
const errors = [];
const warnings = [];

if (!en) errors.push(`${DICT_DIR}/${DEFAULT_LANG}.json is missing`);

for (const lang of langs) {
  if (!dicts.has(lang)) errors.push(`locale "${lang}" is declared in src/i18n/locales.ts but ${DICT_DIR}/${lang}.json does not exist`);
}
for (const lang of dicts.keys()) {
  if (!langs.includes(lang)) warnings.push(`${DICT_DIR}/${lang}.json has no matching locale in src/i18n/locales.ts — it is never loaded`);
}

if (en) {
  const enKeys = Object.keys(en);
  for (const key of [...used].sort()) {
    if (!(key in en)) errors.push(`${key} is used in src/ but missing from ${DEFAULT_LANG}.json — it would render as the raw key`);
  }
  for (const key of enKeys) {
    if (!used.has(key)) warnings.push(`${key} is declared in ${DEFAULT_LANG}.json but never used`);
  }

  for (const [lang, dict] of dicts) {
    if (lang === DEFAULT_LANG) continue;
    const missing = enKeys.filter((k) => !(k in dict));
    const empty = enKeys.filter((k) => k in dict && !String(dict[k]).trim());
    const extra = Object.keys(dict).filter((k) => !(k in en));
    if (missing.length) warnings.push(`${lang}.json is missing ${missing.length} key(s) (falls back to English): ${missing.join(", ")}`);
    if (empty.length) errors.push(`${lang}.json has empty value(s): ${empty.join(", ")}`);
    if (extra.length) errors.push(`${lang}.json has key(s) not in ${DEFAULT_LANG}.json (renamed or stale): ${extra.join(", ")}`);
  }
}

for (const w of warnings) console.log(`WARN  ${w}`);
for (const e of errors) console.log(`FAIL  ${e}`);

console.log(
  `\n${used.size} key(s) used in src/, ${en ? Object.keys(en).length : 0} declared in ${DEFAULT_LANG}.json, ` +
    `${dicts.size} dictionar(ies) for ${langs.length} locale(s): ${langs.join(", ")}`
);
console.log(errors.length ? `${errors.length} error(s)` : "i18n OK");
process.exit(errors.length ? 1 : 0);

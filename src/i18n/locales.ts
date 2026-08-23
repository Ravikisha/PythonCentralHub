/**
 * Single source of truth for the site's locales.
 *
 * `astro.config.mjs` builds Starlight's `locales` map from this, and the
 * translation tooling reads the same list, so adding a language means editing
 * one array instead of hunting through the config.
 *
 * The object KEY is the URL path segment (`/zh-cn/...`); `lang` is the BCP-47
 * tag that goes on `<html lang>`, drives Pagefind's per-language index, and
 * names the dictionary file in `src/content/i18n/<lang>.json`.
 *
 * English is deliberately the `root` locale, NOT `/en/`. The site has 1116
 * pages already indexed by search engines at unprefixed paths; giving English
 * a prefix would move every one of them.
 */
export const LOCALES = {
	root: { label: 'English', lang: 'en' },
	'zh-cn': { label: '简体中文', lang: 'zh-CN' },
	hi: { label: 'हिन्दी', lang: 'hi' },
	es: { label: 'Español', lang: 'es' },
	ja: { label: '日本語', lang: 'ja' },
} as const;

/** BCP-47 tag of the locale served at the site root. */
export const DEFAULT_LANG = LOCALES.root.lang;

/** Every non-default language tag, i.e. the ones that need translating. */
export const TRANSLATION_LANGS = Object.values(LOCALES)
	.map((l) => l.lang)
	.filter((lang) => lang !== DEFAULT_LANG);

/**
 * URL path segment for each non-default language, keyed by BCP-47 tag.
 * Translated content lives at `src/content/docs/<segment>/...`.
 */
export const LANG_TO_SEGMENT: Record<string, string> = Object.fromEntries(
	Object.entries(LOCALES)
		.filter(([segment]) => segment !== 'root')
		.map(([segment, { lang }]) => [lang, segment])
);

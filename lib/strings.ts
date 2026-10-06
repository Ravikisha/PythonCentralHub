import en from "@/src/content/i18n/en.json";

/**
 * UI strings.
 *
 * The Astro build resolved these through Starlight's i18n middleware, one
 * `t()` per component. The Next site launches English-only, so the table is
 * imported directly and the call site stays the same shape -- when the other
 * four locales come back this is the one function that has to change, not the
 * hundred places that call it.
 *
 * An unknown key returns itself. A missing translation should look wrong on
 * the page, not crash the render.
 */
const table = en as Record<string, string>;

export function t(key: string): string {
  return table[key] ?? key;
}

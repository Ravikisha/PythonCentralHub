/**
 * Turning a URL into a stable progress key.
 *
 * Page ids are derived from `window.location.pathname` rather than baked in
 * at build time, so they cannot drift from the routes Starlight actually
 * emits. Two rules make them stable:
 *
 *  - the locale prefix is stripped, so finishing a page in Hindi and finishing
 *    it in English are the same achievement rather than two;
 *  - the trailing slash and any hash/query are dropped.
 *
 * "/hi/tutorials/python-lists/list-slicing/" -> "tutorials/python-lists/list-slicing"
 */

/** URL prefixes that select a translation, not a different page. */
const LOCALE_SEGMENTS = new Set(["zh-cn", "hi", "es", "ja"]);

/**
 * First segments that belong to the application rather than to the
 * curriculum. Pages under these never count towards progress.
 */
const RESERVED = new Set([
  "login",
  "signup",
  "profile",
  "dashboard",
  "reset-password",
  "verify-email",
  "certificates",
  "policy",
  "not-found",
  "404",
  "rss.xml",
]);

/** Locale segment of a path, or "en" for the unprefixed root locale. */
export function localeOf(pathname: string): string {
  const seg = pathname.split("/").filter(Boolean)[0] ?? "";
  return LOCALE_SEGMENTS.has(seg) ? seg : "en";
}

/**
 * Stable id for a content page, or null when the path is not one.
 *
 * Returns null for the home page, the auth pages and any single-segment
 * route, so callers can use it directly as "should this page show progress
 * controls?".
 */
export function pageIdOf(pathname: string): string | null {
  const parts = pathname.split("/").filter(Boolean);
  if (parts.length && LOCALE_SEGMENTS.has(parts[0])) parts.shift();
  if (parts.length < 2) return null; // "/", "/login", "/tutorials"
  if (RESERVED.has(parts[0])) return null;
  return parts.join("/").toLowerCase();
}

/** Module slug a page id belongs to, e.g. "tutorials". */
export function moduleOf(pageId: string): string {
  return pageId.split("/")[0];
}

/**
 * Firestore document ids cannot contain "/", so page ids are escaped before
 * being used as map keys. "__" is not produced by slugification, which makes
 * the mapping reversible.
 */
export function encodeId(pageId: string): string {
  return pageId.replace(/\//g, "__");
}

export function decodeId(key: string): string {
  return key.replace(/__/g, "/");
}

/** Today in the visitor's own timezone, as YYYY-MM-DD. */
export function today(date = new Date()): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/** Whole days between two YYYY-MM-DD strings, ignoring clock time. */
export function daysBetween(from: string, to: string): number {
  const a = Date.parse(`${from}T00:00:00`);
  const b = Date.parse(`${to}T00:00:00`);
  if (Number.isNaN(a) || Number.isNaN(b)) return Number.NaN;
  return Math.round((b - a) / 86_400_000);
}

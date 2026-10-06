/**
 * Canonical site facts, in one place.
 *
 * The site answers on more than one address -- python-central-hub.vercel.app
 * and pythoncentralhub.live -- and either works. One of them is the *primary*
 * address: what the sitemap, the feed, link previews, emails and every
 * canonical link point at, so search engines index one copy rather than two.
 *
 * The primary address is, in order:
 *
 *  1. NEXT_PUBLIC_SITE_URL, if set -- an explicit choice always wins.
 *  2. The project's production domain on Vercel (VERCEL_PROJECT_PRODUCTION_URL,
 *     which Vercel sets at build time). It is the custom domain once one is
 *     attached and marked primary in Vercel, and the .vercel.app address until
 *     then -- so adding pythoncentralhub.live in Vercel moves every canonical
 *     link to it on the next deploy, with no code change.
 *  3. python-central-hub.vercel.app, for local builds.
 *
 * Lesson paths are the same on every address, so the 1,116 URLs indexed under
 * pythoncentralhub.live keep working on it once its DNS points at Vercel.
 */
function primaryUrl(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL;
  if (explicit) return explicit.replace(/\/$/, "");
  const vercel =
    process.env.VERCEL_PROJECT_PRODUCTION_URL ??
    process.env.NEXT_PUBLIC_VERCEL_PROJECT_PRODUCTION_URL;
  if (vercel) return `https://${vercel.replace(/^https?:\/\//, "").replace(/\/$/, "")}`;
  return "https://python-central-hub.vercel.app";
}

export const SITE_URL = primaryUrl();

export const SITE_NAME = "Python Central Hub";

/** The name as one lower-case word, for file names and identifiers. */
export const SITE_SLUG = "pythoncentralhub";

export const SITE_DESCRIPTION =
  "Free, self-paced courses in programming, data, machine learning and the mathematics behind it, with code you run in the page.";

/**
 * A page url as the site actually serves it.
 *
 * `next.config.ts` sets `trailingSlash: true`, so `/tutorials/boolean` redirects
 * to `/tutorials/boolean/`. Fumadocs' `page.url` has no trailing slash, and a
 * canonical link or sitemap entry pointing at the redirecting form asks a
 * crawler to take an extra hop to reach the page it just read.
 */
export function canonical(url: string) {
  const path = url.endsWith("/") ? url : `${url}/`;
  return `${SITE_URL}${path}`;
}

/**
 * The public source repository. Lesson "view source" links and the footer use
 * it. Renaming the GitHub repository? Run `node scripts/rename-repo.mjs
 * <owner>/<new-name>`, which rewrites this and every lesson link at once
 * (GitHub redirects the old URLs in the meantime, so nothing breaks first).
 */
export const REPO_URL = "https://github.com/Ravikisha/PythonCentralHub";

/** Link-preview image for a page, drawn by app/api/og. */
export function ogImage(title: string, course?: string): string {
  const params = new URLSearchParams({ title });
  if (course) params.set("course", course);
  return `/api/og/?${params}`;
}

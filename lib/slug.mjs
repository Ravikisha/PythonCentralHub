/**
 * Starlight's file-path-to-URL rule, reproduced.
 *
 * Plain ESM with no side effects on purpose: both the Next app (via
 * `lib/source.ts`) and `scripts/verify-routes.mjs` import it, so the rule that
 * is verified is the rule that is used. A second copy would drift from this
 * one the first time an edge case appeared -- and the edge cases here are the
 * whole problem.
 *
 * Derived from the 1195 URLs the Astro site actually served, then verified
 * against every one of them. The surprises are load-bearing:
 *
 *   - each whitespace character becomes one dash, and runs are NOT collapsed,
 *     so "Phase 01 - Neural Network Foundations" is
 *     "phase-01---neural-network-foundations" (space, literal dash, space)
 *   - punctuation is dropped *after* that substitution, leaving the dashes
 *     that surrounded it: "Shortcuts & Magic" -> "shortcuts--magic"
 *   - underscores survive (`pivot_table`), dots do not (`tf.distribute` ->
 *     `tfdistribute`)
 *   - non-ASCII letters survive and are percent-encoded
 *
 * Collapsing repeated dashes looks tidier and breaks 642 indexed URLs.
 */
export function slugify(segment) {
  return segment
    .toLowerCase()
    .replace(/\.mdx?$/, "")
    .replace(/\s/g, "-")
    // Unicode-aware: letters and numbers in any script are kept, everything
    // else (dots, ampersands, brackets, commas) goes.
    .replace(/[^\p{L}\p{N}\-_]/gu, "");
}

/**
 * Slug segments for a content file, relative to the docs root.
 *
 * `index` names its parent directory, exactly as Starlight did.
 */
export function slugsFor(relPath) {
  // Fumadocs reports paths with the host OS separator, so this sees
  // "tutorials\Boolean.mdx" on Windows and "tutorials/Boolean.mdx" on the
  // Linux builders. Splitting on both keeps local and CI slugs identical --
  // and a mismatch there would only show up as 404s in production.
  const segments = relPath.split(/[\\/]/).map(slugify);
  if (segments[segments.length - 1] === "index") segments.pop();
  return segments;
}

/** The URL a content file is served at, with a trailing slash. */
export function routeFor(relPath) {
  // Percent-encode per segment so non-ASCII slugs match the URLs actually
  // served; `-` and `_` are unreserved and pass through untouched.
  const path = slugsFor(relPath).map(encodeURIComponent).join("/");
  return path ? `/${path}/` : "/";
}

import { execFileSync } from "node:child_process";

/**
 * When each content file last changed, from git.
 *
 * Fumadocs can report this per page, but only through `page.data.load()` --
 * which compiles the MDX. The sitemap and the feed want dates for 1183 pages
 * and nothing else about them, and compiling the whole corpus to read 1183
 * timestamps would add minutes to a build that already takes twelve.
 *
 * So: one `git log` over the content directory, walked once and cached. Files
 * are listed newest-commit-first, so the first time a path appears is its last
 * modification.
 *
 * Returns an empty map when git is unavailable or the checkout is shallow --
 * which is the case on Vercel unless VERCEL_DEEP_CLONE is set. A sitemap entry
 * without a date is valid; a wrong date is worse than none.
 */
const CONTENT_DIR = "src/content/docs";

let cache: Map<string, Date> | undefined;

export function lastModifiedMap(): Map<string, Date> {
  if (cache) return cache;

  const map = new Map<string, Date>();

  try {
    const log = execFileSync(
      "git",
      [
        "log",
        "--pretty=format:%ct",
        "--name-only",
        "--diff-filter=AMR",
        "--",
        CONTENT_DIR,
      ],
      { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
    );

    let stamp: number | undefined;
    for (const line of log.split("\n")) {
      const text = line.trim();
      if (text === "") continue;

      if (/^\d+$/.test(text)) {
        stamp = Number(text) * 1000;
        continue;
      }

      if (stamp !== undefined && !map.has(text)) map.set(text, new Date(stamp));
    }
  } catch {
    // No git, or no history: every caller treats an absent date as "unknown".
  }

  cache = map;
  return map;
}

/** `relativePath` is the page's path inside the content directory. */
export function lastModifiedFor(relativePath: string): Date | undefined {
  return lastModifiedMap().get(
    `${CONTENT_DIR}/${relativePath.split("\\").join("/")}`,
  );
}

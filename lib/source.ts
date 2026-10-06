/**
 * The page source: content files in, routes and a navigation tree out.
 *
 * `loader()` is Fumadocs' headless core. It gives us slug generation, the page
 * tree the sidebar renders from, and per-page TOC data -- and nothing visual.
 *
 * URL shape is the part that matters most here. The Astro site serves English
 * unprefixed from the site root (`/tutorials/...`, not `/en/tutorials/...`)
 * because 1116 of those URLs are indexed, so `baseUrl` is "/" and must stay
 * that way. The other four locales are additive and arrive after cutover.
 */
import { loader } from "fumadocs-core/source";
// The slugs plugin has its own subpath export; it is not re-exported from
// `fumadocs-core/source`.
import { slugsPlugin } from "fumadocs-core/source/plugins/slugs";
// In `dynamic` collection mode the generated entry point is `dynamic.ts`, not
// `server.ts` -- it inlines every page's frontmatter (so the tree and slugs are
// known without touching disk) and resolves MDX bodies from their absolute
// paths at request time. `server.ts` only carries the factory in this mode.
import { docs } from "@/.source/dynamic";
import { slugsFor } from "./slug.mjs";
import { inReadingOrder } from "./order";
import type { Node, Root } from "fumadocs-core/page-tree";

export const source = loader({
  baseUrl: "/",
  source: docs.toFumadocsSource(),
  plugins: [
    /**
     * Reproduce Starlight's slugs instead of Fumadocs' defaults.
     *
     * Fumadocs slugifies nothing: `Boolean.mdx` serves at `/tutorials/Boolean`
     * where the live site serves `/tutorials/boolean`. Left alone this
     * silently relocates all 1183 content URLs, 1116 of which are indexed --
     * the pages would still render, just at addresses nobody has linked to.
     *
     * `scripts/verify-routes.mjs` checks this against the pre-migration
     * sitemap and is a release gate.
     */
    slugsPlugin((file) => slugsFor(file.path)),
  ],
});

export type Page = ReturnType<typeof source.getPage>;

/** First page url anywhere under a folder, for folders with no index. */
function firstPageUrl(node: {
  type: string;
  children?: unknown[];
  url?: string;
}): string | undefined {
  if (node.type === "page") return node.url;
  for (const child of (node.children ?? []) as (typeof node)[]) {
    const found = firstPageUrl(child);
    if (found) return found;
  }
  return undefined;
}

/** The locales, which are not part of the English course. */
const LOCALES = ["es", "hi", "ja", "zh-cn"];

/** True for `/es` and `/es/anything`, false for `/estimators`. */
function inLocale(url: string) {
  return LOCALES.some((l) => url === `/${l}` || url.startsWith(`/${l}/`));
}

/**
 * The tree the sidebar and the pager walk.
 *
 * Two things are removed from the raw tree:
 *
 *   - **Loose pages at the top level.** `404`, `not-found` and `policy` are
 *     real routes but they are not course material, and listing them above
 *     "Data Analytics" makes the contents read like a directory listing.
 *   - **The locale roots.** Only four translated files exist; the rest of each
 *     locale is a fallback. Until locales are restored properly they would
 *     appear as four more top-level entries titled in their own language, and
 *     they would also land in prev/next, sending an English reader into
 *     Spanish mid-course.
 */
export function courseTree() {
  const tree = source.getPageTree();

  // Reading order, not filesystem order -- see lib/order.ts. Applied here so
  // the sidebar, the mobile drawer and the pager all agree.
  const ordered = withSectionNames(inReadingOrder(tree));

  return {
    ...ordered,
    children: ordered.children.filter((node) => {
      // Every module is a folder, so a loose page at this level is 404,
      // not-found, policy or the landing page — none of them course material.
      if (node.type === "page") return false;

      if (node.type === "folder") {
        // A locale root's folder holds only its index page, so its own url is
        // `/es` with no trailing slash -- a prefix test alone missed it and
        // the four locale roots kept showing up in the contents.
        const url = node.index?.url ?? firstPageUrl(node) ?? "";
        return !inLocale(url);
      }
      return true;
    }),
  };
}

/**
 * The part of the tree a lesson page's sidebar and drawer need: its own
 * course (or module), with nothing but names, urls and nesting.
 *
 * The whole tree used to be handed to the client on every page -- 1,182
 * pages with ids, refs and descriptions, about 670 KB of the 789 KB HTML of
 * a typical lesson. One course's branch, trimmed, is a few kilobytes.
 * Pages outside any course get an empty tree.
 */
export function slimBranch(url: string): Root {
  const tree = courseTree();
  const branch = tree.children.find(
    (node) => node.type === "folder" && containsUrl(node, url),
  );
  return {
    ...(tree.$id ? { $id: tree.$id } : {}),
    name: tree.name,
    children: branch ? [slim(branch)] : [],
  } as Root;
}

function containsUrl(node: Node, url: string): boolean {
  if (node.type === "page") return node.url === url;
  if (node.type !== "folder") return false;
  return node.index?.url === url || node.children.some((c) => containsUrl(c, url));
}

function slim(node: Node): Node {
  if (node.type === "page") {
    return { type: "page", name: node.name, url: node.url } as Node;
  }
  if (node.type === "folder") {
    return {
      type: "folder",
      name: node.name,
      ...(node.index
        ? { index: { type: "page", name: node.index.name, url: node.index.url } }
        : {}),
      children: node.children.map(slim),
    } as Node;
  }
  return node;
}

/**
 * One way of writing a section's name.
 *
 * The folders were named by four conventions over the years --
 * "Phase-01-Foundations", "Phase 01 - The ML Foundation", "Phase 1 - Flask
 * Fundamentals", "Chapter 00 - Getting Ready" -- and the sidebar showed each
 * as it came. Display only: folder names are URL segments, and 1116 indexed
 * URLs depend on them, so the folders themselves stay as they are.
 */
const RENAMED: Record<string, string> = {
  Advance: "Advanced",
  Beginners: "Beginner",
  intermediate: "Intermediate",
};

export function sectionName(raw: string): string {
  if (RENAMED[raw]) return RENAMED[raw];
  const m = raw.match(/^(phase|chapter)[\s_-]*0*(\d+)[\s:._-]*(.*)$/i);
  if (!m) return raw;
  const kind = m[1].charAt(0).toUpperCase() + m[1].slice(1).toLowerCase();
  let rest = m[3].trim();
  // "Core-Data-Structures" (hyphens as spaces) reads as words; a name that
  // already has spaces keeps its own hyphens ("CI - CD").
  if (!/\s/.test(rest)) rest = rest.replace(/-/g, " ");
  rest = rest.replace(/^CI - CD$/, "CI/CD");
  return rest ? `${kind} ${Number(m[2])}: ${rest}` : `${kind} ${Number(m[2])}`;
}

function withSectionNames<T extends { children: Node[] }>(tree: T): T {
  const rename = (node: Node): Node =>
    node.type === "folder"
      ? {
          ...node,
          name: typeof node.name === "string" ? sectionName(node.name) : node.name,
          children: node.children.map(rename),
        }
      : node;
  return { ...tree, children: tree.children.map(rename) };
}

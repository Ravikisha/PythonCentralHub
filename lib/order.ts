import type { Node, Root } from "fumadocs-core/page-tree";
import { source } from "./source";

/**
 * The order the course is meant to be read in.
 *
 * Three rules, applied in this order:
 *
 *  1. **Modules** follow the learning path below, not the alphabet. It is the
 *     order the Astro sidebar was configured with by hand -- setup, then the
 *     language, then what you can build with it -- and alphabetical put "Data
 *     Analytics" first and "Guides" fifth, which is nobody's first day.
 *  2. **Pages** follow `sidebar.order` from their own frontmatter. 1264 of
 *     them carry one; it is the author's sequence and Starlight honoured it.
 *     Fumadocs does not read it, which is why every folder came out in
 *     filename order -- "The Python Library" before "Welcome to Python Central
 *     Hub!".
 *  3. **Ties** fall back to a natural-order comparison of the title, so
 *     "Phase 2" sorts before "Phase 10". Plain alphabetical does the opposite,
 *     and nine of the twelve modules number their phases without padding.
 *
 * A folder takes the lowest order of anything inside it, so a phase sits where
 * its first page says it should.
 */
const MODULE_ORDER = [
  "/guides/",
  "/tutorials/",
  "/flask-tutorials/",
  "/python-automation-and-scripting/",
  "/data-analytics/",
  "/mathematics-for-machine-learning/",
  "/machine-learning/",
  "/deep-learning/",
  "/dsa-with-python/",
  "/software-testing-and-quality/",
  "/projects/",
  "/reference/",
];

/** Sorts after everything with a declared order, never equal to one. */
const UNORDERED = Number.MAX_SAFE_INTEGER;

/** url -> `sidebar.order`, built once from the page data. */
let orders: Map<string, number> | undefined;

function orderByUrl(): Map<string, number> {
  if (orders) return orders;

  orders = new Map();
  for (const page of source.getPages()) {
    const order = page.data.sidebar?.order;
    if (typeof order === "number") orders.set(page.url, order);
  }
  return orders;
}

/** "Phase 2" before "Phase 10"; case- and accent-insensitive otherwise. */
const natural = new Intl.Collator(undefined, {
  numeric: true,
  sensitivity: "base",
});

function nameOf(node: Node): string {
  return typeof node.name === "string" ? node.name : "";
}

function orderOf(node: Node): number {
  if (node.type === "page") return orderByUrl().get(node.url) ?? UNORDERED;

  if (node.type === "folder") {
    // A folder is where its earliest page is. Its own index page counts, so a
    // module whose overview says `order: 0` opens the module.
    let lowest = node.index
      ? (orderByUrl().get(node.index.url) ?? UNORDERED)
      : UNORDERED;
    for (const child of node.children)
      lowest = Math.min(lowest, orderOf(child));
    return lowest;
  }

  return UNORDERED;
}

function moduleRank(node: Node): number {
  const url =
    node.type === "folder"
      ? (node.index?.url ?? firstUrl(node))
      : node.type === "page"
        ? node.url
        : undefined;
  if (!url) return MODULE_ORDER.length;

  const index = MODULE_ORDER.findIndex((prefix) => url.startsWith(prefix));
  return index === -1 ? MODULE_ORDER.length : index;
}

function firstUrl(node: Node): string | undefined {
  if (node.type === "page") return node.url;
  if (node.type !== "folder") return undefined;

  for (const child of node.children) {
    const found = firstUrl(child);
    if (found) return found;
  }
  return node.index?.url;
}

/** Depth-first sort. Returns new arrays; the source tree is left alone. */
function sortChildren(children: Node[]): Node[] {
  return children
    .map((child) =>
      child.type === "folder"
        ? { ...child, children: sortChildren(child.children) }
        : child,
    )
    .sort(
      (a, b) =>
        orderOf(a) - orderOf(b) || natural.compare(nameOf(a), nameOf(b)),
    );
}

/**
 * Put a whole tree in reading order.
 *
 * Modules are ranked by the learning path; everything below them by their own
 * frontmatter. The pager walks this same tree, so "next" follows the sidebar
 * rather than the filesystem.
 */
export function inReadingOrder(tree: Root): Root {
  const children = sortChildren(tree.children).sort(
    (a, b) =>
      moduleRank(a) - moduleRank(b) || natural.compare(nameOf(a), nameOf(b)),
  );

  return { ...tree, children };
}

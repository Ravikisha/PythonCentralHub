import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

export async function GET(context) {
  const docs = await getCollection("docs");

  // Syndicate tutorials and project pages (skip drafts and the 404 page).
  const items = docs
    .filter((entry) => {
      const id = entry.id.toLowerCase();
      return id.startsWith("tutorials/") || id.startsWith("projects/");
    })
    // Astro 5 content layer: entries are keyed by `id` (the old `slug`).
    .filter((entry) => entry.id !== "404")
    .map((entry) => ({
      title: entry.data.title,
      description: entry.data.description ?? "",
      link: `/${entry.id}/`,
      // @astrojs/rss requires pubDate on every item. Docs frontmatter has no
      // date field, so fall back to lastUpdated when present, else a fixed date.
      pubDate: entry.data.lastUpdated ?? new Date("2024-01-01T00:00:00Z"),
    }));

  return rss({
    title: "Python Central Hub",
    description:
      "Tutorials and hands-on Python projects from Python Central Hub.",
    site: context.site,
    items,
  });
}

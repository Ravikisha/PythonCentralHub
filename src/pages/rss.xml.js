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
    .filter((entry) => entry.slug !== "404")
    .map((entry) => ({
      title: entry.data.title,
      description: entry.data.description ?? "",
      link: `/${entry.slug}/`,
    }));

  return rss({
    title: "Python Central Hub",
    description:
      "Tutorials and hands-on Python projects from Python Central Hub.",
    site: context.site,
    items,
  });
}

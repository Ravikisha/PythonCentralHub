import { source } from "@/lib/source";
import { SITE_DESCRIPTION, SITE_NAME, SITE_URL, canonical } from "@/lib/site";
import { lastModifiedFor } from "@/lib/last-modified";

/**
 * /rss.xml -- the feed the Astro site published, kept at the same address.
 *
 * Tutorials and projects only. The reference material, the locale roots and
 * the course-wide index pages are not things anyone wants delivered as a
 * stream of updates, and the old feed drew the same line.
 *
 * Static: the content is known at build time, so this is generated once
 * rather than assembled per request.
 */
export const dynamic = "force-static";

const FEED_PREFIXES = ["/tutorials/", "/projects/"];

/** Frontmatter has no publication date; the file's own history is the honest
 *  fallback, and a fixed date for the pages that predate it. */
const EPOCH = new Date("2024-01-01T00:00:00Z");

function escapeXml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function GET() {
  const items = source
    .getPages()
    .filter((page) =>
      FEED_PREFIXES.some((prefix) => page.url.startsWith(prefix)),
    )
    .map((page) => {
      const date = lastModifiedFor(page.path) ?? EPOCH;
      return `    <item>
      <title>${escapeXml(page.data.title)}</title>
      <description>${escapeXml(page.data.description ?? "")}</description>
      <link>${canonical(page.url)}</link>
      <guid isPermaLink="true">${canonical(page.url)}</guid>
      <pubDate>${date.toUTCString()}</pubDate>
    </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(SITE_NAME)}</title>
    <description>${escapeXml(SITE_DESCRIPTION)}</description>
    <link>${SITE_URL}</link>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: { "content-type": "application/xml; charset=utf-8" },
  });
}

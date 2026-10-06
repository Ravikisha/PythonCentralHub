import type { MetadataRoute } from "next";
import { source } from "@/lib/source";
import { canonical } from "@/lib/site";
import { lastModifiedFor } from "@/lib/last-modified";
import { allCourses } from "@/lib/courses";

/**
 * Every page the course serves, for crawlers.
 *
 * Built from the same source the routes are, so a page cannot exist without
 * appearing here. Dates come from git rather than the build clock, so a
 * crawler is not told that all 1183 pages changed today.
 *
 * The signed-in pages are left out on purpose -- see robots.ts.
 */

/** Real routes, but not pages anyone should be sent to from a search result. */
const EXCLUDED = new Set(["/404", "/not-found"]);

export default function sitemap(): MetadataRoute.Sitemap {
  const lessons: MetadataRoute.Sitemap = source
    .getPages()
    .filter((page) => !EXCLUDED.has(page.url))
    .map((page) => ({
      url: canonical(page.url),
      lastModified: lastModifiedFor(page.path),
      changeFrequency: "monthly",
      priority: page.url === "/" ? 1 : 0.7,
    }));

  // The catalogue and the course pages are app routes, not content files, so
  // the loop above never saw them.
  const courses: MetadataRoute.Sitemap = [
    { url: canonical("/courses/"), changeFrequency: "weekly", priority: 0.9 },
    ...allCourses().map((course) => ({
      url: canonical(course.href),
      changeFrequency: "weekly" as const,
      priority: 0.9,
    })),
  ];

  return [...courses, ...lessons];
}

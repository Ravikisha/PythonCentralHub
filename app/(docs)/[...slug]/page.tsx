import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { findNeighbour, findPath } from "fumadocs-core/page-tree";
import { source, courseTree, slimBranch } from "@/lib/source";
import { Header } from "@/components/docs/Header";
import { Sidebar } from "@/components/docs/Sidebar";
import { getMDXComponents } from "@/mdx-components";
import { Toc } from "@/components/docs/Toc";
import { Pager } from "@/components/docs/Pager";
import { PageProgress } from "@/components/progress/PageProgress";
import { lastModifiedFor } from "@/lib/last-modified";
import { courseInfo } from "@/lib/courses.data.mjs";
import Link from "next/link";
import { Feedback } from "@/components/docs/Feedback";
import { JsonLd } from "@/components/seo/JsonLd";
import { SITE_NAME, canonical, ogImage } from "@/lib/site";
import "@/components/learn/learn.css";

/**
 * Every content page.
 *
 * A required catch-all, not an optional one: `/` is served by app/page.tsx,
 * the landing page, which is a designed surface rather than a content file.
 * Everything below the root keeps the Astro site's URL shape exactly, because
 * 1116 of those URLs are indexed.
 */
export const dynamicParams = false;

const NOINDEX = new Set(["/404", "/not-found"]);

export function generateStaticParams() {
  // Drop the empty slug: that is `/`, and app/page.tsx owns it. Leaving it in
  // makes two routes claim the same path.
  return source.generateParams().filter((p) => p.slug && p.slug.length > 0);
}

export async function generateMetadata(props: {
  params: Promise<{ slug: string[] }>;
}): Promise<Metadata> {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) return {};

  // A preview image naming the lesson and its course, drawn on request by
  // app/api/og. Set here in full: a page's openGraph replaces the layout's.
  const og = ogImage(page.data.title, params.slug[0]);
  return {
    title: page.data.title,
    description: page.data.description,
    alternates: { canonical: page.url },
    openGraph: {
      type: "article",
      siteName: SITE_NAME,
      title: page.data.title,
      description: page.data.description,
      images: [{ url: og, width: 1200, height: 630, alt: page.data.title }],
    },
    twitter: { card: "summary_large_image", images: [og] },
    // These two are content files that exist only as fallbacks; served with
    // a 200 they were indexable soft 404s.
    ...(NOINDEX.has(page.url) ? { robots: { index: false, follow: true } } : {}),
  };
}

export default async function Page(props: {
  params: Promise<{ slug: string[] }>;
}) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const loaded = await page.data.load();
  const { body: MDX, toc } = loaded;

  // Words of prose, at 200 a minute. `structuredData` is what the search
  // extractor builds from the compiled page, so it already excludes code
  // blocks and component markup.
  const words = (loaded.structuredData?.contents ?? [])
    .map((entry: { content?: string }) => entry.content ?? "")
    .join(" ")
    .split(/\s+/)
    .filter(Boolean).length;
  const readingMinutes = Math.max(1, Math.round(words / 200));
  const updated = lastModifiedFor(page.path);

  const tree = courseTree();
  const course = courseInfo(page.url.split("/").filter(Boolean)[0] ?? "");

  // Previous and next stay inside the course. Walking the whole tree sent a
  // reader who finished Machine Learning straight into lesson one of Deep
  // Learning; the last lesson now hands back to the course page instead.
  const courseRoot = course
    ? tree.children.find(
        (n) =>
          n.type === "folder" &&
          findPath([n], (m) => m.type === "page" && m.url === page.url),
      )
    : undefined;
  const neighbours = findNeighbour(
    courseRoot ? { ...tree, children: [courseRoot] } : tree,
    page.url,
  );

  // The folders this page sits under, which is the phase and module it belongs
  // to. Shown above the title because on a course of 1192 pages, "where am I"
  // is the first thing a reader arriving from search needs answered.
  // findPath takes the node list and a matcher, not a tree and a url.
  const trail =
    findPath(tree.children, (n) => n.type === "page" && n.url === page.url) ??
    [];
  const where = trail
    .filter((n) => n.type === "folder")
    .map((n) => (typeof n.name === "string" ? n.name : ""))
    .filter(Boolean);
  // Inside a course the first crumb is the course, by its course name.
  const sections = course ? where.slice(1) : where;

  const branch = slimBranch(page.url);

  return (
    <>
      <Header tree={branch} />
      <div className="shell">
        <div className="shell__sidebar">
          <Sidebar tree={branch} />
        </div>

      {course ? (
        <JsonLd
          data={{
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Courses", item: canonical("/courses/") },
              {
                "@type": "ListItem",
                position: 2,
                name: course.title,
                item: canonical(`/courses/${course.slug}/`),
              },
              { "@type": "ListItem", position: 3, name: page.data.title, item: canonical(page.url) },
            ],
          }}
        />
      ) : null}

      <main className="shell__main">
        <article className="article">
          {course ? (
            <p className="article__eyebrow">
              <Link href={`/courses/${course.slug}/`}>{course.title}</Link>
              {sections.map((name) => (
                <span key={name}> / {name}</span>
              ))}
            </p>
          ) : where.length > 0 ? (
            <p className="article__eyebrow">{where.join(" / ")}</p>
          ) : null}

          <h1 className="article__title">{page.data.title}</h1>

          {page.data.description ? (
            <p className="article__lede">{page.data.description}</p>
          ) : null}

          {/* Two facts a reader uses before starting: how long this takes, and
              whether it has been touched recently. The reading time counts the
              prose at 200 words a minute and ignores code, which is read at a
              different speed entirely. */}
          <p className="article__meta">
            <span>{readingMinutes} min read</span>
            {updated ? (
              <span>
                updated{" "}
                {updated.toLocaleDateString("en-GB", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </span>
            ) : null}
          </p>

          <div className="article__body">
            {/* Components are supplied here rather than imported by each page:
                1062 of the 1190 files used to open with an import line. */}
            <MDX components={getMDXComponents()} />
          </div>

          {/* Marking a page done, saving it, and the learner's own note. Ends
              the page rather than opening it: the decision belongs after the
              reading, not before it. */}
          <PageProgress title={page.data.title} />

          {/* Asked after the page has been read, and it opens only once a face
              is picked -- the fields are not there to be scrolled past. */}
          <Feedback />
        </article>

        <Pager
          previous={
            neighbours.previous
              ? {
                  url: neighbours.previous.url,
                  title: String(neighbours.previous.name),
                }
              : undefined
          }
          next={
            neighbours.next
              ? {
                  url: neighbours.next.url,
                  title: String(neighbours.next.name),
                }
              : course
                ? {
                    url: `/courses/${course.slug}/`,
                    title: `Back to ${course.title}`,
                  }
                : undefined
          }
        />
      </main>

      <div className="shell__toc">
        <Toc items={toc} />
      </div>
      </div>
    </>
  );
}

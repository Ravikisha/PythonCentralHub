import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Check } from "lucide-react";
import { CourseStatus, Syllabus } from "@/components/courses/CourseProgress";
import { CourseRatings } from "@/components/courses/CourseRatings";
import { JsonLd } from "@/components/seo/JsonLd";
import { SITE_NAME, SITE_URL, canonical, ogImage } from "@/lib/site";
import {
  allCourses,
  getCourse,
  LEVEL_LABEL,
  subjectLabel,
} from "@/lib/courses";

export const dynamicParams = false;

export function generateStaticParams() {
  return allCourses().map((c) => ({ course: c.slug }));
}

export async function generateMetadata(props: {
  params: Promise<{ course: string }>;
}): Promise<Metadata> {
  const { course: slug } = await props.params;
  const course = getCourse(slug);
  if (!course) return {};
  const og = ogImage(course.title, course.slug);
  return {
    title: `${course.title} (${course.code})`,
    description: course.summary,
    alternates: { canonical: course.href },
    openGraph: {
      type: "website",
      siteName: SITE_NAME,
      title: `${course.title} (${course.code})`,
      description: course.summary,
      images: [{ url: og, width: 1200, height: 630, alt: course.title }],
    },
    twitter: { card: "summary_large_image", images: [og] },
  };
}

/**
 * One course: what it teaches, how big it is, what to take first, and the
 * full syllabus with the learner's progress on it.
 */
export default async function CoursePage(props: {
  params: Promise<{ course: string }>;
}) {
  const { course: slug } = await props.params;
  const course = getCourse(slug);
  if (!course) notFound();

  const before = (course.after ?? [])
    .map((s) => getCourse(s))
    .filter((c) => c !== undefined);
  const leadsTo = allCourses().filter((c) => c.after?.includes(course.slug));

  return (
    <article className="course" data-subject={course.subject}>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "Course",
          name: course.title,
          courseCode: course.code,
          description: course.summary,
          url: canonical(course.href),
          provider: { "@type": "Organization", name: SITE_NAME, sameAs: SITE_URL },
          isAccessibleForFree: true,
          educationalLevel: LEVEL_LABEL[course.level],
          teaches: course.outcomes,
          hasCourseInstance: {
            "@type": "CourseInstance",
            courseMode: "online",
            courseWorkload: `PT${course.hours}H`,
          },
          offers: { "@type": "Offer", price: 0, priceCurrency: "USD", category: "Free" },
        }}
      />
      <nav className="course__crumbs" aria-label="Breadcrumb">
        <Link href="/courses/">Courses</Link>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{course.title}</span>
      </nav>

      <header className="course__head">
        <p className="course__code">
          <span>{course.code}</span>
          <span className="cc__level">{LEVEL_LABEL[course.level]}</span>
          <span className="course__subject">{subjectLabel(course.subject)}</span>
        </p>
        <h1 className="course__title">{course.title}</h1>
        <p className="course__lede">{course.summary}</p>

        <CourseStatus
          slug={course.slug}
          title={course.title}
          lessons={course.lessons}
          firstLesson={course.firstLesson}
          hasExam={course.hasExam}
          before={before.map(({ slug, title, code, href }) => ({ slug, title, code, href }))}
          after={leadsTo.map(({ slug, title, code, href }) => ({ slug, title, code, href }))}
        />
      </header>

      <div className="course__body">
        <div className="course__main">
          <section aria-labelledby="learn">
            <h2 id="learn">What you will learn</h2>
            <ul className="outcomes">
              {course.outcomes.map((o) => (
                <li key={o}>
                  <Check className="outcomes__icon" aria-hidden="true" />
                  {o}
                </li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="syllabus">
            <h2 id="syllabus">Syllabus</h2>
            <p className="course__note">
              {course.sectionCount > 0
                ? `${course.lessons.length} lessons in ${course.sectionCount} sections. Take them in order, or open any lesson directly.`
                : `${course.lessons.length} lessons. Take them in order, or open any lesson directly.`}
            </p>
            <Syllabus items={course.syllabus} />
          </section>

          <CourseRatings slug={course.slug} title={course.title} />
        </div>

        <aside className="course__side" aria-label="About this course">
          <dl className="facts">
            <div>
              <dt>Lessons</dt>
              <dd>{course.lessons.length}</dd>
            </div>
            {course.exerciseCount > 0 ? (
              <div>
                <dt>Exercises</dt>
                <dd>{course.exerciseCount}</dd>
              </div>
            ) : null}
            <div>
              <dt>Reading time</dt>
              <dd>About {course.hours} h</dd>
            </div>
            <div>
              <dt>Level</dt>
              <dd>{LEVEL_LABEL[course.level]}</dd>
            </div>
            <div>
              <dt>Cost</dt>
              <dd>Free</dd>
            </div>
          </dl>

          <div className="side-card">
            <h2>Before you start</h2>
            {before.length ? (
              <ul className="side-card__list">
                {before.map((c) => (
                  <li key={c.slug} data-subject={c.subject}>
                    <Link href={c.href}>
                      <span className="side-card__code">{c.code}</span>
                      {c.title}
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No earlier course needed. This is a starting point.</p>
            )}
          </div>

          {course.hasExam ? (
            <div className="side-card">
              <h2>Certificate</h2>
              <p>
                Finish 90% of the lessons and pass the final assessment to
                earn a certificate with a public verification link.
              </p>
              <Link className="button" href={`/exam/${course.slug}/`}>
                Final assessment
              </Link>
            </div>
          ) : null}

          {leadsTo.length ? (
            <div className="side-card">
              <h2>Where it leads</h2>
              <ul className="side-card__list">
                {leadsTo.map((c) => (
                  <li key={c.slug} data-subject={c.subject}>
                    <Link href={c.href}>
                      <span className="side-card__code">{c.code}</span>
                      {c.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </aside>
      </div>
    </article>
  );
}

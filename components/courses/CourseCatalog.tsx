"use client";

import Link from "next/link";
import { useState } from "react";
import { countDone, enrol, useProgress } from "./useProgress";

/** What a card needs, flattened so it can cross the server/client boundary. */
export interface CourseCardData {
  slug: string;
  title: string;
  code: string;
  level: string;
  levelLabel: string;
  subject: string;
  subjectLabel: string;
  summary: string;
  href: string;
  firstLesson: string;
  lessonCount: number;
  /** Every lesson's url, so progress counts only lessons that exist. */
  lessonUrls: string[];
  exerciseCount: number;
  hours: number;
  hasExam: boolean;
}

/**
 * The catalogue: every course as a card, filterable by subject.
 *
 * The card is the course's front door, so it answers the three questions
 * someone browsing has, in order: what is it, how big is it, and -- once they
 * have started -- how far along they are. The progress row is empty on the
 * server and fills in after mount from the browser's own store.
 */
export function CourseCatalog({
  courses,
  subjects,
}: {
  courses: CourseCardData[];
  subjects: { id: string; label: string }[];
}) {
  const [subject, setSubject] = useState<string>("all");
  const progress = useProgress();

  // Only offer subjects that have a course in them.
  const offered = subjects.filter((s) =>
    courses.some((c) => c.subject === s.id),
  );
  const shown =
    subject === "all" ? courses : courses.filter((c) => c.subject === subject);

  return (
    <>
      <div className="catalog__filters" role="group" aria-label="Filter by subject">
        <button
          type="button"
          className="chip"
          aria-pressed={subject === "all"}
          onClick={() => setSubject("all")}
        >
          All courses
        </button>
        {offered.map((s) => (
          <button
            key={s.id}
            type="button"
            className="chip"
            data-subject={s.id}
            aria-pressed={subject === s.id}
            onClick={() => setSubject(s.id)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <ul className="catalog__grid">
        {shown.map((course) => {
          // Counted against the course's real lessons, as the course page
          // does: a raw count of stored ids included lessons renamed since,
          // so the card and the course page could disagree.
          const done = countDone(course.lessonUrls, progress.done);
          const pct = course.lessonCount
            ? Math.round((done / course.lessonCount) * 100)
            : 0;
          const lastHere =
            progress.last && progress.last.pageId.split("/")[0] === course.slug
              ? progress.last.href
              : undefined;
          const state =
            done === 0 && !lastHere
              ? "new"
              : done >= course.lessonCount
                ? "complete"
                : "started";

          return (
            <li key={course.slug} className="cc" data-subject={course.subject}>
              <p className="cc__code">
                <span>{course.code}</span>
                <span className="cc__level" data-level={course.level}>
                  {course.levelLabel}
                </span>
              </p>

              <h3 className="cc__title">
                {/* The title link stretches over the card, so the whole card
                    opens the course; the action below sits above it. */}
                <Link href={course.href} className="cc__link">
                  {course.title}
                </Link>
              </h3>

              <p className="cc__summary">{course.summary}</p>

              <ul className="cc__facts" aria-label="Course size">
                <li>{course.lessonCount} lessons</li>
                {course.exerciseCount > 0 ? (
                  <li>{course.exerciseCount} exercises</li>
                ) : null}
                <li>{course.hours} h reading</li>
                {course.hasExam ? <li>Certificate</li> : null}
              </ul>

              <div className="cc__foot">
                <div className="cc__progress" data-state={state}>
                  <span
                    className="meter"
                    role="progressbar"
                    aria-label={`${course.title} progress`}
                    aria-valuemin={0}
                    aria-valuemax={course.lessonCount}
                    aria-valuenow={done}
                  >
                    <span style={{ width: `${pct}%` }} />
                  </span>
                  <span className="cc__count">
                    {!progress.ready || state === "new"
                      ? "Not started"
                      : state === "complete"
                        ? "Completed"
                        : `${done} of ${course.lessonCount} done`}
                  </span>
                </div>

                <Link
                  className="cc__action"
                  onClick={() => enrol(course.slug)}
                  href={
                    state === "started"
                      ? (lastHere ?? course.href)
                      : state === "complete"
                        ? course.href
                        : course.firstLesson
                  }
                >
                  {state === "started"
                    ? "Continue"
                    : state === "complete"
                      ? "Review"
                      : "Start course"}
                </Link>
              </div>
            </li>
          );
        })}
      </ul>
    </>
  );
}

/**
 * "Pick up where you left off", for a returning learner.
 *
 * Until the store is read, and for a first visit, it shows its children
 * instead -- the home page passes the suggested first course.
 */
export function ContinueLearning({
  titles,
  children,
}: {
  /** Course slug -> course title. */
  titles: Record<string, string>;
  /** Shown instead, to a first-time visitor (and in the prerendered HTML). */
  children?: React.ReactNode;
}) {
  const { last, ready } = useProgress();
  const course = last ? titles[last.pageId.split("/")[0]] : undefined;
  if (!ready || !last || !course) return <>{children}</>;

  return (
    <Link className="resume" href={last.href}>
      <span className="resume__label">Pick up where you left off</span>
      <span className="resume__title">{last.title}</span>
      <span className="resume__course">{course}</span>
      <span className="resume__go">Continue</span>
    </Link>
  );
}

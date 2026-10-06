"use client";

import Link from "next/link";
import { Check } from "lucide-react";
import type { Lesson, SyllabusItem } from "@/lib/courses";
import { countDone, enrol, lessonId, practiceIn, useProgress } from "./useProgress";
import { ClaimCompletion } from "./ClaimCompletion";

/** The first lesson not yet done, in course order. */
function nextLesson(lessons: Lesson[], done: Set<string>): Lesson | undefined {
  return lessons.find((l) => !done.has(lessonId(l.url)));
}

/** A course another part of the page points to. */
export interface CourseLink {
  slug: string;
  title: string;
  code: string;
  href: string;
}

/**
 * Where the learner stands in this course, and the one button to go on.
 *
 * "Continue" goes to the first lesson not yet marked done, rather than the
 * last one opened: on a course page the question is what is left, and the
 * last page opened may be one they skimmed past.
 *
 * Two moments get their own line. Before starting, if the courses this one
 * builds on are untouched, it says so -- a suggestion, never a gate. At the
 * end, the finished course gets a proper finish: what to do for the
 * certificate, and which course comes next.
 */
export function CourseStatus({
  slug,
  title,
  lessons,
  firstLesson,
  hasExam,
  before = [],
  after = [],
}: {
  slug: string;
  title: string;
  lessons: Lesson[];
  firstLesson: string;
  hasExam: boolean;
  /** Recommended earlier courses. */
  before?: CourseLink[];
  /** Courses that build on this one. */
  after?: CourseLink[];
}) {
  const progress = useProgress();
  const { done, ready, perCourse } = progress;
  const practice = practiceIn(lessons, progress);
  const finished = countDone(
    lessons.map((l) => l.url),
    done,
  );
  const total = lessons.length;
  const next = nextLesson(lessons, done);
  const started = ready && finished > 0;
  const complete = ready && finished >= total;
  const pct = total ? Math.round((finished / total) * 100) : 0;
  const untouched = ready && !started
    ? before.filter((c) => !(perCourse[c.slug] > 0))
    : [];

  return (
    <>
      <div className="status">
        <div className="status__meter">
          <span
            className="meter"
            role="progressbar"
            aria-label={`${title} progress`}
            aria-valuemin={0}
            aria-valuemax={total}
            aria-valuenow={finished}
          >
            <span style={{ width: `${pct}%` }} />
          </span>
          <span className="status__count">
            {!started
              ? `${total} lessons, not started`
              : complete
                ? `All ${total} lessons done`
                : `${finished} of ${total} lessons done, ${pct}%`}
          </span>
          {ready && (practice.passed || practice.quizzesTaken) ? (
            <span className="status__practice">
              {practice.exercises
                ? `${practice.passed} of ${practice.exercises} exercises passed`
                : null}
              {practice.exercises && practice.quizzesTaken ? " · " : null}
              {practice.quizzesTaken
                ? `quizzes ${Math.round((practice.quizCorrect / practice.quizTotal) * 100)}% correct (${practice.quizzesTaken} ${practice.quizzesTaken === 1 ? "lesson" : "lessons"})`
                : null}
            </span>
          ) : null}
        </div>

        <div className="status__go">
          <Link
            // Once finished, the next step lives in the panel below; this
            // steps down so the page keeps a single primary action.
            className={complete ? "button" : "button button--primary"}
            href={started && next ? next.url : firstLesson}
            onClick={() => enrol(slug)}
          >
            {complete ? "Review from the start" : started ? "Continue" : "Start course"}
          </Link>
          {started && next ? (
            <span className="status__next">
              Next: <Link href={next.url}>{next.title}</Link>
            </span>
          ) : null}
        </div>
      </div>

      {untouched.length ? (
        <p className="status__advice">
          This course builds on{" "}
          {untouched.map((c, i) => (
            <span key={c.slug}>
              {i > 0 ? (i === untouched.length - 1 ? " and " : ", ") : ""}
              <Link href={c.href}>{c.title}</Link>
            </span>
          ))}
          . If those topics are new to you, start there; otherwise, go ahead.
        </p>
      ) : null}

      {complete ? (
        <div className="finish" role="status">
          <p className="finish__title">You finished {title}.</p>
          <p className="finish__body">
            {hasExam
              ? "Sit the final assessment for a certificate with your score, or take a certificate of completion now. Then carry on with what builds on it."
              : "That is every lesson. Here is what builds on it."}
          </p>
          <p className="finish__actions">
            {hasExam ? (
              <Link className="button button--primary" href={`/exam/${slug}/`}>
                Take the final assessment
              </Link>
            ) : null}
            <ClaimCompletion slug={slug} />
            {after.slice(0, 2).map((c) => (
              <Link className="button" href={c.href} key={c.slug}>
                Next: {c.title}
              </Link>
            ))}
            {!after.length ? (
              <Link className="button" href="/courses/">
                Choose another course
              </Link>
            ) : null}
          </p>
        </div>
      ) : null}
    </>
  );
}

/**
 * The syllabus: every lesson in order, with the learner's marks on it.
 *
 * Sections fold, because a 200-lesson list is not a table of contents
 * anyone reads top to bottom. The section holding the next lesson opens
 * itself, so the page lands on where you are.
 */
export function Syllabus({ items }: { items: SyllabusItem[] }) {
  const { done, ready } = useProgress();
  const all = items.flatMap((i) => (i.kind === "lesson" ? [i.lesson] : i.lessons));
  const next = ready ? nextLesson(all, done) : undefined;

  return (
    <ol className="syllabus">
      {items.map((item, i) =>
        item.kind === "lesson" ? (
          <li key={item.lesson.url} className="syllabus__single">
            <LessonRow lesson={item.lesson} done={done} next={next} />
          </li>
        ) : (
          <li key={`${item.title}-${i}`}>
            <Section
              title={item.title}
              lessons={item.lessons}
              done={done}
              next={next}
            />
          </li>
        ),
      )}
    </ol>
  );
}

function Section({
  title,
  lessons,
  done,
  next,
}: {
  title: string;
  lessons: Lesson[];
  done: Set<string>;
  next?: Lesson;
}) {
  const finished = countDone(
    lessons.map((l) => l.url),
    done,
  );
  const holdsNext = Boolean(next && lessons.some((l) => l.url === next.url));

  return (
    <details className="syllabus__section" open={holdsNext || undefined}>
      <summary>
        <span className="syllabus__name">{title}</span>
        <span className="syllabus__tally">
          {finished > 0 ? `${finished} of ${lessons.length}` : `${lessons.length} lessons`}
        </span>
      </summary>
      <ol className="syllabus__lessons">
        {lessons.map((lesson) => (
          <li key={lesson.url}>
            <LessonRow lesson={lesson} done={done} next={next} />
          </li>
        ))}
      </ol>
    </details>
  );
}

function LessonRow({
  lesson,
  done,
  next,
}: {
  lesson: Lesson;
  done: Set<string>;
  next?: Lesson;
}) {
  const isDone = done.has(lessonId(lesson.url));
  const isNext = next?.url === lesson.url;
  const state = isDone ? "done" : isNext ? "next" : "todo";

  return (
    <Link className="lesson" href={lesson.url} data-state={state}>
      <span className="lesson__mark" aria-hidden="true">
        {isDone ? <Check className="size-3" strokeWidth={3} /> : null}
      </span>
      <span className="lesson__title">{lesson.title}</span>
      {lesson.minutes ? (
        <span className="lesson__meta">
          {lesson.minutes} min
          {lesson.exercises ? `, ${lesson.exercises} ${lesson.exercises === 1 ? "exercise" : "exercises"}` : ""}
        </span>
      ) : null}
      {isDone ? (
        <span className="sr-only">(done)</span>
      ) : isNext ? (
        <span className="lesson__tag">Up next</span>
      ) : null}
    </Link>
  );
}

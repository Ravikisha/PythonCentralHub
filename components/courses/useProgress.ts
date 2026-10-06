"use client";

import { useEffect, useState } from "react";
import {
  read,
  subscribe,
  getLastPage,
  exercisesByPage,
  type ProgressState,
} from "@/src/lib/progress/local";

export { enrol } from "@/src/lib/progress/local";

export interface LearnerProgress {
  /** Completed lesson ids, e.g. "tutorials/numbers". */
  done: Set<string>;
  /** Completed lessons per course slug. */
  perCourse: Record<string, number>;
  /** Courses taken up, oldest first. */
  enrolled: string[];
  /** Passed exercises per lesson id. */
  exercises: Map<string, number>;
  /** Best quiz results per lesson id, summed over the lesson's quizzes. */
  quizzes: Map<string, { correct: number; total: number }>;
  /** The last lesson opened anywhere, if any. */
  last: ReturnType<typeof getLastPage>;
  /** False until the browser store has been read. */
  ready: boolean;
}

/** "/tutorials/numbers/" -> "tutorials/numbers", the progress store's key. */
export function lessonId(url: string): string {
  return url.replace(/^\/|\/$/g, "").toLowerCase();
}

function fromState(state: ProgressState): Set<string> {
  return new Set(Object.values(state.modules).flat());
}

/** `${pageId}#${n}` keys grouped by page id. */
function pageOf(key: string): string {
  return key.slice(0, key.lastIndexOf("#"));
}

function quizzesByPage(state: ProgressState): Map<string, { correct: number; total: number }> {
  const out = new Map<string, { correct: number; total: number }>();
  for (const [key, r] of Object.entries(state.quizzes)) {
    const page = pageOf(key);
    const sum = out.get(page) ?? { correct: 0, total: 0 };
    out.set(page, { correct: sum.correct + r.correct, total: sum.total + r.total });
  }
  return out;
}

/**
 * The learner's progress, from the same local store the lesson pages write.
 *
 * Read after mount, never during render: course cards are prerendered and
 * identical for everyone, and reading storage while rendering would make the
 * first client render disagree with the HTML.
 */
export function useProgress(): LearnerProgress {
  const [progress, setProgress] = useState<LearnerProgress>({
    done: new Set(),
    perCourse: {},
    enrolled: [],
    exercises: new Map(),
    quizzes: new Map(),
    last: null,
    ready: false,
  });

  useEffect(() => {
    const update = (state: ProgressState) =>
      setProgress({
        done: fromState(state),
        perCourse: Object.fromEntries(
          Object.entries(state.modules).map(([slug, ids]) => [slug, ids.length]),
        ),
        enrolled: state.enrolled ?? [],
        exercises: exercisesByPage(state),
        quizzes: quizzesByPage(state),
        last: getLastPage(),
        ready: true,
      });
    update(read());
    return subscribe(update);
  }, []);

  return progress;
}

/** How many of these lessons are done. */
export function countDone(urls: string[], done: Set<string>): number {
  let n = 0;
  for (const url of urls) if (done.has(lessonId(url))) n += 1;
  return n;
}

/**
 * Exercises passed and quiz results across these lessons.
 *
 * Passes are capped at each lesson's exercise count, so a lesson whose
 * exercises were since rewritten or removed cannot push past 100%.
 */
export function practiceIn(
  lessons: { url: string; exercises?: number }[],
  progress: Pick<LearnerProgress, "exercises" | "quizzes">,
): {
  passed: number;
  exercises: number;
  quizCorrect: number;
  quizTotal: number;
  quizzesTaken: number;
} {
  let passed = 0;
  let exercises = 0;
  let quizCorrect = 0;
  let quizTotal = 0;
  let quizzesTaken = 0;
  for (const lesson of lessons) {
    const id = lessonId(lesson.url);
    const count = lesson.exercises ?? 0;
    exercises += count;
    passed += Math.min(count, progress.exercises.get(id) ?? 0);
    const quiz = progress.quizzes.get(id);
    if (quiz) {
      quizCorrect += quiz.correct;
      quizTotal += quiz.total;
      quizzesTaken += 1;
    }
  }
  return { passed, exercises, quizCorrect, quizTotal, quizzesTaken };
}

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { enrol, read } from "@/src/lib/progress/local";

export interface Goal {
  id: string;
  title: string;
  blurb: string;
  courses: {
    slug: string;
    title: string;
    code: string;
    subject: string;
    href: string;
    firstLesson: string;
    lessons: number;
  }[];
}

const GOAL_KEY = "pch-goal";

/**
 * The goal picker. Choosing one enrols the learner in its courses, skipping
 * Python Programming if they say they already know it, and remembers the
 * choice so coming back here shows it.
 */
export function Welcome({ goals }: { goals: Goal[] }) {
  const [chosen, setChosen] = useState<string | null>(null);
  const [knowsPython, setKnowsPython] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    try {
      setChosen(localStorage.getItem(GOAL_KEY));
    } catch {
      /* storage blocked: start with nothing chosen */
    }
  }, []);

  const goal = goals.find((g) => g.id === chosen);
  const plan = goal
    ? goal.courses.filter((c) => !(knowsPython && c.slug === "tutorials" && goal.courses.length > 1))
    : [];

  function start() {
    if (!goal) return;
    const already = new Set(read().enrolled ?? []);
    for (const course of plan) if (!already.has(course.slug)) enrol(course.slug);
    try {
      localStorage.setItem(GOAL_KEY, goal.id);
    } catch {
      /* the enrolment itself is saved; only the remembered goal is lost */
    }
    setDone(true);
  }

  return (
    <div className="welcome">
      <div className="welcome__goals" role="radiogroup" aria-label="Your goal">
        {goals.map((g) => (
          <button
            key={g.id}
            type="button"
            role="radio"
            aria-checked={chosen === g.id}
            className="welcome__goal"
            onClick={() => {
              setChosen(g.id);
              setDone(false);
            }}
          >
            <span className="welcome__goal-title">
              {chosen === g.id ? <Check className="size-4" aria-hidden="true" /> : null}
              {g.title}
            </span>
            <span className="welcome__goal-blurb">{g.blurb}</span>
          </button>
        ))}
      </div>

      {goal ? (
        <section className="welcome__plan" aria-live="polite">
          {goal.courses.some((c) => c.slug === "tutorials") && goal.courses.length > 1 ? (
            <label className="welcome__skip">
              <input
                type="checkbox"
                checked={knowsPython}
                onChange={(e) => setKnowsPython(e.target.checked)}
              />
              I already know Python basics: skip Python Programming
            </label>
          ) : null}

          <h2>Your courses, in order</h2>
          <ol className="welcome__courses">
            {plan.map((c) => (
              <li key={c.slug} data-subject={c.subject}>
                <span className="welcome__code">{c.code}</span>
                <Link href={c.href}>{c.title}</Link>
                <span className="welcome__size">{c.lessons} lessons</span>
              </li>
            ))}
          </ol>

          {done && plan[0] ? (
            <p className="welcome__actions">
              <Link className="button button--primary" href={plan[0].firstLesson}>
                Start {plan[0].title}
              </Link>
              <Link className="button" href="/dashboard/">
                See My learning
              </Link>
            </p>
          ) : (
            <p className="welcome__actions">
              <button type="button" className="button button--primary" onClick={start}>
                Add {plan.length === 1 ? "this course" : `these ${plan.length} courses`}
              </button>
              <Link className="button" href="/courses/">
                Browse all courses instead
              </Link>
            </p>
          )}
        </section>
      ) : null}
    </div>
  );
}

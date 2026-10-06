import type { Metadata } from "next";
import { getCourse } from "@/lib/courses";
import { Welcome, type Goal } from "./Welcome";
import "./welcome.css";

/**
 * /welcome -- the first step after signing up: pick what you want to be able
 * to do, and the matching courses are added to "My courses" in order.
 *
 * Works for guests too (enrolment is local first), so the dashboard links
 * here when nobody has chosen a course yet.
 */
export const metadata: Metadata = {
  title: "Choose what to learn",
  robots: { index: false, follow: true },
};

const GOALS: { id: string; title: string; blurb: string; courses: string[] }[] = [
  {
    id: "start",
    title: "Learn to program",
    blurb: "Never written code, or rusty. Start with Python from the first print() and build small projects.",
    courses: ["tutorials", "projects"],
  },
  {
    id: "data-ai",
    title: "Work with data and AI",
    blurb: "Analyse data, then learn the mathematics and models behind machine learning and deep learning.",
    courses: ["tutorials", "data-analytics", "mathematics-for-machine-learning", "machine-learning", "deep-learning"],
  },
  {
    id: "engineering",
    title: "Build and ship software",
    blurb: "Data structures, testing and web apps with Flask: the skills behind production code.",
    courses: ["tutorials", "dsa-with-python", "software-testing-and-quality", "flask-tutorials"],
  },
  {
    id: "interviews",
    title: "Prepare for coding interviews",
    blurb: "Patterns, problem ladders and mock interviews, on top of solid Python.",
    courses: ["tutorials", "dsa-with-python"],
  },
  {
    id: "automate",
    title: "Automate my work",
    blurb: "Scripts that handle files, spreadsheets, the web and email for you.",
    courses: ["tutorials", "python-automation-and-scripting"],
  },
];

export default function WelcomePage() {
  const goals: Goal[] = GOALS.map((goal) => ({
    ...goal,
    courses: goal.courses
      .map((slug) => getCourse(slug))
      .filter((c): c is NonNullable<typeof c> => Boolean(c))
      .map((c) => ({
        slug: c.slug,
        title: c.title,
        code: c.code,
        subject: c.subject,
        href: c.href,
        firstLesson: c.firstLesson,
        lessons: c.lessons.length,
      })),
  }));

  return (
    <>
      <h1 className="pch-auth__title">What do you want to learn?</h1>
      <p className="pch-auth__intro">
        Pick a goal and we&rsquo;ll add the courses for it to <strong>My learning</strong>, in
        the order to take them. You can change this any time.
      </p>
      <Welcome goals={goals} />
    </>
  );
}

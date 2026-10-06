import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/docs/Header";
import { Footer } from "@/components/docs/Footer";
import {
  CourseCatalog,
  ContinueLearning,
} from "@/components/courses/CourseCatalog";
import { catalogCards, courseTitles } from "@/components/courses/catalog-data";
import { allCourses, getCourse, PATHS, SUBJECTS } from "@/lib/courses";
import { SITE_DESCRIPTION, SITE_NAME } from "@/lib/site";
import "@/components/docs/docs.css";
import "@/components/docs/chrome.css";
import "@/components/courses/courses.css";
import "./home.css";

/**
 * The home page is the course catalogue.
 *
 * Python Central Hub is a set of courses, so the first screen answers "what can I
 * learn here" with the courses themselves, sized from their real contents,
 * and a returning learner sees their place before anything else. Every
 * number on the page is counted from the content at build time.
 */
export const metadata: Metadata = {
  title: { absolute: `${SITE_NAME} — self-paced courses in code, data and maths` },
  description: SITE_DESCRIPTION,
  alternates: { canonical: "/" },
};

export default function Home() {
  const courses = allCourses();
  const lessons = courses.reduce((n, c) => n + c.lessons.length, 0);
  const exercises = courses.reduce((n, c) => n + c.exerciseCount, 0);
  const first = getCourse("tutorials");

  return (
    <>
      <Header />

      <main className="home">
        <section className="hero" aria-labelledby="home-title">
          <div className="hero__text">
            <h1 className="hero__title" id="home-title">
              Courses you take at your own pace
            </h1>
            <p className="hero__lede">
              {courses.length} free courses in programming, data, machine
              learning and mathematics: {lessons.toLocaleString("en-US")}{" "}
              lessons and {exercises.toLocaleString("en-US")} exercises that
              run in your browser. Nothing to install, nothing expires, and
              your place is kept for when you come back.
            </p>
            <p className="hero__actions">
              <Link className="button button--primary" href="#courses">
                Browse courses
              </Link>
              <Link className="button" href="/guides/home/">
                Set up Python first
              </Link>
            </p>
          </div>

          <div className="hero__side">
            <ContinueLearning titles={courseTitles()}>
              {first ? (
                <Link className="resume resume--start" href={first.firstLesson}>
                  <span className="resume__label">New to programming?</span>
                  <span className="resume__title">{first.title}</span>
                  <span className="resume__course">
                    {first.code}, {first.lessons.length} lessons. No experience
                    needed.
                  </span>
                  <span className="resume__go">Start the first lesson</span>
                </Link>
              ) : null}
            </ContinueLearning>
          </div>
        </section>

        <section className="catalog" id="courses" aria-labelledby="home-courses">
          <h2 id="home-courses">Courses</h2>
          <CourseCatalog courses={catalogCards()} subjects={SUBJECTS} />
        </section>

        <section className="paths" aria-labelledby="home-paths">
          <h2 id="home-paths">Learning paths</h2>
          <p className="paths__intro">
            Not sure what to take next? These are the courses in the order
            they build on each other.
          </p>

          {PATHS.map((path) => (
            <div className="path" key={path.id} data-subject={path.id}>
              <h3 className="path__title">{path.title}</h3>
              <ol className="path__stops">
                {path.courses.map((slug) => {
                  const course = getCourse(slug);
                  if (!course) return null;
                  return (
                    <li key={slug} data-subject={course.subject}>
                      <Link href={course.href}>
                        <span className="path__code">{course.code}</span>
                        <span className="path__name">{course.title}</span>
                      </Link>
                    </li>
                  );
                })}
              </ol>
            </div>
          ))}
        </section>

        <section className="how" aria-labelledby="home-how">
          <h2 id="home-how">How a course works</h2>
          <ol className="how__steps">
            <li>
              <h3>Read a lesson, run its code</h3>
              <p>
                Examples run on a real Python interpreter in the page, and the
                exercises check your answer as you go.
              </p>
            </li>
            <li>
              <h3>Mark it done and move on</h3>
              <p>
                Your progress is saved in this browser straight away. Sign in
                to keep it across devices, with bookmarks and notes.
              </p>
            </li>
            <li>
              <h3>Take the final assessment</h3>
              <p>
                Courses with a final assessment issue a certificate once you
                finish the lessons and pass, with a link anyone can check.
              </p>
            </li>
          </ol>
        </section>
      </main>

      <Footer />
    </>
  );
}

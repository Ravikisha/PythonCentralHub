import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import yaml from "js-yaml";
import type { Metadata } from "next";
import Link from "next/link";
import { ExamPaper } from "./ExamPaper";
import { getCourse } from "@/lib/courses";

/**
 * /exam/<module> -- the final assessment for one course.
 *
 * One page per file in src/data/exams/, so a course without an exam has no
 * route rather than a route that apologises.
 *
 * The paper itself is NOT baked into this page. It is fetched at runtime from
 * Firestore `exams/<module>`, which holds the questions without their answers;
 * the key never leaves the server and grading happens in app/api/grade-exam.
 * Rendering the questions at build time would put them in the static HTML,
 * where the next step is someone diffing them against the key.
 *
 * What this page does render is everything a learner wants to know before
 * starting: which course, how long, how many questions, the pass mark, and
 * what passing gets them.
 */
const EXAM_DIR = "src/data/exams";

interface ExamFile {
  module: string;
  title?: string;
  passScore?: number;
  timeLimitMinutes?: number;
  questions?: unknown[];
}

function exams(): ExamFile[] {
  if (!existsSync(EXAM_DIR)) return [];

  return readdirSync(EXAM_DIR)
    .filter((file) => /\.ya?ml$/.test(file))
    .map(
      (file) =>
        yaml.load(readFileSync(join(EXAM_DIR, file), "utf8")) as ExamFile,
    );
}

export const dynamicParams = false;

export function generateStaticParams() {
  return exams().map((exam) => ({ module: exam.module }));
}

export async function generateMetadata(props: {
  params: Promise<{ module: string }>;
}): Promise<Metadata> {
  const { module } = await props.params;
  const course = getCourse(module);

  return {
    title: course ? `${course.title}: final assessment` : "Final assessment",
    robots: { index: false, follow: true },
  };
}

export default async function ExamPage(props: {
  params: Promise<{ module: string }>;
}) {
  const { module } = await props.params;
  const exam = exams().find((e) => e.module === module);
  const course = getCourse(module);
  const questions = exam?.questions?.length ?? 0;
  const pass = exam?.passScore ?? 70;
  const minutes = exam?.timeLimitMinutes;

  return (
    <div className="assess" data-subject={course?.subject}>
      {course ? (
        <Link className="assess__course" href={course.href}>
          <span className="assess__code">{course.code}</span>
          <span>{course.title}</span>
        </Link>
      ) : null}

      <h1 className="assess__title">Final assessment</h1>
      <p className="assess__lede">
        {questions} questions on the whole course. Pass with {pass}% or more
        and, once you have finished 90% of the lessons, claim a certificate
        anyone can verify.
      </p>

      <dl className="assess__facts">
        <div>
          <dt>Questions</dt>
          <dd>{questions}</dd>
        </div>
        <div>
          <dt>Pass mark</dt>
          <dd>{pass}%</dd>
        </div>
        {minutes ? (
          <div>
            <dt>Suggested time</dt>
            <dd>{minutes} min</dd>
          </div>
        ) : null}
        <div>
          <dt>Retakes</dt>
          <dd>Every 10 min</dd>
        </div>
      </dl>

      <ExamPaper module={module} />
    </div>
  );
}

import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Node } from "fumadocs-core/page-tree";
import { courseTree, source } from "./source";
import {
  COURSES,
  SUBJECTS,
  PATHS,
  courseInfo,
  type CourseInfo,
} from "./courses.data.mjs";

export { SUBJECTS, PATHS };
export type { CourseInfo };

/**
 * Courses as the app uses them: the catalogue entry from courses.data.mjs,
 * joined to what the content tree actually holds.
 *
 * Everything countable -- lessons, sections, exercises, hours -- is measured
 * here at build time from the files themselves, so the numbers on a course
 * card are the course's real size, not a figure someone typed once.
 */

export interface Lesson {
  url: string;
  title: string;
  /** Minutes of reading (prose at 200 words a minute), at least 1. */
  minutes?: number;
  /** Runnable exercises on the page. */
  exercises?: number;
}

/** A syllabus row: a lesson on its own, or a named section of lessons. */
export type SyllabusItem =
  | { kind: "lesson"; lesson: Lesson }
  | { kind: "section"; title: string; lessons: Lesson[] };

export interface Course extends CourseInfo {
  /** Where the course page lives. */
  href: string;
  /** Where "Start course" goes. */
  firstLesson: string;
  lessons: Lesson[];
  syllabus: SyllabusItem[];
  sectionCount: number;
  exerciseCount: number;
  /** Reading time in hours, rounded up; code and exercises come on top. */
  hours: number;
  hasExam: boolean;
}

const CONTENT_DIR = "src/content/docs";
const EXAMS_DIR = "src/data/exams";

function nameOf(node: Node): string {
  return typeof node.name === "string" ? node.name : "";
}

/** The url as the site serves it (trailingSlash is on), so links never hop. */
function served(url: string): string {
  return url.endsWith("/") ? url : `${url}/`;
}

function lessonsIn(node: Node): Lesson[] {
  if (node.type === "page")
    return [{ url: served(node.url), title: nameOf(node) }];
  if (node.type !== "folder") return [];
  const own = node.index
    ? [{ url: served(node.index.url), title: nameOf(node.index) }]
    : [];
  return [...own, ...node.children.flatMap(lessonsIn)];
}

/** The module folder for a course slug, in reading order. */
function folderFor(slug: string): Extract<Node, { type: "folder" }> | undefined {
  const prefix = `/${slug}/`;
  for (const node of courseTree().children) {
    if (node.type !== "folder") continue;
    const first = lessonsIn(node)[0];
    if (first?.url.startsWith(prefix)) return node;
  }
  return undefined;
}

/** url -> file path under src/content/docs, built once. */
let paths: Map<string, string> | undefined;

function pathFor(url: string): string | undefined {
  if (!paths) {
    paths = new Map();
    for (const page of source.getPages()) paths.set(served(page.url), page.path);
  }
  return paths.get(served(url));
}

/**
 * Prose words and exercises in one lesson file.
 *
 * Front matter, imports, fenced code and component tags are removed before
 * counting, matching the "prose at 200 words a minute" rule the lesson page
 * uses for its own reading time.
 */
function measure(url: string): { words: number; exercises: number } {
  const path = pathFor(url);
  if (!path) return { words: 0, exercises: 0 };

  let raw: string;
  try {
    raw = readFileSync(join(process.cwd(), CONTENT_DIR, path), "utf8");
  } catch {
    return { words: 0, exercises: 0 };
  }

  const exercises = (raw.match(/<DataCampExercise\b/g) ?? []).length;
  const prose = raw
    .replace(/^---[\s\S]*?\n---/, "")
    .replace(/```[\s\S]*?```/g, "")
    // Exercises carry whole programs in their props, so they go first and
    // whole; any other tag is removed on its own, without its contents --
    // a lazy `<X ... />` match ran from one open tag to the next self-closing
    // one and swallowed the prose between them.
    .replace(/<DataCampExercise\b[\s\S]*?\/>/g, "")
    .replace(/<\/?[A-Za-z][^>]*>/g, "")
    .replace(/^import .*$/gm, "");
  const words = prose.split(/\s+/).filter(Boolean).length;
  return { words, exercises };
}

function hasExamFor(slug: string): boolean {
  for (const ext of ["yaml", "yml"]) {
    try {
      readFileSync(join(process.cwd(), EXAMS_DIR, `${slug}.${ext}`));
      return true;
    } catch {
      /* try the next spelling */
    }
  }
  return false;
}

function build(info: CourseInfo): Course | undefined {
  const folder = folderFor(info.slug);
  if (!folder) return undefined;

  const syllabus: SyllabusItem[] = [];
  if (folder.index) {
    syllabus.push({
      kind: "lesson",
      lesson: { url: served(folder.index.url), title: nameOf(folder.index) },
    });
  }
  for (const child of folder.children) {
    if (child.type === "page") {
      syllabus.push({
        kind: "lesson",
        lesson: { url: served(child.url), title: nameOf(child) },
      });
    } else if (child.type === "folder") {
      const lessons = lessonsIn(child);
      if (lessons.length)
        syllabus.push({ kind: "section", title: nameOf(child), lessons });
    }
  }

  const lessons = lessonsIn(folder);
  let words = 0;
  let exercises = 0;
  // Per lesson too, so the syllabus can say how long each one takes -- the
  // question a learner actually has when fitting a lesson into an evening.
  const sized = new Map<string, { minutes: number; exercises: number }>();
  for (const lesson of lessons) {
    const m = measure(lesson.url);
    words += m.words;
    exercises += m.exercises;
    sized.set(lesson.url, {
      minutes: Math.max(1, Math.round(m.words / 200)),
      exercises: m.exercises,
    });
  }
  const withSize = (lesson: Lesson): Lesson => ({ ...lesson, ...sized.get(lesson.url) });
  for (const item of syllabus) {
    if (item.kind === "lesson") item.lesson = withSize(item.lesson);
    else item.lessons = item.lessons.map(withSize);
  }

  const firstLesson =
    info.startAt && lessons.some((l) => l.url === info.startAt)
      ? info.startAt
      : (lessons[0]?.url ?? `/${info.slug}/`);

  return {
    ...info,
    href: `/courses/${info.slug}/`,
    firstLesson,
    lessons: lessons.map(withSize),
    syllabus,
    sectionCount: syllabus.filter((s) => s.kind === "section").length,
    exerciseCount: exercises,
    hours: Math.max(1, Math.ceil(words / 200 / 60)),
    hasExam: hasExamFor(info.slug),
  };
}

let cache: Course[] | undefined;

/** Every catalogued course, in catalogue order. */
export function allCourses(): Course[] {
  if (!cache) {
    cache = COURSES.map(build).filter((c): c is Course => Boolean(c));
  }
  return cache;
}

export function getCourse(slug: string): Course | undefined {
  return allCourses().find((c) => c.slug === slug);
}

/** The course a lesson url belongs to. */
export function courseForUrl(url: string): Course | undefined {
  const slug = url.split("/").filter(Boolean)[0];
  return slug && courseInfo(slug) ? getCourse(slug) : undefined;
}

export function subjectLabel(id: string): string {
  return SUBJECTS.find((s) => s.id === id)?.label ?? id;
}

export const LEVEL_LABEL: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

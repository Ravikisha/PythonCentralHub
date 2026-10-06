import {
  allCourses,
  LEVEL_LABEL,
  subjectLabel,
  type Course,
} from "@/lib/courses";
import type { CourseCardData } from "./CourseCatalog";

/** A course, reduced to what its card shows. */
export function cardData(course: Course): CourseCardData {
  return {
    slug: course.slug,
    title: course.title,
    code: course.code,
    level: course.level,
    levelLabel: LEVEL_LABEL[course.level] ?? course.level,
    subject: course.subject,
    subjectLabel: subjectLabel(course.subject),
    summary: course.summary,
    href: course.href,
    firstLesson: course.firstLesson,
    lessonCount: course.lessons.length,
    lessonUrls: course.lessons.map((l) => l.url),
    exerciseCount: course.exerciseCount,
    hours: course.hours,
    hasExam: course.hasExam,
  };
}

export function catalogCards(): CourseCardData[] {
  return allCourses().map(cardData);
}

/** Course slug -> title, for the client pieces that label a lesson. */
export function courseTitles(): Record<string, string> {
  return Object.fromEntries(allCourses().map((c) => [c.slug, c.title]));
}

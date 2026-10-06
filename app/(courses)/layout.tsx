import { Header } from "@/components/docs/Header";
import { Footer } from "@/components/docs/Footer";
import "@/components/docs/docs.css";
import "@/components/docs/chrome.css";
import "@/components/courses/courses.css";
import "@/components/courses/course-page.css";

/**
 * The catalogue and each course's own page.
 *
 * No lesson sidebar: these pages are about choosing and planning a course,
 * and the syllabus on the page is the table of contents.
 */
export default function CoursesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <main className="courses-main">{children}</main>
      <Footer />
    </>
  );
}

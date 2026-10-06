import { ContentRuntime } from "@/components/docs/ContentRuntime";
import { Footer } from "@/components/docs/Footer";
import "@/components/docs/docs.css";
import "@/components/docs/chrome.css";
import "@/components/courses/courses.css";
/* The in-page Python playground (Run / Edit / Reset on every ```python block)
   and the fullscreen window it and the visualisations open into. Both were
   served as plain <link>s from the Astro footer, which is why the Run buttons
   came over with no size: the markup mounted, the stylesheet never loaded.
   Imported before code.css so the site's own chassis wins where they meet. */
/* Lesson-only stylesheets, moved here from the root layout so pages without
   lessons don't download them. KaTeX's must stay: without it the MathML
   fallback is not hidden and every formula renders twice ("Ax = bAx = b"). */
import "katex/dist/katex.min.css";
import "@/src/styles/viz.css";
import "@/src/styles/dsa-viz.css";
import "@/src/styles/math-viz.css";
import "@/src/styles/dsa-data.css";
import "@/public/styles/python-playground.css";
import "@/public/styles/editor-fullscreen.css";
import "@/components/docs/code.css";
import "@/components/learn/exercise.css";

/**
 * The docs shell.
 *
 * Three columns on a wide screen: the course contents, the page, and what is
 * on this page. The middle column is capped at 72 characters because these
 * pages are read for an hour at a time, and the two side columns are the ones
 * that give way as the screen narrows — contents becomes a drawer below 64rem,
 * the table of contents disappears below 87.5rem.
 *
 * The header, the sidebar and the shell grid are rendered by the page, not
 * here. A layout does not know which page it wraps, so it could only hand the
 * client the whole 1,182-page tree -- which it did, on every page, as most of
 * each page's HTML. The page knows its course and passes just that branch.
 */
export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      {/*
        Everything the content itself needs -- mermaid, p5, the fullscreen
        control, the Python playground -- is loaded per page by ContentRuntime,
        which checks first whether the page has any of that markup.
      */}
      <ContentRuntime />
      {children}
      <Footer />
    </>
  );
}

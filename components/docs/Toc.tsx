"use client";

import {
  Children,
  cloneElement,
  isValidElement,
  useEffect,
  useState,
} from "react";
/**
 * One heading, as the content pipeline reports it. Declared here rather than
 * imported: the type lives in an internal chunk of fumadocs-core with no
 * public entry point, and this shape is the stable part of the contract.
 */
export interface TOCItemType {
  title: React.ReactNode;
  url: string;
  depth: number;
}

/**
 * Strip links out of a heading before it goes in the table of contents.
 *
 * Headings may contain links -- one string page ends with an h2 that links to
 * docs.python.org -- and the TOC entry is itself a link, so rendering the
 * heading verbatim nested an <a> inside an <a>. The browser hoists the inner
 * one out, the server markup and the client tree stop matching, and the whole
 * page re-renders on a hydration error. Everything else in the heading (code
 * spans, emphasis) is kept, since it carries meaning in this contents list.
 */
function unlink(node: React.ReactNode): React.ReactNode {
  return Children.map(node, (child) => {
    if (!isValidElement(child)) return child;

    const children = (child.props as { children?: React.ReactNode }).children;

    // Anchors are unwrapped whatever they hold -- including the empty `#` link
    // this site adds to every section heading. Checking for children first let
    // that empty anchor through, and hydration failed on an <a> in an <a>.
    if (child.type === "a") return <>{unlink(children)}</>;

    if (children === undefined) return child; // void elements take no children

    return cloneElement(child, undefined, unlink(children));
  });
}

/**
 * On this page.
 *
 * Tracks the heading currently being read with an IntersectionObserver rather
 * than scroll maths: the pages here run long and carry tall embedded exercises,
 * so scroll position is a poor proxy for what is on screen.
 */
export function Toc({ items }: { items: TOCItemType[] }) {
  const [active, setActive] = useState<string>("");

  useEffect(() => {
    if (items.length === 0) return;

    const headings = items
      .map((i) => document.getElementById(i.url.replace(/^#/, "")))
      .filter((el): el is HTMLElement => el !== null);

    if (headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        // The topmost heading that is on screen wins. Taking the last
        // intersecting entry instead makes the highlight jump to the bottom of
        // a long section as soon as it scrolls into view.
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

        if (visible[0]) setActive(`#${visible[0].target.id}`);
      },
      // Bias the band to the upper third: a heading is "current" once it has
      // reached the top of the viewport, not when it is halfway down.
      { rootMargin: "-10% 0px -70% 0px", threshold: 0 },
    );

    headings.forEach((h) => observer.observe(h));
    return () => observer.disconnect();
  }, [items]);

  if (items.length === 0) return null;

  return (
    <nav className="toc" aria-label="On this page">
      <p className="toc__title">On this page</p>
      <ul className="toc__list">
        {items.map((item) => (
          <li key={item.url}>
            <a
              className="toc__link"
              href={item.url}
              data-depth={item.depth}
              data-active={active === item.url ? "true" : undefined}
            >
              {unlink(item.title)}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Toc;

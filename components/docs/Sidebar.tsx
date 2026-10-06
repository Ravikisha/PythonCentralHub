"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { Root, Node } from "fumadocs-core/page-tree";
import { courseInfo } from "@/lib/courses.data.mjs";

/**
 * The progress spine.
 *
 * Not a file tree: this site is a course of 1192 pages in numbered phases, and
 * the reader's real question is where they are in the sequence and how much is
 * left. So every row carries the `>>>` marker in a fixed gutter, coloured by
 * state, and every group carries a count.
 *
 * Completion is read from the same localStorage store the rest of the progress
 * system uses, so the sidebar agrees with the dashboard without a round trip.
 * It is read after mount, never during render: the markup is prerendered and
 * identical for everyone, and reading storage during render would desynchronise
 * hydration on all 1192 pages.
 */
export function Sidebar({ tree }: { tree: Root }) {
  const pathname = usePathname();
  const [done, setDone] = useState<Set<string>>(new Set());
  const nav = useRef<HTMLElement | null>(null);

  /**
   * Scroll the current page into view inside the contents.
   *
   * The pane is 1,200 links long and its own scroller, so arriving deep in a
   * module -- from search, or a shared link -- showed the top of the list with
   * no sign of where you were. The pane stays still when the link is already
   * visible.
   *
   * Not `scrollIntoView`: that scrolls every ancestor, the window included, and
   * pushed the breadcrumb under the sticky header on every page load.
   */
  useEffect(() => {
    const active = nav.current?.querySelector<HTMLElement>(
      '[aria-current="page"]',
    );
    let pane = nav.current as HTMLElement | null;
    while (pane && !/(auto|scroll)/.test(getComputedStyle(pane).overflowY)) {
      pane = pane.parentElement;
    }
    if (!active || !pane || pane === document.documentElement) return;

    const box = pane.getBoundingClientRect();
    const link = active.getBoundingClientRect();
    if (link.top >= box.top && link.bottom <= box.bottom) return;
    pane.scrollTop +=
      link.top - box.top - (pane.clientHeight - link.height) / 2;
  }, [pathname]);

  useEffect(() => {
    let cancelled = false;

    let stop: (() => void) | undefined;

    (async () => {
      try {
        const { read, subscribe } = await import("@/src/lib/progress/local");
        const apply = (state: ReturnType<typeof read>) => {
          if (!cancelled) setDone(new Set(Object.values(state.modules).flat()));
        };
        apply(read());
        // The sidebar lives in the layout and outlasts every page, so it has
        // to hear about changes: "Mark as complete" and a cloud sync used to
        // leave its marks and counts stale until a full reload.
        if (cancelled) return;
        stop = subscribe(apply);
      } catch {
        /* progress is optional; the sidebar still navigates without it */
      }
    })();

    return () => {
      cancelled = true;
      stop?.();
    };
  }, []);

  // Inside a course, the contents are that course's lessons only: a learner
  // in Machine Learning has no use for the Flask syllabus beside it, and the
  // whole catalogue is one link away.
  const current = tree.children.find(
    (node) =>
      node.type === "folder" &&
      collectPages(node).some((u) => pathname === u || pathname === `${u}/`),
  );
  const slug =
    current && current.type === "folder"
      ? (collectPages(current)[0] ?? "").split("/").filter(Boolean)[0]
      : undefined;
  const course = slug ? courseInfo(slug) : undefined;

  if (current && current.type === "folder" && course) {
    const pages = collectPages(current);
    const finished = pages.filter((p) => done.has(pageIdFromUrl(p))).length;

    return (
      <nav
        className="side"
        aria-label={`${course.title} lessons`}
        data-subject={course.subject}
        ref={nav}
      >
        <Link className="side__all" href="/courses/">
          All courses
        </Link>

        <Link
          className="side__course"
          href={`/courses/${course.slug}/`}
          data-subject={course.subject}
        >
          <span className="side__course-code">{course.code}</span>
          <span className="side__course-title">{course.title}</span>
          <span className="side__course-progress">
            <span className="meter" aria-hidden="true">
              <span
                style={{
                  width: `${pages.length ? Math.round((finished / pages.length) * 100) : 0}%`,
                }}
              />
            </span>
            <span>
              {finished} of {pages.length} done
            </span>
          </span>
        </Link>

        <ul className="side__list side__list--course">
          {current.index ? (
            <TreeNode
              node={current.index}
              pathname={pathname}
              done={done}
              depth={1}
            />
          ) : null}
          {current.children.map((node, i) => (
            <TreeNode
              key={i}
              node={node}
              pathname={pathname}
              done={done}
              depth={1}
            />
          ))}
        </ul>
      </nav>
    );
  }

  return (
    <nav className="side" aria-label="Course contents" ref={nav}>
      {tree.children.map((node, i) => (
        <TreeNode
          key={i}
          node={node}
          pathname={pathname}
          done={done}
          depth={0}
        />
      ))}
    </nav>
  );
}

function pageIdFromUrl(url: string): string {
  return url.replace(/^\/|\/$/g, "").toLowerCase();
}

function TreeNode({
  node,
  pathname,
  done,
  depth,
}: {
  node: Node;
  pathname: string;
  done: Set<string>;
  depth: number;
}) {
  if (node.type === "separator") {
    return null;
  }

  if (node.type === "page") {
    const id = pageIdFromUrl(node.url);
    const current = pathname === node.url || pathname === `${node.url}/`;
    const state = current ? "current" : done.has(id) ? "done" : undefined;

    return (
      <li>
        <Link
          className="side__link"
          href={node.url}
          aria-current={current ? "page" : undefined}
        >
          <span className="spine" data-state={state} aria-hidden="true" />
          <span>{node.name}</span>
        </Link>
      </li>
    );
  }

  // Folder: a module at the top level, a phase below it.
  const pages = collectPages(node);
  const finished = pages.filter((p) => done.has(pageIdFromUrl(p))).length;
  const contains = pages.some((u) => pathname === u || pathname === `${u}/`);

  const state =
    finished === pages.length && pages.length > 0
      ? "done"
      : contains || finished > 0
        ? "started"
        : undefined;

  return (
    <Folder
      depth={depth}
      name={node.name}
      state={state}
      finished={finished}
      total={pages.length}
      // A folder holding the current page opens itself; the rest stay shut,
      // because 1192 links expanded at once is not a navigation aid.
      startOpen={contains}
    >
      {node.children.map((child, i) => (
        <TreeNode
          key={i}
          node={child}
          pathname={pathname}
          done={done}
          depth={depth + 1}
        />
      ))}
    </Folder>
  );
}

/**
 * A collapsible group.
 *
 * `open` is held in state rather than driven straight from the prop: passing
 * it every render makes the element controlled, and the reader's own clicks
 * get reverted on the next render.
 */
function Folder({
  depth,
  name,
  state,
  finished,
  total,
  startOpen,
  children,
}: {
  depth: number;
  name: React.ReactNode;
  state?: string;
  finished: number;
  total: number;
  startOpen: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(startOpen);

  // Following a link into a closed group should reveal it.
  useEffect(() => {
    if (startOpen) setOpen(true);
  }, [startOpen]);

  return (
    <details
      className={depth === 0 ? "side__module" : "side__phase"}
      open={open}
      onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}
    >
      <summary className="side__summary">
        <span className="spine" data-state={state} aria-hidden="true" />
        <span className="side__name">{name}</span>
        {total > 0 ? (
          <span className="side__count">
            {finished}/{total}
          </span>
        ) : null}

        {/* How far through the module you are, on the row itself. The count
            beside it is the exact number; this is the one you read at a
            glance while scrolling past twelve of them. */}
        {depth === 0 && total > 0 ? (
          <span
            className="side__meter"
            aria-hidden="true"
            style={
              {
                "--fill": `${Math.round((finished / total) * 100)}%`,
              } as React.CSSProperties
            }
          />
        ) : null}
      </summary>

      <ul className="side__list">{children}</ul>
    </details>
  );
}

/** Every page URL under a folder, including nested phases. */
function collectPages(node: Node): string[] {
  if (node.type === "page") return [node.url];
  if (node.type === "folder") return node.children.flatMap(collectPages);
  return [];
}

export default Sidebar;

"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Bookmark, Download, NotebookPen, Trash2 } from "lucide-react";
import {
  read,
  setBookmark,
  setNote,
  subscribe,
  type ProgressState,
} from "@/src/lib/progress/local";
import { moduleOf } from "@/src/lib/progress/ids";
import { courseInfo } from "@/lib/courses.data.mjs";
import { SITE_NAME, SITE_SLUG } from "@/lib/site";

/** "tutorials/python-lists/list-slicing" -> "List slicing". */
function titleOf(pageId: string): string {
  const last = pageId.split("/").pop() ?? pageId;
  const words = last.replace(/-/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function courseTitle(slug: string): string {
  return courseInfo(slug)?.title ?? slug.replace(/-/g, " ");
}

interface Entry {
  pageId: string;
  bookmarked: boolean;
  note: string;
}

/**
 * Bookmarks and notes together, grouped by course.
 *
 * Reads the same local store the lessons write, so it works without an
 * account and repaints when another tab changes something. Removing here is
 * the same call the lesson page makes, so it syncs the same way.
 */
export function Saved() {
  const [state, setState] = useState<ProgressState | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    setState(read());
    return subscribe(setState);
  }, []);

  const groups = useMemo(() => {
    if (!state) return [];
    const byPage = new Map<string, Entry>();
    for (const pageId of state.bookmarks) {
      byPage.set(pageId, { pageId, bookmarked: true, note: "" });
    }
    for (const [pageId, note] of Object.entries(state.notes)) {
      const entry = byPage.get(pageId) ?? { pageId, bookmarked: false, note: "" };
      entry.note = note;
      byPage.set(pageId, entry);
    }

    const needle = filter.trim().toLowerCase();
    const courses = new Map<string, Entry[]>();
    for (const entry of byPage.values()) {
      if (
        needle &&
        !titleOf(entry.pageId).toLowerCase().includes(needle) &&
        !entry.note.toLowerCase().includes(needle) &&
        !courseTitle(moduleOf(entry.pageId)).toLowerCase().includes(needle)
      ) {
        continue;
      }
      const slug = moduleOf(entry.pageId);
      courses.set(slug, [...(courses.get(slug) ?? []), entry]);
    }
    return [...courses.entries()]
      .map(([slug, entries]) => ({
        slug,
        title: courseTitle(slug),
        entries: entries.sort((a, b) => a.pageId.localeCompare(b.pageId)),
      }))
      .sort((a, b) => a.title.localeCompare(b.title));
  }, [state, filter]);

  if (!state) return <p className="app__loading">Loading…</p>;

  const total = new Set([...state.bookmarks, ...Object.keys(state.notes)]).size;
  const noteCount = Object.keys(state.notes).length;

  function exportNotes() {
    if (!state) return;
    const lines = [`# My ${SITE_NAME} notes`, ""];
    const entries = Object.entries(state.notes).sort(([a], [b]) => a.localeCompare(b));
    let course = "";
    for (const [pageId, note] of entries) {
      const slug = moduleOf(pageId);
      if (slug !== course) {
        course = slug;
        lines.push(`## ${courseTitle(slug)}`, "");
      }
      lines.push(`### ${titleOf(pageId)}`, "", `${window.location.origin}/${pageId}/`, "", note, "");
    }
    const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/markdown" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${SITE_SLUG}-notes.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  if (total === 0) {
    return (
      <div className="saved__empty">
        <p>
          Nothing saved yet. On any lesson, use <strong>Bookmark</strong> to keep it for
          later, or <strong>Add a private note</strong> at the end of the page. Both
          collect here.
        </p>
        <p>
          <Link className="button button--primary" href="/courses/">
            Browse courses
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="saved">
      <div className="saved__tools">
        <input
          type="search"
          className="saved__filter"
          placeholder="Filter by lesson, course or note text"
          aria-label="Filter saved lessons"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        {noteCount ? (
          <button type="button" className="button" onClick={exportNotes}>
            <Download className="size-4" aria-hidden="true" />
            Download notes (.md)
          </button>
        ) : null}
      </div>

      <p className="saved__count">
        {state.bookmarks.length} bookmarked · {noteCount} with notes
      </p>

      {groups.length === 0 ? <p className="saved__count">Nothing matches “{filter}”.</p> : null}

      {groups.map((group) => (
        <section
          key={group.slug}
          className="saved__course"
          data-subject={courseInfo(group.slug)?.subject}
        >
          <h2>
            {courseInfo(group.slug)?.code ? (
              <span className="saved__code">{courseInfo(group.slug)?.code}</span>
            ) : null}
            {group.title}
          </h2>
          <ul>
            {group.entries.map((entry) => (
              <li key={entry.pageId} className="saved__item">
                <div className="saved__head">
                  <Link href={`/${entry.pageId}/`}>{titleOf(entry.pageId)}</Link>
                  <span className="saved__marks">
                    {entry.bookmarked ? (
                      <button
                        type="button"
                        className="saved__remove"
                        onClick={() => setBookmark(entry.pageId, false)}
                        title="Remove bookmark"
                      >
                        <Bookmark className="size-4" aria-hidden="true" />
                        <span>Unbookmark</span>
                      </button>
                    ) : null}
                    {entry.note ? (
                      <button
                        type="button"
                        className="saved__remove"
                        onClick={() => {
                          if (window.confirm("Delete this note? This cannot be undone.")) {
                            setNote(entry.pageId, "");
                          }
                        }}
                        title="Delete note"
                      >
                        <Trash2 className="size-4" aria-hidden="true" />
                        <span>Delete note</span>
                      </button>
                    ) : null}
                  </span>
                </div>
                {entry.note ? (
                  <p className="saved__note">
                    <NotebookPen className="size-4" aria-hidden="true" />
                    <span>{entry.note}</span>
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

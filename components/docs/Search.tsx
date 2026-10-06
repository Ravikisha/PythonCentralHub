"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { courseInfo } from "@/lib/courses.data.mjs";
import { Search as SearchIcon } from "lucide-react";
import dynamic from "next/dynamic";
import type { Entry, TextHit } from "./SearchDialog";
import { ShortcutKey } from "./ShortcutKey";

const SearchDialog = dynamic(() => import("./SearchDialog"), { ssr: false });

/**
 * ⌘K search over page titles and descriptions.
 *
 * The index is fetched on first open, not on page load: it is 346 KB, and most
 * readers arrive to read one page rather than to search. After that it is
 * cached for the session.
 *
 * Scoring is deliberately simple and explainable — a title match beats a
 * module match beats a description match, and a prefix beats a mid-word hit.
 * People search for the name of a topic, and ranking that predictably matters
 * more here than a cleverer similarity metric.
 *
 * The dialog is shadcn's Command, with its own filtering switched off
 * (`shouldFilter={false}`): cmdk's fuzzy matcher would re-rank what the
 * scoring below has already ordered, and on 1,183 entries the two disagree.
 */
export function Search() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [everOpened, setEverOpened] = useState(false);
  useEffect(() => {
    if (open) setEverOpened(true);
  }, [open]);
  const [query, setQuery] = useState("");
  const [entries, setEntries] = useState<Entry[] | null>(null);

  const load = useCallback(async () => {
    if (entries) return;
    try {
      const res = await fetch("/search-index.json");
      setEntries((await res.json()) as Entry[]);
    } catch {
      setEntries([]);
    }
  }, [entries]);

  // ⌘K / Ctrl-K from anywhere.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key.toLowerCase() === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((v) => !v);
        void load();
      }
    }
    // Capture phase: a code editor on the page (the playground, an exercise)
    // handles Ctrl-K itself and stops it before it bubbles to the window.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [load]);

  // Inside a course, its lessons rank first and the search can be narrowed
  // to it: someone halfway through Machine Learning typing "regression"
  // wants that course's lesson before the Data Analytics one.
  const pathname = usePathname();
  const course = pathname.split("/").filter(Boolean)[0] ?? "";
  const courseTitle = courseInfo(course)?.title;
  const [onlyCourse, setOnlyCourse] = useState(false);

  const { results, approximate } = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q || !entries) return { results: [] as Entry[], approximate: false };
    const inCourse = (e: Entry) =>
      Boolean(courseTitle) && e.u.startsWith(`/${course}/`);

    // Match on every word, not the whole phrase. People type "string slicing"
    // for a page called "Python String Slicing", and whole-phrase matching
    // finds nothing for any query whose words are not adjacent in the title.
    const tokens = q.split(/\s+/).filter(Boolean);

    /**
     * Per-token weight: title, then a section heading inside the lesson, then
     * the course name, then the description. Headings are what make "list
     * comprehension" find the Lists lesson, whose title says only "Lists".
     */
    function weigh(
      token: string,
      title: string,
      heads: string,
      where: string,
      desc: string,
    ) {
      if (title.includes(token)) return 40;
      if (heads.includes(token)) return 20;
      if (where.includes(token)) return 12;
      if (desc.includes(token)) return 6;
      return 0;
    }

    const all: { e: Entry; score: number; hits: number }[] = [];

    for (const e of entries) {
      if (onlyCourse && !inCourse(e)) continue;
      const title = e.t.toLowerCase();
      const where = e.m.toLowerCase();
      const desc = e.d.toLowerCase();
      const heads = (e.h ?? "").toLowerCase();

      let score = 0;
      let hits = 0;
      for (const token of tokens) {
        const w = weigh(token, title, heads, where, desc);
        if (w) {
          score += w;
          hits++;
        }
      }
      if (!hits) continue;

      // An exact or leading match on the whole phrase still wins outright.
      if (heads.includes(q)) score += 10;
      if (title === q) score += 60;
      else if (title.startsWith(q)) score += 30;
      else if (title.includes(q)) score += 15;

      if (inCourse(e)) score += 20;
      all.push({ e, score, hits });
    }

    const rank = (a: (typeof all)[number], b: (typeof all)[number]) =>
      b.score - a.score || a.e.t.length - b.e.t.length;

    const exact = all.filter((x) => x.hits === tokens.length).sort(rank);
    if (exact.length)
      return {
        results: exact.slice(0, 12).map((x) => x.e),
        approximate: false,
      };

    // Nothing matched every word. Rather than a dead end, offer the pages that
    // matched some of them — the site has a "Python String Slicing" page but no
    // "list slicing" one, and the reader who typed the latter still wants the
    // list pages. Fewer of them, and said to be approximate.
    const partial = all
      .sort((a, b) => b.hits - a.hits || rank(a, b))
      .slice(0, 6);
    return {
      results: partial.map((x) => x.e),
      approximate: partial.length > 0,
    };
  }, [query, entries, onlyCourse, course, courseTitle]);

  // The lesson text, searched on the server: the browser index holds titles
  // and headings only. Debounced, and only for queries long enough to mean
  // something; a stale answer is dropped if the query moved on.
  const [textHits, setTextHits] = useState<TextHit[]>([]);
  useEffect(() => {
    const q = query.trim();
    if (!open || q.length < 3) {
      setTextHits([]);
      return;
    }
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams({ q });
      if (onlyCourse && courseTitle) params.set("course", course);
      fetch(`/api/search/?${params}`, { signal: controller.signal })
        .then((res) => (res.ok ? res.json() : { results: [] }))
        .then((data: { results?: TextHit[] }) => setTextHits(data.results ?? []))
        .catch(() => {});
    }, 300);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [query, open, onlyCourse, course, courseTitle]);

  function go(url: string) {
    setOpen(false);
    router.push(url);
  }

  return (
    <>
      <button
        type="button"
        className="search-trigger"
        aria-label="Search courses"
        onClick={() => {
          setOpen(true);
          void load();
        }}
      >
        <SearchIcon className="size-[15px]" aria-hidden="true" />
        <span>Search courses</span>
        <ShortcutKey />
      </button>

      {/* The dialog (cmdk + Radix, ~125 KB) loads the first time search is
          opened rather than on every page: most readers never open it. */}
      {everOpened ? (
        <SearchDialog
          open={open}
          onOpenChange={(next) => {
            setOpen(next);
            if (!next) setQuery("");
          }}
          query={query}
          onQuery={setQuery}
          entries={entries}
          results={results}
          textHits={textHits.filter((h) => !results.some((r) => r.u === h.u))}
          approximate={approximate}
          go={go}
          courseTitle={courseTitle}
          onlyCourse={onlyCourse}
          onOnlyCourse={setOnlyCourse}
        />
      ) : null}
    </>
  );
}

export default Search;

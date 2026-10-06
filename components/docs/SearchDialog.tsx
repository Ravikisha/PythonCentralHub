"use client";

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

export interface Entry {
  /** title */ t: string;
  /** description */ d: string;
  /** url */ u: string;
  /** module */ m: string;
  /** the lesson's section headings, " | "-separated */ h?: string;
}

/** A lesson whose text matched, from /api/search/. */
export interface TextHit {
  u: string;
  t: string;
  m: string;
  /** The passage around the match. */
  s: string;
}

/** The heading that matched the query, when the title itself did not. */
function matchedHeading(entry: Entry, query: string): string | undefined {
  const q = query.trim().toLowerCase();
  if (!q || !entry.h || entry.t.toLowerCase().includes(q)) return undefined;
  const words = q.split(/\s+/);
  return entry.h
    .split(" | ")
    .find((h) => words.every((w) => h.toLowerCase().includes(w)));
}

/**
 * The search dialog itself. Split from Search.tsx and loaded on first open:
 * cmdk and the Radix dialog are the largest thing in the header, and most
 * readers never search.
 */
export default function SearchDialog({
  open,
  onOpenChange,
  query,
  onQuery,
  entries,
  results,
  textHits,
  approximate,
  go,
  courseTitle,
  onlyCourse,
  onOnlyCourse,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  query: string;
  onQuery: (q: string) => void;
  entries: Entry[] | null;
  results: Entry[];
  /** Lessons matched in their text, minus any already listed above. */
  textHits: TextHit[];
  approximate: boolean;
  go: (url: string) => void;
  /** Set when the reader is inside a course. */
  courseTitle?: string;
  onlyCourse: boolean;
  onOnlyCourse: (on: boolean) => void;
}) {
  return (
  <CommandDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Search"
      description="Search every page by title, and lesson text"
      shouldFilter={false}
      className="sd"
    >
      <CommandInput
        placeholder={
          entries
            ? `Search ${entries.length.toLocaleString()} pages by title`
            : "Search the course"
        }
        value={query}
        onValueChange={onQuery}
      />

      {courseTitle ? (
        <div className="sd__scope" role="group" aria-label="Search in">
          <button
            type="button"
            aria-pressed={!onlyCourse}
            onClick={() => onOnlyCourse(false)}
          >
            All courses
          </button>
          <button
            type="button"
            aria-pressed={onlyCourse}
            onClick={() => onOnlyCourse(true)}
          >
            Only {courseTitle}
          </button>
        </div>
      ) : null}

      <CommandList>
        {query && results.length === 0 && textHits.length === 0 ? (
          <CommandEmpty>
            {entries === null
              ? "Loading the index…"
              : `No page matches “${query}”. Try fewer words, or the topic's own name.`}
          </CommandEmpty>
        ) : null}

        {results.length > 0 ? (
          <CommandGroup
            heading={
              approximate
                ? "No page covers all of that. Closest pages:"
                : "Pages"
            }
          >
            {results.map((r) => (
              <CommandItem key={r.u} value={r.u} onSelect={() => go(r.u)}>
                <span className="sd__title">{r.t}</span>
                {r.m ? <span className="sd__where">{r.m}</span> : null}
                {matchedHeading(r, query) ? (
                  <span className="sd__heading">{matchedHeading(r, query)}</span>
                ) : null}
              </CommandItem>
            ))}
          </CommandGroup>
        ) : null}

        {textHits.length > 0 ? (
          <CommandGroup heading="In lesson text">
            {textHits.map((r) => (
              <CommandItem key={`text:${r.u}`} value={`text:${r.u}`} onSelect={() => go(r.u)}>
                <span className="sd__title">{r.t}</span>
                {r.m ? <span className="sd__where">{r.m}</span> : null}
                <span className="sd__snippet">{r.s}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        ) : null}
      </CommandList>
    </CommandDialog>
  );
}

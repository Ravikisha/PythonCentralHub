"use client";

import { usePathname } from "next/navigation";
import { Bookmark, Check, PenLine } from "lucide-react";
import { toast } from "@/components/ui/sonner";
import { Textarea } from "@/components/ui/textarea";
import { useEffect, useRef, useState } from "react";
import { pageIdOf } from "@/src/lib/progress/ids";
import {
  isComplete,
  setComplete,
  isBookmarked,
  setBookmark,
  setNote,
  getNote,
  setLastPage,
  recordQuiz,
  recordExercise,
  subscribe,
  read,
} from "@/src/lib/progress/local";
import { readHint } from "@/src/lib/auth/hint";
import { t } from "@/lib/strings";

/**
 * The per-page progress controls: mark complete, bookmark, private note.
 *
 * Also the page-level progress host. It records the "continue where you left
 * off" pointer and listens for finished quizzes, because doing that here keeps
 * it to one small component per page rather than three.
 *
 * Renders nothing on pages that are not curriculum -- the landing page, the
 * account pages, the policy page. `pageIdOf` returns null for those.
 */
export function PageProgress({ title }: { title: string }) {
  const pathname = usePathname();
  const pageId = pageIdOf(pathname);

  if (!pageId) return null;
  return (
    <Controls key={pageId} pageId={pageId} pathname={pathname} title={title} />
  );
}

function Controls({
  pageId,
  pathname,
  title,
}: {
  pageId: string;
  pathname: string;
  title: string;
}) {
  const [done, setDone] = useState(false);
  const [saved, setSaved] = useState(false);
  const [note, setNoteText] = useState("");
  const [noteOpen, setNoteOpen] = useState(false);
  const [noteSaved, setNoteSaved] = useState(false);
  const noteTimer = useRef<number | undefined>(undefined);
  /** An edit not yet saved, so leaving the page can still save it. */
  const pendingNote = useRef<{ pageId: string; value: string } | null>(null);
  /** True only when the reader opened the note themselves this visit. */
  const [noteOpenedByUser, setNoteOpenedByUser] = useState(false);

  // The store is localStorage, which the server cannot read, so the first
  // client render is what fills these in. Keeping the initial state false on
  // both sides is what stops the button flickering through a wrong label.
  useEffect(() => {
    function paint() {
      setDone(isComplete(pageId));
      setSaved(isBookmarked(pageId));
    }

    paint();
    const existing = getNote(pageId);
    setNoteText(existing);
    // A page that already has a note opens with it visible -- otherwise the
    // note is invisible until you think to look for it.
    setNoteOpen(Boolean(existing));

    // Keeps the buttons honest when progress changes in another tab.
    return subscribe(paint);
  }, [pageId]);

  /* ---- continue-where-you-left-off pointer ---- */
  useEffect(() => {
    setLastPage(pageId, pathname, title);
  }, [pageId, pathname, title]);

  /* ---- quiz results ----
     The quiz component announces a finished quiz rather than writing progress
     itself, so it stays free of any storage dependency. */
  useEffect(() => {
    function onQuiz(event: Event) {
      const detail = (
        event as CustomEvent<{
          ordinal: number;
          correct: number;
          total: number;
        }>
      ).detail;
      if (detail)
        recordQuiz(pageId, detail.ordinal, detail.correct, detail.total);
    }

    document.addEventListener("pch:quiz-complete", onQuiz);
    return () => document.removeEventListener("pch:quiz-complete", onQuiz);
  }, [pageId]);

  /* ---- exercise passes ---- */
  useEffect(() => {
    function onExercise(event: Event) {
      const ordinal = (event as CustomEvent<{ ordinal: number }>).detail?.ordinal;
      if (pageId && typeof ordinal === "number" && ordinal >= 0) recordExercise(pageId, ordinal);
    }
    document.addEventListener("pch:exercise-passed", onExercise);
    return () => document.removeEventListener("pch:exercise-passed", onExercise);
  }, [pageId]);

  /* ---- first load on a new device ----
     A signed-in learner arriving on a device that has never held their
     progress would otherwise see an empty sidebar until they happened to open
     the dashboard. Pull once, at idle, and only for a real account -- a
     guest's progress lives only in this browser, so there is nothing in the
     cloud to pull. `hydrateOnce` is a no-op afterwards. */
  useEffect(() => {
    const hint = readHint();
    if (!hint || hint.anon || read().hydrated) return;

    const hydrate = async () => {
      try {
        const { hydrateOnce } = await import("@/src/lib/progress/sync");
        await hydrateOnce(); // repaints through the store's subscribers
      } catch (err) {
        console.warn("[progress] hydrate deferred:", err);
      }
    };

    const idle =
      typeof window.requestIdleCallback === "function"
        ? window.requestIdleCallback(() => void hydrate(), { timeout: 6000 })
        : window.setTimeout(() => void hydrate(), 2500);

    return () => {
      if (
        typeof window.cancelIdleCallback === "function" &&
        typeof idle === "number"
      ) {
        window.cancelIdleCallback(idle);
      }
    };
  }, []);

  /* ---- private note ----
     Debounced rather than saved per keystroke: each save is a localStorage
     write plus, for a signed-in learner, a queued Firestore write. */
  function editNote(value: string) {
    setNoteText(value);
    setNoteSaved(false);
    if (!pageId) return;
    pendingNote.current = { pageId, value };
    window.clearTimeout(noteTimer.current);
    noteTimer.current = window.setTimeout(() => {
      setNote(pageId, value);
      pendingNote.current = null;
      setNoteSaved(true);
    }, 700);
  }

  // Leaving the page saves what is pending. Cleanup used to cancel the timer
  // instead, so the last 0.7 s of typing was lost to a quick "Next".
  useEffect(
    () => () => {
      window.clearTimeout(noteTimer.current);
      const pending = pendingNote.current;
      if (pending) setNote(pending.pageId, pending.value);
    },
    [],
  );

  return (
    <>
      <div className="pch-progress">
        {/* The one bold element on a content page: a sticker button that
            presses into its own shadow, and whose marker turns from the `>>>`
            prompt into a tick once the page is done. */}
        <button
          type="button"
          className="pch-progress__complete sticker"
          aria-pressed={done}
          onClick={() => {
            const next = !done;
            setComplete(pageId, next);
            setDone(next);
            if (next)
              toast.success(t("pch.progressDone"), { description: title });
          }}
        >
          <span className="pch-progress__mark" aria-hidden="true">
            {done ? (
              <Check className="size-4" strokeWidth={3} />
            ) : (
              <span>&gt;&gt;&gt;</span>
            )}
          </span>
          <span>{done ? t("pch.progressDone") : t("pch.progressMark")}</span>
        </button>

        <button
          type="button"
          className="pch-progress__note-toggle"
          aria-expanded={noteOpen}
          data-has={String(Boolean(note.trim()))}
          title={t("pch.noteAdd")}
          onClick={() => {
            setNoteOpen((v) => !v);
            setNoteOpenedByUser(true);
          }}
        >
          <PenLine className="size-4" aria-hidden="true" />
          <span className="pch-progress__sr">{t("pch.noteAdd")}</span>
        </button>

        <button
          type="button"
          className="pch-progress__bookmark"
          aria-pressed={saved}
          title={
            saved ? t("pch.progressBookmarked") : t("pch.progressBookmark")
          }
          onClick={() => {
            setBookmark(pageId, !saved);
            setSaved(!saved);
          }}
        >
          <Bookmark
            className="size-4"
            aria-hidden="true"
            fill={saved ? "currentColor" : "none"}
          />
          <span className="pch-progress__sr">{t("pch.progressBookmark")}</span>
        </button>
      </div>

      {noteOpen ? (
        <div className="pch-note">
          <label className="pch-note__label" htmlFor="pch-note-body">
            {t("pch.noteLabel")}
          </label>
          <Textarea
            id="pch-note-body"
            className="pch-note__body"
            rows={4}
            maxLength={4000}
            placeholder={t("pch.notePlaceholder")}
            value={note}
            // Only when the reader opened it: a page that loads with an
            // existing note shown used to jump to it and take the focus.
            autoFocus={noteOpenedByUser}
            onChange={(e) => editNote(e.target.value)}
          />
          <p className="pch-note__state" aria-live="polite">
            {noteSaved ? t("pch.noteSaved") : ""}
          </p>
        </div>
      ) : null}
    </>
  );
}

export default PageProgress;

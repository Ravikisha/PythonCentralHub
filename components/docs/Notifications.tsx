"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Bell, X } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  currentStreak,
  getLastPage,
  read,
  subscribe,
  type ProgressState,
} from "@/src/lib/progress/local";
import { today } from "@/src/lib/progress/ids";

interface Notice {
  /** Stable for as long as the notice means the same thing; dismissals key on it. */
  id: string;
  text: string;
  href: string;
}

interface ManifestModule {
  slug: string;
  label: string;
  count: number;
  hasExam?: boolean;
  course?: boolean;
  href?: string;
}

const DISMISSED_KEY = "pch-notices-dismissed";
/** Matches REQUIRED_COMPLETION in lib/server/admin.ts. */
const CERTIFICATE_SHARE = 0.9;

function readDismissed(): Record<string, number> {
  try {
    return JSON.parse(localStorage.getItem(DISMISSED_KEY) ?? "{}") as Record<string, number>;
  } catch {
    return {};
  }
}

/**
 * What is worth telling the learner right now, worked out from their own
 * progress: a streak about to lapse, a course within reach of its
 * certificate, a lesson left half-way.
 *
 * Derived rather than delivered: there is no notification store, nothing is
 * sent anywhere, and it works the same for guests. A dismissed notice stays
 * dismissed until its meaning changes (the streak one carries the date, so it
 * can come back tomorrow).
 */
function derive(state: ProgressState, modules: ManifestModule[]): Notice[] {
  const notices: Notice[] = [];
  const day = today();
  const last = getLastPage();

  const streak = currentStreak(state);
  if (streak >= 2 && state.streak.last !== day) {
    notices.push({
      id: `streak:${day}`,
      text: `Keep your ${streak}-day streak: finish a lesson today.`,
      href: last?.href ?? "/dashboard/",
    });
  }

  for (const slug of state.enrolled ?? []) {
    const mod = modules.find((m) => m.slug === slug);
    if (!mod?.count) continue;
    const done = (state.modules[slug] ?? []).length;
    const needed = Math.ceil(mod.count * CERTIFICATE_SHARE);
    const href = mod.href ?? `/courses/${slug}/`;
    if (done >= needed) {
      notices.push({
        id: `certificate:${slug}`,
        text: mod.hasExam
          ? `${mod.label}: you can take the final assessment for your certificate.`
          : `${mod.label}: your certificate is ready to claim.`,
        href,
      });
    } else if (done > 0 && needed - done <= 5) {
      notices.push({
        id: `almost:${slug}:${needed - done}`,
        text: `${mod.label}: ${needed - done} more ${needed - done === 1 ? "lesson" : "lessons"} to the certificate.`,
        href,
      });
    }
  }

  if (last && Date.now() - last.at > 3 * 24 * 60 * 60 * 1000) {
    notices.push({
      id: `resume:${last.pageId}`,
      text: `Pick up where you left off: ${last.title}.`,
      href: last.href,
    });
  }

  return notices;
}

export function Notifications() {
  const [state, setState] = useState<ProgressState | null>(null);
  const [modules, setModules] = useState<ManifestModule[]>([]);
  const [dismissed, setDismissed] = useState<Record<string, number>>({});

  useEffect(() => {
    setState(read());
    setDismissed(readDismissed());
    return subscribe(setState);
  }, []);

  // Course sizes, fetched only for a learner who has taken a course up -- a
  // first-time visitor has nothing to be told and costs no request.
  const hasCourses = Boolean(state?.enrolled?.length);
  useEffect(() => {
    if (!hasCourses) return;
    let cancelled = false;
    void fetch("/progress-manifest.json")
      .then((res) => (res.ok ? res.json() : { modules: [] }))
      .then((data: { modules?: ManifestModule[] }) => {
        if (!cancelled) setModules(data.modules ?? []);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [hasCourses]);

  if (!state) return null;
  const notices = derive(state, modules).filter((n) => !dismissed[n.id]);
  if (!notices.length) return null;

  function dismiss(id: string) {
    const next = { ...readDismissed(), [id]: Date.now() };
    // Old entries go, so the key does not grow forever.
    const cutoff = Date.now() - 60 * 24 * 60 * 60 * 1000;
    for (const [key, at] of Object.entries(next)) if (at < cutoff) delete next[key];
    try {
      localStorage.setItem(DISMISSED_KEY, JSON.stringify(next));
    } catch {
      /* dismissed for this page view only */
    }
    setDismissed(next);
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="pch-bell"
          aria-label={`Notifications (${notices.length})`}
        >
          <Bell className="size-[18px]" aria-hidden="true" />
          <span className="pch-bell__count" aria-hidden="true">
            {notices.length}
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>For you</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {notices.map((notice) => (
          <div className="pch-bell__row" key={notice.id}>
            <DropdownMenuItem asChild className="pch-bell__item">
              <Link href={notice.href} onClick={() => dismiss(notice.id)}>
                {notice.text}
              </Link>
            </DropdownMenuItem>
            <button
              type="button"
              className="pch-bell__dismiss"
              aria-label="Dismiss"
              onClick={() => dismiss(notice.id)}
            >
              <X className="size-3.5" aria-hidden="true" />
            </button>
          </div>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default Notifications;

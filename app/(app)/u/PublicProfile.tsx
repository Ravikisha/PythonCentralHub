"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Avatar } from "@/components/auth/Avatar";
import { courseInfo } from "@/lib/courses.data.mjs";
import { levelFor } from "@/src/lib/progress/awards";

interface Entry {
  uid: string;
  displayName: string;
  photoURL?: string;
  pages: number;
  courses?: Record<string, number>;
  certificates: number;
  certificateList?: { id: string; module: string; kind: string; issuedAt: number }[];
  xp: number;
}

interface ManifestModule {
  slug: string;
  label: string;
  count: number;
  href?: string;
}

type State = { kind: "loading" } | { kind: "missing" } | { kind: "found"; entry: Entry };

/**
 * A learner's public page. It reads their leaderboard entry, which exists only
 * if they opted in, so a profile is public exactly when its owner chose to be
 * listed. Everything shown was computed by the server.
 */
export function PublicProfile() {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [modules, setModules] = useState<ManifestModule[]>([]);

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("id") ?? "";
    if (!/^[A-Za-z0-9]{1,128}$/.test(id)) {
      setState({ kind: "missing" });
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const [{ doc, getDoc }, { getDb }] = await Promise.all([
          import("firebase/firestore"),
          import("@/src/lib/firebase/client"),
        ]);
        const snap = await getDoc(doc(await getDb(), "leaderboard", id));
        if (cancelled) return;
        setState(snap.exists() ? { kind: "found", entry: snap.data() as Entry } : { kind: "missing" });
      } catch {
        if (!cancelled) setState({ kind: "missing" });
      }
      try {
        const res = await fetch("/progress-manifest.json");
        if (res.ok && !cancelled) setModules(((await res.json()).modules ?? []) as ManifestModule[]);
      } catch {
        /* course totals are optional */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") return <p className="app__loading">Loading…</p>;
  if (state.kind === "missing") {
    return (
      <>
        <h1 className="pch-auth__title">Profile not found</h1>
        <p className="pch-auth__intro">
          This learner&rsquo;s profile is private, or the link is wrong. Profiles are public
          only for learners who chose to appear on the <Link href="/leaderboard/">leaderboard</Link>.
        </p>
      </>
    );
  }

  const { entry } = state;
  const { level } = levelFor(entry.xp);
  const courses = Object.entries(entry.courses ?? {}).sort((a, b) => b[1] - a[1]);

  return (
    <div className="public-profile">
      <header className="public-profile__head">
        <Avatar photo={entry.photoURL} seed={entry.uid} size={72} />
        <div>
          <h1 className="pch-auth__title">{entry.displayName || "A learner"}</h1>
          <p className="public-profile__stats">
            Level {level} · {entry.xp} XP · {entry.pages} lessons ·{" "}
            {entry.certificates} {entry.certificates === 1 ? "certificate" : "certificates"}
          </p>
        </div>
      </header>

      {courses.length ? (
        <section>
          <h2>Courses</h2>
          <ul className="public-profile__courses">
            {courses.map(([slug, done]) => {
              const info = courseInfo(slug);
              const total = modules.find((m) => m.slug === slug)?.count ?? 0;
              const pct = total ? Math.min(100, Math.round((done / total) * 100)) : 0;
              return (
                <li key={slug} data-subject={info?.subject}>
                  <span className="public-profile__course">
                    {info?.code ? <span className="public-profile__code">{info.code}</span> : null}
                    <Link href={info ? `/courses/${slug}/` : "/courses/"}>{info?.title ?? slug}</Link>
                  </span>
                  <span className="meter" aria-hidden="true">
                    <span style={{ width: `${pct}%` }} />
                  </span>
                  <span className="public-profile__count">
                    {total ? `${done} of ${total} lessons` : `${done} lessons`}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}

      {entry.certificateList?.length ? (
        <section>
          <h2>Certificates</h2>
          <ul className="public-profile__certs">
            {entry.certificateList.map((c) => (
              <li key={c.id}>
                <Link href={`/verify/?id=${c.id}`}>
                  {courseInfo(c.module)?.title ?? c.module}
                </Link>
                <span>
                  {c.kind === "completion" ? "Completion" : "Assessment"}
                  {c.issuedAt
                    ? ` · ${new Date(c.issuedAt).toLocaleDateString(undefined, { year: "numeric", month: "long" })}`
                    : ""}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

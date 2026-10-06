"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SessionLoading, SignedOutGate } from "@/components/auth/SignedOutGate";
import { useSession } from "@/components/auth/useSession";
import { courseInfo } from "@/lib/courses.data.mjs";

interface Stats {
  totals: Record<string, number>;
  feedback: { id: string; rating: string | null; comment: string; page: string; email: string; at: number | null }[];
  contact: { id: string; name: string; email: string; message: string; at: number | null }[];
  certificates: {
    id: string;
    holder: string;
    module: string;
    kind: string;
    score: number | null;
    at: number | null;
  }[];
}

const TOTALS: [string, string][] = [
  ["users", "Accounts with a profile"],
  ["attempts", "Assessment attempts"],
  ["passed", "Assessments passed"],
  ["certificates", "Certificates issued"],
  ["completionCertificates", "of which completion"],
  ["leaderboard", "On the leaderboard"],
  ["feedback", "Feedback received"],
  ["contact", "Contact messages"],
];

function date(at: number | null): string {
  return at ? new Date(at).toLocaleString() : "";
}

/**
 * Read-only operator view. The server decides who may see it (ADMIN_EMAILS);
 * this page only asks and shows what comes back.
 */
export function AdminPanel() {
  const session = useSession();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (session.state !== "signed-in") return;
    let cancelled = false;
    void (async () => {
      try {
        const { callApi } = await import("@/src/lib/firebase/client");
        const data = await callApi<Stats>("admin-stats");
        if (!cancelled) setStats(data);
      } catch (err) {
        if (!cancelled) setError((err as { message?: string }).message || "Could not load.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [session.state]);

  if (session.state === "loading") return <SessionLoading />;
  if (session.state === "signed-out") return <SignedOutGate next="/admin/" />;
  if (error) return <p className="pch-auth__intro">{error}</p>;
  if (!stats) return <SessionLoading />;

  return (
    <div className="admin">
      <ul className="admin__totals">
        {TOTALS.map(([key, label]) => (
          <li key={key}>
            <span className="admin__num">{stats.totals[key] ?? 0}</span>
            <span className="admin__label">{label}</span>
          </li>
        ))}
      </ul>

      <h2>Latest feedback</h2>
      {stats.feedback.length ? (
        <table className="admin__table">
          <thead>
            <tr>
              <th>When</th>
              <th>Rating</th>
              <th>Page</th>
              <th>Comment</th>
            </tr>
          </thead>
          <tbody>
            {stats.feedback.map((f) => (
              <tr key={f.id}>
                <td>{date(f.at)}</td>
                <td>{f.rating}</td>
                <td>{f.page ? <Link href={f.page}>{f.page}</Link> : null}</td>
                <td>
                  {f.comment}
                  {f.email ? <span className="admin__email"> — {f.email}</span> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="pch-auth__intro">None yet.</p>
      )}

      <h2>Latest contact messages</h2>
      {stats.contact.length ? (
        <ul className="admin__messages">
          {stats.contact.map((c) => (
            <li key={c.id}>
              <p className="admin__meta">
                {c.name} · <a href={`mailto:${c.email}`}>{c.email}</a> · {date(c.at)}
              </p>
              <p className="admin__body">{c.message}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="pch-auth__intro">None yet.</p>
      )}

      <h2>Latest certificates</h2>
      {stats.certificates.length ? (
        <table className="admin__table">
          <thead>
            <tr>
              <th>When</th>
              <th>Holder</th>
              <th>Course</th>
              <th>Kind</th>
              <th>Id</th>
            </tr>
          </thead>
          <tbody>
            {stats.certificates.map((c) => (
              <tr key={c.id}>
                <td>{date(c.at)}</td>
                <td>{c.holder}</td>
                <td>{courseInfo(c.module)?.title ?? c.module}</td>
                <td>{c.kind === "completion" ? "Completion" : `Assessment ${c.score ?? ""}%`}</td>
                <td>
                  <Link href={`/verify/?id=${c.id}`}>{c.id}</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="pch-auth__intro">None yet.</p>
      )}
    </div>
  );
}

"use client";

import Link from "next/link";
import { useEffect } from "react";
import { reportError } from "@/lib/report-error";

/**
 * A page that failed to render. Reported, then a way forward instead of a
 * blank screen: try again (most failures are a dropped connection), or go
 * back to the courses.
 */
export default function PageError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    reportError(error, "render");
  }, [error]);

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-24">
      <h1 className="text-3xl font-bold leading-tight">This page did not load</h1>
      <p className="mt-4 text-lg" style={{ color: "var(--muted)" }}>
        Something went wrong while showing it. Your progress is saved. Try
        again, or go back to your courses.
      </p>
      <p className="mt-8 flex flex-wrap gap-3">
        <button type="button" className="button button--primary" onClick={reset}>
          Try again
        </button>
        <Link className="button" href="/courses/">
          All courses
        </Link>
      </p>
      {error.digest ? (
        <p className="mt-6 text-sm" style={{ color: "var(--muted)" }}>
          Reference: {error.digest}
        </p>
      ) : null}
    </main>
  );
}

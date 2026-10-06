"use client";

import { useEffect } from "react";
import { reportError } from "@/lib/report-error";

/**
 * The last resort: the root layout itself failed. It replaces <html>, so it
 * carries its own minimal styling rather than the site's stylesheets.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    reportError(error, "global");
  }, [error]);

  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "system-ui, sans-serif",
          maxWidth: "36rem",
          margin: "6rem auto",
          padding: "0 1rem",
          lineHeight: 1.5,
        }}
      >
        <h1>Python Central Hub could not load</h1>
        <p>Something went wrong on our side. Your progress is saved in this browser.</p>
        <p>
          <button type="button" onClick={reset} style={{ padding: "0.5rem 1rem" }}>
            Try again
          </button>{" "}
          <a href="/">Go to the home page</a>
        </p>
      </body>
    </html>
  );
}

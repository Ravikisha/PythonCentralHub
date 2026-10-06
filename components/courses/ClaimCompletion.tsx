"use client";

import Link from "next/link";
import { useState } from "react";
import { useSession } from "@/components/auth/useSession";

/**
 * Claim a certificate of completion: every lesson done, no assessment.
 *
 * The server counts only progress it holds, so this pushes the local copy
 * first (resync() is a union, it never drops anything) and then asks. Its
 * refusal -- "Complete 154 of 171 lessons first" -- is shown as it comes.
 */
export function ClaimCompletion({ slug }: { slug: string }) {
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (session.state === "loading") return null;
  if (session.state === "signed-out") {
    return (
      <Link className="button" href={`/login/?next=/courses/${slug}/`}>
        Sign in for a completion certificate
      </Link>
    );
  }

  async function claim() {
    setBusy(true);
    setError(null);
    try {
      const { resync } = await import("@/src/lib/progress/sync");
      await resync();
      const { callApi } = await import("@/src/lib/firebase/client");
      const { certificateId } = await callApi<{ certificateId: string }>(
        "issue-certificate",
        { module: slug, kind: "completion" },
      );
      window.location.href = `/certificates/?new=${certificateId}`;
    } catch (err) {
      setError((err as { message?: string }).message || "Could not issue the certificate. Try again.");
      setBusy(false);
    }
  }

  return (
    <>
      <button type="button" className="button" disabled={busy} onClick={() => void claim()}>
        {busy ? "Issuing…" : "Get a completion certificate"}
      </button>
      {error ? (
        <span className="finish__error" role="alert">
          {error}
        </span>
      ) : null}
    </>
  );
}

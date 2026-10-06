"use client";

import Link from "next/link";
import { t } from "@/lib/strings";

/**
 * What a page shows to someone who is not signed in.
 *
 * A link, not a redirect: these pages can be opened directly, bookmarked and
 * shared, and the session is only known once the SDK has restored it. The
 * `next` parameter brings the reader back to the page they asked for.
 */
export function SignedOutGate({ next }: { next: string }) {
  return (
    <div className="app__gate">
      <p>{t("pch.authSignedOutNotice")}</p>
      {/* Two real buttons rather than one small text link: this screen has no
          other job, so the way forward should be the thing you see. */}
      <p className="app__gate-actions">
        <Link
          className="pch-auth__submit app__gate-primary"
          href={`/login/?next=${encodeURIComponent(next)}`}
        >
          {t("pch.authSignIn")}
        </Link>
        <Link
          className="pch-auth__secondary"
          href={`/signup/?next=${encodeURIComponent(next)}`}
        >
          {t("pch.authCreateAccount")}
        </Link>
      </p>
    </div>
  );
}

/** The interval between paint and the session resolving. */
export function SessionLoading() {
  return <p className="app__loading">{t("pch.authLoading")}</p>;
}

export default SignedOutGate;

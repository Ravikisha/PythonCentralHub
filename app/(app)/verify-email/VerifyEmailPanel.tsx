"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import { errorMessage } from "@/components/auth/session";
import { t } from "@/lib/strings";

export function VerifyEmailPanel() {
  const [state, setState] = useState<
    "checking" | "unverified" | "verified" | "signed-out"
  >("checking");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      // All inside the try: offline, a rejected reload() used to leave the
      // page on "checking" for good.
      try {
        const { currentUser } = await import("@/src/lib/firebase/auth");
        const user = await currentUser();

        if (!user || user.isAnonymous) {
          if (!cancelled) setState("signed-out");
          return;
        }

        // reload() refreshes emailVerified, which the cached User object would
        // otherwise keep reporting as false after the learner clicked the link
        // in another tab.
        await user.reload();
        if (!cancelled) setState(user.emailVerified ? "verified" : "unverified");
      } catch (err) {
        if (cancelled) return;
        setState("unverified");
        setStatus({ text: await errorMessage(err), tone: "error" });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  async function resend() {
    setBusy(true);
    setStatus(null);
    try {
      const { sendVerification } = await import("@/src/lib/firebase/auth");
      await sendVerification();
      setStatus({ text: t("pch.authVerifySent"), tone: "success" });
    } catch (err) {
      setStatus({ text: await errorMessage(err), tone: "error" });
      setBusy(false);
    }
  }

  return (
    <>
      <p className="pch-auth__intro">{t("pch.authVerifyIntro")}</p>

      {state === "unverified" ? (
        <button
          type="button"
          className="pch-auth__submit"
          disabled={busy}
          onClick={resend}
        >
          {t("pch.authVerifyResend")}
        </button>
      ) : null}

      <StatusLine
        status={
          state === "verified"
            ? { text: t("pch.authVerifyDone"), tone: "success" }
            : state === "signed-out"
              ? { text: t("pch.authSignedOutNotice"), tone: "error" }
              : status
        }
      />

      <p className="pch-auth__alt">
        <Link href="/welcome/">Choose what to learn</Link>
        {" · "}
        <Link href="/profile/">{t("pch.authProfile")}</Link>
      </p>
    </>
  );
}

export default VerifyEmailPanel;

"use client";

import Link from "next/link";
import { useState } from "react";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import { messageFor } from "@/components/auth/session";
import { t } from "@/lib/strings";

export function ResetForm() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setStatus(null);

    if (!email.trim()) {
      setStatus({ text: messageFor("pch.authErrRequired"), tone: "error" });
      return;
    }

    setBusy(true);
    try {
      const { sendPasswordReset } = await import("@/src/lib/firebase/auth");
      await sendPasswordReset(email.trim());
      setStatus({ text: t("pch.authResetSent"), tone: "success" });
      setEmail("");
    } catch (err) {
      const { authErrorKey } = await import("@/src/lib/firebase/auth");
      const key = authErrorKey(err);

      // `auth/user-not-found` maps to the generic credential message, which
      // would still hint that the address is unknown. Show the same "on its
      // way" line for it as for success.
      setStatus(
        key === "pch.authErrInvalidCredential"
          ? { text: t("pch.authResetSent"), tone: "success" }
          : { text: messageFor(key), tone: "error" },
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <form onSubmit={onSubmit} noValidate>
        <div className="pch-auth__field">
          <label htmlFor="pch-reset-email">{t("pch.authEmail")}</label>
          <input
            id="pch-reset-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            disabled={busy}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <button type="submit" className="pch-auth__submit" disabled={busy}>
          {t("pch.authResetSubmit")}
        </button>
      </form>

      <StatusLine status={status} />

      <p className="pch-auth__alt">
        <Link href="/login/">{t("pch.authSignIn")}</Link>
      </p>
    </>
  );
}

export default ResetForm;

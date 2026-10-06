"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthProviders } from "@/components/auth/AuthProviders";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import {
  errorMessage,
  mergeProgress,
  messageFor,
  nextUrl,
} from "@/components/auth/session";
import { t } from "@/lib/strings";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);

  /**
   * Finish a sign-in that left the site.
   *
   * When the popup is blocked -- Safari and most in-app browsers -- the SDK
   * falls back to a full-page redirect, and the reader lands back here already
   * authenticated. Without this the page would look like the sign-in silently
   * failed.
   */
  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const { completeRedirectSignIn } =
          await import("@/src/lib/firebase/auth");
        if (await completeRedirectSignIn()) {
          await mergeProgress();
          if (!cancelled) window.location.href = nextUrl();
        }
      } catch (err) {
        if (!cancelled)
          setStatus({ text: await errorMessage(err), tone: "error" });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setStatus(null);

    if (!email.trim() || !password) {
      setStatus({ text: messageFor("pch.authErrRequired"), tone: "error" });
      return;
    }

    setBusy(true);
    try {
      const { signInWithEmail } = await import("@/src/lib/firebase/auth");
      await signInWithEmail(email.trim(), password);
      await mergeProgress();
      window.location.href = nextUrl();
    } catch (err) {
      setStatus({ text: await errorMessage(err), tone: "error" });
      setBusy(false);
    }
  }

  async function onProvider(provider: "google" | "github") {
    setStatus(null);
    setBusy(true);
    try {
      const auth = await import("@/src/lib/firebase/auth");
      const cred =
        provider === "google"
          ? await auth.signInWithGoogle()
          : await auth.signInWithGithub();

      // A null credential means the popup was unavailable and a full-page
      // redirect is already under way, so leave the UI as it is.
      if (cred) {
        await mergeProgress();
        window.location.href = nextUrl();
      }
    } catch (err) {
      setStatus({ text: await errorMessage(err), tone: "error" });
      setBusy(false);
    }
  }

  return (
    <>
      <AuthProviders onProvider={onProvider} disabled={busy} />

      <form onSubmit={onSubmit} noValidate>
        <div className="pch-auth__field">
          <label htmlFor="pch-login-email">{t("pch.authEmail")}</label>
          <input
            id="pch-login-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            disabled={busy}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="pch-auth__field">
          <label htmlFor="pch-login-password">{t("pch.authPassword")}</label>
          <input
            id="pch-login-password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            disabled={busy}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit" className="pch-auth__submit" disabled={busy}>
          {t("pch.authLoginSubmit")}
        </button>
      </form>

      <StatusLine status={status} />

      <p className="pch-auth__alt">
        <Link href="/reset-password/">{t("pch.authForgot")}</Link>
      </p>
      <p className="pch-auth__alt">
        {t("pch.authNoAccount")}{" "}
        <Link href="/signup/">{t("pch.authCreateAccount")}</Link>
      </p>
    </>
  );
}

export default LoginForm;

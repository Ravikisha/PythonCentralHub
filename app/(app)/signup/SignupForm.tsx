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

export function SignupForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const { completeRedirectSignIn } =
          await import("@/src/lib/firebase/auth");
        if (await completeRedirectSignIn()) {
          await mergeProgress();
          if (!cancelled) window.location.href = nextUrl("/welcome/");
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

    // Checked here as well as by Firebase so the message matches the hint
    // under the field rather than the SDK's own six-character minimum.
    if (password.length < 8) {
      setStatus({ text: messageFor("pch.authErrWeakPassword"), tone: "error" });
      return;
    }

    setBusy(true);
    try {
      const { signUpWithEmail } = await import("@/src/lib/firebase/auth");
      await signUpWithEmail(email.trim(), password, name.trim() || undefined);
      await mergeProgress();
      window.location.href = "/verify-email/";
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
      if (cred) {
        await mergeProgress();
        window.location.href = nextUrl("/welcome/");
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
          <label htmlFor="pch-signup-name">{t("pch.authName")}</label>
          <input
            id="pch-signup-name"
            name="name"
            type="text"
            autoComplete="name"
            disabled={busy}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="pch-auth__field">
          <label htmlFor="pch-signup-email">{t("pch.authEmail")}</label>
          <input
            id="pch-signup-email"
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
          <label htmlFor="pch-signup-password">{t("pch.authPassword")}</label>
          <input
            id="pch-signup-password"
            name="password"
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            disabled={busy}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <span className="pch-auth__hint">{t("pch.authPasswordHint")}</span>
        </div>

        <button type="submit" className="pch-auth__submit" disabled={busy}>
          {t("pch.authSignupSubmit")}
        </button>

        <p className="pch-auth__hint">
          By creating an account you agree to the <Link href="/terms/">Terms of Use</Link>{" "}
          and the <Link href="/policy/">Privacy Policy</Link>.
        </p>
      </form>

      <StatusLine status={status} />

      <p className="pch-auth__alt">
        {t("pch.authHaveAccount")}{" "}
        <Link href="/login/">{t("pch.authSignIn")}</Link>
      </p>
    </>
  );
}

export default SignupForm;

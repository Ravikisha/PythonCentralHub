import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { LoginForm } from "./LoginForm";

/**
 * /login -- sign in with Google, GitHub or an email address.
 *
 * Statically generated like everything else: there is no server-side session,
 * the page renders identically for everyone, and the client decides what to do
 * once Firebase has restored the session in the browser.
 */
export const metadata: Metadata = {
  title: t("pch.authLoginTitle"),
  robots: { index: false, follow: true },
};

export default function LoginPage() {
  return (
    <div className="pch-auth">
      <h1 className="pch-auth__title">{t("pch.authLoginTitle")}</h1>
      <p className="pch-auth__intro">{t("pch.authLoginIntro")}</p>
      <LoginForm />
    </div>
  );
}

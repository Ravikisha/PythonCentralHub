import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { ResetForm } from "./ResetForm";

/**
 * /reset-password -- request a password reset link.
 *
 * The confirmation is deliberately unconditional: it says the same thing
 * whether or not an account exists for the address. Reporting "no such user"
 * here would let anyone test which email addresses are registered.
 */
export const metadata: Metadata = {
  title: t("pch.authResetTitle"),
  robots: { index: false, follow: true },
};

export default function ResetPasswordPage() {
  return (
    <div className="pch-auth">
      <h1 className="pch-auth__title">{t("pch.authResetTitle")}</h1>
      <p className="pch-auth__intro">{t("pch.authResetIntro")}</p>
      <ResetForm />
    </div>
  );
}

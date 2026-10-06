import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { VerifyEmailPanel } from "./VerifyEmailPanel";

/**
 * /verify-email -- where a new account lands after signing up.
 *
 * Verification is not a wall: every tutorial stays readable without it. It
 * gates certificate issuance only, so that a certificate names an address its
 * holder actually controls.
 */
export const metadata: Metadata = {
  title: t("pch.authVerifyTitle"),
  robots: { index: false, follow: true },
};

export default function VerifyEmailPage() {
  return (
    <div className="pch-auth">
      <h1 className="pch-auth__title">{t("pch.authVerifyTitle")}</h1>
      <VerifyEmailPanel />
    </div>
  );
}

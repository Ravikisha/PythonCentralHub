import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { SignupForm } from "./SignupForm";

/**
 * /signup -- create an account.
 *
 * The verification email is sent automatically. Certificates are gated on it;
 * reading is not.
 */
export const metadata: Metadata = {
  title: t("pch.authSignupTitle"),
  robots: { index: false, follow: true },
};

export default function SignupPage() {
  return (
    <div className="pch-auth">
      <h1 className="pch-auth__title">{t("pch.authSignupTitle")}</h1>
      <p className="pch-auth__intro">{t("pch.authSignupIntro")}</p>
      {/* True, and worth saying: the first sync after sign-up merges this
          browser's guest progress into the new account (src/lib/progress/
          sync.ts, mergeWithCloud), so nobody signs up afraid of starting over. */}
      <p className="pch-auth__note">
        Lessons you have already marked complete in this browser come with
        you into your account.
      </p>
      <SignupForm />
    </div>
  );
}

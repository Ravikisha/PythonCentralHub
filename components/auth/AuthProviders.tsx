"use client";

import { SiGithub, SiGoogle } from "@icons-pack/react-simple-icons";
import { t } from "@/lib/strings";

/**
 * The OAuth buttons shared by /login and /signup.
 *
 * GitHub can be hidden with `NEXT_PUBLIC_AUTH_GITHUB=off` while its OAuth
 * client secret is still missing from the Firebase console -- without the
 * secret the provider returns `auth/operation-not-allowed`, and a button that
 * always fails is worse than no button.
 */
const SHOW_GITHUB = process.env.NEXT_PUBLIC_AUTH_GITHUB !== "off";

export function AuthProviders({
  onProvider,
  disabled,
}: {
  onProvider: (provider: "google" | "github") => void;
  disabled?: boolean;
}) {
  return (
    <>
      <div className="pch-auth__providers">
        <button
          type="button"
          className="pch-auth__provider"
          disabled={disabled}
          onClick={() => onProvider("google")}
        >
          <SiGoogle className="size-4" aria-hidden="true" />
          {t("pch.authContinueGoogle")}
        </button>

        {SHOW_GITHUB ? (
          <button
            type="button"
            className="pch-auth__provider"
            disabled={disabled}
            onClick={() => onProvider("github")}
          >
            <SiGithub className="size-4" aria-hidden="true" />
            {t("pch.authContinueGithub")}
          </button>
        ) : null}
      </div>

      <p className="pch-auth__divider">{t("pch.authOr")}</p>
    </>
  );
}

export default AuthProviders;

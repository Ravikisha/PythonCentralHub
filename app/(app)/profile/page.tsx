import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { ProfilePanel } from "./ProfilePanel";

/**
 * /profile -- account details, preferences, data export and deletion.
 */
export const metadata: Metadata = {
  title: t("pch.authProfileTitle"),
  robots: { index: false, follow: false },
};

export default function ProfilePage() {
  return (
    <>
      <h1 className="pch-auth__title">{t("pch.authProfileTitle")}</h1>
      <ProfilePanel />
    </>
  );
}

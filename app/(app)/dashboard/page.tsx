import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { Dashboard } from "./Dashboard";

/**
 * /dashboard -- everything the learner has done so far.
 */
export const metadata: Metadata = {
  title: t("pch.dashTitle"),
  robots: { index: false, follow: true },
};

export default function DashboardPage() {
  return (
    <>
      <h1 className="pch-auth__title">{t("pch.dashTitle")}</h1>
      <Dashboard />
    </>
  );
}

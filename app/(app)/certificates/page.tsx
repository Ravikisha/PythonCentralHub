import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { CertificateList } from "./CertificateList";

/**
 * /certificates -- the learner's own issued certificates.
 */
export const metadata: Metadata = {
  title: t("pch.authCertificates"),
  robots: { index: false, follow: false },
};

export default function CertificatesPage() {
  return (
    <div className="pch-certs">
      <h1 className="assess__title">{t("pch.authCertificates")}</h1>
      <CertificateList />
    </div>
  );
}

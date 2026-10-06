import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { VerifyPanel } from "./VerifyPanel";

/**
 * /verify?id=XXXX-XXXX-XXXX -- public certificate check.
 *
 * A query parameter rather than a route segment: the site is statically
 * generated, so a /verify/[certId] route could only exist for ids that were
 * known at build time, which is none of them.
 *
 * Open to everyone, signed in or not. A certificate nobody else can check is
 * not a credential, so `certificates/{id}` allows `get` publicly -- and denies
 * `list`, so the collection cannot be swept for holders' names and addresses.
 */
export const metadata: Metadata = {
  title: t("pch.verifyTitle"),
};

export default function VerifyPage() {
  return (
    <div className="assess">
      <h1 className="assess__title">{t("pch.verifyTitle")}</h1>
      <p className="assess__lede">
        Every Python Central Hub certificate carries an ID. Enter it to see who earned
        it, for which course, with what score and when. Anyone can check; no
        account is needed.
      </p>
      <VerifyPanel />
    </div>
  );
}

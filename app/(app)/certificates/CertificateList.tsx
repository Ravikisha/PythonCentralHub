"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SessionLoading, SignedOutGate } from "@/components/auth/SignedOutGate";
import { useSession } from "@/components/auth/useSession";
import { t } from "@/lib/strings";
import { SITE_NAME, SITE_SLUG } from "@/lib/site";
import { courseInfo } from "@/lib/courses.data.mjs";

/**
 * Certificates are read from `users/{uid}/stats/certificates`, an index the
 * issue-certificate function maintains. The certificates collection itself
 * allows `get` but not `list`, so it cannot be enumerated for holders' names
 * and addresses -- which is why this index exists rather than a query.
 */
interface CertIndexItem {
  certificateId: string;
  module: string;
  /** Absent on certificates issued before completion certificates existed. */
  kind?: "assessment" | "completion";
  score: number | null;
  issuedAt: number;
}

export function CertificateList() {
  const session = useSession();

  if (session.state === "loading") return <SessionLoading />;
  if (session.state === "signed-out")
    return <SignedOutGate next="/certificates/" />;

  return (
    <Held
      uid={session.user.uid}
      holder={session.user.displayName || session.user.email || ""}
    />
  );
}

function Held({ uid, holder }: { uid: string; holder: string }) {
  const [items, setItems] = useState<CertIndexItem[] | null>(null);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [printing, setPrinting] = useState<string | null>(null);
  const [highlight, setHighlight] = useState<string | null>(null);

  useEffect(() => {
    setHighlight(new URLSearchParams(window.location.search).get("new"));
  }, []);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const { doc, getDoc } = await import("firebase/firestore");
        const { getDb } = await import("@/src/lib/firebase/client");
        const db = await getDb();
        const snap = await getDoc(
          doc(db, "users", uid, "stats", "certificates"),
        );
        const held = ((snap.data()?.items ?? []) as CertIndexItem[]).sort(
          (a, b) => b.issuedAt - a.issuedAt,
        );
        if (!cancelled) setItems(held);
      } catch {
        if (!cancelled) setItems([]);
      }

      try {
        const res = await fetch("/progress-manifest.json");
        if (!res.ok) return;
        const data = (await res.json()) as {
          modules: { slug: string; label: string }[];
        };
        if (!cancelled) {
          setLabels(
            Object.fromEntries(data.modules.map((m) => [m.slug, m.label])),
          );
        }
      } catch {
        /* a de-slugged module name is a fine fallback */
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [uid]);

  // Printing is a page-level mode: the sheet holds one certificate, and the
  // print stylesheet hides everything that is not the card being printed.
  useEffect(() => {
    function done() {
      setPrinting(null);
      delete document.body.dataset.printing;
    }
    window.addEventListener("afterprint", done);
    return () => window.removeEventListener("afterprint", done);
  }, []);

  const [saving, setSaving] = useState<string | null>(null);

  async function savePdf(button: HTMLElement, certificateId: string, label: string, verifyUrl: string) {
    const card = button.closest<HTMLElement>(".pch-cert");
    if (!card) return;
    setSaving(certificateId);
    try {
      const { downloadCertificatePdf } = await import("@/lib/certificate-pdf");
      await downloadCertificatePdf(card, {
        certificateId,
        verifyUrl,
        fileName: `${SITE_SLUG}-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${certificateId}.pdf`,
      });
    } catch {
      // Printing to PDF still works; say so rather than failing silently.
      window.alert("Could not create the PDF here. Use Print and choose \"Save as PDF\" instead.");
    } finally {
      setSaving(null);
    }
  }

  function print(certificateId: string) {
    setPrinting(certificateId);
    document.body.dataset.printing = "1";
    // Let the class land before the print dialog freezes the page.
    window.requestAnimationFrame(() => window.print());
  }

  if (items === null) return <SessionLoading />;
  if (items.length === 0)
    return <p className="pch-auth__intro">{t("pch.certNone")}</p>;

  return (
    <div>
      {items.map((item) => {
        const label = labels[item.module] ?? item.module.replace(/-/g, " ");
        const issued = new Date(item.issuedAt);
        const url =
          typeof window === "undefined"
            ? ""
            : `${window.location.origin}/verify/?id=${item.certificateId}`;

        const linkedIn = new URLSearchParams({
          startTask: "CERTIFICATION_NAME",
          name: `${label} — ${SITE_NAME}`,
          organizationName: SITE_NAME,
          issueYear: String(issued.getFullYear()),
          issueMonth: String(issued.getMonth() + 1),
          certId: item.certificateId,
          certUrl: url,
        });

        return (
          <article
            className={`pch-cert${printing === item.certificateId ? " pch-cert--printing" : ""}`}
            key={item.certificateId}
            data-new={String(highlight === item.certificateId)}
            data-subject={courseInfo(item.module)?.subject}
          >
            {item.kind === "completion" ? (
              <p className="pch-cert__kind">{t("pch.certCompletion")}</p>
            ) : null}
            <p className="pch-cert__awarded">{t("pch.certAwarded")}</p>
            <p className="pch-cert__holder">{holder}</p>
            <p className="pch-cert__module">
              {courseInfo(item.module)?.code ? (
                <span className="pch-cert__code">{courseInfo(item.module)?.code}</span>
              ) : null}
              {label}
            </p>
            <p className="pch-cert__meta">
              {`${item.kind === "completion" ? t("pch.certCompletionMeta") : `${t("pch.certScore")} ${item.score}%`}  ·  ${t("pch.certIssued")} ${issued.toLocaleDateString(
                undefined,
                { year: "numeric", month: "long", day: "numeric" },
              )}`}
            </p>
            <p className="pch-cert__id">{`${t("pch.certId")} ${item.certificateId}`}</p>

            <p className="pch-cert__actions">
              {/* Print rather than a rendered image: the browser's own "Save
                  as PDF" produces selectable, scalable output, and print CSS
                  keeps one certificate per sheet without a canvas pipeline to
                  maintain. */}
              <button
                type="button"
                className="pch-auth__secondary"
                onClick={() => print(item.certificateId)}
              >
                {t("pch.certPrint")}
              </button>

              <button
                type="button"
                className="pch-auth__secondary"
                disabled={saving === item.certificateId}
                onClick={(e) => void savePdf(e.currentTarget, item.certificateId, label, url)}
              >
                {saving === item.certificateId ? "Preparing PDF…" : "Download PDF"}
              </button>

              <Link
                className="pch-auth__secondary"
                href={`/verify/?id=${item.certificateId}`}
              >
                {t("pch.certVerifyLink")}
              </Link>

              <a
                className="pch-auth__secondary"
                rel="noopener"
                target="_blank"
                href={`https://www.linkedin.com/profile/add?${linkedIn}`}
              >
                {t("pch.certLinkedIn")}
              </a>
            </p>
          </article>
        );
      })}
    </div>
  );
}

export default CertificateList;

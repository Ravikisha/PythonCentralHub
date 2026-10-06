"use client";

import { useCallback, useEffect, useState } from "react";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import { t } from "@/lib/strings";
import { courseInfo } from "@/lib/courses.data.mjs";

interface Certificate {
  certificateId: string;
  holder: string;
  module: string;
  /** Absent on certificates issued before completion certificates existed. */
  kind?: "assessment" | "completion";
  score: number | null;
  pagesCompleted: number;
  pagesTotal: number;
  issuedAt?: { toDate(): Date };
}

async function moduleLabel(slug: string): Promise<string> {
  try {
    const res = await fetch("/progress-manifest.json");
    if (!res.ok) return slug.replace(/-/g, " ");
    const data = (await res.json()) as {
      modules: { slug: string; label: string }[];
    };
    return (
      data.modules.find((m) => m.slug === slug)?.label ??
      slug.replace(/-/g, " ")
    );
  } catch {
    return slug.replace(/-/g, " ");
  }
}

export function VerifyPanel() {
  const [id, setId] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [found, setFound] = useState<{
    cert: Certificate;
    label: string;
  } | null>(null);

  const check = useCallback(async (rawId: string) => {
    const certificateId = rawId.trim().toUpperCase();
    if (!certificateId) return;

    setFound(null);
    setStatus({ text: t("pch.verifyChecking"), tone: "info" });

    try {
      const { doc, getDoc } = await import("firebase/firestore");
      const { getDb } = await import("@/src/lib/firebase/client");
      const snap = await getDoc(
        doc(await getDb(), "certificates", certificateId),
      );

      if (!snap.exists()) {
        setStatus({ text: t("pch.verifyUnknown"), tone: "error" });
        return;
      }

      const cert = snap.data() as Certificate;
      setFound({ cert, label: await moduleLabel(cert.module) });
      setStatus({ text: t("pch.verifyValid"), tone: "success" });
    } catch (err) {
      console.error("[verify] lookup failed:", err);
      setStatus({ text: t("pch.authErrGeneric"), tone: "error" });
    }
  }, []);

  // A certificate is shared as a link, so an id in the URL checks itself.
  useEffect(() => {
    const fromUrl = new URLSearchParams(window.location.search).get("id");
    if (!fromUrl) return;
    setId(fromUrl);
    void check(fromUrl);
  }, [check]);

  const issued = found?.cert.issuedAt?.toDate?.();

  return (
    <>
      <form
        className="verify__form"
        noValidate
        onSubmit={(e) => {
          e.preventDefault();
          void check(id);
        }}
      >
        <label htmlFor="pch-verify-id">{t("pch.certId")}</label>
        <div className="verify__row">
          <input
            id="pch-verify-id"
            name="id"
            type="text"
            autoComplete="off"
            spellCheck={false}
            placeholder="XXXX-XXXX-XXXX"
            value={id}
            onChange={(e) => setId(e.target.value)}
          />
          <button type="submit" className="button button--primary">
            {t("pch.verifySubmit")}
          </button>
        </div>
      </form>

      <StatusLine status={status} />

      {found ? (
        <article
          className="pch-cert"
          data-subject={courseInfo(found.cert.module)?.subject}
        >
          {found.cert.kind === "completion" ? (
            <p className="pch-cert__kind">{t("pch.certCompletion")}</p>
          ) : null}
          <p className="pch-cert__awarded">{t("pch.certAwarded")}</p>
          <p className="pch-cert__holder">{found.cert.holder}</p>
          <p className="pch-cert__module">
            {courseInfo(found.cert.module)?.code ? (
              <span className="pch-cert__code">
                {courseInfo(found.cert.module)?.code}
              </span>
            ) : null}
            {found.label}
          </p>
          <p className="pch-cert__meta">
            {(found.cert.kind === "completion"
              ? t("pch.certCompletionMeta")
              : `${t("pch.certScore")} ${found.cert.score}%`) +
              (issued
                ? `  ·  ${t("pch.certIssued")} ${issued.toLocaleDateString(
                    undefined,
                    {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    },
                  )}`
                : "")}
          </p>
          <p className="pch-cert__id">{`${t("pch.certId")} ${found.cert.certificateId}`}</p>
        </article>
      ) : null}
    </>
  );
}

export default VerifyPanel;

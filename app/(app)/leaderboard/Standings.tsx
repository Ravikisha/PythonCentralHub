"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { t } from "@/lib/strings";
import { Avatar } from "@/components/auth/Avatar";

interface Entry {
  uid: string;
  displayName: string;
  photoURL?: string;
  xp: number;
  pages: number;
  certificates: number;
}

export function Standings() {
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const { collection, getDocs, orderBy, query, limit } =
          await import("firebase/firestore");
        const { getDb } = await import("@/src/lib/firebase/client");

        const snap = await getDocs(
          query(
            collection(await getDb(), "leaderboard"),
            orderBy("xp", "desc"),
            limit(50),
          ),
        );

        if (!cancelled) setEntries(snap.docs.map((d) => d.data() as Entry));
      } catch (err) {
        console.error("[leaderboard] load failed:", err);
        if (!cancelled) setFailed(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  if (failed) return <p data-tone="error">{t("pch.authErrGeneric")}</p>;
  if (entries === null)
    return <p className="app__loading">{t("pch.authLoading")}</p>;
  if (entries.length === 0) return <p>{t("pch.boardEmpty")}</p>;

  return (
    <ol className="pch-board__list">
      {entries.map((entry, index) => (
        <li className="pch-board__row" key={entry.uid}>
          <span className="pch-board__rank">{index + 1}</span>
          <Avatar photo={entry.photoURL} seed={entry.uid} size={28} />
          {/* Display names come from other people's accounts, so they are
              rendered as text and never as markup. */}
          <Link className="pch-board__name" href={`/u/?id=${encodeURIComponent(entry.uid)}`}>
            {entry.displayName || "A learner"}
          </Link>
          <span className="pch-board__detail">
            {entry.pages} lessons
            {entry.certificates
              ? `, ${entry.certificates} ${entry.certificates === 1 ? "certificate" : "certificates"}`
              : ""}
          </span>
          <span className="pch-board__xp">{`${entry.xp} ${t("pch.levelXp")}`}</span>
        </li>
      ))}
    </ol>
  );
}

export default Standings;

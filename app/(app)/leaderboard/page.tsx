import type { Metadata } from "next";
import { t } from "@/lib/strings";
import { Standings } from "./Standings";
import { BoardAction } from "./BoardAction";

/**
 * /leaderboard -- the opt-in public standings.
 *
 * Entries are written only by the publish-leaderboard function, which
 * recomputes each total from server-side records. Nothing here is
 * self-reported, and nobody appears without switching it on in their profile.
 */
export const metadata: Metadata = {
  title: t("pch.boardTitle"),
};

export default function LeaderboardPage() {
  return (
    <div className="assess">
      <h1 className="assess__title">{t("pch.boardTitle")}</h1>
      <p className="assess__lede">{t("pch.boardIntro")}</p>

      {/* How the number is made, because a ranking nobody can explain is
          not worth climbing. Mirrors app/api/publish-leaderboard. */}
      <dl className="assess__facts">
        <div>
          <dt>Each lesson completed</dt>
          <dd>10 XP</dd>
        </div>
        <div>
          <dt>Each certificate</dt>
          <dd>250 XP</dd>
        </div>
        <div>
          <dt>Listed</dt>
          <dd>Only if you opt in</dd>
        </div>
      </dl>

      <Standings />

      <p className="assess__actions">
        <BoardAction />
      </p>
    </div>
  );
}

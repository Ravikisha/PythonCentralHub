"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { readHint } from "@/src/lib/auth/hint";
import { t } from "@/lib/strings";

/**
 * The one thing to do on the leaderboard, depending on who is looking.
 *
 * It used to be a single "Join or leave the leaderboard" link for everyone,
 * which sent guests to a profile page they could not open. Guests are asked
 * to sign in (and come back to the switch); learners go straight to it.
 */
export function BoardAction() {
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    const hint = readHint();
    setSignedIn(Boolean(hint && !hint.anon));
  }, []);

  return signedIn ? (
    <Link className="button" href="/profile/#prof-prefs">
      {t("pch.boardJoin")}
    </Link>
  ) : (
    <Link className="button button--primary" href="/login/?next=/profile/">
      Sign in to join
    </Link>
  );
}

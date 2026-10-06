"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Award, Bookmark, ChartLine, LogIn, LogOut, Trophy, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  readHint,
  clearHint,
  onHintChange,
  type AuthHint,
} from "@/src/lib/auth/hint";
import { Avatar } from "@/components/auth/Avatar";
import { t } from "@/lib/strings";

/**
 * The account control in the site header.
 *
 * On every page, so it is deliberately cheap:
 *
 *  - The first paint comes from the localStorage hint written by
 *    src/lib/auth/hint.ts. No Firebase, no network, no layout shift for the
 *    common case.
 *  - The Firebase Auth SDK is fetched only when there is a hint to verify, or
 *    when the reader actually signs out. A signed-out visitor never downloads
 *    it.
 *
 * An anonymous session is treated as signed out: those exist to hold progress,
 * not to be an account, and this site never creates one.
 */
/* Labels are resolved here rather than from the key at render time, because
   scripts/check-i18n.mjs reads source for literal translation calls. */
const LINKS = [
  { href: "/dashboard/", icon: ChartLine, label: t("pch.authDashboard") },
  { href: "/saved/", icon: Bookmark, label: t("pch.authSaved") },
  { href: "/certificates/", icon: Award, label: t("pch.authCertificates") },
  { href: "/leaderboard/", icon: Trophy, label: t("pch.boardTitle") },
  { href: "/profile/", icon: User, label: t("pch.authProfile") },
];

export function UserMenu() {
  const [hint, setHint] = useState<AuthHint | null>(null);
  const [busy, setBusy] = useState(false);

  // localStorage cannot be read while rendering on the server, and the markup
  // must match what the server sent, so the hint lands on the first effect
  // instead. Signed out is the honest first frame.
  useEffect(() => {
    setHint(readHint());
    // A saved name, a linked provider or a sign-out in another tab repaints
    // the corner straight away rather than on the next page load.
    return onHintChange(() => setHint(readHint()));
  }, []);

  /**
   * Check the hint against the real session, but only when there is one to
   * check and only once the page is idle. This is what catches a session that
   * expired or was revoked on another device.
   */
  useEffect(() => {
    if (!readHint()) return;

    let stop: (() => void) | undefined;
    let cancelled = false;

    const verify = async () => {
      try {
        const { onUser } = await import("@/src/lib/firebase/auth");
        const unsubscribe = await onUser(() => {
          if (!cancelled) setHint(readHint()); // onUser refreshes the hint itself
        });
        if (cancelled) unsubscribe();
        else stop = unsubscribe;
      } catch {
        /* offline: keep showing the cached identity */
      }
    };

    const idle =
      typeof window.requestIdleCallback === "function"
        ? window.requestIdleCallback(() => void verify(), { timeout: 5000 })
        : window.setTimeout(() => void verify(), 2000);

    return () => {
      cancelled = true;
      stop?.();
      if (typeof window.cancelIdleCallback === "function") {
        window.cancelIdleCallback(idle);
      } else {
        // The setTimeout fallback was never cleared.
        window.clearTimeout(idle);
      }
    };
  }, []);

  async function signOut() {
    setBusy(true);
    try {
      const { signOutUser } = await import("@/src/lib/firebase/auth");
      await signOutUser();
    } catch {
      clearHint(); // network died mid-sign-out; at least drop the local state
    }
    window.location.href = "/";
  }

  const account = hint && !hint.anon ? hint : null;

  if (!account) {
    return (
      <Button asChild size="sm" variant="outline" className="pch-user__signin">
        <Link href="/login/">
          <LogIn className="size-4" aria-hidden="true" />
          <span className="max-[30rem]:sr-only">{t("pch.authSignIn")}</span>
        </Link>
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="pch-user__trigger"
          aria-label={t("pch.authAccount")}
        >
          <Avatar photo={account.photo} seed={account.uid} size={32} />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-60">
        <DropdownMenuLabel className="pch-user__who">
          <Avatar photo={account.photo} seed={account.uid} size={40} />
          <span className="pch-user__lines">
            <span className="pch-user__name">
              {account.name || account.email}
            </span>
            {account.name ? (
              <span className="pch-user__email">{account.email}</span>
            ) : null}
          </span>
        </DropdownMenuLabel>

        <DropdownMenuSeparator />

        {LINKS.map(({ href, icon: Icon, label }) => (
          <DropdownMenuItem asChild key={href}>
            <Link href={href}>
              <Icon className="size-4" aria-hidden="true" />
              {label}
            </Link>
          </DropdownMenuItem>
        ))}

        <DropdownMenuSeparator />

        <DropdownMenuItem
          disabled={busy}
          onSelect={() => void signOut()}
          variant="destructive"
        >
          <LogOut className="size-4" aria-hidden="true" />
          {t("pch.authSignOut")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default UserMenu;

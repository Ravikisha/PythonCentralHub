"use client";

import { t } from "@/lib/strings";

/**
 * The pieces every auth screen needs, in one place.
 *
 * The Firebase SDK is imported dynamically, never at module scope: these
 * helpers are pulled into pages that a signed-out reader may only look at, and
 * the SDK is the single largest thing this site can download. Nothing fetches
 * it until a button is pressed.
 */

/** Translated text for a `pch.authErr*` key from `authErrorKey()`. */
export function messageFor(key: string): string {
  return t(key);
}

export async function errorMessage(err: unknown): Promise<string> {
  const { authErrorKey } = await import("@/src/lib/firebase/auth");
  return messageFor(authErrorKey(err));
}

/**
 * Fold progress collected before signing in into the account.
 *
 * Best-effort: a failed merge must never block the redirect, because the
 * sign-in itself already succeeded and the local copy is still intact.
 */
export async function mergeProgress(): Promise<void> {
  try {
    const { resync } = await import("@/src/lib/progress/sync");
    await resync();
  } catch (err) {
    console.warn("[auth] progress merge deferred:", err);
  }
}

/**
 * Where to send the learner after a successful sign-in.
 *
 * The site is statically generated, so there is no server to hold a "return
 * to" value -- it rides in the `?next=` query string instead. Only same-origin
 * relative paths are honoured: accepting an absolute URL here would turn the
 * login page into an open redirect that phishing links could point at.
 */
export function nextUrl(fallback = "/profile/"): string {
  const raw = new URLSearchParams(window.location.search).get("next");
  if (!raw) return fallback;
  if (!raw.startsWith("/")) return fallback;

  // Resolve it the way the browser will, and keep it only if it stays on this
  // origin. A prefix check alone let `/\evil.com` through: browsers read the
  // backslash as a slash, which makes it `//evil.com`.
  try {
    const url = new URL(raw, window.location.origin);
    if (url.origin !== window.location.origin) return fallback;
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return fallback;
  }
}

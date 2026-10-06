"use client";

import { useEffect, useState } from "react";
import type { User } from "firebase/auth";

export type Session =
  | { state: "loading"; user: null }
  | { state: "signed-out"; user: null }
  | { state: "signed-in"; user: User };

/**
 * Who is reading, once the browser knows.
 *
 * Every page here is statically generated, so the server cannot know: the
 * markup is identical for everyone and the answer arrives a moment after
 * paint, when the Firebase SDK has restored the session from storage. Pages
 * render a "loading" state first and then one of the other two -- they do not
 * redirect, because a redirect would fire before auth had finished restoring
 * and would bounce a signed-in reader out of their own account page.
 *
 * An anonymous Firebase session counts as signed out. The site never creates
 * one; a guest's progress lives in localStorage and nowhere else.
 */
export function useSession(): Session {
  const [session, setSession] = useState<Session>({
    state: "loading",
    user: null,
  });

  useEffect(() => {
    let cancelled = false;
    let stop: (() => void) | undefined;

    void (async () => {
      const { onUser } = await import("@/src/lib/firebase/auth");

      const unsubscribe = await onUser((user) => {
        if (cancelled) return;
        setSession(
          user && !user.isAnonymous
            ? { state: "signed-in", user }
            : { state: "signed-out", user: null },
        );
      });
      // Unmounted while the SDK loaded: cleanup already ran, so nobody else
      // will ever call this. It used to leak the listener.
      if (cancelled) unsubscribe();
      else stop = unsubscribe;
    })();

    return () => {
      cancelled = true;
      stop?.();
    };
  }, []);

  return session;
}

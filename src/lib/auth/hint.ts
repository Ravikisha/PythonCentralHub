/**
 * A tiny, Firebase-free cache of "who is signed in".
 *
 * The header renders on every one of the site's ~1190 static pages. Asking
 * Firebase Auth who the user is would mean shipping the Auth SDK to all of
 * them, including to the large majority of readers who never sign in.
 *
 * Instead the signed-in identity is mirrored into localStorage whenever auth
 * state changes, and the header renders straight from that -- synchronously,
 * with no network and no SDK. Pages that actually need a real session (the
 * dashboard, anything that writes) still load the SDK and use the live user.
 *
 * The hint is a display convenience, never an authorisation signal. Editing it
 * by hand changes the avatar in the corner and nothing else: every read and
 * write is still checked against Firestore rules on the server.
 */
const KEY = "pch-auth-hint";

export interface AuthHint {
  uid: string;
  name: string;
  email: string;
  photo: string;
  /** Anonymous learners get a hint too, but no account UI. */
  anon: boolean;
}

export function readHint(): AuthHint | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const v = JSON.parse(raw) as AuthHint;
    return v && typeof v.uid === "string" ? v : null;
  } catch {
    // Private mode, blocked storage, or a corrupt value. Render signed out.
    return null;
  }
}

export function writeHint(hint: AuthHint): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(hint));
  } catch {
    /* storage unavailable -- the UI just falls back to signed out */
  }
}

export function clearHint(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}

/** First letter of the name or email, for the fallback avatar. */
export function initialOf(hint: Pick<AuthHint, "name" | "email">): string {
  const source = hint.name || hint.email || "?";
  return source.trim().charAt(0).toUpperCase() || "?";
}

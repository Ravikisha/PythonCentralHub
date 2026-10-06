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

/**
 * Fired on this window whenever the hint changes, so the header updates the
 * moment a name is saved or a provider is linked instead of on the next page
 * load. Other tabs hear about it through the browser's own `storage` event.
 */
export const HINT_EVENT = "pch-auth-hint";

function announce(): void {
  try {
    window.dispatchEvent(new Event(HINT_EVENT));
  } catch {
    /* no window (server) -- nothing to tell */
  }
}

export function writeHint(hint: AuthHint): void {
  try {
    const next = JSON.stringify(hint);
    if (localStorage.getItem(KEY) === next) return;
    localStorage.setItem(KEY, next);
    announce();
  } catch {
    /* storage unavailable -- the UI just falls back to signed out */
  }
}

export function clearHint(): void {
  try {
    if (localStorage.getItem(KEY) === null) return;
    localStorage.removeItem(KEY);
    announce();
  } catch {
    /* ignore */
  }
}

/** Call `fn` whenever the hint changes here or in another tab. */
export function onHintChange(fn: () => void): () => void {
  const onStorage = (e: StorageEvent) => {
    if (e.key === KEY || e.key === null) fn();
  };
  window.addEventListener(HINT_EVENT, fn);
  window.addEventListener("storage", onStorage);
  return () => {
    window.removeEventListener(HINT_EVENT, fn);
    window.removeEventListener("storage", onStorage);
  };
}

/** First letter of the name or email. */
export function initialOf(hint: Pick<AuthHint, "name" | "email">): string {
  const source = hint.name || hint.email || "?";
  return source.trim().charAt(0).toUpperCase() || "?";
}

/**
 * Lazy Firebase client singletons.
 *
 * Only `firebase/app` is imported statically. Firestore, Auth and Analytics
 * are pulled in through dynamic `import()`, so a reader who never submits a
 * form and never signs in downloads none of them. This matters because
 * Feedback.astro sits in the Footer override, i.e. on all ~1190 pages.
 *
 * Browser-only. Every export bails out during SSR/prerender rather than
 * throwing, so importing this from a component frontmatter is harmless.
 */
import { initializeApp, getApp, getApps, type FirebaseApp } from "firebase/app";
import { firebaseConfig } from "./config";

const isBrowser = () => typeof window !== "undefined";

/** The one FirebaseApp instance. Safe to call repeatedly. */
export function getFirebaseApp(): FirebaseApp {
  return getApps().length ? getApp() : initializeApp(firebaseConfig);
}

/**
 * Local emulators, for the end-to-end tests only (tests/e2e). Set
 * NEXT_PUBLIC_FIREBASE_EMULATORS=1 at build time to point Auth at
 * localhost:9099 and Firestore at localhost:8080. Never set in production.
 */
const EMULATORS = process.env.NEXT_PUBLIC_FIREBASE_EMULATORS === "1";
let dbConnected = false;
let authConnected = false;

/** Firestore handle. The SDK chunk loads on first call, not on page load. */
export async function getDb() {
  const { getFirestore, connectFirestoreEmulator } = await import("firebase/firestore");
  const db = getFirestore(getFirebaseApp());
  if (EMULATORS && !dbConnected) {
    connectFirestoreEmulator(db, "127.0.0.1", 8080);
    dbConnected = true;
  }
  return db;
}

/**
 * Auth handle, with the device language set so Firebase's verification and
 * password-reset emails arrive in the reader's language.
 */
export async function getAuthClient() {
  const { getAuth, connectAuthEmulator } = await import("firebase/auth");
  const auth = getAuth(getFirebaseApp());
  if (EMULATORS && !authConnected) {
    connectAuthEmulator(auth, "http://127.0.0.1:9099", { disableWarnings: true });
    authConnected = true;
  }
  auth.useDeviceLanguage();
  return auth;
}

/**
 * Call one of the site's own serverless endpoints under /api.
 *
 * These are Vercel Functions rather than Firebase Cloud Functions: Cloud
 * Functions need the Blaze plan, and this site is already hosted on Vercel,
 * whose free tier runs them at no cost. The trust boundary is identical --
 * exam keys and certificates are still only touched by code the browser
 * cannot run.
 *
 * Authentication travels as a Firebase ID token in the Authorization header,
 * which the server verifies against Google's public keys. `getIdToken()`
 * refreshes it automatically when it is close to expiring, so a long session
 * does not start failing silently.
 *
 * Errors arrive as `{ error }` with a meaningful status, and are rethrown with
 * the server's own wording -- "Complete 154 of 171 pages first" is far more
 * use to a learner than a generic failure.
 */
export async function callApi<T = unknown>(
  path: string,
  payload: Record<string, unknown> = {}
): Promise<T> {
  const auth = await getAuthClient();
  const user = auth.currentUser;
  if (!user) throw new Error("Sign in first.");

  // Trailing slash: the site sets `trailingSlash`, and without it every call
  // would take a 308 hop before reaching the handler.
  const res = await fetch(`/api/${path.replace(/\/$/, "")}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${await user.getIdToken()}`,
    },
    body: JSON.stringify(payload),
  });

  const data = (await res.json().catch(() => ({}))) as {
    error?: string;
    code?: string;
  } & T;
  if (!res.ok) {
    // The code rides along so callers can tell "sign in again" or "not set up
    // yet" apart from a plain failure, and so authErrorKey() can translate it.
    throw Object.assign(
      new Error(data.error || "Something went wrong. Please try again."),
      { code: data.code, status: res.status },
    );
  }
  return data as T;
}

let analyticsStarted = false;

/**
 * Start Analytics once, off the critical path.
 *
 * Deferred to idle time and guarded by `isSupported()` so it never runs in a
 * context where the measurement SDK would throw (no cookies, some in-app
 * browsers). Fire-and-forget: callers do not await it.
 */
export function initAnalytics(): void {
  if (!isBrowser() || analyticsStarted) return;
  analyticsStarted = true;

  const start = async () => {
    try {
      const { getAnalytics, isSupported } = await import("firebase/analytics");
      if (await isSupported()) getAnalytics(getFirebaseApp());
    } catch (err) {
      console.warn("[firebase] analytics unavailable:", err);
    }
  };

  if (typeof window.requestIdleCallback === "function") {
    window.requestIdleCallback(() => void start(), { timeout: 4000 });
  } else {
    window.setTimeout(() => void start(), 1500);
  }
}

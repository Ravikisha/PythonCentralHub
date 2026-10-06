/**
 * Auth helpers for the learning platform.
 *
 * Everything here is browser-only and loads the Firebase Auth SDK on demand
 * (see client.ts). Import it from a `<script>` block, never from component
 * frontmatter.
 *
 * Providers: Google, GitHub, email + password, and anonymous. The Firebase
 * project has "one account per email address" linking enabled, so signing in
 * with Google using an address that already has a password account links the
 * two instead of erroring. GitHub can still collide when its account exposes
 * no verified email, so AUTH_ERROR_KEYS covers that case too.
 */
import type { User, UserCredential } from "firebase/auth";
import { getAuthClient, getDb } from "./client";
import { clearHint, writeHint } from "../auth/hint";

export type { User };

/**
 * Mirror the current user into the localStorage hint the header renders from.
 *
 * Called on every auth-state change and after every successful sign-in, so the
 * next page load can draw the account menu without touching Firebase.
 */
export function syncHint(user: User | null): void {
  if (!user) {
    clearHint();
    return;
  }
  writeHint({
    uid: user.uid,
    name: user.displayName ?? "",
    email: user.email ?? "",
    photo: photoOf(user),
    anon: user.isAnonymous,
  });
}

/**
 * The account's picture, wherever the provider put it.
 *
 * `user.photoURL` is only filled from the provider the account was *created*
 * with. An email-and-password account that later links Google keeps an empty
 * photoURL, and the Google picture sits in `providerData` -- so the header
 * showed an initial for someone who had signed in with Google.
 */
export function photoOf(user: User): string {
  return (
    user.photoURL ||
    user.providerData.find((p) => p.photoURL)?.photoURL ||
    ""
  );
}

/* -------------------------------------------------------------------------- */
/* Session                                                                     */
/* -------------------------------------------------------------------------- */

/**
 * Subscribe to auth state. Returns the unsubscribe function through a promise,
 * because the SDK itself is loaded lazily.
 *
 * Anonymous learners arrive as a User with `isAnonymous === true`, not as
 * null. Callers that only care about real accounts must check that flag.
 */
export async function onUser(cb: (user: User | null) => void): Promise<() => void> {
  const { onAuthStateChanged } = await import("firebase/auth");
  const auth = await getAuthClient();
  return onAuthStateChanged(auth, (user) => {
    syncHint(user);
    cb(user);
  });
}

/** Current user once auth has finished restoring from storage. */
export async function currentUser(): Promise<User | null> {
  const auth = await getAuthClient();
  await auth.authStateReady();
  return auth.currentUser;
}

/** True when there is a signed-in, non-anonymous account. */
export async function isSignedIn(): Promise<boolean> {
  const user = await currentUser();
  return !!user && !user.isAnonymous;
}

export async function signOutUser(): Promise<void> {
  const { signOut } = await import("firebase/auth");
  const auth = await getAuthClient();
  await signOut(auth);
  clearHint();
  // The signed-in learner's progress and private notes were mirrored into this
  // browser. Left behind, the next person to sign in here had them merged into
  // their own account on first sync -- and, flagged as already hydrated,
  // never pulled their own. Signed out, the device starts clean.
  const { clearLocal } = await import("../progress/local");
  clearLocal();
}

/* -------------------------------------------------------------------------- */
/* OAuth providers                                                             */
/* -------------------------------------------------------------------------- */

type OAuthName = "google" | "github";

const POPUP_UNAVAILABLE = new Set([
  "auth/popup-blocked",
  "auth/operation-not-supported-in-this-environment",
  "auth/cancelled-popup-request",
]);

/**
 * Popup sign-in, falling back to a full-page redirect.
 *
 * Popups give the better desktop flow but are blocked outright by some in-app
 * browsers (Instagram, LinkedIn) and by strict popup blockers. Only those
 * specific failures trigger the redirect fallback -- a learner who
 * deliberately closed the popup should not then be navigated away.
 */
async function oauthSignIn(name: OAuthName): Promise<UserCredential | null> {
  const mod = await import("firebase/auth");
  const auth = await getAuthClient();

  const provider =
    name === "google" ? new mod.GoogleAuthProvider() : new mod.GithubAuthProvider();

  if (name === "github") provider.addScope("read:user");
  provider.setCustomParameters({ prompt: "select_account" });

  const anon = auth.currentUser?.isAnonymous ? auth.currentUser : null;

  try {
    // An anonymous learner keeps their uid -- and so all their progress -- by
    // linking the provider rather than signing in fresh.
    const cred = anon
      ? await mod.linkWithPopup(anon, provider)
      : await mod.signInWithPopup(auth, provider);
    await ensureProfile(cred.user);
    syncHint(cred.user);
    return cred;
  } catch (err) {
    const code = (err as { code?: string })?.code ?? "";

    // The anonymous session's credential already belongs to a real account.
    // That progress cannot be merged automatically, so fall through to a
    // normal sign-in and let the Phase 2 merge step reconcile it.
    if (anon && code === "auth/credential-already-in-use") {
      const cred = await mod.signInWithPopup(auth, provider);
      await ensureProfile(cred.user);
      syncHint(cred.user);
      return cred;
    }

    if (POPUP_UNAVAILABLE.has(code)) {
      await mod.signInWithRedirect(auth, provider);
      return null; // the page is navigating away
    }
    throw err;
  }
}

export const signInWithGoogle = () => oauthSignIn("google");
export const signInWithGithub = () => oauthSignIn("github");

/**
 * Finish a redirect-based sign-in. Call once on load from any page that can
 * start OAuth; resolves to null on an ordinary (non-redirect) load.
 */
export async function completeRedirectSignIn(): Promise<UserCredential | null> {
  const { getRedirectResult } = await import("firebase/auth");
  const auth = await getAuthClient();
  const cred = await getRedirectResult(auth);
  if (cred) {
    await ensureProfile(cred.user);
    syncHint(cred.user);
  }
  return cred;
}

/* -------------------------------------------------------------------------- */
/* Email + password                                                            */
/* -------------------------------------------------------------------------- */

export async function signUpWithEmail(
  email: string,
  password: string,
  displayName?: string
): Promise<UserCredential> {
  const mod = await import("firebase/auth");
  const auth = await getAuthClient();
  const anon = auth.currentUser?.isAnonymous ? auth.currentUser : null;

  let cred: UserCredential;
  if (anon) {
    const credential = mod.EmailAuthProvider.credential(email, password);
    cred = await mod.linkWithCredential(anon, credential);
  } else {
    cred = await mod.createUserWithEmailAndPassword(auth, email, password);
  }

  if (displayName) await mod.updateProfile(cred.user, { displayName });
  // The account exists by now. A failed verification email (rate limit,
  // network) must not turn that into an error -- the learner would retry and
  // be told the address is already in use. They can resend from the
  // verify-email page.
  await sendVerification().catch((err) =>
    console.warn("[auth] verification email not sent:", err),
  );
  await ensureProfile(cred.user);
  syncHint(cred.user);
  return cred;
}

export async function signInWithEmail(
  email: string,
  password: string
): Promise<UserCredential> {
  const { signInWithEmailAndPassword } = await import("firebase/auth");
  const auth = await getAuthClient();
  const cred = await signInWithEmailAndPassword(auth, email, password);
  await ensureProfile(cred.user);
  syncHint(cred.user);
  return cred;
}

export async function sendPasswordReset(email: string): Promise<void> {
  const { sendPasswordResetEmail } = await import("firebase/auth");
  const auth = await getAuthClient();
  await sendPasswordResetEmail(auth, email);
}

/** (Re)send the verification email to the signed-in user. */
export async function sendVerification(): Promise<void> {
  const { sendEmailVerification } = await import("firebase/auth");
  const auth = await getAuthClient();
  const user = auth.currentUser;
  if (!user || user.emailVerified) return;
  await sendEmailVerification(user, { url: `${window.location.origin}/profile` });
}

/* -------------------------------------------------------------------------- */
/* Accounts vs. guests                                                         */
/* -------------------------------------------------------------------------- */

/**
 * The signed-in account, or null for a guest.
 *
 * "Account" means Google, GitHub or email+password. Anonymous sessions do not
 * count, and nothing in the site creates one: a guest's progress lives purely
 * in localStorage and only reaches Firestore once they sign in. That keeps
 * reading the site free of any Auth record, and keeps the database to real
 * users rather than one row per visitor.
 *
 * Never triggers a sign-in. It resolves once auth has restored whatever
 * session already exists, so it is safe to call from a content page.
 */
export async function signedInAccount(): Promise<User | null> {
  const auth = await getAuthClient();
  await auth.authStateReady();
  const user = auth.currentUser;
  return user && !user.isAnonymous ? user : null;
}

/* -------------------------------------------------------------------------- */
/* Profile document                                                            */
/* -------------------------------------------------------------------------- */

/** Locale prefix of the current URL, e.g. "hi" on /hi/tutorials/..., else "en". */
function currentLocale(): string {
  const seg = window.location.pathname.split("/")[1] ?? "";
  return ["zh-cn", "hi", "es", "ja"].includes(seg) ? seg : "en";
}

/**
 * Create or refresh `users/{uid}`.
 *
 * Merged, so a returning learner keeps `createdAt` and their settings. The
 * field set is kept in sync with `validProfile()` in
 * firebase/firestore.rules -- adding a field here without adding it there
 * makes every write fail.
 */
export async function ensureProfile(user: User): Promise<void> {
  if (user.isAnonymous) return;

  const { doc, getDoc, setDoc, serverTimestamp } = await import("firebase/firestore");
  const db = await getDb();
  const ref = doc(db, "users", user.uid);
  const snap = await getDoc(ref);

  await setDoc(
    ref,
    {
      uid: user.uid,
      email: user.email ?? "",
      displayName: user.displayName ?? "",
      photoURL: photoOf(user),
      locale: currentLocale(),
      providers: user.providerData.map((p) => p.providerId),
      ...(snap.exists() ? {} : { createdAt: serverTimestamp(), settings: {} }),
      updatedAt: serverTimestamp(),
    },
    { merge: true }
  );
}

/** Update the display name on both the Auth record and the profile doc. */
export async function updateDisplayName(displayName: string): Promise<void> {
  const { updateProfile } = await import("firebase/auth");
  const auth = await getAuthClient();
  const user = auth.currentUser;
  if (!user) throw new Error("not signed in");
  await updateProfile(user, { displayName });
  await ensureProfile(user);
  syncHint(user);
}

/* -------------------------------------------------------------------------- */
/* Account removal + export                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Delete the account and everything that belongs to it.
 *
 * The work happens on the server (app/api/delete-account), which can reach
 * what the browser cannot: the public leaderboard row and graded attempts.
 * Issued certificates are kept -- they are public credentials others may
 * already have checked -- and the profile copy says so.
 *
 * Until the server is configured (no service account on the deployment) it
 * answers "server/not-configured", and this falls back to deleting what the
 * rules let the owner delete, then the Auth user. The fallback cannot remove
 * a leaderboard row, which is why the server path is the real one.
 */

/** Per-user stats documents the owner may delete. `certificates` is
    server-written and read-only to its owner, so it is not in this list. */
const USER_STATS_DOCS = ["bookmarks", "quizzes", "notes", "summary"];

/**
 * Firebase refuses to delete an account unless the sign-in is recent (about
 * five minutes). Checked before anything is removed, so a stale session is
 * told to sign in again instead of losing its data and keeping its account.
 */
const RECENT_SIGN_IN_MS = 5 * 60 * 1000;

export async function deleteAccount(): Promise<void> {
  const auth = await getAuthClient();
  const user = auth.currentUser;
  if (!user) throw new Error("not signed in");

  const signedInAt = Date.parse(user.metadata.lastSignInTime ?? "");
  if (!Number.isFinite(signedInAt) || Date.now() - signedInAt > RECENT_SIGN_IN_MS) {
    throw Object.assign(new Error("sign in again before deleting"), {
      code: "auth/requires-recent-login",
    });
  }

  const { callApi } = await import("./client");
  try {
    await callApi("delete-account");
  } catch (err) {
    if ((err as { code?: string }).code !== "server/not-configured") throw err;
    await deleteFromClient(user);
  }

  // The browser's own copy goes too. Leaving it would mean the next account
  // created here inherits a deleted one's reading history on first sync.
  const { clearLocal } = await import("../progress/local");
  clearLocal();
  clearHint();
  // The server removed the Auth user; drop the local session that pointed
  // at it. Harmless if the fallback already did.
  const { signOut } = await import("firebase/auth");
  await signOut(auth).catch(() => {});
}

async function deleteFromClient(user: User): Promise<void> {
  const { doc, deleteDoc, collection, getDocs, writeBatch } = await import(
    "firebase/firestore"
  );
  const db = await getDb();
  const uid = user.uid;

  // One batch for the lot: a half-deleted account is worse than a failed one.
  const batch = writeBatch(db);
  const progress = await getDocs(collection(db, "users", uid, "progress"));
  progress.forEach((entry) => batch.delete(entry.ref));
  for (const name of USER_STATS_DOCS) {
    batch.delete(doc(db, "users", uid, "stats", name));
  }
  await batch.commit();
  // Outside the batch: refused where the rules for it are not deployed yet.
  await deleteDoc(doc(db, "users", uid, "stats", "exercises")).catch(() => {});
  await deleteDoc(doc(db, "users", uid));
  await user.delete();
}

/** Everything the site stores about the signed-in user, as a JSON blob. */
export async function exportUserData(): Promise<Record<string, unknown>> {
  const auth = await getAuthClient();
  const user = auth.currentUser;
  if (!user) throw new Error("not signed in");

  const { doc, getDoc, collection, getDocs } = await import("firebase/firestore");
  const db = await getDb();
  const snap = await getDoc(doc(db, "users", user.uid));

  // The profile says the export holds progress, quiz results, bookmarks and
  // notes; it used to hold the profile document alone.
  const stats: Record<string, unknown> = {};
  for (const name of [...USER_STATS_DOCS, "exercises", "certificates"]) {
    // Per document: one the rules do not (yet) allow should not sink the
    // whole export.
    const entry = await getDoc(doc(db, "users", user.uid, "stats", name)).catch(() => null);
    if (entry?.exists()) stats[name] = entry.data();
  }
  const cloudProgress = await getDocs(collection(db, "users", user.uid, "progress"));
  const { read } = await import("../progress/local");

  return {
    exportedAt: new Date().toISOString(),
    account: {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      emailVerified: user.emailVerified,
      providers: user.providerData.map((p) => p.providerId),
      createdAt: user.metadata.creationTime,
      lastSignInAt: user.metadata.lastSignInTime,
    },
    profile: snap.exists() ? snap.data() : null,
    stats,
    progress: Object.fromEntries(cloudProgress.docs.map((d) => [d.id, d.data()])),
    /** What this browser holds, which includes anything not yet synced. */
    thisDevice: read(),
  };
}

/* -------------------------------------------------------------------------- */
/* Errors                                                                      */
/* -------------------------------------------------------------------------- */

/**
 * Firebase error code -> `pch.authErr*` translation key.
 *
 * Deliberately vague for credential failures: telling "no such user" apart
 * from "wrong password" hands an attacker a free account-enumeration oracle.
 * Firebase's own email-enumeration protection returns `auth/invalid-credential`
 * for both, and this keeps the two indistinguishable in the UI as well.
 */
export const AUTH_ERROR_KEYS: Record<string, string> = {
  "auth/invalid-credential": "pch.authErrInvalidCredential",
  "auth/wrong-password": "pch.authErrInvalidCredential",
  "auth/user-not-found": "pch.authErrInvalidCredential",
  "auth/invalid-email": "pch.authErrInvalidEmail",
  "auth/email-already-in-use": "pch.authErrEmailInUse",
  "auth/weak-password": "pch.authErrWeakPassword",
  "auth/too-many-requests": "pch.authErrTooManyRequests",
  "auth/network-request-failed": "pch.authErrNetwork",
  "auth/popup-closed-by-user": "pch.authErrPopupClosed",
  "auth/account-exists-with-different-credential": "pch.authErrDifferentProvider",
  "auth/requires-recent-login": "pch.authErrRecentLogin",
  "auth/user-disabled": "pch.authErrDisabled",
  "auth/operation-not-allowed": "pch.authErrProviderDisabled",
};

/** Translation key for any thrown auth error, with a generic fallback. */
export function authErrorKey(err: unknown): string {
  const code = (err as { code?: string })?.code ?? "";
  return AUTH_ERROR_KEYS[code] ?? "pch.authErrGeneric";
}

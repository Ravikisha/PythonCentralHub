import {
  db,
  adminAuth,
  post,
  HttpError,
  requireCaller,
  RECENT_AUTH_MS,
} from "@/lib/server/admin";
import { deleteRatingsBy } from "@/lib/server/ratings";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/delete-account/  {}
 *
 * Removes an account and everything that belongs to it, with the Admin SDK.
 *
 * The browser could not do this alone: the rules give it no delete on the
 * public leaderboard row or on graded attempts, so a deleted learner's name
 * and photo stayed ranked for good. Here the order is data first, account
 * last, and it all happens on the server, so the browser never ends up with a
 * live account whose progress is already gone.
 *
 * Issued certificates are kept on purpose: they are public credentials that
 * others may already have checked. The profile copy says so.
 *
 * The sign-in must be recent -- the same rule Firebase applies to deleting
 * from the client -- so a token lifted from an old session cannot erase an
 * account.
 */
export const POST = post(async (req) => {
  const caller = await requireCaller(req);

  const signedInAt = (caller.auth_time ?? 0) * 1000;
  if (Date.now() - signedInAt > RECENT_AUTH_MS) {
    throw new HttpError(
      401,
      "For security, sign in again before making this change.",
      "auth/requires-recent-login",
    );
  }

  const store = db();
  const uid = caller.uid;

  const attempts = await store.collection("attempts").where("uid", "==", uid).get();
  const batch = store.batch();
  attempts.forEach((doc) => batch.delete(doc.ref));
  batch.delete(store.doc(`leaderboard/${uid}`));
  await batch.commit();

  // Their course ratings, taken back out of each course's average.
  await deleteRatingsBy(store, uid);

  // The profile document and every subcollection under it.
  await store.recursiveDelete(store.doc(`users/${uid}`));

  await adminAuth().deleteUser(uid);
  return { deleted: true };
});

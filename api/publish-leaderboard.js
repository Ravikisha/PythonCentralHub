/**
 * POST /api/publish-leaderboard  {}
 *
 * Recomputes the caller's public leaderboard entry from server-side records.
 *
 * Self-reported standings would be worthless -- a leaderboard is the one
 * surface where being wrong is the whole problem -- so the numbers are read
 * back out of `users/{uid}/progress/*` and the certificate index rather than
 * taken from the request. The client may ask for a refresh; it may not say
 * what the answer is.
 *
 * Opt-in only. Nobody appears on a public board because they signed up.
 */
import { db, handler, requireVerifiedCaller, FieldValue } from "./_lib/admin.js";

export default handler(async (req) => {
  const caller = await requireVerifiedCaller(req);
  const store = db();

  const [profileSnap, progressSnap, certSnap] = await Promise.all([
    store.doc(`users/${caller.uid}`).get(),
    store.collection(`users/${caller.uid}/progress`).get(),
    store.doc(`users/${caller.uid}/stats/certificates`).get(),
  ]);

  const entryRef = store.doc(`leaderboard/${caller.uid}`);

  // Opting out removes the entry outright rather than hiding it, so "off"
  // means the row is gone rather than merely unlisted.
  if (profileSnap.data()?.settings?.leaderboard !== true) {
    await entryRef.delete();
    return { listed: false };
  }

  let pages = 0;
  progressSnap.forEach((d) => {
    pages += (d.data().completed || []).length;
  });
  const certificates = (certSnap.data()?.items || []).length;

  // Mirrors XP_PER_* in src/lib/progress/awards.ts. Quizzes are left out on
  // purpose: their answers ship in the page source, so they are not evidence
  // of anything and must not move a public ranking.
  const xp = pages * 10 + certificates * 250;

  await entryRef.set({
    uid: caller.uid,
    displayName: caller.name || "Anonymous learner",
    photoURL: caller.picture || "",
    pages,
    certificates,
    xp,
    updatedAt: FieldValue.serverTimestamp(),
  });

  return { listed: true, xp, pages, certificates };
});

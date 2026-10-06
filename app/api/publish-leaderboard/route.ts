import {
  db,
  post,
  requireVerifiedCaller,
  countRealLessons,
  FieldValue,
} from "@/lib/server/admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/publish-leaderboard/  {}
 *
 * Recomputes the caller's public leaderboard entry from records the caller
 * cannot inflate:
 *
 *  - lessons: only ids that are real lessons of the course they are filed
 *    under, each counted once. Raw array lengths let one learner write five
 *    thousand invented ids and top the board.
 *  - certificates: counted in `certificates/`, which only the issuing
 *    endpoint writes -- not in the learner's own index.
 *
 * Opt-in only. Nobody appears on a public board because they signed up.
 * The same entry is the learner's public profile (/u/?id=<uid>): lessons per
 * course and their certificates, nothing else.
 */
export const POST = post(async (req) => {
  const caller = await requireVerifiedCaller(req);
  const store = db();

  const [profileSnap, progressSnap, certSnap] = await Promise.all([
    store.doc(`users/${caller.uid}`).get(),
    store.collection(`users/${caller.uid}/progress`).get(),
    store.collection("certificates").where("uid", "==", caller.uid).get(),
  ]);

  const entryRef = store.doc(`leaderboard/${caller.uid}`);

  // Opting out removes the entry outright rather than hiding it.
  if (profileSnap.data()?.settings?.leaderboard !== true) {
    await entryRef.delete();
    return { listed: false };
  }

  let pages = 0;
  // Per course too, for the public profile (/u/?id=...). Same real-lesson
  // count as the total, so it cannot be padded either.
  const courses: Record<string, number> = {};
  progressSnap.forEach((d) => {
    const n = countRealLessons(d.id, d.data().completed);
    pages += n;
    if (n) courses[d.id] = n;
  });
  const certificates = certSnap.size;
  // Certificates are public by id already; a learner who opted in to the
  // board shows theirs on the profile, newest first.
  const certificateList = certSnap.docs
    .map((d) => {
      const c = d.data();
      return {
        id: d.id,
        module: String(c.module ?? ""),
        kind: (c.kind as string | undefined) ?? "assessment",
        issuedAt: c.issuedAt?.toMillis?.() ?? 0,
      };
    })
    .sort((a, b) => b.issuedAt - a.issuedAt)
    .slice(0, 20);

  // Mirrors XP_PER_* in src/lib/progress/awards.ts. Quizzes are left out on
  // purpose: their answers ship in the page source.
  const xp = pages * 10 + certificates * 250;

  await entryRef.set({
    uid: caller.uid,
    displayName: caller.name || "A learner",
    photoURL: caller.picture || "",
    pages,
    courses,
    certificates,
    certificateList,
    xp,
    updatedAt: FieldValue.serverTimestamp(),
  });

  return { listed: true, xp, pages, certificates };
});

/**
 * POST /api/issue-certificate  { module }
 *
 * Issues a certificate only when the server's own records support it. Nothing
 * the client sends is trusted beyond the module name: completion is read from
 * `users/{uid}/progress/{module}`, the denominator from `config/modules`, and
 * the exam result from `attempts/` -- which only the grader can write.
 */
import {
  db,
  handler,
  HttpError,
  requireVerifiedCaller,
  requireModuleSlug,
  certificateId,
  FieldValue,
  REQUIRED_COMPLETION,
} from "./_lib/admin.js";

export default handler(async (req, body) => {
  const caller = await requireVerifiedCaller(req);
  const moduleSlug = requireModuleSlug(body.module);
  const store = db();

  const [configSnap, progressSnap, attemptSnap, certIndexSnap] = await Promise.all([
    store.doc("config/modules").get(),
    store.doc(`users/${caller.uid}/progress/${moduleSlug}`).get(),
    store.doc(`attempts/${caller.uid}_${moduleSlug}`).get(),
    store.doc(`users/${caller.uid}/stats/certificates`).get(),
  ]);

  const counts = configSnap.data()?.counts || {};
  const total = counts[moduleSlug];
  if (!total) throw new HttpError(404, "Unknown module.");

  // Re-issuing would mint a second id for the same achievement and leave the
  // first one verifiable but orphaned.
  const existing = (certIndexSnap.data()?.items || []).find((c) => c.module === moduleSlug);
  if (existing) return { certificateId: existing.certificateId, existing: true };

  const completed = (progressSnap.data()?.completed || []).length;
  if (completed / total < REQUIRED_COMPLETION) {
    throw new HttpError(
      412,
      `Complete ${Math.ceil(total * REQUIRED_COMPLETION)} of ${total} pages first.`
    );
  }

  const attempt = attemptSnap.data();
  if (!attempt?.passed) {
    throw new HttpError(412, "Pass the final assessment first.");
  }

  const certId = certificateId();
  const batch = store.batch();

  batch.set(store.doc(`certificates/${certId}`), {
    certificateId: certId,
    uid: caller.uid,
    holder: caller.name || caller.email,
    email: caller.email,
    module: moduleSlug,
    score: attempt.best ?? attempt.score,
    pagesCompleted: completed,
    pagesTotal: total,
    issuedAt: FieldValue.serverTimestamp(),
  });

  batch.set(
    store.doc(`users/${caller.uid}/stats/certificates`),
    {
      items: FieldValue.arrayUnion({
        certificateId: certId,
        module: moduleSlug,
        score: attempt.best ?? attempt.score,
        issuedAt: Date.now(),
      }),
    },
    { merge: true }
  );

  await batch.commit();
  return { certificateId: certId, existing: false };
});

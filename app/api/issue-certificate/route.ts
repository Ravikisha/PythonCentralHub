import {
  db,
  post,
  HttpError,
  requireVerifiedCaller,
  requireModuleSlug,
  certificateId,
  countRealLessons,
  lessonsByCourse,
  FieldValue,
  REQUIRED_COMPLETION,
} from "@/lib/server/admin";
import { certificateBlocker, type CertificateKind } from "@/lib/server/grading";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/issue-certificate/  { module, kind? }
 *
 * Issues a certificate only when the server's own records support it. Two
 * kinds:
 *
 *  - "assessment" (the default): lessons done AND the final assessment
 *    passed. Carries the score.
 *  - "completion": lessons done, no assessment. Says so on its face and
 *    carries no score. A learner can hold one of each per course.
 *
 * Certificates issued before kinds existed have no `kind` and are all
 * assessment certificates.
 *
 *  - Completion counts only ids that are real lessons of this course. The
 *    progress document is written by its owner, so its raw length proved
 *    nothing: 171 invented ids used to pass the 90% gate.
 *  - The denominator is the course as it ships, read from the content.
 *  - "Already issued" is looked up in `certificates/`, which only this code
 *    writes, not in the learner-writable index.
 *  - The public certificate carries no email address: anyone holding the id
 *    can read it.
 */
export const POST = post(async (req, body) => {
  const caller = await requireVerifiedCaller(req);
  const moduleSlug = requireModuleSlug(body.module);
  const kind: CertificateKind = body.kind === "completion" ? "completion" : "assessment";
  const store = db();

  const total = lessonsByCourse().get(moduleSlug)?.size ?? 0;
  if (!total) throw new HttpError(404, "Unknown course.");

  const [progressSnap, attemptSnap, issued] = await Promise.all([
    store.doc(`users/${caller.uid}/progress/${moduleSlug}`).get(),
    store.doc(`attempts/${caller.uid}_${moduleSlug}`).get(),
    store
      .collection("certificates")
      .where("uid", "==", caller.uid)
      .where("module", "==", moduleSlug)
      .get(),
  ]);

  // Re-issuing would mint a second id for the same achievement and leave the
  // first one verifiable but orphaned.
  const held = issued.docs.find((d) => (d.data().kind ?? "assessment") === kind);
  if (held) {
    return { certificateId: held.id, existing: true, kind };
  }

  const completed = countRealLessons(moduleSlug, progressSnap.data()?.completed);
  const attempt = attemptSnap.data();
  const blocker = certificateBlocker({
    kind,
    completed,
    total,
    share: REQUIRED_COMPLETION,
    assessmentPassed: attempt?.passed === true,
  });
  if (blocker) throw new HttpError(412, blocker);

  const certId = certificateId();
  const score =
    kind === "assessment" ? ((attempt!.best ?? attempt!.score) as number) : null;
  const batch = store.batch();

  batch.set(store.doc(`certificates/${certId}`), {
    certificateId: certId,
    uid: caller.uid,
    holder: caller.name || caller.email || "Python Central Hub learner",
    module: moduleSlug,
    kind,
    score,
    pagesCompleted: completed,
    pagesTotal: total,
    issuedAt: FieldValue.serverTimestamp(),
  });

  // The learner's own index, for listing on their profile. Written only here:
  // the rules make it read-only to its owner.
  batch.set(
    store.doc(`users/${caller.uid}/stats/certificates`),
    {
      items: FieldValue.arrayUnion({
        certificateId: certId,
        module: moduleSlug,
        kind,
        score,
        issuedAt: Date.now(),
      }),
    },
    { merge: true },
  );

  await batch.commit();
  return { certificateId: certId, existing: false, kind };
});

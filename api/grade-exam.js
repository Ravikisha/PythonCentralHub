/**
 * POST /api/grade-exam  { module, answers: number[] }
 *
 * Marks a final assessment against a key the browser has never seen.
 *
 * What comes back depends on the result, because the two cases want opposite
 * things:
 *
 *   passed  -- the learner is done with this exam, so send every explanation.
 *              There is nothing left to game and the explanations are the most
 *              useful part.
 *   failed  -- they will sit it again, so send only which questions were
 *              wrong. Explanations routinely state the correct answer, and
 *              handing those over would make the retry a formality.
 */
import {
  db,
  handler,
  HttpError,
  requireVerifiedCaller,
  requireModuleSlug,
  FieldValue,
  DEFAULT_PASS_SCORE,
  ATTEMPT_COOLDOWN_MS,
} from "./_lib/admin.js";

export default handler(async (req, body) => {
  const caller = await requireVerifiedCaller(req);
  const moduleSlug = requireModuleSlug(body.module);
  const answers = body.answers;

  if (!Array.isArray(answers) || answers.length > 200) {
    throw new HttpError(400, "Answers must be a list.");
  }

  const store = db();
  const [examSnap, keySnap] = await Promise.all([
    store.doc(`exams/${moduleSlug}`).get(),
    store.doc(`examKeys/${moduleSlug}`).get(),
  ]);

  if (!examSnap.exists || !keySnap.exists) {
    throw new HttpError(404, "No exam for that module yet.");
  }

  const exam = examSnap.data();
  const key = keySnap.data().answers || [];

  if (answers.length !== key.length) {
    throw new HttpError(400, "Answer one question per item.");
  }

  const attemptRef = store.doc(`attempts/${caller.uid}_${moduleSlug}`);
  const previous = await attemptRef.get();

  // Rate limit. Without it the exam is a brute force: a client could resubmit
  // permutations until something passes.
  if (previous.exists) {
    const last = previous.data().gradedAt?.toMillis?.() ?? 0;
    const wait = ATTEMPT_COOLDOWN_MS - (Date.now() - last);
    if (wait > 0) {
      throw new HttpError(429, `Try again in ${Math.ceil(wait / 60000)} minute(s).`);
    }
  }

  const wrong = [];
  let correct = 0;
  key.forEach((expected, i) => {
    if (answers[i] === expected) correct += 1;
    else wrong.push(i);
  });

  const score = Math.round((correct / key.length) * 100);
  const passScore = exam.passScore ?? DEFAULT_PASS_SCORE;
  const passed = score >= passScore;
  const best = Math.max(score, previous.exists ? previous.data().best ?? 0 : 0);

  await attemptRef.set(
    {
      uid: caller.uid,
      module: moduleSlug,
      score,
      best,
      passed: passed || (previous.exists ? !!previous.data().passed : false),
      attempts: FieldValue.increment(1),
      gradedAt: FieldValue.serverTimestamp(),
    },
    { merge: true }
  );

  return {
    score,
    passScore,
    passed,
    correct,
    total: key.length,
    wrong,
    explanations: passed ? keySnap.data().explanations ?? [] : [],
  };
});

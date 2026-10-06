import {
  db,
  post,
  HttpError,
  requireVerifiedCaller,
  requireModuleSlug,
  FieldValue,
  DEFAULT_PASS_SCORE,
  ATTEMPT_COOLDOWN_MS,
} from "@/lib/server/admin";
import { cooldownRemaining, grade, parseAnswers } from "@/lib/server/grading";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/grade-exam/  { module, answers: number[] }
 *
 * Marks a final assessment against a key the browser has never seen.
 *
 *   passed -- send every explanation: nothing is left to game, and the
 *             explanations are the most useful part.
 *   failed -- send the score and nothing else. It used to send which
 *             questions were wrong, which recovers the whole key in two or
 *             three attempts on four-option questions.
 *
 * The cooldown check and the attempt write happen in one transaction.
 * Separately, fifty parallel submissions all read "no recent attempt" and
 * were all graded.
 */
export const POST = post(async (req, body) => {
  const caller = await requireVerifiedCaller(req);
  const moduleSlug = requireModuleSlug(body.module);
  const answers = parseAnswers(body.answers);
  if (!answers) {
    throw new HttpError(400, "Answers must be a list of option numbers.");
  }

  const store = db();
  const [examSnap, keySnap] = await Promise.all([
    store.doc(`exams/${moduleSlug}`).get(),
    store.doc(`examKeys/${moduleSlug}`).get(),
  ]);
  if (!examSnap.exists || !keySnap.exists) {
    throw new HttpError(404, "This course does not have a final assessment yet.");
  }

  const exam = examSnap.data() ?? {};
  const keyData = keySnap.data() ?? {};
  const key = (keyData.answers ?? []) as number[];
  if (answers.length !== key.length) {
    throw new HttpError(400, "Answer one question per item.");
  }

  const passScore = (exam.passScore as number | undefined) ?? DEFAULT_PASS_SCORE;
  const { correct, score, passed } = grade(answers, key, passScore);

  const attemptRef = store.doc(`attempts/${caller.uid}_${moduleSlug}`);

  await store.runTransaction(async (tx) => {
    const previous = await tx.get(attemptRef);
    const prev = previous.exists ? (previous.data() ?? {}) : {};

    const last = prev.gradedAt?.toMillis?.() ?? 0;
    const wait = cooldownRemaining(last, ATTEMPT_COOLDOWN_MS);
    if (wait > 0) {
      throw new HttpError(429, `Try again in ${Math.ceil(wait / 60000)} minute(s).`);
    }

    tx.set(
      attemptRef,
      {
        uid: caller.uid,
        module: moduleSlug,
        score,
        best: Math.max(score, (prev.best as number | undefined) ?? 0),
        passed: passed || prev.passed === true,
        attempts: FieldValue.increment(1),
        gradedAt: FieldValue.serverTimestamp(),
      },
      { merge: true },
    );
  });

  return {
    score,
    passScore,
    passed,
    correct,
    total: key.length,
    explanations: passed ? (keyData.explanations ?? []) : [],
  };
});

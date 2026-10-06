/**
 * The decisions behind assessments and certificates, without Firebase.
 *
 * The route handlers (app/api/grade-exam, app/api/issue-certificate) read and
 * write Firestore; every rule about what passes and what earns a certificate
 * lives here, as plain functions, so it can be unit-tested (lib/server/
 * grading.test.ts) without a database.
 */

export type CertificateKind = "assessment" | "completion";

/** A list of option numbers, one per question, or null if it is not one. */
export function parseAnswers(value: unknown): number[] | null {
  if (
    !Array.isArray(value) ||
    value.length > 200 ||
    !value.every((a) => Number.isInteger(a) && a >= 0 && a < 26)
  ) {
    return null;
  }
  return value as number[];
}

export interface Grade {
  correct: number;
  total: number;
  /** Whole percent, rounded. */
  score: number;
  passed: boolean;
}

/** Mark answers against a key. Lengths must match; the caller checks. */
export function grade(answers: number[], key: number[], passScore: number): Grade {
  let correct = 0;
  key.forEach((expected, i) => {
    if (answers[i] === expected) correct += 1;
  });
  const score = key.length ? Math.round((correct / key.length) * 100) : 0;
  return { correct, total: key.length, score, passed: score >= passScore };
}

/** Milliseconds still to wait before another attempt; 0 or less means go. */
export function cooldownRemaining(lastAttemptMs: number, cooldownMs: number, now = Date.now()): number {
  return cooldownMs - (now - lastAttemptMs);
}

/** Distinct ids in `claimed` that are in `real`, case-insensitively. */
export function countReal(real: Set<string> | undefined, claimed: unknown): number {
  if (!real || !Array.isArray(claimed)) return 0;
  const seen = new Set<string>();
  for (const id of claimed) {
    if (typeof id === "string" && real.has(id.toLowerCase())) seen.add(id.toLowerCase());
  }
  return seen.size;
}

/** Lessons needed for a certificate out of `total`. */
export function lessonsNeeded(total: number, share: number): number {
  return Math.ceil(total * share);
}

/**
 * Whether a certificate of this kind can be issued, and if not, the reason
 * to show the learner.
 */
export function certificateBlocker(input: {
  kind: CertificateKind;
  completed: number;
  total: number;
  share: number;
  assessmentPassed: boolean;
}): string | null {
  const needed = lessonsNeeded(input.total, input.share);
  if (input.completed < needed) {
    return `Complete ${needed} of ${input.total} lessons first.`;
  }
  if (input.kind === "assessment" && !input.assessmentPassed) {
    return "Pass the final assessment first.";
  }
  return null;
}

/**
 * SUPERSEDED -- not deployed.
 *
 * Cloud Functions require the Firebase Blaze plan. This project is on Spark,
 * so the same four endpoints now live in `api/` as Vercel Functions, which the
 * site's existing (free) Vercel hosting runs at no cost. `firebase.json` no
 * longer references this directory.
 *
 * Kept as the Firebase-flavoured reference in case the project ever moves to
 * Blaze. If you change the grading or issuing rules, change them in `api/` --
 * that is the copy that actually runs.
 */

/**
 * Server-side half of the learning platform.
 *
 * Everything in this file exists because the site is statically generated and
 * therefore cannot be trusted with any of it. Two jobs:
 *
 *   gradeExam         marks a final assessment against answers the browser
 *                     has never seen
 *   issueCertificate  mints a certificate only when the progress and score
 *                     actually recorded on the server support it
 *
 * The rule that shapes the design: a client may report what it has read, but
 * never what it has earned. Page completions are self-reported and that is
 * fine -- they are the learner's own notes to themselves. Exam answers and
 * certificates are not, so they live in collections no client can read or
 * write (`examKeys`, `attempts`, `certificates`) and are only ever touched
 * through the Admin SDK here.
 */
const { onCall, HttpsError } = require("firebase-functions/v2/https");
const { onSchedule } = require("firebase-functions/v2/scheduler");
const { initializeApp } = require("firebase-admin/app");
const { getFirestore, FieldValue } = require("firebase-admin/firestore");

initializeApp();
const db = getFirestore();

/** Share of a module's pages that must be complete before a certificate. */
const REQUIRED_COMPLETION = 0.9;

/** Fallback pass mark, when an exam document does not set its own. */
const DEFAULT_PASS_SCORE = 70;

/** Minimum gap between attempts at the same exam. */
const ATTEMPT_COOLDOWN_MS = 10 * 60 * 1000;

/* -------------------------------------------------------------------------- */
/* Helpers                                                                     */
/* -------------------------------------------------------------------------- */

/**
 * The caller's uid, rejecting guests and unverified addresses.
 *
 * Verification matters here and nowhere else on the site: a certificate names
 * an email address, so that address has to be one its holder controls.
 */
function requireVerifiedCaller(request) {
  const auth = request.auth;
  if (!auth) {
    throw new HttpsError("unauthenticated", "Sign in first.");
  }
  if (auth.token.firebase?.sign_in_provider === "anonymous") {
    throw new HttpsError("permission-denied", "Create an account first.");
  }
  if (!auth.token.email_verified) {
    throw new HttpsError("failed-precondition", "Verify your email address first.");
  }
  return auth;
}

/** Reject anything that is not a plain module slug. */
function requireModuleSlug(value) {
  if (typeof value !== "string" || !/^[a-z0-9-]{1,64}$/.test(value)) {
    throw new HttpsError("invalid-argument", "Unknown module.");
  }
  return value;
}

/** Certificate ids are read aloud and pasted into URLs, so: no ambiguity. */
function certificateId() {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no I, O, 0, 1
  let out = "";
  for (let i = 0; i < 12; i += 1) {
    out += alphabet[Math.floor(Math.random() * alphabet.length)];
  }
  return `${out.slice(0, 4)}-${out.slice(4, 8)}-${out.slice(8)}`;
}

/* -------------------------------------------------------------------------- */
/* gradeExam                                                                   */
/* -------------------------------------------------------------------------- */

/**
 * Mark a final assessment.
 *
 * The browser posts only the chosen option indexes and never receives the key.
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
exports.gradeExam = onCall(async (request) => {
  const auth = requireVerifiedCaller(request);
  const moduleSlug = requireModuleSlug(request.data?.module);
  const answers = request.data?.answers;

  if (!Array.isArray(answers) || answers.length > 200) {
    throw new HttpsError("invalid-argument", "Answers must be a list.");
  }

  const [examSnap, keySnap] = await Promise.all([
    db.doc(`exams/${moduleSlug}`).get(),
    db.doc(`examKeys/${moduleSlug}`).get(),
  ]);

  if (!examSnap.exists || !keySnap.exists) {
    throw new HttpsError("not-found", "No exam for that module yet.");
  }

  const exam = examSnap.data();
  const key = keySnap.data().answers || [];

  if (answers.length !== key.length) {
    throw new HttpsError("invalid-argument", "Answer one question per item.");
  }

  const attemptRef = db.doc(`attempts/${auth.uid}_${moduleSlug}`);
  const previous = await attemptRef.get();

  // Rate limit. Without it the exam is a 30-question brute force: a client
  // could resubmit permutations until something passes.
  if (previous.exists) {
    const last = previous.data().gradedAt?.toMillis?.() ?? 0;
    const wait = ATTEMPT_COOLDOWN_MS - (Date.now() - last);
    if (wait > 0) {
      throw new HttpsError(
        "resource-exhausted",
        `Try again in ${Math.ceil(wait / 60000)} minute(s).`
      );
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

  const best = Math.max(score, previous.exists ? (previous.data().best ?? 0) : 0);

  await attemptRef.set(
    {
      uid: auth.uid,
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

/* -------------------------------------------------------------------------- */
/* issueCertificate                                                            */
/* -------------------------------------------------------------------------- */

/**
 * Issue a certificate, if the server's own records support it.
 *
 * Nothing the client sends is trusted beyond the module name. Completion is
 * read from `users/{uid}/progress/{module}`, the denominator from
 * `config/modules` (seeded at deploy time from the build manifest), and the
 * exam result from `attempts/` -- which only this function can write.
 */
exports.issueCertificate = onCall(async (request) => {
  const auth = requireVerifiedCaller(request);
  const moduleSlug = requireModuleSlug(request.data?.module);

  const [configSnap, progressSnap, attemptSnap, certIndexSnap] = await Promise.all([
    db.doc("config/modules").get(),
    db.doc(`users/${auth.uid}/progress/${moduleSlug}`).get(),
    db.doc(`attempts/${auth.uid}_${moduleSlug}`).get(),
    db.doc(`users/${auth.uid}/stats/certificates`).get(),
  ]);

  const counts = configSnap.data()?.counts || {};
  const total = counts[moduleSlug];
  if (!total) {
    throw new HttpsError("not-found", "Unknown module.");
  }

  // Re-issuing would mint a second id for the same achievement and leave the
  // first one verifiable but orphaned.
  const existing = (certIndexSnap.data()?.items || []).find(
    (c) => c.module === moduleSlug
  );
  if (existing) return { certificateId: existing.certificateId, existing: true };

  const completed = (progressSnap.data()?.completed || []).length;
  const ratio = completed / total;
  if (ratio < REQUIRED_COMPLETION) {
    throw new HttpsError(
      "failed-precondition",
      `Complete ${Math.ceil(total * REQUIRED_COMPLETION)} of ${total} pages first.`
    );
  }

  const attempt = attemptSnap.data();
  if (!attempt?.passed) {
    throw new HttpsError("failed-precondition", "Pass the final assessment first.");
  }

  const certId = certificateId();
  const holder = auth.token.name || auth.token.email;

  const batch = db.batch();
  batch.set(db.doc(`certificates/${certId}`), {
    certificateId: certId,
    uid: auth.uid,
    holder,
    email: auth.token.email,
    module: moduleSlug,
    score: attempt.best ?? attempt.score,
    pagesCompleted: completed,
    pagesTotal: total,
    issuedAt: FieldValue.serverTimestamp(),
  });
  batch.set(
    db.doc(`users/${auth.uid}/stats/certificates`),
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

/* -------------------------------------------------------------------------- */
/* publishLeaderboard                                                          */
/* -------------------------------------------------------------------------- */

/**
 * Recompute this learner's public leaderboard entry from server-side records.
 *
 * Self-reported standings would be worthless -- a leaderboard is the one
 * surface where being wrong is the whole problem -- so the numbers are read
 * back out of `users/{uid}/progress/*` and the certificate index rather than
 * taken from the request. The client may ask for a refresh; it may not say
 * what the answer is.
 *
 * Opt-in only. Nobody appears on a public board because they signed up.
 */
exports.publishLeaderboard = onCall(async (request) => {
  const auth = requireVerifiedCaller(request);

  const [profileSnap, progressSnap, certSnap] = await Promise.all([
    db.doc(`users/${auth.uid}`).get(),
    db.collection(`users/${auth.uid}/progress`).get(),
    db.doc(`users/${auth.uid}/stats/certificates`).get(),
  ]);

  const entryRef = db.doc(`leaderboard/${auth.uid}`);

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
    uid: auth.uid,
    displayName: auth.token.name || "Anonymous learner",
    photoURL: auth.token.picture || "",
    pages,
    certificates,
    xp,
    updatedAt: FieldValue.serverTimestamp(),
  });

  return { listed: true, xp, pages, certificates };
});

/* -------------------------------------------------------------------------- */
/* sendDigests                                                                 */
/* -------------------------------------------------------------------------- */

/**
 * Weekly nudge for learners who are close to a certificate.
 *
 * Delivery goes through the Firebase "Trigger Email from Firestore" extension:
 * this writes a document to `mail/`, the extension sends it. That keeps SMTP
 * credentials out of this codebase entirely -- without the extension installed
 * the documents simply accumulate unsent, which is a visible, harmless failure
 * rather than a silent one.
 *
 * Only writes for people who opted in AND are actually close to something, so
 * the mail is a reminder rather than a newsletter.
 */
exports.sendDigests = onSchedule("every monday 09:00", async () => {
  const configSnap = await db.doc("config/modules").get();
  const counts = configSnap.data()?.counts || {};

  const optedIn = await db.collection("users").where("settings.digest", "==", true).get();

  let queued = 0;

  for (const userDoc of optedIn.docs) {
    const user = userDoc.data();
    if (!user.email) continue;

    const progress = await db.collection(`users/${userDoc.id}/progress`).get();

    const nearly = [];
    progress.forEach((d) => {
      const total = counts[d.id];
      if (!total) return;
      const done = (d.data().completed || []).length;
      const remaining = Math.ceil(total * REQUIRED_COMPLETION) - done;
      if (remaining > 0 && remaining <= 5) {
        nearly.push({ module: d.id, remaining });
      }
    });

    if (!nearly.length) continue;

    const lines = nearly
      .map((n) => `• ${n.module}: ${n.remaining} page(s) to go`)
      .join("\n");

    await db.collection("mail").add({
      to: [user.email],
      message: {
        subject: "You're close to a Python Central Hub certificate",
        text:
          `You're nearly there:\n\n${lines}\n\n` +
          `Pick up where you left off: https://pythoncentralhub.live/dashboard\n\n` +
          `Stop these emails: https://pythoncentralhub.live/profile`,
      },
      createdAt: FieldValue.serverTimestamp(),
    });
    queued += 1;
  }

  console.log(`sendDigests: queued ${queued} message(s)`);
});

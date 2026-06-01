/**
 * Reference Cloud Function for validating reCAPTCHA v3 tokens before allowing
 * a write to Firestore. This is an EXAMPLE — deploy it under your own Firebase
 * Functions project and wire the client forms to POST here instead of writing
 * to Firestore directly, OR call it from a Firestore `onCreate` trigger.
 *
 * Setup:
 *   1. firebase init functions
 *   2. Copy this file to functions/index.js (adjust as needed)
 *   3. Set the secret:  firebase functions:config:set recaptcha.secret="YOUR_SECRET"
 *   4. firebase deploy --only functions
 *
 * The client forms (Contact.astro / Feedback.astro) attach a `recaptchaToken`
 * field. Validate it here; reject low scores / failed verifications.
 */

const functions = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

const MIN_SCORE = 0.5;

async function verifyToken(token) {
  const secret = functions.config().recaptcha.secret;
  const res = await fetch("https://www.google.com/recaptcha/api/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `secret=${encodeURIComponent(secret)}&response=${encodeURIComponent(token)}`,
  });
  const data = await res.json();
  return data.success === true && (data.score ?? 0) >= MIN_SCORE;
}

// HTTPS callable: client posts { collection, payload, recaptchaToken }.
exports.submitForm = functions.https.onCall(async (data) => {
  const { collection, payload, recaptchaToken } = data || {};

  if (!["contact", "feedback"].includes(collection)) {
    throw new functions.https.HttpsError("invalid-argument", "Bad collection.");
  }
  if (!recaptchaToken || !(await verifyToken(recaptchaToken))) {
    throw new functions.https.HttpsError(
      "permission-denied",
      "reCAPTCHA verification failed."
    );
  }

  const { recaptchaToken: _omit, ...clean } = payload || {};
  await admin
    .firestore()
    .collection(collection)
    .add({ ...clean, createdAt: admin.firestore.FieldValue.serverTimestamp() });

  return { ok: true };
});

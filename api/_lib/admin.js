/**
 * Shared server-side helpers for the Vercel serverless functions.
 *
 * These endpoints replace what would otherwise be Firebase Cloud Functions.
 * Cloud Functions require the Blaze plan; Vercel's free tier already hosts
 * this site and runs serverless functions at no cost, so the trust boundary
 * moves here instead of disappearing. The guarantee is unchanged: exam keys,
 * graded attempts and certificates are only ever touched by code the browser
 * cannot run.
 *
 * Files under `_lib/` are not routed by Vercel, so this one is importable
 * without becoming an endpoint of its own.
 *
 * Requires `FIREBASE_SERVICE_ACCOUNT` in the environment: the full service
 * account JSON, from Firebase console -> Project settings -> Service accounts.
 */
import { initializeApp, cert, getApps } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";
import { getAuth } from "firebase-admin/auth";

/** Share of a module's pages that must be complete before a certificate. */
export const REQUIRED_COMPLETION = 0.9;

/** Fallback pass mark, when an exam document does not set its own. */
export const DEFAULT_PASS_SCORE = 70;

/** Minimum gap between attempts at the same exam. */
export const ATTEMPT_COOLDOWN_MS = 10 * 60 * 1000;

export { FieldValue };

/**
 * One Admin app per warm instance.
 *
 * Serverless instances are reused between invocations, so initialising
 * unconditionally would throw "app already exists" on the second request.
 */
function app() {
  if (getApps().length) return getApps()[0];

  const raw = process.env.FIREBASE_SERVICE_ACCOUNT;
  if (!raw) {
    throw new Error(
      "FIREBASE_SERVICE_ACCOUNT is not set. Add the service account JSON to the " +
        "Vercel project's environment variables."
    );
  }

  return initializeApp({ credential: cert(JSON.parse(raw)) });
}

export const db = () => getFirestore(app());

/** An error carrying the HTTP status the client should see. */
export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/**
 * Identify the caller from their Firebase ID token, rejecting guests and
 * unverified addresses.
 *
 * The token is verified against Google's public keys by the Admin SDK, so a
 * forged or expired one fails here rather than deeper in. Verification of the
 * email matters because a certificate names an address, and that address has
 * to be one its holder controls.
 */
export async function requireVerifiedCaller(req) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  if (!token) throw new HttpError(401, "Sign in first.");

  let decoded;
  try {
    decoded = await getAuth(app()).verifyIdToken(token);
  } catch {
    throw new HttpError(401, "Your session has expired. Sign in again.");
  }

  if (decoded.firebase?.sign_in_provider === "anonymous") {
    throw new HttpError(403, "Create an account first.");
  }
  if (!decoded.email_verified) {
    throw new HttpError(412, "Verify your email address first.");
  }
  return decoded;
}

/** Reject anything that is not a plain module slug. */
export function requireModuleSlug(value) {
  if (typeof value !== "string" || !/^[a-z0-9-]{1,64}$/.test(value)) {
    throw new HttpError(400, "Unknown module.");
  }
  return value;
}

/** Certificate ids are read aloud and pasted into URLs, so: no ambiguity. */
export function certificateId() {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no I, O, 0, 1
  let out = "";
  for (let i = 0; i < 12; i += 1) {
    out += alphabet[Math.floor(Math.random() * alphabet.length)];
  }
  return `${out.slice(0, 4)}-${out.slice(4, 8)}-${out.slice(8)}`;
}

/**
 * Wrap a handler so thrown HttpErrors become their status and everything else
 * becomes a 500 without leaking a stack trace to the browser.
 */
export function handler(fn) {
  return async (req, res) => {
    if (req.method !== "POST") {
      res.status(405).json({ error: "Use POST." });
      return;
    }
    try {
      const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
      const data = await fn(req, body);
      res.status(200).json(data);
    } catch (err) {
      if (err instanceof HttpError) {
        res.status(err.status).json({ error: err.message });
        return;
      }
      console.error(err);
      res.status(500).json({ error: "Something went wrong. Please try again." });
    }
  };
}

import { timingSafeEqual } from "node:crypto";
import { countReal } from "./grading";
import { initializeApp, cert, getApps, type App } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";
import { getAuth, type DecodedIdToken } from "firebase-admin/auth";
import { source } from "@/lib/source";

/**
 * Shared server-side helpers for the route handlers under app/api/.
 *
 * These endpoints stand in for Firebase Cloud Functions, which need the Blaze
 * plan. They were plain `api/*.js` files at the repo root, which Vercel only
 * routes for projects that are not built with Next.js; as Next route handlers
 * they deploy with the app itself, and can read the course content directly
 * -- which is what lets them check a learner's claims against real lessons
 * instead of trusting the list the learner's own browser wrote.
 *
 * Requires `FIREBASE_SERVICE_ACCOUNT`: the full service-account JSON, from
 * Firebase console -> Project settings -> Service accounts.
 */

/** Share of a course's lessons that must be complete before a certificate. */
export const REQUIRED_COMPLETION = 0.9;

/** Fallback pass mark, when an exam document does not set its own. */
export const DEFAULT_PASS_SCORE = 70;

/** Minimum gap between attempts at the same exam. */
export const ATTEMPT_COOLDOWN_MS = 10 * 60 * 1000;

/** How recent a sign-in must be to delete the account it belongs to. */
export const RECENT_AUTH_MS = 5 * 60 * 1000;

export { FieldValue };

function app(): App {
  const existing = getApps()[0];
  if (existing) return existing;

  // Against the emulators (tests/e2e) no credential is needed: the Admin
  // SDK reads FIRESTORE_EMULATOR_HOST and FIREBASE_AUTH_EMULATOR_HOST itself.
  if (process.env.FIRESTORE_EMULATOR_HOST && process.env.FIREBASE_AUTH_EMULATOR_HOST) {
    return initializeApp({ projectId: process.env.GCLOUD_PROJECT || "demo-pythoncentralhub" });
  }

  const raw = process.env.FIREBASE_SERVICE_ACCOUNT;
  if (!raw) {
    throw new HttpError(
      503,
      "This feature is not configured yet.",
      "server/not-configured",
    );
  }
  return initializeApp({ credential: cert(JSON.parse(raw)) });
}

export const db = () => getFirestore(app());
export const adminAuth = () => getAuth(app());

/** An error carrying the HTTP status (and optionally a code) the client sees. */
export class HttpError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message);
  }
}

/**
 * Identify the caller from their Firebase ID token.
 *
 * `checkRevoked` is on: a disabled or deleted account's token would otherwise
 * keep working for up to an hour after the fact.
 */
export async function requireCaller(req: Request): Promise<DecodedIdToken> {
  const header = req.headers.get("authorization") ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  if (!token) throw new HttpError(401, "Sign in first.");

  const auth = adminAuth();
  let decoded: DecodedIdToken;
  try {
    decoded = await auth.verifyIdToken(token, true);
  } catch {
    throw new HttpError(401, "Your session has expired. Sign in again.");
  }

  if (decoded.firebase?.sign_in_provider === "anonymous") {
    throw new HttpError(403, "Create an account first.");
  }
  return decoded;
}

/**
 * The caller, with a verified email address. A certificate names an address,
 * and that address has to be one its holder controls.
 */
export async function requireVerifiedCaller(
  req: Request,
): Promise<DecodedIdToken> {
  const decoded = await requireCaller(req);
  if (!decoded.email_verified) {
    throw new HttpError(412, "Verify your email address first.");
  }
  return decoded;
}

/** Reject anything that is not a plain course slug. */
export function requireModuleSlug(value: unknown): string {
  if (typeof value !== "string" || !/^[a-z0-9-]{1,64}$/.test(value)) {
    throw new HttpError(400, "Unknown course.");
  }
  return value;
}

/* -------------------------------------------------------------------------- */
/* The real lessons                                                            */
/* -------------------------------------------------------------------------- */

const LOCALES = new Set(["es", "hi", "ja", "zh-cn"]);

let lessonIds: Map<string, Set<string>> | undefined;

/**
 * Every real lesson id, grouped by course: the same "tutorials/numbers" form
 * the browser's progress store uses (src/lib/progress/ids.ts).
 *
 * This is the check the leaderboard and certificates were missing. Progress
 * documents are written by their owner, so anything counted from them has to
 * be intersected with lessons that exist -- otherwise five thousand invented
 * ids are five thousand pages read.
 */
export function lessonsByCourse(): Map<string, Set<string>> {
  if (lessonIds) return lessonIds;
  lessonIds = new Map();
  for (const page of source.getPages()) {
    const id = page.url.replace(/^\/|\/$/g, "").toLowerCase();
    const parts = id.split("/");
    if (parts.length < 2 || LOCALES.has(parts[0])) continue;
    const course = parts[0];
    if (!lessonIds.has(course)) lessonIds.set(course, new Set());
    lessonIds.get(course)!.add(id);
  }
  return lessonIds;
}

/** How many of `claimed` are real lessons of `course`, each counted once. */
export function countRealLessons(course: string, claimed: unknown): number {
  return countReal(lessonsByCourse().get(course), claimed);
}

/* -------------------------------------------------------------------------- */
/* Misc                                                                        */
/* -------------------------------------------------------------------------- */

/** Certificate ids are read aloud and pasted into URLs, so: no ambiguity. */
export function certificateId(): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no I, O, 0, 1
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  let out = "";
  for (const b of bytes) out += alphabet[b % alphabet.length];
  return `${out.slice(0, 4)}-${out.slice(4, 8)}-${out.slice(8)}`;
}

/** Constant-time string comparison, for shared secrets. */
export function safeEqual(a: string, b: string): boolean {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

/**
 * Wrap a POST handler: parse the body (400 on bad JSON), turn HttpErrors into
 * their status, and everything else into a 500 without a stack trace.
 */
export function post(
  fn: (req: Request, body: Record<string, unknown>) => Promise<unknown>,
) {
  return async (req: Request): Promise<Response> => {
    let body: Record<string, unknown> = {};
    try {
      const text = await req.text();
      body = text ? (JSON.parse(text) as Record<string, unknown>) : {};
      if (typeof body !== "object" || body === null || Array.isArray(body)) {
        throw new Error("not an object");
      }
    } catch {
      return Response.json({ error: "Send a JSON object." }, { status: 400 });
    }

    try {
      return Response.json(await fn(req, body));
    } catch (err) {
      if (err instanceof HttpError) {
        return Response.json(
          { error: err.message, ...(err.code ? { code: err.code } : {}) },
          { status: err.status },
        );
      }
      console.error(err);
      return Response.json(
        { error: "Something went wrong. Please try again." },
        { status: 500 },
      );
    }
  };
}

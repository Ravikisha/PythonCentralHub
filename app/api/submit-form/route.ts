import { db, post, HttpError } from "@/lib/server/admin";
import { allow, clientIp } from "@/lib/server/rate-limit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/submit-form/  { form: "contact" | "feedback", ...fields, recaptchaToken }
 *
 * The contact and feedback forms used to write to Firestore straight from the
 * browser. The reCAPTCHA token rode along but nothing could check it without
 * a server, so a script could fill both collections without limit. Here the
 * token is verified with Google before anything is stored, fields are
 * validated and capped, and each address is rate limited.
 *
 * Needs RECAPTCHA_SECRET (the secret half of NEXT_PUBLIC_RECAPTCHA_SITE_KEY)
 * and FIREBASE_SERVICE_ACCOUNT. Until both are set it answers 503 with
 * code "server/not-configured" and the forms fall back to the old direct
 * write -- see components/docs/Feedback.tsx.
 */

/** reCAPTCHA v3 score below which a submission is treated as a bot. */
const MIN_SCORE = 0.5;

function str(value: unknown, max: number, required = false): string {
  if (value === undefined || value === null || value === "") {
    if (required) throw new HttpError(400, "Fill in the required fields.");
    return "";
  }
  if (typeof value !== "string") throw new HttpError(400, "Invalid form data.");
  const trimmed = value.trim();
  if (trimmed.length > max) throw new HttpError(400, "That message is too long.");
  if (required && !trimmed) throw new HttpError(400, "Fill in the required fields.");
  return trimmed;
}

async function verifyCaptcha(token: string, action: string, ip: string) {
  const secret = process.env.RECAPTCHA_SECRET;
  if (!secret) {
    throw new HttpError(503, "Forms are not configured yet.", "server/not-configured");
  }
  if (!token) throw new HttpError(400, "The spam check did not load. Reload and try again.");

  const res = await fetch("https://www.google.com/recaptcha/api/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ secret, response: token, remoteip: ip }),
  });
  const result = (await res.json()) as {
    success?: boolean;
    score?: number;
    action?: string;
  };
  if (!result.success || (result.score ?? 0) < MIN_SCORE || result.action !== action) {
    throw new HttpError(403, "That looked automated. Try again in a moment.");
  }
}

export const POST = post(async (req, body) => {
  // Global with Upstash configured, per instance otherwise; the captcha is
  // the real gate either way.
  const ip = clientIp(req);
  if (!(await allow(`form:${ip}`, 5, 60_000))) {
    throw new HttpError(429, "Too many messages. Try again in a minute.");
  }

  const form = body.form;
  if (form !== "contact" && form !== "feedback") {
    throw new HttpError(400, "Unknown form.");
  }

  await verifyCaptcha(str(body.recaptchaToken, 4000), form, ip);

  const email = str(body.email, 254);
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new HttpError(400, "Check the email address.");
  }

  const createdAt = new Date().toISOString();
  const store = db();

  if (form === "contact") {
    await store.collection("contact").add({
      name: str(body.name, 120, true),
      email,
      message: str(body.message, 5000, true),
      createdAt,
    });
  } else {
    await store.collection("feedback").add({
      feedback: str(body.feedback, 40, true),
      email,
      comment: str(body.comment, 5000),
      // Which page it is about. Ratings used to arrive with no page at all.
      page: str(body.page, 512),
      createdAt,
    });
  }

  return { ok: true };
});

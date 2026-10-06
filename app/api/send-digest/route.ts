import {
  db,
  adminAuth,
  safeEqual,
  countRealLessons,
  lessonsByCourse,
  FieldValue,
  REQUIRED_COMPLETION,
} from "@/lib/server/admin";
import { SITE_NAME, SITE_URL } from "@/lib/site";
import { courseInfo } from "@/lib/courses.data.mjs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

/**
 * GET /api/send-digest/ -- weekly nudge, run by Vercel Cron (vercel.json).
 *
 * Mails only people who opted in AND are within five lessons of the
 * certificate threshold. With RESEND_API_KEY and EMAIL_FROM set, mail goes out
 * through Resend's HTTP API directly. Without them it is queued as a `mail/`
 * document for the Firebase "Trigger Email from Firestore" extension; with
 * neither, those documents sit unsent.
 *
 * The address comes from Firebase Auth, and only when it is verified. It used
 * to come from the profile document, which its owner can edit -- so anyone
 * could point the weekly mail at someone else's inbox.
 *
 * Protected by CRON_SECRET, which Vercel sends as a bearer token.
 */
const CHUNK = 20;

type Mail = { to: string; subject: string; text: string };

/** Send through Resend if configured. Returns false when it is not. */
async function sendDirect(mail: Mail): Promise<boolean> {
  const key = process.env.RESEND_API_KEY;
  const from = process.env.EMAIL_FROM;
  if (!key || !from) return false;
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: [mail.to], subject: mail.subject, text: mail.text }),
  });
  if (!res.ok) throw new Error(`Resend answered ${res.status}: ${await res.text()}`);
  return true;
}

export async function GET(req: Request): Promise<Response> {
  const secret = process.env.CRON_SECRET;
  if (!secret) {
    return Response.json({ error: "CRON_SECRET is not configured." }, { status: 500 });
  }
  const given = req.headers.get("authorization") ?? "";
  if (!safeEqual(given, `Bearer ${secret}`)) {
    return Response.json({ error: "Not authorised." }, { status: 401 });
  }

  try {
    const store = db();
    const auth = adminAuth();
    const optedIn = await store
      .collection("users")
      .where("settings.digest", "==", true)
      .get();

    let queued = 0;
    const direct = Boolean(process.env.RESEND_API_KEY && process.env.EMAIL_FROM);

    // In chunks rather than one user at a time, so the run finishes inside the
    // function's time limit as the list grows.
    for (let i = 0; i < optedIn.docs.length; i += CHUNK) {
      const chunk = optedIn.docs.slice(i, i + CHUNK);
      const results = await Promise.all(
        chunk.map(async (userDoc) => {
          const account = await auth.getUser(userDoc.id).catch(() => null);
          if (!account?.email || !account.emailVerified || account.disabled) return 0;

          const progress = await store.collection(`users/${userDoc.id}/progress`).get();
          const nearly: { title: string; remaining: number }[] = [];
          progress.forEach((d) => {
            const total = lessonsByCourse().get(d.id)?.size ?? 0;
            if (!total) return;
            const done = countRealLessons(d.id, d.data().completed);
            const remaining = Math.ceil(total * REQUIRED_COMPLETION) - done;
            if (remaining > 0 && remaining <= 5) {
              nearly.push({ title: courseInfo(d.id)?.title ?? d.id, remaining });
            }
          });
          if (!nearly.length) return 0;

          const lines = nearly
            .map((n) => `- ${n.title}: ${n.remaining} lesson(s) to go`)
            .join("\n");

          const mail: Mail = {
            to: account.email,
            subject: `You're close to a ${SITE_NAME} certificate`,
            text:
              `You're nearly there:\n\n${lines}\n\n` +
              `Pick up where you left off: ${SITE_URL}/dashboard/\n\n` +
              `Stop these emails: ${SITE_URL}/profile/`,
          };
          if (await sendDirect(mail)) return 1;
          await store.collection("mail").add({
            to: [mail.to],
            message: { subject: mail.subject, text: mail.text },
            createdAt: FieldValue.serverTimestamp(),
          });
          return 1;
        }),
      );
      queued += results.reduce<number>((n, r) => n + r, 0);
    }

    return Response.json({ [direct ? "sent" : "queued"]: queued });
  } catch (err) {
    console.error(err);
    return Response.json({ error: "Digest run failed." }, { status: 500 });
  }
}

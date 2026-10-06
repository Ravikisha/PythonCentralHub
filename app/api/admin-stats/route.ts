import type { Query, Timestamp } from "firebase-admin/firestore";
import { db, post, HttpError, requireVerifiedCaller } from "@/lib/server/admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/admin-stats/  {}
 *
 * Totals and the latest messages for the /admin page. Only for verified
 * accounts whose address is listed in ADMIN_EMAILS (comma-separated); everyone
 * else gets a 403 that says nothing about what is behind it.
 *
 * Counts use Firestore's count() aggregation, which bills one read per
 * thousand documents rather than one per document.
 */
const RECENT = 25;

function admins(): Set<string> {
  return new Set(
    (process.env.ADMIN_EMAILS ?? "")
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean),
  );
}

/** Forms store an ISO string; older client-written rows a Timestamp. */
function when(value: unknown): number | null {
  if (typeof value === "string") {
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? null : ms;
  }
  return value && typeof (value as Timestamp).toMillis === "function"
    ? (value as Timestamp).toMillis()
    : null;
}

export const POST = post(async (req) => {
  const caller = await requireVerifiedCaller(req);
  if (!caller.email || !admins().has(caller.email.toLowerCase())) {
    throw new HttpError(403, "Not authorised.");
  }

  const store = db();
  const count = async (query: Query) =>
    (await query.count().get()).data().count;

  const [users, attempts, passed, certificates, completion, leaderboard, feedbackN, contactN] =
    await Promise.all([
      count(store.collection("users")),
      count(store.collection("attempts")),
      count(store.collection("attempts").where("passed", "==", true)),
      count(store.collection("certificates")),
      count(store.collection("certificates").where("kind", "==", "completion")),
      count(store.collection("leaderboard")),
      count(store.collection("feedback")),
      count(store.collection("contact")),
    ]);

  const [feedback, contact, recentCerts] = await Promise.all([
    store.collection("feedback").orderBy("createdAt", "desc").limit(RECENT).get(),
    store.collection("contact").orderBy("createdAt", "desc").limit(RECENT).get(),
    store.collection("certificates").orderBy("issuedAt", "desc").limit(RECENT).get(),
  ]);

  return {
    totals: {
      users,
      attempts,
      passed,
      certificates,
      completionCertificates: completion,
      leaderboard,
      feedback: feedbackN,
      contact: contactN,
    },
    feedback: feedback.docs.map((d) => {
      const f = d.data();
      return {
        id: d.id,
        rating: f.feedback ?? null,
        comment: f.comment ?? "",
        page: f.page ?? "",
        email: f.email ?? "",
        at: when(f.createdAt),
      };
    }),
    contact: contact.docs.map((d) => {
      const c = d.data();
      return {
        id: d.id,
        name: c.name ?? "",
        email: c.email ?? "",
        message: c.message ?? "",
        at: when(c.createdAt),
      };
    }),
    certificates: recentCerts.docs.map((d) => {
      const c = d.data();
      return {
        id: d.id,
        holder: c.holder ?? "",
        module: c.module ?? "",
        kind: c.kind ?? "assessment",
        score: c.score ?? null,
        at: when(c.issuedAt),
      };
    }),
  };
});

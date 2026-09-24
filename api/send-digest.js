/**
 * GET/POST /api/send-digest — weekly nudge, run by Vercel Cron.
 *
 * Only writes for people who opted in AND are within five pages of a
 * certificate, so the mail is a reminder rather than a newsletter.
 *
 * Delivery goes through the Firebase "Trigger Email from Firestore"
 * extension: this writes a document to `mail/`, the extension sends it. That
 * keeps SMTP credentials out of this codebase entirely, and without the
 * extension installed the documents simply accumulate unsent -- a visible,
 * harmless failure rather than a silent one.
 *
 * Protected by CRON_SECRET. Vercel sends it as a bearer token on scheduled
 * invocations; without the check this endpoint would be an open trigger for
 * anyone who found the URL.
 */
import { db, FieldValue, REQUIRED_COMPLETION } from "./_lib/admin.js";

export default async function send(req, res) {
  const secret = process.env.CRON_SECRET;
  if (!secret) {
    res.status(500).json({ error: "CRON_SECRET is not configured." });
    return;
  }
  if (req.headers.authorization !== `Bearer ${secret}`) {
    res.status(401).json({ error: "Not authorised." });
    return;
  }

  try {
    const store = db();
    const configSnap = await store.doc("config/modules").get();
    const counts = configSnap.data()?.counts || {};

    const optedIn = await store.collection("users").where("settings.digest", "==", true).get();

    let queued = 0;

    for (const userDoc of optedIn.docs) {
      const user = userDoc.data();
      if (!user.email) continue;

      const progress = await store.collection(`users/${userDoc.id}/progress`).get();

      const nearly = [];
      progress.forEach((d) => {
        const total = counts[d.id];
        if (!total) return;
        const done = (d.data().completed || []).length;
        const remaining = Math.ceil(total * REQUIRED_COMPLETION) - done;
        if (remaining > 0 && remaining <= 5) nearly.push({ module: d.id, remaining });
      });

      if (!nearly.length) continue;

      const lines = nearly.map((n) => `• ${n.module}: ${n.remaining} page(s) to go`).join("\n");

      await store.collection("mail").add({
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

    res.status(200).json({ queued });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Digest run failed." });
  }
}

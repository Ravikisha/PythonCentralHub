/**
 * Send the contact or feedback form.
 *
 * Goes through /api/submit-form/, which checks the reCAPTCHA token on the
 * server before storing anything. While that endpoint is not configured yet
 * (no RECAPTCHA_SECRET or service account on the deployment) it answers 503
 * with "server/not-configured", and the submission falls back to the old
 * direct Firestore write so the forms keep working in the meantime. Once the
 * endpoint is live, set `allow create: if false` on both collections in
 * firebase/firestore.rules and the fallback stops being possible.
 */
export type FormPayload =
  | {
      form: "contact";
      name: string;
      email: string;
      message: string;
      recaptchaToken: string;
    }
  | {
      form: "feedback";
      feedback: string;
      email: string;
      comment: string;
      page: string;
      recaptchaToken: string;
    };

export class FormError extends Error {}

export async function submitForm(payload: FormPayload): Promise<void> {
  let res: Response | null = null;
  try {
    res = await fetch("/api/submit-form/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    res = null; // offline or blocked: fall through to the direct write
  }

  if (res?.ok) return;

  const data = res
    ? ((await res.json().catch(() => ({}))) as { error?: string; code?: string })
    : {};

  // Anything but "not configured" is a real answer from the server -- a
  // failed captcha, a rate limit, a bad field -- and the learner should see it.
  if (res && data.code !== "server/not-configured") {
    throw new FormError(data.error || "We could not send that. Try again in a moment.");
  }

  const { doc, setDoc } = await import("firebase/firestore");
  const { getDb } = await import("@/src/lib/firebase/client");
  const db = await getDb();
  // `page` is left out here: the rules deployed before this change do not
  // list it, and a field they don't know fails the whole write. The endpoint
  // records it; the fallback only has to keep the form working.
  const { form, ...fields } = payload;
  if ("page" in fields) delete (fields as { page?: string }).page;
  await setDoc(doc(db, form, crypto.randomUUID()), {
    ...fields,
    createdAt: new Date().toISOString(),
  });
}

"use client";

import { useState } from "react";
import { t } from "@/lib/strings";

/**
 * "Was this page helpful?" -- the per-page feedback form.
 *
 * Writes straight to the `feedback` collection, which is append-only for
 * everyone: anyone may file one, nobody may read, change or delete one (see
 * firebase/firestore.rules). That is why a sender's address is never exposed
 * to the next visitor.
 *
 * The field names below are an allowlist in those rules. Adding one here
 * without adding it there makes every submission fail.
 *
 * reCAPTCHA v3 is optional. When `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` is unset the
 * form still works and sends an empty token; the rules cap the fields either
 * way.
 */
const RECAPTCHA_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ?? "";

/** The five faces, worst to best. One path each, drawn on a shared circle. */
const FACES: { value: number; label: string; mouth: string; extra?: string }[] =
  [
    {
      value: 1,
      label: t("pch.ratingVeryDissatisfied"),
      mouth: "M8.5 16 Q12 13.8 15.5 16",
      extra: "M8 8.6 L10.2 9.8 M16 8.6 L13.8 9.8",
    },
    {
      value: 2,
      label: t("pch.ratingDissatisfied"),
      mouth: "M8.5 16 Q12 14.4 15.5 16",
    },
    { value: 3, label: t("pch.ratingNeutral"), mouth: "M8.5 15 L15.5 15" },
    {
      value: 4,
      label: t("pch.ratingSatisfied"),
      mouth: "M8.5 14 Q12 16.6 15.5 14",
    },
    {
      value: 5,
      label: t("pch.ratingVerySatisfied"),
      mouth: "M8 13.6 Q12 17.6 16 13.6",
    },
  ];

function notify(
  title: string,
  description: string,
  variant: "success" | "error",
) {
  window.toast?.show({ title, description, variant });
}

async function recaptchaToken(): Promise<string> {
  if (!RECAPTCHA_KEY || !window.grecaptcha) return "";
  try {
    await new Promise<void>((resolve) => window.grecaptcha!.ready(resolve));
    return await window.grecaptcha.execute(RECAPTCHA_KEY, {
      action: "feedback",
    });
  } catch {
    return "";
  }
}

export function Feedback() {
  const [rating, setRating] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    if (rating === null) {
      setError("Select a face before submitting.");
      notify("Pick a rating", "Select a face before submitting.", "error");
      return;
    }

    setBusy(true);
    try {
      const { submitForm } = await import("@/src/lib/forms");
      await submitForm({
        form: "feedback",
        feedback: String(rating),
        email,
        comment,
        page: window.location.pathname,
        recaptchaToken: await recaptchaToken(),
      });

      notify(
        "Feedback received",
        "Thank you — it goes straight to whoever maintains this page.",
        "success",
      );
      setRating(null);
      setEmail("");
      setComment("");
    } catch (err) {
      console.error("[feedback] submit failed:", err);
      const { FormError } = await import("@/src/lib/forms");
      const message =
        err instanceof FormError
          ? err.message
          : "We could not send that. Try again in a moment.";
      setError(message);
      notify("Something went wrong", message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="fb">
      <h2 className="fb__title">{t("pch.feedbackHeading")}</h2>
      <p className="fb__sub">{t("pch.feedbackSubheading")}</p>

      <form onSubmit={submit}>
        <div
          className="fb__faces"
          role="radiogroup"
          aria-label={t("pch.feedbackHeading")}
        >
          {FACES.map((face) => (
            <label
              className="fb__face"
              key={face.value}
              aria-label={face.label}
            >
              {/* The radio stays in the DOM and focusable -- hidden visually,
                  not with display:none -- so the row is keyboard-operable. */}
              <input
                className="fb__radio"
                type="radio"
                name="feedback"
                value={face.value}
                checked={rating === face.value}
                onChange={() => setRating(face.value)}
              />
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="9" />
                <circle
                  cx="9"
                  cy="10.5"
                  r="0.7"
                  fill="currentColor"
                  stroke="none"
                />
                <circle
                  cx="15"
                  cy="10.5"
                  r="0.7"
                  fill="currentColor"
                  stroke="none"
                />
                <path d={face.mouth} />
                {face.extra ? <path d={face.extra} /> : null}
              </svg>
            </label>
          ))}
        </div>

        {/* Both fields open only once a face is picked: asking for an email
            address before the reader has said anything is the wrong order. */}
        {rating !== null ? (
          <>
            <div className="fb__field">
              <label htmlFor="fb-email">{t("pch.feedbackEmail")}</label>
              <input
                id="fb-email"
                type="email"
                name="email"
                placeholder={t("pch.feedbackEmailPlaceholder")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="fb__field">
              <label htmlFor="fb-comment">{t("pch.feedbackComment")}</label>
              <textarea
                id="fb-comment"
                name="comment"
                rows={3}
                maxLength={5000}
                placeholder={t("pch.feedbackCommentPlaceholder")}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
            </div>

            <p className="fb__error" role="alert" aria-live="polite">
              {error}
            </p>

            <button type="submit" className="fb__submit" disabled={busy}>
              {busy ? "Sending…" : t("pch.feedbackSubmit")}
            </button>
          </>
        ) : null}
      </form>
    </section>
  );
}

export default Feedback;

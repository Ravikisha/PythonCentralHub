"use client";

import { useState } from "react";

/**
 * Contact — the site's contact form.
 *
 * Writes straight to Firestore, as the Astro version did. The reCAPTCHA token
 * is collected and stored but **not verified**: verifying it needs a server,
 * and the `submitForm` function that was meant to do it has never been
 * deployed. The length caps in firebase/firestore.rules are the real spam
 * control today.
 *
 * Client component: it owns form state and talks to Firestore on submit.
 */
const FIELD =
  "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg " +
  "focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 " +
  "dark:border-gray-600 dark:placeholder-gray-400 dark:text-white " +
  "dark:focus:ring-primary-500 dark:focus:border-primary-500 dark:shadow-sm-light";

const LABEL =
  "block mb-2 text-lg font-bold font-poppins text-gray-900 dark:text-gray-300";

export function Contact() {
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ?? "";
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function notify(title: string, description: string, variant: string) {
    if (typeof window !== "undefined" && window.toast?.show) {
      window.toast.show({ title, description, variant });
    }
  }

  async function recaptchaToken(): Promise<string> {
    if (!siteKey || !window.grecaptcha) return "";
    try {
      await new Promise<void>((resolve) => window.grecaptcha!.ready(resolve));
      return await window.grecaptcha!.execute(siteKey, { action: "contact" });
    } catch {
      return "";
    }
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);

    const form = event.currentTarget;
    const data = new FormData(form);

    try {
      const { submitForm } = await import("@/src/lib/forms");
      await submitForm({
        form: "contact",
        name: String(data.get("name") ?? ""),
        email: String(data.get("email") ?? ""),
        message: String(data.get("message") ?? ""),
        recaptchaToken: await recaptchaToken(),
      });

      notify(
        "Message sent",
        "Thank you for your message! We will get back to you as soon as possible.",
        "success",
      );
      form.reset();
    } catch (err) {
      console.error("[contact] submit failed:", err);
      const { FormError } = await import("@/src/lib/forms");
      const message =
        err instanceof FormError
          ? err.message
          : "We couldn't send your message. Please try again later.";
      setError(message);
      notify("Something went wrong", message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="px-4 mx-auto max-w-screen-md">
        <p className="mb-8 lg:mb-16 font-light text-center text-gray-500 dark:text-gray-400 sm:text-xl">
          Got a question, a correction, or a tutorial you would like to see?
          Send it over.
        </p>

        <noscript>
          <p className="mb-6 p-3 rounded-lg text-center text-sm bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200">
            This form needs JavaScript. You can email{" "}
            <a className="underline" href="mailto:ravikishan63392@gmail.com">
              ravikishan63392@gmail.com
            </a>{" "}
            instead.
          </p>
        </noscript>

        <form className="space-y-8" onSubmit={onSubmit}>
          <div>
            <label htmlFor="email" className={LABEL}>
              Your email{" "}
              <span className="text-red-500" aria-hidden="true">
                *
              </span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              aria-required="true"
              className={FIELD}
              placeholder="you@example.com"
              required
              disabled={busy}
            />
          </div>

          <div>
            <label htmlFor="name" className={LABEL}>
              Your name{" "}
              <span className="text-red-500" aria-hidden="true">
                *
              </span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              aria-required="true"
              className={FIELD}
              placeholder="Ada Lovelace"
              required
              disabled={busy}
            />
          </div>

          <div>
            <label htmlFor="message" className={LABEL}>
              Your message{" "}
              <span className="text-red-500" aria-hidden="true">
                *
              </span>
            </label>
            <textarea
              id="message"
              rows={6}
              name="message"
              aria-required="true"
              className="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg shadow-sm border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
              placeholder="Describe your issue, question, or feedback..."
              required
              disabled={busy}
            />
          </div>

          <div
            role="alert"
            aria-live="polite"
            className={error ? "text-sm text-red-600" : "sr-only"}
          >
            {error}
          </div>

          <button
            type="submit"
            disabled={busy}
            className="inline-flex items-center justify-center gap-2 py-3 px-5 text-sm font-medium text-center text-gray-900 dark:text-white rounded-lg bg-primary-700 sm:w-fit hover:bg-primary-800 focus:ring-4 focus:outline-none focus:ring-primary-300 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {busy ? (
              <span
                className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
                aria-hidden="true"
              />
            ) : null}
            <span>{busy ? "Sending…" : "Send message"}</span>
          </button>
        </form>
      </div>
    </section>
  );
}

export default Contact;

/**
 * The one-line result under an auth form.
 *
 * The live region is always mounted and only its contents change: a region
 * that appears together with its text is often not announced by screen
 * readers, which is how "Wrong password" went unheard. Errors are also
 * `role="alert"`, so they interrupt; successes and progress wait politely.
 * An empty region takes no space, so it never holds open a row.
 */
export type Tone = "error" | "success" | "info";

export interface Status {
  text: string;
  tone: Tone;
}

export function StatusLine({ status }: { status: Status | null }) {
  return (
    <div aria-live="polite" aria-atomic="true">
      {status ? (
        <p
          className="pch-auth__status"
          data-tone={status.tone}
          role={status.tone === "error" ? "alert" : undefined}
        >
          {status.text}
        </p>
      ) : null}
    </div>
  );
}

export default StatusLine;

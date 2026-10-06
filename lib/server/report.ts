/**
 * Error reporting, without a third-party account.
 *
 * Every report is one JSON log line tagged `pythoncentralhub:error`, which Vercel
 * keeps with the deployment's logs (Project -> Logs, filter on the tag). Set
 * ERROR_WEBHOOK_URL to also post each report to a chat or incident webhook
 * (Slack, Discord, or anything that accepts a JSON POST).
 *
 * Used by instrumentation.ts (server errors) and app/api/client-error (errors
 * from readers' browsers, including the exercise runner).
 */
export interface ErrorReport {
  source: "server" | "client";
  message: string;
  stack?: string;
  url?: string;
  digest?: string;
  kind?: string;
  userAgent?: string;
}

const MAX = 4000;

export async function report(entry: ErrorReport): Promise<void> {
  const clean: ErrorReport = {
    ...entry,
    message: entry.message.slice(0, 1000),
    stack: entry.stack?.slice(0, MAX),
  };
  console.error("pythoncentralhub:error " + JSON.stringify({ at: new Date().toISOString(), ...clean }));

  const hook = process.env.ERROR_WEBHOOK_URL;
  if (!hook) return;
  try {
    await fetch(hook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // `text` is what Slack and Discord-compatible hooks display.
      body: JSON.stringify({
        text: `Python Central Hub ${clean.source} error: ${clean.message}${clean.url ? `\n${clean.url}` : ""}`,
        content: `Python Central Hub ${clean.source} error: ${clean.message}${clean.url ? `\n${clean.url}` : ""}`,
        report: clean,
      }),
      signal: AbortSignal.timeout(3000),
    });
  } catch {
    /* the log line above is the record; a failed webhook is not an error */
  }
}

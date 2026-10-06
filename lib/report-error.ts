/**
 * Send a browser-side error to /api/client-error/ (see lib/server/report.ts).
 *
 * At most a few per page and never the same one twice, so a tight error loop
 * cannot flood the endpoint. Uses sendBeacon where possible so a report
 * survives the page closing.
 */
const sent = new Set<string>();
let count = 0;
const MAX_PER_PAGE = 5;

export function reportError(
  error: unknown,
  kind = "error",
): void {
  if (typeof window === "undefined") return;
  const err = error instanceof Error ? error : new Error(String(error));
  const key = `${kind}:${err.message}`;
  if (sent.has(key) || count >= MAX_PER_PAGE) return;
  sent.add(key);
  count += 1;

  const body = JSON.stringify({
    message: err.message.slice(0, 1000),
    stack: err.stack?.slice(0, 4000),
    url: window.location.pathname,
    kind,
  });
  try {
    const blob = new Blob([body], { type: "application/json" });
    if (navigator.sendBeacon?.("/api/client-error/", blob)) return;
  } catch {
    /* fall through to fetch */
  }
  void fetch("/api/client-error/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    keepalive: true,
  }).catch(() => {});
}

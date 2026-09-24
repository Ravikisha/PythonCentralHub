/**
 * Client-side lookup for the translated auth strings emitted by
 * src/components/auth/AuthMessages.astro.
 */
let cache: Record<string, string> | null = null;

function table(): Record<string, string> {
  if (cache) return cache;
  const el = document.querySelector("[data-pch-auth-messages]");
  try {
    cache = el ? (JSON.parse(el.textContent || "{}") as Record<string, string>) : {};
  } catch {
    cache = {};
  }
  return cache;
}

/** Translated text for a `pch.authErr*` key, falling back to the key itself. */
export function messageFor(key: string): string {
  return table()[key] ?? key;
}

/**
 * Paint the shared status line under an auth form.
 *
 * `tone` drives the colour of the left rule; passing `null` as the text hides
 * the element again so it never occupies empty space.
 */
export function setStatus(
  el: HTMLElement | null,
  text: string | null,
  tone: "error" | "success" | "info" = "info"
): void {
  if (!el) return;
  if (!text) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.dataset.tone = tone;
  el.textContent = text;
}

/**
 * Where to send the learner after a successful sign-in.
 *
 * The site is statically generated, so there is no server to hold a "return
 * to" value -- it rides in the `?next=` query string instead. Only same-origin
 * relative paths are honoured: accepting an absolute URL here would turn the
 * login page into an open redirect that phishing links could point at.
 */
export function nextUrl(fallback = "/profile"): string {
  const raw = new URLSearchParams(window.location.search).get("next");
  if (!raw) return fallback;
  if (!raw.startsWith("/") || raw.startsWith("//")) return fallback;
  return raw;
}

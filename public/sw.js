// Python Central Hub offline worker.
//
// Registered by components/ServiceWorker.tsx in production builds only.
//
// What it does:
//   - Lessons you have opened stay readable offline. Pages and Next's
//     client-navigation payloads are fetched from the network first and kept
//     as a fallback, so a deploy is never hidden behind a stale copy.
//   - Hashed build assets (/_next/static/) never change, so they are served
//     from the cache once fetched. Fonts and images likewise.
//   - The Python runtime (Pyodide, from jsDelivr) and wheels from PyPI are
//     versioned URLs: cached on first use, so exercises you have run once
//     work offline and start faster afterwards.
//   - Nothing under /api/ and no other origin is touched.
//
// This file replaced a retired worker that once loaded an ad script; browsers
// that still hold that one pick this up on their next visit and it is gone.
const VERSION = "v1";
const STATIC = `pch-static-${VERSION}`;
const PAGES = `pch-pages-${VERSION}`;
const PYODIDE = "pch-pyodide-0.29.5";
const KEEP = new Set([STATIC, PAGES, PYODIDE]);
const MAX_PAGES = 250;

const PYODIDE_PREFIX = "https://cdn.jsdelivr.net/pyodide/v0.29.5/";
const PYPI_HOST = "files.pythonhosted.org";

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => !KEEP.has(k)).map((k) => caches.delete(k)));
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  if (url.href.startsWith(PYODIDE_PREFIX) || url.host === PYPI_HOST) {
    event.respondWith(cacheFirst(req, PYODIDE));
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname === "/sw.js") return;

  if (
    url.pathname.startsWith("/_next/static/") ||
    url.pathname.startsWith("/fonts/") ||
    url.pathname.startsWith("/images/") ||
    url.pathname.startsWith("/assets/")
  ) {
    event.respondWith(cacheFirst(req, STATIC));
    return;
  }

  const isPage = req.mode === "navigate" || req.headers.get("RSC") === "1";
  if (isPage) {
    event.respondWith(networkFirst(req, req.mode === "navigate"));
    return;
  }

  // Everything else from this origin (unhashed scripts, the search index,
  // the progress manifest): fresh when online, the last copy when not.
  event.respondWith(networkFirst(req, false, STATIC));
});

async function cacheFirst(req, name) {
  const cache = await caches.open(name);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok) cache.put(req, res.clone()).catch(() => {});
  return res;
}

async function networkFirst(req, navigation, name = PAGES) {
  const cache = await caches.open(name);
  try {
    const res = await fetch(req);
    if (res.ok && res.type === "basic") {
      cache.put(req, res.clone()).then(() => name === PAGES && trim(cache)).catch(() => {});
    }
    return res;
  } catch (err) {
    const hit = await cache.match(req);
    if (hit) return hit;
    if (navigation) return offlinePage();
    throw err;
  }
}

/** Oldest first out, so the cache does not grow without bound. */
async function trim(cache) {
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - MAX_PAGES; i++) await cache.delete(keys[i]);
}

function offlinePage() {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline | Python Central Hub</title>
<style>body{font-family:system-ui,sans-serif;max-width:34rem;margin:5rem auto;padding:0 1rem;line-height:1.55;color:#1f2330;background:#fafafc}
@media (prefers-color-scheme:dark){body{color:#e6e8ef;background:#0d1117}}a{color:#7c4dff}</style></head>
<body><h1>You are offline</h1>
<p>This page has not been opened on this device before, so there is no saved copy of it.</p>
<p>Lessons you have already opened still work offline, and your progress is saved in this browser and will sync when you are back online.</p>
<p><a href="/">Try the home page</a> · <a href="javascript:location.reload()">Retry</a></p></body></html>`;
  return new Response(html, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

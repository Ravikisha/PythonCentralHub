"use client";

import { useEffect } from "react";

/**
 * Register the offline worker (public/sw.js) once the page is idle.
 *
 * Production only: in development it would cache hot-reloaded chunks and
 * serve yesterday's code. Set NEXT_PUBLIC_DISABLE_SW=1 to ship without it;
 * the worker then stays registered in browsers that already have it, so to
 * retire it, replace sw.js with one that unregisters itself.
 */
export function ServiceWorker() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") return;
    if (process.env.NEXT_PUBLIC_DISABLE_SW === "1") return;
    if (!("serviceWorker" in navigator)) return;

    const register = () => {
      navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {
        /* offline support is a bonus; the site works without it */
      });
    };
    if (document.readyState === "complete") register();
    else window.addEventListener("load", register, { once: true });
  }, []);
  return null;
}

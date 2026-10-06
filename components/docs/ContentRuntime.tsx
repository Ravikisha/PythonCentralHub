"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

/**
 * The behaviour a content page needs, loaded only if that page needs it.
 *
 * Four scripts carried over from the Astro build upgrade markup the MDX
 * pipeline emits as plain HTML: mermaid draws the diagrams, p5-viz runs the
 * sketches, viz-fullscreen adds the expand control, and python-playground turns
 * ```python blocks into a runnable editor. The Astro layout loaded all four on
 * every page. Here they are fetched per page and only when the markup they
 * upgrade is actually present -- 28 KB of playground is not worth sending to a
 * page with no Python in it, and the browser was warning about two preloads it
 * never used.
 *
 * Re-running matters as much as loading. Links inside the shell are client-side
 * navigations, so the document is never reloaded: a script that did its work on
 * DOMContentLoaded would run once for the whole session and every diagram
 * reached by clicking through the contents would show its own source instead.
 * Each script therefore exposes an idempotent entry point, and this effect
 * calls it again on every path change.
 */

/** Scripts already requested this session, so a second page does not refetch. */
const loaded = new Map<string, Promise<void>>();

function ensure(src: string, isModule = false) {
  const cached = loaded.get(src);
  if (cached) return cached;

  const promise = new Promise<void>((resolve, reject) => {
    const el = document.createElement("script");
    el.src = src;
    if (isModule) el.type = "module";
    el.onload = () => resolve();
    el.onerror = () => reject(new Error(`failed to load ${src}`));
    document.head.appendChild(el);
  });

  loaded.set(src, promise);
  return promise;
}

interface Runtime {
  /** What on the page needs this script. */
  selector: string;
  src: string;
  module?: boolean;
  /** Global the script publishes, called again on every navigation. */
  rerun: () => void;
}

const RUNTIMES: Runtime[] = [
  {
    selector: "pre.mermaid",
    src: "/scripts/mermaid.js",
    module: true,
    rerun: () => window.__pchMermaid?.run(),
  },
  {
    selector: ".pch-p5[data-p5]",
    src: "/scripts/p5-viz.js",
    rerun: () => window.__pchP5?.init(),
  },
  {
    selector:
      ".pch-viz, [data-rehype-pretty-code-figure], [data-rehype-pretty-code-fragment]",
    src: "/scripts/viz-fullscreen.js",
    module: true,
    rerun: () => window.__pchVizFullscreen?.init(),
  },
  {
    selector: 'pre[data-language="python"]',
    src: "/scripts/python-playground.js",
    rerun: () => window.__pchPlayground?.init(),
  },
];

export function ContentRuntime() {
  const pathname = usePathname();

  /**
   * Copy, for every code block on the page, from one listener.
   *
   * The button is plain markup added by lib/rehype/code-chrome.ts; there are
   * 7,131 code blocks in the corpus and up to a few dozen on a page, so they
   * do not each get a React component.
   */
  useEffect(() => {
    async function onClick(event: MouseEvent) {
      const button = (
        event.target as HTMLElement | null
      )?.closest<HTMLButtonElement>("[data-copy]");
      if (!button) return;

      // The figure, not the nearest div: on untitled blocks the button sits in
      // div.code__bar, which holds no code, so copying silently did nothing.
      const code = button.closest("figure")?.querySelector("pre code");
      if (!code) return;

      try {
        await navigator.clipboard.writeText(code.textContent ?? "");
        button.dataset.copied = "true";
        const label = button.querySelector(".code__copy-label");
        if (label) label.textContent = "Copied";

        window.setTimeout(() => {
          delete button.dataset.copied;
          if (label) label.textContent = "Copy";
        }, 1600);
      } catch {
        // Clipboard access can be refused (insecure origin, permissions).
        // Selecting the text still works, so this stays quiet.
      }
    }

    /** Unfold a long code block, once, in place. */
    function onUnfold(event: MouseEvent) {
      const button = (
        event.target as HTMLElement | null
      )?.closest<HTMLButtonElement>("[data-unfold]");
      if (!button) return;

      const figure = button.closest<HTMLElement>("figure");
      if (!figure) return;

      figure.dataset.long = "false";
      button.remove();
    }

    document.addEventListener("click", onClick);
    document.addEventListener("click", onUnfold);
    return () => {
      document.removeEventListener("click", onClick);
      document.removeEventListener("click", onUnfold);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    for (const runtime of RUNTIMES) {
      if (!document.querySelector(runtime.selector)) continue;

      void ensure(runtime.src, runtime.module).then(() => {
        // The script runs itself on first load; this catches the second and
        // later visits, when it is already in memory.
        if (!cancelled) runtime.rerun();
      });
    }

    return () => {
      cancelled = true;
      // Leaving the page: stop its sketches, which otherwise keep their
      // window-level handlers alive across client-side navigation.
      window.__pchP5?.destroy?.();
    };
  }, [pathname]);

  return null;
}

declare global {
  interface Window {
    __pchMermaid?: { run: () => void };
    __pchP5?: { init: () => void; destroy?: () => void };
    __pchVizFullscreen?: { init: () => void };
    __pchPlayground?: { init: () => void };
  }
}

export default ContentRuntime;

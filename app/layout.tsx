import type { Metadata, Viewport } from "next";
import { Toaster } from "@/components/ui/sonner";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { ErrorReporter } from "@/components/ErrorReporter";
import { ServiceWorker } from "@/components/ServiceWorker";
import { SITE_DESCRIPTION, SITE_NAME, SITE_URL } from "@/lib/site";
import "./globals.css";

/**
 * Stylesheets carried over from astro.config.mjs's `customCss`.
 *
 * These style the *content*, not the chrome: code blocks (global.css targets
 * rehype-pretty-code's output), the visualisation chassis every viz component
 * shares, the DSA tables, and the four webfonts the type scale names. Without
 * them a page renders with correct markup and no styling at all.
 *
 * Phase 2 replaces the chrome-related parts; these stay until their rules are
 * folded into the new design system.
 */
import "./carried-tokens.css";
import "@/src/styles/atkinson.css";
import "@/src/styles/source.css";
import "@/src/styles/fira.css";
import "@/src/styles/global.css";
/* KaTeX and the visualisation / DSA sheets are lesson-only and load from
   app/(docs)/layout.tsx. Here they cost the home page, the catalogue and the
   sign-in screens ~90 KB of CSS they never use. */
/* The account menu in the header and the progress controls on every content
   page are styled by these two, so they are site-wide rather than part of the
   signed-in area. */
import "@/src/styles/auth.css";
import "@/src/styles/progress.css";

/**
 * Root layout.
 *
 * Deliberately thin: the docs shell, header and sidebar are designed in
 * phase 2 (docs/nextjs-migration-plan.md) rather than sketched now and
 * rewritten later. This exists so phase 0 can prove the content pipeline
 * end to end.
 */
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SITE_NAME,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,

  /**
   * Link previews.
   *
   * The Astro head carried these as hand-written meta tags; here the page
   * title and description flow in from each route's own metadata, so a shared
   * tutorial link previews as that tutorial rather than as the site.
   */
  openGraph: {
    type: "website",
    siteName: SITE_NAME,
    // No `url` here. It was "/" and no route overrode it, so every shared
    // lesson previewed as the home page. Without it, link previews use the
    // address that was shared, and crawlers use each page's canonical.
    images: [{ url: "/og.png?v=2", width: 1200, height: 630, alt: SITE_NAME }],
  },
  twitter: {
    card: "summary_large_image",
    images: ["/og.png?v=2"],
  },
  alternates: {
    types: { "application/rss+xml": "/rss.xml" },
  },
  // The files were in public/ all along; nothing linked them.
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "any" },
    ],
    apple: "/images/icons/icon-192x192.png",
  },
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fafafc" },
    { media: "(prefers-color-scheme: dark)", color: "#0d1117" },
  ],
};

/**
 * Apply the remembered theme before the first paint.
 *
 * Runs blocking in <head>: any later and the page paints in the wrong theme
 * first, which is more jarring than the few milliseconds this costs. Wrapped
 * in try/catch because reading localStorage throws outright in a private
 * window rather than returning null.
 */
const THEME_SCRIPT = `
try {
  var t = localStorage.getItem("pch-theme");
  if (!t) t = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.dataset.theme = t;
} catch (e) {}
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
        {/* The body face, both weights every page uses. Declared in
            atkinson.css, so without a preload the browser only finds them
            after that stylesheet has been parsed and text has painted once
            in the fallback -- a visible reflow on every first visit. */}
        <link
          rel="preload"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
          href="/fonts/atkinson/atkinson-hyperlegible-v11-latin_latin-ext-regular.woff2"
        />
        <link
          rel="preload"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
          href="/fonts/atkinson/atkinson-hyperlegible-v11-latin_latin-ext-700.woff2"
        />
      </head>
      <body>
        {children}

        {/* One toast surface for the whole site, styled from the same tokens
            as everything else rather than from sonner's defaults. */}
        <Toaster />

        {/* Page views (cookieless, no personal data) and real-visitor page
            speed, both from Vercel; nothing is sent in development. Uncaught
            browser errors go to /api/client-error. See the privacy policy. */}
        <Analytics />
        <SpeedInsights />
        <ErrorReporter />
        {/* Lessons already opened, and the Python runtime, keep working
            offline. See public/sw.js. */}
        <ServiceWorker />
      </body>
    </html>
  );
}

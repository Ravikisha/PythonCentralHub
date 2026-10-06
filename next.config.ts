import type { NextConfig } from "next";
import { createMDX } from "fumadocs-mdx/next";
import { COURSES } from "./lib/courses.data.mjs";

/**
 * Next.js configuration.
 *
 * Deliberately minimal while the migration is in progress. Redirects for any
 * slug the new build cannot reproduce exactly get added here once
 * `scripts/verify-routes.mjs` reports what they are -- see
 * docs/nextjs-migration-plan.md. There are 1116 indexed URLs, so a slug that
 * silently changes is a ranking lost.
 */
const config: NextConfig = {
  reactStrictMode: true,

  /**
   * Serve `/tutorials/boolean/`, not `/tutorials/boolean`.
   *
   * Every one of the 1195 baseline URLs ends in a slash, because that is what
   * Astro emitted. Next's default is the opposite and 308-redirects to it,
   * which would make the canonical address of all 1183 indexed pages differ
   * from the one in Google's index.
   */
  trailingSlash: true,

  // `.js` is left out on purpose. Next adopts a sibling `pages/` directory as
  // a Pages Router and refuses to run it alongside `app/`; the Astro tree is
  // gone, but this keeps a stray `.js` file under src/ from reviving that.
  pageExtensions: ["ts", "tsx", "mdx"],

  /**
   * Let Node require these rather than bundling them.
   *
   * `dynamic` content mode loads MDX at request time through `satteri`,
   * fumadocs' native markdown compiler. Its webcontainer fallback resolves a
   * `.wasi.cjs` binary through a computed path, which Turbopack cannot follow
   * ("server relative imports are not implemented yet"). Bundling is the wrong
   * tool for a native module anyway.
   */
  serverExternalPackages: ["satteri", "@fumadocs/satteri", "fumadocs-mdx"],

  /**
   * The locale-prefixed URLs.
   *
   * The Astro build published 4740 of them, but only four were ever
   * translated: the rest were Starlight *fallbacks*, which served the English
   * text under a Spanish or Japanese address. Regenerating them here would
   * quintuple a build that already takes twelve minutes, to publish four
   * thousand duplicates of pages that exist in English.
   *
   * So each locale-prefixed path redirects, permanently, to the English page
   * it was always showing. The four real translations are the locale roots
   * (`/es/`, `/hi/`, `/ja/`, `/zh-cn/`), and `:path+` requires at least one
   * segment after the locale, so those keep serving their own content.
   */
  async redirects() {
    return [
      {
        source: "/:locale(es|hi|ja|zh-cn)/:path+",
        // The trailing slash is spelled out: `trailingSlash` does not add one
        // to a redirect destination, and without it every locale URL costs two
        // hops instead of one.
        destination: "/:path+/",
        permanent: true,
      },
      // A course folder's own url was never a page (it 404'd); it is now the
      // course, whose page lives under /courses/. Temporary, so the course
      // folder stays free to become a page of its own later.
      {
        source: `/:course(${COURSES.map((c) => c.slug).join("|")})`,
        destination: "/courses/:course/",
        permanent: false,
      },
    ];
  },

  // The Astro site served these from the same origin; keep them working.
  // The image optimiser is off. Every image here is already sized for the
  // web (figures are SVG or pre-rendered WebP, see
  // scripts/rasterize-figures.mjs), nothing renders through next/image, and
  // on Vercel's free plan the optimiser has its own quota -- this makes sure
  // a stray next/image can never start spending it.
  images: {
    unoptimized: true,
  },

  // The heaviest Mathematics pages (hundreds of KaTeX formulas each) took
  // over the 60 s default to render on a busy builder and only passed on a
  // retry. Headroom here keeps one slow page from failing a deploy.
  staticPageGenerationTimeout: 180,

  typescript: {
    ignoreBuildErrors: false,
  },

  /**
   * Security headers on every response.
   *
   * The Content-Security-Policy ships as Report-Only first: the site loads
   * Pyodide and its wheels, Monaco, mermaid and p5 from CDNs, Firebase Auth
   * opens its own frame, reCAPTCHA has its own scripts, and learners' code may
   * fetch any https URL. Violations are reported to /api/csp-report/ (and so
   * to the error log) instead of breaking a lesson. Once a week of production
   * reports comes back clean, rename the header to Content-Security-Policy.
   *
   * 'unsafe-eval' is needed by p5 sketches (evaluated with `new Function`) and
   * 'wasm-unsafe-eval' by Pyodide. 'unsafe-inline' scripts are needed by the
   * theme script in app/layout.tsx and Next's inline bootstrap.
   */
  async headers() {
    const csp = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://apis.google.com https://www.google.com https://www.gstatic.com https://va.vercel-scripts.com",
      "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
      "img-src 'self' data: blob: https:",
      "font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
      "connect-src 'self' https: wss:",
      "worker-src 'self' blob:",
      "frame-src 'self' https://*.firebaseapp.com https://www.google.com https://recaptcha.google.com",
      "frame-ancestors 'self'",
      "form-action 'self'",
      "base-uri 'self'",
      "object-src 'none'",
      "report-uri /api/csp-report/",
    ].join("; ");

    return [
      {
        source: "/:path*",
        headers: [
          // No includeSubDomains/preload until the domain is settled: preload is
          // hard to undo and would force HTTPS on every subdomain.
          { key: "Strict-Transport-Security", value: "max-age=63072000" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          // Enforced now, unlike the CSP's frame-ancestors above.
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()",
          },
          { key: "Content-Security-Policy-Report-Only", value: csp },
        ],
      },
    ];
  },

  // The lesson text behind full-text search: generated before the build
  // (scripts/gen-search-index.mjs) and read with fs at request time, which
  // the file tracer cannot see on its own.
  outputFileTracingIncludes: {
    "/api/search": ["./.search/fulltext.json"],
  },
};

const withMDX = createMDX();

export default withMDX(config);

import { defineConfig } from "astro/config";
import { fileURLToPath } from "node:url";
import starlight from "@astrojs/starlight";
import rehypePrettyCode from "rehype-pretty-code";
import robotsTxt from "astro-robots-txt";
import remakeMermaid from "./lib/mermaid/remake.ts";
import remakeP5 from "./lib/p5/remake.ts";
import remarkDefaultCodeMeta from "./lib/remark/default-code-meta.ts";
import { unified } from "@astrojs/markdown-remark";
import { LOCALES } from "./src/i18n/locales.ts";
import { withSidebarTranslations, untranslatedLabels } from "./src/i18n/sidebar-labels.ts";

const site = "https://pythoncentralhub.live";

/** @type {import('rehype-pretty-code').Options} */
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import react from "@astrojs/react";

const options = {
  theme: {
    dark: "github-dark-dimmed",
    light: "github-light",
  },
  keepBackground: true,
  grid: true,
  filterMetaString: (string) => string.replace(/filename="[^"]*"/, ""),
  // getHighlighter: (options) =>
  //   getHighlighter({
  //     ...options,
  //     langs: [...BUNDLED_LANGUAGES],
  //   }),
  onVisitLine: (line) => {
    if (line.number === 2) {
      return {
        ...line,
        className: "line-highlight",
      };
    }
    return line;
  },
  onVisitHighlightedLine: (line) => {
    return {
      ...line,
      className: "line-highlight",
    };
  },
  defaultLang: "python",
};
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { visit } from 'unist-util-visit';

// This function finds text nodes and replaces { with its HTML entity
function remarkEscapeBraces() {
  return (tree) => {
    visit(tree, 'text', (node) => {
      if (node.value.includes('{') || node.value.includes('}')) {
        // We replace { with &#123; and } with &#125;
        // This prevents MDX from seeing them as JSX blocks
        node.value = node.value
          .replace(/{/g, '&#123;')
          .replace(/}/g, '&#125;');
      }
    });
  };
}

// https://astro.build/config
export default defineConfig({
  // Astro 7 changed the default to "jsx", which collapses whitespace using
  // React's rules and can drop spaces between inline elements. `true` is the
  // lossless pre-v7 behaviour -- keeps rendered output byte-comparable.
  compressHTML: true,

  image: {
    domains: ["yt3.googleusercontent.com"],
  },

  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  },

  site,
  markdown: {
    // Disable Astro's built-in Shiki highlighting -- rehype-pretty-code below
    // owns every code block on the site.
    syntaxHighlight: false,
    // Astro 7 defaults to the Satteri processor. This site's whole markdown
    // pipeline is remark/rehype (mermaid, p5, KaTeX, rehype-pretty-code), so
    // keep the unified processor and hang the plugins off it.
    processor: unified({
      rehypePlugins: [[rehypePrettyCode, options], rehypeKatex],
      remarkPlugins: [remakeMermaid, remakeP5, remarkDefaultCodeMeta, remarkMath, remarkEscapeBraces],
    }),
  },
  integrations: [
    starlight({
      title: "Python Central Hub",
      logo: {
        src: "./src/assets/pythonlogo.png",
      },
      // English is served at the site root (no `/en/` prefix) so the 1116
      // already-indexed URLs keep working; every other language is prefixed.
      // Untranslated pages fall back to the English content automatically and
      // show Starlight's <FallbackContentNotice />, so a language can ship
      // with a handful of pages translated instead of all 1116.
      defaultLocale: "root",
      locales: LOCALES,
      // Show "Last updated" on content pages, derived from git history.
      lastUpdated: true,
      // Starlight ships Expressive Code, which would take over every fenced
      // block. This site's code styling is rehype-pretty-code (see
      // markdown.processor) + src/styles/global.css, so keep EC out.
      expressiveCode: false,
      components: {
        Footer: "./src/components/Footer.astro",
        // Injects per-page JSON-LD structured data.
        Head: "./src/components/Head.astro",
        // Adds sidebar search + collapse/expand-all with persisted state.
        Sidebar: "./src/components/Sidebar.astro",
      },
      favicon: "./src/assets/favicon.ico",
      // Starlight 0.33 replaced the keyed object with an array of link items.
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/Ravikisha/PythonCentralHub.git" },
        { icon: "instagram", label: "Instagram", href: "https://www.instagram.com/ravikishan.404" },
        { icon: "x.com", label: "X", href: "https://twitter.com/@Ravikishan_" },
        { icon: "email", label: "Email", href: "mailto:ravikishan63392@gmail.com" },
        { icon: "linkedin", label: "LinkedIn", href: "https://www.linkedin.com/in/ravikisha/" },
      ],
      sidebar: withSidebarTranslations([
        {
          label: "Guides",
          items: [{ autogenerate: { directory: "guides" } }],
        },
        {
          label: "Tutorials",
          items: [{ autogenerate: { directory: "tutorials" } }],
        },
        {
          label: "Flask Tutorials",
          items: [{ autogenerate: { directory: "Flask Tutorials" } }],
        },
        {
          label: "Python Automation and Scripting",
          items: [{ autogenerate: { directory: "Python Automation and Scripting" } }],
        },
        {
          label: "Data Analytics",
          items: [{ autogenerate: { directory: "Data Analytics" } }],
        },
        {
          label: "Mathematics for Machine Learning",
          items: [{ autogenerate: { directory: "Mathematics for Machine Learning" } }],
        },
        {
          label: "Machine Learning",
          items: [{ autogenerate: { directory: "Machine Learning" } }],
        },
        {
          label: "Deep Learning",
          items: [{ autogenerate: { directory: "Deep Learning" } }],
        },
        {
          label: "DSA with Python",
          collapsed: true,
          items: [
            {
              label: "Start Here",
              collapsed: true,
              badge: { text: "8", variant: "note" },
              items: [
                {
                  label: "00 · Start Here",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-00-Start-Here" } }],
                },
              ],
            },
            {
              label: "Foundations",
              collapsed: true,
              badge: { text: "29", variant: "note" },
              items: [
                {
                  label: "01 · Foundations",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-01-Foundations" } }],
                },
                {
                  label: "02 · Python for DSA & CP",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-02-Python-for-DSA-and-CP" } }],
                },
                {
                  label: "03 · Core Data Structures",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-03-Core-Data-Structures" } }],
                },
                {
                  label: "04 · Sorting & Searching",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-04-Sorting-and-Searching" } }],
                },
              ],
            },
            {
              label: "Interview Patterns",
              collapsed: true,
              badge: { text: "77", variant: "note" },
              items: [
                {
                  label: "05 · Arrays & Strings",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-05-Patterns-Arrays-and-Strings" } }],
                },
                {
                  label: "06 · Search & Selection",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-06-Patterns-Search-and-Selection" } }],
                },
                {
                  label: "07 · Intervals & Greedy",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-07-Patterns-Intervals-and-Greedy" } }],
                },
                {
                  label: "08 · Linked Lists",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-08-Patterns-Linked-Lists" } }],
                },
                {
                  label: "09 · Trees",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-09-Patterns-Trees" } }],
                },
                {
                  label: "10 · Graphs",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-10-Patterns-Graphs" } }],
                },
                {
                  label: "11 · Recursion & Backtracking",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-11-Recursion-and-Backtracking" } }],
                },
                {
                  label: "12 · Dynamic Programming",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-12-Dynamic-Programming" } }],
                },
                {
                  label: "13 · Bit Manipulation & Math",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-13-Bit-Manipulation-and-Math" } }],
                },
                {
                  label: "14 · Design Problems",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-14-Design-Problems" } }],
                },
                {
                  label: "15 · Simulation & Implementation",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-15-Simulation-and-Implementation" } }],
                },
              ],
            },
            {
              label: "Advanced & Competitive",
              collapsed: true,
              badge: { text: "8", variant: "note" },
              items: [
                {
                  label: "16 · Advanced Graph Algorithms",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-16-Advanced-Graph-Algorithms" } }],
                },
                {
                  label: "17 · Advanced CP Topics",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-17-Advanced-CP-Topics" } }],
                },
              ],
            },
            {
              label: "Reference & Strategy",
              collapsed: true,
              badge: { text: "14", variant: "note" },
              items: [
                {
                  label: "18 · Templates & Cheatsheets",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-18-Templates-and-Cheatsheets" } }],
                },
                {
                  label: "19 · Interview & Contest Strategy",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-19-Interview-and-Contest-Strategy" } }],
                },
                {
                  label: "20 · Problem Sets",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-20-Problem-Sets" } }],
                },
              ],
            },
            {
              label: "Company Guides",
              collapsed: true,
              badge: { text: "10", variant: "note" },
              items: [
                {
                  label: "21 · Company Guides",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-21-Company-Guides" } }],
                },
              ],
            },
            {
              label: "Low-Level Design",
              collapsed: true,
              badge: { text: "5", variant: "note" },
              items: [
                {
                  label: "22 · Low-Level Design (OOD)",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-22-Low-Level-Design" } }],
                },
              ],
            },
            {
              label: "Concurrency",
              collapsed: true,
              badge: { text: "2", variant: "note" },
              items: [
                {
                  label: "23 · Concurrency",
                  collapsed: true,
                  items: [{ autogenerate: { directory: "DSA with Python/Phase-23-Concurrency" } }],
                },
              ],
            },
          ],
        },
        {
          label: "Software Testing and Quality",
          items: [{ autogenerate: { directory: "Software Testing and Quality" } }],
        },
        {
          label: "Projects",
          items: [{ autogenerate: { directory: "projects" } }],
        },
        {
          label: "Reference",
          items: [{ autogenerate: { directory: "reference" } }],
        },
      ]),
      customCss: [
        // Tailwind v4 entrypoint. MUST stay first: it declares the
        // base/starlight/theme/components/utilities layer order.
        "./src/styles/tailwind.css",
        // KaTeX stylesheet — required so remark-math/rehype-katex formulas
        // render with correct glyphs/spacing (fonts bundled by Vite from the pkg).
        "katex/dist/katex.min.css",
        "./src/styles/global.css",
        "./src/styles/theme.css",
        "./src/styles/viz.css",
        // Step-through DSA visualizations (src/components/viz/*). Extends the
        // .pch-viz chassis above, so it must load after viz.css.
        "./src/styles/dsa-viz.css",
        // Maths labs (src/components/viz/math/*): six extra tag pills plus the
        // matrix/axis stage primitives. Extends the same .pch-viz__tag and
        // .pch-vz__* chassis, so it must load after dsa-viz.css.
        "./src/styles/math-viz.css",
        // Problem ladders, sheet trackers and company boards (src/components/dsa/*).
        "./src/styles/dsa-data.css",
        "./src/styles/landing.css",
        "./src/styles/poppins.css",
        "./src/styles/atkinson.css",
        "./src/styles/source.css",
        "./src/styles/fira.css",
      ],
      head: [
        {
          tag: "meta",
          attrs: {
            property: "og:image",
            content: site + "/og.png?v=1",
          },
        },
        {
          tag: "meta",
          attrs: {
            property: "twitter:image",
            content: site + "/og.png?v=1",
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "/fontawesome/css/all.min.css",
          },
        },
        {
          tag: "script",
          attrs: {
            src: "/scripts/main.js",
          },
        },
        ...(import.meta.env.VITE_GOOGLE_ADSENSE
          ? [
              {
                tag: "meta",
                attrs: {
                  name: "google-adsense-account",
                  content: import.meta.env.VITE_GOOGLE_ADSENSE,
                },
              },
            ]
          : []),
        {
          tag: "meta",
          attrs: {
            name: "og:description",
            property: "og:description",
            content:
              "The Python Projects Repository is designed to provide a comprehensive collection of open-source Python projects that span different domains. These projects aim to serve as educational resources, examples, and starting points for your Python journey.",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "og:url",
            property: "og:url",
            content: site,
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:card",
            content: "summary_large_image",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:title",
            content: "Python Central Hub",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:description",
            content:
              "The Python Projects Repository is designed to provide a comprehensive collection of open-source Python projects that span different domains. These projects aim to serve as educational resources, examples, and starting points for your Python journey.",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:image:alt",
            content: "Python Central Hub",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:site",
            content: "@Ravikishan_",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:creator",
            content: "@Ravikishan_",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:domain",
            content: site,
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "keywords",
            content:
              "Python, Python Projects, Python Central Hub, Python Central Hub Projects, Python Central Hub Tutorials, Python Central Hub Guides, Python Central Hub Reference, Python Tutorial, Python tutorials, Python programming, Learn Python, Python for beginners, Python code examples, Python development, Python projects,Python programming language, Python tips and tricks,Python resources,Python learning platform,Python coding lessons,Python programming for beginners,Python programming exercises,Python coding practice,Python syntax,Python libraries,Python community,Python best practices,Python coding challenges",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "author",
            content: "Ravi Kishan",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "robots",
            content: "index, follow",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "google-site-verification",
            content: "APcUc_Z3jsswucDreyJEXK3kcIpbw1wqRx0lO9VHjOA",
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "manifest",
            href: "/manifest.json",
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "alternate",
            type: "application/rss+xml",
            title: "Python Central Hub RSS Feed",
            href: "/rss.xml",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "theme-color",
            content: "#4b8bbe",
          },
        },
        ...(import.meta.env.VITE_GOOGLE_ANALYTICS
          ? [
              {
                tag: "script",
                attrs: {
                  async: true,
                  src: `https://www.googletagmanager.com/gtag/js?id=${import.meta.env.VITE_GOOGLE_ANALYTICS}`,
                },
              },
              {
                tag: "script",
                attrs: {
                  async: true,
                  src: "/scripts/gtag.js",
                },
              },
            ]
          : []),
        {
          tag: "script",
          attrs: {
            async: true,
            type: "module",
            src: "/scripts/mermaid.js",
          },
        },
        {
          tag: "script",
          attrs: {
            defer: true,
            src: "/scripts/p5-viz.js",
          },
        },
        {
          // Adds a "view fullscreen" button to mermaid, p5 and (non-python)
          // code blocks. ES module — imports the shared editor-fullscreen modal.
          tag: "script",
          attrs: {
            type: "module",
            src: "/scripts/viz-fullscreen.js",
          },
        },
        ...(import.meta.env.VITE_GOOGLE_ADSENSE
          ? [
              {
                tag: "script",
                attrs: {
                  async: true,
                  src: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${import.meta.env.VITE_GOOGLE_ADSENSE}`,
                  crossorigin: "anonymous",
                },
              },
            ]
          : []),

        {
          tag: "link",
          attrs: {
            rel: "preconnect",
            href: "https://cdn.datacamp.com",
            crossorigin: true,
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "dns-prefetch",
            href: "https://cdn.datacamp.com",
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://cdn.datacamp.com/dcl-react.css",
          },
        },
        {
          tag: "script",
          attrs: {
            src: "https://cdn.datacamp.com/dcl-react.js.gz",
          },
        }
      ],
    }),
    react(),
    sitemap({
      // Emit <xhtml:link rel="alternate" hreflang="..."> for every locale so
      // search engines treat the five language variants as one page, not as
      // duplicate content. Mirrors what Starlight's own sitemap helper does;
      // spelled out here because this config passes a custom `serialize`.
      i18n: {
        defaultLocale: "root",
        locales: Object.fromEntries(
          Object.entries(LOCALES).map(([segment, { lang }]) => [segment, lang]),
        ),
      },
      // Give index/guides/tutorials higher priority than deep pages and
      // stamp a build-time lastmod so crawlers see fresh dates.
      serialize(item) {
        const url = item.url;
        if (url === `${site}/`) {
          item.priority = 1.0;
        } else if (url.includes("/guides/")) {
          item.priority = 0.9;
        } else if (url.includes("/tutorials/")) {
          item.priority = 0.8;
        } else if (url.includes("/projects/")) {
          item.priority = 0.7;
        } else {
          item.priority = 0.6;
        }
        item.changefreq = "weekly";
        item.lastmod = new Date().toISOString();
        return item;
      },
    }),
    robotsTxt(),
  ],
});

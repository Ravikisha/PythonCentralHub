import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import rehypePrettyCode from "rehype-pretty-code";
import robotsTxt from "astro-robots-txt";
import remakeMermaid from "./lib/mermaid/remake.ts";
import markdownIntegration from "@astropub/md";

const site = "https://pythoncentralhub.live";

/** @type {import('rehype-pretty-code').Options} */
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

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
  image: {
    domains: ["yt3.googleusercontent.com"],
  },

  site,
  markdown: {
    syntaxHighlight: false,
    // Disable syntax built-in syntax hightlighting from astro
    rehypePlugins: [[rehypePrettyCode, options], rehypeKatex],
    remarkPlugins: [remakeMermaid, remarkMath, remarkEscapeBraces],
  },
  integrations: [
    starlight({
      title: "Python Central Hub",
      logo: {
        src: "./src/assets/pythonlogo.png",
      },
      // Show "Last updated" on content pages, derived from git history.
      lastUpdated: true,
      components: {
        Footer: "./src/components/Footer.astro",
        // Injects per-page JSON-LD structured data.
        Head: "./src/components/Head.astro",
        // Adds sidebar search + collapse/expand-all with persisted state.
        Sidebar: "./src/components/Sidebar.astro",
      },
      favicon: "./src/assets/favicon.ico",
      social: {
        github: "https://github.com/Ravikisha/PythonCentralHub.git",
        instagram: "https://www.instagram.com/ravikishan.404",
        "x.com": "https://twitter.com/@Ravikishan_",
        email: "mailto:ravikishan63392@gmail.com",
        linkedin: "https://www.linkedin.com/in/ravikisha/",
      },
      sidebar: [
        {
          label: "Guides",
          autogenerate: {
            directory: "guides",
          },
        },
        {
          label: "Tutorials",
          autogenerate: {
            directory: "tutorials",
          },
        },
        {
          label: "Flask Tutorials",
          autogenerate: {
            directory: "Flask Tutorials",
          },
        },
        {
          label: "Python Automation and Scripting",
          autogenerate: {
            directory: "Python Automation and Scripting",
          },
        },
        {
          label: "Data Analytics",
          autogenerate: {
            directory: "Data Analytics",
          },
        },
        {
          label: "Machine Learning",
          autogenerate: {
            directory: "Machine Learning",
          },
        },
        {
          label: "Software Testing and Quality",
          autogenerate: {
            directory: "Software Testing and Quality",
          },
        },
        {
          label: "Projects",
          autogenerate: {
            directory: "projects",
          },
        },
        {
          label: "Reference",
          autogenerate: {
            directory: "reference",
          },
        },
      ],
      customCss: [
        "./src/styles/global.css",
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
        ...(import.meta.env.VITE_MONETAG
          ? [
              {
                tag: "meta",
                attrs: {
                  name: "monetag",
                  content: `${import.meta.env.VITE_MONETAG}`,
                },
              },
            ]
          : []),
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
        // <script src="https://quge5.com/88/tag.min.js" data-zone="217965" async data-cfasync="false"></script>
        {
          tag: "script",
          attrs: {
            src: "https://quge5.com/88/tag.min.js",
            "data-zone": "217965",
            async: true,
            "data-cfasync": "false"
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "theme-color",
            content: "#e7c384",
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
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap({
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
    markdownIntegration(),
  ],
});

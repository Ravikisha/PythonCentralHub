import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import rehypePrettyCode from "rehype-pretty-code";
import robotsTxt from "astro-robots-txt";
import remakeMermaid from "./lib/mermaid/remake.ts";
import markdownIntegration from "@astropub/md";

const site = "https://python-central-hub.vercel.app";

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

// https://astro.build/config
export default defineConfig({
  image: {
    domains: ["yt3.googleusercontent.com"],
  },
  
  site,
  markdown: {
    syntaxHighlight: false,
    // Disable syntax built-in syntax hightlighting from astro
    rehypePlugins: [[rehypePrettyCode, options]],
    remarkPlugins: [remakeMermaid],
  },
  integrations: [
    starlight({
      title: "Python Central Hub",
      logo: {
        src: "./src/assets/pythonlogo.png",
      },
      components: {
        Footer: './src/components/Footer.astro',
      },
      // editLink: {
      //   baseUrl: "https://github.com/Ravikisha/PythonCentralHub/edit/main/",
      // },
      favicon: "./src/assets/favicon.ico",
      social: {
        github: "https://github.com/Ravikisha/PythonCentralHub.git",
        instagram: "https://www.instagram.com/ravikishan.69",
        "x.com": "https://twitter.com/@Ravikishan_",
        email: "mailto:ravikishan63392@gmail.com",
        linkedin: "https://www.linkedin.com/in/ravi-kishan-62ab51221/",
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
        {
          tag: "meta",
          attrs: {
            name: "google-adsense-account",
            content: import.meta.env.VITE_GOOGLE_ADSENSE,
          },
        },
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
          tag: "meta",
          attrs: {
            name: "theme-color",
            content: "#e7c384",
          },
        },
        {
          tag: "script",
          attrs: {
            async: true,
            src: `https://www.googletagmanager.com/gtag/js?id=${
              import.meta.env.VITE_GOOGLE_ANALYTICS
            }`,
          },
        },
        {
          tag: "script",
          attrs: {
            async: true,
            src: "/scripts/gtag.js",
          },
        },
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
            async: true,
            src: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${
              import.meta.env.VITE_GOOGLE_ADSENSE
            }`,
            crossorigin: "anonymous",
          },
        },
      ],
    }),
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap(),
    robotsTxt(),
    markdownIntegration(),
  ],
});

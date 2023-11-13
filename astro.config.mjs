import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import rehypePrettyCode from "rehype-pretty-code";

/** @type {import('rehype-pretty-code').Options} */
import tailwind from "@astrojs/tailwind";
const options = {
  theme: {
    dark: "github-dark-dimmed",
    light: "github-light",
  },
  keepBackground: true,
  grid: true,
  filterMetaString: (string) => string.replace(/filename="[^"]*"/, ""),
  //   getHighlighter: (options) =>
  //     getHighlighter({
  //       ...options,
  //       langs: [
  //         ...BUNDLED_LANGUAGES,
  //         {
  //           id: "groq",
  //           scopeName: "source.groq",
  //           path: "./langs/vscode-sanity/grammars/groq.json",
  //         },
  //       ],
  //     }),
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
  markdown: {
    syntaxHighlight: false,
    // Disable syntax built-in syntax hightlighting from astro
    rehypePlugins: [[rehypePrettyCode, options]],
  },
  integrations: [
    starlight({
      title: "Python Central Hub",
      logo: {
        src: "./src/assets/pythonlogo.png",
      },
      editLink: {
        baseUrl: "https://github.com/Ravikisha/PythonCentralHub/edit/main/",
      },
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
      customCss: ["./src/styles/global.css"],
      head: [
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
            integrity:
              "sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==",
            crossorigin: "anonymous",
            referrerpolicy: "no-referrer",
          },
        },
        {
          tag: "script",
          attrs: {
            src: "/scripts/main.js",
          },
        },
      ],
    }),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
});

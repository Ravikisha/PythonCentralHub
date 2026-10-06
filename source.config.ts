/**
 * Content source for the Next.js site.
 *
 * Fumadocs is used headless: this file and `lib/source.ts` give us the parts
 * that are tedious and invisible -- frontmatter validation, slug and page-tree
 * generation, TOC extraction, search indexing -- while every rendered pixel
 * stays ours. None of Fumadocs' own UI is imported anywhere.
 *
 * `dir` still points at the Astro tree. Moving the 1190 files is phase 4 of
 * docs/nextjs-migration-plan.md; until then both frameworks read the same
 * content, which is what makes the route diff meaningful.
 */
import { defineDocs, defineConfig } from "fumadocs-mdx/config";
import { z } from "zod";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeCodeChrome from "./lib/rehype/code-chrome";
import rehypeHeadingAnchors from "./lib/rehype/heading-anchors";
import rehypeRaw from "rehype-raw";
import rehypePrettyCode from "rehype-pretty-code";
import remakeMermaid from "./lib/mermaid/remake";
import remakeP5 from "./lib/p5/remake";
import remarkDirective from "remark-directive";
import { remarkDirectiveAdmonition } from "fumadocs-core/mdx-plugins/remark-directive-admonition";

/**
 * DSA interview metadata, carried over from src/content.config.ts.
 *
 * Every field is optional, and must stay that way: roughly 700 of the 1190
 * pages set none of them, and a required field here fails their build.
 */
const dsaMeta = z
  .object({
    /** Pattern slugs this page teaches, e.g. `sliding-window`. */
    patterns: z.array(z.string()).optional(),
    difficulty: z.enum(["easy", "medium", "hard", "mixed"]).optional(),
    /** Pattern slugs a reader should have covered first. */
    prereqs: z.array(z.string()).optional(),
    /** Where the topic sits in each public study sheet. */
    sheets: z.record(z.string(), z.union([z.string(), z.boolean()])).optional(),
    companies: z.array(z.string()).optional(),
  })
  .optional();

/** rehype-pretty-code options, unchanged from the Astro build. */
const prettyCodeOptions = {
  theme: { dark: "github-dark-dimmed", light: "github-light" },
  keepBackground: true,
  grid: true,
  filterMetaString: (str: string) => str.replace(/filename="[^"]*"/, ""),
  defaultLang: "python",
  onVisitLine(line: { number?: number; className?: string }) {
    if (line.number === 2) return { ...line, className: "line-highlight" };
    return line;
  },
  onVisitHighlightedLine(line: { className?: string }) {
    return { ...line, className: "line-highlight" };
  },
};

export const docs = defineDocs({
  dir: "src/content/docs",
  docs: {
    /**
     * Load content on demand instead of bundling every file.
     *
     * Without this, `.source/server.ts` statically imports all 1190 MDX
     * files, so the first request compiles the entire corpus -- measured at
     * over eight minutes in dev before timing out. Async mode compiles a page
     * when it is asked for, which is the only workable shape at this size.
     */
    async: true,

    /**
     * Read content through the filesystem at runtime rather than as bundler
     * imports.
     *
     * `async` alone still emits one import per file -- 1190 of them, which
     * Turbopack did not finish compiling in five minutes. Dynamic mode removes
     * the static import graph entirely, which is the only thing that scales at
     * this corpus size.
     */
    dynamic: true,

    // Starlight showed "Last updated" from git history; keep the data
    // available so the new design can decide whether to.
    lastModified: true,
    schema: z.object({
      title: z.string(),
      description: z.string().optional(),
      /** Starlight's splash pages. The new layout reads this to pick a shell. */
      template: z.enum(["doc", "splash"]).optional(),
      /** Starlight hero block -- only the landing page uses it. */
      hero: z.unknown().optional(),
      editUrl: z.union([z.string(), z.boolean()]).optional(),
      /**
       * Starlight's sidebar controls. Only `order` is read, by `lib/order.ts`:
       * 1264 pages carry one, and it is the author's own ordering of the
       * course. Typed rather than `unknown` so the sort can rely on it.
       */
      sidebar: z
        .object({
          order: z.number().optional(),
          label: z.string().optional(),
          hidden: z.boolean().optional(),
          badge: z.unknown().optional(),
        })
        .passthrough()
        .optional(),
      dsa: dsaMeta,
      draft: z.boolean().optional(),
    }),
  },
});

export default defineConfig({
  mdxOptions: {
    /**
     * The same unified plugins the Astro build used -- they are ordinary
     * remark plugins, so they port unchanged.
     *
     * The two "remake" plugins are not optional: 926 content files use a
     * ```mermaid fence and 556 use ```p5. Without them Shiki is handed those
     * fences as if they named a language and fails with
     * "Language `p5` not found".
     *
     * KaTeX likewise: the Mathematics for Machine Learning module is
     * unreadable without it.
     */
    remarkPlugins: [
      remakeMermaid,
      remakeP5,
      /**
       * Asides: 666 files carry 2186 `:::note` / `:::tip` / `:::caution` /
       * `:::danger` blocks, which Starlight used to render. Without these two
       * the directive text prints literally in the middle of the prose.
       *
       * `remark-directive` parses the syntax (including the `[label]` form);
       * the admonition transform turns it into the components below, which
       * components/learn/Aside.tsx provides.
       */
      remarkDirective,
      [
        remarkDirectiveAdmonition,
        {
          tags: {
            CalloutContainer: "Callout",
            CalloutTitle: "CalloutTitle",
            CalloutDescription: "CalloutBody",
          },
          // Starlight's four kinds, mapped onto this site's four tones.
          types: {
            note: "info",
            info: "info",
            tip: "tip",
            caution: "warn",
            warning: "warn",
            danger: "error",
          },
        },
      ],
      remarkMath,
    ],
    /**
     * `rehype-raw` parses the raw HTML the mermaid and p5 plugins emit.
     *
     * Those plugins replace a fence with an mdast `html` node, which becomes a
     * hast `raw` node that MDX refuses outright ("Cannot handle unknown node
     * `raw`"). Astro's pipeline accepted it; MDX needs this step to turn the
     * string into real elements.
     *
     * `passThrough` is mandatory: without it this strips every MDX construct
     * on the page -- every <Quiz>, every <DataCampExercise> -- because they
     * are not HTML as far as it is concerned.
     */
    rehypePlugins: [
      [
        rehypeRaw,
        {
          passThrough: [
            "mdxjsEsm",
            "mdxFlowExpression",
            "mdxTextExpression",
            "mdxJsxFlowElement",
            "mdxJsxTextElement",
          ],
        },
      ],
      /**
       * The site's own highlighter, carried over from astro.config.mjs.
       *
       * Fumadocs ships a Shiki step of its own, but it emits different markup,
       * and every code-block rule in src/styles/global.css is written against
       * rehype-pretty-code's `data-rehype-pretty-code-*` wrapper and
       * `[data-line]` spans. Using theirs would silently unstyle every code
       * block on 1190 pages -- and it also threw on the `math` language that
       * the KaTeX pipeline produces.
       *
       * Options are byte-for-byte the Astro ones so output stays comparable.
       */
      [rehypePrettyCode, prettyCodeOptions],
      /* One header row per code block -- language on the left, copy on the
         right -- because a fence without `filename=` had no frame at all. */
      rehypeCodeChrome,
      /* A `#` in the gutter of every section heading, so a step of a tutorial
         can be linked to directly. */
      rehypeHeadingAnchors,
      rehypeKatex,
    ],

    // Fumadocs' own Shiki step, disabled in favour of the above. Leaving both
    // on would highlight every block twice.
    rehypeCodeOptions: false,
  },
});

import { visit } from "unist-util-visit";

/**
 * Ensure every fenced code block renders the terminal header bar.
 *
 * rehype-pretty-code only emits the title element (`div[data-rehype-pretty-code-title]`,
 * which global.css styles into the traffic-dots + `>>>` header) when the fence
 * carries a `title="..."`. Snippets written as a bare ```python therefore render
 * headerless. This plugin gives those blocks a sensible default so the header is
 * always visible and consistent:
 *   - `title="<language>"` when no title/filename is set (falls back to "text"),
 *   - `showLineNumbers` when not already requested (sets the gutter width attr;
 *     the actual numbering is drawn by the CSS counter in global.css).
 *
 * Authors can still override either by writing their own `title=` / `showLineNumbers`.
 * Runs AFTER remakeMermaid/remakeP5 in astro.config, so ```mermaid and ```p5 blocks
 * have already been turned into their own panels and are never touched here.
 */
export default function remarkDefaultCodeMeta() {
  return (tree: any) => {
    visit(tree, "code", (node: any) => {
      const lang = (node.lang || "").toLowerCase();

      // These render as their own instrument panels, not fenced code.
      if (lang === "mermaid" || lang === "p5") return;

      let meta: string = node.meta || "";

      if (!/\btitle\s*=/.test(meta)) {
        const label = lang || "text";
        meta = `${meta} title="${label}"`.trim();
      }

      if (!/\bshowLineNumbers\b/.test(meta)) {
        meta = `${meta} showLineNumbers`.trim();
      }

      node.meta = meta;
    });
  };
}

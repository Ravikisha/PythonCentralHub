import { visit } from "unist-util-visit";

/**
 * Make every section heading linkable.
 *
 * The headings already carry ids -- the table of contents jumps to them -- but
 * there was no way to copy the link to one, which is how people share a
 * specific step of a tutorial. This adds a `#` in the gutter, shown on hover
 * or keyboard focus (see components/docs/code.css).
 *
 * `h1` is skipped: the page title is the page's own URL.
 */
interface Node {
  type: string;
  tagName?: string;
  properties?: Record<string, unknown>;
  children?: Node[];
  value?: string;
}

const LEVELS = new Set(["h2", "h3", "h4"]);

export default function rehypeHeadingAnchors() {
  return (tree: Node) => {
    visit(tree, "element", (node: Node) => {
      if (!node.tagName || !LEVELS.has(node.tagName)) return;

      const id = node.properties?.id;
      if (typeof id !== "string" || !id) return;

      node.children = [
        {
          type: "element",
          tagName: "a",
          properties: {
            href: `#${id}`,
            className: ["heading-anchor"],
            ariaLabel: "Link to this section",
            tabIndex: -1,
          },
          /* Empty on purpose. The `#` is drawn by CSS, because the table of
             contents takes its labels from the heading's text: a literal
             character here prefixed every entry in it with a stray hash. */
          children: [],
        },
        ...(node.children ?? []),
      ];
    });
  };
}

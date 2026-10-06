import { visit } from "unist-util-visit";

/**
 * Give every code block a header, whether or not the author titled it.
 *
 * rehype-pretty-code emits a <figure> with an optional <figcaption> title, so
 * a plain ```python fence rendered as a bare slab of colour with no frame and
 * nothing to press. This adds one row at the top of each block carrying the
 * language and a copy button, and hoists the language onto the figure so the
 * stylesheet can reach it (it lives on the <pre>, where CSS cannot read it
 * from an ancestor).
 *
 * The button is inert markup. `components/docs/ContentRuntime.tsx` listens for
 * clicks on `[data-copy]` once per page rather than shipping a handler per
 * block -- there are 7,131 of them.
 *
 * Runs after rehype-pretty-code, which is the only thing that creates these
 * figures.
 */
interface Node {
  type: string;
  tagName?: string;
  properties?: Record<string, unknown>;
  children?: Node[];
  value?: string;
}

/** Display names for the languages this site actually uses. */
const LANGUAGE_NAMES: Record<string, string> = {
  py: "Python",
  python: "Python",
  js: "JavaScript",
  javascript: "JavaScript",
  ts: "TypeScript",
  typescript: "TypeScript",
  jsx: "JSX",
  tsx: "TSX",
  sh: "Shell",
  bash: "Shell",
  zsh: "Shell",
  shell: "Shell",
  console: "Console",
  text: "Text",
  plaintext: "Text",
  json: "JSON",
  yaml: "YAML",
  yml: "YAML",
  toml: "TOML",
  html: "HTML",
  css: "CSS",
  sql: "SQL",
  md: "Markdown",
  mdx: "MDX",
  diff: "Diff",
  ini: "INI",
  xml: "XML",
  c: "C",
  cpp: "C++",
  java: "Java",
  go: "Go",
  rust: "Rust",
  dockerfile: "Dockerfile",
};

/** Longer than this and the block folds, with a control to open it. */
const LONG_BLOCK_LINES = 28;

function element(
  tagName: string,
  properties: Record<string, unknown>,
  children: Node[] = [],
): Node {
  return { type: "element", tagName, properties, children };
}

function text(value: string): Node {
  return { type: "text", value };
}

/** The copy glyph, inline so no icon runtime is needed inside content HTML. */
function copyIcon(): Node {
  return element(
    "svg",
    {
      viewBox: "0 0 24 24",
      width: 15,
      height: 15,
      fill: "none",
      stroke: "currentColor",
      strokeWidth: 1.8,
      strokeLinecap: "round",
      strokeLinejoin: "round",
      ariaHidden: "true",
    },
    [
      element("rect", { x: 9, y: 9, width: 11, height: 11, rx: 2 }),
      element("path", { d: "M5 15V6a1 1 0 0 1 1-1h9" }),
    ],
  );
}

export default function rehypeCodeChrome() {
  return (tree: Node) => {
    visit(tree, "element", (node: Node) => {
      const isFigure =
        node.tagName === "figure" &&
        node.properties &&
        "data-rehype-pretty-code-figure" in node.properties;

      if (!isFigure || !node.children) return;

      const pre = node.children.find((child) => child.tagName === "pre");
      if (!pre) return;

      const language = String(pre.properties?.["data-language"] ?? "text");
      const label = LANGUAGE_NAMES[language] ?? language;

      // How many lines: rehype-pretty-code's `grid` mode emits one element per
      // line. A snippet longer than a screen is folded rather than pushing the
      // prose that explains it off the page.
      const code = pre.children?.find((child) => child.tagName === "code");
      const lines = (code?.children ?? []).filter(
        (child) => child.properties && "data-line" in child.properties
      ).length;
      const long = lines > LONG_BLOCK_LINES;

      node.properties = {
        ...node.properties,
        "data-lang": language,
        ...(long ? { "data-long": "true", "data-lines": String(lines) } : {}),
      };

      const caption = node.children.find(
        (child) =>
          child.properties &&
          "data-rehype-pretty-code-title" in child.properties,
      );

      const button = element(
        "button",
        {
          type: "button",
          className: ["code__copy"],
          "data-copy": "",
          title: "Copy code",
          ariaLabel: "Copy code",
        },
        [
          copyIcon(),
          element("span", { className: ["code__copy-label"] }, [text("Copy")]),
        ],
      );

      /** Sits under a folded block; the delegated handler unfolds it. */
      const unfold = element(
        "button",
        {
          type: "button",
          className: ["code__more"],
          "data-unfold": "",
        },
        [text(`Show all ${lines} lines`)]
      );

      if (caption) {
        // An author-titled block keeps its title; the button joins that row.
        caption.children = [...(caption.children ?? []), button];
        if (long) node.children = [...node.children, unfold];
        return;
      }

      node.children = [
        element("div", { className: ["code__bar"] }, [
          element("span", { className: ["code__lang"] }, [text(label)]),
          button,
        ]),
        ...node.children,
        ...(long ? [unfold] : []),
      ];
    });
  };
}

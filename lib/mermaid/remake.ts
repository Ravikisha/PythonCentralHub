/**
 * WIP
 *
 * Some bits of code are from https://github.com/sjwall/mdx-mermaid
 *
 * Using Parcel to bundle this plugin because
 * Astro uses MJS for its config file.
 * (It seems that it support TS too, but it breaks some third-parties)
 *
 * Also, this could be a separate remark plugin?
 */

/**
 * Code from
 * Astro Diagrams (https://code.juliancataldo.com/component/astro-diagram/)
 *
 */

// TODO: Proper TypeScript rehaul for this file.

// eslint-disable-next-line import/no-extraneous-dependencies
import { visit } from "unist-util-visit";
import renderDiagram from "./render-diagram";

function getTitle(meta: string) {
  if (!meta) return false;
  if (meta.length === 0) return false;

  // Use a regular expression to extract the title value
  const match = meta.match(/title="([^"]*)"/);

  // Check if a match is found
  if (match) {
    // Extract the title value
    const title = match[1];

    return title;
  } else {
    return false;
  }
}

function getDesc(meta: string) {
  if (!meta) return false;
  if (meta.length === 0) return false;

  // Use a regular expression to extract the title value
  const match = meta.match(/desc="([^"]*)"/);

  // Check if a match is found
  if (match) {
    // Extract the title value
    const desc = match[1];

    return desc;
  } else {
    return false;
  }
}

function plugin() {
  return async function transformer(ast: any) {
    // Find all the mermaid diagram code blocks. i.e. ```mermaid
    const instances: any[] = [];
    visit(ast, { type: "code", lang: "mermaid" }, (node, index, parent) => {
      instances.push([node, index, parent]);
    });
    // Replace each Mermaid code block with the server-side rendered SVG
    await Promise.all(
      instances.map(async ([node, index, parent]) => {
        // MDX rendering seems to be already cached.
        // or this keep running puppeeter ?
        // Also, disabling it prevent a bug which doesn't
        // occur in the regular component.
        let html: string;
        try {
          html = await renderDiagram({
            config: {},
            code: node.value,
          }).then((diagram) => diagram);
        } catch (err) {
          // A single bad diagram must not kill the whole build/page.
          // Emit the original mermaid source so the author can debug it.
          const message = err instanceof Error ? err.message : String(err);
          console.warn(`[mermaid] Failed to render diagram: ${message}`);
          const escaped = node.value
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
          parent.children.splice(index, 1, {
            type: "html",
            value: `<!-- mermaid render failed: ${message.replace(/--+/g, "—")} -->\n<pre class="mermaid-error"><code>${escaped}</code></pre>`,
            position: node.position,
          });
          return;
        }

        const title = getTitle(node.meta);
        const desc = getDesc(node.meta);
        // Class-based "instrument panel" — styling lives in src/styles/viz.css
        // so it themes with the site (see the .pch-viz / .mermaid-diagram rules)
        // instead of the old hard-coded white card.
        parent.children.splice(index, 1, {
          type: "html",
          value: `
<figure class="pch-viz mermaid-diagram">
  <div class="pch-viz__bar">
    <span class="pch-viz__dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="pch-viz__tag">diagram</span>
    <span class="pch-viz__title">${title || "Diagram"}</span>
    <span class="pch-viz__lib">mermaid</span>
  </div>
  <div class="mermaid-diagram__stage">
    ${html}
  </div>
  ${desc ? `<figcaption class="pch-viz__cap">${desc}</figcaption>` : ""}
</figure>
          `,

          position: node.position,
        });
      }),
    );

    return ast;
  };
}

export default plugin;

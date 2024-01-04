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

const style = `all: initial; width: 100%;display: flex; flex-direction: column; justify-content: center;align-items: center; background-color: #fff; border-radius: 0.5rem; box-shadow: 10px 24px 50px 17px rgba(0, 0, 0, 0.1);border: 1px solid #c2c2c2;`;

function getTitle(meta: string) {
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
        const html = await renderDiagram({
          config: {},
          code: node.value,
        }).then((diagram) => diagram);

        parent.children.splice(index, 1, {
          type: "html",
          // TODO: put CSS elsewhere
          value: `
          <div class="mermaid-diagram" style="${style}">
          <p style="text-align: center;color: #222;font-size: 1rem; margin: 1rem 0 1rem 0; font-family: 'Atkinson Hyperlegible', sans-serif;padding: 0 1rem 0 1rem;">${
            getDesc(node.meta) ?? ""
          }</p>
          <hr style="width: 80%; margin: 0.5rem 0 0.5rem 0; border: 1px solid #c2c2c2;"/>
          ${html}
          <h2 style="text-align: center;color: #222;font-size: 1.5rem; font-weight: 500; margin: 1rem 0 1rem 0; font-family: 'Atkinson Hyperlegible', sans-serif;">${
            getTitle(node.meta) ?? ""
          }</h2>
          </div>
          `,

          position: node.position,
        });
      })
    );

    return ast;
  };
}

export default plugin;

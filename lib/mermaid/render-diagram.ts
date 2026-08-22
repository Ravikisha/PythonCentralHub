// import path from 'node:path';
// import fs from 'node:fs/promises';
// // import { createRequire } from 'module';
// import puppeteer from 'puppeteer';
/* ·········································································· */
// import type { Props } from './Props';

/* —————————————————————————————————————————————————————————————————————————— */

// FIXME: prefer this method over `fs.readFile`.
// Parceled MDX plugin wasn't working well with this ——v
// const require = createRequire(import.meta.url);
// const path = require.resolve('mermaid/dist/mermaid.js');

/**
 * Code from
 * Astro Diagrams (https://code.juliancataldo.com/component/astro-diagram/)
 *
 */

export default async function renderDiagram({ config, code }: any) {
  /* const browser = await puppeteer.launch({ args: ['--no-sandbox'], headless: "new" });
  const page = await browser.newPage();

  const content = await fs.readFile(
    path.join(process.cwd(), 'node_modules/mermaid/dist/mermaid.js'),
    'utf8',
  );

  await page.addScriptTag({ content });

  const result: {
    status: string;
    error?: Error;
    message?: string;
    svgCode?: string;
  } = await page.evaluate(
    async(configB, codeB: string) => {
      // FIXME: `window.mermaid` global browser stubbing
    //   window.mermaid.initialize(configB);
    const mermaidAPI = window.mermaid.mermaidAPI;

      try {
        const svgCode = await mermaidAPI.render('diagram', codeB);
        return { status: 'success', svgCode: svgCode.svg };
      } catch (error: any) {
        return { status: 'error', error, message: error.message };
      }
    },
    config,
    code,
  );

  await browser.close();

  if (result.status === 'success' && typeof result.svgCode === 'string') {
    return result.svgCode;
  }

  return false;
  */

  // This string is spliced into the mdast as a raw `html` node, and MDX compiles
  // raw HTML straight into JSX. A bare `{` there therefore opens a JSX expression
  // and the build dies with "Unexpected end of file in expression, expected a
  // corresponding closing brace for `{`". Mermaid uses braces for decision nodes
  // (`Q{"..."}`) and for class/state bodies, so this hits real diagrams — 249 of
  // the 932 blocks in this repo contain one.
  //
  // Numeric character references keep MDX out of it while surviving to the
  // client: mermaid runs with startOnLoad and reads `.mermaid` via textContent,
  // which decodes `&#123;` back to `{` before parsing the diagram.
  const escapeBraces = (s: string) =>
    s.replace(/{/g, "&#123;").replace(/}/g, "&#125;");

  // Provide a text alternative for screen readers. The mermaid client script
  // renders an <svg> into this <pre>; the role/aria-label survive on the element
  // so assistive tech can still describe the diagram from its source.
  const ariaLabel = escapeBraces(
    code
      .trim()
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\s+/g, " "),
  );

  const htmlCode = `
<pre class="mermaid" role="img" aria-label="Diagram: ${ariaLabel}" style="all: initial; width: 100%;display: flex; flex-direction: column; justify-content: center;align-items: center;">
  ${escapeBraces(code.trimStart())}
</pre>
  `;
  return htmlCode;
}

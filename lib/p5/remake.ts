/**
 * Remark plugin: turn ```p5 fenced code blocks into interactive p5.js
 * "instrument panels". Mirrors the mermaid pipeline (lib/mermaid/remake.ts):
 * the sketch runs on the client (public/scripts/p5-viz.js) — here we only
 * emit the panel markup and stash the sketch source as base64 in a data
 * attribute (base64 dodges all HTML/MDX escaping + brace-parsing pitfalls).
 *
 * Author syntax:
 *   ```p5 title="Bouncing ball" desc="A ball under gravity" height="360"
 *   function setup(){ createCanvas(600, 360); }
 *   function draw(){ background(13,17,23); circle(mouseX, mouseY, 40); }
 *   ```
 *
 * Sketches are written in ordinary p5 global style (bare `createCanvas`,
 * `draw`, …); the runtime wraps them in instance mode so many sketches can
 * share one page without colliding.
 */
import { visit } from "unist-util-visit";

function getMeta(meta: string, key: string): string | null {
  if (!meta) return null;
  const match = meta.match(new RegExp(`${key}="([^"]*)"`));
  return match ? match[1] : null;
}

function escapeAttr(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function plugin() {
  return function transformer(ast: any) {
    const instances: any[] = [];
    visit(ast, { type: "code", lang: "p5" }, (node, index, parent) => {
      instances.push([node, index, parent]);
    });

    instances.forEach(([node, index, parent]) => {
      const code: string = node.value ?? "";
      const b64 = Buffer.from(code, "utf8").toString("base64");
      const title = getMeta(node.meta, "title");
      const desc = getMeta(node.meta, "desc");
      const heightRaw = getMeta(node.meta, "height");
      const height = heightRaw && /^\d+$/.test(heightRaw) ? heightRaw : "360";

      const caption = desc
        ? `<figcaption class="pch-viz__cap">${escapeAttr(desc)}</figcaption>`
        : "";

      const html = `
<figure class="pch-viz pch-p5" data-p5 data-height="${height}" data-p5-code="${b64}">
  <div class="pch-viz__bar">
    <span class="pch-viz__dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="pch-viz__tag">sketch</span>
    <span class="pch-viz__title">${title ? escapeAttr(title) : "p5 sketch"}</span>
    <span class="pch-viz__lib">p5.js</span>
    <span class="pch-viz__controls">
      <button type="button" class="pch-viz__btn" data-p5-toggle aria-label="Pause or play the sketch">
        <span class="pch-viz__btn-label">Pause</span>
      </button>
      <button type="button" class="pch-viz__btn" data-p5-restart aria-label="Restart the sketch">Restart</button>
    </span>
  </div>
  <div class="pch-p5__stage" data-p5-stage role="img" aria-label="Interactive p5.js sketch${title ? ": " + escapeAttr(title) : ""}"></div>
  ${caption}
</figure>`;

      parent.children.splice(index, 1, {
        type: "html",
        value: html,
        position: node.position,
      });
    });

    return ast;
  };
}

export default plugin;

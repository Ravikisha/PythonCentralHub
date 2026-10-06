/* viz-fullscreen.js
   ─────────────────
   Adds a "view fullscreen" button to every visualization surface so readers
   can blow them up into the shared macOS-style window (editor-fullscreen.js):

     • mermaid diagrams (.pch-viz.mermaid-diagram) → clone the rendered SVG
     • p5.js sketches   (.pch-viz.pch-p5)          → run a fresh instance with
                                                      its own Pause/Restart
                                                      controls + caption
     • fenced code blocks                          → clone the highlighted <pre>

   Python code blocks already get a fullscreen (expand) control from the
   interactive playground toolbar, so those are skipped here. No-ops on pages
   with none of these surfaces. */
import { openFullscreen } from "/scripts/editor-fullscreen.js";

const FS_ICON =
  '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">' +
  '<path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>';

function makeBtn(label, extraClass) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "pch-viz__btn pch-fs-btn" + (extraClass ? " " + extraClass : "");
  b.setAttribute("aria-label", label);
  b.title = label;
  b.innerHTML = FS_ICON;
  return b;
}

function captionOf(panel) {
  const cap = panel.querySelector(".pch-viz__cap");
  const t = cap && cap.textContent ? cap.textContent.trim() : "";
  return t || undefined;
}

// p5 sketch runner (mirrors public/scripts/p5-viz.js) so a fresh, correctly
// sized instance can be built in the overlay regardless of whether the inline
// sketch has lazily mounted yet.
const P5_HOOKS = [
  "preload", "setup", "draw",
  "mousePressed", "mouseReleased", "mouseClicked", "mouseMoved",
  "mouseDragged", "doubleClicked", "mouseWheel",
  "keyPressed", "keyReleased", "keyTyped",
  "touchStarted", "touchMoved", "touchEnded", "windowResized",
];
function decodeB64(b64) {
  try {
    return decodeURIComponent(
      Array.prototype.map
        .call(atob(b64), function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
  } catch (e) {
    try { return atob(b64); } catch (e2) { return ""; }
  }
}
function makeP5Factory(code) {
  let rebind = "";
  for (const n of P5_HOOKS) {
    rebind += 'if(typeof ' + n + '==="function"){p.' + n + "=" + n + ";}";
  }
  // eslint-disable-next-line no-new-func
  return new Function("p", "with(p){\n" + code + "\n}\n" + rebind);
}

// A control button matching the inline p5 toolbar (icon comes from CSS).
function ctlBtn(kind, label) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "pch-viz__btn";
  b.setAttribute(kind === "toggle" ? "data-p5-toggle" : "data-p5-restart", "");
  const l = document.createElement("span");
  l.className = "pch-viz__btn-label";
  l.textContent = label;
  b.appendChild(l);
  return b;
}

// ── .pch-viz panels: mermaid + p5 ────────────────────────────────────────────
function enhanceViz(panel) {
  if (panel.querySelector(".pch-fs-btn")) return;
  const bar = panel.querySelector(".pch-viz__bar");
  if (!bar) return;

  let controls = bar.querySelector(".pch-viz__controls");
  if (!controls) {
    controls = document.createElement("span");
    controls.className = "pch-viz__controls";
    bar.appendChild(controls);
  }
  const btn = makeBtn("View fullscreen");
  controls.appendChild(btn);

  const isP5 = panel.classList.contains("pch-p5");
  const titleEl = panel.querySelector(".pch-viz__title");
  const title = (titleEl && titleEl.textContent.trim()) || (isP5 ? "Sketch" : "Diagram");

  btn.addEventListener("click", function () {
    if (isP5) {
      const code = decodeB64(panel.getAttribute("data-p5-code") || "");
      let instance = null;
      let wrap = null;
      let running = true;

      function newInstance() {
        if (!window.p5 || !wrap) return;
        try { instance = new window.p5(makeP5Factory(code), wrap); }
        catch (e) {
          wrap.innerHTML = '<pre class="pch-p5__error">Sketch error: ' +
            String((e && e.message) || e).replace(/</g, "&lt;") + "</pre>";
        }
      }

      openFullscreen({
        title: title,
        trigger: btn,
        caption: captionOf(panel),
        buildContent: function (stage) {
          wrap = document.createElement("div");
          wrap.className = "pch-fs-stage pch-fs-stage--p5";
          stage.appendChild(wrap);
          if (window.p5) newInstance();
          else wrap.innerHTML = '<pre class="pch-p5__error">p5.js is still loading — try again.</pre>';
        },
        buildControls: function (slot) {
          const toggle = ctlBtn("toggle", "Pause");
          const label = toggle.querySelector(".pch-viz__btn-label");
          const restart = ctlBtn("restart", "Restart");

          toggle.addEventListener("click", function () {
            if (!instance) return;
            if (running) { instance.noLoop && instance.noLoop(); running = false; }
            else { instance.loop && instance.loop(); running = true; }
            toggle.classList.toggle("is-paused", !running);
            label.textContent = running ? "Pause" : "Play";
          });
          restart.addEventListener("click", function () {
            if (instance && instance.remove) { try { instance.remove(); } catch (e) {} }
            if (wrap) wrap.innerHTML = "";
            newInstance();
            running = true;
            toggle.classList.remove("is-paused");
            label.textContent = "Pause";
          });

          slot.append(toggle, restart);
        },
        onClose: function () {
          if (instance && instance.remove) { try { instance.remove(); } catch (e) {} }
          instance = null;
        },
      });
    } else {
      // mermaid (and any other .pch-viz): clone the rendered <svg>.
      const stageEl =
        panel.querySelector(".mermaid-diagram__stage") ||
        panel.querySelector(".pch-p5__stage") ||
        panel;
      const svg = stageEl.querySelector("svg");
      openFullscreen({
        title: title,
        trigger: btn,
        caption: captionOf(panel),
        buildContent: function (stage) {
          const wrap = document.createElement("div");
          wrap.className = "pch-fs-stage pch-fs-stage--diagram";
          if (svg) wrap.appendChild(svg.cloneNode(true));
          else if (stageEl) wrap.innerHTML = stageEl.innerHTML;
          stage.appendChild(wrap);
        },
      });
    }
  });
}

// ── Fenced code blocks (non-python; python uses the playground control) ───────
function enhanceCode(frag) {
  if (frag.querySelector(".pch-fs-btn")) return;
  const pre = frag.querySelector("pre");
  // Titled blocks carry rehype-pretty-code's caption; untitled ones carry the
  // header added by lib/rehype/code-chrome.ts. Requiring the caption meant a
  // plain fence had no way to be opened full screen.
  const title =
    frag.querySelector(":scope > [data-rehype-pretty-code-title]") ||
    frag.querySelector(":scope > .code__bar");
  if (!pre || !title) return;

  const lang = (pre.getAttribute("data-language") || "").toLowerCase();
  if (lang === "python") return; // playground toolbar already has expand
  if (title.querySelector(".py-playground__toolbar--in-title")) return;

  const btn = makeBtn("View code fullscreen", "pch-code-fs-btn");
  title.appendChild(btn);

  btn.addEventListener("click", function () {
    // The header also holds the copy button and this one, so take the label
    // from the language chip (or the filename) rather than the whole row --
    // the window was coming up titled "cmdCopy".
    const label = title.querySelector(".code__lang, [data-rehype-pretty-code-title]");
    const heading = (label ? label.textContent : title.childNodes[0]?.textContent) || "";

    openFullscreen({
      title: heading.trim() || lang || "Code",
      trigger: btn,
      buildContent: function (stage) {
        const wrap = document.createElement("div");
        wrap.className = "pch-fs-stage pch-fs-stage--code";
        wrap.appendChild(pre.cloneNode(true));
        stage.appendChild(wrap);
      },
    });
  });
}

function init() {
  const panels = document.querySelectorAll(".pch-viz");
  const frags = document.querySelectorAll("[data-rehype-pretty-code-fragment], [data-rehype-pretty-code-figure]");
  if (!panels.length && !frags.length) return;
  panels.forEach(enhanceViz);
  // Defer code blocks a tick so the Python playground can mount its own toolbar
  // first (its expand button covers python blocks; we handle the rest).
  setTimeout(function () {
    frags.forEach(enhanceCode);
  }, 0);
}

// Called again after each client-side navigation; enhanceViz and enhanceCode
// both return early on a panel that already carries a fullscreen button.
window.__pchVizFullscreen = { init: init };

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

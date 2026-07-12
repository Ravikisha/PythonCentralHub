/**
 * editor-fullscreen.js
 * ─────────────────────
 * A shared, macOS-style floating window used by:
 *   • Python playground (Monaco + Pyodide)
 *   • DataCamp Light exercise iframes
 *   • p5.js sketches, mermaid diagrams and code blocks (via viz-fullscreen.js)
 *
 * The window has real macOS "traffic-light" controls (close / minimize /
 * maximize), can be dragged by its title bar, and resized from its edges and
 * bottom-right corner.
 *
 * Usage:
 *   import { openFullscreen, closeFullscreen } from '/scripts/editor-fullscreen.js';
 *
 *   openFullscreen({
 *     title: 'Exercise 1',
 *     buildContent:  (bodyStage)   => { … mount your editor/canvas here … },
 *     buildControls: (controlSlot) => { … optional: header controls (right) … },
 *     caption:       'Optional note shown under the stage',   // string or Node
 *     onClose:       () => { … teardown … },
 *     trigger:       btnEl,   // focus returns here on close
 *   });
 */

const MODAL_ID = "editor-fullscreen-modal";
const MIN_W = 360;
const MIN_H = 220;

function ensureModal() {
  let modal = document.getElementById(MODAL_ID);
  if (modal) return modal;

  modal = document.createElement("div");
  modal.id = MODAL_ID;
  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-label", "Fullscreen window");
  modal.className = "ef-overlay";
  modal.hidden = true;

  const backdrop = document.createElement("div");
  backdrop.className = "ef-backdrop";
  backdrop.setAttribute("aria-hidden", "true");

  const panel = document.createElement("div");
  panel.className = "ef-panel";

  // ── Header (title bar) ──────────────────────────────────────────────────
  const header = document.createElement("div");
  header.className = "ef-header";

  // macOS traffic lights
  const traffic = document.createElement("div");
  traffic.className = "ef-traffic";
  function light(kind, label) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "ef-dot ef-dot--" + kind;
    b.setAttribute("aria-label", label);
    b.title = label;
    return b;
  }
  const closeDot = light("close", "Close");
  const minDot = light("min", "Minimize");
  const maxDot = light("max", "Maximize");
  traffic.append(closeDot, minDot, maxDot);

  const titleEl = document.createElement("span");
  titleEl.className = "ef-title";

  const controls = document.createElement("span");
  controls.className = "ef-controls";

  header.append(traffic, titleEl, controls);

  // ── Body ────────────────────────────────────────────────────────────────
  const body = document.createElement("div");
  body.className = "ef-body";

  // ── Resize grips ──────────────────────────────────────────────────────────
  const grips = document.createElement("div");
  grips.className = "ef-grips";
  ["e", "s", "se"].forEach(function (dir) {
    const g = document.createElement("div");
    g.className = "ef-grip ef-grip--" + dir;
    g.dataset.dir = dir;
    grips.appendChild(g);
  });

  panel.append(header, body, grips);
  modal.append(backdrop, panel);
  document.body.appendChild(modal);

  // ── Geometry helpers ──────────────────────────────────────────────────────
  let saved = null; // geometry saved before maximize

  function float() {
    // Detach from the overlay's flex-centering so we can position freely.
    if (panel.classList.contains("ef-floating")) return;
    const r = panel.getBoundingClientRect();
    panel.classList.add("ef-floating");
    panel.style.left = r.left + "px";
    panel.style.top = r.top + "px";
    panel.style.width = r.width + "px";
    panel.style.height = r.height + "px";
  }
  function clampIntoView() {
    const w = panel.offsetWidth, h = panel.offsetHeight;
    let left = parseFloat(panel.style.left) || 0;
    let top = parseFloat(panel.style.top) || 0;
    left = Math.max(8 - w + 120, Math.min(left, window.innerWidth - 120));
    top = Math.max(8, Math.min(top, window.innerHeight - 44));
    panel.style.left = left + "px";
    panel.style.top = top + "px";
  }

  // ── Drag (title bar) ──────────────────────────────────────────────────────
  let drag = null;
  header.addEventListener("pointerdown", function (e) {
    if (e.target.closest(".ef-traffic") || e.target.closest(".ef-controls")) return;
    if (panel.classList.contains("ef-max") || panel.classList.contains("ef-min")) return;
    float();
    drag = { px: e.clientX, py: e.clientY, left: parseFloat(panel.style.left), top: parseFloat(panel.style.top) };
    header.setPointerCapture(e.pointerId);
    panel.classList.add("ef-grabbing");
  });
  header.addEventListener("pointermove", function (e) {
    if (!drag) return;
    panel.style.left = drag.left + (e.clientX - drag.px) + "px";
    panel.style.top = drag.top + (e.clientY - drag.py) + "px";
  });
  function endDrag(e) {
    if (!drag) return;
    drag = null;
    panel.classList.remove("ef-grabbing");
    clampIntoView();
    try { header.releasePointerCapture(e.pointerId); } catch (_) {}
  }
  header.addEventListener("pointerup", endDrag);
  header.addEventListener("pointercancel", endDrag);

  // ── Resize (grips) ────────────────────────────────────────────────────────
  let rez = null; // resize state
  grips.addEventListener("pointerdown", function (e) {
    const grip = e.target.closest(".ef-grip");
    if (!grip || panel.classList.contains("ef-max") || panel.classList.contains("ef-min")) return;
    float();
    rez = {
      dir: grip.dataset.dir,
      px: e.clientX, py: e.clientY,
      w: panel.offsetWidth, h: panel.offsetHeight,
    };
    grip.setPointerCapture(e.pointerId);
    panel.classList.add("ef-resizing");
  });
  grips.addEventListener("pointermove", function (e) {
    if (!rez) return;
    const dx = e.clientX - rez.px, dy = e.clientY - rez.py;
    if (rez.dir.indexOf("e") !== -1) {
      panel.style.width = Math.max(MIN_W, Math.min(rez.w + dx, window.innerWidth - panel.offsetLeft - 8)) + "px";
    }
    if (rez.dir.indexOf("s") !== -1) {
      panel.style.height = Math.max(MIN_H, Math.min(rez.h + dy, window.innerHeight - panel.offsetTop - 8)) + "px";
    }
  });
  function endResize(e) {
    if (!rez) return;
    rez = null;
    panel.classList.remove("ef-resizing");
  }
  grips.addEventListener("pointerup", endResize);
  grips.addEventListener("pointercancel", endResize);

  // ── Window controls ───────────────────────────────────────────────────────
  function close() {
    const cb = modal._onClose;
    try { cb && cb(); } catch (e) { /* ignore */ }
    body.innerHTML = "";
    controls.innerHTML = "";
    modal._onClose = null;
    modal.hidden = true;
    document.body.style.overflow = "";
    // Reset window state + geometry for next open.
    panel.classList.remove("ef-floating", "ef-max", "ef-min", "ef-grabbing", "ef-resizing");
    panel.style.left = panel.style.top = panel.style.width = panel.style.height = "";
    saved = null;
    try { modal._trigger && modal._trigger.focus(); } catch (_) {}
    modal._trigger = null;
  }
  function toggleMin() {
    panel.classList.remove("ef-max");
    panel.classList.toggle("ef-min");
  }
  function toggleMax() {
    if (panel.classList.contains("ef-min")) panel.classList.remove("ef-min");
    if (panel.classList.contains("ef-max")) {
      panel.classList.remove("ef-max");
      if (saved) {
        panel.classList.add("ef-floating");
        panel.style.left = saved.left; panel.style.top = saved.top;
        panel.style.width = saved.width; panel.style.height = saved.height;
      }
      saved = null;
    } else {
      if (panel.classList.contains("ef-floating")) {
        saved = { left: panel.style.left, top: panel.style.top, width: panel.style.width, height: panel.style.height };
      }
      panel.classList.add("ef-max");
      panel.style.left = panel.style.top = panel.style.width = panel.style.height = "";
    }
  }
  closeDot.addEventListener("click", close);
  minDot.addEventListener("click", toggleMin);
  maxDot.addEventListener("click", toggleMax);
  backdrop.addEventListener("click", close);
  // Double-click the title bar to (un)maximize, like macOS.
  header.addEventListener("dblclick", function (e) {
    if (e.target.closest(".ef-traffic") || e.target.closest(".ef-controls")) return;
    toggleMax();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal.hidden) close();
  });

  modal._close = close;
  modal._body = body;
  modal._title = titleEl;
  modal._controls = controls;
  return modal;
}

/**
 * Open the fullscreen window.
 * @param {object} opts
 * @param {string}   opts.title
 * @param {function} opts.buildContent  – receives the body stage container.
 * @param {function} [opts.buildControls] – receives the header control slot.
 * @param {(string|Node)} [opts.caption] – note rendered under the stage.
 * @param {function} [opts.onClose]
 * @param {Element}  [opts.trigger]
 */
export function openFullscreen({ title = "", buildContent, buildControls, caption, onClose, trigger } = {}) {
  const modal = ensureModal();
  modal._body.innerHTML = "";
  modal._controls.innerHTML = "";
  modal._title.textContent = title;
  modal._onClose = onClose || null;
  modal._trigger = trigger || null;

  // Stage wrapper the caller mounts into.
  const stage = document.createElement("div");
  stage.className = "ef-stage";
  modal._body.appendChild(stage);

  try { buildContent && buildContent(stage); } catch (e) {
    console.error("[editor-fullscreen] buildContent threw:", e);
  }

  if (caption) {
    const cap = document.createElement("div");
    cap.className = "ef-caption";
    if (caption instanceof Node) cap.appendChild(caption);
    else cap.textContent = String(caption);
    modal._body.appendChild(cap);
  }

  if (buildControls) {
    try { buildControls(modal._controls); } catch (e) {
      console.error("[editor-fullscreen] buildControls threw:", e);
    }
  }

  modal.hidden = false;
  document.body.style.overflow = "hidden";
}

/** Close the modal programmatically. */
export function closeFullscreen() {
  const modal = document.getElementById(MODAL_ID);
  if (modal && !modal.hidden && modal._close) modal._close();
}

/** True if the modal is currently open. */
export function isFullscreen() {
  const modal = document.getElementById(MODAL_ID);
  return modal ? !modal.hidden : false;
}

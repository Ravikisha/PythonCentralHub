/**
 * editor-fullscreen.js
 * ─────────────────────
 * Shared fullscreen modal system used by:
 *   • Python playground (Monaco + Pyodide)
 *   • DataCamp Light exercise iframes
 *
 * Usage:
 *   import { openFullscreen, closeFullscreen } from '/scripts/editor-fullscreen.js';
 *
 *   openFullscreen({
 *     title: 'Exercise 1',           // shown in the modal header
 *     buildContent: (container) => { // mount your editor/iframe into container
 *       container.appendChild(myIframe);
 *     },
 *     onClose: () => {               // called when user closes modal
 *       myIframe.remove();
 *     }
 *   });
 */

const MODAL_ID = 'editor-fullscreen-modal';

// ── Build the modal DOM (once) ────────────────────────────────────────────────

function ensureModal() {
  let modal = document.getElementById(MODAL_ID);
  if (modal) return modal;

  // Overlay
  modal = document.createElement('div');
  modal.id = MODAL_ID;
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-label', 'Fullscreen editor');
  modal.className = 'ef-overlay';
  modal.hidden = true;

  // Backdrop (click to close)
  const backdrop = document.createElement('div');
  backdrop.className = 'ef-backdrop';
  backdrop.setAttribute('aria-hidden', 'true');

  // Panel
  const panel = document.createElement('div');
  panel.className = 'ef-panel';

  // Header
  const header = document.createElement('div');
  header.className = 'ef-header';

  const titleEl = document.createElement('span');
  titleEl.className = 'ef-title';

  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'ef-close-btn';
  closeBtn.setAttribute('aria-label', 'Close fullscreen editor');
  closeBtn.innerHTML = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41
        10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>`;

  header.appendChild(titleEl);
  header.appendChild(closeBtn);

  // Body — editors mount here
  const body = document.createElement('div');
  body.className = 'ef-body';

  panel.appendChild(header);
  panel.appendChild(body);
  modal.appendChild(backdrop);
  modal.appendChild(panel);
  document.body.appendChild(modal);

  // ── Close handlers ────────────────────────────────────────────────────────
  function close() {
    const cb = modal._onClose;
    // Run body teardown first so the caller can cleanly unmount the editor
    // before we wipe the DOM.
    try { cb && cb(); } catch (e) { /* ignore */ }
    body.innerHTML = '';
    modal._onClose = null;
    modal.hidden = true;
    document.body.style.overflow = '';
    // Restore focus to the trigger that opened the modal
    try { modal._trigger && modal._trigger.focus(); } catch {} 
    modal._trigger = null;
  }

  closeBtn.addEventListener('click', close);
  backdrop.addEventListener('click', close);

  // Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) close();
  });

  modal._close = close;
  modal._body  = body;
  modal._title = titleEl;

  return modal;
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Open the fullscreen modal.
 * @param {object} opts
 * @param {string}   opts.title        – Heading text in the modal header.
 * @param {function} opts.buildContent – Receives the body container; mount your UI.
 * @param {function} [opts.onClose]    – Called when the modal closes.
 * @param {Element}  [opts.trigger]    – Element to return focus to on close.
 */
export function openFullscreen({ title = '', buildContent, onClose, trigger } = {}) {
  const modal = ensureModal();
  // Wipe any previous content
  modal._body.innerHTML = '';
  modal._title.textContent = title;
  modal._onClose = onClose || null;
  modal._trigger = trigger || null;

  try { buildContent(modal._body); } catch (e) {
    console.error('[editor-fullscreen] buildContent threw:', e);
  }

  modal.hidden = false;
  document.body.style.overflow = 'hidden';
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

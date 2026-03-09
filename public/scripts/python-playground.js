// Python playground for fenced ```python code blocks.
// Uses Pyodide (Python + stdlib compiled to WebAssembly) entirely in-browser.
//
// How it works:
// - Finds code blocks rendered by rehype-pretty-code: <figure data-rehype-pretty-code-figure> ...
// - Filters language=python blocks.
// - Replaces the read-only code view with an editable textarea and adds Run/Copy/Reset.
// - Executes code inside a shared Pyodide instance and prints output.
//
// Notes:
// - This is intentionally vanilla JS (no build step) and is loaded globally.
// - Pyodide is lazy-loaded only if a python playground exists on the page.

(() => {
  const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.25.1/full/";

  /** @type {Promise<any> | null} */
  let pyodidePromise = null;

  // Small inline SVG icons (so we don't depend on any icon library being loaded).
  const ICONS = {
    play:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>',
    refresh:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 6V3L8 7l4 4V8c2.8 0 5 2.2 5 5a5 5 0 0 1-8.7 3.4l-1.4 1.4A7 7 0 0 0 19 13c0-3.9-3.1-7-7-7z"/></svg>',
    copy:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>',
    edit:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1.003 1.003 0 0 0 0-1.42L18.37 3.29a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.83z"/></svg>',
    eye:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/></svg>',
    terminal:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 5h16v14H4V5zm2 2v10h12V7H6zm1.2 1.9 3.6 3.1-3.6 3.1-1.2-1.4 2.5-2.1-2.5-2.1 1.2-1.6zM12 15h5v-2h-5v2z"/></svg>',
    expand:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>',
  };

  // ── Load fullscreen modal CSS once ──────────────────────────────────────────
  (function ensureFullscreenCSS() {
    const href = '/styles/editor-fullscreen.css';
    if (!document.querySelector(`link[href="${href}"]`)) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    }
  })();

  function isPythonBlock(block) {
    // In this repo, rehype-pretty-code renders a wrapper:
    // <div data-rehype-pretty-code-fragment>
    //   <div data-rehype-pretty-code-title data-language="python">...
    //   <pre ...><code>...</code></pre>
    // </div>
    const title = block.querySelector('div[data-rehype-pretty-code-title]');
    const lang = (title?.getAttribute('data-language') || '').toLowerCase();
    if (lang) return lang === 'python';

    // Fallback: sometimes language is on <pre data-language>
    const pre = block.querySelector('pre[data-language]');
    const preLang = (pre?.getAttribute('data-language') || '').toLowerCase();
    return preLang === 'python';
  }

  function isRunnableBlock(block) {
    // Default runnable.
    // Allow authors to opt-out per block by adding:
    //   - data-runnable="false" on the fragment, or
    //   - data-runnable="false" on the title, or
    //   - include "norun" in the title text (e.g. "print.py (norun)").
    const fragAttr = (block.getAttribute('data-runnable') || '').toLowerCase();
    if (fragAttr === 'false' || fragAttr === '0' || fragAttr === 'no') return false;

    const title = block.querySelector('div[data-rehype-pretty-code-title]');
    const titleAttr = (title?.getAttribute('data-runnable') || '').toLowerCase();
    if (titleAttr === 'false' || titleAttr === '0' || titleAttr === 'no') return false;

    const t = (title?.textContent || '').toLowerCase();
    if (t.includes('norun') || t.includes('no-run') || t.includes('no run')) return false;

    return true;
  }

  function getCodeFromBlock(block) {
    const pre = block.querySelector('pre');
    if (!pre) return '';

    // rehype-pretty-code wraps every token in <span> elements and sometimes
    // injects zero-width-space chars (\u200B) for copy behaviour. Using
    // `innerText` on the highlighted <pre> returns all those invisible chars
    // and produces garbage when loaded into the Monaco editor.
    //
    // Instead, walk every text node inside <code> and collect only real text,
    // stripping zero-width chars and keeping newlines from <br> or per-line
    // spans that rehype-pretty-code emits.
    const code = pre.querySelector('code');
    if (!code) {
      // Fallback: plain text, strip zero-width chars.
      return (pre.innerText || '')
        .replace(/\u200B/g, '')
        .replace(/\r\n/g, '\n')
        .trimEnd();
    }

    // rehype-pretty-code emits one [data-line] span per source line.
    const lineSpans = code.querySelectorAll('[data-line]');
    if (lineSpans.length > 0) {
      // Each [data-line] span holds the tokens for one line.
      const lines = Array.from(lineSpans).map((span) =>
        (span.textContent || '').replace(/\u200B/g, '')
      );
      return lines.join('\n').trimEnd();
    }

    // Generic fallback: collect text nodes, strip zero-width chars.
    const walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    let text = '';
    let node;
    while ((node = walker.nextNode())) {
      text += node.nodeValue || '';
    }
    return text.replace(/\u200B/g, '').replace(/\r\n/g, '\n').trimEnd();
  }

  function ensurePyodide() {
    if (pyodidePromise) return pyodidePromise;

    pyodidePromise = new Promise((resolve, reject) => {
      // Load pyodide loader
      const s = document.createElement('script');
      s.src = `${PYODIDE_URL}pyodide.js`;
      s.async = true;
      s.onload = async () => {
        try {
          // global loadPyodide provided by pyodide.js
          const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });

          // Capture stdout/stderr into JS
          pyodide.setStdout({ batched: (s) => window.__py_playground_stdout?.(s) });
          pyodide.setStderr({ batched: (s) => window.__py_playground_stderr?.(s) });

          resolve(pyodide);
        } catch (e) {
          reject(e);
        }
      };
      s.onerror = () => reject(new Error('Failed to load Pyodide'));
      document.head.appendChild(s);
    });

    return pyodidePromise;
  }

  async function ensurePackages(pyodide, packages, statusEl) {
    const pkgs = (packages || []).map((p) => String(p).trim()).filter(Boolean);
    if (!pkgs.length) return;
    try {
      setStatus(statusEl, `Loading packages: ${pkgs.join(', ')}…`, 'info');
      await pyodide.loadPackage(pkgs);
      setStatus(statusEl, 'Packages loaded', 'success');
    } catch (e) {
      // If a package doesn't exist in Pyodide, provide a friendly error.
      const msg = (e && e.message) ? e.message : String(e);
      setStatus(statusEl, `Package load failed: ${msg}`, 'error');
      throw e;
    }
  }

  function createUI(initialCode) {
    const root = document.createElement('div');
    root.className = 'py-playground';

  const toolbar = document.createElement('div');
  toolbar.className = 'py-playground__toolbar';

  const runBtn = document.createElement('button');
  runBtn.type = 'button';
  runBtn.className = 'py-playground__icon-btn py-playground__icon-btn--primary';
  runBtn.setAttribute('aria-label', 'Run');
  runBtn.innerHTML = ICONS.play;

  const resetBtn = document.createElement('button');
  resetBtn.type = 'button';
  resetBtn.className = 'py-playground__icon-btn';
  resetBtn.setAttribute('aria-label', 'Reset');
  resetBtn.innerHTML = ICONS.refresh;

  const copyBtn = document.createElement('button');
  copyBtn.type = 'button';
  copyBtn.className = 'py-playground__icon-btn';
  copyBtn.setAttribute('aria-label', 'Copy');
  copyBtn.innerHTML = ICONS.copy;

  const expandBtn = document.createElement('button');
  expandBtn.type = 'button';
  expandBtn.className = 'py-playground__icon-btn ef-expand-btn';
  expandBtn.setAttribute('aria-label', 'Open in fullscreen');
  expandBtn.title = 'Open in fullscreen';
  expandBtn.innerHTML = ICONS.expand;

  toolbar.appendChild(runBtn);
  toolbar.appendChild(resetBtn);
  toolbar.appendChild(copyBtn);
  toolbar.appendChild(expandBtn);

  // The editor (Monaco) will mount into this container.
  const editor = document.createElement('div');
  editor.className = 'py-playground__cm';
  editor.dataset.initialCode = initialCode;

  const outputWrap = document.createElement('div');
  outputWrap.className = 'py-playground__output-wrap';
  outputWrap.hidden = true;

    const outputLabel = document.createElement('div');
    outputLabel.className = 'py-playground__output-label';
    outputLabel.textContent = 'Output';

    const output = document.createElement('pre');
    output.className = 'py-playground__output';
    output.textContent = '';

    outputWrap.appendChild(outputLabel);
    outputWrap.appendChild(output);

    root.appendChild(toolbar);
    root.appendChild(editor);
    root.appendChild(outputWrap);

  return { root, toolbar, runBtn, resetBtn, copyBtn, expandBtn, status: null, editor, output, initialCode };
  }

  function setStatus(statusEl, text, kind = 'info') {
    // Keep status element for accessibility / fallback but surface messages via toast.
    try {
      if (window.toast && typeof window.toast.show === 'function' && text) {
        const title = kind === 'error' ? 'Error' : kind === 'success' ? 'Success' : '';
        window.toast.show({ title: title || '', description: text, variant: kind === 'error' ? 'error' : kind === 'success' ? 'success' : 'info' });
      }
    } catch (e) {
      // ignore
    }
    if (statusEl) {
      statusEl.textContent = text || '';
      statusEl.dataset.kind = kind;
    }
  }

  async function runPython(code, outputEl, statusEl) {
    outputEl.textContent = '';

    let stdout = '';
    let stderr = '';

    // One-run scoped hooks.
    window.__py_playground_stdout = (s) => { stdout += s; };
    window.__py_playground_stderr = (s) => { stderr += s; };

    try {
      setStatus(statusEl, 'Loading Python…', 'info');
      const pyodide = await ensurePyodide();

  // Optional package loading.
  const pkgList = outputEl.closest('.py-playground')?.dataset?.pyodidePackages;
  const packages = pkgList ? pkgList.split(',') : [];
  await ensurePackages(pyodide, packages, statusEl);

      setStatus(statusEl, 'Running…', 'info');
      // Use runPythonAsync to allow top-level await in the future if needed.
      await pyodide.runPythonAsync(code);

  // Preserve multiline output exactly as produced.
  // Normalize \r\n → \n and simulate \r (carriage-return) line-overwrite
  // behaviour so the output <pre> shows what a real terminal would show.
  const normalizeOutput = (s) => {
    // First collapse Windows-style \r\n into \n.
    let result = s.replace(/\r\n/g, '\n');
    // Then simulate bare \r: split on \r, each segment overwrites the
    // current line from the start (matching real terminal behaviour).
    if (result.includes('\r')) {
      const lines = result.split('\n');
      const processed = lines.map((line) => {
        const parts = line.split('\r');
        // Each \r resets to column 0; last part wins for overlapping chars.
        let out = '';
        for (const part of parts) {
          if (part.length >= out.length) {
            out = part;
          } else {
            out = part + out.slice(part.length);
          }
        }
        return out;
      });
      result = processed.join('\n');
    }
    return result;
  };

  const out = normalizeOutput(stdout || '');
  const err = normalizeOutput(stderr || '');

  // Show output only after a run attempt.
  const wrap = outputEl.closest('.py-playground__output-wrap');
  if (wrap) wrap.hidden = false;

      if (err) {
        outputEl.textContent = (out ? out : "") + (out && err ? "\n" : "") + err;
        setStatus(statusEl, 'Error', 'error');
      } else {
        // If program prints nothing, show a helpful placeholder.
        outputEl.textContent = out ? out : '(no output)';
        setStatus(statusEl, 'Done', 'success');
      }
    } catch (e) {
      const msg = (e && e.message) ? e.message : String(e);
      outputEl.textContent = msg;
  const wrap = outputEl.closest('.py-playground__output-wrap');
  if (wrap) wrap.hidden = false;
      setStatus(statusEl, 'Error', 'error');
    } finally {
      window.__py_playground_stdout = null;
      window.__py_playground_stderr = null;
    }
  }

  function upgradeBlock(block) {
    if (block.dataset.pyPlaygroundUpgraded === 'true') return;
    block.dataset.pyPlaygroundUpgraded = 'true';

  // Allow opting out on a per-block basis.
  if (!isRunnableBlock(block)) return;

    const code = getCodeFromBlock(block);

    const pre = block.querySelector('pre');
    if (!pre) return;

    // Determine packages to load from an optional attribute on the title.
    // Example (in HTML output):
    // <div data-rehype-pretty-code-title data-language="python" data-pyodide-packages="numpy,pandas">...
    const title = block.querySelector('div[data-rehype-pretty-code-title]');
    const packagesAttr = title?.getAttribute('data-pyodide-packages') || '';
    const packages = packagesAttr
      .split(',')
      .map((p) => p.trim())
      .filter(Boolean);

    // Keep original syntax highlighting: we don't remove <pre>, we hide it.
    // A toggle lets users switch between highlighted view and editable view.
    const ui = createUI(code);

  // Store packages on the root so runPython can pick them up.
  if (packages.length) ui.root.dataset.pyodidePackages = packages.join(',');

  const toggleBtn = document.createElement('button');
  toggleBtn.type = 'button';
  toggleBtn.className = 'py-playground__icon-btn';
  toggleBtn.setAttribute('aria-label', 'Edit');
  toggleBtn.style.marginTop = '1.5rem';
  toggleBtn.innerHTML = ICONS.edit;
  ui.toolbar.insertBefore(toggleBtn, ui.runBtn);

  // Start in "view" mode (highlighted); user clicks Edit to open the editor.
    ui.root.dataset.mode = 'view';
    // Hide the entire playground root — only the highlighted <pre> is shown at rest.
    // This prevents the empty Monaco container from rendering as a black box.
    ui.root.hidden = true;
    ui.editor.hidden = true;

    // Mount Monaco lazily when user enters edit mode.
    // cm is nulled when the user switches back to view (Monaco is destroyed).
    /** @type {any | null} */
    let cm = null;
    async function ensureEditor() {
      if (cm) return cm;
      const mod = await import('/scripts/python-playground-monaco.js');
      // Always get the latest code value — could differ from initialCode if
      // user edited, ran, then closed and re-opened.
      const currentCode = cm ? cm.getValue() : ui.initialCode;
      cm = await mod.createPythonEditor({
        parent: ui.editor,
        doc: currentCode,
        onCtrlEnterRun: () => ui.runBtn.click(),
      });
      return cm;
    }

    toggleBtn.addEventListener('click', () => {
      const isView = ui.root.dataset.mode === 'view';
      if (isView) {
        ui.root.dataset.mode = 'edit';
        toggleBtn.setAttribute('aria-label', 'View');
        toggleBtn.innerHTML = ICONS.eye;
        // Show the playground root (editor + output), hide the highlighted pre.
        ui.root.hidden = false;
        ui.editor.hidden = false;
        pre.hidden = true;
        ensureEditor().then((x) => {
          // Fire multiple layout passes after the container becomes visible.
          // A single rAF is not enough when the parent has a CSS transition or
          // when the Starlight sidebar shifts content width after paint.
          const doLayout = () => { try { x.layout?.(); } catch {} };
          requestAnimationFrame(() => {
            doLayout();
            setTimeout(doLayout, 50);
            setTimeout(doLayout, 200);
          });
          x.focus();
        });
      } else {
        ui.root.dataset.mode = 'view';
        toggleBtn.setAttribute('aria-label', 'Edit');
        toggleBtn.innerHTML = ICONS.edit;
        // Destroy and wipe Monaco so the container has zero DOM and zero height.
        if (cm) {
          try { cm.dispose?.(); } catch {}
          cm = null;
        }
        ui.editor.innerHTML = '';
        ui.editor.style.height = '';
        // Hide editor container, output, and the whole playground root.
        ui.editor.hidden = true;
        ui.output.textContent = '';
        const wrap = ui.output.closest('.py-playground__output-wrap');
        if (wrap) wrap.hidden = true;
        ui.root.hidden = true;
        // Restore the original highlighted code.
        pre.hidden = false;
      }
    });

    // Hook buttons
    ui.runBtn.addEventListener('click', async () => {
      const cmInstance = await ensureEditor().catch(() => null);
      const codeToRun = cmInstance ? cmInstance.getValue() : ui.initialCode;
      // Ensure the playground root is visible so output can be seen.
      // (User may click Run without ever opening the editor.)
      ui.root.hidden = false;
      runPython(codeToRun, ui.output, ui.status);
    });

    ui.resetBtn.addEventListener('click', () => {
      // Ensure the editor exists so Reset always restores the code, even if user never clicked Edit.
      ensureEditor().then((editor) => editor.setValue(ui.initialCode)).catch(() => {/* ignore */});
      ui.output.textContent = '';
      // Reset: hide the output panel and the whole playground root (back to view mode).
      const wrap = ui.output.closest('.py-playground__output-wrap');
      if (wrap) wrap.hidden = true;
      // Only collapse the root back if we're still in view mode (editor not open).
      if (ui.root.dataset.mode === 'view') {
        ui.root.hidden = true;
      }
      setStatus(ui.status, '', 'info');
    });

    ui.copyBtn.addEventListener('click', async () => {
      try {
        // If the editor is already open use its current content, otherwise
        // use the original code directly — no need to spin up Monaco just to copy.
        const cmInstance = cm;
        const text = cmInstance ? cmInstance.getValue() : ui.initialCode;
        await navigator.clipboard.writeText(text);
        setStatus(ui.status, 'Copied', 'success');
      } catch {
        setStatus(ui.status, 'Copy failed', 'error');
      }
    });

    // ── Fullscreen button ────────────────────────────────────────────────────
    ui.expandBtn.addEventListener('click', async () => {
      try {
        const mod = await import('/scripts/editor-fullscreen.js');

        // Get the exercise title from the nearest heading above the code block.
        let modalTitle = 'Python Playground';
        const figure = block;
        let sibling = figure && figure.previousElementSibling;
        while (sibling) {
          const tag = sibling.tagName && sibling.tagName.toLowerCase();
          if (tag === 'h2' || tag === 'h3' || tag === 'h4') {
            modalTitle = sibling.textContent.trim();
            break;
          }
          sibling = sibling.previousElementSibling;
        }

        // Current code value
        const currentCode = cm ? cm.getValue() : ui.initialCode;

        // We keep a reference to the Monaco instance created inside the modal.
        let modalCm = null;

        mod.openFullscreen({
          title: modalTitle,
          trigger: ui.expandBtn,
          buildContent(container) {
            // Clone the playground UI structure into the modal container.
            // We create a fresh Monaco editor inside the modal with the same code.
            const fsRoot = document.createElement('div');
            fsRoot.className = 'py-playground';
            fsRoot.style.height = '100%';

            // Toolbar row (Run + Reset + Copy) — no expand btn inside modal
            const fsTbar = document.createElement('div');
            fsTbar.className = 'py-playground__toolbar';

            const fsRunBtn = document.createElement('button');
            fsRunBtn.type = 'button';
            fsRunBtn.className = 'py-playground__icon-btn py-playground__icon-btn--primary';
            fsRunBtn.setAttribute('aria-label', 'Run');
            fsRunBtn.innerHTML = ICONS.play;

            const fsResetBtn = document.createElement('button');
            fsResetBtn.type = 'button';
            fsResetBtn.className = 'py-playground__icon-btn';
            fsResetBtn.setAttribute('aria-label', 'Reset');
            fsResetBtn.innerHTML = ICONS.refresh;

            const fsCopyBtn = document.createElement('button');
            fsCopyBtn.type = 'button';
            fsCopyBtn.className = 'py-playground__icon-btn';
            fsCopyBtn.setAttribute('aria-label', 'Copy');
            fsCopyBtn.innerHTML = ICONS.copy;

            fsTbar.appendChild(fsRunBtn);
            fsTbar.appendChild(fsResetBtn);
            fsTbar.appendChild(fsCopyBtn);

            const fsEditor = document.createElement('div');
            fsEditor.className = 'py-playground__cm';

            const fsOutWrap = document.createElement('div');
            fsOutWrap.className = 'py-playground__output-wrap';
            fsOutWrap.hidden = true;
            const fsOutLabel = document.createElement('div');
            fsOutLabel.className = 'py-playground__output-label';
            fsOutLabel.textContent = 'Output';
            const fsOut = document.createElement('pre');
            fsOut.className = 'py-playground__output';
            fsOutWrap.appendChild(fsOutLabel);
            fsOutWrap.appendChild(fsOut);

            fsRoot.appendChild(fsTbar);
            fsRoot.appendChild(fsEditor);
            fsRoot.appendChild(fsOutWrap);
            container.appendChild(fsRoot);

            // Create Monaco inside the modal editor div
            import('/scripts/python-playground-monaco.js').then((monacoMod) => {
              monacoMod.createPythonEditor({
                parent: fsEditor,
                doc: currentCode,
                onCtrlEnterRun: () => fsRunBtn.click(),
              }).then((editor) => {
                modalCm = editor;
                // Force layout after modal animation completes
                setTimeout(() => {
                  try { editor.layout?.(); } catch {}
                }, 250);
                editor.focus();
              });
            });

            // Run button
            fsRunBtn.addEventListener('click', async () => {
              const code = modalCm ? modalCm.getValue() : currentCode;
              fsOutWrap.hidden = false;
              runPython(code, fsOut, null);
            });

            // Reset button
            fsResetBtn.addEventListener('click', () => {
              if (modalCm) modalCm.setValue(ui.initialCode);
              fsOut.textContent = '';
              fsOutWrap.hidden = true;
            });

            // Copy button
            fsCopyBtn.addEventListener('click', async () => {
              try {
                const text = modalCm ? modalCm.getValue() : currentCode;
                await navigator.clipboard.writeText(text);
                setStatus(null, 'Copied', 'success');
              } catch {
                setStatus(null, 'Copy failed', 'error');
              }
            });
          },
          onClose() {
            // Sync code back to the inline editor when modal closes
            if (modalCm) {
              const latestCode = modalCm.getValue();
              // If inline editor is open, update it; otherwise update initialCode buffer
              if (cm) {
                try { cm.setValue(latestCode); } catch {}
              } else {
                ui.initialCode = latestCode;
                ui.editor.dataset.initialCode = latestCode;
              }
              try { modalCm.dispose?.(); } catch {}
              modalCm = null;
            }
          },
        });
      } catch (err) {
        console.error('[py-playground] Fullscreen failed:', err);
      }
    });

    // Place toolbar in the top-right of the code block title bar.
    if (title) {
      title.classList.add('py-playground__title');
      ui.toolbar.classList.add('py-playground__toolbar--in-title');
      title.appendChild(ui.toolbar);
    }

  // Insert the playground *after* the highlighted <pre>.
  // This preserves old highlighting and your existing copy/title UI.
  pre.insertAdjacentElement('afterend', ui.root);
  }

  function init() {
  const blocks = Array.from(document.querySelectorAll('div[data-rehype-pretty-code-fragment]'));
  const pythonBlocks = blocks.filter((b) => isPythonBlock(b) && isRunnableBlock(b));

  if (!pythonBlocks.length) return;

    // Lazy-load engine only if we need it.
    // (We load on first run too, but preloading reduces perceived latency.)
    ensurePyodide().catch(() => {/* ignore until run */});

  pythonBlocks.forEach(upgradeBlock);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

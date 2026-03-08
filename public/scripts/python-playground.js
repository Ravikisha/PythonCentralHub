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
  };

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
    return (pre.innerText || '').replace(/\r\n/g, '\n').trimEnd();
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

  toolbar.appendChild(runBtn);
  toolbar.appendChild(resetBtn);
  toolbar.appendChild(copyBtn);

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

  return { root, toolbar, runBtn, resetBtn, copyBtn, status: null, editor, output, initialCode };
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

  // Preserve multiline output exactly as produced, including trailing newlines.
  // (trimEnd() breaks some teaching examples that rely on blank lines.)
  const out = (stdout || '');
  const err = (stderr || '');

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
  toggleBtn.innerHTML = ICONS.edit;
  ui.toolbar.insertBefore(toggleBtn, ui.runBtn);

  // Start in "view" mode (highlighted); user clicks Edit to open the editor.
    ui.root.dataset.mode = 'view';
    ui.editor.hidden = true;

    // Mount Monaco lazily when user first enters edit mode.
    /** @type {any | null} */
    let cm = null;
    async function ensureEditor() {
      if (cm) return cm;
  const mod = await import('/scripts/python-playground-monaco.js');
      cm = mod.createPythonEditor({
        parent: ui.editor,
        doc: ui.initialCode,
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
        ui.editor.hidden = false;
  // Hide the original highlighted code.
  pre.hidden = true;
  ensureEditor().then((x) => x.focus());
      } else {
        ui.root.dataset.mode = 'view';
  toggleBtn.setAttribute('aria-label', 'Edit');
  toggleBtn.innerHTML = ICONS.edit;
        ui.editor.hidden = true;
        pre.hidden = false;
      }
    });

    // Hook buttons
    ui.runBtn.addEventListener('click', async () => {
  const cmInstance = await ensureEditor().catch(() => null);
      const codeToRun = cmInstance ? cmInstance.getValue() : ui.initialCode;
      runPython(codeToRun, ui.output, ui.status);
    });

    ui.resetBtn.addEventListener('click', () => {
  // Ensure the editor exists so Reset always restores the code, even if user never clicked Edit.
  ensureEditor().then((editor) => editor.setValue(ui.initialCode)).catch(() => {/* ignore */});
      ui.output.textContent = '';
  // Reset should also clear/hide the output panel.
  const wrap = ui.output.closest('.py-playground__output-wrap');
  if (wrap) wrap.hidden = true;
  setStatus(ui.status, '', 'info');
    });

    ui.copyBtn.addEventListener('click', async () => {
      try {
    const cmInstance = await ensureEditor().catch(() => null);
        const text = cmInstance ? cmInstance.getValue() : ui.initialCode;
        await navigator.clipboard.writeText(text);
        setStatus(ui.status, 'Copied', 'success');
      } catch {
        setStatus(ui.status, 'Copy failed', 'error');
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

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
  const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";
  // Package loads report progress ("Loading numpy", "Loaded numpy") through
  // the same stdout the output panel captures, so they printed into the
  // learner's results. Loading is shown on the Run button instead.
  const QUIET_LOAD = { messageCallback: () => {}, errorCallback: () => {} };

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
    const title = block.querySelector('[data-rehype-pretty-code-title]');
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

    const title = block.querySelector('[data-rehype-pretty-code-title]');
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
          // Pyodide 0.29 writes its own package-loader lines ("Loading numpy",
          // "Loaded numpy, pandas") to stdout from internal loads that take no
          // callback. They are not the learner's output, so they never reach
          // the panel.
          const LOADER_LINE = /^(Loading|Loaded) [\w.\-]+(, [\w.\-]+)*$/;
          pyodide.setStdout({
            batched: (s) => {
              if (LOADER_LINE.test(s.trim())) return;
              window.__py_playground_stdout?.(s);
            },
          });
          pyodide.setStderr({ batched: (s) => window.__py_playground_stderr?.(s) });

          resolve(pyodide);
        } catch (e) {
          reject(e);
        }
      };
      s.onerror = () => {
        s.remove();
        reject(new Error('Failed to load Pyodide'));
      };
      document.head.appendChild(s);
    });

    // A failed load is not cached. It used to be, so one blip on the CDN (or
    // an idle prewarm while offline) broke every Run button until a reload.
    const attempt = pyodidePromise;
    attempt.catch(() => {
      if (pyodidePromise === attempt) pyodidePromise = null;
    });

    return pyodidePromise;
  }

  // Share one runtime with any other component on the page that needs Python.
  // Pyodide is a ~10 MB download and a second `loadPyodide()` would build a
  // whole second interpreter, so MockInterview reuses this promise rather than
  // loading its own. Callers must capture stdout Python-side (redirect
  // `sys.stdout` to a StringIO) rather than touching the hooks set above,
  // which belong to the playground.
  window.__pchPyodide = ensurePyodide;

  async function ensurePackages(pyodide, packages, statusEl) {
    const pkgs = (packages || []).map((p) => String(p).trim()).filter(Boolean);
    if (!pkgs.length) return;
    try {
      setStatus(statusEl, `Loading packages: ${pkgs.join(', ')}…`, 'info');
      await pyodide.loadPackage(pkgs, QUIET_LOAD);
      setStatus(statusEl, 'Packages loaded', 'success');
    } catch (e) {
      // If a package doesn't exist in Pyodide, provide a friendly error.
      const msg = (e && e.message) ? e.message : String(e);
      setStatus(statusEl, `Package load failed: ${msg}`, 'error', { toast: true });
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
  // The one control on the bar a learner looks for, so it says what it does
  // rather than relying on a triangle. The others keep icons with tooltips.
  runBtn.className += ' py-playground__icon-btn--labelled';
  runBtn.title = 'Run this code';
  runBtn.innerHTML = ICONS.play + '<span>Run</span>';

  const resetBtn = document.createElement('button');
  resetBtn.type = 'button';
  resetBtn.className = 'py-playground__icon-btn';
  resetBtn.setAttribute('aria-label', 'Reset');
  resetBtn.title = 'Reset to the original code';
  resetBtn.innerHTML = ICONS.refresh;

  const copyBtn = document.createElement('button');
  copyBtn.type = 'button';
  copyBtn.className = 'py-playground__icon-btn';
  copyBtn.setAttribute('aria-label', 'Copy');
  copyBtn.title = 'Copy code';
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

    // The panel says what state it is in -- idle, running, finished, raised --
    // in words as well as colour, and offers the one action that belongs to
    // output: clearing it.
    const outputLabel = document.createElement('div');
    outputLabel.className = 'py-playground__output-label';

    const outputState = document.createElement('span');
    outputState.className = 'py-playground__state';
    outputState.textContent = 'Output';

    const clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'py-playground__clear';
    clearBtn.textContent = 'Clear';

    outputLabel.appendChild(outputState);
    outputLabel.appendChild(clearBtn);

    const output = document.createElement('pre');
    output.className = 'py-playground__output';
    output.textContent = '';

    outputWrap.appendChild(outputLabel);
    outputWrap.appendChild(output);

    root.appendChild(toolbar);
    root.appendChild(editor);
    root.appendChild(outputWrap);

  clearBtn.addEventListener('click', () => {
    output.textContent = '';
    outputWrap.hidden = true;
    outputWrap.dataset.state = 'idle';
  });

  return { root, toolbar, runBtn, resetBtn, copyBtn, expandBtn, status: null, editor, output, outputWrap, outputState, initialCode };
  }

  /**
   * Report progress.
   *
   * The run's own states -- starting, running, finished, raised -- are shown
   * in the output panel, beside the code they belong to. Toasting them as
   * well put three notifications in the corner for every click, describing
   * something the reader was already looking at. Only things that happen
   * away from the panel (a copy, a package failure) toast now.
   */
  function setStatus(statusEl, text, kind = 'info', { toast = false } = {}) {
    try {
      if (toast && window.toast && typeof window.toast.show === 'function' && text) {
        const title = kind === 'error' ? 'Error' : kind === 'success' ? 'Done' : '';
        window.toast.show({
          title: title || '',
          description: text,
          variant: kind === 'error' ? 'error' : kind === 'success' ? 'success' : 'info',
        });
      }
    } catch (e) {
      // ignore
    }
    if (statusEl) {
      statusEl.textContent = text || '';
      statusEl.dataset.kind = kind;
    }
  }

  /** Paint the output panel's state: the label, and the rail beside it. */
  function setPanel(outputEl, state, label) {
    const wrap = outputEl.closest('.py-playground__output-wrap');
    if (!wrap) return;
    wrap.dataset.state = state;
    const said = wrap.querySelector('.py-playground__state');
    if (said) said.textContent = label;
  }

  /**
   * Runs go one at a time. stdout and stderr reach JS through one pair of
   * global hooks, so two blocks running together -- Run on A while Python is
   * still loading, then Run on B -- wrote A's output into B, and A's cleanup
   * then cut B off mid-run. Queued, each run owns the hooks until it ends.
   */
  let runQueue = Promise.resolve();
  let inFlight = 0;

  function runPython(code, outputEl, statusEl) {
    if (inFlight > 0) setPanel(outputEl, 'running', 'Waiting for the other run…');
    inFlight += 1;
    const job = runQueue
      .then(() => runPythonNow(code, outputEl, statusEl))
      .finally(() => {
        inFlight -= 1;
      });
    runQueue = job.catch(() => {});
    return job;
  }

  async function runPythonNow(code, outputEl, statusEl) {
    outputEl.textContent = '';

    let stdout = '';
    let stderr = '';

    // One-run scoped hooks.
    window.__py_playground_stdout = (s) => { stdout += s; };
    window.__py_playground_stderr = (s) => { stderr += s; };

    try {
      setPanel(outputEl, 'running', 'Starting Python…');
      const wrapEarly = outputEl.closest('.py-playground__output-wrap');
      if (wrapEarly) wrapEarly.hidden = false;

      setStatus(statusEl, 'Loading Python…', 'info');
      const pyodide = await ensurePyodide();

  // Optional explicit package loading (via ```python packages="..." meta).
  const pkgList = outputEl.closest('.py-playground')?.dataset?.pyodidePackages;
  const packages = pkgList ? pkgList.split(',') : [];
  if (packages.length) {
    setPanel(outputEl, 'running', `Installing ${packages.join(', ')}…`);
  }
  await ensurePackages(pyodide, packages, statusEl);

  // Auto-load any Pyodide-provided packages the code imports (numpy,
  // matplotlib, pandas, scipy, scikit-learn as `sklearn`, …). This scans the
  // import statements and fetches matching wheels, so authors don't have to
  // declare them per block. Non-fatal: pure-stdlib code loads nothing.
  try {
    setStatus(statusEl, 'Loading libraries…', 'info');
    // numpy and pandas are tens of megabytes on a cold run; the panel says so
    // rather than sitting on "Starting Python…" for twenty seconds.
    if (/^\s*(import|from)\s+/m.test(code)) {
      setPanel(outputEl, 'running', 'Fetching libraries…');
    }
    await pyodide.loadPackagesFromImports(code, QUIET_LOAD);
  } catch (e) {
    // A missing/unknown import here isn't necessarily fatal — let the actual
    // run surface a precise error. Just note it.
    const msg = (e && e.message) ? e.message : String(e);
    setStatus(statusEl, `Some imports could not be preloaded: ${msg}`, 'info');
  }

      setPanel(outputEl, 'running', 'Running…');
      setStatus(statusEl, 'Running…', 'info');
      // runPythonAsync returns the value of the final expression, and allows
      // top-level await. The value is what makes a snippet that ends in
      // `fruits` or `df.head()` -- and there are hundreds of those -- print
      // something instead of "(no output)", the way a REPL would.
      const value = await pyodide.runPythonAsync(code);
      let echo = '';

      if (value !== undefined && value !== null) {
        try {
          // repr(), not str(): a string should come back quoted, so the
          // reader can tell '3' from 3.
          const pyRepr = pyodide.globals.get('repr');
          echo = pyRepr(value).toString();
          pyRepr.destroy();
        } catch {
          echo = String(value);
        }
      }

      // PyProxies hold a reference into the WASM heap until released.
      if (value && typeof value.destroy === 'function') value.destroy();

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
      } else if (out) {
        // Anything printed wins: the echo is a fallback, not an addition, or
        // a snippet that both prints and ends in an expression says it twice.
        outputEl.textContent = out;
        setPanel(outputEl, 'done', 'Output');
        setStatus(statusEl, 'Done', 'success');
      } else if (echo) {
        outputEl.textContent = echo;
        setPanel(outputEl, 'done', 'Value');
        setStatus(statusEl, 'Done', 'success');
      } else {
        // Ran, changed something, printed nothing -- an assignment or a
        // definition. Say that rather than looking broken.
        outputEl.textContent = 'Ran without printing anything.';
        setPanel(outputEl, 'done', 'Output');
        setStatus(statusEl, 'Done', 'success');
      }
    } catch (e) {
      const raw = (e && e.message) ? e.message : String(e);

      // Pyodide's traceback opens with its own frames -- eval_code_async in
      // _pyodide/_base.py -- before it reaches the reader's line. Those frames
      // are noise to someone learning Python, so the visible traceback starts
      // at their own code.
      const NEWLINE = String.fromCharCode(10);
      const lines = raw.split(NEWLINE);
      const mine = [];
      let skipping = false;
      for (const line of lines) {
        const isInternal = line.indexOf('_pyodide/_base.py') !== -1 || line.indexOf('_pyodide\_base.py') !== -1;
        if (isInternal) {
          skipping = true; // also drop the source line printed under it
          continue;
        }
        if (skipping && /^\s/.test(line) && !/^\s*File /.test(line)) continue;
        skipping = false;
        mine.push(line);
      }

      const msg = mine.join(NEWLINE).trim() || raw;
      outputEl.textContent = msg;
      setPanel(outputEl, 'error', 'Error');
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

    // rehype-pretty-code emits TWO <pre> (a light-theme and a dark-theme copy;
    // one is display:none per theme). Use the LAST one as the anchor so the
    // playground (editor + output) is inserted AFTER both — otherwise output
    // lands between the hidden light pre and the visible dark pre, i.e. ABOVE
    // the code. Hiding all of them on edit avoids a duplicate code block.
    const allPre = block.querySelectorAll('pre');
    const pre = allPre[allPre.length - 1];
    if (!pre) return;

    // Determine packages to load from an optional attribute on the title.
    // Example (in HTML output):
    // <div data-rehype-pretty-code-title data-language="python" data-pyodide-packages="numpy,pandas">...
    const title = block.querySelector('[data-rehype-pretty-code-title]');
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
  toggleBtn.title = 'Edit this code';
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
        allPre.forEach((p) => { p.hidden = true; });
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
        }).catch((err) => {
          // Silence here is how "Edit opens an empty box" went unnoticed: the
          // editor failed to mount and nothing said so.
          console.error('[py-playground] editor failed to mount:', err);
          if (window.toast) {
            window.toast.show({
              title: 'Editor unavailable',
              description: 'The code editor could not load. The snippet still runs as written.',
              variant: 'error',
            });
          }
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
        // Restore the original highlighted code (CSS shows the right theme copy).
        allPre.forEach((p) => { p.hidden = false; });
      }
    });

    // Hook buttons
    ui.runBtn.addEventListener('click', async () => {
      if (ui.runBtn.dataset.busy === 'true') return;

      const cmInstance = await ensureEditor().catch(() => null);
      const codeToRun = cmInstance ? cmInstance.getValue() : ui.initialCode;
      // Ensure the playground root is visible so output can be seen.
      // (User may click Run without ever opening the editor.)
      ui.root.hidden = false;

      // Pyodide takes ten to twenty seconds on a cold first run, and the
      // button gave no sign it had heard the click. It spins, and refuses a
      // second run until the first finishes.
      ui.runBtn.dataset.busy = 'true';
      ui.runBtn.disabled = true;
      try {
        await runPython(codeToRun, ui.output, ui.status);
      } finally {
        delete ui.runBtn.dataset.busy;
        ui.runBtn.disabled = false;
      }
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
        setStatus(ui.status, 'Copied', 'success', { toast: true });
      } catch {
        setStatus(ui.status, 'Copy failed', 'error', { toast: true });
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
            fsRunBtn.className = 'py-playground__icon-btn py-playground__icon-btn--primary py-playground__icon-btn--labelled';
            fsRunBtn.title = 'Run this code';
            fsRunBtn.innerHTML = ICONS.play + '<span>Run</span>';

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
                setStatus(null, 'Copied', 'success', { toast: true });
              } catch {
                setStatus(null, 'Copy failed', 'error', { toast: true });
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

    // Place the toolbar in the top-right of the code block's header.
    //
    // Titled blocks have rehype-pretty-code's <figcaption>; untitled ones have
    // the header this site adds in lib/rehype/code-chrome.ts. Only the first
    // was handled, so every fenced ```python block without a filename lost its
    // Run, Reset, Copy and fullscreen buttons.
    const bar = title || block.querySelector('.code__bar');
    if (bar) {
      bar.classList.add('py-playground__title');
      ui.toolbar.classList.add('py-playground__toolbar--in-title');

      // The header's own copy button would sit beside the toolbar's, doing the
      // same job on the same code.
      bar.querySelector('[data-copy]')?.remove();

      bar.appendChild(ui.toolbar);
    }

  // Insert the playground *after* the highlighted <pre>.
  // This preserves old highlighting and your existing copy/title UI.
  pre.insertAdjacentElement('afterend', ui.root);
  }

  function init() {
  const blocks = Array.from(document.querySelectorAll('[data-rehype-pretty-code-fragment], [data-rehype-pretty-code-figure]'));
  const pythonBlocks = blocks.filter((b) => isPythonBlock(b) && isRunnableBlock(b));

  if (!pythonBlocks.length) return;

    // Pre-warm the engine and the packages this page needs as soon as the
    // reader shows intent -- a pointer over, or focus on, a playground's
    // controls -- so the click that follows is near-instant.
    //
    // It used to run at idle on every page with a Python block. That fetched
    // and compiled Pyodide plus numpy/pandas (tens of MB) on the main thread
    // for every reader, including the many who never press Run: 10+ s of
    // blocked main thread on a mid-range phone, and the data plan to match.
    const prewarm = () => {
      ensurePyodide()
        .then(async (pyodide) => {
          // Collect every runnable block's code and preload the union of the
          // Pyodide-provided packages they import (numpy, pandas, sklearn, …).
          const allCode = pythonBlocks
            .map((b) => {
              try { return getCodeFromBlock(b); } catch { return ''; }
            })
            .join('\n');
          if (allCode.trim()) {
            try { await pyodide.loadPackagesFromImports(allCode, QUIET_LOAD); } catch {/* surfaced on run */}
          }
        })
        .catch(() => {/* ignore until run */});
    };
    let warmed = false;
    const onIntent = (event) => {
      if (warmed) return;
      const el = event.target;
      if (!(el instanceof Element) || !el.closest('.py-playground__toolbar, .py-playground')) return;
      warmed = true;
      document.removeEventListener('pointerover', onIntent, true);
      document.removeEventListener('focusin', onIntent, true);
      prewarm();
    };
    document.addEventListener('pointerover', onIntent, true);
    document.addEventListener('focusin', onIntent, true);

  pythonBlocks.forEach(upgradeBlock);
  }

  // Re-entrant: upgradeBlock marks each block it has taken over, so calling
  // this after a client-side navigation only picks up the new page's blocks.
  window.__pchPlayground = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

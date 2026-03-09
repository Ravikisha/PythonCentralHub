// Minimal, no-build Monaco Editor loader for the Python playground.
// Served from /public so it ships as-is.
//
// Contract:
// - export async function createPythonEditor({ parent, doc, onCtrlEnterRun })
// - returns an object with getValue(), setValue(text), focus().
//
// Notes:
// - Monaco is loaded from a CDN using AMD `require`.
// - This is a lazy loader; only loads when a user clicks Edit.

let _monacoLoaded = false;
let _monacoLoading = null;

function pickTheme() {
  // Starlight uses html[data-theme] = 'light' | 'dark'
  const t = (document.documentElement.getAttribute('data-theme') || '').toLowerCase();
  return t === 'light' ? 'vs' : 'vs-dark';
}

function loadStyle(href) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`link[rel="stylesheet"][href="${href}"]`);
    if (existing) return resolve();
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.onload = () => resolve();
    link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
    document.head.appendChild(link);
  });
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) return resolve();
    const s = document.createElement('script');
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(s);
  });
}

async function ensureMonaco() {
  if (_monacoLoaded) return;
  if (_monacoLoading) return _monacoLoading;

  _monacoLoading = (async () => {
    // Monaco loader (AMD). Using a pinned-ish version for stability.
    const base = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min';

    // Monaco requires its own CSS
    await loadStyle(`${base}/vs/editor/editor.main.min.css`);

    // Load AMD loader
    await loadScript(`${base}/vs/loader.min.js`);

    if (!window.require) throw new Error('Monaco loader failed to load (window.require missing)');

    // Configure where Monaco should load its modules from.
    window.require.config({ paths: { vs: `${base}/vs` } });

    await new Promise((resolve, reject) => {
      window.require(['vs/editor/editor.main'], () => resolve(), reject);
    });

    if (!window.monaco || !window.monaco.editor) throw new Error('Monaco failed to initialize');

    _monacoLoaded = true;
  })();

  return _monacoLoading;
}

export async function createPythonEditor({ parent, doc, onCtrlEnterRun }) {
  await ensureMonaco();

  // Defensive: clear parent
  parent.innerHTML = '';

  // Pre-calculate the correct height based on line count BEFORE creating the
  // editor. Monaco reads the container dimensions at construction time to build
  // its internal coordinate mapping. If the height is wrong at that moment,
  // clicks register on the wrong line (cursor misalignment).
  const lineCount = (doc ?? '').split('\n').length;
  const lineHeight = 20; // must match the lineHeight option below
  const padding = 18;
  const minLines = 8;
  const maxLines = 40;
  const initialLines = Math.min(maxLines, Math.max(minLines, lineCount));
  const initialHeight = initialLines * lineHeight + padding;
  parent.style.height = `${initialHeight}px`;

  const editor = window.monaco.editor.create(parent, {
    value: doc ?? '',
    language: 'python',
    theme: pickTheme(),
    // Use false + manual layout() calls so Monaco never fights the CSS container.
    automaticLayout: false,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    fontSize: 14,
    lineHeight: 20,
    tabSize: 4,
    fontLigatures: true,
  });

  // Ensure the editor only captures keystrokes when it is actually focused.
  // In some docs layouts, the editor can keep a hidden textarea focused even
  // after clicking elsewhere, causing typing to go "under the cursor".
  //
  // We aggressively blur the editor if a pointerdown happens outside it.
  // (Monaco's focus can be sticky due to internal hidden textareas.)
  const editorDomNode = editor.getDomNode?.();
  const onPointerDownCapture = (ev) => {
    if (!editorDomNode) return;
    const target = ev.target;
    if (!(target instanceof Node)) return;
    if (editorDomNode.contains(target)) return;
    try {
      // Remove focus from Monaco so normal page typing works.
      editor.blur?.();
      // Ensure any focused internal textarea releases focus.
      document.activeElement?.blur?.();
    } catch {
      // ignore
    }
  };
  document.addEventListener('pointerdown', onPointerDownCapture, true);

  // React to theme changes in Starlight.
  const themeObserver = new MutationObserver(() => {
    try {
      window.monaco.editor.setTheme(pickTheme());
    } catch {
      // ignore
    }
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });

  // Ctrl/Cmd + Enter to Run
  editor.addCommand(window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.Enter, () => {
    onCtrlEnterRun?.();
  });

  // Auto-height: resize the editor DOM to fit content.
  // Monaco wants explicit height; we adapt to content height.
  // Constants must match the pre-calculation above.
  const updateHeight = () => {
    const lc = editor.getModel()?.getLineCount?.() ?? 1;
    const lh = editor.getOption(window.monaco.editor.EditorOption.lineHeight);
    const lines = Math.min(maxLines, Math.max(minLines, lc));
    const height = lines * lh + padding;
    parent.style.height = `${height}px`;
    editor.layout({ width: parent.clientWidth, height });
  };

  // First layout after the editor is actually visible in the document.
  // Monaco's internal coordinate mapping (line → pixel) is only correct once
  // the container has its real painted size. We fire layout at 0ms, 50ms and
  // 200ms after creation so staggered CSS transitions / Starlight sidebar
  // animations don't leave the mapping stale and cause cursor misalignment.
  const forceLayout = () => {
    const w = parent.clientWidth;
    const h = parent.clientHeight || parseInt(parent.style.height, 10) || 176;
    if (w > 0) editor.layout({ width: w, height: h });
    updateHeight();
  };
  requestAnimationFrame(() => {
    forceLayout();
    setTimeout(forceLayout, 50);
    setTimeout(forceLayout, 200);
  });
  const disposable = editor.onDidContentSizeChange(() => updateHeight());

  // Since automaticLayout is off, watch the container for width changes
  // (e.g. sidebar open/close) and re-layout accordingly.
  let _resizeObserver = null;
  try {
    _resizeObserver = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        editor.layout({ width: parent.clientWidth, height: parent.clientHeight });
      });
    });
    _resizeObserver.observe(parent);
  } catch {
    // ResizeObserver not available — degraded gracefully.
  }

  // Adapter used by python-playground.js
  return {
    getValue: () => editor.getValue(),
    setValue: (t) => editor.setValue(t ?? ''),
    focus: () => editor.focus(),
    dispose: () => {
      try {
        themeObserver?.disconnect?.();
      } catch {}
      try {
        document.removeEventListener('pointerdown', onPointerDownCapture, true);
      } catch {}
      try {
        _resizeObserver?.disconnect?.();
      } catch {}
      try {
        disposable?.dispose?.();
      } catch {}
      try {
        editor?.dispose?.();
      } catch {}
    },
  };
}

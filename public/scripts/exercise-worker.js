/* Exercise runner: Python in a Web Worker, with pythonwhat-style grading.
 *
 * The exercises used to run on DataCamp Light, whose backend is Python 3.5.2
 * with numpy 1.11, pandas 0.19 and scikit-learn 0.18. 1,178 of the 2,900
 * exercises in the course (f-strings, np.random.default_rng, modern pandas)
 * could not run there at all: Submit answered "invalid syntax".
 *
 * This runs them on Pyodide instead -- the same Python the code blocks' Run
 * buttons use -- inside a worker, so an infinite loop in a learner's code
 * cannot freeze the page: the page stops the worker after a time limit and
 * starts a fresh one.
 *
 * Grading implements the two checker functions the course's `sct` props use
 * (a survey of all 2,900 found nothing else): test_output_contains and
 * success_msg, with pythonwhat's semantics -- `pattern=True` (the default)
 * means a regular-expression search, `pattern=False` a literal substring.
 *
 * Message in:  { id, pre, code, sct | null }
 * Message out: { id, stdout, error | null, grade | null } or { id, status }
 */
/* global importScripts, loadPyodide */
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";

/** Package-load progress stays out of the console the learner never sees. */
const QUIET_LOAD = { messageCallback: () => {}, errorCallback: () => {} };

let ready = null;

function boot() {
  if (ready) return ready;
  ready = (async () => {
    importScripts(PYODIDE_URL + "pyodide.js");
    const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
    await pyodide.runPythonAsync(HARNESS);
    return pyodide;
  })();
  ready.catch(() => {
    ready = null; // a failed boot is retried on the next message
  });
  return ready;
}

const HARNESS = String.raw`
import sys, io, re, traceback, builtins, os

os.environ.setdefault("MPLBACKEND", "Agg")

def _trim_tb(tb):
    # Drop the harness's own frames: the learner should see their line, not ours.
    keep = [l for l in tb.splitlines() if "<exec>" not in l and "_pch_run" not in l]
    return "\n".join(keep)

import ast, types, inspect, queue

# ---- asyncio ---------------------------------------------------------------
# Pyodide cannot block inside asyncio.run() without WebAssembly stack
# switching, which most browsers do not have. Module-level asyncio.run(x)
# becomes a top-level "await x", which the browser event loop can drive.
# Rewritten on the syntax tree, so asyncio.run inside a function is untouched.

class _AwaitAsyncioRun(ast.NodeTransformer):
    def __init__(self):
        self.depth = 0
        self.changed = False

    def _scope(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1
        return node

    visit_FunctionDef = visit_AsyncFunctionDef = visit_Lambda = visit_ClassDef = _scope

    def visit_Call(self, node):
        self.generic_visit(node)
        f = node.func
        is_run = (
            isinstance(f, ast.Attribute)
            and f.attr in ("run", "run_until_complete")
            and node.args
        )
        if self.depth == 0 and is_run:
            self.changed = True
            return ast.copy_location(ast.Await(value=node.args[0]), node)
        return node

def _compile(source, filename):
    tree = ast.parse(source, filename)
    fixer = _AwaitAsyncioRun()
    tree = ast.fix_missing_locations(fixer.visit(tree))
    flags = ast.PyCF_ALLOW_TOP_LEVEL_AWAIT if fixer.changed else 0
    return compile(tree, filename, "exec", flags=flags)

# ---- threads and processes -------------------------------------------------
# WebAssembly has no threads, so Thread.start(), executors and process pools
# fail outright. They run one after another instead: results are the same
# for most programs, interleaving is not. The output panel says so.

_CONCURRENCY = re.compile(r"\b(threading|concurrent\.futures|multiprocessing|ThreadPoolExecutor|ProcessPoolExecutor)\b")

def _sequential_concurrency():
    import threading
    if getattr(threading.Thread, "_pch_sequential", False):
        return
    def start(self):
        self._pch_alive = True
        try:
            self.run()
        finally:
            self._pch_alive = False
    threading.Thread.start = start
    threading.Thread.join = lambda self, timeout=None: None
    threading.Thread.is_alive = lambda self: getattr(self, "_pch_alive", False)
    threading.Thread._pch_sequential = True

    import concurrent.futures as cf
    class SequentialExecutor(cf.Executor):
        def __init__(self, *args, **kwargs):
            pass
        def submit(self, fn, /, *args, **kwargs):
            future = cf.Future()
            try:
                future.set_result(fn(*args, **kwargs))
            except BaseException as exc:
                future.set_exception(exc)
            return future
        def shutdown(self, wait=True, *, cancel_futures=False):
            pass
    cf.ThreadPoolExecutor = cf.ProcessPoolExecutor = SequentialExecutor

    # Pyodide's own multiprocessing cannot even be imported (no
    # _multiprocessing), so a sequential stand-in takes its name.
    if True:
        mp = types.ModuleType("multiprocessing")
        class Pool:
            def __init__(self, processes=None, *a, **k):
                pass
            def map(self, fn, it, chunksize=None):
                return list(map(fn, it))
            def starmap(self, fn, it, chunksize=None):
                return [fn(*args) for args in it]
            def imap(self, fn, it, chunksize=1):
                return map(fn, it)
            imap_unordered = imap
            def apply(self, fn, args=(), kwds={}):
                return fn(*args, **kwds)
            def apply_async(self, fn, args=(), kwds={}, callback=None):
                value = fn(*args, **kwds)
                if callback:
                    callback(value)
                result = types.SimpleNamespace(get=lambda timeout=None: value, ready=lambda: True, successful=lambda: True)
                return result
            def close(self):
                pass
            def join(self):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *exc):
                return False
        class Process(threading.Thread):
            pass
        mp.Pool = Pool
        mp.Process = Process
        mp.Queue = queue.Queue
        mp.JoinableQueue = queue.Queue
        mp.Lock = threading.Lock
        mp.RLock = threading.RLock
        mp.Event = threading.Event
        mp.cpu_count = lambda: 1
        mp.current_process = lambda: types.SimpleNamespace(name="MainProcess", pid=1)
        pool_mod = types.ModuleType("multiprocessing.pool")
        pool_mod.Pool = Pool
        pool_mod.ThreadPool = Pool
        mp.pool = pool_mod
        sys.modules["multiprocessing"] = mp
        sys.modules["multiprocessing.pool"] = pool_mod

_SEQUENTIAL_NOTE = "Threads and processes run one after another in this in-browser Python, so output that depends on their interleaving can differ from a normal computer."

async def _pch_run(pre, code, sct):
    out = io.StringIO()
    ns = {"__name__": "__main__"}
    real_stdout, real_stderr, real_input = sys.stdout, sys.stderr, builtins.input
    notice = None
    if _CONCURRENCY.search(pre + "\n" + code):
        _sequential_concurrency()
        notice = _SEQUENTIAL_NOTE

    def fake_input(prompt=""):
        # No keyboard in a worker. Echo the prompt, answer empty, like a
        # script given no input.
        out.write(str(prompt))
        out.write("\n")
        return ""

    error = None
    sys.stdout = sys.stderr = out
    builtins.input = fake_input
    try:
        try:
            import matplotlib
            matplotlib.use("Agg")
        except Exception:
            pass
        for source, name in ((pre, "<setup>"), (code, "script.py")):
            if not source:
                continue
            result = eval(_compile(source, name), ns)
            if inspect.isawaitable(result):
                await result
    except SystemExit:
        pass
    except BaseException:
        error = _trim_tb(traceback.format_exc())
    finally:
        sys.stdout, sys.stderr, builtins.input = real_stdout, real_stderr, real_input

    output = out.getvalue()
    grade = None
    if sct is not None:
        grade = _pch_grade(sct, output, error)
    return {"stdout": output, "error": error, "grade": grade, "notice": notice}

class _Fail(Exception):
    pass

# Regex syntax a check would use on purpose: escapes (\d, \s, \.), wildcards
# (.*, .+, .?), anchors, and counted repeats. Not "|": the course prints
# tables, P(A|B) and |x| constantly, and as alternation a pipe would let half
# of the expected line pass.
_LOOKS_LIKE_REGEX = re.compile(r"\\[dDsSwWbB.()\[\]{}+*?|^$]|\.[*+?]|^\^|\$$|\{\d+(,\d*)?\}")

def _pch_grade(sct, output, error):
    if error:
        last = error.strip().splitlines()[-1] if error.strip() else "an error"
        return {"passed": False, "message": "Your code stopped with an error (" + last + "). Fix it, then submit again."}

    state = {"success": None}

    def test_output_contains(text, pattern=True, no_output_msg=None):
        text = str(text)
        # Literal text always counts. With pattern=True (pythonwhat's default)
        # the text is also tried as a regex -- but only when it is written as
        # one. Most checks are plain text with regex characters in them:
        # "O(n log n)" can never match as a regex, and "[5, 0, 0, 2]" is a
        # character class that matches almost anything, so an unfinished
        # starter printing [None, None] "passed". Those are matched literally.
        found = text in output
        if pattern and not found and _LOOKS_LIKE_REGEX.search(text):
            try:
                found = re.search(text, output) is not None
            except re.error:
                pass
        if not found:
            raise _Fail(no_output_msg or ("Your output should contain \"" + text + "\". Check your code and run it again."))

    def success_msg(message):
        state["success"] = str(message)

    env = {"test_output_contains": test_output_contains, "success_msg": success_msg}
    try:
        exec(compile(sct, "<check>", "exec"), env)
    except _Fail as fail:
        return {"passed": False, "message": str(fail)}
    except Exception as exc:
        return {"passed": False, "message": "This exercise's check could not run (" + type(exc).__name__ + "). Your code may still be right."}
    return {"passed": True, "message": state["success"] or "Correct. Well done."}
`;

/**
 * Libraries Pyodide does not ship but the course uses, installed from PyPI on
 * first import. Pure-Python wheels only (micropip cannot build C extensions);
 * import name -> package name.
 */
const FROM_PYPI = {
  plotly: "plotly",
  seaborn: "seaborn",
  bs4: "beautifulsoup4",
  tabulate: "tabulate",
  faker: "faker",
  schedule: "schedule",
  dateutil: "python-dateutil",
  flask: "flask",
  flask_wtf: "flask-wtf",
  wtforms: "wtforms",
  werkzeug: "werkzeug",
  itsdangerous: "itsdangerous",
};

/**
 * Network from Python. Pyodide's urllib and requests cannot open sockets, so
 * seaborn.load_dataset() and pd.read_csv("https://...") failed with
 * "unknown url type: https". pyodide-http routes them through the worker's
 * synchronous XHR, which browsers allow in a worker.
 */
const NEEDS_NETWORK = /https?:\/\/|\bload_dataset\s*\(|\bimport\s+requests\b|\burllib\.request\b/;

async function enableNetwork(pyodide, source) {
  if (!NEEDS_NETWORK.test(source)) return;
  // Ships with Pyodide 0.29, so no PyPI round trip.
  await pyodide.loadPackage("pyodide-http", QUIET_LOAD);
  pyodide.runPython("import pyodide_http; pyodide_http.patch_all()");
}

async function installPurePython(pyodide, source) {
  const wanted = Object.keys(FROM_PYPI).filter((name) =>
    new RegExp(`^\\s*(import|from)\\s+${name}\\b`, "m").test(source),
  );
  if (!wanted.length) return;
  const missing = wanted.filter((name) => {
    try {
      pyodide.pyimport(name);
      return false;
    } catch {
      return true;
    }
  });
  if (!missing.length) return;
  await pyodide.loadPackage("micropip", QUIET_LOAD);
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(missing.map((name) => FROM_PYPI[name]));
}

self.onmessage = async (event) => {
  const { id, pre, code, sct } = event.data || {};
  try {
    self.postMessage({ id, status: "loading" });
    const pyodide = await boot();
    self.postMessage({ id, status: "packages" });
    // numpy, pandas, scikit-learn, scipy, matplotlib... fetched on first use.
    const source = [pre, code].filter(Boolean).join("\n");
    // Setup and learner code scanned separately: code with a syntax error
    // made the scan of the joined text find no imports at all.
    for (const piece of [pre, code]) {
      if (piece) await pyodide.loadPackagesFromImports(piece, QUIET_LOAD).catch(() => {});
    }
    await installPurePython(pyodide, source);
    await enableNetwork(pyodide, source).catch(() => {
      /* offline: the code will report its own network error */
    });
    self.postMessage({ id, status: "running" });
    const run = pyodide.globals.get("_pch_run");
    // _pch_run is async (top-level await for asyncio code), so each call is
    // awaited before its result is converted.
    const call = async () => {
      const proxy = await run(pre || "", code || "", sct == null ? null : sct);
      const value = proxy.toJs({ dict_converter: Object.fromEntries });
      proxy.destroy?.();
      return value;
    };
    let result = await call();
    // An import the scan above missed (inside a function, after a syntax the
    // scanner could not parse): load that one package and run once more.
    // Two wordings: plain Python's, and Pyodide's own for a package it ships
    // but has not loaded yet.
    const missing =
      /No module named '([\w.]+)'/.exec(result.error || "") ||
      /module '([\w.]+)' is included in the Pyodide distribution/.exec(result.error || "");
    if (missing) {
      const name = missing[1].split(".")[0];
      try {
        await pyodide.loadPackage(name === "sklearn" ? "scikit-learn" : name, QUIET_LOAD);
        result = await call();
      } catch {
        /* not a Pyodide package: keep the original error */
      }
    }
    run.destroy();
    self.postMessage({
      id,
      stdout: result.stdout ?? "",
      error: result.error ?? null,
      grade: result.grade ?? null,
      notice: result.notice ?? null,
    });
  } catch (err) {
    self.postMessage({
      id,
      stdout: "",
      error: "Python could not start: " + (err && err.message ? err.message : String(err)),
      grade: null,
    });
  }
};

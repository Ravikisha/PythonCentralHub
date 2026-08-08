/**
 * scripts/lint-p5.mjs — check every ```p5 sketch actually parses.
 *
 * WHY THIS EXISTS
 * ---------------
 * A p5 sketch is base64-encoded by lib/p5/remake.ts and eval'd in the browser by
 * public/scripts/p5-viz.js. Nothing on the build path ever parses it, so a syntax
 * error is invisible until a reader scrolls the panel into view and gets an empty
 * box plus a console error. With 300+ sketches across the site that is a silent
 * failure mode worth closing.
 *
 * What it checks, per sketch:
 *   1. It parses as JavaScript. The sketch is wrapped in `with (p) { … }` at
 *      runtime, so it is checked inside an equivalent wrapper here — which also
 *      means a sketch relying on strict-mode-only syntax will be caught.
 *   2. It defines setup(). Without it p5 has no canvas.
 *   3. Every function declared at top level is either a p5 lifecycle hook or is
 *      referenced from within the sketch — an unhooked, unreferenced function is
 *      almost always a misspelled hook (drawFrame instead of draw).
 *   4. setup() actually RUNS against a p5 stand-in without throwing. Parsing only
 *      proves syntax; a sketch that dies on its first frame looks identical to the
 *      reader. See the STUB comment for what this does and does not catch.
 *   5. The fence carries a title, so the panel is not labelled "p5 sketch".
 * Note on backticks: they are FINE inside a sketch. Many existing sketches use JS
 * template literals, and only a line *starting* with three backticks closes a fenced
 * block — a lone backtick does not. An earlier version of this script flagged all of
 * them and was wrong.
 *
 * Run: npm run dsa:p5   (also part of `npm run dsa`)
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import vm from "node:vm";

const ROOT = process.argv[2] ?? "src/content/docs";

/** p5 lifecycle hooks — the runtime re-binds exactly these onto the instance. */
const HOOKS = new Set([
  "preload", "setup", "draw",
  "mousePressed", "mouseReleased", "mouseClicked", "mouseMoved",
  "mouseDragged", "doubleClicked", "mouseWheel",
  "keyPressed", "keyReleased", "keyTyped",
  "touchStarted", "touchMoved", "touchEnded",
  "windowResized",
]);

/**
 * A stand-in p5 instance. Drawing calls are no-ops; the maths helpers return real
 * values so arithmetic in setup() behaves. `has` deliberately defers to the global
 * scope for names a real p5 instance does not own — claiming Math, JSON and friends
 * would make them resolve to no-ops and break sketches the browser runs fine.
 */
const STUB = `
  (function () {
    const real = {
      createCanvas: () => ({ elt: {}, canvas: {} }), textFont: () => {}, millis: () => 0,
      width: 600, height: 400, frameCount: 0, mouseX: 10, mouseY: 10, PI: Math.PI,
      LEFT: "LEFT", RIGHT: "RIGHT", CENTER: "CENTER", TOP: "TOP", BOTTOM: "BOTTOM",
      BASELINE: "BASELINE", CLOSE: "CLOSE", RADIUS: "RADIUS", CORNER: "CORNER",
      color: () => ({ levels: [0, 0, 0, 255], toString: () => "#000" }),
      random: (a, b) => (Array.isArray(a) ? a[0] : b === undefined ? (a === undefined ? 0.5 : a * 0.5) : a),
      createVector: (x = 0, y = 0) => ({ x, y, add() { return this }, mult() { return this }, copy() { return this } }),
      drawingContext: { setLineDash: () => {}, createLinearGradient: () => ({ addColorStop: () => {} }) },
      map: (v, a, b, c, d) => c + ((v - a) / ((b - a) || 1)) * (d - c),
      constrain: (v, lo, hi) => Math.min(hi, Math.max(lo, v)),
      dist: (x1, y1, x2, y2) => Math.hypot(x2 - x1, y2 - y1),
      lerp: (a, b, t) => a + (b - a) * t,
      radians: (d) => (d * Math.PI) / 180, degrees: (r) => (r * 180) / Math.PI,
      sin: Math.sin, cos: Math.cos, atan2: Math.atan2, abs: Math.abs,
      min: Math.min, max: Math.max, floor: Math.floor, ceil: Math.ceil, round: Math.round,
      sqrt: Math.sqrt, pow: Math.pow, log: Math.log, exp: Math.exp,
      noise: () => 0.5, textWidth: () => 10, select: () => null,
    };
    return new Proxy(real, {
      has: (t, k) => k in t || !(k in globalThis),
      get: (t, k) => (k in t ? t[k] : () => {}),
    });
  })()
`;

const SANDBOX_GLOBALS = {
  Math, JSON, Number, String, Array, Object, Boolean, Date: undefined,
  isFinite, isNaN, parseInt, parseFloat, Infinity, NaN,
  console: { log() {}, warn() {}, error() {} },
};

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".mdx")) out.push(full);
  }
  return out;
}

const problems = [];
let sketches = 0;
let files = 0;

for (const file of walk(ROOT)) {
  const text = readFileSync(file, "utf8");
  if (!text.includes("```p5")) continue;
  files += 1;
  const rel = relative(process.cwd(), file);

  // Every ```p5 … ``` block, with the line it starts on for a clickable report.
  const re = /^```p5([^\n]*)\n([\s\S]*?)^```/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    sketches += 1;
    const meta = m[1];
    const code = m[2];
    const line = text.slice(0, m.index).split("\n").length;
    const where = `${rel}:${line}`;

    // 1. does it parse? Wrap exactly as the runtime does.
    try {
      new vm.Script(`(function(p){ with(p){ ${code}\n } })`);
    } catch (err) {
      problems.push(`${where} — does not parse: ${String(err.message).split("\n")[0]}`);
      continue; // the checks below would be noise
    }

    // 2. setup() is mandatory.
    if (!/function\s+setup\s*\(/.test(code)) {
      problems.push(`${where} — no setup(): p5 will never create a canvas`);
    }

    // 3. Top-level functions must be a p5 hook, or referenced somewhere.
    //
    // "Referenced", not "called": sketches legitimately pass helpers around as
    // values — `{ fn: relu, label: "ReLU" }` — so counting only `name(` reports
    // six false positives on the existing corpus. Count every mention of the
    // identifier instead, and subtract the declaration itself.
    const declared = [...code.matchAll(/^function\s+(\w+)\s*\(/gm)].map((x) => x[1]);
    for (const name of declared) {
      if (HOOKS.has(name)) continue;
      const mentions = (code.match(new RegExp(`\\b${name}\\b`, "g")) ?? []).length;
      if (mentions <= 1) {
        problems.push(
          `${where} — function ${name}() is not a p5 hook and is never referenced. ` +
            `The runtime only re-binds the hooks in HOOKS, so this never runs ` +
            `(misspelled hook?)`,
        );
      }
    }

    // 4. actually RUN setup() against a p5 stand-in. Parsing only proves the
    //    syntax; this catches a sketch that throws on its very first frame, which
    //    renders exactly the same empty panel. Verified against the whole corpus
    //    at 0 false positives, and self-tested to catch null-property access, bad
    //    method calls and infinite loops.
    //
    //    KNOWN LIMITATION: it does not catch undefined identifiers. The stub
    //    answers for every name it is asked about, so a stray `total += 1`
    //    quietly yields NaN here where a real browser would throw a
    //    ReferenceError. Closing that needs a real p5 API allowlist.
    try {
      vm.runInNewContext(
        `(function(p){ with(p){ ${code}\n; if (typeof setup === "function") setup(); } })(${STUB})`,
        SANDBOX_GLOBALS,
        { timeout: 3000 },
      );
    } catch (err) {
      problems.push(`${where} — setup() throws: ${String(err.message).split("\n")[0]}`);
    }

    // 5. a title is worth having: the panel falls back to "p5 sketch" otherwise.
    if (!/title="/.test(meta)) {
      problems.push(`${where} — no title="…" on the fence; the panel will read "p5 sketch"`);
    }
  }
}

const bar = "─".repeat(72);
console.log(bar);
console.log(`p5 lint — ${sketches} sketches across ${files} pages under ${ROOT}`);
console.log(bar);

if (problems.length === 0) {
  console.log("\nOK — every sketch parses, defines setup(), and has a title.\n");
  process.exit(0);
}

console.log(`\n${problems.length} problem(s):`);
for (const p of problems) console.log(`  · ${p}`);
console.log("\nA broken sketch renders as an empty panel — nothing on the build path catches it.\n");
process.exit(1);

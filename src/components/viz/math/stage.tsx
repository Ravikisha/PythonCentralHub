/**
 * stage.tsx — the SVG primitives the maths stages share.
 *
 * Every lab in this directory draws in a coordinate system: a plane with axes, a
 * grid, arrows for vectors, contours for a surface. Writing that four times over
 * would be four subtly different sets of tick spacing and four arrowheads that
 * do not match. It lives here once.
 *
 * Everything is a pure function or a stateless component. No hooks, no refs, no
 * measurement — the stage renderers these feed are called with one frame and
 * must return the same markup on the server and after hydration.
 *
 * Colours come from `math-viz.css` classes wherever a class will do. Where a
 * colour has to be inline (an arrow that changes meaning per frame), it comes
 * from `TONE` below, which mirrors the `Tone` union in `frames.ts` so a stage can
 * map a frame's tone straight onto a stroke.
 */
import type { ReactNode } from "react";

/** Mirrors the `Tone` union in frames.ts. Kept in sync by hand; it is six lines. */
export const TONE = {
  active: "#ffd343",
  good: "#7ee787",
  bad: "#ff9d9d",
  warn: "#ffab70",
  muted: "#768390",
  info: "#6ba9dd",
} as const;

export type ToneName = keyof typeof TONE;

/* -------------------------------------------------------------------------- */
/* Coordinate mapping                                                          */
/* -------------------------------------------------------------------------- */

export interface Viewport {
  /** Data-space bounds: `[xMin, xMax, yMin, yMax]`. */
  domain: [number, number, number, number];
  /** Pixel size of the drawing area, padding included. */
  width: number;
  height: number;
  pad: { top: number; right: number; bottom: number; left: number };
}

export interface Scale {
  /** Data x to pixel x. */
  sx: (x: number) => number;
  /** Data y to pixel y. Flipped, because SVG y grows downwards. */
  sy: (y: number) => number;
  /** Pixel length of one data unit, per axis. */
  ux: number;
  uy: number;
  /** Inner plot rectangle in pixels. */
  box: { x: number; y: number; w: number; h: number };
  vp: Viewport;
}

export function scale(vp: Viewport): Scale {
  const [x0, x1, y0, y1] = vp.domain;
  const box = {
    x: vp.pad.left,
    y: vp.pad.top,
    w: vp.width - vp.pad.left - vp.pad.right,
    h: vp.height - vp.pad.top - vp.pad.bottom,
  };
  const ux = box.w / (x1 - x0);
  const uy = box.h / (y1 - y0);
  return {
    sx: (x) => box.x + (x - x0) * ux,
    sy: (y) => box.y + box.h - (y - y0) * uy,
    ux,
    uy,
    box,
    vp,
  };
}

/** Standard viewport: 600 wide, caller picks the height and the data bounds. */
export function viewport(
  domain: [number, number, number, number],
  height = 320,
  width = 600,
  pad = { top: 14, right: 18, bottom: 30, left: 40 },
): Viewport {
  return { domain, width, height, pad };
}

/** "Nice" tick positions: 1, 2 or 5 times a power of ten, about `target` of them. */
export function ticks(min: number, max: number, target = 6): number[] {
  const span = max - min;
  if (!(span > 0)) return [min];
  const raw = span / target;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const norm = raw / mag;
  const stepUnit = norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10;
  const step = stepUnit * mag;
  const first = Math.ceil(min / step) * step;
  const out: number[] = [];
  for (let v = first; v <= max + step / 1e6; v += step) {
    // Snap away float dust so a tick reads "0" and not "-1.1e-16".
    out.push(Math.abs(v) < step / 1e6 ? 0 : Number(v.toPrecision(12)));
  }
  return out;
}

const tickLabel = (v: number) => {
  const a = Math.abs(v);
  if (a === 0) return "0";
  if (a < 1e-3 || a >= 1e5) return v.toExponential(0);
  return String(Number(v.toPrecision(3)));
};

/* -------------------------------------------------------------------------- */
/* Axes                                                                        */
/* -------------------------------------------------------------------------- */

export function Axes({
  s,
  xLabel,
  yLabel,
  grid = true,
  origin = true,
}: {
  s: Scale;
  xLabel?: string;
  yLabel?: string;
  /** Draw the faint interior gridlines. */
  grid?: boolean;
  /** Draw heavier lines through x = 0 and y = 0 when they are in range. */
  origin?: boolean;
}) {
  const [x0, x1, y0, y1] = s.vp.domain;
  const xt = ticks(x0, x1);
  const yt = ticks(y0, y1);
  const { box } = s;

  return (
    <g>
      {grid &&
        xt.map((x) => (
          <line
            key={`gx${x}`}
            className="pch-mz__gridline"
            x1={s.sx(x)}
            y1={box.y}
            x2={s.sx(x)}
            y2={box.y + box.h}
          />
        ))}
      {grid &&
        yt.map((y) => (
          <line
            key={`gy${y}`}
            className="pch-mz__gridline"
            x1={box.x}
            y1={s.sy(y)}
            x2={box.x + box.w}
            y2={s.sy(y)}
          />
        ))}

      {origin && x0 < 0 && x1 > 0 && (
        <line className="pch-mz__axis" x1={s.sx(0)} y1={box.y} x2={s.sx(0)} y2={box.y + box.h} />
      )}
      {origin && y0 < 0 && y1 > 0 && (
        <line className="pch-mz__axis" x1={box.x} y1={s.sy(0)} x2={box.x + box.w} y2={s.sy(0)} />
      )}

      <line
        className="pch-mz__axis"
        x1={box.x}
        y1={box.y + box.h}
        x2={box.x + box.w}
        y2={box.y + box.h}
      />
      <line className="pch-mz__axis" x1={box.x} y1={box.y} x2={box.x} y2={box.y + box.h} />

      {xt.map((x) => (
        <text
          key={`tx${x}`}
          className="pch-mz__tick"
          x={s.sx(x)}
          y={box.y + box.h + 13}
          textAnchor="middle"
        >
          {tickLabel(x)}
        </text>
      ))}
      {yt.map((y) => (
        <text
          key={`ty${y}`}
          className="pch-mz__tick"
          x={box.x - 6}
          y={s.sy(y) + 3}
          textAnchor="end"
        >
          {tickLabel(y)}
        </text>
      ))}

      {xLabel && (
        <text
          className="pch-mz__label"
          x={box.x + box.w}
          y={box.y + box.h + 25}
          textAnchor="end"
        >
          {xLabel}
        </text>
      )}
      {yLabel && (
        <text className="pch-mz__label" x={box.x} y={box.y - 3} textAnchor="start">
          {yLabel}
        </text>
      )}
    </g>
  );
}

/* -------------------------------------------------------------------------- */
/* Arrows                                                                      */
/* -------------------------------------------------------------------------- */

/**
 * A vector arrow in pixel space, head included.
 *
 * The head is a drawn triangle rather than an SVG `marker`, because a marker
 * inherits the line's stroke width and these arrows vary theirs; sizing the head
 * independently is worth the four lines of trigonometry.
 */
export function Arrow({
  x1,
  y1,
  x2,
  y2,
  color,
  width = 2.2,
  head = 8,
  dashed = false,
  opacity = 1,
}: {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  width?: number;
  head?: number;
  dashed?: boolean;
  opacity?: number;
}) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy);
  if (len < 0.5) return null;

  const ux = dx / len;
  const uy = dy / len;
  // Stop the shaft short so the stroke does not poke through the head.
  const bx = x2 - ux * head * 0.85;
  const by = y2 - uy * head * 0.85;
  const px = -uy;
  const py = ux;

  return (
    <g opacity={opacity}>
      <line
        x1={x1}
        y1={y1}
        x2={bx}
        y2={by}
        stroke={color}
        strokeWidth={width}
        strokeDasharray={dashed ? "5 4" : undefined}
        strokeLinecap="round"
      />
      <polygon
        points={[
          `${x2},${y2}`,
          `${bx + px * head * 0.42},${by + py * head * 0.42}`,
          `${bx - px * head * 0.42},${by - py * head * 0.42}`,
        ].join(" ")}
        fill={color}
      />
    </g>
  );
}

/** A labelled dot. Used for iterates, data points, marked optima. */
export function Dot({
  cx,
  cy,
  r = 4,
  color,
  label,
  labelDx = 7,
  labelDy = -7,
}: {
  cx: number;
  cy: number;
  r?: number;
  color: string;
  label?: string;
  labelDx?: number;
  labelDy?: number;
}) {
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={color} />
      {label && (
        <text className="pch-mz__label" x={cx + labelDx} y={cy + labelDy} fill={color}>
          {label}
        </text>
      )}
    </g>
  );
}

/* -------------------------------------------------------------------------- */
/* Polylines and contours                                                      */
/* -------------------------------------------------------------------------- */

/** `d` attribute for a polyline through data-space points. */
export function pathOf(pts: [number, number][], s: Scale): string {
  if (pts.length === 0) return "";
  return pts.map((p, i) => `${i === 0 ? "M" : "L"}${s.sx(p[0])},${s.sy(p[1])}`).join(" ");
}

/** `d` attribute for a curve given as parallel xs / ys arrays. */
export function curveOf(xs: number[], ys: number[], s: Scale): string {
  const n = Math.min(xs.length, ys.length);
  let d = "";
  for (let i = 0; i < n; i++) {
    if (!Number.isFinite(ys[i])) continue;
    d += `${d === "" ? "M" : "L"}${s.sx(xs[i])},${s.sy(ys[i])} `;
  }
  return d.trim();
}

/**
 * Marching squares: one contour of a scalar field, as a set of SVG line
 * segments.
 *
 * Returned as segments rather than joined paths on purpose. Joining them
 * correctly means tracing loops and handling saddle-cell ambiguity, which buys
 * nothing here — the segments are drawn with `stroke-linecap: round` and read as
 * a continuous curve at any size a page uses. A closed-loop tracer would be 150
 * lines to fix a problem the reader cannot see.
 */
export function contourSegments(
  xs: number[],
  ys: number[],
  z: number[][],
  level: number,
): [number, number, number, number][] {
  const segs: [number, number, number, number][] = [];
  const interp = (a: number, b: number, va: number, vb: number) =>
    a + ((level - va) * (b - a)) / (vb - va || 1e-12);

  for (let j = 0; j < ys.length - 1; j++) {
    for (let i = 0; i < xs.length - 1; i++) {
      const v00 = z[j][i];
      const v10 = z[j][i + 1];
      const v01 = z[j + 1][i];
      const v11 = z[j + 1][i + 1];
      if (![v00, v10, v01, v11].every(Number.isFinite)) continue;

      // Crossings on each of the cell's four edges, if any.
      const pts: [number, number][] = [];
      if (v00 < level !== v10 < level) pts.push([interp(xs[i], xs[i + 1], v00, v10), ys[j]]);
      if (v10 < level !== v11 < level) pts.push([xs[i + 1], interp(ys[j], ys[j + 1], v10, v11)]);
      if (v01 < level !== v11 < level) pts.push([interp(xs[i], xs[i + 1], v01, v11), ys[j + 1]]);
      if (v00 < level !== v01 < level) pts.push([xs[i], interp(ys[j], ys[j + 1], v00, v01)]);

      // Two crossings: one segment. Four: an ambiguous saddle cell, drawn as
      // two segments pairing opposite edges, which is one of the two valid
      // resolutions and visually indistinguishable at this scale.
      if (pts.length >= 2) segs.push([pts[0][0], pts[0][1], pts[1][0], pts[1][1]]);
      if (pts.length === 4) segs.push([pts[2][0], pts[2][1], pts[3][0], pts[3][1]]);
    }
  }
  return segs;
}

/** All contours of a field, ready to drop into a stage. */
export function Contours({
  xs,
  ys,
  z,
  levels,
  s,
  color = TONE.muted,
  opacity = 0.75,
}: {
  xs: number[];
  ys: number[];
  z: number[][];
  levels: number[];
  s: Scale;
  color?: string;
  opacity?: number;
}) {
  return (
    <g opacity={opacity}>
      {levels.map((lv) => (
        <g key={lv}>
          {contourSegments(xs, ys, z, lv).map((sg, k) => (
            <line
              key={k}
              x1={s.sx(sg[0])}
              y1={s.sy(sg[1])}
              x2={s.sx(sg[2])}
              y2={s.sy(sg[3])}
              stroke={color}
              strokeWidth={0.9}
              strokeLinecap="round"
            />
          ))}
        </g>
      ))}
    </g>
  );
}

/* -------------------------------------------------------------------------- */
/* Chrome                                                                      */
/* -------------------------------------------------------------------------- */

/** The `<svg>` wrapper every stage uses: fixed viewBox, responsive width. */
export function Stage({
  vp,
  children,
  label,
}: {
  vp: Viewport;
  children: ReactNode;
  /** Accessible summary. Stages are informative, so this is not optional. */
  label: string;
}) {
  return (
    <svg
      viewBox={`0 0 ${vp.width} ${vp.height}`}
      width="100%"
      height={vp.height}
      role="img"
      aria-label={label}
      style={{ display: "block", maxWidth: "100%" }}
    >
      {children}
    </svg>
  );
}

/** The scalar strip under a stage: eigenvalues, λ, loss, whatever the page wants. */
export function Scalars({ items }: { items: { label: string; value: string }[] }) {
  if (items.length === 0) return null;
  return (
    <div className="pch-mz__scalars">
      {items.map((it) => (
        <span className="pch-mz__scalar" key={it.label}>
          {it.label} <b>{it.value}</b>
        </span>
      ))}
    </div>
  );
}

/** A matrix rendered as a bracketed grid, with per-cell tone classes. */
export function MatrixGrid({
  rows,
  cols,
  cellClass,
  format = (v) => (Number.isInteger(v) ? String(v) : v.toFixed(2)),
  divider,
}: {
  rows: number[][];
  /** Column count, so a ragged input still renders a rectangle. */
  cols?: number;
  /** Extra class per cell, e.g. `pch-mz__cell--active`. */
  cellClass?: (r: number, c: number) => string | undefined;
  format?: (v: number) => string;
  /** Draw a vertical rule after this column index — the augmented-matrix bar. */
  divider?: number;
}) {
  const n = cols ?? Math.max(...rows.map((r) => r.length));
  return (
    <div
      className="pch-mz__matrix"
      style={{ gridTemplateColumns: `repeat(${n}, auto)` }}
    >
      {rows.flatMap((row, r) =>
        Array.from({ length: n }, (_, c) => (
          <span
            key={`${r}-${c}`}
            className={`pch-mz__cell ${cellClass?.(r, c) ?? ""}`}
            style={
              divider !== undefined && c === divider
                ? { borderLeft: "1px solid var(--pch-line, #30363d)", paddingLeft: "0.55rem" }
                : undefined
            }
          >
            {row[c] === undefined ? "" : format(row[c])}
          </span>
        )),
      )}
    </div>
  );
}

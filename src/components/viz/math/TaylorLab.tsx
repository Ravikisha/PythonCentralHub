"use client";

/**
 * TaylorLab — one Taylor polynomial per frame, drawn against the function it is
 * approximating, with the error measured twice.
 *
 * The reason this is a lab and not a slider: the interesting frames are named.
 * "The one where T_2 is still symmetric." "The one where a degree-4 polynomial
 * stops being an approximation and becomes the function." "The one where adding
 * a term makes the fit *worse* at the edge of the window." A reader who is stuck
 * is stuck on a specific degree, and needs to stop there and read a sentence.
 *
 * Two error numbers are shown side by side, deliberately:
 *
 *   * the error **near x0**, which falls monotonically with degree for every
 *     function here — that is what a Taylor expansion promises, and
 *   * the error **over the whole window**, which for four of the five functions
 *     *grows* with degree.
 *
 * Showing only the first would flatter the method; showing only the second would
 * look like a bug. Showing both is the lesson: a Taylor polynomial buys accuracy
 * near a point by giving it up away from it.
 *
 * MDX usage:
 *
 *     import TaylorLab from "../../../../components/viz/math/TaylorLab.tsx";
 *
 *     <TaylorLab
 *       client:visible
 *       fn="sin-plus-cos"
 *       maxDegree={5}
 *       title="Exercise 5.4, one degree at a time"
 *       desc="The coefficients cycle +1, +1, −1, −1."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { taylor, type TaylorInput, type TaylorState } from "./algos/taylor";
import { Axes, Scalars, Stage, TONE, curveOf, scale as mkScale, viewport } from "./stage";

export interface TaylorLabProps extends TaylorInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 4) => {
  if (Math.abs(v) < 5e-13) return "0";
  const r = Math.round(v);
  if (Math.abs(v - r) < 1e-12) return String(r);
  return String(Number(v.toFixed(d)));
};

/**
 * The vertical window. Taylor polynomials shoot off to infinity outside their
 * useful range, so the y-range is pinned to the FUNCTION's range with a margin
 * rather than to the polynomial's — otherwise a single degree-7 tail would
 * rescale the plot until the interesting part was a flat line.
 */
function yWindow(st: TaylorState): [number, number] {
  let lo = Math.min(...st.fs);
  let hi = Math.max(...st.fs);
  const pad = Math.max(0.35, (hi - lo) * 0.45);
  lo -= pad;
  hi += pad;
  return [lo, hi];
}

function renderStage(frame: Frame<TaylorState>) {
  const st = frame.state;
  const [ylo, yhi] = yWindow(st);
  const vp = viewport([st.window[0], st.window[1], ylo, yhi], 330, 600);
  const s = mkScale(vp);

  // Clip the polynomial to the visible box so a runaway tail does not paint over
  // the axis labels.
  const clipId = `taylor-clip-${st.fn}-${st.degree}`;
  const tsClipped = st.ts.map((v) => Math.max(ylo - 1, Math.min(yhi + 1, v)));

  const nearLo = st.x0 - st.nearHalfWidth;
  const nearHi = st.x0 + st.nearHalfWidth;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <defs>
          <clipPath id={clipId}>
            <rect x={s.box.x} y={s.box.y} width={s.box.w} height={s.box.h} />
          </clipPath>
        </defs>

        <Axes s={s} xLabel="x" yLabel="f(x)" />

        {/* The band within which the error is reported as "near x0". */}
        <rect
          x={s.sx(Math.max(st.window[0], nearLo))}
          y={s.box.y}
          width={Math.max(1, s.sx(Math.min(st.window[1], nearHi)) - s.sx(Math.max(st.window[0], nearLo)))}
          height={s.box.h}
          fill={TONE.good}
          opacity={0.07}
        />

        {/* f itself, always the reference. */}
        <path
          d={curveOf(st.xs, st.fs, s)}
          fill="none"
          stroke={TONE.muted}
          strokeWidth={2.6}
          clipPath={`url(#${clipId})`}
        />

        {/* T_n. Green when it is exact, amber otherwise. */}
        <path
          d={curveOf(st.xs, tsClipped, s)}
          fill="none"
          stroke={st.exact ? TONE.good : TONE.active}
          strokeWidth={2.2}
          strokeDasharray={st.exact ? undefined : "6 3"}
          clipPath={`url(#${clipId})`}
        />

        {/* The expansion point, and the vertical line marking where the worst
            error on the window happens — usually at an edge. */}
        <line
          x1={s.sx(st.x0)}
          y1={s.box.y}
          x2={s.sx(st.x0)}
          y2={s.box.y + s.box.h}
          stroke={TONE.good}
          strokeWidth={1.2}
          strokeDasharray="3 3"
        />
        {!st.exact && (
          <line
            x1={s.sx(st.maxErrAt)}
            y1={s.box.y}
            x2={s.sx(st.maxErrAt)}
            y2={s.box.y + s.box.h}
            stroke={TONE.bad}
            strokeWidth={1}
            strokeDasharray="2 4"
            opacity={0.8}
          />
        )}

        <text className="pch-mz__label" x={s.sx(st.x0) + 6} y={s.box.y + 16} fill={TONE.good}>
          {`x0 = ${fmt(st.x0, 2)}`}
        </text>

        <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 18} fill={TONE.muted}>
          f
        </text>
        <text
          className="pch-mz__label"
          x={s.box.x + 8}
          y={s.box.y + 36}
          fill={st.exact ? TONE.good : TONE.active}
        >
          {st.exact ? `T_${st.degree} = f exactly` : `T_${st.degree}`}
        </text>
        {st.divergesOnWindow && (
          <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 54} fill={TONE.bad}>
            worse at the edge than degree {st.degree - 1}
          </text>
        )}
      </Stage>

      {/* The polynomial as text: the thing the reader is meant to copy down. */}
      <div className="pch-mz__named">
        <span className="pch-mz__namedLabel">{`T_${st.degree}(x) =`}</span> {st.polyText}
      </div>

      <Scalars
        items={[
          { label: "degree", value: `${st.degree} of ${st.maxDegree}` },
          { label: `|f − T| within ±${fmt(st.nearHalfWidth, 2)}`, value: st.nearErr.toExponential(2) },
          { label: "on the whole window", value: fmt(st.maxErr, 4) },
          { label: "local order", value: `h^${st.localOrder}` },
          ...(st.errRatio !== null && st.errRatio > 0 && st.errRatio < 1
            ? [{ label: "better than last degree by", value: `${fmt(1 / st.errRatio, 1)}x` }]
            : []),
        ]}
      />

      {/* Coefficients, with the ones not yet in play dimmed. */}
      <div className="pch-mz__scalars">
        {st.coeffs.slice(0, Math.min(st.maxDegree + 3, st.coeffs.length)).map((c, k) => (
          <span
            className="pch-mz__scalar"
            key={k}
            style={{ opacity: k <= st.degree ? 1 : 0.32 }}
          >
            {`a${k}`} <b>{fmt(c, 6)}</b>
          </span>
        ))}
      </div>

      {st.checks.length > 0 && (
        <div className="pch-mz__scalars">
          {st.checks.map((c) => (
            <span
              className="pch-mz__scalar"
              key={c.label}
              style={{ color: c.ok ? TONE.good : TONE.bad }}
            >
              {c.label} <b>{c.value}</b>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function TaylorLab({
  fn = "sin-plus-cos",
  maxDegree = 5,
  x0,
  title,
  desc,
  lib,
  ms = 1500,
  autoPlay = true,
}: TaylorLabProps) {
  const trace = useMemo(() => taylor({ fn, maxDegree, x0 }), [fn, maxDegree, x0]);

  return (
    <VizPlayer<TaylorState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="field"
      lib={lib ?? "Taylor polynomials, §5.1.1"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

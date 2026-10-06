"use client";

/**
 * SurfaceGrad — the gradient built from its definition, one claim per frame.
 *
 * §5.2 states three things about the gradient and proves none of them: that each
 * component is a limit of difference quotients, that the assembled row vector
 * points in the direction of steepest ascent, and that it is perpendicular to the
 * level set. All three are checkable, and each is one frame here with the number
 * printed underneath.
 *
 * The frame worth stopping on is the difference-quotient table. Every reader has
 * been told "let h go to zero"; almost none have seen that in floating point the
 * error stops falling and starts *rising* around h = 1e-6, because subtracting two
 * nearly equal numbers destroys digits. That table is the difference between
 * knowing the definition and being able to use it.
 *
 * MDX usage:
 *
 *     import SurfaceGrad from "../../../../components/viz/math/SurfaceGrad.tsx";
 *
 *     <SurfaceGrad
 *       client:visible
 *       surface="example-5-7"
 *       title="The book's Example 5.7, built from the definition"
 *       desc="Two limits, one row vector, three checks."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import {
  surfaceGrad,
  type SurfaceGradInput,
  type SurfaceGradState,
} from "./algos/surfacegrad";
import { Arrow, Axes, Dot, Scalars, Stage, TONE, scale as mkScale, viewport } from "./stage";

export interface SurfaceGradProps extends SurfaceGradInput {
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

/** Arrow length in data units for the longest gradient on the field. */
const FIELD_MAX_LEN = 0.42;

function renderStage(frame: Frame<SurfaceGradState>) {
  const st = frame.state;
  const vp = viewport(st.window, 340, 600);
  const s = mkScale(vp);
  const [px, py] = st.at;

  // The gradient arrow is drawn at a fixed screen length so it stays readable
  // whether |grad f| is 0.5 or 50; the number is in the strip below.
  const gLen = st.gradNorm > 1e-12 ? 0.9 : 0;
  const gx = st.gradNorm > 1e-12 ? (st.grad[0] / st.gradNorm) * gLen : 0;
  const gy = st.gradNorm > 1e-12 ? (st.grad[1] / st.gradNorm) * gLen : 0;

  const maxMag = st.field ? st.field.reduce((m, v) => Math.max(m, v.mag), 0) : 1;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <Axes s={s} xLabel="x1" yLabel="x2" />

        {/* Contours, always. They are the reference every other claim is about. */}
        {st.contours.map((c) =>
          c.segments.map((seg, k) => (
            <line
              key={`${c.level}-${k}`}
              x1={s.sx(seg[0][0])}
              y1={s.sy(seg[0][1])}
              x2={s.sx(seg[1][0])}
              y2={s.sy(seg[1][1])}
              stroke={TONE.muted}
              strokeWidth={1.1}
              opacity={0.55}
            />
          ))
        )}

        {/* The whole gradient field, on the last frame only. */}
        {st.field &&
          st.field.map((v, i) => {
            if (v.mag < 1e-9) return null;
            const L = (v.mag / maxMag) * FIELD_MAX_LEN;
            const ux = (v.dx / v.mag) * L;
            const uy = (v.dy / v.mag) * L;
            return (
              <Arrow
                key={i}
                x1={s.sx(v.x)}
                y1={s.sy(v.y)}
                x2={s.sx(v.x + ux)}
                y2={s.sy(v.y + uy)}
                color={TONE.info}
                width={1.4}
              />
            );
          })}

        {/* The directional sweep, as a polar rosette of the rate. Negative rates
            are drawn on the opposite side, which is why it is a circle through
            the origin rather than a blob. */}
        {st.sweep && st.gradNorm > 1e-12 && (
          <path
            d={
              st.sweep
                .map((q, i) => {
                  const r = (q.rate / st.gradNorm) * 0.85;
                  const x = px + r * Math.cos(q.angle);
                  const y = py + r * Math.sin(q.angle);
                  return `${i === 0 ? "M" : "L"}${s.sx(x)},${s.sy(y)}`;
                })
                .join(" ") + " Z"
            }
            fill={TONE.active}
            fillOpacity={0.1}
            stroke={TONE.active}
            strokeWidth={1.6}
          />
        )}

        {/* The two axis-aligned probes, on the partial-derivative frames. */}
        {st.wrt === 1 && (
          <line
            x1={s.sx(px - 0.7)}
            y1={s.sy(py)}
            x2={s.sx(px + 0.7)}
            y2={s.sy(py)}
            stroke={TONE.active}
            strokeWidth={2.4}
          />
        )}
        {st.wrt === 2 && (
          <line
            x1={s.sx(px)}
            y1={s.sy(py - 0.7)}
            x2={s.sx(px)}
            y2={s.sy(py + 0.7)}
            stroke={TONE.active}
            strokeWidth={2.4}
          />
        )}

        {/* The contour tangent, on the orthogonality frame. */}
        {st.tangent && st.stage === "orthogonal" && (
          <line
            x1={s.sx(px - st.tangent[0] * 0.9)}
            y1={s.sy(py - st.tangent[1] * 0.9)}
            x2={s.sx(px + st.tangent[0] * 0.9)}
            y2={s.sy(py + st.tangent[1] * 0.9)}
            stroke={TONE.good}
            strokeWidth={2.2}
            strokeDasharray="5 3"
          />
        )}

        {/* The gradient itself, from the gradient frame onwards. */}
        {st.stage !== "point" && st.stage !== "partial-1" && st.stage !== "partial-2" && gLen > 0 && (
          <Arrow
            x1={s.sx(px)}
            y1={s.sy(py)}
            x2={s.sx(px + gx)}
            y2={s.sy(py + gy)}
            color={TONE.bad}
            width={3}
          />
        )}

        <Dot cx={s.sx(px)} cy={s.sy(py)} r={5} color="#ffffff" />

        <text className="pch-mz__label" x={s.sx(px) + 9} y={s.sy(py) + 17} fill={TONE.muted}>
          {`(${fmt(px, 2)}, ${fmt(py, 2)})`}
        </text>
        {st.stage !== "point" && st.stage !== "partial-1" && st.stage !== "partial-2" && gLen > 0 && (
          <text
            className="pch-mz__label"
            x={s.sx(px + gx) + 7}
            y={s.sy(py + gy) - 6}
            fill={TONE.bad}
          >
            grad f
          </text>
        )}
        {st.stage === "orthogonal" && st.tangent && (
          <text
            className="pch-mz__label"
            x={s.sx(px + st.tangent[0] * 0.9) + 6}
            y={s.sy(py + st.tangent[1] * 0.9) + 14}
            fill={TONE.good}
          >
            contour tangent
          </text>
        )}
      </Stage>

      {/* The difference-quotient table: the point of the whole lab. */}
      {st.quotients && (
        <div className="pch-mz__named" style={{ overflowX: "auto" }}>
          <span className="pch-mz__namedLabel">{`df/dx${st.wrt} as h shrinks`}</span>
          <table style={{ borderCollapse: "collapse", fontSize: "0.78rem", marginTop: "0.4rem" }}>
            <thead>
              <tr style={{ color: TONE.muted }}>
                <th style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>h</th>
                <th style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>forward</th>
                <th style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>error</th>
                <th style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>central</th>
                <th style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>error</th>
              </tr>
            </thead>
            <tbody>
              {st.quotients.map((q) => {
                const best = q.h === st.bestH;
                return (
                  <tr key={q.h} style={{ color: best ? TONE.good : undefined }}>
                    <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {q.h.toExponential(0)}
                    </td>
                    <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {q.forward.toFixed(8)}
                    </td>
                    <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {q.errForward.toExponential(1)}
                    </td>
                    <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {q.central.toFixed(8)}
                    </td>
                    <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {q.errCentral.toExponential(1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Scalars
        items={[
          { label: "f(x)", value: fmt(st.fAt, 6) },
          { label: "df/dx1", value: fmt(st.grad[0], 6) },
          { label: "df/dx2", value: fmt(st.grad[1], 6) },
          { label: "|grad f|", value: fmt(st.gradNorm, 6) },
          { label: "shape", value: "1 x 2" },
          ...(st.sweepMax
            ? [
                {
                  label: "steepest sampled rate",
                  value: fmt(st.sweepMax.rate, 6),
                },
              ]
            : []),
        ]}
      />

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

export default function SurfaceGrad({
  surface = "example-5-7",
  at,
  title,
  desc,
  lib,
  ms = 1900,
  autoPlay = true,
}: SurfaceGradProps) {
  const trace = useMemo(() => surfaceGrad({ surface, at }), [surface, at]);

  return (
    <VizPlayer<SurfaceGradState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="field"
      lib={lib ?? "partial derivatives and the gradient, §5.2"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

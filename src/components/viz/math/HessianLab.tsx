"use client";

/**
 * HessianLab — §5.7's two pages, one claim per frame.
 *
 * The frame worth stopping on is the curvature sweep. "The Hessian measures the
 * curvature of the function locally" is the sentence the book spends one line on,
 * and it has an exact meaning: the second derivative along a unit direction d is
 * d^T H d. Drawn as a polar rosette against a measured second difference, the
 * two curves lie on top of each other and the rosette's extremes are the
 * eigenvalues — the spectral theorem visible rather than cited.
 *
 * The second frame worth stopping on is the verdict on `degenerate`. Its Hessian
 * has an eigenvalue of exactly zero, the second-order test is silent, and the
 * origin is a strict minimum anyway. That is the case every "positive definite
 * means minimum" summary quietly drops.
 *
 * MDX usage:
 *
 *     import HessianLab from "../../../../components/viz/math/HessianLab.tsx";
 *
 *     <HessianLab
 *       client:visible
 *       surface="saddle"
 *       title="A saddle, classified"
 *       desc="Zero gradient, mixed eigenvalue signs."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { hessian, type HessianInput, type HessianState } from "./algos/hessian";
import { Arrow, Axes, Dot, Scalars, Stage, TONE, scale as mkScale, viewport } from "./stage";

export interface HessianLabProps extends HessianInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, dp = 4) => {
  if (Math.abs(v) < 5e-13) return "0";
  const r = Math.round(v);
  if (Math.abs(v - r) < 1e-12) return String(r);
  return String(Number(v.toFixed(dp)));
};

/** Longest radius of the curvature rosette, in data units. */
const ROSETTE = 1.5;

function renderStage(frame: Frame<HessianState>) {
  const st = frame.state;
  const vp = viewport(st.window, 340, 600);
  const s = mkScale(vp);
  const [px, py] = st.at;

  // The rosette is normalised by the largest curvature magnitude so that a
  // Hessian with eigenvalues 1 and 30 is still readable. Negative curvature is
  // drawn inward from the point, which is what makes a saddle look like a
  // four-lobed clover rather than a circle.
  const cMax = st.sweep
    ? Math.max(...st.sweep.map((q) => Math.abs(q.quad)), 1e-12)
    : 1;

  const eigColor = (l: number) =>
    l > 1e-6 ? TONE.good : l < -1e-6 ? TONE.bad : TONE.active;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <Axes s={s} xLabel="x1" yLabel="x2" />

        {st.contours.map((c) =>
          c.segments.map((sg, k) => (
            <line
              key={`${c.level}-${k}`}
              x1={s.sx(sg[0])}
              y1={s.sy(sg[1])}
              x2={s.sx(sg[2])}
              y2={s.sy(sg[3])}
              stroke={TONE.muted}
              strokeWidth={1.1}
              opacity={0.5}
            />
          ))
        )}

        {/* The probe circle whose samples decide the ground-truth verdict. */}
        {st.probe && (
          <circle
            cx={s.sx(px)}
            cy={s.sy(py)}
            r={Math.abs(s.sx(px + st.probe.radius) - s.sx(px))}
            fill="none"
            stroke={TONE.active}
            strokeWidth={1.6}
          />
        )}

        {/* Curvature rosette: |d^T H d| as a radius, sign as the colour. */}
        {st.sweep && (
          <>
            <path
              d={st.sweep
                .map((q, i) => {
                  const r = (Math.abs(q.quad) / cMax) * ROSETTE;
                  const x = px + r * Math.cos(q.angle);
                  const y = py + r * Math.sin(q.angle);
                  return `${i === 0 ? "M" : "L"}${s.sx(x)},${s.sy(y)}`;
                })
                .join(" ")}
              fill="none"
              stroke={TONE.info}
              strokeWidth={2}
              opacity={0.95}
            />
            {/* The measured second differences, dashed, on top of the analytic
                curve. Two curves that coincide is the check. */}
            <path
              d={st.sweep
                .map((q, i) => {
                  const r = (Math.abs(q.measured) / cMax) * ROSETTE;
                  const x = px + r * Math.cos(q.angle);
                  const y = py + r * Math.sin(q.angle);
                  return `${i === 0 ? "M" : "L"}${s.sx(x)},${s.sy(y)}`;
                })
                .join(" ")}
              fill="none"
              stroke={TONE.active}
              strokeWidth={1.4}
              strokeDasharray="4 4"
            />
            {/* Sign markers: where the curvature is negative the surface bends
                DOWN along that direction, which the radius alone cannot say. */}
            {st.sweep
              .filter((_, i) => i % 12 === 0)
              .map((q, k) => {
                const r = (Math.abs(q.quad) / cMax) * ROSETTE;
                return (
                  <circle
                    key={k}
                    cx={s.sx(px + r * Math.cos(q.angle))}
                    cy={s.sy(py + r * Math.sin(q.angle))}
                    r={2.4}
                    fill={q.quad >= 0 ? TONE.good : TONE.bad}
                  />
                );
              })}
          </>
        )}

        {/* The eigenvectors, scaled by their eigenvalue's magnitude. */}
        {(st.stage === "eigen" || st.stage === "curvature") &&
          st.vecs.map((v, i) => {
            const l = st.eigs[i];
            const mag = Math.max(Math.abs(l), 1e-9);
            const scaleMax = Math.max(Math.abs(st.eigs[0]), Math.abs(st.eigs[1]), 1e-9);
            const L = 0.35 + (mag / scaleMax) * 1.05;
            return (
              <g key={i}>
                <Arrow
                  x1={s.sx(px)}
                  y1={s.sy(py)}
                  x2={s.sx(px + v[0] * L)}
                  y2={s.sy(py + v[1] * L)}
                  color={eigColor(l)}
                  width={2.6}
                />
                <Arrow
                  x1={s.sx(px)}
                  y1={s.sy(py)}
                  x2={s.sx(px - v[0] * L)}
                  y2={s.sy(py - v[1] * L)}
                  color={eigColor(l)}
                  width={2.6}
                />
                <text
                  x={s.sx(px + v[0] * (L + 0.22))}
                  y={s.sy(py + v[1] * (L + 0.22))}
                  fill={eigColor(l)}
                  fontSize={11}
                  textAnchor="middle"
                  fontFamily="monospace"
                >
                  {fmt(l, 3)}
                </text>
              </g>
            );
          })}

        {/* The gradient, where there is one worth drawing. */}
        {st.stage === "point" && st.gradNorm > 1e-9 && (
          <Arrow
            x1={s.sx(px)}
            y1={s.sy(py)}
            x2={s.sx(px + (st.grad[0] / st.gradNorm) * 0.9)}
            y2={s.sy(py + (st.grad[1] / st.gradNorm) * 0.9)}
            color={TONE.active}
            width={2.2}
          />
        )}

        {/* The two competing steps. */}
        {st.steps && (
          <>
            <Arrow
              x1={s.sx(st.steps.start[0])}
              y1={s.sy(st.steps.start[1])}
              x2={s.sx(st.steps.gradient[0])}
              y2={s.sy(st.steps.gradient[1])}
              color={TONE.warn}
              width={2.2}
            />
            <Arrow
              x1={s.sx(st.steps.start[0])}
              y1={s.sy(st.steps.start[1])}
              x2={s.sx(st.steps.newton[0])}
              y2={s.sy(st.steps.newton[1])}
              color={TONE.good}
              width={2.6}
            />
            <Dot cx={s.sx(st.steps.start[0])} cy={s.sy(st.steps.start[1])} color={TONE.muted} />
            <text
              x={s.sx(st.steps.gradient[0]) + 8}
              y={s.sy(st.steps.gradient[1]) - 6}
              fill={TONE.warn}
              fontSize={11}
              fontFamily="monospace"
            >
              gradient step
            </text>
            <text
              x={s.sx(st.steps.newton[0]) + 8}
              y={s.sy(st.steps.newton[1]) + 14}
              fill={TONE.good}
              fontSize={11}
              fontFamily="monospace"
            >
              Newton step
            </text>
          </>
        )}

        <Dot cx={s.sx(px)} cy={s.sy(py)} color={TONE.active} r={5} />
      </Stage>

      {/* The Hessian itself, analytic beside differenced. */}
      <div className="pch-mz__named">
        <span className="pch-mz__namedLabel">
          H at ({fmt(px, 3)}, {fmt(py, 3)}) — analytic, then by second differences at h = 1e-4
        </span>
        <div
          style={{
            display: "flex",
            gap: "1.4rem",
            marginTop: "0.4rem",
            flexWrap: "wrap",
            fontFamily: "monospace",
            fontSize: "0.82rem",
          }}
        >
          {[st.H, st.Hnum].map((M, k) => (
            <div key={k} style={{ display: "grid", gridTemplateColumns: "auto auto", gap: "0.15rem 0.9rem" }}>
              {M.flatMap((row, r) =>
                row.map((v, c) => (
                  <span
                    key={`${r}-${c}`}
                    style={{
                      textAlign: "right",
                      color:
                        st.entry && st.entry[0] === r && st.entry[1] === c
                          ? TONE.active
                          : r !== c
                            ? TONE.info
                            : undefined,
                    }}
                  >
                    {k === 0 ? fmt(v, 5) : v.toPrecision(7)}
                  </span>
                ))
              )}
            </div>
          ))}
        </div>
      </div>

      {/* The second-difference ladder. */}
      {st.stencils && (
        <div className="pch-mz__named" style={{ overflowX: "auto" }}>
          <span className="pch-mz__namedLabel">
            every entry as h shrinks — and the floor a division by h squared brings on early
          </span>
          <table
            style={{ borderCollapse: "collapse", fontSize: "0.78rem", marginTop: "0.4rem" }}
          >
            <thead>
              <tr style={{ color: TONE.muted }}>
                {["h", "d2f/dx1^2", "d2f/dx1dx2", "d2f/dx2dx1", "d2f/dx2^2", "worst error"].map(
                  (h) => (
                    <th key={h} style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {st.stencils.map((r) => (
                <tr key={r.h}>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                    {r.h.toExponential(0)}
                  </td>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                    {r.fxx.toFixed(6)}
                  </td>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem", color: TONE.info }}>
                    {r.fxy.toFixed(6)}
                  </td>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem", color: TONE.info }}>
                    {r.fyx.toFixed(6)}
                  </td>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                    {r.fyy.toFixed(6)}
                  </td>
                  <td style={{ textAlign: "right", padding: "0.1rem 0.6rem" }}>
                    {r.err.toExponential(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Scalars
        items={[
          { label: "f(x)", value: fmt(st.fAt, 6) },
          { label: "|grad f|", value: st.gradNorm.toExponential(1) },
          { label: "lambda_min", value: fmt(st.eigs[0], 6) },
          { label: "lambda_max", value: fmt(st.eigs[1], 6) },
          { label: "trace", value: fmt(st.H[0][0] + st.H[1][1], 6) },
          { label: "det", value: fmt(st.H[0][0] * st.H[1][1] - st.H[0][1] * st.H[1][0], 6) },
          {
            label: "condition number",
            value: st.kappa === null ? "singular" : fmt(st.kappa, 4),
          },
          ...(st.testSays ? [{ label: "test says", value: st.testSays }] : []),
          ...(st.verdict ? [{ label: "truth", value: st.verdict }] : []),
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

export default function HessianLab({
  surface = "saddle",
  at,
  title,
  desc,
  lib,
  ms = 2100,
  autoPlay = true,
}: HessianLabProps) {
  const trace = useMemo(() => hessian({ surface, at }), [surface, at]);

  return (
    <VizPlayer<HessianState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="field"
      lib={lib ?? "the Hessian, §5.7"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

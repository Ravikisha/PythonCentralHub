"use client";

/**
 * ProjectionLab — §3.8 stepped: projection onto a line, projection onto a
 * plane, and Gram-Schmidt.
 *
 * The three modes share a stage because they share a picture. In every one of
 * them there is a subspace, a vector that is not in it, and a perpendicular
 * dropped from the vector to the subspace; what changes is which part is being
 * computed and which part is already known. Drawing them the same way makes
 * Gram-Schmidt legible as what it is — the same projection, applied
 * constructively rather than as an answer.
 *
 * R³ is drawn in a fixed oblique projection with the subspace shaded, matching
 * SpanExplorer so a reader moving between the two pages does not have to relearn
 * the view. A perspective camera would make "is this arrow in the plane?"
 * ambiguous precisely where the answer matters, and the dashed perpendicular
 * settles it in any case.
 *
 * MDX usage:
 *
 *     import ProjectionLab from "../../../../components/viz/math/ProjectionLab.tsx";
 *
 *     <ProjectionLab
 *       client:visible
 *       mode="plane"
 *       basis={[[1, 1, 1], [0, 1, 2]]}
 *       target={[6, 0, 0]}
 *       title="The book's Example 3.11, step by step"
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { project, type ProjInput, type ProjState } from "./algos/projection";
import { Arrow, MatrixGrid, Scalars, Stage, TONE, scale as mkScale, viewport } from "./stage";

export interface ProjectionLabProps extends ProjInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 3) => {
  const z = Math.abs(v) < 1e-10 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

/** Oblique projection, matching SpanExplorer: z runs down-left. */
const OBL_X = -0.52;
const OBL_Y = -0.36;

function flatten(v: number[], dim: number): [number, number] {
  if (dim === 2) return [v[0], v[1]];
  return [v[0] + OBL_X * v[2], v[1] + OBL_Y * v[2]];
}

function renderStage(frame: Frame<ProjState>) {
  const st = frame.state;
  const dim = st.dim;

  const everything = [
    ...st.basis,
    ...st.built,
    ...(st.target ? [st.target] : []),
    ...(st.proj ? [st.proj] : []),
  ];
  const reach = Math.max(2, ...everything.flatMap((v) => v.map(Math.abs))) * 1.3;
  const vp = viewport([-reach, reach, -reach, reach], 380, 600);
  const s = mkScale(vp);

  const px = (v: number[]) => {
    const [a, b] = flatten(v, dim);
    return [s.sx(a), s.sy(b)] as const;
  };
  const O = px(new Array(dim).fill(0));

  // The subspace, drawn from the orthonormal frame the algorithm supplied.
  const subspace = (() => {
    if (st.frame.length === 0) return null;
    const t = reach * 1.6;
    if (st.frame.length === 1) {
      const f = st.frame[0];
      const a = px(f.map((c) => c * t));
      const b = px(f.map((c) => -c * t));
      return (
        <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={TONE.good} strokeWidth={2} opacity={0.6} />
      );
    }
    const [f, g] = st.frame;
    const corners = [
      f.map((c, i) => (c + g[i]) * t),
      f.map((c, i) => (c - g[i]) * t),
      f.map((c, i) => (-c - g[i]) * t),
      f.map((c, i) => (-c + g[i]) * t),
    ];
    return (
      <polygon
        points={corners.map((c) => px(c).join(",")).join(" ")}
        fill={TONE.good}
        fillOpacity={0.13}
        stroke={TONE.good}
        strokeWidth={1.2}
        strokeOpacity={0.5}
      />
    );
  })();

  const label = (v: number[], text: string, colour: string, dy = -6) => {
    const p = px(v);
    return (
      <text className="pch-mz__label" x={p[0] + 7} y={p[1] + dy} fill={colour}>
        {text}
      </text>
    );
  };

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <line className="pch-mz__axis" x1={s.sx(-reach)} y1={s.sy(0)} x2={s.sx(reach)} y2={s.sy(0)} />
        <line className="pch-mz__axis" x1={s.sx(0)} y1={s.sy(-reach)} x2={s.sx(0)} y2={s.sy(reach)} />
        {dim === 3 && (
          <line
            className="pch-mz__axis"
            x1={px([0, 0, -reach])[0]}
            y1={px([0, 0, -reach])[1]}
            x2={px([0, 0, reach])[0]}
            y2={px([0, 0, reach])[1]}
          />
        )}

        {subspace}

        {/* The spanning vectors. */}
        {st.basis.map((b, i) => {
          const p = px(b);
          const focused = st.focus === i;
          const colour = focused ? TONE.active : TONE.info;
          return (
            <g key={`b${i}`}>
              <Arrow
                x1={O[0]}
                y1={O[1]}
                x2={p[0]}
                y2={p[1]}
                color={colour}
                width={focused ? 3 : 2.2}
                opacity={st.mode === "gram-schmidt" && !focused ? 0.55 : 1}
              />
              {label(b, `b${i + 1}`, colour)}
            </g>
          );
        })}

        {/* Gram-Schmidt output. */}
        {st.built.map((u, i) => (
          <g key={`u${i}`}>
            <Arrow
              x1={O[0]}
              y1={O[1]}
              x2={px(u)[0]}
              y2={px(u)[1]}
              color={TONE.good}
              width={2.6}
            />
            {label(u, `u${i + 1}`, TONE.good, 16)}
          </g>
        ))}
        {st.normalised.map((q, i) => (
          <g key={`q${i}`}>
            <Arrow
              x1={O[0]}
              y1={O[1]}
              x2={px(q)[0]}
              y2={px(q)[1]}
              color="#ffffff"
              width={2}
            />
            <circle cx={px(q)[0]} cy={px(q)[1]} r={4} fill="#ffffff" />
          </g>
        ))}

        {/* The target and its projection. */}
        {st.target && (
          <g>
            <Arrow
              x1={O[0]}
              y1={O[1]}
              x2={px(st.target)[0]}
              y2={px(st.target)[1]}
              color={TONE.active}
              width={2.8}
            />
            {label(st.target, "x", TONE.active)}
          </g>
        )}
        {st.proj && (
          <g>
            <Arrow
              x1={O[0]}
              y1={O[1]}
              x2={px(st.proj)[0]}
              y2={px(st.proj)[1]}
              color={TONE.good}
              width={2.8}
            />
            {label(st.proj, "π(x)", TONE.good, 18)}
          </g>
        )}

        {/* The perpendicular: either the error, or the shadow being subtracted. */}
        {st.shadow && (
          <g>
            <line
              x1={px(st.shadow.from)[0]}
              y1={px(st.shadow.from)[1]}
              x2={px(st.shadow.to)[0]}
              y2={px(st.shadow.to)[1]}
              stroke={TONE.bad}
              strokeWidth={2.2}
              strokeDasharray="5 4"
            />
            {st.errorNorm !== null && (
              <text
                className="pch-mz__label"
                x={(px(st.shadow.from)[0] + px(st.shadow.to)[0]) / 2 + 8}
                y={(px(st.shadow.from)[1] + px(st.shadow.to)[1]) / 2}
                fill={TONE.bad}
              >
                {`error ${fmt(st.errorNorm, 3)}`}
              </text>
            )}
          </g>
        )}
      </Stage>

      {st.matrices.length > 0 && (
        <div className="pch-mz__row">
          {st.matrices.map((m) => (
            <div className="pch-mz__named" key={m.label}>
              <span className="pch-mz__namedLabel">{m.label}</span>
              <MatrixGrid rows={m.rows} format={(v) => fmt(v, 3)} />
            </div>
          ))}
        </div>
      )}

      {st.checks.length > 0 && (
        <Scalars items={st.checks.map((c) => ({ label: c.label, value: c.value }))} />
      )}

      <Scalars
        items={[
          ...(st.lambda ? [{ label: "λ", value: `(${st.lambda.map((v) => fmt(v)).join(", ")})` }] : []),
          ...(st.proj ? [{ label: "π(x)", value: `(${st.proj.map((v) => fmt(v)).join(", ")})` }] : []),
          ...(st.errorNorm !== null ? [{ label: "error", value: fmt(st.errorNorm) }] : []),
          { label: "dim U", value: String(st.frame.length) },
          { label: "ambient", value: `R^${st.dim}` },
        ]}
      />
    </div>
  );
}

export default function ProjectionLab({
  mode,
  basis,
  target,
  title,
  desc,
  lib,
  ms = 2000,
  autoPlay = true,
}: ProjectionLabProps) {
  const trace = useMemo(() => project({ mode, basis, target }), [mode, basis, target]);

  return (
    <VizPlayer<ProjState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="vector"
      lib={
        lib ??
        (mode === "gram-schmidt"
          ? "Gram-Schmidt, §3.8.3"
          : mode === "line"
            ? "projection onto a line, §3.8.1"
            : "projection onto a subspace, §3.8.2")
      }
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

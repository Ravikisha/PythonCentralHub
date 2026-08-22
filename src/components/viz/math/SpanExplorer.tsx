/**
 * SpanExplorer — offering vectors one at a time and watching the span grow.
 *
 * The stage draws the candidates as arrows, the currently-spanned subspace as a
 * shaded line or plane, and the vector under test in amber with its residual —
 * the part sticking out of the subspace — drawn as a dashed segment. When the
 * residual is zero the arrow lies flat inside the shading, which is what
 * "linearly dependent" looks like.
 *
 * 3-D is drawn in an oblique projection rather than a perspective one. A
 * perspective view makes depth ambiguous exactly when it matters (is this arrow
 * in the plane or in front of it?), whereas a fixed oblique projection with a
 * drawn floor grid keeps the answer readable, and the residual segment settles
 * it regardless.
 *
 * MDX usage:
 *
 *     import SpanExplorer from "../../../../components/viz/math/SpanExplorer.tsx";
 *
 *     <SpanExplorer
 *       client:visible
 *       dim={3}
 *       vectors={[[1, 2, -3], [2, -1, 1], [4, 3, -5]]}
 *       title="The third vector adds nothing"
 *       desc="Watch the residual collapse to zero on the last candidate — it was already in the plane."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { span, type SpanInput, type SpanState } from "./algos/span";
import { Arrow, Scalars, Stage, TONE, scale as mkScale, viewport } from "./stage";

export interface SpanExplorerProps extends SpanInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number) => {
  const z = Math.abs(v) < 1e-10 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(2)));
};

const dot = (a: number[], b: number[]) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = (a: number[]) => Math.sqrt(dot(a, a));

/** Oblique projection: z goes down-left, so the xy-plane reads as a floor. */
const OBL_X = -0.52;
const OBL_Y = -0.36;

function project(v: number[], dim: number): [number, number] {
  if (dim === 2) return [v[0], v[1]];
  return [v[0] + OBL_X * v[2], v[1] + OBL_Y * v[2]];
}

function renderStage(frame: Frame<SpanState>) {
  const st = frame.state;
  const dim = st.dim;

  const reach = Math.max(2.2, ...st.vectors.flatMap((v) => v.map(Math.abs))) * 1.25;
  const vp = viewport([-reach, reach, -reach, reach], 360, 600);
  const s = mkScale(vp);

  const px = (v: number[]) => {
    const [a, b] = project(v, dim);
    return [s.sx(a), s.sy(b)] as const;
  };
  const O = px(new Array(dim).fill(0));

  // The spanned subspace, drawn from the orthonormal frame the algorithm built.
  const subspace = (() => {
    if (st.frame.length === 0) return null;
    const t = reach * 1.5;
    if (st.frame.length === 1) {
      const f = st.frame[0];
      const a = px(f.map((c) => c * t));
      const b = px(f.map((c) => -c * t));
      return (
        <line
          x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
          stroke={TONE.good} strokeWidth={2} opacity={0.55}
          strokeDasharray="9 5"
        />
      );
    }
    // Two or more frame directions: shade the parallelogram they span.
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
        fill={TONE.good} fillOpacity={st.frame.length >= 3 ? 0.2 : 0.13}
        stroke={TONE.good} strokeWidth={1.2} strokeOpacity={0.5}
      />
    );
  })();

  // Residual of the vector under test, against the frame as it stood before it.
  const residualSeg = (() => {
    if (st.testing === null) return null;
    const v = st.vectors[st.testing];
    // Rebuild the pre-test frame: drop the last direction if this frame accepted it.
    const fr = st.verdict === "accepted" ? st.frame.slice(0, -1) : st.frame;
    let r = [...v];
    for (const f of fr) {
      const c = dot(r, f);
      r = r.map((x, i) => x - c * f[i]);
    }
    const foot = v.map((x, i) => x - r[i]);
    if (norm(r) < 1e-7) return { seg: null, len: 0, foot };
    return { seg: [px(foot), px(v)] as const, len: norm(r), foot };
  })();

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        {/* Axes. In 3-D the z axis is drawn too, so the projection is legible. */}
        <line className="pch-mz__axis" x1={s.sx(-reach)} y1={s.sy(0)} x2={s.sx(reach)} y2={s.sy(0)} />
        <line className="pch-mz__axis" x1={s.sx(0)} y1={s.sy(-reach)} x2={s.sx(0)} y2={s.sy(reach)} />
        {dim === 3 && (
          <line
            className="pch-mz__axis"
            x1={px([0, 0, -reach])[0]} y1={px([0, 0, -reach])[1]}
            x2={px([0, 0, reach])[0]} y2={px([0, 0, reach])[1]}
          />
        )}
        <text className="pch-mz__tick" x={s.sx(reach) - 10} y={s.sy(0) - 6}>x1</text>
        <text className="pch-mz__tick" x={s.sx(0) + 6} y={s.sy(reach) + 12}>x2</text>
        {dim === 3 && (
          <text className="pch-mz__tick" x={px([0, 0, reach])[0] - 4} y={px([0, 0, reach])[1] - 6}>x3</text>
        )}

        {subspace}

        {/* Every candidate. Accepted are green, rejected muted, under test amber. */}
        {st.vectors.map((v, i) => {
          const isBasis = st.basis.includes(i);
          const isRejected = st.rejected.some((r) => r.index === i);
          const isTesting = st.testing === i;
          const seen = isBasis || isRejected || isTesting;
          if (!seen) return null;
          const p = px(v);
          const colour = isTesting ? TONE.active : isBasis ? TONE.good : TONE.muted;
          return (
            <g key={i}>
              <Arrow
                x1={O[0]} y1={O[1]} x2={p[0]} y2={p[1]}
                color={colour}
                width={isTesting ? 3 : isBasis ? 2.4 : 1.6}
                opacity={isRejected && !isTesting ? 0.5 : 1}
              />
              <text
                className="pch-mz__label"
                x={p[0] + 7} y={p[1] - 6}
                fill={colour}
              >
                {`v${i + 1}`}
              </text>
            </g>
          );
        })}

        {/* The residual: what the tested vector adds beyond the current span. */}
        {residualSeg?.seg && (
          <g>
            <line
              x1={residualSeg.seg[0][0]} y1={residualSeg.seg[0][1]}
              x2={residualSeg.seg[1][0]} y2={residualSeg.seg[1][1]}
              stroke={TONE.bad} strokeWidth={2.2} strokeDasharray="5 4"
            />
            <circle
              cx={residualSeg.seg[0][0]} cy={residualSeg.seg[0][1]}
              r={3} fill={TONE.bad}
            />
            <text
              className="pch-mz__label"
              x={(residualSeg.seg[0][0] + residualSeg.seg[1][0]) / 2 + 8}
              y={(residualSeg.seg[0][1] + residualSeg.seg[1][1]) / 2}
              fill={TONE.bad}
            >
              {`new part: ${fmt(residualSeg.len)}`}
            </text>
          </g>
        )}
        {st.testing !== null && residualSeg && !residualSeg.seg && (
          <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 16} fill={TONE.bad}>
            residual is zero — this vector is already inside the span
          </text>
        )}
      </Stage>

      <Scalars
        items={[
          { label: "rank", value: String(st.basis.length) },
          { label: "of", value: String(st.dim) },
          { label: "basis", value: st.basis.length ? st.basis.map((b) => `v${b + 1}`).join(", ") : "empty" },
          ...(st.rejected.length
            ? [{ label: "dependent", value: st.rejected.map((r) => `v${r.index + 1}`).join(", ") }]
            : []),
        ]}
      />
    </div>
  );
}

export default function SpanExplorer({
  vectors,
  dim = 2,
  title,
  desc,
  lib,
  ms = 1500,
  autoPlay = true,
}: SpanExplorerProps) {
  const trace = useMemo(() => span({ vectors, dim }), [vectors, dim]);

  return (
    <VizPlayer<SpanState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="vector"
      lib={lib ?? `span in R^${dim}`}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

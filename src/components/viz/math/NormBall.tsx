/**
 * NormBall — the unit ball of ℓ_p as p sweeps, with the probe vector rescaled
 * onto it at every step.
 *
 * The shape is the lesson. A reader who has only seen the two formulas in §3.1
 * has no reason to care which one a library uses; a reader who has watched the
 * diamond's corners round off into a circle knows exactly why Lasso produces
 * exact zeros and Ridge does not.
 *
 * Earlier balls are kept as a faint trail so the sweep reads as one continuous
 * deformation rather than seven unrelated pictures, and the axes are scaled so
 * that the p = 2 ball is a true circle — an unequal aspect ratio would quietly
 * destroy the only frame the reader already has an expectation about.
 *
 * MDX usage:
 *
 *     import NormBall from "../../../../components/viz/math/NormBall.tsx";
 *
 *     <NormBall
 *       client:visible
 *       probe={[1.6, 0.9]}
 *       title="One vector, seven rulers"
 *       desc="Watch the corners appear as p falls to 1 and vanish as it rises to 2."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { norms, type NormsInput, type NormsState } from "./algos/norms";
import { Arrow, Axes, Dot, Scalars, Stage, TONE, pathOf, scale as mkScale, viewport } from "./stage";

export interface NormBallProps extends NormsInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 3) => String(Number(v.toFixed(d)));

/** Aspect chosen so one data unit is the same pixel count on both axes. */
const DOMAIN: [number, number, number, number] = [-2.2, 2.2, -1.2, 1.2];

function renderStage(frame: Frame<NormsState>) {
  const st = frame.state;
  const vp = viewport(DOMAIN, 340, 600);
  const s = mkScale(vp);

  const closed = (pts: [number, number][]) => `${pathOf(pts, s)} Z`;
  const colour = st.triangle.holds ? TONE.info : TONE.bad;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <Axes s={s} xLabel="x1" yLabel="x2" />

        {/* The trail: every ball already visited, faint. */}
        {st.trail.map((tr) => (
          <path
            key={tr.pLabel}
            d={closed(tr.ball)}
            fill="none"
            stroke={TONE.muted}
            strokeWidth={1}
            opacity={0.35}
          />
        ))}

        {/* The current ball. Shaded, because it is a set and not a curve. */}
        <path d={closed(st.ball)} fill={colour} fillOpacity={0.12} stroke={colour} strokeWidth={2.4} />

        {/* Where the ball meets the axes — ℓ1's corners, ℓ∞'s edge midpoints. */}
        {st.corners.map((c, i) => (
          <circle key={i} cx={s.sx(c[0])} cy={s.sy(c[1])} r={2.6} fill={colour} opacity={0.8} />
        ))}

        {/* The probe, and the same vector cut down to unit length. */}
        <Arrow
          x1={s.sx(0)}
          y1={s.sy(0)}
          x2={s.sx(st.probe[0])}
          y2={s.sy(st.probe[1])}
          color={TONE.active}
          width={2.6}
        />
        <Arrow
          x1={s.sx(0)}
          y1={s.sy(0)}
          x2={s.sx(st.onBall[0])}
          y2={s.sy(st.onBall[1])}
          color={TONE.good}
          width={2}
        />
        <Dot cx={s.sx(st.onBall[0])} cy={s.sy(st.onBall[1])} r={4.5} color="#ffffff" />

        <text className="pch-mz__label" x={s.sx(st.probe[0]) + 8} y={s.sy(st.probe[1]) - 6} fill={TONE.active}>
          x
        </text>
        <text
          className="pch-mz__label"
          x={s.sx(st.onBall[0]) + 8}
          y={s.sy(st.onBall[1]) + 16}
          fill={TONE.good}
        >
          {`x / ‖x‖ = ${fmt(st.probeNorm, 2)}`}
        </text>

        <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 18} fill={colour}>
          {`‖x‖_${st.pLabel} = 1`}
        </text>
        {!st.triangle.holds && (
          <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 36} fill={TONE.bad}>
            not a norm: the boundary is not convex
          </text>
        )}
      </Stage>

      <Scalars
        items={[
          { label: "p", value: st.pLabel },
          { label: "‖x‖_p", value: fmt(st.probeNorm) },
          { label: "‖e1+e2‖_p", value: fmt(st.triangle.lhs) },
          { label: "‖e1‖+‖e2‖", value: fmt(st.triangle.rhs) },
          { label: "triangle", value: st.triangle.holds ? "holds" : "fails" },
        ]}
      />
    </div>
  );
}

export default function NormBall({
  ps,
  probe,
  title,
  desc,
  lib,
  ms = 1700,
  autoPlay = true,
}: NormBallProps) {
  const trace = useMemo(() => norms({ ps, probe }), [ps, probe]);

  return (
    <VizPlayer<NormsState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="vector"
      lib={lib ?? "unit balls of the p-norm"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

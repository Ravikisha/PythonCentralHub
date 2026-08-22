/**
 * DescentLab — gradient descent and its variants, one update per frame.
 *
 * The stage is a contour plot with the iterate path drawn on it, the current
 * gradient as a dashed arrow (pointing uphill, because that is what a gradient
 * does) and the step actually taken as a solid one. Seeing those two arrows
 * disagree — on the ravine, on Rosenbrock — is the point: the step is not the
 * negative gradient once momentum or curvature is involved.
 *
 * A frame where the loss rose is marked, so an overshooting learning rate is
 * legible as an event rather than as a wobble.
 *
 * MDX usage:
 *
 *     import DescentLab from "../../../../components/viz/math/DescentLab.tsx";
 *
 *     <DescentLab
 *       client:visible
 *       surface="ill-conditioned"
 *       method="momentum"
 *       lr={0.16}
 *       beta={0.85}
 *       title="Momentum turns a hundred crossings into one traversal"
 *       desc="Watch the velocity arrow grow along the valley while the across-valley components cancel."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { descend, type DescentInput, type DescentState } from "./algos/descent";
import { Arrow, Axes, Contours, Dot, Scalars, Stage, TONE, pathOf, scale, viewport } from "./stage";

export interface DescentLabProps extends DescentInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 3) => {
  if (!Number.isFinite(v)) return "inf";
  const a = Math.abs(v);
  if (a !== 0 && (a < 1e-3 || a >= 1e5)) return v.toExponential(1);
  return v.toFixed(d).replace(/\.?0+$/, "") || "0";
};

const METHOD_LABEL: Record<string, string> = {
  gd: "gradient descent",
  momentum: "descent with momentum",
  sgd: "stochastic gradient descent",
  newton: "Newton's method",
};

function renderStage(frame: Frame<DescentState>) {
  const st = frame.state;
  const g = st.grid;
  const vp = viewport(g.window, 340, 600);
  const s = scale(vp);

  // Gradient arrows are drawn at a fixed pixel length: their magnitude varies by
  // orders of magnitude across these surfaces, and a to-scale arrow is either a
  // dot or off the canvas. The magnitude is in the watch panel instead.
  const gn = Math.hypot(st.grad[0], st.grad[1]) || 1;
  const ARROW = 46 / Math.max(s.ux, s.uy);
  const gTip: [number, number] = [
    st.at[0] + (st.grad[0] / gn) * ARROW,
    st.at[1] + (st.grad[1] / gn) * ARROW,
  ];

  const stepTip = st.step ? [st.at[0], st.at[1]] : null;
  const stepFrom = st.step ? [st.at[0] - st.step[0], st.at[1] - st.step[1]] : null;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <Axes s={s} xLabel="theta_1" yLabel="theta_2" origin={false} />
        <Contours xs={g.xs} ys={g.ys} z={g.z} levels={g.levels} s={s} />

        {g.optimum && (
          <g>
            <line
              x1={s.sx(g.optimum[0]) - 6}
              y1={s.sy(g.optimum[1])}
              x2={s.sx(g.optimum[0]) + 6}
              y2={s.sy(g.optimum[1])}
              stroke={TONE.good}
              strokeWidth={1.6}
            />
            <line
              x1={s.sx(g.optimum[0])}
              y1={s.sy(g.optimum[1]) - 6}
              x2={s.sx(g.optimum[0])}
              y2={s.sy(g.optimum[1]) + 6}
              stroke={TONE.good}
              strokeWidth={1.6}
            />
          </g>
        )}

        {/* The path so far. */}
        <path d={pathOf(st.path, s)} fill="none" stroke={TONE.info} strokeWidth={1.7} opacity={0.9} />
        {st.path.slice(0, -1).map((p, i) => (
          <circle key={i} cx={s.sx(p[0])} cy={s.sy(p[1])} r={2} fill={TONE.info} opacity={0.65} />
        ))}

        {/* The step that produced this frame's iterate. */}
        {stepFrom && stepTip && (
          <Arrow
            x1={s.sx(stepFrom[0])}
            y1={s.sy(stepFrom[1])}
            x2={s.sx(stepTip[0])}
            y2={s.sy(stepTip[1])}
            color={st.uphill ? TONE.bad : TONE.active}
            width={2.6}
          />
        )}

        {/* The gradient at the current iterate — uphill, fixed length. */}
        <Arrow
          x1={s.sx(st.at[0])}
          y1={s.sy(st.at[1])}
          x2={s.sx(gTip[0])}
          y2={s.sy(gTip[1])}
          color={TONE.muted}
          width={1.6}
          dashed
        />
        <text
          className="pch-mz__label"
          x={s.sx(gTip[0]) + 5}
          y={s.sy(gTip[1]) - 4}
          fill={TONE.muted}
        >
          grad (uphill)
        </text>

        <Dot cx={s.sx(st.at[0])} cy={s.sy(st.at[1])} r={4.6} color={st.uphill ? TONE.bad : TONE.active} />
      </Stage>

      <Scalars
        items={[
          { label: "theta", value: `(${fmt(st.at[0], 2)}, ${fmt(st.at[1], 2)})` },
          { label: "loss", value: fmt(st.loss) },
          { label: "|grad|", value: fmt(Math.hypot(st.grad[0], st.grad[1]), 2) },
          ...(st.step ? [{ label: "|step|", value: fmt(Math.hypot(st.step[0], st.step[1])) }] : []),
          ...(st.velocity ? [{ label: "|v|", value: fmt(Math.hypot(st.velocity[0], st.velocity[1])) }] : []),
          { label: "steps", value: String(st.path.length - 1) },
        ]}
      />
    </div>
  );
}

export default function DescentLab({
  surface = "quadratic",
  method = "gd",
  lr,
  beta = 0.85,
  noise = 0.9,
  steps = 24,
  start,
  title,
  desc,
  lib,
  ms = 850,
  autoPlay = true,
}: DescentLabProps) {
  const trace = useMemo(
    () => descend({ surface, method, lr, beta, noise, steps, start }),
    [surface, method, lr, beta, noise, steps, start],
  );

  return (
    <VizPlayer<DescentState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="opt"
      lib={lib ?? METHOD_LABEL[method]}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

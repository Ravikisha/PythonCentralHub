/**
 * DistributionLab — densities, mass functions, and Gaussian conditioning.
 *
 * One component with three modes rather than three components, because the three
 * traces answer parts of the same question ("what is a distribution, and what
 * can you read off it?") and a page often uses two of them a few paragraphs
 * apart. Sharing the shell keeps the visual language identical across those
 * paragraphs.
 *
 *   mode="sweep"        one frame per parameter value; pdf on the left, cdf right
 *   mode="mass"         one frame per outcome; bars plus the cdf staircase
 *   mode="conditioning" joint contours, then marginals, then a conditional slice
 *
 * MDX usage:
 *
 *     import DistributionLab from "../../../../components/viz/math/DistributionLab.tsx";
 *
 *     <DistributionLab client:visible mode="sweep" sweep="sd"
 *       values={[0.4, 0.7, 1, 1.6, 2.4]} interval={[-1, 1]}
 *       title="Narrow costs height, because the area is always 1" />
 *
 *     <DistributionLab client:visible mode="conditioning"
 *       cov={[[1, 0.8], [0.8, 1]]} slice={1.2}
 *       title="Conditioning shrinks the variance; marginalising does not" />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import {
  discreteMass,
  gaussianConditioning,
  gaussianSweep,
  type BarsState,
  type ConditioningInput,
  type CurveState,
  type DistState,
  type JointState,
  type MassInput,
  type SweepInput,
} from "./algos/distributions";
import { Axes, Contours, Dot, Scalars, Stage, TONE, curveOf, scale, viewport } from "./stage";

export type DistributionLabProps = { title: string; desc?: string; lib?: string; ms?: number; autoPlay?: boolean } & (
  | ({ mode: "sweep" } & SweepInput)
  | ({ mode: "mass" } & MassInput)
  | ({ mode: "conditioning" } & ConditioningInput)
);

const fmt = (v: number, d = 3) => v.toFixed(d).replace(/\.?0+$/, "") || "0";

/* -------------------------------------------------------------------------- */
/* Stage: continuous curve (pdf + cdf side by side)                            */
/* -------------------------------------------------------------------------- */

function CurveStage({ st, caption }: { st: CurveState; caption: string }) {
  const xMin = st.xs[0];
  const xMax = st.xs[st.xs.length - 1];
  const peak = Math.max(...st.pdf.filter(Number.isFinite), 0.001);

  // Two panels in one viewBox: the pdf left, the cdf right. Shared x domain so
  // a reader can drop a vertical line mentally from one to the other.
  const W = 600;
  const H = 300;
  const half = W / 2;

  const left = scale({
    domain: [xMin, xMax, 0, peak * 1.15],
    width: half,
    height: H,
    pad: { top: 16, right: 12, bottom: 32, left: 42 },
  });
  const right = scale({
    domain: [xMin, xMax, 0, 1.05],
    width: half,
    height: H,
    pad: { top: 16, right: 14, bottom: 32, left: 40 },
  });

  const shadeIdx = st.shade
    ? st.xs.map((x, i) => [x, i] as const).filter(([x]) => x >= st.shade!.from && x <= st.shade!.to)
    : [];

  return (
    <div>
      <Stage vp={{ domain: [0, 1, 0, 1], width: W, height: H, pad: { top: 0, right: 0, bottom: 0, left: 0 } }} label={caption}>
        {/* ---- pdf panel ---- */}
        <g>
          <Axes s={left} xLabel="x" yLabel="p(x)" origin={false} />

          {st.shade && shadeIdx.length > 1 && (
            <path
              d={
                `M${left.sx(shadeIdx[0][0])},${left.sy(0)} ` +
                shadeIdx.map(([x, i]) => `L${left.sx(x)},${left.sy(st.pdf[i])}`).join(" ") +
                ` L${left.sx(shadeIdx[shadeIdx.length - 1][0])},${left.sy(0)} Z`
              }
              fill={TONE.active}
              fillOpacity={0.2}
            />
          )}

          {st.ghosts.map((gh, k) => (
            <path
              key={k}
              d={curveOf(st.xs, gh, left)}
              fill="none"
              stroke={TONE.muted}
              strokeWidth={1}
              opacity={0.35}
            />
          ))}

          <path d={curveOf(st.xs, st.pdf, left)} fill="none" stroke={TONE.info} strokeWidth={2.4} />

          {st.markers.map((m) => (
            <g key={m.label}>
              <line
                x1={left.sx(m.at)}
                y1={left.box.y}
                x2={left.sx(m.at)}
                y2={left.box.y + left.box.h}
                stroke={TONE.active}
                strokeWidth={1.2}
                strokeDasharray="4 3"
              />
              <text className="pch-mz__label" x={left.sx(m.at) + 4} y={left.box.y + 11} fill={TONE.active}>
                {m.label}
              </text>
            </g>
          ))}
        </g>

        {/* ---- cdf panel, translated right ---- */}
        <g transform={`translate(${half}, 0)`}>
          <Axes s={right} xLabel="x" yLabel="F(x)" origin={false} />
          <path d={curveOf(st.xs, st.cdf, right)} fill="none" stroke={TONE.good} strokeWidth={2.4} />

          {st.shade && (
            <g>
              {[st.shade.from, st.shade.to].map((v, i) => (
                <line
                  key={i}
                  x1={right.sx(v)}
                  y1={right.box.y}
                  x2={right.sx(v)}
                  y2={right.box.y + right.box.h}
                  stroke={TONE.active}
                  strokeWidth={1.1}
                  strokeDasharray="4 3"
                />
              ))}
              <text
                className="pch-mz__label"
                x={right.sx(st.shade.to) + 5}
                y={right.box.y + 24}
                fill={TONE.active}
              >
                {`diff = ${fmt(st.shade.mass)}`}
              </text>
            </g>
          )}
        </g>
      </Stage>

      <Scalars
        items={[
          ...st.params.map((p) => ({ label: p.label, value: p.value })),
          ...(st.shade ? [{ label: "shaded mass", value: fmt(st.shade.mass) }] : []),
        ]}
      />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Stage: discrete bars + cdf staircase                                        */
/* -------------------------------------------------------------------------- */

function BarsStage({ st, caption }: { st: BarsState; caption: string }) {
  const W = 600;
  const H = 300;
  const n = Math.max(st.bars.length, 1);
  const peak = Math.max(0.12, ...st.bars.map((b) => b.p));

  const vp = viewport([0, n, 0, peak * 1.2], H, W, { top: 16, right: 16, bottom: 34, left: 44 });
  const s = scale(vp);
  const cdfTop = (v: number) => s.box.y + s.box.h - (v / 1) * s.box.h;
  const bw = (s.box.w / n) * 0.56;

  return (
    <div>
      <Stage vp={vp} label={caption}>
        <line
          className="pch-mz__axis"
          x1={s.box.x}
          y1={s.box.y + s.box.h}
          x2={s.box.x + s.box.w}
          y2={s.box.y + s.box.h}
        />

        {/* The cdf staircase, on a 0..1 axis sharing the same box. */}
        <path
          d={st.bars
            .filter((b) => b.revealed)
            .map((b, i) => {
              const x0 = s.sx(i);
              const x1 = s.sx(i + 1);
              return `M${x0},${cdfTop(b.cum)} L${x1},${cdfTop(b.cum)}`;
            })
            .join(" ")}
          fill="none"
          stroke={TONE.good}
          strokeWidth={2}
        />

        {st.bars.map((b, i) => {
          const x = s.sx(i + 0.5) - bw / 2;
          const h = b.revealed ? (b.p / (peak * 1.2)) * s.box.h : 0;
          const tone = st.at === i ? TONE.active : b.revealed ? TONE.info : TONE.muted;
          return (
            <g key={b.label}>
              <rect
                x={x}
                y={s.box.y + s.box.h - h}
                width={bw}
                height={h}
                fill={tone}
                fillOpacity={st.at === i ? 0.85 : 0.55}
                stroke={tone}
                strokeWidth={1.2}
                rx={2}
              />
              <text
                className="pch-mz__tick"
                x={s.sx(i + 0.5)}
                y={s.box.y + s.box.h + 15}
                textAnchor="middle"
              >
                {b.label}
              </text>
              {b.revealed && (
                <text
                  className="pch-mz__label"
                  x={s.sx(i + 0.5)}
                  y={s.box.y + s.box.h - h - 5}
                  textAnchor="middle"
                  fill={tone}
                >
                  {fmt(b.p, 2)}
                </text>
              )}
              {b.revealed && (
                <Dot cx={s.sx(i + 1)} cy={cdfTop(b.cum)} r={3} color={TONE.good} />
              )}
            </g>
          );
        })}

        <text className="pch-mz__label" x={s.box.x} y={s.box.y - 2}>
          bars = P(X = x), green staircase = F(x) on 0..1
        </text>
      </Stage>

      <Scalars items={st.params.map((p) => ({ label: p.label, value: p.value }))} />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Stage: joint Gaussian with marginals and a conditional                      */
/* -------------------------------------------------------------------------- */

function JointStage({ st, caption }: { st: JointState; caption: string }) {
  const [[s11, s12], [s21, s22]] = st.cov;
  const sd1 = Math.sqrt(s11);
  const sd2 = Math.sqrt(s22);
  const dom: [number, number, number, number] = [
    st.mu[0] - 3.4 * sd1,
    st.mu[0] + 3.4 * sd1,
    st.mu[1] - 3.4 * sd2,
    st.mu[1] + 3.4 * sd2,
  ];

  const W = 600;
  const H = 340;
  const JOINT_W = 400;

  const joint = scale({
    domain: dom,
    width: JOINT_W,
    height: H,
    pad: { top: 46, right: 12, bottom: 34, left: 46 },
  });

  // Contours of the Mahalanobis distance, which is what "1σ ellipse" means.
  const det = s11 * s22 - s12 * s21;
  const inv = [
    [s22 / det, -s12 / det],
    [-s21 / det, s11 / det],
  ];
  const gx = Array.from({ length: 61 }, (_, i) => dom[0] + ((dom[1] - dom[0]) * i) / 60);
  const gy = Array.from({ length: 61 }, (_, j) => dom[2] + ((dom[3] - dom[2]) * j) / 60);
  const z = gy.map((y) =>
    gx.map((x) => {
      const d0 = x - st.mu[0];
      const d1 = y - st.mu[1];
      return Math.sqrt(
        Math.max(0, d0 * (inv[0][0] * d0 + inv[0][1] * d1) + d1 * (inv[1][0] * d0 + inv[1][1] * d1)),
      );
    }),
  );

  // Marginal of x1 sits above the joint; x2's marginal and the conditional sit
  // to the right, rotated so their axis lines up with the joint's y axis.
  const topPeak = st.marginalX ? Math.max(...st.marginalX.pdf) : 1;
  const sidePeak = Math.max(
    st.marginalY ? Math.max(...st.marginalY.pdf) : 0,
    st.conditional ? Math.max(...st.conditional.pdf) : 0,
    0.001,
  );

  return (
    <div>
      <Stage vp={{ domain: dom, width: W, height: H, pad: { top: 0, right: 0, bottom: 0, left: 0 } }} label={caption}>
        <Axes s={joint} xLabel="x1" yLabel="x2" origin={false} />
        <Contours xs={gx} ys={gy} z={z} levels={st.levels} s={joint} color={TONE.info} opacity={0.9} />
        <Dot cx={joint.sx(st.mu[0])} cy={joint.sy(st.mu[1])} r={3.6} color={TONE.active} label="mu" />

        {/* Marginal of x1, drawn along the top edge. */}
        {st.marginalX && (
          <path
            d={st.marginalX.xs
              .map((x, i) => {
                const px = joint.sx(x);
                const py = 40 - (st.marginalX!.pdf[i] / topPeak) * 26;
                return `${i === 0 ? "M" : "L"}${px},${py}`;
              })
              .join(" ")}
            fill="none"
            stroke={TONE.muted}
            strokeWidth={2}
          />
        )}
        {st.marginalX && (
          <text className="pch-mz__label" x={joint.box.x} y={12} fill={TONE.muted}>
            p(x1) — marginal
          </text>
        )}

        {/* The conditioning slice. */}
        {st.slice !== null && (
          <g>
            <line
              x1={joint.sx(st.slice)}
              y1={joint.box.y}
              x2={joint.sx(st.slice)}
              y2={joint.box.y + joint.box.h}
              stroke={TONE.active}
              strokeWidth={2}
            />
            <text
              className="pch-mz__label"
              x={joint.sx(st.slice) + 5}
              y={joint.box.y + joint.box.h - 6}
              fill={TONE.active}
            >
              {`x1 = ${fmt(st.slice, 2)}`}
            </text>
          </g>
        )}

        {/* Marginal and conditional of x2, along the right, x mapped to density. */}
        <g>
          {st.marginalY && (
            <path
              d={st.marginalY.xs
                .map((y, i) => {
                  const px = JOINT_W + 18 + (st.marginalY!.pdf[i] / sidePeak) * 140;
                  return `${i === 0 ? "M" : "L"}${px},${joint.sy(y)}`;
                })
                .join(" ")}
              fill="none"
              stroke={TONE.muted}
              strokeWidth={2}
            />
          )}
          {st.conditional && (
            <path
              d={st.conditional.xs
                .map((y, i) => {
                  const px = JOINT_W + 18 + (st.conditional!.pdf[i] / sidePeak) * 140;
                  return `${i === 0 ? "M" : "L"}${px},${joint.sy(y)}`;
                })
                .join(" ")}
              fill="none"
              stroke={TONE.good}
              strokeWidth={2.6}
            />
          )}
          <line
            x1={JOINT_W + 18}
            y1={joint.box.y}
            x2={JOINT_W + 18}
            y2={joint.box.y + joint.box.h}
            className="pch-mz__axis"
          />
          <text className="pch-mz__label" x={JOINT_W + 18} y={12}>
            p(x2)
          </text>
          {st.conditional && (
            <text className="pch-mz__label" x={JOINT_W + 18} y={26} fill={TONE.good}>
              p(x2 | x1) — narrower
            </text>
          )}
        </g>
      </Stage>

      <Scalars
        items={[
          ...st.params.map((p) => ({ label: p.label, value: p.value })),
          ...(st.conditional
            ? [
                { label: "conditional mean", value: fmt(st.conditional.mu) },
                { label: "conditional sd", value: fmt(st.conditional.sd) },
              ]
            : []),
        ]}
      />
    </div>
  );
}

/* -------------------------------------------------------------------------- */

function renderStage(frame: Frame<DistState>) {
  const st = frame.state;
  if (st.kind === "curve") return <CurveStage st={st} caption={frame.caption} />;
  if (st.kind === "bars") return <BarsStage st={st} caption={frame.caption} />;
  return <JointStage st={st} caption={frame.caption} />;
}

const LIB: Record<string, string> = {
  sweep: "univariate Gaussian",
  mass: "probability mass function",
  conditioning: "bivariate Gaussian",
};

export default function DistributionLab(props: DistributionLabProps) {
  const { title, desc, lib, ms, autoPlay = true } = props;

  const trace = useMemo(() => {
    if (props.mode === "sweep") {
      const { sweep, values, fixed, domain, interval } = props;
      return gaussianSweep({ sweep, values, fixed, domain, interval }) as unknown as {
        frames: Frame<DistState>[];
        code?: string[];
        result?: string;
      };
    }
    if (props.mode === "mass") {
      const { labels, probs } = props;
      return discreteMass({ labels, probs }) as unknown as {
        frames: Frame<DistState>[];
        code?: string[];
        result?: string;
      };
    }
    const { mu, cov, slice } = props;
    return gaussianConditioning({ mu, cov, slice }) as unknown as {
      frames: Frame<DistState>[];
      code?: string[];
      result?: string;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(props)]);

  return (
    <VizPlayer<DistState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="dist"
      lib={lib ?? LIB[props.mode]}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms ?? (props.mode === "mass" ? 900 : 1200)}
      autoPlay={autoPlay}
    />
  );
}

/**
 * EigenLab — §4.2 stepped: characteristic polynomial, eigenvalues, eigenspaces,
 * the det/trace theorems, and the defectiveness verdict.
 *
 * In 2-D the stage draws the geometry: the unit circle and its image (an ellipse
 * for a symmetric matrix, a tilted one otherwise), the invariant lines through
 * each real eigenspace, and each eigenvector next to its image so that "the
 * matrix only scales it" is something you can see rather than something the
 * caption asserts.
 *
 * Above 2-D there is no honest picture of a general eigenbasis, so the stage
 * shows the matrix, the polynomial and the spectrum instead of a bad drawing.
 * The frames carry the same information either way.
 *
 * MDX usage:
 *
 *     import EigenLab from "../../../../components/viz/math/EigenLab.tsx";
 *
 *     <EigenLab
 *       client:visible
 *       matrix={[[4, 2], [1, 3]]}
 *       probe={[1, 0.4]}
 *       title="Example 4.5, step by step"
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { eigen, type EigenInput, type EigenState } from "./algos/eigen";
import { Arrow, MatrixGrid, Scalars, Stage, TONE, scale as mkScale, viewport } from "./stage";

export interface EigenLabProps extends EigenInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 3) => {
  const z = Math.abs(v) < 1e-9 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

const cFmt = (z: { re: number; im: number }) =>
  z.im === 0 ? fmt(z.re) : `${fmt(z.re)} ${z.im < 0 ? "-" : "+"} ${fmt(Math.abs(z.im))}i`;

/** Colour per eigenvalue index, so a value keeps its colour across frames. */
const EIG_COLOURS = [TONE.active, TONE.info, TONE.good, TONE.warn];

function renderStage(frame: Frame<EigenState>) {
  const st = frame.state;
  const twoD = st.n === 2;

  const reach = twoD
    ? Math.max(2.2, ...st.matrix.flat().map(Math.abs)) * 1.15
    : 3;
  const vp = viewport([-reach, reach, -reach, reach], twoD ? 380 : 190, 600);
  const s = mkScale(vp);

  const apply = (v: number[]) => st.matrix.map((row) => row.reduce((a, x, i) => a + x * v[i], 0));

  const circle = (mapped: boolean) => {
    const pts: string[] = [];
    for (let i = 0; i <= 160; i++) {
      const th = (2 * Math.PI * i) / 160;
      const p = mapped ? apply([Math.cos(th), Math.sin(th)]) : [Math.cos(th), Math.sin(th)];
      pts.push(`${s.sx(p[0])},${s.sy(p[1])}`);
    }
    return pts.join(" ");
  };

  return (
    <div>
      {twoD && (
        <Stage vp={vp} label={frame.caption}>
          <line className="pch-mz__axis" x1={s.sx(-reach)} y1={s.sy(0)} x2={s.sx(reach)} y2={s.sy(0)} />
          <line className="pch-mz__axis" x1={s.sx(0)} y1={s.sy(-reach)} x2={s.sx(0)} y2={s.sy(reach)} />

          {/* Unit circle, and its image under A. */}
          <polyline points={circle(false)} fill="none" stroke={TONE.muted} strokeWidth={1.2} opacity={0.7} />
          <polyline points={circle(true)} fill="none" stroke={TONE.bad} strokeWidth={2} opacity={0.85} />

          {/* Invariant lines: one per real eigenspace direction. */}
          {st.pairs.flatMap((p, pi) =>
            p.basis.map((b, bi) => {
              const colour = EIG_COLOURS[pi % EIG_COLOURS.length];
              const t = reach * 1.6;
              const dim = st.focus !== null && st.focus !== pi;
              return (
                <line
                  key={`inv${pi}-${bi}`}
                  x1={s.sx(-b[0] * t)} y1={s.sy(-b[1] * t)}
                  x2={s.sx(b[0] * t)} y2={s.sy(b[1] * t)}
                  stroke={colour}
                  strokeWidth={dim ? 1.2 : 2}
                  strokeDasharray="8 5"
                  opacity={dim ? 0.35 : 0.8}
                />
              );
            }),
          )}

          {/* Each eigenvector, and its image — collinear by construction. */}
          {st.pairs.flatMap((p, pi) =>
            p.basis.map((b, bi) => {
              const colour = EIG_COLOURS[pi % EIG_COLOURS.length];
              const img = apply(b);
              const dim = st.focus !== null && st.focus !== pi;
              return (
                <g key={`ev${pi}-${bi}`} opacity={dim ? 0.4 : 1}>
                  <Arrow
                    x1={s.sx(0)} y1={s.sy(0)} x2={s.sx(img[0])} y2={s.sy(img[1])}
                    color={colour} width={3.2} opacity={0.55}
                  />
                  <Arrow
                    x1={s.sx(0)} y1={s.sy(0)} x2={s.sx(b[0])} y2={s.sy(b[1])}
                    color={colour} width={2}
                  />
                  <text
                    className="pch-mz__label"
                    x={s.sx(img[0]) + 7} y={s.sy(img[1]) - 6}
                    fill={colour}
                  >
                    {`A v = ${cFmt(p.value)} v`}
                  </text>
                </g>
              );
            }),
          )}

          {/* The probe, if given: a direction that is generally NOT invariant. */}
          {st.probe && st.probe.length === 2 && (
            <g>
              <Arrow
                x1={s.sx(0)} y1={s.sy(0)} x2={s.sx(st.probe[0])} y2={s.sy(st.probe[1])}
                color="#ffffff" width={1.8} dashed
              />
              <Arrow
                x1={s.sx(0)} y1={s.sy(0)}
                x2={s.sx(apply(st.probe)[0])} y2={s.sy(apply(st.probe)[1])}
                color="#ffffff" width={2.4}
              />
              <text
                className="pch-mz__label"
                x={s.sx(apply(st.probe)[0]) + 7} y={s.sy(apply(st.probe)[1]) + 14}
                fill="#ffffff"
              >
                A x (rotated, not just scaled)
              </text>
            </g>
          )}

          {!st.allReal && (
            <text className="pch-mz__label" x={s.box.x + 8} y={s.box.y + 16} fill={TONE.bad}>
              complex spectrum: no real direction is invariant
            </text>
          )}
        </Stage>
      )}

      <div className="pch-mz__row">
        <div className="pch-mz__named">
          <span className="pch-mz__namedLabel">A</span>
          <MatrixGrid rows={st.matrix} format={(v) => fmt(v, 3)} />
        </div>
        {st.matrices.map((m) => (
          <div className="pch-mz__named" key={m.label}>
            <span className="pch-mz__namedLabel">{m.label}</span>
            <MatrixGrid rows={m.rows} format={(v) => fmt(v, 3)} />
          </div>
        ))}
      </div>

      {st.polyText && (
        <Scalars items={[{ label: "p(L) = det(A - L I)", value: st.polyText }]} />
      )}

      {st.pairs.length > 0 && (
        <Scalars
          items={st.pairs.map((p, i) => ({
            label: `L${i + 1}`,
            value: `${cFmt(p.value)}  (alg ${p.algebraic}, geom ${p.geometric})`,
          }))}
        />
      )}

      {st.checks.length > 0 && (
        <Scalars items={st.checks.map((c) => ({ label: c.label, value: c.value }))} />
      )}
    </div>
  );
}

export default function EigenLab({
  matrix,
  probe,
  title,
  desc,
  lib,
  ms = 2100,
  autoPlay = true,
}: EigenLabProps) {
  const trace = useMemo(() => eigen({ matrix, probe }), [matrix, probe]);

  return (
    <VizPlayer<EigenState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="matrix"
      lib={lib ?? "eigen analysis, §4.2"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

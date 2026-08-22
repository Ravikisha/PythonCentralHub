/**
 * SVDLab — §4.5 construction and §4.6 low-rank approximation, stepped.
 *
 * Two modes, one stage. `construct` walks the book's route from A^T A to
 * U Sigma V-transpose; `approximate` sums rank-1 pieces and checks the
 * Eckart-Young error against a spectral norm measured independently.
 *
 * The stage is deliberately not a geometric picture. An SVD relates two
 * different spaces of possibly different dimension, and a 2-D drawing of that
 * either restricts to 2x2 (where the SVD is least interesting) or lies. What is
 * worth seeing is the *numbers*: the singular value spectrum as a bar strip, and
 * in approximation mode the matrix, its reconstruction and their difference as
 * three heatmaps on one shared colour scale — so "the error is the next singular
 * value" is visible as the difference panel fading out.
 *
 * MDX usage:
 *
 *     import SVDLab from "../../../../components/viz/math/SVDLab.tsx";
 *
 *     <SVDLab client:visible mode="construct" matrix={[[1, 0, 1], [-2, 1, 0]]} title="..." />
 *     <SVDLab client:visible mode="approximate" matrix={ratings} title="..." />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { svd, type SvdInput, type SvdState } from "./algos/svd";
import { MatrixGrid, Scalars, Stage, TONE, viewport } from "./stage";

export interface SVDLabProps extends SvdInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 4) => {
  const z = Math.abs(v) < 1e-9 ? 0 : v;
  return Number.isInteger(z) ? String(z) : String(Number(z.toFixed(d)));
};

/** Blue for negative, amber for positive, on a shared scale. */
function heat(v: number, span: number): string {
  if (span <= 0) return "#1b2027";
  const t = Math.min(1, Math.abs(v) / span);
  const [r, g, b] = v >= 0 ? [255, 211, 67] : [107, 169, 221];
  const mix = (c: number) => Math.round(27 + (c - 27) * t);
  return `rgb(${mix(r)}, ${mix(g)}, ${mix(b)})`;
}

function Heatmap({
  rows,
  span,
  label,
  cell = 20,
}: {
  rows: number[][];
  span: number;
  label: string;
  cell?: number;
}) {
  const m = rows.length;
  const n = rows[0].length;
  return (
    <div className="pch-mz__named">
      <span className="pch-mz__namedLabel">{label}</span>
      <svg width={n * cell + 2} height={m * cell + 2} role="img" aria-label={label}>
        {rows.flatMap((row, i) =>
          row.map((v, j) => (
            <rect
              key={`${i}-${j}`}
              x={j * cell + 1}
              y={i * cell + 1}
              width={cell - 1}
              height={cell - 1}
              fill={heat(v, span)}
            />
          )),
        )}
      </svg>
    </div>
  );
}

function renderStage(frame: Frame<SvdState>) {
  const st = frame.state;
  const showHeat = st.mode === "approximate" && st.approx !== null;
  const span = Math.max(1e-9, ...st.matrix.flat().map(Math.abs));

  // The singular value strip. Fixed height, so the stage does not jump.
  const vp = viewport([0, 1, 0, 1], 118, 600, { top: 22, right: 18, bottom: 26, left: 40 });
  const sMax = Math.max(1e-9, ...st.sigma);
  const barW = st.sigma.length ? Math.min(56, 520 / st.sigma.length) : 0;

  return (
    <div>
      <Stage vp={vp} label={`singular values: ${st.sigma.map((x) => fmt(x)).join(", ")}`}>
        <line className="pch-mz__axis" x1={40} y1={92} x2={582} y2={92} />
        {st.sigma.map((v, i) => {
          const h = (v / sMax) * 62;
          const kept = st.k !== null ? i < st.k : st.focus === null || st.focus === i;
          return (
            <g key={i}>
              <rect
                x={44 + i * barW}
                y={92 - h}
                width={barW - 6}
                height={Math.max(1, h)}
                fill={kept ? TONE.active : TONE.muted}
                opacity={kept ? 0.9 : 0.45}
              />
              <text
                className="pch-mz__tick"
                x={44 + i * barW + (barW - 6) / 2}
                y={106}
                textAnchor="middle"
              >
                {`σ${i + 1}`}
              </text>
              {barW > 30 && (
                <text
                  className="pch-mz__label"
                  x={44 + i * barW + (barW - 6) / 2}
                  y={92 - h - 5}
                  textAnchor="middle"
                  fill={kept ? TONE.active : TONE.muted}
                >
                  {fmt(v, 3)}
                </text>
              )}
            </g>
          );
        })}
        <text className="pch-mz__label" x={44} y={16} fill={TONE.muted}>
          {st.k !== null ? `amber = the ${st.k} kept, grey = discarded` : "singular values, descending"}
        </text>
      </Stage>

      {showHeat && st.approx && (
        <div className="pch-mz__row">
          <Heatmap rows={st.matrix} span={span} label="A" />
          <Heatmap rows={st.approx} span={span} label={`Â(${st.k})`} />
          <Heatmap
            rows={st.matrix.map((row, i) => row.map((v, j) => v - st.approx![i][j]))}
            span={span}
            label="A − Â"
          />
        </div>
      )}

      {st.matrices.length > 0 && (
        <div className="pch-mz__row">
          {st.matrices.map((mx) => (
            <div className="pch-mz__named" key={mx.label}>
              <span className="pch-mz__namedLabel">{mx.label}</span>
              <MatrixGrid rows={mx.rows} format={(v) => fmt(v, 3)} />
            </div>
          ))}
        </div>
      )}

      <Scalars
        items={[
          { label: "shape", value: `${st.m} × ${st.n}` },
          { label: "rank", value: String(st.rank) },
          ...(st.k !== null ? [{ label: "k", value: String(st.k) }] : []),
          ...st.checks.map((c) => ({ label: c.label, value: c.value })),
        ]}
      />
    </div>
  );
}

export default function SVDLab({
  mode,
  matrix,
  ranks,
  title,
  desc,
  lib,
  ms = 2200,
  autoPlay = true,
}: SVDLabProps) {
  const trace = useMemo(() => svd({ mode, matrix, ranks }), [mode, matrix, ranks]);

  return (
    <VizPlayer<SvdState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="matrix"
      lib={mode === "construct" ? "SVD construction, §4.5.2" : "low-rank approximation, §4.6"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

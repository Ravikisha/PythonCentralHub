"use client";

/**
 * MatrixLab — what a 2×2 matrix does to the plane, built one column at a time.
 *
 * The stage draws the transformed grid rather than the original one. That is the
 * whole trick: the reader watches the *image* of a square lattice deform, so the
 * claim "straight lines stay straight and parallel lines stay parallel" is not
 * asserted, it is visible. The original lattice stays as a faint ghost so there
 * is something to compare against.
 *
 * MDX usage:
 *
 *     import MatrixLab from "../../../../components/viz/math/MatrixLab.tsx";
 *
 *     <MatrixLab
 *       client:visible
 *       matrix={[[2, 1], [0, 1.5]]}
 *       probe={[1, 1]}
 *       title="A matrix is just where the basis vectors go"
 *       desc="Frames 2 and 3 place the two columns. Everything after them follows by linearity."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { transform, type MatrixInput, type MatrixState } from "./algos/matrix";
import { Arrow, Axes, Dot, MatrixGrid, Scalars, Stage, TONE, scale, viewport } from "./stage";

export interface MatrixLabProps extends MatrixInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(2));

/** Lattice lines from −n to n, as data-space endpoint pairs. */
function lattice(n: number): [number, number, number, number][] {
  const out: [number, number, number, number][] = [];
  for (let k = -n; k <= n; k++) {
    out.push([k, -n, k, n]);
    out.push([-n, k, n, k]);
  }
  return out;
}

const LATTICE = lattice(4);

function renderStage(frame: Frame<MatrixState>) {
  const st = frame.state;
  const A = st.A;

  // The window has to hold the image of the lattice, or the interesting part
  // walks off the edge on a matrix with a large entry.
  const corners = [
    [4, 4],
    [-4, 4],
    [4, -4],
    [-4, -4],
  ].map(([x, y]) => [A[0][0] * x + A[0][1] * y, A[1][0] * x + A[1][1] * y]);
  const reach = Math.max(4.2, ...corners.flatMap((c) => [Math.abs(c[0]), Math.abs(c[1])]) );
  const lim = Math.min(reach, 9);

  const vp = viewport([-lim, lim, -lim, lim], 340, 600);
  const s = scale(vp);

  const map = (x: number, y: number): [number, number] => [
    A[0][0] * x + A[0][1] * y,
    A[1][0] * x + A[1][1] * y,
  ];

  const [c0, c1] = st.columns;

  return (
    <div>
      <Stage vp={vp} label={frame.caption}>
        <Axes s={s} xLabel="x1" yLabel="x2" />

        {/* The untransformed lattice, faint, as the thing being compared against. */}
        <g opacity={0.28}>
          {LATTICE.map((l, i) => (
            <line
              key={`o${i}`}
              x1={s.sx(l[0])}
              y1={s.sy(l[1])}
              x2={s.sx(l[2])}
              y2={s.sy(l[3])}
              stroke={TONE.muted}
              strokeWidth={0.7}
            />
          ))}
        </g>

        {/* The image of the lattice. Only appears once the frame says so. */}
        {st.grid && (
          <g opacity={0.85}>
            {LATTICE.map((l, i) => {
              const a = map(l[0], l[1]);
              const b = map(l[2], l[3]);
              return (
                <line
                  key={`t${i}`}
                  x1={s.sx(a[0])}
                  y1={s.sy(a[1])}
                  x2={s.sx(b[0])}
                  y2={s.sy(b[1])}
                  stroke={TONE.info}
                  strokeWidth={0.8}
                  opacity={0.5}
                />
              );
            })}
          </g>
        )}

        {/* The image of the unit square. */}
        {st.cell && c0 && c1 && (
          <polygon
            points={[
              [0, 0],
              c0,
              [c0[0] + c1[0], c0[1] + c1[1]],
              c1,
            ]
              .map((p) => `${s.sx(p[0])},${s.sy(p[1])}`)
              .join(" ")}
            fill={st.det < 0 ? TONE.bad : TONE.active}
            fillOpacity={0.16}
            stroke={st.det < 0 ? TONE.bad : TONE.active}
            strokeWidth={1.4}
          />
        )}

        {/* The unit square before the map, for the area comparison. */}
        {st.cell && (
          <polygon
            points={[
              [0, 0],
              [1, 0],
              [1, 1],
              [0, 1],
            ]
              .map((p) => `${s.sx(p[0])},${s.sy(p[1])}`)
              .join(" ")}
            fill="none"
            stroke={TONE.muted}
            strokeWidth={1}
            strokeDasharray="4 3"
          />
        )}

        {/* Eigen-directions, drawn as full lines because they are subspaces. */}
        {st.eigen?.map((e, i) => {
          const t = lim * 1.4;
          return (
            <g key={`e${i}`}>
              <line
                x1={s.sx(-e.vector[0] * t)}
                y1={s.sy(-e.vector[1] * t)}
                x2={s.sx(e.vector[0] * t)}
                y2={s.sy(e.vector[1] * t)}
                stroke={TONE.good}
                strokeWidth={1.3}
                strokeDasharray="7 4"
                opacity={0.9}
              />
              <text
                className="pch-mz__label"
                x={s.sx(e.vector[0] * lim * 0.72)}
                y={s.sy(e.vector[1] * lim * 0.72) - 6}
                fill={TONE.good}
              >
                {`lam = ${fmt(e.value)}`}
              </text>
            </g>
          );
        })}

        {/* The basis vectors before the map. */}
        <Arrow x1={s.sx(0)} y1={s.sy(0)} x2={s.sx(1)} y2={s.sy(0)} color={TONE.muted} width={1.6} dashed />
        <Arrow x1={s.sx(0)} y1={s.sy(0)} x2={s.sx(0)} y2={s.sy(1)} color={TONE.muted} width={1.6} dashed />

        {/* Their images. */}
        {c0 && (
          <Arrow
            x1={s.sx(0)}
            y1={s.sy(0)}
            x2={s.sx(c0[0])}
            y2={s.sy(c0[1])}
            color={st.focus === "col0" ? TONE.active : TONE.info}
            width={2.6}
          />
        )}
        {c1 && (
          <Arrow
            x1={s.sx(0)}
            y1={s.sy(0)}
            x2={s.sx(c1[0])}
            y2={s.sy(c1[1])}
            color={st.focus === "col1" ? TONE.active : TONE.good}
            width={2.6}
          />
        )}

        {c0 && (
          <text className="pch-mz__label" x={s.sx(c0[0]) + 6} y={s.sy(c0[1]) - 6} fill={TONE.info}>
            A e1
          </text>
        )}
        {c1 && (
          <text className="pch-mz__label" x={s.sx(c1[0]) + 6} y={s.sy(c1[1]) - 6} fill={TONE.good}>
            A e2
          </text>
        )}

        {/* The probe vector and its image. */}
        {st.probe && (
          <>
            <Arrow
              x1={s.sx(0)}
              y1={s.sy(0)}
              x2={s.sx(st.probe.v[0])}
              y2={s.sy(st.probe.v[1])}
              color={TONE.muted}
              width={1.8}
              dashed
            />
            <Arrow
              x1={s.sx(0)}
              y1={s.sy(0)}
              x2={s.sx(st.probe.image[0])}
              y2={s.sy(st.probe.image[1])}
              color={TONE.active}
              width={2.8}
            />
            <Dot
              cx={s.sx(st.probe.image[0])}
              cy={s.sy(st.probe.image[1])}
              color={TONE.active}
              r={3.4}
              label={st.probe.combo}
              labelDx={8}
              labelDy={14}
            />
          </>
        )}
      </Stage>

      <div className="pch-mz__row" style={{ marginTop: "0.6rem" }}>
        <MatrixGrid
          rows={A}
          format={fmt}
          cellClass={(_, c) =>
            (c === 0 && st.focus === "col0") || (c === 1 && st.focus === "col1")
              ? "pch-mz__cell--active"
              : undefined
          }
        />
        <span className="pch-mz__op">columns of A = images of e1, e2</span>
      </div>

      <Scalars
        items={[
          { label: "det A", value: fmt(st.det) },
          { label: "area factor", value: fmt(Math.abs(st.det)) },
          {
            label: "orientation",
            value: st.det < 0 ? "flipped" : Math.abs(st.det) < 1e-9 ? "collapsed" : "preserved",
          },
        ]}
      />
    </div>
  );
}

export default function MatrixLab({
  matrix,
  probe,
  eigen = true,
  title,
  desc,
  lib,
  ms = 1300,
  autoPlay = true,
}: MatrixLabProps) {
  const trace = useMemo(() => transform({ matrix, probe, eigen }), [matrix, probe, eigen]);

  return (
    <VizPlayer<MatrixState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="matrix"
      lib={lib ?? "linear map on R^2"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

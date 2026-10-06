"use client";

/**
 * AutodiffGraph — the computation graph of §5.6, forward then reverse, one node
 * per frame.
 *
 * §5.6 claims that computing a derivative costs about as much as computing the
 * function, and calls the claim "quite counterintuitive" itself. The way to make
 * it land is to count operations on screen: this lab prints the running forward
 * and reverse flop counts, and for the book's Example 5.14 the ratio comes out at
 * 2.67x — not the blow-up the symbolic expression for the derivative suggests.
 *
 * The frame to stop on is the adjoint of `a`. It is the only node in the book's
 * example with two children, so its adjoint is Eq 5.137's *sum* rather than a
 * single product, and the terms are broken out individually underneath. Dropping
 * one of those terms is the classic backpropagation bug, and it is invisible in
 * an animation that keeps moving.
 *
 * MDX usage:
 *
 *     import AutodiffGraph from "../../../../components/viz/math/AutodiffGraph.tsx";
 *
 *     <AutodiffGraph
 *       client:visible
 *       graph="example-5-14"
 *       title="Example 5.14, forward then backward"
 *       desc="Six intermediates; one of them branches."
 *     />
 */
import { useMemo } from "react";
import VizPlayer from "../VizPlayer";
import type { Frame } from "../frames";
import { autodiff, type AutodiffInput, type AutodiffState } from "./algos/autodiff";
import { Scalars, Stage, TONE, viewport } from "./stage";

export interface AutodiffGraphProps extends AutodiffInput {
  title: string;
  desc?: string;
  lib?: string;
  ms?: number;
  autoPlay?: boolean;
}

const fmt = (v: number, d = 6) => {
  if (Math.abs(v) < 5e-13) return "0";
  const r = Math.round(v);
  if (Math.abs(v - r) < 1e-12) return String(r);
  return String(Number(v.toPrecision(d)));
};

const NODE_W = 74;
const NODE_H = 42;

function renderStage(frame: Frame<AutodiffState>) {
  const st = frame.state;

  const cols = Math.max(...st.nodes.map((n) => n.col)) + 1;
  const rows = Math.max(...st.nodes.map((n) => n.row)) + 1;
  const padX = 28;
  const padY = 26;
  const gapX = 22;
  const gapY = 18;
  const width = padX * 2 + cols * NODE_W + (cols - 1) * gapX;
  const height = padY * 2 + rows * NODE_H + (rows - 1) * gapY;
  const vp = viewport([0, width, 0, height], height, width);

  const nx = (col: number) => padX + col * (NODE_W + gapX);
  const ny = (row: number) => padY + row * (NODE_H + gapY);
  const cx = (col: number) => nx(col) + NODE_W / 2;
  const cy = (row: number) => ny(row) + NODE_H / 2;

  const reverse = st.phase !== "forward";

  return (
    <div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height={height}
        role="img"
        aria-label={frame.caption}
        style={{ display: "block", maxWidth: "100%" }}
      >
        <defs>
          <marker id="ad-fwd" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill={TONE.muted} />
          </marker>
          <marker id="ad-rev" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill={TONE.bad} />
          </marker>
        </defs>

        {/* Edges. Drawn parent -> child during the forward pass and reversed
            during the sweep, so the direction of the arrows IS the phase. */}
        {st.nodes.flatMap((n, i) =>
          n.parents.map((p) => {
            const pn = st.nodes[p];
            const branching = st.nodes[p].terms !== null;
            const active =
              (!reverse && st.active === i) || (reverse && st.active === p);
            const colour = reverse ? (active || branching ? TONE.bad : TONE.muted) : active ? TONE.active : TONE.muted;
            const x1 = reverse ? nx(n.col) : nx(pn.col) + NODE_W;
            const y1 = reverse ? cy(n.row) : cy(pn.row);
            const x2 = reverse ? nx(pn.col) + NODE_W : nx(n.col);
            const y2 = reverse ? cy(pn.row) : cy(n.row);
            return (
              <line
                key={`${p}-${i}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={colour}
                strokeWidth={active || branching ? 2.2 : 1.2}
                opacity={active || branching ? 1 : 0.5}
                markerEnd={`url(#${reverse ? "ad-rev" : "ad-fwd"})`}
              />
            );
          })
        )}

        {/* Nodes. */}
        {st.nodes.map((n, i) => {
          const active = st.active === i;
          const settled = n.value !== null;
          const hasAdj = n.adjoint !== null;
          const stroke = active ? (reverse ? TONE.bad : TONE.active) : hasAdj ? TONE.good : settled ? TONE.info : TONE.muted;
          return (
            <g key={n.id}>
              <rect
                x={nx(n.col)}
                y={ny(n.row)}
                width={NODE_W}
                height={NODE_H}
                rx={6}
                fill={stroke}
                fillOpacity={active ? 0.2 : 0.07}
                stroke={stroke}
                strokeWidth={active ? 2.4 : 1.3}
              />
              <text
                className="pch-mz__label"
                x={cx(n.col)}
                y={ny(n.row) + 15}
                textAnchor="middle"
                fill={stroke}
                style={{ fontWeight: 600 }}
              >
                {n.id}
              </text>
              <text
                className="pch-mz__label"
                x={cx(n.col)}
                y={ny(n.row) + 28}
                textAnchor="middle"
                fill={TONE.muted}
                style={{ fontSize: "0.62rem" }}
              >
                {n.value === null ? "—" : fmt(n.value, 5)}
              </text>
              {n.adjoint !== null && (
                <text
                  className="pch-mz__label"
                  x={cx(n.col)}
                  y={ny(n.row) + 39}
                  textAnchor="middle"
                  fill={TONE.bad}
                  style={{ fontSize: "0.62rem" }}
                >
                  {`adj ${fmt(n.adjoint, 4)}`}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* The sum that builds the current adjoint, broken into its terms. This is
          the panel the whole lab exists for. */}
      {st.nodes.some((n) => n.terms !== null) && (
        <div className="pch-mz__named">
          {st.nodes
            .filter((n) => n.terms !== null)
            .map((n) => (
              <div key={n.id}>
                <span className="pch-mz__namedLabel">{`adj[${n.id}] =`}</span>{" "}
                {n.terms!
                  .map(
                    (tm) =>
                      `adj[${tm.from}]·∂${tm.from}/∂${n.id} = ${fmt(tm.childAdjoint, 6)}·${fmt(tm.local, 6)} = ${fmt(tm.product, 6)}`
                  )
                  .join("   +   ")}
                {n.terms!.length > 1 && (
                  <>
                    {"   →   "}
                    <b style={{ color: TONE.bad }}>{fmt(n.adjoint ?? 0, 8)}</b>
                    <span style={{ color: TONE.bad }}>
                      {"   (two children, so a SUM — Eq 5.137)"}
                    </span>
                  </>
                )}
              </div>
            ))}
        </div>
      )}

      <Scalars
        items={[
          { label: "phase", value: st.phase },
          { label: "x", value: String(st.x) },
          { label: "forward ops", value: String(st.forwardCost) },
          { label: "reverse ops", value: String(st.reverseCost) },
          ...(st.dfdx !== null
            ? [
                { label: "df/dx", value: fmt(st.dfdx, 9) },
                { label: "analytic", value: fmt(st.analytic, 9) },
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

export default function AutodiffGraph({
  graph = "example-5-14",
  x,
  title,
  desc,
  lib,
  ms = 1500,
  autoPlay = true,
}: AutodiffGraphProps) {
  const trace = useMemo(() => autodiff({ graph, x }), [graph, x]);

  return (
    <VizPlayer<AutodiffState>
      frames={trace.frames}
      renderStage={renderStage}
      title={title}
      tag="field"
      lib={lib ?? "reverse-mode autodiff, §5.6"}
      desc={desc}
      code={trace.code}
      result={trace.result}
      ms={ms}
      autoPlay={autoPlay}
    />
  );
}

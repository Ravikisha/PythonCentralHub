"""Figures for *Linear and Quadratic Programming*.

1. `example-7-5-linear-program` — the book's Figure 7.9, computed. The five
   half-planes, the feasible pentagon, linear contours, and all five vertices
   labelled with their objective values so the optimum is not merely asserted.

2. `an-lp-optimum-is-a-vertex` — why a linear objective always ends up at a
   corner, and what that costs you: rotating the objective direction makes the
   optimal vertex JUMP rather than slide. Measured over 3600 directions.

3. `primal-and-dual-side-by-side` — the two duals of Section 7.3 worked out. For
   the linear program the dual is a different-shaped LP; for the quadratic
   program Equation 7.51 is verified against a direct minimisation to 1.8e-14.
"""

from __future__ import annotations

import itertools

import numpy as np

from _style import Palette, figure

# Example 7.5, Equation 7.44.
C_LP = np.array([-5.0, -3.0])
A_LP = np.array([[2.0, 2.0], [2.0, -4.0], [-2.0, 1.0],
                 [0.0, -1.0], [0.0, 1.0]])
B_LP = np.array([33.0, 8.0, 5.0, -1.0, 8.0])

# Example 7.6, Equations 7.46 and 7.47.
Q_QP = np.array([[2.0, 1.0], [1.0, 4.0]])
C_QP = np.array([5.0, 3.0])
A_QP = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
B_QP = np.ones(4)

LABELS = ["$2x_2 \\leq 33 - 2x_1$", "$4x_2 \\geq 2x_1 - 8$",
          "$x_2 \\leq 2x_1 - 5$", "$x_2 \\geq 1$", "$x_2 \\leq 8$"]


def _vertices(A, b):
    """Every feasible intersection of two constraint boundaries."""
    out = []
    for i, j in itertools.combinations(range(len(b)), 2):
        M = A[[i, j]]
        if abs(np.linalg.det(M)) < 1e-12:
            continue
        v = np.linalg.solve(M, b[[i, j]])
        if np.all(A @ v <= b + 1e-9):
            if not any(np.allclose(v, w, atol=1e-9) for w in out):
                out.append(v)
    return np.array(out)


def _polygon(A, b, lo=-6.0, hi=18.0, n=900):
    """A boolean feasibility mask on a grid, for shading."""
    g = np.linspace(lo, hi, n)
    X, Y = np.meshgrid(g, g)
    ok = np.ones_like(X, dtype=bool)
    for row, bv in zip(A, b):
        ok &= (row[0] * X + row[1] * Y <= bv + 1e-12)
    return X, Y, ok


def example_7_5_linear_program(fig, ax, p: Palette) -> None:
    """Figure 7.9, with every vertex evaluated."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.25, 1.0])

    X, Y, ok = _polygon(A_LP, B_LP, -4.0, 17.0, 700)
    left.contourf(X, Y, ok.astype(float), levels=[0.5, 1.5],
                  colors=[p.blue], alpha=0.16)

    xs = np.linspace(-4.0, 17.0, 400)
    cols = [p.blue, p.amber, p.green, p.purple, p.red]
    for (row, bv), lab, col in zip(zip(A_LP, B_LP), LABELS, cols):
        if abs(row[1]) > 1e-12:
            left.plot(xs, (bv - row[0] * xs) / row[1], color=col,
                      linewidth=1.5, label=lab)
        else:
            left.axvline(bv / row[0], color=col, linewidth=1.5, label=lab)

    # linear contours of the objective
    for val in np.arange(-90, 30, 12.0):
        left.plot(xs, (val - C_LP[0] * xs) / C_LP[1], color=p.grid,
                  linewidth=0.8, linestyle=":")

    verts = _vertices(A_LP, B_LP)
    order = np.argsort(verts @ C_LP)
    for k, v in enumerate(verts[order]):
        best = k == 0
        left.plot([v[0]], [v[1]], "*" if best else "o",
                  color=p.green if best else p.fg,
                  markersize=17 if best else 6, zorder=7,
                  markeredgecolor=p.bg, markeredgewidth=0.8)
        left.annotate(f"{v @ C_LP:.3f}", xy=v, xytext=(7, 6),
                      textcoords="offset points", fontsize=7.6,
                      color=p.green if best else p.muted, family="monospace")
    left.set_xlim(-4.0, 17.0)
    left.set_ylim(-1.5, 11.5)
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title("Example 7.5, and the book's Figure 7.9", fontsize=9.8)
    left.legend(fontsize=7.0, loc="upper left", ncols=2)
    left.grid(alpha=0.16, linewidth=0.6)

    right.axis("off")
    right.set_xlim(0, 10)
    right.set_ylim(-0.8, 7.4)
    right.set_title("All five vertices, evaluated", fontsize=9.8)
    heads = ("vertex", "$\\mathbf{c}^\\top\\mathbf{x}$", "active constraints")
    for hx, h in zip((0.15, 3.6, 5.6), heads):
        right.text(hx, 6.9, h, fontsize=8.6, color=p.fg, weight="bold")
    right.plot([0.1, 9.9], [6.66, 6.66], color=p.grid, linewidth=1.2)
    for k, v in enumerate(verts[order]):
        y = 5.9 - k * 0.95
        best = k == 0
        col = p.green if best else p.muted
        act = [i for i, q in enumerate(A_LP @ v - B_LP) if abs(q) < 1e-9]
        right.text(0.15, y, f"({v[0]:8.5f}, {v[1]:7.5f})", fontsize=8.4,
                   color=col, family="monospace")
        right.text(3.6, y, f"{v @ C_LP:10.5f}", fontsize=8.4, color=col,
                   family="monospace")
        right.text(5.9, y, str(act), fontsize=8.4, color=col,
                   family="monospace")
        if best:
            right.text(7.6, y, "OPTIMUM", fontsize=8.2, color=p.green,
                       family="monospace")
    best_v = verts[order][0]
    right.text(
        0.15, 0.5,
        f"The optimum is $(37/3, 25/6) = ({best_v[0]:.6f}, {best_v[1]:.6f})$ "
        f"with value $-445/6 = {best_v @ C_LP:.6f}$.\n"
        "Exactly TWO constraints are active there, which is the number of "
        "variables — that is what\nmakes it a vertex rather than an edge or a "
        "face. The objective spans $-74.167$ to $+7.000$\nover the five corners, "
        "so the choice of corner is the entire problem.",
        fontsize=8.2, color=p.fg, va="bottom")

    fig.suptitle(
        "A linear program: linear objective, linear constraints, and the answer "
        "is always a corner",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The dotted lines are contours of $\\mathbf{c}^\\top\\mathbf{x}$. Because "
        "they are straight and parallel, sliding them as far as the feasible set "
        "allows always ends at a\nvertex — and it is the last vertex the contour "
        "touches. Enumerating all five and picking the smallest is a complete "
        "algorithm here; it is also why LP\nsolvers are combinatorial searches "
        "over vertices rather than gradient methods.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def an_lp_optimum_is_a_vertex(fig, ax, p: Palette) -> None:
    """The corner rule, and the discontinuity it implies."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    verts = _vertices(A_LP, B_LP)
    # order the polygon for drawing
    ctr = verts.mean(axis=0)
    ang = np.arctan2(verts[:, 1] - ctr[1], verts[:, 0] - ctr[0])
    poly = verts[np.argsort(ang)]

    left.fill(poly[:, 0], poly[:, 1], color=p.blue, alpha=0.16)
    left.plot(np.append(poly[:, 0], poly[0, 0]),
              np.append(poly[:, 1], poly[0, 1]), color=p.blue, linewidth=1.6)
    left.plot(verts[:, 0], verts[:, 1], "o", color=p.fg, markersize=6,
              zorder=6)

    # the objective along the boundary, walked
    seq = np.vstack([poly, poly[0]])
    tt = np.linspace(0, 1, 200)
    path = []
    for i in range(len(poly)):
        seg = seq[i] + np.outer(tt, seq[i + 1] - seq[i])
        path.append(seg)
    path = np.vstack(path)
    vals = path @ C_LP
    sc = left.scatter(path[:, 0], path[:, 1], c=vals, s=7, cmap="viridis",
                      zorder=5)
    best = verts[np.argmin(verts @ C_LP)]
    left.plot([best[0]], [best[1]], "*", color=p.green, markersize=18,
              markeredgecolor=p.bg, markeredgewidth=0.9, zorder=8)
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title("The objective on the boundary is piecewise LINEAR",
                   fontsize=9.6)
    left.grid(alpha=0.16, linewidth=0.6)
    left.text(
        0.03, 0.03,
        "along any edge the objective is\nlinear in the position, so it is\n"
        "monotone: it cannot have an\ninterior minimum. The minimum\n"
        "of the walk must be a CORNER.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    # rotate the objective direction and see which vertex wins
    angles = np.linspace(0, 2 * np.pi, 3601)
    winners = []
    for a in angles:
        cvec = np.array([np.cos(a), np.sin(a)])
        winners.append(int(np.argmin(verts @ cvec)))
    winners = np.array(winners)
    changes = int((np.diff(winners) != 0).sum())
    uniq = len(set(winners.tolist()))
    for k in range(len(verts)):
        mask = winners == k
        right.scatter(np.degrees(angles[mask]), np.full(mask.sum(), k),
                      s=5, color=[p.blue, p.amber, p.green, p.purple,
                                  p.red][k % 5])
    right.set_yticks(range(len(verts)))
    right.set_yticklabels([f"({v[0]:.2f}, {v[1]:.2f})" for v in verts],
                          fontsize=7.6)
    right.set_xlabel("direction of $\\mathbf{c}$, degrees")
    right.set_ylabel("which vertex is optimal")
    right.set_title("Rotate the objective: the answer JUMPS", fontsize=9.6)
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.97, 0.06,
        f"{uniq} of {len(verts)} vertices are optimal for\nsome direction; "
        f"{changes} switches over\n3600 sampled directions.\n\n"
        "The optimum never moves smoothly:\nit sits at one corner, then "
        "instantly\nsits at another.",
        transform=right.transAxes, ha="right", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Why linear programs are solved by walking corners, not by following "
        "gradients",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The gradient of a linear objective is the constant vector "
        "$\\mathbf{c}$ — it is the same everywhere and never zero, so there is no "
        "stationary point to find.\nAll the information is in which constraints "
        "are active, which is a combinatorial question. That is the structural "
        "reason simplex-type methods exist,\nand the right panel is the "
        "consequence: an arbitrarily small change in $\\mathbf{c}$ can move the "
        "answer to a completely different corner.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def primal_and_dual_side_by_side(fig, ax, p: Palette) -> None:
    """Both duals of Section 7.3, worked and checked."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    # --- the LP dual -------------------------------------------------------
    left.axis("off")
    left.set_xlim(0, 10)
    left.set_ylim(-1.2, 9.4)
    left.set_title("Linear program, Equations 7.39 and 7.43", fontsize=9.8)

    lam_lp = np.array([13 / 6, 1 / 3, 0.0, 0.0, 0.0])
    x_lp = np.array([37 / 3, 25 / 6])
    rows = [
        ("primal, Eq 7.39", p.blue,
         "$\\min\\ \\mathbf{c}^\\top\\mathbf{x}$   s.t.  "
         "$\\mathbf{A}\\mathbf{x} \\leq \\mathbf{b}$",
         f"2 variables, 5 constraints",
         f"$\\mathbf{{x}}^\\star = (37/3,\\ 25/6)$",
         f"value $= {x_lp @ C_LP:.6f}$"),
        ("dual, Eq 7.43", p.green,
         "$\\max\\ -\\mathbf{b}^\\top\\boldsymbol{\\lambda}$   s.t.  "
         "$\\mathbf{c} + \\mathbf{A}^\\top\\boldsymbol{\\lambda} = \\mathbf{0}$, "
         "$\\boldsymbol{\\lambda} \\geq 0$",
         "5 variables, 2 equality constraints",
         "$\\boldsymbol{\\lambda}^\\star = (13/6,\\ 1/3,\\ 0,\\ 0,\\ 0)$",
         f"value $= {-(B_LP @ lam_lp):.6f}$"),
    ]
    for k, (name, col, prob, shape, sol, val) in enumerate(rows):
        y = 8.6 - k * 3.9
        left.text(0.2, y, name, fontsize=10, color=col)
        left.text(0.6, y - 0.85, prob, fontsize=9.0, color=p.fg)
        left.text(0.6, y - 1.60, shape, fontsize=8.2, color=p.muted,
                  family="monospace")
        left.text(0.6, y - 2.30, sol, fontsize=8.8, color=col)
        left.text(0.6, y - 3.00, val, fontsize=8.8, color=col)
    left.text(0.2, 0.55,
              f"duality gap $= {abs(x_lp @ C_LP - (-(B_LP @ lam_lp))):.1e}$.  "
              "Both are LPs, and the dual of\nan LP is an LP — but with the "
              "roles of variables and constraints swapped.\nHere the primal is "
              "the smaller problem, so solve that one.",
              fontsize=8.2, color=p.fg, va="bottom")

    # --- the QP dual, Eq 7.51, verified -----------------------------------
    Qinv = np.linalg.inv(Q_QP)

    def d51(l):
        v = C_QP + A_QP.T @ l
        return -0.5 * v @ Qinv @ v - l @ B_QP

    def x50(l):
        return -Qinv @ (C_QP + A_QP.T @ l)

    def primal(x):
        return 0.5 * x @ Q_QP @ x + C_QP @ x

    ts = np.linspace(0.0, 6.0, 1201)
    dv = np.array([d51(np.array([0.0, t, 0.0, 0.0])) for t in ts])
    kb = int(np.argmax(dv))
    xstar = np.array([-1.0, -0.5])

    right.plot(ts, dv, color=p.green, linewidth=2.5,
               label="$D(\\lambda)$ from Eq 7.51")
    right.axhline(primal(xstar), color=p.blue, linestyle="--", linewidth=1.8,
                  label=f"$p^\\star = {primal(xstar):.6f}$")
    right.plot([ts[kb]], [dv[kb]], "o", color=p.amber, markersize=9)
    right.annotate(
        f"$\\lambda^\\star = {ts[kb]:.3f}$\n$d^\\star = {dv[kb]:.9f}$\n"
        f"gap $= {abs(primal(xstar) - dv[kb]):.1e}$",
        xy=(ts[kb], dv[kb]), xytext=(0.44, 0.24), textcoords="axes fraction",
        fontsize=8.0, color=p.fg, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))
    right.set_xlabel("$\\lambda$ on the one active coordinate")
    right.set_ylabel("dual objective")
    right.set_title("Quadratic program, Equations 7.45 and 7.52",
                    fontsize=9.8)
    right.legend(fontsize=8, loc="lower right")
    right.grid(alpha=0.20, linewidth=0.6)

    # verify Eq 7.51 against a direct evaluation of the Lagrangian
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(20000):
        l = rng.uniform(0, 4, 4)
        xx = x50(l)
        worst = max(worst, abs((primal(xx) + l @ (A_QP @ xx - B_QP)) - d51(l)))
    right.text(
        0.03, 0.97,
        f"Eq 7.50 gives $x(\\lambda) = -Q^{{-1}}(c + A^\\top\\lambda)$.\n"
        f"Substituting it into Eq 7.48 must reproduce Eq 7.51:\n"
        f"max discrepancy over 20000 random $\\lambda$ is {worst:.1e}.\n\n"
        f"$Q$ eigenvalues "
        f"{np.linalg.eigvalsh(Q_QP)[0]:.6f}, "
        f"{np.linalg.eigvalsh(Q_QP)[1]:.6f} — positive definite,\n"
        "so $Q^{-1}$ exists and Eq 7.50 is well defined.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Two convex families, two duals, and both gaps are zero",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The pattern is the same both times: write the Lagrangian, collect the "
        "terms in $\\mathbf{x}$, set the derivative in $\\mathbf{x}$ to zero. For "
        "the LP that derivative\nhas no $\\mathbf{x}$ in it, so it becomes a "
        "CONSTRAINT on $\\boldsymbol{\\lambda}$ and the dual is another LP. For "
        "the QP it can be solved for $\\mathbf{x}$, so substituting back gives a "
        "concave\nquadratic in $\\boldsymbol{\\lambda}$. That difference is the "
        "whole distinction between Equations 7.43 and 7.52.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


FIGURES = [
    figure("example-7-5-linear-program", example_7_5_linear_program,
           size=(13.4, 5.1), axes=False),
    figure("an-lp-optimum-is-a-vertex", an_lp_optimum_is_a_vertex,
           size=(12.4, 4.9), axes=False),
    figure("primal-and-dual-side-by-side", primal_and_dual_side_by_side,
           size=(13.2, 5.0), axes=False),
]

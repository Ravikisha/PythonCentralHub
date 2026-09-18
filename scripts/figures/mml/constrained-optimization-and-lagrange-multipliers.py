"""Figures for *Constrained Optimization and Lagrange Multipliers*.

1. `the-wall-and-the-slope` — Equations 7.18/7.19 against 7.20. The indicator
   function gives the right answer and cannot be optimised: outside the feasible
   set it is +inf everywhere, so its gradient carries no information about which
   way the feasible set lies. The Lagrangian replaces that wall with a slope, and
   the slope is what a gradient method can follow.

2. `example-7-6-box-constrained-qp` — the book's Figure 7.4. Elliptical contours,
   a box, an unconstrained minimiser that is infeasible, and the constrained
   optimum pinned on the boundary. The multipliers are computed, and only the
   active constraint gets a nonzero one.

3. `weak-and-strong-duality` — three measurements. The minimax inequality with a
   deliberately strict gap; the convex QP where the dual closes to 1e-14; and a
   nonconvex problem where the gap is 1.9841 and the dual optimum is attained at
   an infeasible point.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from _style import Palette, figure

# The book's Example 7.6 / Figure 7.4.
Q = np.array([[2.0, 1.0], [1.0, 4.0]])
C = np.array([5.0, 3.0])
AMAT = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
BVEC = np.ones(4)
X_UNC = np.linalg.solve(Q, -C)          # [-17/7, -1/7]
X_CON = np.array([-1.0, -0.5])          # solved by hand on the x1 = -1 edge


def _f(x1, x2):
    return (x1 ** 2 + x1 * x2 + 2.0 * x2 ** 2) + 5.0 * x1 + 3.0 * x2


def the_wall_and_the_slope(fig, ax, p: Palette) -> None:
    """An infinite step cannot be descended; a linear penalty can."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    # A one-dimensional slice through the QP at x2 = -0.5, so the picture is
    # honest about what a gradient method actually sees.
    xs = np.linspace(-3.0, 1.6, 2000)
    fv = _f(xs, -0.5)
    feas = xs >= -1.0

    a1.plot(xs, fv, color=p.muted, linewidth=1.6, linestyle="--",
            label="$f(x)$, unconstrained")
    big = 30.0
    jv = np.where(feas, fv, np.nan)
    a1.plot(xs[feas], jv[feas], color=p.blue, linewidth=2.6,
            label="$J(x)$, Eq 7.18")
    a1.plot([-1.0, -1.0], [_f(-1.0, -0.5), big], color=p.blue, linewidth=2.6)
    a1.annotate("", xy=(-1.0, big), xytext=(-1.0, big - 8),
                arrowprops=dict(arrowstyle="-|>", color=p.blue, linewidth=2.2))
    a1.axvspan(-3.0, -1.0, color=p.red, alpha=0.10, linewidth=0)
    a1.text(-2.0, 20, "$J = +\\infty$ here\nfor every $x$",
            ha="center", fontsize=8.6, color=p.red, family="monospace")
    a1.text(-2.0, 8,
            "gradient: $0$ or undefined.\nNothing points back\ntoward the "
            "feasible set.",
            ha="center", va="top", fontsize=7.8, color=p.red,
            family="monospace")
    a1.plot([X_UNC[0]], [_f(*X_UNC)], "o", color=p.muted, markersize=7)
    a1.text(X_UNC[0], _f(*X_UNC) - 3.2,
            f"unconstrained\nminimum, $f={_f(*X_UNC):.4f}$\nINFEASIBLE",
            ha="center", va="top", fontsize=7.6, color=p.muted,
            family="monospace")
    a1.set_xlabel("$x_1$  (slice at $x_2 = -0.5$)")
    a1.set_ylabel("objective")
    a1.set_ylim(-9, 34)
    a1.set_title("Eq 7.19: an infinite step function", fontsize=9.6)
    a1.legend(fontsize=7.8, loc="upper right")
    a1.grid(alpha=0.20, linewidth=0.6)

    for lam, col in ((0.0, p.muted), (1.0, p.blue), (2.5, p.green),
                     (5.0, p.amber)):
        lv = fv + lam * (-xs - 1.0)
        a2.plot(xs, lv, color=col, linewidth=2.1,
                label=f"$\\lambda = {lam}$")
        k = int(np.argmin(lv))
        a2.plot([xs[k]], [lv[k]], "o", color=col, markersize=5.5)
    a2.axvline(-1.0, color=p.red, linestyle="--", linewidth=1.5)
    a2.text(-0.95, -12.5, "constraint\n$x_1 \\geq -1$", fontsize=7.8,
            color=p.red, family="monospace", va="bottom")
    a2.set_xlabel("$x_1$")
    a2.set_ylabel("$L(x, \\lambda)$")
    a2.set_ylim(-13, 24)
    a2.set_title("Eq 7.20: a slope instead of a wall", fontsize=9.6)
    a2.legend(fontsize=7.8, loc="upper right")
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(0.03, 0.03,
            "every one of these is smooth\nand differentiable everywhere.\n"
            "The minimiser slides right as\n$\\lambda$ grows, and reaches the\n"
            "boundary at exactly $\\lambda^\\star$.",
            transform=a2.transAxes, ha="left", va="bottom", fontsize=7.6,
            color=p.fg, family="monospace")

    # D(lambda) for the slice, and where it peaks.
    lams = np.linspace(0.0, 8.0, 801)
    dv = np.array([(fv + lam * (-xs - 1.0)).min() for lam in lams])
    a3.plot(lams, dv, color=p.green, linewidth=2.4, label="$D(\\lambda)$")
    kbest = int(np.argmax(dv))
    a3.plot([lams[kbest]], [dv[kbest]], "o", color=p.amber, markersize=8)
    a3.axhline(_f(-1.0, -0.5), color=p.blue, linestyle="--", linewidth=1.6,
               label="$p^\\star$, the primal optimum of the slice")
    a3.set_xlabel("$\\lambda$")
    a3.set_ylabel("$D(\\lambda) = \\min_x L(x, \\lambda)$")
    a3.set_title("The dual: concave, and it peaks at $p^\\star$", fontsize=9.6)
    a3.legend(fontsize=7.8, loc="lower right")
    a3.grid(alpha=0.20, linewidth=0.6)
    a3.text(
        0.97, 0.55,
        f"$\\lambda^\\star = {lams[kbest]:.3f}$\n"
        f"$D(\\lambda^\\star) = {dv[kbest]:.6f}$\n"
        f"$p^\\star = {_f(-1.0, -0.5):.6f}$\n"
        f"gap = {_f(-1.0, -0.5) - dv[kbest]:.2e}",
        transform=a3.transAxes, ha="right", va="center", fontsize=7.8,
        color=p.fg, family="monospace")

    fig.suptitle(
        "The whole idea of a Lagrange multiplier: replace an infinite step "
        "with a linear function",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Equation 7.18 is correct and useless. Its penalty is $+\\infty$ on the "
        "whole infeasible region, so a gradient computed there is either zero or "
        "undefined\nand cannot tell you where to go. Equation 7.20 penalises "
        "linearly instead: still an over-estimate of the constraint's cost when "
        "$\\lambda$ is large, but\ndifferentiable everywhere, and its minimiser "
        "walks continuously to the boundary as $\\lambda$ rises.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def example_7_6_box_constrained_qp(fig, ax, p: Palette) -> None:
    """Figure 7.4, computed rather than sketched."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.15, 1.0])

    g1 = np.linspace(-3.2, 3.2, 320)
    g2 = np.linspace(-3.2, 3.2, 320)
    G1, G2 = np.meshgrid(g1, g2)
    Z = _f(G1, G2)
    cs = left.contour(G1, G2, Z, levels=22, colors=p.grid, linewidths=0.9)
    left.contour(G1, G2, Z, levels=[_f(*X_CON)], colors=[p.green],
                 linewidths=1.8, linestyles="--")

    left.add_patch(Rectangle((-1, -1), 2, 2, facecolor=p.blue, alpha=0.12,
                             edgecolor=p.blue, linewidth=2.0))
    left.text(0.0, 1.12, "feasible set: $-1 \\leq x_i \\leq 1$", ha="center",
              fontsize=8.4, color=p.blue)

    left.plot([X_UNC[0]], [X_UNC[1]], "o", color=p.red, markersize=10,
              markeredgecolor=p.bg, markeredgewidth=1.2)
    left.annotate(
        f"unconstrained\n$(-17/7, -1/7)$\n$f = {_f(*X_UNC):.6f}$\nINFEASIBLE",
        xy=X_UNC, xytext=(-30, -46), textcoords="offset points",
        ha="center", fontsize=7.8, color=p.red, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    left.plot([X_CON[0]], [X_CON[1]], "*", color=p.green, markersize=18,
              markeredgecolor=p.bg, markeredgewidth=0.8, zorder=7)
    left.annotate(
        f"constrained\n$(-1, -1/2)$\n$f = {_f(*X_CON):.6f}$",
        xy=X_CON, xytext=(46, 26), textcoords="offset points",
        ha="center", fontsize=7.8, color=p.green, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.green, linewidth=1.1))
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_aspect("equal")
    left.set_title("Example 7.6, and the book's Figure 7.4", fontsize=9.8)

    # The multipliers, from the stationarity condition Qx + c + A^T lam = 0.
    lam = np.zeros(4)
    lam[1] = 2.5              # only the x1 >= -1 face is active
    resid = Q @ X_CON + C + AMAT.T @ lam
    gvals = AMAT @ X_CON - BVEC
    names = ["$x_1 \\leq 1$", "$-x_1 \\leq 1$", "$x_2 \\leq 1$",
             "$-x_2 \\leq 1$"]

    right.axis("off")
    right.set_xlim(0, 10)
    right.set_ylim(-1.4, 6.4)
    right.set_title("Which constraints are doing work?", fontsize=9.8)
    heads = ("constraint", "$g_i(x^\\star)$", "$\\lambda_i^\\star$",
             "$\\lambda_i g_i$", "status")
    xs = (0.2, 2.9, 4.7, 6.3, 8.0)
    for hx, h in zip(xs, heads):
        right.text(hx, 5.9, h, fontsize=8.6, color=p.fg, weight="bold")
    right.plot([0.1, 9.9], [5.66, 5.66], color=p.grid, linewidth=1.2)
    for k in range(4):
        y = 4.7 - k * 0.85
        active = abs(gvals[k]) < 1e-9
        col = p.amber if active else p.muted
        right.text(xs[0], y, names[k], fontsize=8.6, color=col)
        right.text(xs[1], y, f"{gvals[k]:+.4f}", fontsize=8.4, color=col,
                   family="monospace")
        right.text(xs[2], y, f"{lam[k]:.4f}", fontsize=8.4, color=col,
                   family="monospace")
        right.text(xs[3], y, f"{lam[k] * gvals[k]:+.1e}", fontsize=8.4,
                   color=col, family="monospace")
        right.text(xs[4], y, "ACTIVE" if active else "slack", fontsize=8.4,
                   color=(p.amber if active else p.muted), family="monospace")
    right.text(
        0.2, 0.55,
        "Complementary slackness: for every $i$, either the constraint is tight\n"
        "($g_i = 0$) or its multiplier is zero. Never both nonzero. So a\n"
        "multiplier is the PRICE of a constraint, and a slack constraint is free.",
        fontsize=8.2, color=p.fg, va="bottom")
    right.text(
        0.2, -1.25,
        f"Stationarity check, $\\|Qx^\\star + c + A^\\top\\lambda^\\star\\| = "
        f"{np.linalg.norm(resid):.2e}$.  The constraint costs "
        f"{_f(*X_CON) - _f(*X_UNC):.6f} in objective value,\n"
        f"and $\\lambda^\\star_2 = 2.5$ is the rate at which that cost would fall "
        "if the boundary were relaxed.",
        fontsize=8.0, color=p.muted, va="bottom")

    fig.suptitle(
        "A constrained optimum sits where it is pushed, not where the gradient "
        "vanishes",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "At the starred point the gradient of $f$ is NOT zero — it points out "
        "through the wall, and the wall pushes back. That balance is exactly "
        "what\n$\\nabla f + \\mathbf{A}^\\top\\boldsymbol{\\lambda} = \\mathbf{0}$ "
        "says, and it is why constrained optimality is a statement about forces "
        "rather than about flatness.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def weak_and_strong_duality(fig, ax, p: Palette) -> None:
    """Three measurements: a strict minimax gap, strong duality, a real gap."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    # --- panel 1: the minimax inequality, made strict ----------------------
    grid = np.linspace(0.0, 1.0, 601)
    X, Y = np.meshgrid(grid, grid, indexing="ij")
    PHI = (X - Y) ** 2
    inner_max = PHI.max(axis=1)
    inner_min = PHI.min(axis=0)
    minimax = inner_max.min()
    maximin = inner_min.max()

    a1.plot(grid, inner_max, color=p.blue, linewidth=2.3,
            label="$\\max_y \\phi(x,y)$, a function of $x$")
    a1.plot(grid, inner_min, color=p.green, linewidth=2.3,
            label="$\\min_x \\phi(x,y)$, a function of $y$")
    a1.axhline(minimax, color=p.blue, linestyle="--", linewidth=1.4)
    a1.axhline(maximin, color=p.green, linestyle="--", linewidth=1.4)
    a1.fill_between(grid, maximin, minimax, color=p.amber, alpha=0.15,
                    linewidth=0)
    a1.text(0.5, (minimax + maximin) / 2,
            f"gap = {minimax - maximin:.4f}", ha="center", fontsize=8.6,
            color=p.amber, family="monospace")
    a1.set_xlabel("the free variable")
    a1.set_ylabel("$\\phi(x,y) = (x-y)^2$ on $[0,1]^2$")
    a1.set_title("Eq 7.23 is an inequality, not an identity", fontsize=9.6)
    a1.legend(fontsize=7.4, loc="upper center")
    a1.grid(alpha=0.20, linewidth=0.6)
    a1.text(0.02, 0.97,
            f"$\\min_x\\max_y = {minimax:.4f}$  (exactly $1/4$)\n"
            f"$\\max_y\\min_x = {maximin:.4f}$  (exactly $0$)\n"
            "maximin $\\leq$ minimax, strictly",
            transform=a1.transAxes, ha="left", va="top", fontsize=7.6,
            color=p.fg, family="monospace")

    # --- panel 2: strong duality on the convex QP --------------------------
    def dual_qp(lam):
        v = C + AMAT.T @ lam
        xs_ = np.linalg.solve(Q, -v)
        return 0.5 * xs_ @ Q @ xs_ + v @ xs_ - lam @ BVEC

    l2 = np.linspace(0.0, 6.0, 601)
    dq = np.array([dual_qp(np.array([0.0, t, 0.0, 0.0])) for t in l2])
    pstar = _f(*X_CON)
    a2.plot(l2, dq, color=p.green, linewidth=2.4,
            label="$D(\\lambda)$ along the active coordinate")
    a2.axhline(pstar, color=p.blue, linestyle="--", linewidth=1.7,
               label=f"$p^\\star = {pstar:.6f}$")
    kb = int(np.argmax(dq))
    a2.plot([l2[kb]], [dq[kb]], "o", color=p.amber, markersize=9)
    a2.annotate(f"$\\lambda^\\star = {l2[kb]:.3f}$\n"
                f"$d^\\star = {dq[kb]:.6f}$\n"
                f"gap = {pstar - dq[kb]:.1e}",
                xy=(l2[kb], dq[kb]), xytext=(0.42, 0.22),
                textcoords="axes fraction", fontsize=7.8, color=p.fg,
                family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))
    a2.set_xlabel("$\\lambda$")
    a2.set_ylabel("dual objective")
    a2.set_title("Convex problem: the gap closes", fontsize=9.6)
    a2.legend(fontsize=7.6, loc="lower right")
    a2.grid(alpha=0.20, linewidth=0.6)

    # --- panel 3: a nonconvex primal with a real gap -----------------------
    xs3 = np.linspace(-4.0, 4.0, 40001)
    f3 = xs3 ** 4 - 8.0 * xs3 ** 2 + xs3
    g3 = -xs3                                    # the constraint x >= 0
    feas3 = g3 <= 0
    p3 = float(f3[feas3].min())
    xp3 = float(xs3[feas3][int(np.argmin(f3[feas3]))])
    lam3 = np.linspace(0.0, 6.0, 1201)
    d3 = np.array([(f3 + t * g3).min() for t in lam3])
    kb3 = int(np.argmax(d3))
    lstar3 = float(lam3[kb3])
    xd3 = float(xs3[int(np.argmin(f3 + lstar3 * g3))])

    a3.plot(xs3, f3, color=p.muted, linewidth=1.7, label="$f(x) = x^4-8x^2+x$")
    a3.plot(xs3, f3 + lstar3 * g3, color=p.green, linewidth=2.2,
            label=f"$L(x, \\lambda^\\star={lstar3:.2f})$")
    a3.axvspan(-4.0, 0.0, color=p.red, alpha=0.10, linewidth=0)
    a3.text(-2.0, 26, "infeasible\n$x < 0$", ha="center", fontsize=8.2,
            color=p.red, family="monospace")
    a3.plot([xp3], [p3], "*", color=p.blue, markersize=16, zorder=6)
    a3.plot([xd3], [float(d3[kb3])], "o", color=p.amber, markersize=8,
            zorder=6)
    a3.annotate(f"$p^\\star = {p3:.4f}$\nat $x = {xp3:.4f}$",
                xy=(xp3, p3), xytext=(14, 26), textcoords="offset points",
                fontsize=7.6, color=p.blue, family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.blue, linewidth=1.0))
    a3.annotate(f"$d^\\star = {d3[kb3]:.4f}$\nattained at $x = {xd3:.2f}$,\n"
                "which is INFEASIBLE",
                xy=(xd3, float(d3[kb3])), xytext=(-8, -54),
                textcoords="offset points", ha="center",
                fontsize=7.6, color=p.amber, family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.0))
    a3.set_xlabel("$x$")
    a3.set_ylabel("objective")
    a3.set_ylim(-24, 34)
    a3.set_title(f"Nonconvex: a gap of {p3 - float(d3[kb3]):.4f}",
                 fontsize=9.6)
    a3.legend(fontsize=7.4, loc="upper left")
    a3.grid(alpha=0.20, linewidth=0.6)

    fig.suptitle(
        "Weak duality always holds; strong duality is a property of convex "
        "problems",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Left: swapping a min and a max is not free — here it costs exactly "
        f"$1/4$. Middle: for the convex quadratic program the dual optimum "
        f"reaches $p^\\star$ to\n"
        f"{pstar - dq[kb]:.0e}, so solving either problem answers the other. "
        f"Right: the same machinery on a nonconvex objective leaves "
        f"{p3 - float(d3[kb3]):.4f} on the table, and the dual's\n"
        f"best guess sits at $x = {xd3:.2f}$, a point the primal forbids. The "
        "dual only ever sees the convex envelope of the problem.",
        ha="center", va="bottom", fontsize=8.1, color=p.muted)


FIGURES = [
    figure("the-wall-and-the-slope", the_wall_and_the_slope,
           size=(13.6, 4.9), axes=False),
    figure("example-7-6-box-constrained-qp", example_7_6_box_constrained_qp,
           size=(12.6, 5.1), axes=False),
    figure("weak-and-strong-duality", weak_and_strong_duality,
           size=(14.0, 4.9), axes=False),
]

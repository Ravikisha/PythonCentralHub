"""Figures for *The Concept of the Margin* (§12.2.1).

1. `distance-needs-a-scale` — Figure 12.4 on the running example: the vector
   addition of Equation 12.8, the orthogonal projection onto the hyperplane,
   and r read off as a signed coordinate along w/||w||.

2. `what-a-scale-costs` — the two things a scale choice decides. Left: an
   anisotropic rescale swings the separating direction by up to 45 degrees on
   data that never moved. Right: how the margin collapses as a negative point
   walks toward the positive class, and where feasibility stops.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
W_STAR, B_STAR = np.array([1.0, 0.0]), -2.0


def _hard_margin(XX, YY, seed=0):
    rg = np.random.default_rng(seed)
    d = XX.shape[1]
    v0 = np.r_[rg.normal(0, 1, d), rg.normal(0, 1)]
    return minimize(lambda v: 0.5 * v[:d] @ v[:d], v0,
                    constraints=[{"type": "ineq",
                                  "fun": lambda v: YY * (XX @ v[:d] + v[d]) - 1}],
                    method="SLSQP", options={"maxiter": 5000, "ftol": 1e-14})


def _best(XX, YY, tries=25):
    best, bv = None, np.inf
    for s in range(tries):
        r = _hard_margin(XX, YY, seed=s)
        d = XX.shape[1]
        viol = float(np.maximum(0, 1 - YY * (XX @ r.x[:d] + r.x[d])).max())
        val = 0.5 * r.x[:d] @ r.x[:d]
        if viol < 1e-7 and val < bv:
            bv, best = val, r
    return best


def _scatter(ax, p: Palette, XX=X, YY=Y, size=85):
    pos, neg = XX[YY > 0], XX[YY < 0]
    ax.scatter(pos[:, 0], pos[:, 1], marker="x", s=size, lw=2.3,
               color=p.amber, label="$y = +1$", zorder=4)
    ax.scatter(neg[:, 0], neg[:, 1], marker="o", s=size, lw=2.0,
               facecolor="none", edgecolor=p.blue, label="$y = -1$", zorder=4)


# --------------------------------------------------------------------------
# 1. distance needs a scale
# --------------------------------------------------------------------------

def distance_needs_a_scale(fig, ax, p: Palette) -> None:
    ax.set_xlim(-2.2, 7.4)
    ax.set_ylim(-2.4, 2.6)
    ax.axvline(2.0, color=p.fg, lw=2.4)
    ax.axvline(3.0, color=p.amber, ls="--", lw=1.6)
    ax.axvline(1.0, color=p.blue, ls="--", lw=1.6)
    ax.axvspan(1.0, 3.0, color=p.muted, alpha=0.10)

    # Equation 12.8 for the far positive point
    xa = np.array([6.0, 1.0])
    r = W_STAR @ xa + B_STAR
    xp = xa - r * W_STAR
    ax.annotate("", xy=tuple(xa), xytext=tuple(xp),
                arrowprops=dict(arrowstyle="-|>", lw=2.2, color=p.red))
    ax.plot([xp[0]], [xp[1]], "o", ms=8, color=p.red, zorder=5)
    ax.annotate(r"$x_a$", (6.1, 1.16), fontsize=12, color=p.red)
    ax.annotate(r"$x_a'$", (1.45, 1.16), fontsize=12, color=p.red)
    ax.annotate(r"$r \cdot w/\|w\|$", (3.7, 1.28),
                fontsize=12, color=p.red)

    ax.annotate(r"$\langle w,x\rangle + b = 0$", (2.06, -2.28),
                fontsize=10, color=p.fg)
    ax.annotate(r"$\langle w,x\rangle + b = +1$", (3.06, 2.16),
                fontsize=10, color=p.amber)
    ax.annotate(r"$= -1$", (0.30, 2.16), fontsize=10, color=p.blue)
    ax.annotate("", xy=(3.0, -1.78), xytext=(2.0, -1.78),
                arrowprops=dict(arrowstyle="<|-|>", lw=1.7, color=p.purple))
    ax.annotate(r"$r = 1/\|w\| = 1$", (2.05, -1.62),
                fontsize=11, color=p.purple)

    _scatter(ax, p)
    sv = np.isclose(Y * (X @ W_STAR + B_STAR), 1.0)
    ax.scatter(X[sv, 0], X[sv, 1], s=310, facecolor="none",
               edgecolor=p.green, lw=2.2, zorder=3,
               label="on the margin")
    ax.set_xlabel("$x^{(1)}$")
    ax.set_ylabel("$x^{(2)}$")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Equation 12.8: $r$ is the coordinate of $x_a$ along "
                 r"$w/\|w\|$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what a scale costs
# --------------------------------------------------------------------------

def what_a_scale_costs(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.05]})

    # --- left: an anisotropic rescale on rotated data
    th = np.radians(30.0)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    XR = X @ R.T
    w_ref = _best(XR, Y).x[:2]
    w_ref = w_ref / np.linalg.norm(w_ref)

    cols = [p.blue, p.green, p.fg, p.purple, p.red]
    ts = np.array([-3.0, 3.0])
    for (s, c) in zip((0.1, 0.5, 1.0, 4.0, 10.0), cols):
        Xs = XR * np.array([1.0, s])
        best = _best(Xs, Y)
        ww, bb = best.x[:2], best.x[2]
        wo = np.array([ww[0], ww[1] * s])       # back to original coordinates
        u = wo / np.linalg.norm(wo)
        if u @ w_ref < 0:
            u, wo, bb = -u, -wo, -bb
        ang = np.degrees(np.arccos(np.clip(u @ w_ref, -1, 1)))
        # the line {x : <wo, x> + bb = 0}
        d = np.array([-wo[1], wo[0]]) / np.linalg.norm(wo)
        x0 = -bb * wo / (wo @ wo)
        pts = x0[None, :] + ts[:, None] * d[None, :] * 1.6
        lw = 2.8 if abs(s - 1.0) < 1e-9 else 1.6
        a1.plot(pts[:, 0], pts[:, 1], color=c, lw=lw,
                label=f"$s = {s:g}$  ({ang:.1f}$^\\circ$)")
    _scatter(a1, p, XR, Y, size=70)
    a1.set_xlim(-1.9, 6.9)
    a1.set_ylim(-2.0, 6.4)
    a1.set_aspect("equal", adjustable="box")
    a1.set_xlabel("$x^{(1)}$")
    a1.set_ylabel("$x^{(2)}$")
    a1.legend(fontsize=7.2, loc="upper left", ncol=2, framealpha=0.92,
              handlelength=1.4, columnspacing=0.9)
    a1.set_title("scale $x^{(2)}$ by $s$, refit, map back:\n"
                 "the separator rotates by up to $45^\\circ$", fontsize=10)

    # --- right: the margin as an intruder walks in
    ts2 = np.linspace(0.2, 3.6, 35)
    got_t, got_m = [], []
    for t in ts2:
        XX, YY = np.vstack([X, [t, 0.0]]), np.r_[Y, -1.0]
        best = _best(XX, YY, tries=14)
        if best is None:
            continue
        got_t.append(t)
        got_m.append(1.0 / np.linalg.norm(best.x[:2]))
    a2.plot(got_t, got_m, "o", ms=6, color=p.blue, label="measured")
    grid = np.linspace(0.2, 3.0, 300)
    a2.plot(grid, np.minimum(1.0, (3.0 - grid) / 2.0), color=p.red, lw=2.2,
            label=r"$\min\{1,\ (3-t)/2\}$")
    a2.axvspan(3.0, 3.7, color=p.red, alpha=0.12)
    a2.annotate("no separating\nhyperplane exists", (3.32, 0.62),
                fontsize=9, color=p.red, ha="center")
    a2.axvline(3.0, color=p.red, ls="--", lw=1.5)
    a2.set_xlim(0.15, 3.7)
    a2.set_ylim(-0.05, 1.15)
    a2.set_xlabel("$t$, where the extra negative point $(t, 0)$ sits")
    a2.set_ylabel("the maximum margin")
    a2.legend(fontsize=8.5, loc="lower left")
    a2.set_title("the margin falls to zero before\nfeasibility does",
                 fontsize=10)

    fig.suptitle("A distance needs a scale, and a margin needs a gap",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("distance-needs-a-scale", distance_needs_a_scale, size=(8.6, 4.8)),
    figure("what-a-scale-costs", what_a_scale_costs, size=(9.8, 4.8),
           axes=False),
]

"""Figures for *The Convex Hull View* (§12.3.2).

1. `the-two-closest-points` — Figure 12.9(b) on the running example: the two
   convex hulls, the shortest segment joining them, and the SVM hyperplane
   drawn as its perpendicular bisector.

2. `the-reduced-hull` — the remark at the end of §12.3.2, measured. Capping
   every weight at mu contracts each hull toward its class mean, and the two
   closest points move apart.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
XP, XN = X[Y > 0], X[Y < 0]


def _hull_distance(P, N_, mu=1.0, tries=20):
    np_, nn = len(P), len(N_)

    def obj(v):
        c, d = v[:np_] @ P, v[np_:] @ N_
        return float((c - d) @ (c - d))

    best, bv = None, np.inf
    for s in range(tries):
        rg = np.random.default_rng(s)
        r = minimize(obj, np.r_[rg.dirichlet(np.ones(np_)),
                                rg.dirichlet(np.ones(nn))],
                     bounds=[(0.0, mu)] * (np_ + nn),
                     constraints=[
                         {"type": "eq", "fun": lambda v: v[:np_].sum() - 1.0},
                         {"type": "eq", "fun": lambda v: v[np_:].sum() - 1.0}],
                     method="SLSQP", options={"maxiter": 30000, "ftol": 1e-15})
        if r.success and r.fun < bv - 1e-14:
            bv, best = r.fun, r.x.copy()
    if best is None:
        return None, None
    return best[:np_] @ P, best[np_:] @ N_


def _poly(ax, pts, col, p: Palette, alpha=0.13, lw=1.8, ls="-"):
    if len(pts) < 3:
        ax.plot(pts[:, 0], pts[:, 1], color=col, lw=lw, ls=ls)
        return
    h = ConvexHull(pts)
    loop = np.r_[h.vertices, h.vertices[:1]]
    ax.fill(pts[h.vertices, 0], pts[h.vertices, 1], color=col, alpha=alpha,
            zorder=1)
    ax.plot(pts[loop, 0], pts[loop, 1], color=col, lw=lw, ls=ls, zorder=2)


def _scatter(ax, p: Palette, size=85):
    ax.scatter(XP[:, 0], XP[:, 1], marker="x", s=size, lw=2.3, color=p.amber,
               label="$y = +1$", zorder=6)
    ax.scatter(XN[:, 0], XN[:, 1], marker="o", s=size, lw=2.1,
               facecolor="none", edgecolor=p.blue, label="$y = -1$", zorder=6)


# --------------------------------------------------------------------------
# 1. the two closest points
# --------------------------------------------------------------------------

def the_two_closest_points(fig, ax, p: Palette) -> None:
    c, d = _hull_distance(XP, XN)
    w = 2 * (c - d) / ((c - d) @ (c - d))
    b = -w @ ((c + d) / 2)

    _poly(ax, XP, p.amber, p)
    _poly(ax, XN, p.blue, p)

    ys = np.array([-2.4, 2.4])
    ax.plot((-b - w[1] * ys) / w[0], ys, color=p.fg, lw=2.6, zorder=3,
            label="the SVM hyperplane")
    ax.annotate("", xy=tuple(c), xytext=tuple(d),
                arrowprops=dict(arrowstyle="<|-|>", lw=2.4, color=p.green))
    ax.plot([c[0], d[0]], [c[1], d[1]], "o", ms=9, color=p.green, zorder=7)
    cc, dd = c + 0.0, d + 0.0          # kill any negative zero in the label
    ax.annotate(rf"$c = ({cc[0]:.0f}, {abs(cc[1]):.0f})$",
                (c[0] + 0.16, c[1] + 0.20), fontsize=11, color=p.green)
    ax.annotate(rf"$d = ({dd[0]:.0f}, {abs(dd[1]):.0f})$",
                (d[0] - 1.42, d[1] + 0.20), fontsize=11, color=p.green)
    ax.annotate(r"$\|c - d\| = 2$", (1.55, -0.45), fontsize=10.5,
                color=p.green, ha="center")
    ax.plot([2.0], [0.0], "s", ms=8, color=p.fg, zorder=7)
    ax.annotate("the midpoint", (2.06, -1.35), fontsize=9.5, color=p.fg)

    _scatter(ax, p)
    ax.set_xlim(-2.2, 7.4)
    ax.set_ylim(-2.4, 2.4)
    ax.set_xlabel("$x^{(1)}$")
    ax.set_ylabel("$x^{(2)}$")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Figure 12.9(b): the hyperplane bisects the shortest "
                 "segment between the hulls",
                 fontsize=11, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the reduced hull
# --------------------------------------------------------------------------

def the_reduced_hull(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    # the reduced hull of a point set: all weightings with each weight <= mu
    def reduced_pts(pts, mu, samples=4000):
        n = len(pts)
        if mu * n < 1 - 1e-12:
            return None
        rg = np.random.default_rng(0)
        out = []
        for _ in range(samples):
            a = rg.dirichlet(np.ones(n))
            if a.max() <= mu:
                out.append(a @ pts)
        # plus the extreme points: put mu on as many as possible
        for order in range(n):
            a = np.zeros(n)
            left = 1.0
            for k in range(n):
                idx = (order + k) % n
                take = min(mu, left)
                a[idx] = take
                left -= take
                if left <= 1e-12:
                    break
            out.append(a @ pts)
        return np.array(out)

    for mu, col, ls in ((1.0, None, "-"), (0.5, p.purple, "--"),
                        (0.3, p.red, ":")):
        RP, RN = reduced_pts(XP, mu), reduced_pts(XN, mu)
        if RP is None or RN is None:
            continue
        _poly(a1, RP, col or p.amber, p, alpha=0.10, lw=1.7, ls=ls)
        _poly(a1, RN, col or p.blue, p, alpha=0.10, lw=1.7, ls=ls)
        c, d = _hull_distance(XP, XN, mu=mu)
        a1.plot([c[0], d[0]], [c[1], d[1]], color=col or p.green, lw=2.2,
                ls=ls, marker="o", ms=6, zorder=5,
                label=rf"$\mu = {mu:g}$: $\|c-d\| = "
                      rf"{np.linalg.norm(c-d):.2f}$")
    a1.plot(*XP.mean(0), "*", ms=16, color=p.amber, zorder=7,
            markeredgecolor=p.fg, markeredgewidth=0.6)
    a1.plot(*XN.mean(0), "*", ms=16, color=p.blue, zorder=7,
            markeredgecolor=p.fg, markeredgewidth=0.6)
    _scatter(a1, p, size=70)
    a1.set_xlim(-2.0, 7.2)
    a1.set_ylim(-2.35, 1.9)
    a1.set_xlabel("$x^{(1)}$")
    a1.set_ylabel("$x^{(2)}$")
    a1.legend(fontsize=7.6, loc="lower center", ncol=2, framealpha=0.93)
    a1.set_title("capping each weight at $\\mu$ shrinks both hulls\n"
                 "toward their class means (stars)", fontsize=10)

    mus = np.array([1.0, 0.8, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.28, 0.26])
    dist = []
    for mu in mus:
        c, d = _hull_distance(XP, XN, mu=float(mu), tries=12)
        dist.append(np.linalg.norm(c - d) if c is not None else np.nan)
    a2.plot(mus, dist, color=p.purple, lw=2.6, marker="o")
    sep = np.linalg.norm(XP.mean(0) - XN.mean(0))
    a2.axhline(sep, color=p.green, ls="--", lw=1.8)
    a2.annotate(f"distance between the class means, {sep:.2f}",
                (0.99, sep - 0.22), fontsize=9, color=p.green, ha="right")
    a2.axvline(0.25, color=p.red, ls=":", lw=1.6)
    a2.annotate(r"$\mu = 1/4$: each hull" "\n" "collapses to one point",
                (0.31, 2.35), fontsize=8.8, color=p.red, ha="left")
    a2.set_xlabel(r"$\mu$, the cap on every weight")
    a2.set_ylabel(r"$\|c - d\|$")
    a2.invert_xaxis()
    a2.set_title("and the closest points move apart", fontsize=10)

    fig.suptitle("The reduced hull: what the bound $\\alpha_i \\leq C$ "
                 "does to the geometry",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-two-closest-points", the_two_closest_points, size=(8.8, 4.6)),
    figure("the-reduced-hull", the_reduced_hull, size=(10.0, 4.4),
           axes=False),
]

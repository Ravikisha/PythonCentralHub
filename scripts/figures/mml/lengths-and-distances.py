"""Figures for *Lengths and Distances*.

1. `cauchy-schwarz` — the inequality as a measurement. Ten thousand random pairs
   of vectors, each plotted as |<x,y>| against ||x|| * ||y||. Every point falls
   on or below the diagonal, and the ones that touch it are exactly the parallel
   pairs. The panel prints the largest ratio observed, so the claim "never
   exceeds one" is a number on the figure rather than an assertion in the prose.

2. `metric-changes-neighbours` — the choice of metric is a modelling decision,
   not a formality. One query point, nine candidates, and four different
   notions of distance: l1, l2, l-infinity, and the Mahalanobis distance induced
   by the covariance of the surrounding cloud. Each panel draws its own unit
   ball around the query and marks its own winner, and the winners differ.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

QUERY = np.array([0.0, 0.0])

# Nine candidates, placed so that the four metrics genuinely disagree: some are
# close along one axis, some along the diagonal, some along the cloud's own
# principal direction.
CANDIDATES = np.array(
    [
        [1.30, 0.10],
        [0.20, 1.24],
        [0.86, 0.84],
        [-0.95, 0.70],
        [1.05, -0.62],
        [-0.30, -1.18],
        [1.44, 1.30],
        [-1.35, -1.20],
        [0.55, -0.98],
    ]
)

# The cloud whose covariance defines the Mahalanobis metric. Strongly correlated,
# so "far" along the minor axis is much less distance than the same displacement
# along the major one.
COV = np.array([[1.0, 0.86], [0.86, 1.0]])


def cauchy_schwarz(fig, ax, p: Palette) -> None:
    """Ten thousand pairs, none of which breaks the bound."""
    rng = np.random.default_rng(3)
    n = 10000
    d = 5
    X = rng.normal(size=(n, d))
    Y = rng.normal(size=(n, d))

    # Force a slice of the sample to be exactly parallel or antiparallel, so the
    # equality case is present rather than merely approached.
    k = 220
    signs = rng.choice([-1.0, 1.0], size=k)[:, None]
    Y[:k] = X[:k] * signs * rng.uniform(0.3, 2.5, size=(k, 1))

    lhs = np.abs(np.sum(X * Y, axis=1))
    rhs = np.linalg.norm(X, axis=1) * np.linalg.norm(Y, axis=1)
    ratio = lhs / rhs

    ax.scatter(rhs, lhs, s=4, alpha=0.28, color=p.blue, edgecolor="none", label="random pairs")
    ax.scatter(rhs[:k], lhs[:k], s=10, alpha=0.85, color=p.amber, edgecolor="none",
               label="parallel pairs (equality)")

    hi = float(rhs.max()) * 1.02
    ax.plot([0, hi], [0, hi], color=p.red, linewidth=1.8,
            label=r"$|\langle x,y\rangle| = \|x\|\,\|y\|$")

    violations = int(np.sum(ratio > 1.0 + 1e-12))
    ax.text(
        0.03,
        0.95,
        f"pairs tested: {n}\n"
        f"largest ratio seen: {ratio.max():.12f}\n"
        f"pairs above the line: {violations}\n"
        f"median ratio (dimension {d}): {np.median(ratio):.4f}",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="top",
    )

    ax.set_xlabel(r"$\|x\|\,\|y\|$")
    ax.set_ylabel(r"$|\langle x, y\rangle|$")
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi)
    ax.set_aspect("equal")
    ax.legend(loc="lower right", fontsize=8.5)


def metric_changes_neighbours(fig, ax, p: Palette) -> None:
    """Four metrics, four different nearest neighbours."""
    fig.clear()
    axes = fig.subplots(1, 4, sharex=True, sharey=True)

    Sinv = np.linalg.inv(COV)
    th = np.linspace(0.0, 2.0 * np.pi, 721)
    dirs = np.stack([np.cos(th), np.sin(th)], axis=1)

    def unit_set(kind: str, radius: float) -> np.ndarray:
        if kind == "l1":
            r = 1.0 / np.sum(np.abs(dirs), axis=1)
        elif kind == "l2":
            r = np.ones(len(dirs))
        elif kind == "linf":
            r = 1.0 / np.max(np.abs(dirs), axis=1)
        else:
            r = 1.0 / np.sqrt(np.einsum("ij,jk,ik->i", dirs, Sinv, dirs))
        return dirs * (r * radius)[:, None]

    def dist(kind: str, V: np.ndarray) -> np.ndarray:
        if kind == "l1":
            return np.sum(np.abs(V), axis=1)
        if kind == "l2":
            return np.linalg.norm(V, axis=1)
        if kind == "linf":
            return np.max(np.abs(V), axis=1)
        return np.sqrt(np.einsum("ij,jk,ik->i", V, Sinv, V))

    kinds = [
        ("l1", r"$\ell_1$ (Manhattan)", p.amber),
        ("l2", r"$\ell_2$ (Euclidean)", p.blue),
        ("linf", r"$\ell_\infty$ (maximum)", p.green),
        ("maha", "Mahalanobis", p.purple),
    ]

    V = CANDIDATES - QUERY
    winners: list[int] = []

    for a, (kind, label, colour) in zip(axes, kinds):
        d = dist(kind, V)
        win = int(np.argmin(d))
        winners.append(win)

        # Draw the ball that just touches the winner, so "nearest" is visible.
        ball = unit_set(kind, float(d[win]))
        a.plot(ball[:, 0] + QUERY[0], ball[:, 1] + QUERY[1], color=colour, linewidth=1.8)
        a.fill(ball[:, 0] + QUERY[0], ball[:, 1] + QUERY[1], color=colour, alpha=0.09)

        a.scatter(CANDIDATES[:, 0], CANDIDATES[:, 1], s=26, color=p.muted, zorder=5)
        a.scatter(*CANDIDATES[win], s=78, color=colour, zorder=7, edgecolor=p.bg, linewidth=0.9)
        a.scatter(*QUERY, s=60, marker="x", color=p.fg, zorder=8, linewidth=1.8)

        a.annotate(
            f"#{win + 1}\nd = {d[win]:.3f}",
            xy=tuple(CANDIDATES[win]),
            xytext=(CANDIDATES[win][0] * 0.35 - 1.85, CANDIDATES[win][1] * 0.35 + 1.55),
            color=colour,
            fontsize=8,
            arrowprops=dict(arrowstyle="->", color=colour, linewidth=1.0),
        )

        a.set_title(label, color=colour, fontsize=10)
        a.set_xlim(-2.1, 2.1)
        a.set_ylim(-2.1, 2.1)
        a.set_aspect("equal")
        a.set_xlabel("$x_1$")

    axes[0].set_ylabel("$x_2$")
    distinct = len(set(winners))
    axes[0].text(
        0.04,
        0.04,
        f"{distinct} distinct winners\nout of 4 metrics",
        transform=axes[0].transAxes,
        color=p.fg,
        fontsize=8,
        va="bottom",
    )


FIGURES = [
    figure("cauchy-schwarz", cauchy_schwarz, size=(6.4, 5.4)),
    figure("metric-changes-neighbours", metric_changes_neighbours, size=(11.0, 3.4), axes=False),
]

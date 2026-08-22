"""Figures for *Norms*.

1. `unit-balls` — the sets ``{x : ||x||_p = 1}`` for p = 1, 2 and infinity, drawn
   on one pair of axes with a single probe vector measured by all three. Three
   rulers disagree about the length of the same arrow, which is the only way to
   make "there is more than one norm" feel like a fact rather than a formality.

2. `lasso-versus-ridge` — the geometry that produces sparsity. Elliptical loss
   contours of a real two-feature least-squares problem, with the l1 and l2
   constraint sets of equal *area* overlaid and each constrained optimum found
   by searching the boundary. Equal area rather than equal radius, because the
   l1 ball of a given radius sits strictly inside the l2 one and a reader is
   entitled to dismiss a corner won on a tighter budget. The l1 optimum lands on a corner, where one
   coefficient is exactly zero; the l2 optimum lands on a smooth arc, where
   neither is.

3. `coefficient-paths` — the same fact without geometry, over a sweep of the
   regularisation strength. Lasso coefficients hit exactly zero and stay there;
   ridge coefficients shrink towards zero and never arrive. Both paths are
   computed here (ridge in closed form, lasso by coordinate descent) so the
   zeros are measured rather than drawn.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

PROBE = np.array([1.6, 0.9])


def _pnorm(x: np.ndarray, p: float) -> float:
    if np.isinf(p):
        return float(np.max(np.abs(x)))
    return float(np.sum(np.abs(x) ** p) ** (1.0 / p))


def _ball(p: float, samples: int = 720) -> np.ndarray:
    """The unit ball of l_p in the plane, sampled by angle."""
    th = np.linspace(0.0, 2.0 * np.pi, samples)
    dirs = np.stack([np.cos(th), np.sin(th)], axis=1)
    if np.isinf(p):
        r = 1.0 / np.max(np.abs(dirs), axis=1)
    else:
        r = 1.0 / np.sum(np.abs(dirs) ** p, axis=1) ** (1.0 / p)
    return dirs * r[:, None]


# --------------------------------------------------------------------------- #
# The regression problem the last two figures share.
# --------------------------------------------------------------------------- #


def _problem(n: int = 60, seed: int = 11) -> tuple[np.ndarray, np.ndarray]:
    """Two correlated features and a target that mostly depends on the first.

    Correlation is the condition that makes the choice of penalty *matter*: with
    orthogonal columns both penalties shrink each coefficient independently and
    the geometric difference is invisible.
    """
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = 0.85 * x1 + 0.53 * rng.normal(size=n)
    X = np.stack([x1, x2], axis=1)
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    y = 1.6 * X[:, 0] + 0.35 * X[:, 1] + 0.45 * rng.normal(size=n)
    y = y - y.mean()
    return X, y


def _constrained_optimum(X: np.ndarray, y: np.ndarray, radius: float, p: float) -> np.ndarray:
    """Minimise the squared error over the boundary of the l_p ball of `radius`.

    A boundary search rather than a solver: the point of the figure is that the
    optimum sits on the boundary and *where* on the boundary, so computing it the
    same way it is drawn keeps the two honest with each other.
    """
    boundary = _ball(p, samples=20001) * radius
    resid = y[None, :] - boundary @ X.T
    sse = np.sum(resid**2, axis=1)
    return boundary[int(np.argmin(sse))]


def _ridge_path(X: np.ndarray, y: np.ndarray, lams: np.ndarray) -> np.ndarray:
    G = X.T @ X
    c = X.T @ y
    return np.stack([np.linalg.solve(G + lam * np.eye(X.shape[1]), c) for lam in lams])


def _lasso_path(X: np.ndarray, y: np.ndarray, lams: np.ndarray, iters: int = 500) -> np.ndarray:
    """Coordinate descent with soft thresholding, warm-started down the path."""
    n, d = X.shape
    col_sq = np.sum(X**2, axis=0)
    out = np.zeros((len(lams), d))
    w = np.zeros(d)
    for i, lam in enumerate(lams):
        for _ in range(iters):
            w_old = w.copy()
            for j in range(d):
                r = y - X @ w + X[:, j] * w[j]
                rho = X[:, j] @ r
                w[j] = np.sign(rho) * max(abs(rho) - lam, 0.0) / col_sq[j]
            if np.max(np.abs(w - w_old)) < 1e-12:
                break
        out[i] = w
    return out


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #


def unit_balls(fig, ax, p: Palette) -> None:
    """Three rulers, one arrow."""
    specs = [
        (1.0, p.amber, r"$p = 1$  (Manhattan)"),
        (2.0, p.blue, r"$p = 2$  (Euclidean)"),
        (np.inf, p.green, r"$p = \infty$  (maximum)"),
    ]

    for q, colour, label in specs:
        b = _ball(q)
        ax.plot(b[:, 0], b[:, 1], color=colour, linewidth=2.4, label=label)
        ax.fill(b[:, 0], b[:, 1], color=colour, alpha=0.07)

    ax.annotate(
        "",
        xy=tuple(PROBE),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=p.purple, linewidth=2.6),
    )
    ax.annotate(
        rf"$\mathbf{{x}} = ({PROBE[0]},\ {PROBE[1]})$",
        xy=tuple(PROBE),
        xytext=(PROBE[0] + 0.06, PROBE[1] + 0.10),
        color=p.purple,
        fontsize=10,
    )

    # The three measurements, printed in the same order as the legend.
    rows = "\n".join(
        f"  {name:<9} {_pnorm(PROBE, q):.4f}"
        for q, name in ((1.0, "l1"), (2.0, "l2"), (np.inf, "l-inf"))
    )
    ax.text(
        0.02,
        0.03,
        "one vector, three lengths:\n" + rows,
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="bottom",
    )

    # Where the l1 ball touches the axes: the corners that make Lasso sparse.
    ax.scatter([1, 0, -1, 0], [0, 1, 0, -1], s=34, color=p.amber, zorder=6)
    ax.annotate(
        "the only sharp points of the\ndiamond sit on the axes",
        xy=(0, 1),
        xytext=(-1.72, 1.24),
        color=p.amber,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.0),
    )

    ax.axhline(0, color=p.grid, linewidth=0.9)
    ax.axvline(0, color=p.grid, linewidth=0.9)
    ax.set_aspect("equal")
    ax.set_xlim(-1.85, 1.95)
    ax.set_ylim(-1.35, 1.55)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.legend(loc="upper right", fontsize=8.5)


def lasso_versus_ridge(fig, ax, p: Palette) -> None:
    """Loss contours against the two constraint sets of equal area."""
    X, y = _problem()
    ols = np.linalg.lstsq(X, y, rcond=None)[0]

    # Equal *area*, not equal radius. The l1 ball of radius t sits strictly
    # inside the l2 ball of the same radius, so comparing at equal radius lets a
    # reader dismiss the corner as an artefact of a tighter budget. Area 2t1^2
    # against pi*t2^2 gives t1 = t2 * sqrt(pi/2).
    r2 = 1.05
    r1 = r2 * np.sqrt(np.pi / 2.0)
    w_l1 = _constrained_optimum(X, y, r1, 1.0)
    w_l2 = _constrained_optimum(X, y, r2, 2.0)
    sse_l1 = float(np.sum((y - X @ w_l1) ** 2))
    sse_l2 = float(np.sum((y - X @ w_l2) ** 2))

    g = np.linspace(-0.55, 2.15, 320)
    h = np.linspace(-1.05, 1.35, 320)
    G, H = np.meshgrid(g, h)
    W = np.stack([G.ravel(), H.ravel()], axis=1)
    sse = np.sum((y[None, :] - W @ X.T) ** 2, axis=1).reshape(G.shape)

    ax.contour(
        G,
        H,
        sse,
        levels=np.quantile(sse, [0.002, 0.01, 0.03, 0.08, 0.16, 0.3, 0.5]),
        colors=[p.muted],
        linewidths=0.9,
        alpha=0.85,
    )

    for q, rad, colour, label in (
        (1.0, r1, p.amber, rf"$\|w\|_1 \leq {r1:.3f}$"),
        (2.0, r2, p.blue, rf"$\|w\|_2 \leq {r2:.2f}$"),
    ):
        b = _ball(q) * rad
        ax.plot(b[:, 0], b[:, 1], color=colour, linewidth=2.2, label=label)
        ax.fill(b[:, 0], b[:, 1], color=colour, alpha=0.08)

    ax.scatter(*ols, s=70, marker="*", color=p.green, zorder=7, label="unpenalised optimum")
    ax.scatter(*w_l1, s=52, color=p.amber, zorder=7, edgecolor=p.bg, linewidth=0.8)
    ax.scatter(*w_l2, s=52, color=p.blue, zorder=7, edgecolor=p.bg, linewidth=0.8)

    ax.annotate(
        f"$\\ell_1$: $w_2 = {w_l1[1]:+.4f}$",
        xy=tuple(w_l1),
        xytext=(w_l1[0] - 0.05, w_l1[1] - 0.62),
        color=p.amber,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1),
    )
    ax.annotate(
        f"$\\ell_2$: $w_2 = {w_l2[1]:+.4f}$",
        xy=tuple(w_l2),
        xytext=(w_l2[0] + 0.18, w_l2[1] + 0.42),
        color=p.blue,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.blue, linewidth=1.1),
    )

    ax.axhline(0, color=p.grid, linewidth=0.9)
    ax.axvline(0, color=p.grid, linewidth=0.9)
    ax.set_xlabel("$w_1$")
    ax.set_ylabel("$w_2$")
    ax.text(
        0.02,
        0.03,
        "both regions have area "
        + f"{2 * r1**2:.3f}"
        + "\n"
        + rf"$\ell_1$ squared error {sse_l1:.2f} using 1 feature"
        + "\n"
        + rf"$\ell_2$ squared error {sse_l2:.2f} using 2 features",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=8.5,
        va="bottom",
    )
    ax.set_title("equal-area budgets, two shapes", fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8.5)


def coefficient_paths(fig, ax, p: Palette) -> None:
    """Shrinkage against exact elimination, over a sweep of the penalty."""
    fig.clear()
    axes = fig.subplots(1, 2, sharey=True)

    X, y = _problem()
    lams = np.logspace(-2.0, 2.4, 60)

    ridge = _ridge_path(X, y, lams)
    lasso = _lasso_path(X, y, lams)

    for a, path, name in ((axes[0], lasso, "lasso  ($\\ell_1$)"), (axes[1], ridge, "ridge  ($\\ell_2$)")):
        a.plot(lams, path[:, 0], color=p.blue, linewidth=2.2, label="$w_1$")
        a.plot(lams, path[:, 1], color=p.amber, linewidth=2.2, label="$w_2$")
        a.axhline(0, color=p.muted, linewidth=1.0, linestyle=":")
        a.set_xscale("log")
        a.set_xlabel(r"penalty strength $\lambda$")
        a.set_title(name, fontsize=10.5)
        a.legend(loc="upper right", fontsize=8.5)

    # Exactly how many coefficients each method sets to exactly zero.
    lasso_zeros = int(np.sum(np.abs(lasso) == 0.0))
    ridge_zeros = int(np.sum(np.abs(ridge) == 0.0))
    zero2 = np.abs(lasso[:, 1]) == 0.0
    zero1 = np.abs(lasso[:, 0]) == 0.0
    first_zero = lams[np.argmax(zero2)] if zero2.any() else float("nan")
    first_zero1 = lams[np.argmax(zero1)] if zero1.any() else float("nan")

    axes[0].annotate(
        f"$w_2$ becomes exactly zero\nat $\\lambda \\approx {first_zero:.2f}$",
        xy=(first_zero, 0.0),
        xytext=(first_zero * 0.06, 0.55),
        color=p.amber,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1),
    )
    axes[0].text(
        0.03,
        0.05,
        f"exact zeros along the path: {lasso_zeros}"
        + "\n"
        + rf"$w_2$ gone at $\lambda$ {first_zero:.1f}, $w_1$ at {first_zero1:.0f}",
        transform=axes[0].transAxes,
        color=p.green,
        fontsize=8.5,
    )
    axes[1].text(
        0.03,
        0.05,
        f"exact zeros along the path: {ridge_zeros}\n"
        f"smallest $|w_2|$ reached: {np.min(np.abs(ridge[:, 1])):.2e}",
        transform=axes[1].transAxes,
        color=p.red,
        fontsize=8.5,
    )

    axes[0].set_ylabel("coefficient value")


FIGURES = [
    figure("unit-balls", unit_balls, size=(6.6, 5.2)),
    figure("lasso-versus-ridge", lasso_versus_ridge, size=(7.0, 5.0)),
    figure("coefficient-paths", coefficient_paths, size=(9.6, 4.0), axes=False),
]

"""Figures for *Systems of Linear Equations*.

1. `three-regimes` — the same pair of lines in the three possible relationships,
   with each system's determinant printed. The point the page makes from it is
   that a zero determinant tells you "not exactly one" without distinguishing
   "none" from "infinitely many": panels two and three both have determinant
   zero and completely different solution sets.

2. `overdetermined` — twelve data points and a fitted line, with every residual
   drawn. This is the case machine learning actually lives in: twelve equations,
   two unknowns, and no exact solution unless the points happen to be collinear.
   Drawing the residuals rather than just the line is the whole point — it shows
   that the misses cannot all be zero.
"""

import numpy as np

from _style import Palette, figure

# The three systems, matching the page's table exactly.
_CASES = [
    ("one solution", np.array([[1.0, 1.0], [1.0, -1.0]]), np.array([3.0, 1.0])),
    ("no solution", np.array([[1.0, 1.0], [1.0, 1.0]]), np.array([3.0, 1.0])),
    ("infinitely many", np.array([[1.0, 1.0], [2.0, 2.0]]), np.array([3.0, 6.0])),
]


def _line(ax, a, b, c, colour, label, lo=-1.0, hi=5.0, **kw):
    """Draw a*x1 + b*x2 = c over the window, handling the vertical case."""
    if abs(b) > 1e-12:
        x = np.linspace(lo, hi, 200)
        ax.plot(x, (c - a * x) / b, color=colour, label=label, **kw)
    else:
        ax.axvline(c / a, color=colour, label=label, **kw)


def three_regimes(fig, ax, p: Palette) -> None:
    """Two lines, in each of the three possible relationships."""
    fig.clear()
    axes = fig.subplots(1, 3, sharex=True, sharey=True)

    for a, (name, A, b) in zip(axes, _CASES):
        det = float(np.linalg.det(A))
        rank_A = np.linalg.matrix_rank(A)
        rank_Ab = np.linalg.matrix_rank(np.c_[A, b])

        # The second line is drawn dashed so a coincident pair is still visible
        # as two lines rather than reading as one.
        _line(a, A[0, 0], A[0, 1], b[0], p.amber, "equation 1", linewidth=2.4)
        _line(a, A[1, 0], A[1, 1], b[1], p.blue, "equation 2",
              linewidth=2.0, linestyle="--")

        if rank_A == rank_Ab == A.shape[1]:
            x = np.linalg.solve(A, b)
            a.plot(*x, marker="o", color=p.fg, markersize=8, zorder=5)
            a.annotate(f"({x[0]:g}, {x[1]:g})", xy=x, xytext=(x[0] + 0.25, x[1] + 0.45),
                       color=p.fg, fontsize=9)
        elif rank_A == rank_Ab:
            # The whole line is the solution set; thicken it to say so.
            _line(a, A[0, 0], A[0, 1], b[0], p.green, None, linewidth=6, alpha=0.28)

        a.set_title(name)
        a.set_xlabel("$x_1$")
        a.text(0.04, 0.05, f"$\\det = {det:g}$", transform=a.transAxes,
               color=p.muted, fontsize=9.5)
        a.text(0.04, 0.14,
               f"rk$(A)$={rank_A}, rk$(A|b)$={rank_Ab}",
               transform=a.transAxes, color=p.muted, fontsize=9)
        a.set_xlim(-1, 5)
        a.set_ylim(-1, 5)

    axes[0].set_ylabel("$x_2$")
    axes[0].legend(loc="upper right", fontsize=8.5)


def overdetermined(fig, ax, p: Palette) -> None:
    """Twelve equations, two unknowns, and every residual drawn."""
    rng = np.random.default_rng(7)
    t = np.linspace(0.2, 5.0, 12)
    y = 0.85 * t + 0.7 + rng.normal(0, 0.32, t.size)

    A = np.c_[np.ones_like(t), t]
    fit = np.linalg.lstsq(A, y, rcond=None)[0]
    pred = A @ fit
    resid = y - pred

    grid = np.linspace(0, 5.2, 100)
    ax.plot(grid, fit[0] + fit[1] * grid, color=p.amber, linewidth=2.4,
            label=f"least squares: $y = {fit[0]:.2f} + {fit[1]:.2f}t$")

    # Residuals first so the markers sit on top of them.
    for ti, yi, pi in zip(t, y, pred):
        ax.plot([ti, ti], [yi, pi], color=p.red, linewidth=1.4, alpha=0.9)
    ax.plot(t, y, "o", color=p.blue, markersize=6, label="data (12 constraints)")

    ax.set_xlabel("$t$")
    ax.set_ylabel("$y$")
    ax.text(0.03, 0.93,
            f"12 equations, 2 unknowns\nno residual is zero\nSSE = {resid @ resid:.3f}",
            transform=ax.transAxes, color=p.muted, fontsize=9.5, va="top")
    ax.legend(loc="lower right", fontsize=9)


FIGURES = [
    figure("three-regimes", three_regimes, size=(9.6, 3.5), axes=False),
    figure("overdetermined", overdetermined, size=(7.4, 4.2)),
]

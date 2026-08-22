"""Figures for *Affine Spaces*.

1. `subspace-versus-affine` — the same direction, two positions. On the left a
   line through the origin, with two of its points and their sum all lying on it.
   On the right the same line translated, with the sum of two of its points
   landing visibly off it. Drawing the *same* direction in both panels is the
   point: translation is the only difference, and it breaks both closure and the
   zero test at once.

2. `hyperplane-separates` — why codimension one matters. A separating line in the
   plane with its normal vector and the two half-spaces shaded, annotated with
   the sign of w-dot-x plus b. A hyperplane divides the space because it is one
   dimension short; a lower-dimensional object does not, because you can walk
   around it. That is the geometric basis of Chapter 12.
"""

import numpy as np

from _data import linearly_separable
from _style import Palette, figure

# The line used on the page's p5 sketch, so figure and sketch agree.
_X0 = np.array([-1.5, 1.4])
_U = np.array([1.6, 0.7])


def subspace_versus_affine(fig, ax, p: Palette) -> None:
    """A subspace and its translate, with closure tested in both."""
    fig.clear()
    axes = fig.subplots(1, 2, sharex=True, sharey=True)

    t = np.linspace(-3.0, 3.0, 200)

    panels = [
        (np.zeros(2), "subspace: through the origin", True),
        (_X0, "affine: the same line, translated", False),
    ]

    for a, (x0, title, is_sub) in zip(panels and axes, panels):
        line = x0[None, :] + t[:, None] * _U[None, :]
        colour = p.green if is_sub else p.red
        a.plot(line[:, 0], line[:, 1], color=colour, linewidth=2.4)

        # Two points on the line, and their sum.
        pt1 = x0 + 0.55 * _U
        pt2 = x0 - 1.10 * _U
        s = pt1 + pt2

        for q, name, col in ((pt1, "$u$", p.amber), (pt2, "$v$", p.purple)):
            a.annotate("", xy=q, xytext=(0, 0),
                       arrowprops=dict(arrowstyle="->", color=col, linewidth=1.9))
            a.annotate(name, xy=q, xytext=(q[0] + 0.14, q[1] + 0.14), color=col, fontsize=10)

        # Is the sum on the line? Solve both coordinates and compare.
        lams = (s - x0) / _U
        on = bool(np.allclose(lams, lams[0]))
        a.plot(*s, marker="o", color=p.green if on else p.red, markersize=10, zorder=6)
        a.annotate(f"$u+v$ {'on' if on else 'OFF'} the line",
                   xy=s, xytext=(s[0] - 2.4, s[1] + (0.5 if on else 0.9)),
                   color=p.green if on else p.red, fontsize=9,
                   arrowprops=dict(arrowstyle="->", color=p.green if on else p.red,
                                   linewidth=1.1))

        # The origin, and whether it is on the line.
        origin_lams = (np.zeros(2) - x0) / _U
        origin_on = bool(np.allclose(origin_lams, origin_lams[0]))
        a.plot(0, 0, marker="o", markerfacecolor=p.bg,
               markeredgecolor=p.fg, markeredgewidth=1.6, markersize=8, zorder=7)
        a.annotate("origin: " + ("ON" if origin_on else "not on"),
                   xy=(0, 0), xytext=(0.2, -1.5),
                   color=p.fg if origin_on else p.red, fontsize=9)

        a.set_title(title, color=colour, fontsize=10.5)
        a.set_xlabel("$x_1$")
        a.axhline(0, color=p.grid, linewidth=0.9)
        a.axvline(0, color=p.grid, linewidth=0.9)
        a.set_xlim(-5.2, 4.2)
        a.set_ylim(-2.4, 4.2)

    axes[0].set_ylabel("$x_2$")


def hyperplane_separates(fig, ax, p: Palette) -> None:
    """A separating hyperplane, its normal, and the two half-spaces."""
    X, y = linearly_separable(n=70, margin=0.9, seed=5)

    # The true boundary is x2 = x1, i.e. w = (-1, 1), b = 0. Offset it a little so
    # the figure is about an affine hyperplane rather than a subspace.
    w = np.array([-1.0, 1.0]) / np.sqrt(2.0)
    b = -0.25

    lo, hi = -3.4, 3.4
    grid = np.linspace(lo, hi, 300)
    # w1*x1 + w2*x2 + b = 0  ->  x2 = -(w1*x1 + b)/w2
    boundary = -(w[0] * grid + b) / w[1]

    ax.fill_between(grid, boundary, hi + 1, color=p.blue, alpha=0.10)
    ax.fill_between(grid, lo - 1, boundary, color=p.red, alpha=0.10)
    ax.plot(grid, boundary, color=p.amber, linewidth=2.6,
            label=r"hyperplane: $\mathbf{w}^\top\mathbf{x} + b = 0$")

    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=22, color=p.blue, label="$y = +1$")
    ax.scatter(X[y == -1, 0], X[y == -1, 1], s=22, color=p.red, label="$y = -1$")

    # The normal vector, anchored on the boundary.
    foot = np.array([0.0, -b / w[1]])
    ax.annotate("", xy=foot + 1.1 * w, xytext=foot,
                arrowprops=dict(arrowstyle="->", color=p.green, linewidth=2.4))
    ax.annotate(r"$\mathbf{w}$ (normal)", xy=foot + 1.1 * w,
                xytext=(foot[0] + 1.1 * w[0] - 1.5, foot[1] + 1.1 * w[1] + 0.28),
                color=p.green, fontsize=10)

    ax.text(0.03, 0.94, r"$\mathbf{w}^\top\mathbf{x} + b > 0$",
            transform=ax.transAxes, color=p.blue, fontsize=10)
    ax.text(0.66, 0.06, r"$\mathbf{w}^\top\mathbf{x} + b < 0$",
            transform=ax.transAxes, color=p.red, fontsize=10)

    # Confirm the split is genuine before claiming it.
    side = np.sign(X @ w + b)
    correct = int((side == y).sum())
    ax.text(0.03, 0.05,
            f"separates {correct} of {len(y)} points\n"
            r"in $\mathbb{R}^n$ this object has $n-1$ dimensions,"
            "\nwhich is why it has two sides",
            transform=ax.transAxes, color=p.muted, fontsize=8.5)

    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.legend(loc="upper right", fontsize=8.5)


FIGURES = [
    figure("subspace-versus-affine", subspace_versus_affine, size=(9.6, 4.0), axes=False),
    figure("hyperplane-separates", hyperplane_separates, size=(7.2, 5.0)),
]

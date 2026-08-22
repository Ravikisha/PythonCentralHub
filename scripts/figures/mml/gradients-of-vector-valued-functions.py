"""Figures for *Gradients of Vector-Valued Functions*.

1. `jacobian-area-magnifier` — the book's Figure 5.5. The unit square spanned by
   b1 = [1,0] and b2 = [0,1] maps to the parallelogram spanned by c1 = [-2,1] and
   c2 = [1,1] under the linear map of Eq 5.63-5.64, and the area grows by exactly
   |det J| = 3. The panel checks that against a Monte-Carlo area estimate, so the
   determinant claim is verified by counting rather than by quoting §4.1.

2. `nonlinear-jacobian-local` — the same claim for a NONLINEAR map, where it only
   holds in the limit. Squares of shrinking side are pushed through a nonlinear
   map and the measured area ratio is compared with |det J| at the corner. The
   ratio converges at first order in the side length, and the table shows it.

3. `jacobian-shapes` — Definition 5.6's shape rule, laid out for the functions the
   chapter actually differentiates. The point is that "the gradient" is an m x n
   matrix whose rows are indexed by the OUTPUT and columns by the input — the
   numerator layout — and that every special case in the chapter is that one rule.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Polygon

from _style import Palette, figure

# The book's Eq 5.63-5.64: y1 = -2 x1 + x2, y2 = x1 + x2.
A = np.array([[-2.0, 1.0], [1.0, 1.0]])


def jacobian_area_magnifier(fig, ax, p: Palette) -> None:
    """The unit square, its image, and |det J| as the area ratio."""
    unit = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    img = unit @ A.T

    ax.add_patch(Polygon(unit, closed=True, facecolor=p.blue, alpha=0.22,
                         edgecolor=p.blue, linewidth=2.0, label="unit square, area 1"))
    ax.add_patch(Polygon(img, closed=True, facecolor=p.amber, alpha=0.22,
                         edgecolor=p.amber, linewidth=2.0, label="its image"))

    for v, colour, name in ((np.array([1.0, 0.0]), p.blue, "$b_1$"),
                            (np.array([0.0, 1.0]), p.blue, "$b_2$")):
        ax.annotate("", xy=tuple(v), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.4))
        ax.annotate(name, xy=tuple(v), xytext=(v[0] * 1.1 + 0.06, v[1] * 1.1 + 0.06),
                    color=colour, fontsize=9.5)
    for v, name in ((A @ np.array([1.0, 0.0]), "$c_1 = Jb_1$"),
                    (A @ np.array([0.0, 1.0]), "$c_2 = Jb_2$")):
        ax.annotate("", xy=tuple(v), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=2.4))
        ax.annotate(name, xy=tuple(v), xytext=(v[0] * 1.06 - 0.35, v[1] * 1.06 + 0.12),
                    color=p.amber, fontsize=9.5)

    det = float(np.linalg.det(A))

    # An independent area estimate: sample the unit square, map it, and count
    # points landing inside the image parallelogram via barycentric coordinates
    # in the (c1, c2) basis. This never touches the determinant.
    rng = np.random.default_rng(7)
    box_lo = img.min(axis=0)
    box_hi = img.max(axis=0)
    pts = rng.uniform(box_lo, box_hi, size=(400000, 2))
    coeff = np.linalg.solve(A, pts.T).T          # coordinates in the (b1, b2) frame
    inside = np.all((coeff >= 0) & (coeff <= 1), axis=1)
    box_area = float(np.prod(box_hi - box_lo))
    mc_area = box_area * inside.mean()

    ax.set_aspect("equal")
    ax.set_xlim(-2.6, 1.8)
    ax.set_ylim(-0.4, 2.4)
    ax.set_xlabel("$y_1$")
    ax.set_ylabel("$y_2$")
    ax.axhline(0, color=p.grid, linewidth=0.9)
    ax.axvline(0, color=p.grid, linewidth=0.9)
    ax.set_title("$|\\det J|$ is the area magnifier (Figure 5.5)", fontsize=10.5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.text(
        0.98,
        0.02,
        f"J = [[-2, 1], [1, 1]]\n"
        f"det J          {det:+.4f}\n"
        f"|det J|        {abs(det):.4f}\n"
        f"Monte-Carlo    {mc_area:.4f}  ({inside.sum()} of {pts.shape[0]} hits)\n"
        f"gap            {abs(mc_area - abs(det)):.4f}\n"
        f"det is NEGATIVE, so orientation flips",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=p.fg,
        fontsize=7.6,
        family="monospace",
    )


def nonlinear_jacobian_local(fig, ax, p: Palette) -> None:
    """For a nonlinear map the determinant is only a LOCAL magnifier."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1]})

    # A nonlinear map with a clean Jacobian.
    F = lambda u, v: np.stack([u + 0.6 * v**2, v + 0.5 * u**2], axis=-1)
    J = lambda u, v: np.array([[1.0, 1.2 * v], [1.0 * u, 1.0]])

    # The base point matters. det J = 1 - 1.2*u*v vanishes on the hyperbola
    # u*v = 1/1.2 = 0.8333, and past it the map FOLDS: the image boundary crosses
    # itself and the shoelace formula returns the difference of two signed areas
    # rather than the area. Basing the squares at (0.8, 0.6) with side 0.4 puts
    # u*v up to 1.2, well past the fold, and the measured ratio comes out at 0.04
    # against a determinant of 0.424 -- not a convergence failure, a folded
    # polygon. Basing them here keeps every square on one side of the fold.
    u0, v0 = 0.4, 0.3
    sides = [0.4, 0.2, 0.1, 0.05, 0.02, 0.01]

    # Draw the largest and smallest squares and their images.
    for side, colour, alpha in ((0.4, p.red, 0.9), (0.1, p.amber, 0.9)):
        sq = np.array([[u0, v0], [u0 + side, v0], [u0 + side, v0 + side], [u0, v0 + side]])
        left.add_patch(Polygon(sq, closed=True, facecolor="none", edgecolor=colour,
                               linewidth=1.8, linestyle="--", alpha=alpha))
        t = np.linspace(0, 1, 60)
        edge = np.concatenate([
            np.stack([sq[0] + (sq[1] - sq[0]) * ti for ti in t]),
            np.stack([sq[1] + (sq[2] - sq[1]) * ti for ti in t]),
            np.stack([sq[2] + (sq[3] - sq[2]) * ti for ti in t]),
            np.stack([sq[3] + (sq[0] - sq[3]) * ti for ti in t]),
        ])
        im = F(edge[:, 0], edge[:, 1])
        left.plot(im[:, 0], im[:, 1], color=colour, linewidth=2.0,
                  label=f"image of a {side} square")

    left.plot(*F(np.array(u0), np.array(v0)), "o", color=p.green, markersize=7, zorder=5)
    left.set_aspect("equal")
    left.set_xlabel("$y_1$")
    left.set_ylabel("$y_2$")
    left.set_title("a nonlinear map bends the square", fontsize=10)
    left.legend(loc="upper left", fontsize=8)

    # Area ratio against side length, by the shoelace formula on the image edge.
    rows = []
    detJ = abs(float(np.linalg.det(J(u0, v0))))
    for side in sides:
        t = np.linspace(0, 1, 400)
        sq = np.array([[u0, v0], [u0 + side, v0], [u0 + side, v0 + side], [u0, v0 + side]])
        edge = np.concatenate([
            np.stack([sq[i] + (sq[(i + 1) % 4] - sq[i]) * ti for ti in t]) for i in range(4)
        ])
        im = F(edge[:, 0], edge[:, 1])
        x, y = im[:, 0], im[:, 1]
        area = 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
        rows.append((side, area / side**2, abs(area / side**2 - detJ)))

    right.loglog([r[0] for r in rows], [r[2] for r in rows], "o-", color=p.blue, linewidth=2.0,
                 label="$|$ratio $- |\\det J||$")
    ss = np.array([r[0] for r in rows])
    right.loglog(ss, ss * rows[0][2] / ss[0], color=p.muted, linewidth=1.0, linestyle=":",
                 label="$\\propto$ side")
    right.set_xlabel("side length of the square")
    right.set_ylabel("gap to $|\\det J|$")
    right.set_title("exact only in the limit, at first order", fontsize=10)
    right.legend(loc="lower right", fontsize=8)
    right.text(
        0.03,
        0.97,
        f"|det J| at ({u0}, {v0}) = {detJ:.6f}\n"
        f"the map folds where u*v = {1 / 1.2:.4f};\n"
        f"largest u*v used here is {(u0 + sides[0]) * (v0 + sides[0]):.4f}\n\n"
        + "  side    area/side^2      gap\n"
        + "\n".join(f"  {r[0]:<7} {r[1]:<14.6f} {r[2]:.2e}" for r in rows),
        transform=right.transAxes,
        va="top",
        color=p.fg,
        fontsize=7.2,
        family="monospace",
    )


def jacobian_shapes(fig, ax, p: Palette) -> None:
    """Definition 5.6's one rule, and every special case of it in the chapter."""
    ax.axis("off")

    rows = [
        ("f : R^n -> R^m", "df/dx", "m x n", "Definition 5.6, the general case"),
        ("f : R^n -> R", "df/dx", "1 x n", "Eq 5.40 — the gradient, a ROW vector"),
        ("f : R -> R^m", "df/dx", "m x 1", "a column: one output per row"),
        ("f : R -> R", "df/dx", "1 x 1", "the scalar derivative of §5.1"),
        ("f(x) = Ax,  A in R^{MxN}", "df/dx", "M x N", "Example 5.9: df/dx = A exactly"),
        ("f(X) = tr(AXB)", "df/dX", "1 x (E x F)", "Exercise 5.6: a scalar of a matrix"),
        ("f(X) = X^{-1}", "df/dX", "(n x n) x (n x n)", "§5.4: a fourth-order tensor"),
    ]

    ax.text(
        0.5,
        1.0,
        "one rule: rows are indexed by the output, columns by the input",
        transform=ax.transAxes,
        ha="center",
        va="top",
        color=p.fg,
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.93,
        "(the numerator layout; the transpose of this is the denominator layout, "
        "which the book does not use)",
        transform=ax.transAxes,
        ha="center",
        va="top",
        color=p.muted,
        fontsize=8.2,
    )

    y = 0.80
    ax.text(0.03, y, "function", color=p.muted, fontsize=8.6, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.36, y, "derivative", color=p.muted, fontsize=8.6, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.50, y, "shape", color=p.muted, fontsize=8.6, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.70, y, "where", color=p.muted, fontsize=8.6, fontweight="bold",
            transform=ax.transAxes)

    for i, (fn, dv, shape, where) in enumerate(rows):
        yy = 0.72 - i * 0.098
        colour = p.green if i == 1 else p.fg
        ax.text(0.03, yy, fn, color=colour, fontsize=8.8, family="monospace",
                transform=ax.transAxes)
        ax.text(0.36, yy, dv, color=colour, fontsize=8.8, family="monospace",
                transform=ax.transAxes)
        ax.text(0.50, yy, shape, color=p.amber, fontsize=8.8, family="monospace",
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.70, yy, where, color=p.muted, fontsize=8.0, transform=ax.transAxes)


FIGURES = [
    figure("jacobian-area-magnifier", jacobian_area_magnifier, size=(7.6, 5.6)),
    figure("nonlinear-jacobian-local", nonlinear_jacobian_local, size=(11.0, 4.8), axes=False),
    figure("jacobian-shapes", jacobian_shapes, size=(10.2, 5.0)),
]

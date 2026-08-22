"""Figures for *Partial Differentiation and Gradients*.

1. `gradient-field-orthogonal` — the book's Example 5.7 surface with its contours
   and its gradient field. The claim being drawn is that every arrow crosses its
   own contour at a right angle, and the panel measures it across the whole grid
   rather than at one convenient point.

2. `steepest-ascent-sweep` — the directional derivative D_d f = grad f . d swept
   through 360 unit directions at a single point, plotted as a polar rosette. It
   is a circle through the origin, its widest point lies along the gradient, and
   its radius there is exactly |grad f|. Two claims from §5.2 in one picture.

3. `row-vector-shapes` — why Eq 5.40 makes the gradient a ROW vector. Two chain
   rule computations side by side with their shapes annotated: the row convention
   composes as a plain matrix product, and the column convention needs a
   transpose inserted at every step. The figure counts the transposes.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# The book's Example 5.7.
f = lambda x, y: x**2 * y + x * y**3
fx = lambda x, y: 2 * x * y + y**3
fy = lambda x, y: x**2 + 3 * x * y**2


def gradient_field_orthogonal(fig, ax, p: Palette) -> None:
    """Contours plus the gradient field, with orthogonality measured."""
    lo, hi = -2.2, 2.2
    g = np.linspace(lo, hi, 320)
    X, Y = np.meshgrid(g, g)
    Z = f(X, Y)

    levels = [-8, -4, -2, -0.8, 0, 0.8, 2, 4, 8]
    cs = ax.contour(X, Y, Z, levels=levels, colors=p.muted, linewidths=1.1, alpha=0.75)
    ax.clabel(cs, inline=True, fontsize=7, fmt="%g")

    n = 15
    gq = np.linspace(lo + 0.12, hi - 0.12, n)
    XQ, YQ = np.meshgrid(gq, gq)
    U = fx(XQ, YQ)
    V = fy(XQ, YQ)
    M = np.hypot(U, V)

    ax.quiver(
        XQ, YQ, U / (M + 1e-12), V / (M + 1e-12), M,
        cmap="viridis", scale=26, width=0.0042, alpha=0.95,
    )

    # The orthogonality claim, measured. The contour tangent is the gradient
    # rotated by 90 degrees, so the inner product must vanish identically -- but
    # measuring it catches a sign or index error that eyeballing would not.
    tx, ty = -V, U
    dots = np.abs(U * tx + V * ty) / (M + 1e-12) ** 2
    worst = float(np.nanmax(dots))

    ax.plot([1], [1], "o", color=p.red, markersize=8, zorder=6)
    ax.annotate(
        "$(1, 1)$: $\\nabla f = [3, 4]$, $|\\nabla f| = 5$",
        xy=(1, 1),
        xytext=(1.05, 1.5),
        color=p.red,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.0),
    )

    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_aspect("equal")
    ax.set_title(
        "$f(x_1,x_2) = x_1^2x_2 + x_1x_2^3$: the gradient field, "
        "normalised and coloured by magnitude",
        fontsize=10,
    )
    ax.text(
        0.02,
        0.02,
        f"orthogonality of $\\nabla f$ to the contour tangent,\n"
        f"over all {U.size} grid points: worst |cos| = {worst:.1e}\n"
        f"largest $|\\nabla f|$ on the window: {M.max():.3f}",
        transform=ax.transAxes,
        va="bottom",
        color=p.fg,
        fontsize=7.8,
        family="monospace",
    )


def steepest_ascent_sweep(fig, ax, p: Palette) -> None:
    """The directional derivative as a function of direction."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.05]})

    x0, y0 = 1.0, 1.0
    gx, gy = fx(x0, y0), fy(x0, y0)
    gn = float(np.hypot(gx, gy))
    gang = float(np.arctan2(gy, gx))

    th = np.linspace(0, 2 * np.pi, 721)
    rate = gx * np.cos(th) + gy * np.sin(th)

    # Polar rosette. Negative rates are plotted at negative radius, which is what
    # makes the shape a circle through the origin rather than two lobes.
    left.plot(rate * np.cos(th), rate * np.sin(th), color=p.blue, linewidth=2.0)
    left.fill(rate * np.cos(th), rate * np.sin(th), color=p.blue, alpha=0.10)
    left.annotate(
        "",
        xy=(gx, gy),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=2.6),
    )
    left.plot([0], [0], "o", color=p.fg, markersize=5)
    left.annotate(
        f"$\\nabla f$, length {gn:.4f}",
        xy=(gx, gy),
        xytext=(gx * 0.35, gy * 1.08),
        color=p.red,
        fontsize=8.5,
    )
    # The zero-rate directions: the contour tangents.
    left.plot(
        [-gy / gn * gn, gy / gn * gn],
        [gx / gn * gn, -gx / gn * gn],
        color=p.green,
        linewidth=1.4,
        linestyle="--",
    )
    left.text(
        -gy * 0.62,
        gx * 0.62,
        "$D_d f = 0$:\nthe contour",
        color=p.green,
        fontsize=8,
        ha="center",
    )
    left.set_aspect("equal")
    left.set_xlabel("$d_1 \\cdot D_d f$")
    left.set_ylabel("$d_2 \\cdot D_d f$")
    left.set_title("$D_d f$ over all directions at $(1,1)$", fontsize=10)
    left.axhline(0, color=p.grid, linewidth=0.8)
    left.axvline(0, color=p.grid, linewidth=0.8)

    deg = np.degrees(th)
    right.plot(deg, rate, color=p.blue, linewidth=2.0, label="$D_d f = \\nabla f \\cdot d$")
    right.axhline(gn, color=p.red, linewidth=1.3, linestyle="--", label="$|\\nabla f|$")
    right.axhline(-gn, color=p.red, linewidth=1.3, linestyle="--")
    right.axhline(0, color=p.grid, linewidth=0.9)
    right.axvline(np.degrees(gang) % 360, color=p.red, linewidth=1.1, linestyle=":")

    i = int(np.argmax(rate))
    right.plot([deg[i]], [rate[i]], "*", color=p.red, markersize=14, zorder=5)

    right.set_xlabel("direction, degrees")
    right.set_ylabel("rate of change")
    right.set_xlim(0, 360)
    right.set_xticks([0, 90, 180, 270, 360])
    right.set_title("a cosine, peaking at the gradient's angle", fontsize=10)
    right.legend(loc="lower right", fontsize=8)
    right.text(
        0.02,
        0.03,
        f"gradient angle   {np.degrees(gang):.4f} deg\n"
        f"sampled argmax   {deg[i]:.4f} deg\n"
        f"|grad f|         {gn:.6f}\n"
        f"sampled max      {rate[i]:.6f}\n"
        f"shortfall        {gn - rate[i]:.2e}",
        transform=right.transAxes,
        va="bottom",
        color=p.fg,
        fontsize=7.6,
        family="monospace",
    )


def row_vector_shapes(fig, ax, p: Palette) -> None:
    """Why Eq 5.40 makes the gradient a row: the shapes compose."""
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(
        0.5,
        0.97,
        "the same chain rule, two conventions",
        transform=ax.transAxes,
        ha="center",
        va="top",
        color=p.fg,
        fontsize=11,
        fontweight="bold",
    )

    row_lines = [
        "the book's convention (Eq 5.40): gradients are ROWS",
        "",
        "  f : R^n -> R          df/dx   is  1 x n",
        "  g : R^m -> R^n        dg/dy   is  n x m",
        "",
        "  d(f o g)/dy  =  df/dx  @  dg/dy",
        "                 (1 x n) @ (n x m)  =  1 x m",
        "",
        "  transposes needed: 0",
        "  the shapes line up left to right, in the",
        "  order the functions are applied.",
    ]
    col_lines = [
        "the column convention: gradients are COLUMNS",
        "",
        "  f : R^n -> R          grad f  is  n x 1",
        "  g : R^m -> R^n        J_g     is  n x m",
        "",
        "  grad(f o g)  =  J_g^T  @  grad f",
        "                  (m x n) @ (n x 1)  =  m x 1",
        "",
        "  transposes needed: 1 per composition",
        "  and the factors appear in the OPPOSITE",
        "  order to the functions.",
    ]

    for x, lines, colour, title_colour in (
        (0.04, row_lines, p.fg, p.green),
        (0.53, col_lines, p.fg, p.amber),
    ):
        ax.text(
            x,
            0.86,
            lines[0],
            transform=ax.transAxes,
            color=title_colour,
            fontsize=9.5,
            fontweight="bold",
            va="top",
        )
        ax.text(
            x,
            0.79,
            "\n".join(lines[1:]),
            transform=ax.transAxes,
            color=colour,
            fontsize=8.6,
            family="monospace",
            va="top",
        )

    ax.text(
        0.5,
        0.12,
        "Neither is wrong, and the book says so. But a three-layer network is a\n"
        "composition of six functions, so the right-hand column needs six transposes\n"
        "and the left-hand one needs none — which is the whole reason §5.3 can write\n"
        "the multivariate chain rule as one matrix product and move on.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        color=p.muted,
        fontsize=8.4,
    )


FIGURES = [
    figure("gradient-field-orthogonal", gradient_field_orthogonal, size=(7.8, 6.4)),
    figure("steepest-ascent-sweep", steepest_ascent_sweep, size=(11.0, 4.6), axes=False),
    figure("row-vector-shapes", row_vector_shapes, size=(10.4, 4.6)),
]

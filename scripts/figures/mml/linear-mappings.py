"""Figures for *Linear Mappings*.

1. `three-transformations` — the book's Figure 2.10, reproduced. Four hundred
   points arranged in a square, then the same points under three transformation
   matrices from Equation 2.97: a 45-degree rotation, a stretch of two along the
   horizontal axis, and a combined reflection-rotation-stretch. Points are
   coloured by their original position so the reader can follow where each part
   of the square went — the book's own figure does the same, and without it the
   fourth panel is unreadable.

2. `rank-nullity` — the theorem as a conservation law. One stacked bar per
   matrix, image dimension below and kernel dimension above, and the total is
   always the number of columns. Drawing it this way makes the consequences
   immediate: a wide matrix cannot have a trivial kernel because the image is
   capped by the height, so a wide matrix is never injective.
"""

import numpy as np

from _style import Palette, figure

# Equation 2.97, exactly as the book gives them.
_A1 = np.array([[np.cos(np.pi / 4), -np.sin(np.pi / 4)],
                [np.sin(np.pi / 4),  np.cos(np.pi / 4)]])
_A2 = np.array([[2.0, 0.0], [0.0, 1.0]])
_A3 = 0.5 * np.array([[3.0, -1.0], [1.0, -1.0]])


def three_transformations(fig, ax, p: Palette) -> None:
    """400 points in a square, and their images under three matrices."""
    fig.clear()
    axes = fig.subplots(1, 4, sharex=True, sharey=True)

    # 20x20 = 400 points, matching the book's count.
    g = np.linspace(-1, 1, 20)
    G1, G2 = np.meshgrid(g, g)
    P = np.c_[G1.ravel(), G2.ravel()]

    # Colour by original vertical position so the mapping is traceable.
    shade = (P[:, 1] - P[:, 1].min()) / np.ptp(P[:, 1])
    colours = np.array([p.blue, p.amber])
    rgb = [colours[int(round(s))] for s in shade]

    panels = [
        (P, "(a) original", None),
        (P @ _A1.T, "(b) rotation by 45 deg", _A1),
        (P @ _A2.T, "(c) stretch by 2 along $x_1$", _A2),
        (P @ _A3.T, "(d) reflection, rotation, stretch", _A3),
    ]

    for a, (Q, title, M) in zip(axes, panels):
        a.scatter(Q[:, 0], Q[:, 1], s=4, c=rgb, linewidths=0)
        a.set_title(title, fontsize=10)
        a.set_xlabel("$x_1$")
        a.axhline(0, color=p.grid, linewidth=0.8)
        a.axvline(0, color=p.grid, linewidth=0.8)
        a.set_aspect("equal", adjustable="box")
        if M is not None:
            a.text(0.03, 0.04, f"det = {np.linalg.det(M):+.2f}",
                   transform=a.transAxes, color=p.muted, fontsize=8.5)

    axes[0].set_ylabel("$x_2$")
    axes[0].set_xlim(-2.4, 2.4)
    axes[0].set_ylim(-2.4, 2.4)


def rank_nullity(fig, ax, p: Palette) -> None:
    """Image and kernel dimensions stacked to the column count."""
    cases = [
        ("$2\\times4$\nrank 2", np.array([[1.0, 2.0, -1.0, 0.0],
                                          [1.0, 0.0,  0.0, 1.0]])),
        ("$3\\times1$\nrank 1", np.array([[1.0], [2.0], [3.0]])),
        ("$3\\times3$\nrank 2", np.array([[1.0, 0.0, 1.0],
                                          [0.0, 1.0, 1.0],
                                          [0.0, 0.0, 0.0]])),
        ("$3\\times3$\nrank 3", np.eye(3)),
        ("$2\\times5$\nrank 2", np.array([[1.0, 0.0, 1.0, 2.0, 3.0],
                                          [0.0, 1.0, 1.0, 1.0, 1.0]])),
    ]

    labels, im_dims, ker_dims, cols = [], [], [], []
    for name, A in cases:
        m, n = A.shape
        r = int(np.linalg.matrix_rank(A))
        labels.append(name)
        im_dims.append(r)
        ker_dims.append(n - r)
        cols.append(n)

    x = np.arange(len(labels))
    ax.bar(x, im_dims, color=p.blue, width=0.58, label=r"$\dim(\mathrm{Im}\,\Phi)$ = rank")
    ax.bar(x, ker_dims, bottom=im_dims, color=p.red, width=0.58,
           label=r"$\dim(\ker\Phi)$")

    for xi, (i, k, n) in enumerate(zip(im_dims, ker_dims, cols)):
        ax.text(xi, n + 0.12, f"total {n}\n= columns", ha="center",
                color=p.fg, fontsize=8.5)
        if i:
            ax.text(xi, i / 2, str(i), ha="center", va="center",
                    color=p.bg, fontsize=10, fontweight="bold")
        if k:
            ax.text(xi, i + k / 2, str(k), ha="center", va="center",
                    color=p.bg, fontsize=10, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("dimensions")
    ax.set_ylim(0, max(cols) + 1.4)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=9)
    ax.text(0.99, 0.02,
            "a WIDE matrix cannot have a trivial kernel:\n"
            "the image is capped by the height, so the rest\n"
            "of the input dimensions must be crushed",
            transform=ax.transAxes, color=p.muted, fontsize=8.2, ha="right")


FIGURES = [
    figure("three-transformations", three_transformations, size=(10.8, 3.4), axes=False),
    figure("rank-nullity", rank_nullity, size=(7.8, 4.4)),
]

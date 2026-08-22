"""Figures for *Inner Products*.

1. `spd-or-not` — the book's Example 3.4 as a surface rather than a claim. Two
   matrices that differ in a single entry, with the quadratic form x -> x^T A x
   drawn as filled contours over the plane. One is positive everywhere off the
   origin; the other has a whole wedge where it goes negative, and the book's
   witness x = (2, -3) is marked inside that wedge. Eigenvalues are printed
   because the sign pattern is the thing being tested.

2. `induced-unit-circles` — "unit length" is a statement about an inner product,
   not about a vector. The set of vectors of length one under three different
   inner products, with the vector (1, 1) marked: it measures sqrt(2) under the
   dot product and exactly 1 under the book's Equation 3.19, which is Example
   3.5 drawn instead of computed.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# Example 3.4: identical except for the lower-right entry.
A1 = np.array([[9.0, 6.0], [6.0, 5.0]])
A2 = np.array([[9.0, 6.0], [6.0, 3.0]])
WITNESS = np.array([2.0, -3.0])

# Example 3.5 / Equation 3.19, and one plain diagonal reweighting for contrast.
DOT = np.eye(2)
EQ319 = np.array([[1.0, -0.5], [-0.5, 1.0]])
DIAG = np.array([[2.0, 0.0], [0.0, 1.0]])


def _form(A: np.ndarray, G: np.ndarray, H: np.ndarray) -> np.ndarray:
    """x^T A x evaluated on a meshgrid."""
    return A[0, 0] * G**2 + (A[0, 1] + A[1, 0]) * G * H + A[1, 1] * H**2


def spd_or_not(fig, ax, p: Palette) -> None:
    """One entry apart: positive definite against indefinite."""
    fig.clear()
    axes = fig.subplots(1, 2, sharex=True, sharey=True)

    lim = 3.6
    g = np.linspace(-lim, lim, 400)
    G, H = np.meshgrid(g, g)

    for a, A, name in ((axes[0], A1, "A_1"), (axes[1], A2, "A_2")):
        Z = _form(A, G, H)
        eig = np.linalg.eigvalsh(A)
        definite = bool(np.all(eig > 0))

        # A symmetric colour scale, so "negative" is visible as a colour and not
        # only as a contour label.
        span = float(np.max(np.abs(Z)))
        a.contourf(G, H, Z, levels=np.linspace(-span, span, 41), cmap="RdBu_r", alpha=0.85)
        a.contour(G, H, Z, levels=[0.0], colors=[p.fg], linewidths=2.0)

        if not definite:
            # Shade the region where the "inner product" of x with itself is
            # negative, which no inner product may ever do.
            a.contourf(G, H, Z, levels=[-span, 0.0], colors=[p.red], alpha=0.22)
            a.scatter(*WITNESS, s=70, color=p.amber, zorder=8, edgecolor=p.bg, linewidth=1.0)
            value = float(WITNESS @ A @ WITNESS)
            a.annotate(
                rf"$\mathbf{{x}} = (2, -3)$, $\mathbf{{x}}^\top A_2 \mathbf{{x}} = {value:.0f}$",
                xy=tuple(WITNESS),
                xytext=(-3.3, -3.1),
                color=p.amber,
                fontsize=9,
                arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.2),
            )

        a.set_title(
            f"${name}$: eigenvalues {eig[0]:.3f}, {eig[1]:.3f}\n"
            + ("positive definite" if definite else "indefinite — not an inner product"),
            color=p.green if definite else p.red,
            fontsize=10,
        )
        a.set_xlabel("$x_1$")
        a.set_aspect("equal")
        a.grid(False)

    axes[0].set_ylabel("$x_2$")
    axes[0].text(
        0.03,
        0.04,
        "the heavy line marks where the form is zero",
        transform=axes[0].transAxes,
        color=p.fg,
        fontsize=8,
    )


def induced_unit_circles(fig, ax, p: Palette) -> None:
    """Three inner products, three different meanings of "length one"."""
    th = np.linspace(0.0, 2.0 * np.pi, 721)
    dirs = np.stack([np.cos(th), np.sin(th)], axis=1)

    specs = [
        (DOT, p.blue, r"dot product: $\|\mathbf{x}\| = 1$"),
        (EQ319, p.amber, r"Eq. 3.19: $x_1y_1-\frac{1}{2}(x_1y_2{+}x_2y_1)+x_2y_2$"),
        (DIAG, p.green, r"$\mathrm{diag}(2, 1)$: $x_1$ counts double"),
    ]

    probe = np.array([1.0, 1.0])

    for A, colour, label in specs:
        # Along each direction d, the vector r*d has squared length r^2 d^T A d,
        # so the unit set is r = 1/sqrt(d^T A d).
        q = np.einsum("ij,jk,ik->i", dirs, A, dirs)
        r = 1.0 / np.sqrt(q)
        pts = dirs * r[:, None]
        ax.plot(pts[:, 0], pts[:, 1], color=colour, linewidth=2.4, label=label)

    ax.annotate(
        "",
        xy=tuple(probe),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=p.purple, linewidth=2.6),
    )

    rows = []
    for A, _, name in ((DOT, None, "dot"), (EQ319, None, "Eq. 3.19"), (DIAG, None, "diag(2,1)")):
        rows.append(f"  {name:<10} {np.sqrt(probe @ A @ probe):.4f}")
    ax.text(
        0.02,
        0.03,
        "length of (1, 1):\n" + "\n".join(rows),
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="bottom",
    )
    ax.annotate(
        r"$(1, 1)$ lies exactly on the amber curve,"
        "\n"
        r"so under Eq. 3.19 it is a unit vector",
        xy=tuple(probe),
        xytext=(-1.55, 1.32),
        color=p.purple,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.purple, linewidth=1.0),
    )

    ax.axhline(0, color=p.grid, linewidth=0.9)
    ax.axvline(0, color=p.grid, linewidth=0.9)
    ax.set_aspect("equal")
    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.75, 1.75)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.legend(loc="lower right", fontsize=8)


FIGURES = [
    figure("spd-or-not", spd_or_not, size=(9.6, 4.4), axes=False),
    figure("induced-unit-circles", induced_unit_circles, size=(6.8, 5.4)),
]

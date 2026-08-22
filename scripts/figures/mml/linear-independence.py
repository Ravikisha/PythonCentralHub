"""Figures for *Linear Independence*.

1. `dependence-is-zero-area` — the absolute determinant of two 2-D vectors as the
   second rotates through a full turn. It touches zero **twice**, once when the
   vectors are aligned and once when they are anti-aligned, which is the visual
   form of the book's shortcut "if x_i = lambda x_j for any lambda, the set is
   dependent". The sign of lambda never mattered, and the plot says so.

2. `rank-tolerance` — where a reported rank actually comes from. A matrix built
   to be exactly rank 3 already has five nonzero singular values; the two
   trailing ones sit around 1e-16 rather than at zero. Sweeping a perturbation
   upwards walks them through numpy's default threshold, and the reported rank
   steps from 3 to 5 at the crossing. The step is a property of the threshold,
   not of the mathematics.
"""

import numpy as np

from _style import Palette, figure


def dependence_is_zero_area(fig, ax, p: Palette) -> None:
    """Determinant against the angle of the second vector."""
    v1 = np.array([2.2, 0.6])
    ang = np.linspace(0, 2 * np.pi, 900)
    v2 = 2.0 * np.c_[np.cos(ang), np.sin(ang)]
    det = v1[0] * v2[:, 1] - v1[1] * v2[:, 0]

    ax.plot(np.degrees(ang), np.abs(det), color=p.blue, linewidth=2.2,
            label=r"$|\det[\,x_1\ x_2\,]|$ = area of the parallelogram")
    ax.axhline(0, color=p.grid, linewidth=1)

    # The two zeros: where v2 is parallel or antiparallel to v1.
    a0 = np.arctan2(v1[1], v1[0])
    for k, (theta, note) in enumerate([(a0, "aligned\n$\\lambda > 0$"),
                                       (a0 + np.pi, "anti-aligned\n$\\lambda < 0$")]):
        d = np.degrees(theta % (2 * np.pi))
        ax.plot([d], [0], marker="o", color=p.red, markersize=8, zorder=5)
        ax.annotate(note, xy=(d, 0), xytext=(d + 12, 1.05 + 0.5 * k),
                    color=p.red, fontsize=9,
                    arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))

    ax.set_xlabel(r"angle of $x_2$ (degrees)")
    ax.set_ylabel("area spanned")
    ax.set_xlim(0, 360)
    ax.set_xticks([0, 90, 180, 270, 360])
    ax.legend(loc="upper right", fontsize=9)
    ax.text(0.02, 0.05, "zero area = linearly dependent",
            transform=ax.transAxes, color=p.muted, fontsize=9.5)


def rank_tolerance(fig, ax, p: Palette) -> None:
    """Singular values against perturbation size, with numpy's threshold drawn."""
    rng = np.random.default_rng(0)
    B = rng.standard_normal((6, 3))
    C = np.c_[B, B @ rng.standard_normal((3, 2))]     # exactly rank 3

    scales = np.logspace(-18, -8, 41)
    curves = []
    ranks = []
    for scale in scales:
        g = np.random.default_rng(1)
        Cn = C + scale * g.standard_normal(C.shape)
        curves.append(np.linalg.svd(Cn, compute_uv=False))
        ranks.append(np.linalg.matrix_rank(Cn))
    curves = np.array(curves)
    ranks = np.array(ranks)

    for k in range(curves.shape[1]):
        big = k < 3
        ax.loglog(scales, curves[:, k],
                  color=p.blue if big else p.red,
                  linewidth=2.0 if big else 1.8,
                  linestyle="-" if big else "--",
                  label=(r"$\sigma_1,\sigma_2,\sigma_3$ (the real rank)" if k == 0 else
                         r"$\sigma_4,\sigma_5$ (should be zero)" if k == 3 else None))

    m, n = C.shape
    tol = max(m, n) * np.finfo(float).eps * curves[0, 0]
    ax.axhline(tol, color=p.amber, linewidth=1.6, linestyle=":",
               label=rf"numpy default tolerance $\approx$ {tol:.1e}")

    # Mark where the reported rank first leaves 3.
    flip = np.argmax(ranks > 3)
    if ranks[flip] > 3:
        ax.axvline(scales[flip], color=p.green, linewidth=1.4, linestyle="--")
        ax.annotate(f"reported rank steps\n3 -> {ranks[flip]} here",
                    xy=(scales[flip], tol), xytext=(scales[flip] / 300, tol * 300),
                    color=p.green, fontsize=9,
                    arrowprops=dict(arrowstyle="->", color=p.green, linewidth=1.1))

    ax.set_xlabel("size of the perturbation added to an exactly rank-3 matrix")
    ax.set_ylabel("singular value")
    ax.legend(loc="lower right", fontsize=8.5)


FIGURES = [
    figure("dependence-is-zero-area", dependence_is_zero_area, size=(7.4, 4.0)),
    figure("rank-tolerance", rank_tolerance, size=(7.6, 4.4)),
]

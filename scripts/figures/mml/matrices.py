"""Figures for *Matrices*.

1. `matrix-two-faces` — the same object read as data and as an action. Left, a
   small matrix rendered as a heat map with its entries printed: the matrix is
   what is being looked at. Right, a square lattice and its image under that
   same matrix, with the two column vectors drawn: the matrix is what is doing
   the looking. Using *one* matrix for both panels is the whole point.

2. `multiply-cost` — wall-clock time for an n-by-n product, naive triple loop
   against ``@``, with an n-cubed reference line. Both are cubic; the gap is
   constant factors. The page uses this to separate asymptotic cost from
   wall-clock cost, and to motivate section 2.3's remark that Gaussian
   elimination is impractical at scale regardless of who writes the loop.
"""

import time

import numpy as np

from _data import digit_matrix
from _style import Palette, figure

# The matrix used on the page's MatrixLab, so the figure and the lab agree.
_M = np.array([[2.0, 1.0], [0.0, 1.5]])


def matrix_two_faces(fig, ax, p: Palette) -> None:
    """Data on the left, action on the right, same matrix."""
    fig.clear()
    axes = fig.subplots(1, 2, width_ratios=[1.0, 1.25])

    # ---- data: a small image, entries printed ---------------------------
    a = axes[0]
    img = digit_matrix(8)
    a.imshow(img, cmap="gray", vmin=0, vmax=1)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            a.text(j, i, f"{img[i, j]:.2f}"[1:], ha="center", va="center",
                   fontsize=6.0, color=p.bg if img[i, j] > 0.6 else p.fg)
    a.set_title("as DATA: a grid of numbers")
    a.set_xticks([])
    a.set_yticks([])
    a.grid(False)

    # ---- action: a lattice and its image --------------------------------
    a = axes[1]
    g = np.arange(-2, 2.01, 0.5)
    for v in g:                                      # original lattice, faint
        a.plot([-2, 2], [v, v], color=p.muted, linewidth=0.6, alpha=0.35)
        a.plot([v, v], [-2, 2], color=p.muted, linewidth=0.6, alpha=0.35)
    for v in g:                                      # transformed lattice
        for p0, p1 in (([-2, v], [2, v]), ([v, -2], [v, 2])):
            q0, q1 = _M @ np.array(p0), _M @ np.array(p1)
            a.plot([q0[0], q1[0]], [q0[1], q1[1]], color=p.blue,
                   linewidth=0.9, alpha=0.7)

    # The unit square and its image.
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]).T
    a.plot(sq[0], sq[1], color=p.muted, linewidth=1.4, linestyle="--")
    im = _M @ sq
    a.fill(im[0], im[1], color=p.amber, alpha=0.22)
    a.plot(im[0], im[1], color=p.amber, linewidth=1.8)

    for k, colour, name in ((0, p.blue, r"$Ae_1$"), (1, p.green, r"$Ae_2$")):
        a.annotate("", xy=_M[:, k], xytext=(0, 0),
                   arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.2))
        a.annotate(name, xy=_M[:, k], xytext=(_M[0, k] + 0.12, _M[1, k] + 0.12),
                   color=colour, fontsize=10)

    a.set_title("as ACTION: where the basis vectors go")
    a.set_xlim(-2.6, 4.2)
    a.set_ylim(-3.2, 3.6)
    a.set_xlabel("$x_1$")
    a.set_ylabel("$x_2$")
    a.axhline(0, color=p.grid, linewidth=0.9)
    a.axvline(0, color=p.grid, linewidth=0.9)
    a.text(0.03, 0.05, f"det = {np.linalg.det(_M):g}",
           transform=a.transAxes, color=p.muted, fontsize=9.5)


def _naive_matmul(A, B):
    """The definition, written out. Deliberately the slow way."""
    n, k = A.shape[0], B.shape[1]
    m = A.shape[1]
    C = np.zeros((n, k))
    for i in range(n):
        for j in range(k):
            s = 0.0
            for l in range(m):
                s += A[i, l] * B[l, j]
            C[i, j] = s
    return C


def multiply_cost(fig, ax, p: Palette) -> None:
    """Naive triple loop against the BLAS-backed operator."""
    rng = np.random.default_rng(1)
    sizes_naive = [8, 12, 18, 26, 38, 56, 80]
    sizes_fast = [8, 16, 32, 64, 128, 256, 512]

    def timed(fn, n, repeats):
        A = rng.standard_normal((n, n))
        B = rng.standard_normal((n, n))
        best = float("inf")
        for _ in range(repeats):
            t0 = time.perf_counter()
            fn(A, B)
            best = min(best, time.perf_counter() - t0)
        return best

    t_naive = [timed(_naive_matmul, n, 1) for n in sizes_naive]
    t_fast = [timed(lambda A, B: A @ B, n, 5) for n in sizes_fast]

    ax.loglog(sizes_naive, t_naive, "o-", color=p.red, linewidth=2,
              markersize=4, label="naive triple loop (Python)")
    ax.loglog(sizes_fast, t_fast, "s-", color=p.blue, linewidth=2,
              markersize=4, label="A @ B (BLAS)")

    # An n-cubed reference, anchored to the naive curve's first point.
    ref_n = np.array(sizes_naive, dtype=float)
    ax.loglog(ref_n, t_naive[0] * (ref_n / ref_n[0]) ** 3, ":",
              color=p.muted, linewidth=1.2, label=r"reference slope $n^3$")

    ax.set_xlabel("matrix size $n$")
    ax.set_ylabel("time for one product (s)")
    ax.legend(loc="upper left", fontsize=9)


FIGURES = [
    figure("matrix-two-faces", matrix_two_faces, size=(9.6, 4.0), axes=False),
    figure("multiply-cost", multiply_cost, size=(7.4, 4.2)),
]

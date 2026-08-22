"""Figures for *Matrix Approximation*.

1. `rank-one-pieces` — the book's Figures 4.11 and 4.12 in one panel set. The top
   row shows the first five rank-1 outer products with their singular values; the
   bottom row shows the cumulative reconstructions. Each rank-1 piece has the
   grid-like structure the book points out, because an outer product is one column
   pattern times one row pattern and nothing else.

2. `eckart-young-measured` — Theorem 4.25, tested rather than quoted. For many
   random matrices and every k, the measured spectral norm of A - Ahat(k) is
   plotted against sigma_{k+1}; the points land on the diagonal. Random rank-k
   matrices are plotted alongside and sit strictly above it, which is the
   optimality half of the theorem.

3. `compression-tradeoff` — the storage arithmetic the book does for Stonehenge,
   generalised. Numbers stored against reconstruction error for every k, with the
   exact rank marked and the rank at which a factorisation stops saving anything
   marked separately. For a square matrix a factorisation only saves when
   k < n/2 roughly, and this image is exact long before that.
"""

from __future__ import annotations

import numpy as np

from _data import blocks_image
from _style import Palette, figure

IMG = blocks_image(size=64)


def rank_one_pieces(fig, ax, p: Palette) -> None:
    """Five rank-1 pieces, and the five partial sums they build."""
    fig.clear()
    gs = fig.add_gridspec(2, 6, wspace=0.08, hspace=0.28)

    U, s, Vt = np.linalg.svd(IMG)

    orig = fig.add_subplot(gs[0, 0])
    orig.imshow(IMG, cmap="gray", vmin=0, vmax=1)
    orig.set_title("original", fontsize=9)
    orig.set_xticks([]); orig.set_yticks([]); orig.grid(False)

    rank = int(np.linalg.matrix_rank(IMG))
    total = fig.add_subplot(gs[1, 0])
    total.axis("off")
    total.text(
        0.0, 0.5,
        f"{IMG.shape[0]}×{IMG.shape[1]}\n"
        f"rank {rank}\n"
        f"$\\sigma_1$ = {s[0]:.2f}\n"
        f"$\\sigma_6/\\sigma_1$ = {s[5] / s[0]:.4f}",
        transform=total.transAxes, color=p.fg, fontsize=8, va="center",
    )

    acc = np.zeros_like(IMG)
    for i in range(5):
        piece = s[i] * np.outer(U[:, i], Vt[i])
        acc = acc + piece

        a = fig.add_subplot(gs[0, i + 1])
        a.imshow(piece, cmap="gray")
        a.set_title(f"$A_{i + 1}$, $\\sigma_{i + 1}$ = {s[i]:.2f}", fontsize=8.5)
        a.set_xticks([]); a.set_yticks([]); a.grid(False)

        b = fig.add_subplot(gs[1, i + 1])
        b.imshow(acc, cmap="gray", vmin=0, vmax=1)
        err = float(np.linalg.norm(IMG - acc, 2))
        b.set_title(f"$\\hat{{A}}({i + 1})$, err {err:.3f}", fontsize=8.5)
        b.set_xticks([]); b.set_yticks([]); b.grid(False)

    fig.text(
        0.5, 0.02,
        "Top: the individual rank-1 pieces $\\sigma_i u_i v_i^\\top$, each a single "
        "column pattern times a single row pattern — which is why they look like grids. "
        "Bottom: the running sums.",
        ha="center", color=p.muted, fontsize=8.5,
    )


def eckart_young_measured(fig, ax, p: Palette) -> None:
    """The SVD truncation is optimal, and its error is the next singular value."""
    rng = np.random.default_rng(17)

    svd_x, svd_y, rnd_x, rnd_y = [], [], [], []
    worst_svd = 0.0
    best_random_ratio = np.inf

    for _ in range(90):
        m, n = int(rng.integers(4, 10)), int(rng.integers(4, 10))
        A = rng.normal(size=(m, n))
        U, s, Vt = np.linalg.svd(A)
        r = min(m, n)
        for k in range(1, r):
            Ahat = sum(s[i] * np.outer(U[:, i], Vt[i]) for i in range(k))
            measured = float(np.linalg.norm(A - Ahat, 2))
            svd_x.append(s[k])
            svd_y.append(measured)
            worst_svd = max(worst_svd, abs(measured - s[k]))

            # A random rank-k competitor, scaled to a comparable size.
            L = rng.normal(size=(m, k))
            R = rng.normal(size=(k, n))
            B = L @ R
            B = B * (np.linalg.norm(Ahat) / max(np.linalg.norm(B), 1e-12))
            rnd = float(np.linalg.norm(A - B, 2))
            rnd_x.append(s[k])
            rnd_y.append(rnd)
            best_random_ratio = min(best_random_ratio, rnd / max(measured, 1e-12))

    ax.scatter(rnd_x, rnd_y, s=6, alpha=0.25, color=p.red, edgecolor="none",
               label="a random rank-$k$ matrix")
    ax.scatter(svd_x, svd_y, s=9, alpha=0.7, color=p.green, edgecolor="none",
               label=r"SVD truncation $\hat{A}(k)$")

    hi = max(max(svd_x), max(svd_y)) * 1.05
    ax.plot([0, hi], [0, hi], color=p.fg, linewidth=1.4,
            label=r"$\|A - \hat{A}(k)\|_2 = \sigma_{k+1}$")

    ax.text(
        0.03, 0.95,
        f"truncations tested: {len(svd_x)}\n"
        f"largest |measured - sigma_(k+1)|: {worst_svd:.2e}\n"
        f"best random competitor was still {best_random_ratio:.2f}x worse\n"
        f"random competitors below the line: "
        f"{int(sum(1 for x, y in zip(rnd_x, rnd_y) if y < x - 1e-9))}",
        transform=ax.transAxes, color=p.fg, fontsize=8.5,
        family="monospace", va="top",
    )

    ax.set_xlabel(r"$\sigma_{k+1}$")
    ax.set_ylabel(r"measured $\|A - B\|_2$")
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi * 1.9)
    ax.set_title("no rank-$k$ matrix does better, and the SVD hits the bound exactly",
                 fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8.5)


def compression_tradeoff(fig, ax, p: Palette) -> None:
    """Numbers stored against error, with the break-even rank marked."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    U, s, Vt = np.linalg.svd(IMG)
    m, n = IMG.shape
    r = int(np.linalg.matrix_rank(IMG))
    ks = np.arange(1, min(m, n) + 1)

    stored = ks * (m + n + 1)
    errors = []
    fro = []
    for k in ks:
        Ahat = (U[:, :k] * s[:k]) @ Vt[:k]
        errors.append(float(np.linalg.norm(IMG - Ahat, 2)))
        fro.append(float(np.linalg.norm(IMG - Ahat, "fro")))
    errors = np.array(errors)
    fro = np.array(fro)

    left.semilogy(ks, np.maximum(errors, 1e-18), color=p.blue, linewidth=2.0,
                  label=r"spectral norm $\|A - \hat{A}(k)\|_2$")
    left.semilogy(ks, np.maximum(fro, 1e-18), color=p.amber, linewidth=1.6,
                  linestyle="--", label="Frobenius norm")
    left.semilogy(ks[:-1], np.maximum(s[1:len(ks)], 1e-18), color=p.green, linewidth=1.2,
                  linestyle=":", label=r"$\sigma_{k+1}$")
    left.axvline(r, color=p.red, linewidth=1.2, linestyle="--")
    left.annotate(f"rank {r}: exact", xy=(r, errors[min(r, len(errors)) - 1]),
                  xytext=(r - 17, max(errors) * 0.02), color=p.red, fontsize=8.5,
                  arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.0))
    left.set_xlabel("rank $k$")
    left.set_ylabel("reconstruction error")
    left.set_title(f"error against rank, {m}×{n} image", fontsize=10.5)
    left.legend(loc="lower left", fontsize=8)

    right.plot(stored, np.maximum(errors, 1e-18), color=p.blue, linewidth=2.0,
               marker="o", markersize=2.8)
    right.set_yscale("log")
    right.axvline(m * n, color=p.red, linewidth=1.4, linestyle="--")
    break_even = int(np.searchsorted(stored, m * n) + 1)
    right.annotate(
        "storing the matrix outright costs "
        + f"{m * n}"
        + "\n"
        + f"a rank-{break_even} factorisation costs the same,"
        + "\n"
        + f"so only $k < {break_even}$ saves anything —"
        + "\n"
        + f"and this image is already exact at $k = {r}$",
        xy=(m * n, errors[min(break_even, len(errors)) - 1]),
        xytext=(m * n * 0.13, max(errors) * 0.05),
        color=p.red, fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.0),
    )
    right.scatter([stored[r - 1]], [max(errors[r - 1], 1e-18)], s=80, marker="*",
                  color=p.green, zorder=6)
    right.annotate(
        f"exact at rank {r}: {stored[r - 1]} numbers, "
        + f"{100.0 * stored[r - 1] / (m * n):.1f}% of the original",
        xy=(stored[r - 1], max(errors[r - 1], 1e-18)),
        xytext=(stored[r - 1] + 0.06 * m * n, max(errors) * 1e-3),
        color=p.green, fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.green, linewidth=1.0),
    )
    for k_mark in (1, 4, 12):
        i = k_mark - 1
        right.annotate(
            f"k={k_mark}: {stored[i]} numbers\n"
            f"{100.0 * stored[i] / (m * n):.1f}% of the original",
            xy=(stored[i], errors[i]),
            xytext=(stored[i] + 0.09 * m * n, errors[i] * 2.4),
            color=p.amber, fontsize=8,
            arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=0.9),
        )
    right.set_xlabel("numbers stored: $k(m + n + 1)$")
    right.set_ylabel("spectral-norm error")
    right.set_title("the storage-error trade-off", fontsize=10.5)


FIGURES = [
    figure("rank-one-pieces", rank_one_pieces, size=(11.4, 4.2), axes=False),
    figure("eckart-young-measured", eckart_young_measured, size=(7.6, 5.2)),
    figure("compression-tradeoff", compression_tradeoff, size=(9.8, 4.4), axes=False),
]

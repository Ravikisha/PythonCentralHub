"""Figures for *Basis and Rank*.

1. `rank-tells-you-everything` — four matrices of decreasing rank, each with its
   singular-value spectrum and the five quantities the rank determines: image
   dimension, null-space dimension, full rank or not, invertible or not. The
   point is that one integer fixes all of them.

2. `effective-dimension` — the gap between the two notions of dimension, on real
   data. The 8x8 digit images live in 64 dimensions and their rank is 61, because
   three border pixels are blank in every single image. That is what exact
   dependence looks like in practice: dull. The interesting redundancy is soft —
   21 components carry 90% of the variance — and rank cannot see it at all,
   because those directions are small rather than zero.

   This is the figure Chapter 10 is built on, so it is worth its space here.
"""

import numpy as np

from _data import digits_dataset
from _style import Palette, figure


def rank_tells_you_everything(fig, ax, p: Palette) -> None:
    """Four spectra, annotated with everything the rank decides."""
    fig.clear()
    axes = fig.subplots(1, 4, sharey=True)

    rng = np.random.default_rng(4)
    base = rng.standard_normal((4, 4))

    cases = []
    for r in (4, 3, 2, 1):
        # Build an exactly-rank-r 4x4 from a truncated SVD of the same base, so
        # the four panels are the same matrix progressively degraded rather than
        # four unrelated random ones.
        U, s, Vt = np.linalg.svd(base)
        s2 = s.copy()
        s2[r:] = 0.0
        cases.append((r, U @ np.diag(s2) @ Vt))

    for a, (r_target, A) in zip(axes, cases):
        sv = np.linalg.svd(A, compute_uv=False)
        r = np.linalg.matrix_rank(A)
        m, n = A.shape

        colours = [p.blue if v > 1e-10 else p.red for v in sv]
        a.bar(np.arange(1, len(sv) + 1), np.maximum(sv, 1e-3), color=colours, width=0.62)
        a.set_yscale("log")
        a.set_ylim(1e-3, 10)
        a.set_xticks(np.arange(1, len(sv) + 1))
        a.set_xlabel("index $i$")
        a.set_title(f"rank {r}", color=p.fg, fontsize=11)

        lines = [
            f"image dim      {r}",
            f"null-space dim {n - r}",
            f"full rank      {'yes' if r == min(m, n) else 'no'}",
            f"invertible     {'yes' if (m == n and r == n) else 'no'}",
        ]
        a.text(0.04, 0.04, "\n".join(lines), transform=a.transAxes,
               color=p.muted, fontsize=8.2, family="monospace", va="bottom")

    axes[0].set_ylabel(r"singular value $\sigma_i$")
    axes[0].text(0.04, 0.96, "red bars are\nzero (floored\nfor the log axis)",
                 transform=axes[0].transAxes, color=p.red, fontsize=8, va="top")


def effective_dimension(fig, ax, p: Palette) -> None:
    """Rank versus the dimension that actually carries the variance."""
    X, _, source = digits_dataset()
    sv = np.linalg.svd(X, compute_uv=False)
    cum = np.cumsum(sv**2) / np.sum(sv**2)
    r = np.linalg.matrix_rank(X)
    n90 = int(np.searchsorted(cum, 0.90)) + 1
    n95 = int(np.searchsorted(cum, 0.95)) + 1
    idx = np.arange(1, sv.size + 1)

    ax.semilogy(idx, np.maximum(sv, 1e-3), color=p.blue, linewidth=2,
                label=r"singular values $\sigma_i$")
    ax.axvline(r, color=p.red, linewidth=1.6, linestyle="--")
    ax.annotate(f"rank = {r} of {sv.size}\n(three pixels are blank\nin every image)",
                xy=(r, 3.0), xytext=(r - 30, 0.02),
                color=p.red, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))

    ax.axvline(n90, color=p.green, linewidth=1.6, linestyle=":")
    ax.annotate(f"{n90} components\ncarry 90% of the variance",
                xy=(n90, 60), xytext=(n90 + 6, 300),
                color=p.green, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=p.green, linewidth=1.1))

    ax.set_xlabel("component index")
    ax.set_ylabel(r"singular value $\sigma_i$ (log scale)")
    ax.set_ylim(1e-3, 2e3)

    # Cumulative variance on a twin axis: the reason "effective dimension" is
    # not an integer.
    ax2 = ax.twinx()
    ax2.plot(idx, cum, color=p.amber, linewidth=1.8, label="cumulative variance")
    ax2.set_ylabel("cumulative fraction of variance", color=p.amber)
    ax2.tick_params(axis="y", colors=p.amber)
    ax2.set_ylim(0, 1.02)
    ax2.grid(False)
    ax2.axhline(0.90, color=p.green, linewidth=0.9, linestyle=":")

    ax.text(0.985, 0.06,
            f"{source}\n{X.shape[0]} images, {X.shape[1]} pixels\n"
            f"90% at {n90} components, 95% at {n95}",
            transform=ax.transAxes, color=p.muted, fontsize=8, ha="right")

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8.5)


FIGURES = [
    figure("rank-tells-you-everything", rank_tells_you_everything, size=(10.6, 3.6), axes=False),
    figure("effective-dimension", effective_dimension, size=(7.8, 4.6)),
]

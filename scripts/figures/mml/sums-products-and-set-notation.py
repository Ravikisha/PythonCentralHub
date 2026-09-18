"""Figures for *Sums, Products and Set Notation*.

1. `double-sum-as-a-grid` — why swapping constant limits is free and swapping a
   triangular limit is not. Rows-then-columns and columns-then-rows agree on the
   full block; on the lower triangle, swapping the symbols WITHOUT rewriting the
   limits silently collects the upper triangle instead and returns a different
   number.

2. `log-turns-products-into-sums` — the reason every likelihood in the book is
   logged. A product of N small probabilities reaches exactly 0.0 in float64 at
   a measurable N, taking the gradient with it; the sum of logarithms is still a
   perfectly ordinary number there.

3. `constant-out-of-a-product` — Rule 1 does not transfer to products. Pulling a
   constant out of N factors leaves c^N, not c, and the plot shows how fast the
   two answers separate for the Gaussian normalising constant.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from _style import Palette, figure


def _grid(n: int = 4) -> np.ndarray:
    """a_ij = 10i + j. Deliberately asymmetric: on a symmetric grid the upper and
    lower triangles would agree and the swapping bug would be invisible."""
    i = np.arange(1, n + 1)[:, None]
    j = np.arange(1, n + 1)[None, :]
    return 10 * i + j


def _cells(ax, a, mask, p: Palette, title, subtitle, title_color=None):
    n = a.shape[0]
    for r in range(n):
        for c in range(n):
            on = bool(mask[r, c])
            ax.add_patch(Rectangle(
                (c, n - 1 - r), 1, 1,
                facecolor=(p.amber if on else p.grid),
                alpha=(0.30 if on else 0.55),
                edgecolor=(p.amber if on else p.grid),
                linewidth=1.4,
            ))
            ax.text(c + 0.5, n - 1 - r + 0.5, str(a[r, c]),
                    ha="center", va="center", fontsize=9.5, family="monospace",
                    color=(p.fg if on else p.muted))
    for r in range(n):
        ax.text(-0.28, n - 1 - r + 0.5, f"$i={r + 1}$", ha="right", va="center",
                fontsize=8, color=p.muted)
    for c in range(n):
        ax.text(c + 0.5, -0.22, f"$j={c + 1}$", ha="center", va="top",
                fontsize=8, color=p.muted)
    ax.set_xlim(-1.0, n + 0.1)
    ax.set_ylim(-0.9, n + 1.05)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9.5, color=(title_color or p.fg))
    ax.text(n / 2, n + 0.15, subtitle, ha="center", va="bottom",
            fontsize=8.2, family="monospace", color=p.amber)


def double_sum_as_a_grid(fig, ax, p: Palette) -> None:
    """Constant limits swap freely; a triangular limit does not."""
    fig.clear()
    axes = fig.subplots(1, 3)
    a = _grid(4)
    n = 4

    full = np.ones_like(a, dtype=bool)
    total = int(a.sum())
    rows = [int(a[r].sum()) for r in range(n)]
    cols = [int(a[:, c].sum()) for c in range(n)]
    _cells(axes[0], a, full, p,
           "Constant limits: the swap is free",
           "rows " + "+".join(map(str, rows)) + f" = {total}\n"
           "cols " + "+".join(map(str, cols)) + f" = {total}")

    lower = np.tril(full)
    low_total = int(a[lower].sum())
    _cells(axes[1], a, lower, p,
           "$\\sum_{i=1}^{4}\\sum_{j=1}^{i} a_{ij}$, the lower triangle",
           f"{int(lower.sum())} terms\ntotal = {low_total}")

    upper = np.triu(full)
    up_total = int(a[upper].sum())
    _cells(axes[2], a, upper, p,
           "Symbols swapped, limits left alone",
           f"the OTHER triangle\ntotal = {up_total}   "
           f"(off by {low_total - up_total})",
           title_color=p.red)

    fig.suptitle(
        "A double sum is a grid. Which cells the limits select is the whole question.",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.015,
        f"Left: adding the row totals and adding the column totals both give {total}, "
        "so constant limits commute. Right: rewriting\n"
        "$\\sum_i\\sum_{j\\leq i}$ as $\\sum_j\\sum_{i\\leq j}$ selects the transpose "
        f"of the intended set, giving {up_total} instead of {low_total}. The correct "
        "swap is $\\sum_{j=1}^{4}\\sum_{i=j}^{4}$.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def log_turns_products_into_sums(fig, ax, p: Palette) -> None:
    """Measured underflow. The product dies; the sum of logs does not."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    prob = 0.01
    ns = np.arange(1, 401)
    prods = np.array([prob ** float(k) for k in ns])
    logsum = ns * np.log(prob)

    zeros = np.flatnonzero(prods == 0.0)
    first_zero = int(ns[zeros[0]])
    tiny = np.finfo(float).tiny
    subs = np.flatnonzero((prods > 0) & (prods < tiny))
    first_sub = int(ns[subs[0]])

    left.semilogy(ns, np.where(prods > 0, prods, np.nan),
                  color=p.blue, linewidth=2.2,
                  label=f"$\\prod_i p_i$ with every $p_i = {prob}$")
    left.axvline(first_sub, color=p.amber, linestyle=":", linewidth=1.6)
    left.axvline(first_zero, color=p.red, linestyle="--", linewidth=1.8)
    left.text(first_sub - 8, 1e-90, f"subnormal from\n$N={first_sub}$",
              ha="right", va="center", fontsize=8, color=p.amber,
              family="monospace")
    left.text(first_zero + 10, 1e-240, f"exactly 0.0 from\n$N={first_zero}$",
              ha="left", va="center", fontsize=8, color=p.red,
              family="monospace")
    left.set_xlabel("$N$, number of factors")
    left.set_ylabel("value of the product")
    left.set_title("The product underflows", fontsize=10)
    left.legend(fontsize=8, loc="lower left")
    left.grid(alpha=0.25, linewidth=0.6)

    right.plot(ns, logsum, color=p.green, linewidth=2.4,
               label="$\\sum_i \\log p_i$")
    right.axvline(first_zero, color=p.red, linestyle="--", linewidth=1.8)
    at_zero = first_zero * np.log(prob)
    right.plot([first_zero], [at_zero], "o", color=p.green, markersize=6)
    right.annotate(
        f"at $N={first_zero}$ the log-sum is\n{at_zero:.1f}, an ordinary number",
        xy=(first_zero, at_zero),
        xytext=(0.30, 0.26), textcoords="axes fraction",
        fontsize=8.2, color=p.fg, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.muted, linewidth=1.1))
    right.set_xlabel("$N$, number of terms")
    right.set_ylabel("value of the log-sum")
    right.set_title("The sum of logarithms does not", fontsize=10)
    right.legend(fontsize=8, loc="upper right")
    right.grid(alpha=0.25, linewidth=0.6)

    fig.suptitle(
        "$\\log\\prod_i p_i = \\sum_i \\log p_i$ — identical in exact arithmetic, "
        "not in float64",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"From $N={first_zero}$ the left-hand quantity is not small, it is the number "
        "zero: its logarithm is $-\\infty$ and its gradient is\nundefined. Every "
        "likelihood in Chapters 8 to 12 is logged before it is optimised, and this is "
        "the whole reason.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def constant_out_of_a_product(fig, ax, p: Palette) -> None:
    """Rule 1 becomes c^N under a product. The Gaussian normaliser shows the cost."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    ns = np.arange(1, 201)
    c = 2 * np.pi                       # the 2 pi sigma^2 of a unit-variance Gaussian
    log_right = -0.5 * ns * np.log(c)   # (2 pi sigma^2)^(-N/2), correct
    log_wrong = -0.5 * np.log(c) * np.ones_like(ns, dtype=float)
    log_ratio = (log_wrong - log_right) / np.log(10)

    left.plot(ns, log_right / np.log(10), color=p.green, linewidth=2.4,
              label="$(2\\pi\\sigma^2)^{-N/2}$, correct")
    left.plot(ns, log_wrong / np.log(10), color=p.red, linewidth=2.2,
              linestyle="--",
              label="$(2\\pi\\sigma^2)^{-1/2}$, exponent dropped")
    left.set_xlabel("$N$, number of independent points")
    left.set_ylabel("$\\log_{10}$ of the normalising constant")
    left.set_title("Two normalising constants", fontsize=10)
    left.legend(fontsize=8, loc="lower left")
    left.grid(alpha=0.25, linewidth=0.6)

    right.plot(ns, log_ratio, color=p.amber, linewidth=2.4)
    for mark in (10, 50, 100, 200):
        val = log_ratio[mark - 1]
        right.plot([mark], [val], "o", color=p.amber, markersize=5)
        right.annotate(f"$N={mark}$: $10^{{{val:.0f}}}$ times too big",
                       xy=(mark, val), xytext=(-4, 10),
                       textcoords="offset points", fontsize=8,
                       ha="left", color=p.fg, family="monospace")
    right.set_xlabel("$N$")
    right.set_ylabel("$\\log_{10}$ of the ratio")
    right.set_title("How wrong the dropped exponent is", fontsize=10)
    right.grid(alpha=0.25, linewidth=0.6)

    fig.suptitle(
        "$\\prod_{i=1}^{N} c\\,a_i = c^{N}\\prod_i a_i$ — the constant leaves "
        "raised to the $N$",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "A constant factored out of a SUM comes out once, because it multiplies the "
        "whole sum. Factored out of a PRODUCT it\ncomes out once per factor. At "
        f"$N=100$ the two answers differ by a factor of "
        f"$10^{{{log_ratio[99]:.0f}}}$, so this is not a rounding-level mistake.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


FIGURES = [
    figure("double-sum-as-a-grid", double_sum_as_a_grid, size=(12.6, 4.8),
           axes=False),
    figure("log-turns-products-into-sums", log_turns_products_into_sums,
           size=(11.4, 4.6), axes=False),
    figure("constant-out-of-a-product", constant_out_of_a_product,
           size=(11.4, 4.6), axes=False),
]

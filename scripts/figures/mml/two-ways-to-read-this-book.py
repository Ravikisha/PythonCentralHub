"""Figures for *Two Ways to Read This Book*.

1. `pillars-and-foundations` — the book's Figure 1.1 as an incidence matrix
   rather than a drawing, so the row and column sums can be read off. Linear
   algebra feeds all four pillars; nothing else does. Each pillar needs three or
   four of the six foundations, never all six.

2. `two-routes-one-building` — the reading-order question, costed. Bottom-up
   spends six chapters before the first pillar pays off; top-down spends three or
   four for a single named goal, but revisits foundations as it goes. Both reach
   the same place; they differ in when the payoff arrives and in how much is read
   that the goal did not need.

The dependency data is taken directly from the book's own Figure 1.1 and is the
same data the interactive sketch on the page uses.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from _style import Palette, figure

FOUNDATIONS = [
    ("2", "Linear Algebra"),
    ("3", "Analytic Geometry"),
    ("4", "Matrix Decompositions"),
    ("5", "Vector Calculus"),
    ("6", "Probability"),
    ("7", "Optimization"),
]

PILLARS = [
    ("9", "Regression", ["2", "3", "5", "6"]),
    ("10", "Dimensionality\nReduction", ["2", "3", "4", "7"]),
    ("11", "Density\nEstimation", ["2", "4", "6", "7"]),
    ("12", "Classification", ["2", "3", "7"]),
]


def _incidence() -> np.ndarray:
    m = np.zeros((len(FOUNDATIONS), len(PILLARS)), dtype=int)
    for c, (_, _, deps) in enumerate(PILLARS):
        for r, (num, _) in enumerate(FOUNDATIONS):
            if num in deps:
                m[r, c] = 1
    return m


def pillars_and_foundations(fig, ax, p: Palette) -> None:
    """Figure 1.1 as a matrix, so the row and column sums are visible."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.35, 1.0])

    m = _incidence()
    nf, np_ = m.shape
    row_sum = m.sum(axis=1)
    col_sum = m.sum(axis=0)

    left.set_xlim(-3.9, np_ + 1.5)
    left.set_ylim(-1.35, nf + 0.95)
    left.axis("off")
    for c, (num, name, _) in enumerate(PILLARS):
        left.text(c + 0.5, nf + 0.12, f"Ch {num}\n{name}", ha="center",
                  va="bottom", fontsize=8.2, color=p.fg)
    left.text(np_ + 0.75, nf + 0.12, "pillars\nfed", ha="center", va="bottom",
              fontsize=8.2, color=p.amber)
    for r, (num, name) in enumerate(FOUNDATIONS):
        yy = nf - 1 - r
        left.text(-0.22, yy + 0.5, f"Ch {num} · {name}", ha="right",
                  va="center", fontsize=8.4,
                  color=(p.amber if row_sum[r] == np_ else p.fg))
        for c in range(np_):
            on = bool(m[r, c])
            left.add_patch(Rectangle(
                (c + 0.06, yy + 0.06), 0.88, 0.88,
                facecolor=(p.blue if on else p.grid),
                alpha=(0.42 if on else 0.5),
                edgecolor=(p.blue if on else p.grid), linewidth=1.3))
            if on:
                left.text(c + 0.5, yy + 0.5, "•", ha="center", va="center",
                          fontsize=17, color=p.fg)
        left.text(np_ + 0.75, yy + 0.5, str(row_sum[r]), ha="center",
                  va="center", fontsize=10.5, family="monospace",
                  color=(p.amber if row_sum[r] == np_ else p.muted))
    for c in range(np_):
        left.text(c + 0.5, -0.35, str(col_sum[c]), ha="center", va="center",
                  fontsize=10.5, family="monospace", color=p.green)
    left.text(-0.22, -0.35, "foundations needed", ha="right", va="center",
              fontsize=8.4, color=p.green)
    left.text(
        (np_ + 1.5 - 3.9) / 2 - 0.6, -1.25,
        f"Every pillar needs Chapter 2. No pillar needs all {nf} foundations: "
        f"the counts are {', '.join(map(str, col_sum))}.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)
    left.set_title("The book's Figure 1.1 as an incidence matrix", fontsize=9.8)

    order = np.argsort(-row_sum)
    labels = [f"Ch {FOUNDATIONS[i][0]}" for i in order]
    vals = row_sum[order]
    bars = right.barh(range(len(vals)), vals,
                      color=[p.amber if v == np_ else p.blue for v in vals],
                      alpha=0.65, height=0.62)
    right.set_yticks(range(len(vals)))
    right.set_yticklabels(labels, fontsize=9)
    right.invert_yaxis()
    for k, (b, v, i) in enumerate(zip(bars, vals, order)):
        right.text(v + 0.07, k, f"{FOUNDATIONS[i][1]} — {v} of {np_}",
                   va="center", fontsize=8.3, color=p.fg)
    right.set_xlim(0, np_ + 2.3)
    right.set_xlabel("number of pillars this foundation feeds")
    right.set_title("Which foundation earns its place", fontsize=9.8)
    right.grid(alpha=0.2, axis="x", linewidth=0.6)

    fig.suptitle(
        "Four pillars on six foundations, and the coupling is not uniform",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Reading the row sums: Chapter 2 is the only foundation every pillar needs, "
        "which is why it is not optional on any route. Reading the column\nsums: "
        "Classification needs three foundations, the other three pillars need four, "
        "and none needs all six. One caveat the matrix cannot show: these are\nthe "
        "DIRECT edges of Figure 1.1 only. Vector Calculus scores 1 because only "
        "Regression names it, yet Chapter 7 is built on its gradients, so every\n"
        "route through Optimization needs it as well.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def two_routes_one_building(fig, ax, p: Palette) -> None:
    """What each reading order costs before it pays anything."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    m = _incidence()
    nf = m.shape[0]
    col_sum = m.sum(axis=0)

    names = [f"Ch {num}\n{name.replace(chr(10), ' ')}" for num, name, _ in PILLARS]
    bottom_up = np.full(len(PILLARS), nf, dtype=int)
    top_down = col_sum

    idx = np.arange(len(PILLARS))
    width = 0.38
    left.bar(idx - width / 2, bottom_up, width, color=p.blue, alpha=0.65,
             label="bottom-up: all foundations first")
    left.bar(idx + width / 2, top_down, width, color=p.green, alpha=0.7,
             label="top-down: only what this goal needs")
    for k in idx:
        left.text(k - width / 2, bottom_up[k] + 0.1, str(bottom_up[k]),
                  ha="center", fontsize=9, color=p.blue, family="monospace")
        left.text(k + width / 2, top_down[k] + 0.1, str(top_down[k]),
                  ha="center", fontsize=9, color=p.green, family="monospace")
        saved = bottom_up[k] - top_down[k]
        left.text(k, -0.62, f"saves {saved}", ha="center", fontsize=8,
                  color=(p.amber if saved else p.muted), family="monospace")
    left.set_xticks(idx)
    left.set_xticklabels(names, fontsize=8.2)
    left.set_ylabel("foundation chapters read before the payoff")
    left.set_ylim(-1.1, nf + 1.1)
    left.set_title("Cost of reaching one named goal", fontsize=9.8)
    left.legend(fontsize=8, loc="upper right")
    left.grid(alpha=0.2, axis="y", linewidth=0.6)

    # Cumulative foundations needed as you add pillars, cheapest-first.
    cheap_order = list(np.argsort(col_sum))
    book_order = list(range(len(PILLARS)))
    for seq, col, style, lab in ((cheap_order, p.green, "-", "cheapest pillar first"),
                                 (book_order, p.blue, "--", "the book's order, Ch 9 to 12")):
        need = set()
        xs, ys = [0], [0]
        for k, pidx in enumerate(seq, start=1):
            need |= {r for r in range(nf) if m[r, pidx]}
            xs.append(k)
            ys.append(len(need))
        right.plot(xs, ys, marker="o", color=col, linewidth=2.2,
                   markersize=6, linestyle=style, label=lab)
        for xx, yy in zip(xs[1:], ys[1:]):
            right.text(xx, yy + 0.14, str(yy), ha="center", fontsize=8.4,
                       color=col, family="monospace")
    right.axhline(nf, color=p.muted, linestyle=":", linewidth=1.3)
    right.text(0.08, nf + 0.16, f"all {nf} foundations", fontsize=8.2,
               color=p.muted, family="monospace")
    right.set_xlabel("number of pillars you want")
    right.set_ylabel("distinct foundation chapters required")
    right.set_xticks(range(len(PILLARS) + 1))
    right.set_ylim(0, nf + 1.0)
    right.set_title("The saving shrinks as you add goals", fontsize=9.8)
    right.legend(fontsize=8, loc="lower right")
    right.grid(alpha=0.2, linewidth=0.6)

    first = int(col_sum.min())
    right.text(
        0.03, 0.97,
        f"one pillar: as few as {first} foundations\n"
        f"two pillars: {len({r for r in range(nf) if m[r, cheap_order[0]] or m[r, cheap_order[1]]})}\n"
        f"all four: {nf}, i.e. the whole of Part I",
        transform=right.transAxes, ha="left", va="top", fontsize=8,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Bottom-up and top-down reach the same place; they differ in when the "
        "payoff arrives",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Left: a reader who only wants Classification can reach it after three "
        "foundation chapters instead of six. Right: that saving is real for one\ngoal "
        "and evaporates by the fourth — wanting all four pillars means reading all "
        "six foundations, so the choice of route is about order, not volume.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


FIGURES = [
    figure("pillars-and-foundations", pillars_and_foundations,
           size=(13.2, 4.6), axes=False),
    figure("two-routes-one-building", two_routes_one_building,
           size=(12.4, 4.7), axes=False),
]

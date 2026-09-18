"""Figures for *Notation and Symbols*.

1. `typeface-tells-you-the-shape` — the convention doing real work. Reading a
   product left to right, the typeface alone fixes every intermediate shape and
   so catches a malformed expression without any arithmetic. The right panel is
   why that habit matters in code: over all sixteen pairings of the shapes (3,),
   (3,1), (1,3) and (3,3), NumPy's elementwise `*` raises an error on NONE of
   them, so a shape mistake becomes a silently wrong array rather than a crash.

2. `three-flavours-of-b` — B, bold B and script B are three different objects
   built from the same three vectors, and the book uses all three on one page.
   The panel shows what each one supports and what it forgets.

3. `overloaded-marks` — the half-dozen marks that mean more than one thing, with
   the context rule that disambiguates each, and the shape each meaning returns.
"""

from __future__ import annotations

import itertools

import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from _style import Palette, figure


def _box(ax, x, y, w, h, text, p: Palette, color, fontsize=9.5, alpha=0.20):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor=color, alpha=alpha, edgecolor=color, linewidth=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=p.fg)


def typeface_tells_you_the_shape(fig, ax, p: Palette) -> None:
    """Shape chaining by eye, and the code reason it is worth doing."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.05, 1.0])

    left.set_xlim(0, 10)
    left.set_ylim(0, 10)
    left.axis("off")
    left.set_title("Reading $\\mathbf{x}^\\top\\mathbf{A}\\mathbf{x}$ "
                   "without doing any arithmetic", fontsize=9.6)

    items = [
        ("$\\mathbf{x}^\\top$", "bold lower,\ntransposed", "$1 \\times D$", p.blue),
        ("$\\mathbf{A}$", "bold upper", "$D \\times D$", p.amber),
        ("$\\mathbf{x}$", "bold lower", "$D \\times 1$", p.blue),
    ]
    for k, (sym, why, shape, col) in enumerate(items):
        x = 0.5 + k * 3.1
        _box(left, x, 7.0, 2.4, 1.5, sym, p, col, fontsize=13)
        left.text(x + 1.2, 6.75, why, ha="center", va="top", fontsize=8,
                  color=p.muted, family="monospace")
        left.text(x + 1.2, 5.55, shape, ha="center", va="top", fontsize=9.5,
                  color=col, family="monospace")
        if k < 2:
            left.annotate("", xy=(x + 3.05, 7.75), xytext=(x + 2.45, 7.75),
                          arrowprops=dict(arrowstyle="-|>", color=p.muted,
                                          linewidth=1.4))

    left.text(5.0, 4.5,
              "$(1 \\times D)(D \\times D)(D \\times 1) = 1 \\times 1$",
              ha="center", fontsize=11.5, color=p.green)
    left.text(5.0, 3.7, "inner dimensions agree at every join, so the whole "
                        "product is a SCALAR",
              ha="center", fontsize=8.4, color=p.green, family="monospace")

    left.add_patch(Rectangle((0.4, 0.5), 9.2, 2.7, facecolor=p.red,
                             alpha=0.08, edgecolor=p.red, linewidth=1.2))
    left.text(5.0, 2.85, "now try $\\mathbf{A}\\mathbf{x}^\\top$",
              ha="center", va="top", fontsize=10, color=p.red)
    left.text(5.0, 2.05,
              "$(D \\times D)(1 \\times D)$ — inner dimensions $D$ and $1$ "
              "disagree",
              ha="center", va="top", fontsize=9.2, color=p.fg)
    left.text(5.0, 1.25,
              "malformed, and you knew that from the typeface alone",
              ha="center", va="top", fontsize=8.4, color=p.red,
              family="monospace")

    # The measurement: NumPy will not catch this for you.
    shapes = {"(3,)": (3,), "(3,1)": (3, 1), "(1,3)": (1, 3), "(3,3)": (3, 3)}
    rows = []
    star_err = at_err = 0
    for (an, a), (bn, b) in itertools.product(shapes.items(), repeat=2):
        A, B = np.ones(a), np.ones(b)
        try:
            star = str(np.shape(A * B))
        except ValueError:
            star, = ("error",)
            star_err += 1
        try:
            atm = str(np.shape(A @ B))
        except ValueError:
            atm = "error"
            at_err += 1
        rows.append((an, bn, star, atm))

    right.set_xlim(0, 10)
    right.set_ylim(-0.6, len(rows) + 2.6)
    right.axis("off")
    right.set_title("What NumPy does with the same sixteen pairings",
                    fontsize=9.6)
    heads = ("A", "B", "A * B", "A @ B")
    xs = (0.6, 2.5, 4.6, 7.4)
    for hx, h in zip(xs, heads):
        right.text(hx, len(rows) + 1.1, h, fontsize=8.8, color=p.fg,
                   family="monospace", weight="bold")
    for k, (an, bn, star, atm) in enumerate(rows):
        y = len(rows) - 1 - k
        if k % 2 == 0:
            right.add_patch(Rectangle((0.35, y - 0.16), 9.3, 0.86,
                                      facecolor=p.grid, alpha=0.35,
                                      edgecolor="none"))
        bad = (star != "error") and (an != bn)
        right.text(xs[0], y + 0.26, an, fontsize=8.2, color=p.muted,
                   family="monospace", va="center")
        right.text(xs[1], y + 0.26, bn, fontsize=8.2, color=p.muted,
                   family="monospace", va="center")
        right.text(xs[2], y + 0.26, star, fontsize=8.2,
                   color=(p.red if bad else p.fg),
                   family="monospace", va="center")
        right.text(xs[3], y + 0.26, atm, fontsize=8.2,
                   color=(p.green if atm == "error" else p.fg),
                   family="monospace", va="center")

    right.text(0.35, -0.35,
               f"`*` raised an error on {star_err} of {len(rows)} pairings.  "
               f"`@` raised on {at_err}.",
               fontsize=8.6, color=p.amber, family="monospace", va="top")

    fig.suptitle(
        "The typeface convention is a shape checker you run in your head",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Left: lowercase bold is a column, uppercase bold is a grid, so every "
        "intermediate shape in a product is fixed before you compute anything, and "
        "a\nmalformed expression is visible on sight. Right: the reason to bother. "
        f"Elementwise `*` accepted all {len(rows)} pairings, inventing a "
        "$3\\times3$ from a $(3,)$ and a $(3,1)$\nwithout complaint. Red rows are "
        "shape mismatches that produced an array instead of an exception.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def three_flavours_of_b(fig, ax, p: Palette) -> None:
    """B, bold B, script B: same three vectors, three jobs."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    b1, b2, b3 = (np.array([2.0, 1.0]), np.array([1.0, 3.0]),
                  np.array([-1.0, 1.0]))
    cols = (p.blue, p.amber, p.green)

    for axx in (a1, a2, a3):
        axx.set_xlim(0, 10)
        axx.set_ylim(0, 10)
        axx.axis("off")

    a1.set_title("$B$ — an ordered TUPLE", fontsize=10, color=p.blue)
    a1.text(5.0, 8.9, "$B = (\\mathbf{b}_1, \\mathbf{b}_2, \\mathbf{b}_3)$",
            ha="center", fontsize=12, color=p.fg)
    for k, (v, col) in enumerate(zip((b1, b2, b3), cols)):
        _box(a1, 1.2 + k * 2.7, 6.1, 2.3, 1.5,
             f"$\\mathbf{{b}}_{k + 1}$\n$({v[0]:.0f}, {v[1]:.0f})$", p, col)
        a1.text(1.2 + k * 2.7 + 1.15, 5.85, f"position {k + 1}", ha="center",
                va="top", fontsize=7.8, color=p.muted, family="monospace")
    a1.text(5.0, 4.4, "ORDER MATTERS", ha="center", fontsize=9.5, color=p.blue,
            family="monospace")
    a1.text(5.0, 3.5,
            "so coordinates are well defined:\nswap two entries and every\n"
            "coordinate vector changes",
            ha="center", va="top", fontsize=8.4, color=p.muted)
    a1.text(5.0, 0.8, "used when: $\\S2.6.1$, coordinates\nw.r.t. a basis",
            ha="center", va="bottom", fontsize=8.2, color=p.fg)

    a2.set_title("$\\boldsymbol{B}$ — a MATRIX", fontsize=10, color=p.amber)
    a2.text(5.0, 8.9,
            "$\\boldsymbol{B} = [\\mathbf{b}_1\\;\\mathbf{b}_2\\;\\mathbf{b}_3]$",
            ha="center", fontsize=12, color=p.fg)
    M = np.column_stack([b1, b2, b3])
    for r in range(2):
        for c in range(3):
            a2.add_patch(Rectangle((2.6 + c * 1.6, 6.4 - r * 1.3), 1.5, 1.2,
                                   facecolor=p.amber, alpha=0.20,
                                   edgecolor=p.amber, linewidth=1.3))
            a2.text(2.6 + c * 1.6 + 0.75, 6.4 - r * 1.3 + 0.6,
                    f"{M[r, c]:.0f}", ha="center", va="center", fontsize=11,
                    color=p.fg, family="monospace")
    a2.text(5.0, 4.4, "shape $2 \\times 3$", ha="center", fontsize=9.5,
            color=p.amber, family="monospace")
    rank = int(np.linalg.matrix_rank(M))
    a2.text(5.0, 3.5,
            f"you can MULTIPLY by it:\n$\\boldsymbol{{B}}\\mathbf{{z}}$ maps "
            f"$\\mathbb{{R}}^3 \\to \\mathbb{{R}}^2$\nmeasured rank {rank}",
            ha="center", va="top", fontsize=8.4, color=p.muted)
    a2.text(5.0, 0.8, "used when: $\\S2.7$, a linear map\nas a concrete object",
            ha="center", va="bottom", fontsize=8.2, color=p.fg)

    a3.set_title("$\\mathcal{B}$ — an unordered SET", fontsize=10,
                 color=p.purple)
    a3.text(5.0, 8.9,
            "$\\mathcal{B} = \\{\\mathbf{b}_1, \\mathbf{b}_2, \\mathbf{b}_3\\}$",
            ha="center", fontsize=12, color=p.fg)
    from matplotlib.patches import Ellipse
    a3.add_patch(Ellipse((5.0, 6.9), 7.4, 3.0, facecolor=p.purple, alpha=0.12,
                         edgecolor=p.purple, linewidth=1.5))
    spots = ((3.3, 7.4), (5.6, 6.3), (6.6, 7.6))
    for (sx, sy), col, k in zip(spots, cols, range(3)):
        a3.plot([sx], [sy], "o", color=col, markersize=11)
        a3.text(sx, sy - 0.75, f"$\\mathbf{{b}}_{k + 1}$", ha="center",
                fontsize=9.5, color=col)
    a3.text(5.0, 4.4, "ONLY MEMBERSHIP", ha="center", fontsize=9.5,
            color=p.purple, family="monospace")
    a3.text(5.0, 3.5,
            "no order, no duplicates:\nyou may ask "
            "$\\mathbf{b}_2 \\in \\mathcal{B}$\nand nothing else",
            ha="center", va="top", fontsize=8.4, color=p.muted)
    a3.text(5.0, 0.8, "used when: $\\S2.6$, spanning\nand independence",
            ha="center", va="bottom", fontsize=8.2, color=p.fg)

    fig.suptitle(
        "$B$, $\\boldsymbol{B}$ and $\\mathcal{B}$ are three different objects, "
        "and the book uses all three",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The same three vectors throughout. A basis is a tuple when you need "
        "coordinates in a fixed order, a matrix when you want to multiply by it, "
        "and a set\nwhen you only care what belongs to it. Choosing the wrong one "
        "is not a typo — asking for the second element of $\\mathcal{B}$ is a "
        "question the object cannot answer.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def overloaded_marks(fig, ax, p: Palette) -> None:
    """The marks that mean more than one thing, and the rule that decides."""
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")

    v = np.array([3.0, -4.0])
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    rows = [
        ("$\|\\,\\cdot\\,\|$",
         "absolute value of a scalar",
         "argument is a scalar",
         f"$\| -4 \| = {abs(-4.0):.0f}$", p.blue),
        ("$\|\\,\\cdot\\,\|$",
         "determinant of a matrix",
         "argument is a square matrix",
         f"$\| \\boldsymbol{{A}} \| = "
         f"{np.linalg.det(A):.0f}$", p.amber),
        ("$\|\\,\\cdot\\,\|$",
         "cardinality of a set",
         "argument is a set",
         "$\|\\{a,b,c\\}\| = 3$", p.green),
        ("$\\|\\,\\cdot\\,\\|$",
         "a norm, length of a vector",
         "double bars, never single",
         f"$\\| (3,-4) \\| = "
         f"{np.linalg.norm(v):.0f}$", p.purple),
        ("$\\cdot$",
         "ordinary multiplication",
         "between two scalars",
         "$2 \\cdot 3 = 6$", p.blue),
        ("$\\cdot$",
         "a placeholder for the argument",
         "standing alone inside a bracket",
         "$f(\\cdot)$ names the function", p.red),
        ("$\\top$",
         "transpose",
         "superscript on a vector or matrix",
         "$(D\\times1)^\\top$ is $1\\times D$", p.amber),
        ("$B$ vs $\\boldsymbol{B}$ vs $\\mathcal{B}$",
         "tuple, matrix, set",
         "the typeface, and only the typeface",
         "see the figure above", p.green),
        ("$X$",
         "a random variable",
         "Chapter 6 onward, italic upper",
         "$p(X = x)$", p.purple),
        ("$X$",
         "a count or a dimension",
         "as an index bound, e.g. $N$, $D$",
         "$\\sum_{n=1}^{N}$", p.blue),
    ]

    ax.set_xlim(0, 10)
    ax.set_ylim(-0.9, len(rows) + 1.6)
    heads = ("mark", "meaning", "how you can tell", "example")
    xs = (0.35, 2.25, 4.95, 7.75)
    for hx, h in zip(xs, heads):
        ax.text(hx, len(rows) + 0.55, h, fontsize=9.2, color=p.fg,
                family="monospace", weight="bold")
    ax.plot([0.3, 9.9], [len(rows) + 0.32] * 2, color=p.grid, linewidth=1.2)

    for k, (mark, meaning, tell, ex, col) in enumerate(rows):
        y = len(rows) - 1 - k
        if k % 2 == 0:
            ax.add_patch(Rectangle((0.28, y - 0.06), 9.64, 0.92,
                                   facecolor=p.grid, alpha=0.35,
                                   edgecolor="none"))
        ax.text(xs[0], y + 0.4, mark, fontsize=10, color=col, va="center")
        ax.text(xs[1], y + 0.4, meaning, fontsize=8.6, color=p.fg, va="center")
        ax.text(xs[2], y + 0.4, tell, fontsize=8.4, color=p.muted, va="center")
        ax.text(xs[3], y + 0.4, ex, fontsize=8.6, color=col, va="center")

    ax.text(0.3, -0.55,
            "In every case the mark is disambiguated by the TYPE of its argument, "
            "never by the mark itself. That is why reading the typeface first is "
            "not optional.",
            fontsize=8.4, color=p.amber, va="center")

    fig.suptitle(
        "Six marks that mean more than one thing, and what settles which",
        y=0.985, fontsize=10, color=p.fg)


FIGURES = [
    figure("typeface-tells-you-the-shape", typeface_tells_you_the_shape,
           size=(13.0, 5.6), axes=False),
    figure("three-flavours-of-b", three_flavours_of_b, size=(13.0, 4.9),
           axes=False),
    figure("overloaded-marks", overloaded_marks, size=(11.8, 5.4), axes=False),
]

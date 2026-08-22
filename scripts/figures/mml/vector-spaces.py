"""Figures for *Vector Spaces*.

`subspace-or-not` — the book's Figure 2.6, redrawn with the **witness** shown.

The original figure asserts which of four subsets of the plane is a subspace.
This version annotates each failing panel with the specific vectors whose sum or
whose scaling escapes the set, because "not a subspace" is never a judgement
call: it is always a counterexample, and the productive habit is to hunt for one
rather than to reason about it abstractly.

The bounded-square panel is the one the page dwells on. It contains the origin
and it is closed under addition of small enough vectors, which is exactly why it
feels like it should qualify — and it fails on scaling, because closure must hold
for every real scalar, not merely the modest ones.
"""

import numpy as np

from _style import Palette, figure


def subspace_or_not(fig, ax, p: Palette) -> None:
    """Four subsets, one subspace, each failure shown with its witness."""
    fig.clear()
    axes = fig.subplots(1, 4, sharex=True, sharey=True)

    LIM = 3.2

    def chrome(a, title, ok):
        a.axhline(0, color=p.grid, linewidth=0.9)
        a.axvline(0, color=p.grid, linewidth=0.9)
        a.set_xlim(-LIM, LIM)
        a.set_ylim(-LIM, LIM)
        a.set_xlabel("$x_1$")
        a.set_title(title, color=p.green if ok else p.red, fontsize=10.5)
        a.plot(0, 0, marker="o", color=p.fg, markersize=4, zorder=6)

    def arrow(a, v, colour, label, dx=0.14, dy=0.14):
        a.annotate("", xy=v, xytext=(0, 0),
                   arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.0))
        a.annotate(label, xy=v, xytext=(v[0] + dx, v[1] + dy),
                   color=colour, fontsize=9)

    # ---- panel A: a bounded square. Fails scaling. ----------------------
    a = axes[0]
    a.add_patch(__import__("matplotlib").patches.Rectangle(
        (-1, -1), 2, 2, facecolor=p.blue, alpha=0.18, edgecolor=p.blue, linewidth=1.4))
    u = np.array([0.7, 0.6])
    arrow(a, u, p.amber, "$u$")
    arrow(a, 3 * u, p.red, r"$3u$ — escaped")
    chrome(a, "bounded square\nfails SCALING", False)
    a.text(-3.0, -2.95, "contains 0, closed under\nsmall sums — still not a subspace",
           color=p.muted, fontsize=8)

    # ---- panel B: a line through the origin. Passes. --------------------
    a = axes[1]
    t = np.linspace(-LIM, LIM, 50)
    d = np.array([1.0, 0.62]) / np.linalg.norm([1.0, 0.62])
    a.plot(t * d[0] * 2.4, t * d[1] * 2.4, color=p.green, linewidth=2.6)
    v1, v2 = 1.1 * d, -1.9 * d
    arrow(a, v1, p.amber, "$u$")
    arrow(a, v2, p.purple, "$v$")
    arrow(a, v1 + v2, p.green, "$u+v$ stays")
    chrome(a, "line through the origin\nSUBSPACE", True)
    a.text(-3.0, -2.95, "closed under both operations,\nand contains 0",
           color=p.muted, fontsize=8)

    # ---- panel C: a pair of cones. Fails addition. ---------------------
    a = axes[2]
    for sign in (1, -1):
        ang = np.linspace(np.pi / 2 - 0.42, np.pi / 2 + 0.42, 30)
        xs = np.concatenate([[0], LIM * np.cos(ang) * sign, [0]])
        ys = np.concatenate([[0], LIM * np.sin(ang) * sign, [0]])
        a.fill(xs, ys, color=p.blue, alpha=0.18, edgecolor=p.blue, linewidth=1.2)
    u = np.array([0.5, 2.0])
    v = np.array([-0.5, 2.0])
    arrow(a, u, p.amber, "$u$", dx=0.1, dy=0.05)
    arrow(a, v, p.purple, "$v$", dx=-0.95, dy=0.05)
    # Both are in the upper cone; a vector from each cone sums outside both.
    w = np.array([0.5, 2.0]) + np.array([-2.0, -0.6])
    arrow(a, np.array([-2.0, -0.6]), p.green, "$w$", dx=-0.5, dy=-0.4)
    arrow(a, w, p.red, "$u+w$ — escaped", dx=-0.4, dy=-0.5)
    chrome(a, "two cones\nfails ADDITION", False)
    a.text(-3.0, -2.95, "closed under scaling,\nbut sums leave the set",
           color=p.muted, fontsize=8)

    # ---- panel D: a single off-origin point. Fails the zero test. -------
    a = axes[3]
    q = np.array([0.0, 1.6])
    a.plot(*q, marker="o", color=p.blue, markersize=9)
    a.annotate("the only member", xy=q, xytext=(q[0] - 2.6, q[1] + 0.6),
               color=p.blue, fontsize=8.5)
    a.annotate("", xy=(0, 0), xytext=q,
               arrowprops=dict(arrowstyle="<->", color=p.red, linewidth=1.4,
                               linestyle="--"))
    a.text(0.14, 0.7, "does not\ncontain 0", color=p.red, fontsize=9)
    chrome(a, "one point, off origin\nfails ZERO", False)
    a.text(-3.0, -2.95, "the cheapest test, and\nthe first one to run",
           color=p.muted, fontsize=8)

    axes[0].set_ylabel("$x_2$")


FIGURES = [
    figure("subspace-or-not", subspace_or_not, size=(11.0, 3.6), axes=False),
]

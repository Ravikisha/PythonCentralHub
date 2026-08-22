"""Figures for *Backpropagation and Automatic Differentiation*.

1. `forward-vs-reverse-cost` — the sentence §5.6.2 uses to justify reverse mode:
   "in the context of neural networks, where the input dimensionality is often
   much higher than the dimensionality of the labels, the reverse mode is
   computationally significantly cheaper." Forward mode costs one sweep per INPUT,
   reverse mode one sweep per OUTPUT, so the choice is decided by the shape of the
   Jacobian and nothing else. Both costs are plotted, with the crossover marked.

2. `example-5-14-flow` — the book's Figure 5.11 with numbers on it: the six
   intermediate variables of Eq 5.123-5.128 carrying their forward values, and the
   adjoints of Eq 5.135-5.142 carrying their reverse ones. The node that branches
   is highlighted, because its adjoint is the one sum in the whole example.

3. `autodiff-beats-differencing` — accuracy, not speed. The derivative of
   Example 5.14 computed three ways against h: automatic differentiation is a flat
   line at machine precision because it has no h at all, while forward and central
   differences trace out their V curves. Measured: AD lands at 2.2e-16 while the
   best central difference over 200 values of h reaches only 9.8e-12 -- a factor
   of forty thousand, and that is the BEST h, which you do not know in advance.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


# The book's Example 5.14, Eq 5.122.
def f_5_14(x):
    a = x ** 2
    b = np.exp(a)
    c = a + b
    d = np.sqrt(c)
    e = np.cos(c)
    return d + e


def dfdx_5_14(x):
    """Differentiated by hand: f = sqrt(u) + cos(u) with u = x^2 + exp(x^2)."""
    u = x ** 2 + np.exp(x ** 2)
    dudx = 2 * x * (1 + np.exp(x ** 2))
    return (1 / (2 * np.sqrt(u)) - np.sin(u)) * dudx


def forward_vs_reverse_cost(fig, ax, p: Palette) -> None:
    """One sweep per input against one sweep per output."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.05]})

    # A fixed graph size; only the input and output widths vary.
    ops = 1.0                     # cost of one forward evaluation, normalised
    ns = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 1024, 4096])

    # A scalar loss: m = 1. Forward needs n sweeps, reverse needs 1.
    left.loglog(ns, ns * ops * 1.0, "^-", color=p.red, linewidth=2.0,
                label="forward mode: $n$ sweeps")
    left.loglog(ns, np.full_like(ns, 1, dtype=float) * 2.5, "s-", color=p.blue,
                linewidth=2.0, label="reverse mode: 1 sweep ($\\approx 2.5\\times$)")
    left.set_xlabel("number of inputs $n$   (outputs $m = 1$)")
    left.set_ylabel("cost, in forward evaluations")
    left.set_title("a scalar loss: reverse mode wins from $n = 3$", fontsize=10)
    left.legend(loc="upper left", fontsize=8.4)
    left.axvline(3, color=p.muted, linewidth=1.0, linestyle="--")
    left.text(
        0.98, 0.03,
        "a neural network has n in the millions\n"
        "and m = 1, so this is not a close call:\n"
        "reverse mode is the only option, and\n"
        "that is what backpropagation IS.",
        transform=left.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.6, family="monospace",
    )

    # The general rule, as a heatmap of which mode wins.
    grid = np.array([1, 2, 4, 8, 16, 32, 64, 128])
    Nn, Mm = np.meshgrid(grid, grid)
    fwd = Nn * 1.0
    rev = Mm * 2.5
    winner = np.where(fwd < rev, 0.0, 1.0)
    right.imshow(winner, origin="lower", cmap="coolwarm", alpha=0.75,
                 extent=[-0.5, len(grid) - 0.5, -0.5, len(grid) - 0.5], aspect="auto")
    right.set_xticks(range(len(grid)), [str(g) for g in grid], fontsize=8)
    right.set_yticks(range(len(grid)), [str(g) for g in grid], fontsize=8)
    right.set_xlabel("inputs $n$")
    right.set_ylabel("outputs $m$")
    right.set_title("which mode is cheaper", fontsize=10)
    for i in range(len(grid)):
        for j in range(len(grid)):
            right.text(j, i, "fwd" if winner[i, j] == 0 else "rev",
                       ha="center", va="center", fontsize=6.6,
                       color=p.bg)
    right.plot([len(grid) - 1], [0], "*", color=p.amber, markersize=18, zorder=5)
    right.text(len(grid) - 1.4, 0.35, "a network:\nmany in, one out",
               color=p.amber, fontsize=7.4, ha="right")


def example_5_14_flow(fig, ax, p: Palette) -> None:
    """Figure 5.11, with the forward values and the adjoints written on it."""
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    x0 = 0.9
    a = x0 ** 2
    b = np.exp(a)
    c = a + b
    d = np.sqrt(c)
    e = np.cos(c)
    fv = d + e

    # Eq 5.135-5.142, in the order the sweep computes them.
    adj_f = 1.0
    adj_d = adj_f * 1.0
    adj_e = adj_f * 1.0
    adj_c = adj_d * (1 / (2 * np.sqrt(c))) + adj_e * (-np.sin(c))
    adj_b = adj_c * 1.0
    adj_a = adj_b * np.exp(a) + adj_c * 1.0
    adj_x = adj_a * 2 * x0

    nodes = [
        ("x", 0.05, 0.50, x0, adj_x, "input"),
        ("a", 0.21, 0.50, a, adj_a, "$a = x^2$"),
        ("b", 0.38, 0.74, b, adj_b, "$b = \\exp(a)$"),
        ("c", 0.55, 0.50, c, adj_c, "$c = a + b$"),
        ("d", 0.73, 0.74, d, adj_d, "$d = \\sqrt{c}$"),
        ("e", 0.73, 0.26, e, adj_e, "$e = \\cos(c)$"),
        ("f", 0.91, 0.50, fv, adj_f, "$f = d + e$"),
    ]
    pos = {n[0]: (n[1], n[2]) for n in nodes}
    edges = [("x", "a"), ("a", "b"), ("a", "c"), ("b", "c"), ("c", "d"), ("c", "e"),
             ("d", "f"), ("e", "f")]

    for u, v in edges:
        branch = u == "a"
        ax.annotate(
            "",
            xy=pos[v], xytext=pos[u],
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=dict(arrowstyle="->", color=p.amber if branch else p.muted,
                            linewidth=2.2 if branch else 1.3,
                            shrinkA=20, shrinkB=20),
        )

    for name, xx, yy, val, adj, label in nodes:
        colour = p.amber if name == "a" else p.blue
        ax.text(xx, yy + 0.075, label, transform=ax.transAxes, ha="center",
                color=p.muted, fontsize=8.0)
        circ = ax.scatter([xx], [yy], s=1250, transform=ax.transAxes,
                          facecolor=colour, alpha=0.16, edgecolor=colour, linewidths=1.8,
                          zorder=3)
        ax.text(xx, yy + 0.018, name, transform=ax.transAxes, ha="center", va="center",
                color=colour, fontsize=11, fontweight="bold", zorder=4)
        ax.text(xx, yy - 0.035, f"{val:.4f}", transform=ax.transAxes, ha="center",
                va="center", color=p.fg, fontsize=7.4, family="monospace", zorder=4)
        ax.text(xx, yy - 0.082, f"adj {adj:.4f}", transform=ax.transAxes, ha="center",
                va="center", color=p.red, fontsize=7.2, family="monospace", zorder=4)

    ax.text(
        0.5, 0.99,
        f"Example 5.14 at $x = {x0}$:  forward values in white, adjoints in red",
        transform=ax.transAxes, ha="center", va="top",
        color=p.fg, fontsize=10.5, fontweight="bold",
    )
    ax.text(
        0.5, 0.14,
        f"$a$ feeds both $b$ and $c$, so its adjoint is a SUM (Eq 5.137):\n"
        f"adj$[a]$ = adj$[b]\\cdot\\exp(a)$ + adj$[c]\\cdot 1$ = "
        f"{adj_b:.6f}$\\times${np.exp(a):.6f} + {adj_c:.6f} = {adj_a:.6f}\n"
        f"and then $\\partial f/\\partial x$ = adj$[a]\\cdot 2x$ = {adj_a:.6f}$\\times${2 * x0} "
        f"= {adj_x:.6f}",
        transform=ax.transAxes, ha="center", va="top",
        color=p.amber, fontsize=8.6,
    )
    ax.text(
        0.5, 0.02,
        f"hand-differentiated: {dfdx_5_14(x0):.10f}    reverse mode: {adj_x:.10f}    "
        f"gap: {abs(adj_x - dfdx_5_14(x0)):.1e}",
        transform=ax.transAxes, ha="center", va="bottom",
        color=p.green, fontsize=8.4, family="monospace",
    )


def autodiff_beats_differencing(fig, ax, p: Palette) -> None:
    """AD has no h, so it has no V."""
    x0 = 0.9
    exact = dfdx_5_14(x0)

    hs = np.logspace(0, -15, 200)
    fwd = np.abs((f_5_14(x0 + hs) - f_5_14(x0)) / hs - exact)
    cen = np.abs((f_5_14(x0 + hs) - f_5_14(x0 - hs)) / (2 * hs) - exact)

    # Reverse mode, computed once. It does not depend on h at all.
    a = x0 ** 2
    b = np.exp(a)
    c = a + b
    adj_c = 1.0 * (1 / (2 * np.sqrt(c))) + 1.0 * (-np.sin(c))
    adj_a = adj_c * np.exp(a) + adj_c * 1.0
    ad = adj_a * 2 * x0
    ad_err = max(abs(ad - exact), 1e-17)

    floor = 1e-18
    ax.loglog(hs, np.maximum(fwd, floor), color=p.red, linewidth=2.0, label="forward difference")
    ax.loglog(hs, np.maximum(cen, floor), color=p.blue, linewidth=2.0, label="central difference")
    ax.axhline(ad_err, color=p.green, linewidth=2.6,
               label=f"reverse-mode AD: {ad_err:.1e}, no $h$")
    ax.axhline(np.finfo(float).eps, color=p.muted, linewidth=0.9, linestyle="--")

    i_c = int(np.argmin(cen))
    ax.plot([hs[i_c]], [cen[i_c]], "*", color=p.blue, markersize=14, zorder=5)

    ax.set_xlabel("step $h$")
    ax.set_ylabel("$|$estimate $-$ exact$|$")
    ax.invert_xaxis()
    ax.set_title("automatic differentiation is exact up to round-off, at any scale",
                 fontsize=10.5)
    ax.legend(loc="lower left", fontsize=8.2)
    ax.text(
        0.98, 0.97,
        f"exact derivative      {exact:.12f}\n"
        f"reverse-mode AD       {ad:.12f}\n"
        f"best central diff     {(cen[i_c] + exact):.12f}\n"
        f"                      at h = {hs[i_c]:.1e}\n\n"
        f"AD error              {ad_err:.1e}\n"
        f"best differencing     {cen[i_c]:.1e}\n"
        f"ratio                 {cen[i_c] / ad_err:.0e}x",
        transform=ax.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.4, family="monospace",
    )


FIGURES = [
    figure("forward-vs-reverse-cost", forward_vs_reverse_cost, size=(11.0, 4.6), axes=False),
    figure("example-5-14-flow", example_5_14_flow, size=(10.8, 5.2)),
    figure("autodiff-beats-differencing", autodiff_beats_differencing, size=(8.6, 5.0)),
]

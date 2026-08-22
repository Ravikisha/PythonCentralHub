"""Figures for *Differentiation of Univariate Functions*.

1. `secant-to-tangent` — the book's Figure 5.3/5.4 in one panel: the difference
   quotient as the slope of a secant through (x, f(x)) and (x + h, f(x + h)), for
   a ladder of shrinking h, with the limiting tangent drawn heavy. The panel
   reports the secant slopes so the convergence is a column of numbers rather
   than an impression.

2. `difference-quotient-floor` — the half of Definition 5.2 that a calculus
   course never shows. Plotted against h on log-log axes, the error of a forward
   difference falls like h and the error of a central difference like h squared,
   until round-off takes over and both turn around. The V shape is the point: the
   best h is neither large nor as small as possible, and "let h go to zero" is
   advice you cannot follow in floating point.

3. `taylor-degrees` — Taylor polynomials T_0 through T_5 of sin(x) + cos(x) at
   x0 = 0 (Example 5.4, Exercise 5.4), with the error measured twice: on a tight
   neighbourhood of x0, where it falls monotonically, and on the whole window,
   where it does not. Showing only the first would flatter the method.
"""

from __future__ import annotations

import math

import numpy as np

from _style import Palette, figure


def secant_to_tangent(fig, ax, p: Palette) -> None:
    """The difference quotient, converging to the tangent."""
    f = lambda x: np.sin(x) + 0.35 * x ** 2
    fp = lambda x: np.cos(x) + 0.7 * x
    x0 = 0.9

    xs = np.linspace(-0.4, 3.0, 400)
    ax.plot(xs, f(xs), color=p.fg, linewidth=2.2, label="$f$", zorder=3)

    hs = [1.6, 0.8, 0.4, 0.2]
    shades = [p.red, p.amber, p.purple, p.blue]
    rows = []
    for h, colour in zip(hs, shades):
        slope = (f(x0 + h) - f(x0)) / h
        rows.append((h, slope))
        # Draw the secant across the whole window so the slopes are comparable.
        line = f(x0) + slope * (xs - x0)
        ax.plot(xs, line, color=colour, linewidth=1.3, linestyle="--", alpha=0.85)
        ax.plot([x0 + h], [f(x0 + h)], "o", color=colour, markersize=5)
        ax.annotate(
            f"$h={h}$",
            xy=(x0 + h, f(x0 + h)),
            xytext=(x0 + h + 0.06, f(x0 + h) - 0.55),
            color=colour,
            fontsize=8.5,
        )

    tangent = f(x0) + fp(x0) * (xs - x0)
    ax.plot(xs, tangent, color=p.green, linewidth=2.4, label="tangent, slope $f'(x_0)$", zorder=4)
    ax.plot([x0], [f(x0)], "o", color=p.green, markersize=7, zorder=5)

    ax.set_xlabel("$x$")
    ax.set_ylabel("$f(x)$")
    ax.set_title("the difference quotient is the slope of a secant", fontsize=10.5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_xlim(-0.4, 3.0)
    ax.set_ylim(f(x0) - 2.4, max(f(xs)) + 0.4)

    table = "\n".join(f"  h = {h:<5} slope {s:.6f}" for h, s in rows)
    ax.text(
        0.985,
        0.03,
        f"secant slopes\n{table}\n  exact      {fp(x0):.6f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=p.fg,
        fontsize=7.8,
        family="monospace",
    )


def difference_quotient_floor(fig, ax, p: Palette) -> None:
    """Truncation falls, round-off rises, and the sum has a floor."""
    f = lambda x: np.sin(x) + 0.35 * x ** 2
    fp = lambda x: np.cos(x) + 0.7 * x
    x0 = 0.9
    exact = fp(x0)

    hs = np.logspace(0, -15, 160)
    fwd = np.abs((f(x0 + hs) - f(x0)) / hs - exact)
    cen = np.abs((f(x0 + hs) - f(x0 - hs)) / (2 * hs) - exact)

    floor = 1e-18
    ax.loglog(hs, np.maximum(fwd, floor), color=p.red, linewidth=2.0, label="forward, $O(h)$")
    ax.loglog(hs, np.maximum(cen, floor), color=p.blue, linewidth=2.0, label="central, $O(h^2)$")

    # Reference slopes, so the orders are readable rather than asserted.
    ref = hs[(hs < 1e-1) & (hs > 1e-6)]
    ax.loglog(ref, ref * 0.5, color=p.muted, linewidth=1.0, linestyle=":", label="$\\propto h$")
    ax.loglog(ref, ref ** 2 * 0.2, color=p.muted, linewidth=1.0, linestyle="-.", label="$\\propto h^2$")

    i_f = int(np.argmin(fwd))
    i_c = int(np.argmin(cen))
    for i, colour, name in ((i_f, p.red, "forward"), (i_c, p.blue, "central")):
        ax.plot([hs[i]], [max(fwd[i] if colour == p.red else cen[i], floor)], "*",
                color=colour, markersize=13, zorder=5)

    ax.axhline(np.finfo(float).eps, color=p.muted, linewidth=0.9, linestyle="--")
    ax.text(
        hs[-1] * 3,
        np.finfo(float).eps * 1.6,
        "machine epsilon",
        color=p.muted,
        fontsize=7.6,
    )

    ax.set_xlabel("step $h$")
    ax.set_ylabel("$|$estimate $-$ exact$|$")
    ax.set_title("'let $h$ go to zero' is advice you cannot follow", fontsize=10.5)
    ax.invert_xaxis()
    ax.legend(loc="upper left", fontsize=8)
    ax.text(
        0.02,
        0.03,
        f"best forward: h = {hs[i_f]:.1e}, error {fwd[i_f]:.2e}\n"
        f"best central: h = {hs[i_c]:.1e}, error {cen[i_c]:.2e}\n"
        f"at h = 1e-15 the central error is {cen[-1]:.2e},\n"
        f"{cen[-1] / cen[i_c]:.1e}x worse than its own best",
        transform=ax.transAxes,
        va="bottom",
        color=p.fg,
        fontsize=7.8,
        family="monospace",
    )


def taylor_degrees(fig, ax, p: Palette) -> None:
    """T_0 .. T_5 of sin + cos at 0, with both error measures."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.35, 1]})

    f = lambda x: np.sin(x) + np.cos(x)
    # Coefficients a_k = f^(k)(0)/k!; f^(k)(0) = sin(k pi/2) + cos(k pi/2), which
    # cycles +1, +1, -1, -1 with period four.
    K = 8
    coeff = np.array(
        [
            (np.sin(k * np.pi / 2) + np.cos(k * np.pi / 2)) / math.factorial(k)
            for k in range(K + 1)
        ]
    )

    xs = np.linspace(-4, 4, 601)
    left.plot(xs, f(xs), color=p.fg, linewidth=2.6, label="$f$", zorder=5)

    colours = [p.red, p.amber, p.purple, p.blue, p.green, p.muted]
    near = 0.5
    rows = []
    for n, colour in zip(range(6), colours):
        T = sum(coeff[k] * xs ** k for k in range(n + 1))
        left.plot(xs, T, color=colour, linewidth=1.5, linestyle="--", alpha=0.9,
                  label=f"$T_{n}$")
        err = np.abs(f(xs) - T)
        rows.append((n, err[np.abs(xs) <= near].max(), err.max()))

    left.set_xlabel("$x$")
    left.set_ylabel("$f(x)$")
    left.set_title("$f(x) = \\sin x + \\cos x$ at $x_0 = 0$", fontsize=10.5)
    left.set_ylim(-3.2, 3.2)
    left.axvspan(-near, near, color=p.green, alpha=0.08)
    left.legend(loc="lower center", fontsize=7.6, ncol=4)

    ns = [r[0] for r in rows]
    right.semilogy(ns, [r[1] for r in rows], "o-", color=p.green, linewidth=2.0,
                   label=f"max error on $|x| \\leq {near}$")
    right.semilogy(ns, [r[2] for r in rows], "s--", color=p.red, linewidth=2.0,
                   label="max error on $|x| \\leq 4$")
    right.set_xlabel("degree $n$")
    right.set_ylabel("error")
    right.set_title("near $x_0$ it falls; far away it does not", fontsize=10.5)
    right.set_xticks(ns)
    right.legend(loc="lower left", fontsize=8)
    right.text(
        0.97,
        0.97,
        "\n".join(f"n={r[0]}  near {r[1]:.2e}  far {r[2]:.2f}" for r in rows),
        transform=right.transAxes,
        ha="right",
        va="top",
        color=p.fg,
        fontsize=7.4,
        family="monospace",
    )


FIGURES = [
    figure("secant-to-tangent", secant_to_tangent, size=(8.6, 4.8)),
    figure("difference-quotient-floor", difference_quotient_floor, size=(8.2, 4.8)),
    figure("taylor-degrees", taylor_degrees, size=(11.0, 4.4), axes=False),
]

"""Figures for *Single-Variable Calculus Refresher*.

1. `riemann-convergence` — the error of the left, right and midpoint Riemann
   sums against the number of rectangles, on log axes. The endpoint rules sit on
   a line of slope -1 and the midpoint rule on a line of slope -2, so the
   accuracy order is something you read off the plot rather than take on trust.
   It is the same cancellation argument that makes the central difference beat
   the forward difference, which is the second figure.

2. `finite-difference-u` — the U-shaped error of a numerical derivative. The
   falling branch is mathematics (truncation error), the rising branch is
   floating point (cancellation), and the minimum is the step size to actually
   use. Section 5.5's gradient check depends on knowing where that minimum is.
"""

import numpy as np

from _style import Palette, figure

# A function with nonzero curvature everywhere on the interval, so no rule is
# accidentally exact. Its integral over [0, 2] is known in closed form.
_F = lambda x: 0.55 * x**2 + 0.4
_A, _B = 0.0, 2.6
_EXACT = 0.55 * _B**3 / 3 + 0.4 * _B


def _riemann(n: int, rule: str) -> float:
    edges = np.linspace(_A, _B, n + 1)
    dx = (_B - _A) / n
    if rule == "left":
        xs = edges[:-1]
    elif rule == "right":
        xs = edges[1:]
    else:
        xs = (edges[:-1] + edges[1:]) / 2
    return float(_F(xs).sum() * dx)


def riemann_convergence(fig, ax, p: Palette) -> None:
    """Error against the number of rectangles, for the three rules."""
    ns = np.unique(np.logspace(0.3, 3.5, 30).astype(int))

    styles = [
        ("left", p.red, "-", "left endpoint"),
        ("right", p.green, "-", "right endpoint"),
        ("mid", p.blue, "-", "midpoint"),
    ]
    for rule, colour, ls, label in styles:
        errs = [abs(_riemann(int(n), rule) - _EXACT) for n in ns]
        ax.loglog(ns, errs, color=colour, linestyle=ls, linewidth=2, label=label)

    # Reference slopes, so the reader can read the order off the plot.
    ax.loglog(ns, 3.0 / ns, color=p.muted, linewidth=1, linestyle=":", label=r"slope $-1$: error $\propto 1/n$")
    ax.loglog(ns, 3.0 / ns**2, color=p.purple, linewidth=1, linestyle=":", label=r"slope $-2$: error $\propto 1/n^2$")

    ax.set_xlabel("number of rectangles $n$")
    ax.set_ylabel("absolute error")
    ax.legend(loc="lower left", fontsize=8.5)


def finite_difference_u(fig, ax, p: Palette) -> None:
    """The truncation-versus-rounding tradeoff, for forward and central differences."""
    hs = np.logspace(-1, -15, 120)
    x = 1.0
    exact = np.exp(x)

    forward = np.abs((np.exp(x + hs) - np.exp(x)) / hs - exact)
    central = np.abs((np.exp(x + hs) - np.exp(x - hs)) / (2 * hs) - exact)

    ax.loglog(hs, forward, color=p.red, linewidth=2, label="forward difference")
    ax.loglog(hs, central, color=p.blue, linewidth=2, label="central difference")

    # The two competing effects, drawn as the asymptotes they are.
    eps = np.finfo(float).eps
    ax.loglog(hs, 0.5 * exact * hs, color=p.muted, linestyle=":", linewidth=1.1,
              label=r"truncation $\propto h$")
    ax.loglog(hs, exact * eps / hs, color=p.purple, linestyle=":", linewidth=1.1,
              label=r"rounding $\propto \varepsilon/h$")

    best = hs[int(np.argmin(central))]
    ax.axvline(best, color=p.amber, linewidth=1.3, linestyle="--")
    ax.annotate(
        f"best $h \\approx {best:.0e}$",
        xy=(best, central.min()), xytext=(best * 90, central.min() * 260),
        color=p.amber, fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1),
    )

    ax.set_xlabel("step size $h$")
    ax.set_ylabel(r"error in $\mathrm{d}e^x/\mathrm{d}x$ at $x=1$")
    ax.invert_xaxis()
    ax.set_ylim(1e-12, 1e2)
    ax.legend(loc="upper center", fontsize=8.5, ncol=2)


FIGURES = [
    figure("riemann-convergence", riemann_convergence, size=(7.4, 4.2)),
    figure("finite-difference-u", finite_difference_u, size=(7.4, 4.4)),
]

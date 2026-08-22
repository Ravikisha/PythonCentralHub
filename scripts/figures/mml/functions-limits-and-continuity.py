"""Figures for *Functions, Limits, and Continuity*.

Two figures, each making one claim the prose cannot make on its own:

1. `three-failures` — continuous and differentiable, continuous only, and
   neither, side by side. The middle panel is the one that matters: the pen
   never lifts, so it is continuous, and yet there is no single tangent. That is
   ReLU's shape, and it is why the derivative of the most common activation
   function in deep learning does not exist at one point.

2. `secant-convergence` — the one-sided difference quotients plotted against the
   step size. For a smooth function they converge; for a corner they settle on
   two different numbers and the gap never closes. The distinction between "the
   gap shrinks with h" and "the gap is flat" is what section 5.5's gradient
   check relies on.
"""

import numpy as np

from _style import Palette, figure


def three_failures(fig, ax, p: Palette) -> None:
    """Three panels: smooth, corner, jump."""
    fig.clear()
    axes = fig.subplots(1, 3)

    x = np.linspace(-1.6, 1.6, 601)

    # --- smooth: x^2, with its tangent at the origin -----------------------
    a = axes[0]
    a.plot(x, x**2, color=p.blue, linewidth=2.2)
    a.plot(x, np.zeros_like(x), color=p.amber, linewidth=1.4, linestyle="--")
    a.plot([0], [0], marker="o", color=p.amber, markersize=6)
    a.set_title("continuous and differentiable")
    a.text(0.03, 0.92, r"$f(x)=x^2$", transform=a.transAxes, color=p.fg, fontsize=10)
    a.text(
        0.03, 0.82,
        "one tangent, slope 0",
        transform=a.transAxes, color=p.muted, fontsize=9,
    )

    # --- corner: |x|, with both one-sided slopes drawn ---------------------
    a = axes[1]
    a.plot(x, np.abs(x), color=p.blue, linewidth=2.2)
    # The two candidate tangents. Neither wins, which is the point.
    a.plot(x[x <= 0.9], -x[x <= 0.9], color=p.red, linewidth=1.3, linestyle="--")
    a.plot(x[x >= -0.9], x[x >= -0.9], color=p.green, linewidth=1.3, linestyle="--")
    a.plot([0], [0], marker="o", color=p.amber, markersize=6)
    a.set_title("continuous, not differentiable")
    a.text(0.03, 0.92, r"$f(x)=|x|$", transform=a.transAxes, color=p.fg, fontsize=10)
    a.text(0.03, 0.82, "slope $-1$ from the left", transform=a.transAxes, color=p.red, fontsize=9)
    a.text(0.03, 0.72, "slope $+1$ from the right", transform=a.transAxes, color=p.green, fontsize=9)

    # --- jump: sign(x). Open circles mark values not attained -------------
    a = axes[2]
    neg = x[x < 0]
    pos = x[x > 0]
    a.plot(neg, np.full_like(neg, -1.0), color=p.blue, linewidth=2.2)
    a.plot(pos, np.full_like(pos, 1.0), color=p.blue, linewidth=2.2)
    # Filled dot at the defined value, hollow dots at the two limits.
    a.plot([0], [0], marker="o", color=p.amber, markersize=6, zorder=5)
    for y in (-1.0, 1.0):
        a.plot([0], [y], marker="o", markerfacecolor=p.bg,
               markeredgecolor=p.blue, markeredgewidth=1.6, markersize=6, zorder=5)
    a.set_title("neither")
    a.text(0.03, 0.92, r"$f(x)=\mathrm{sign}(x)$", transform=a.transAxes, color=p.fg, fontsize=10)
    a.text(0.03, 0.82, "limits $-1$ and $+1$ disagree", transform=a.transAxes, color=p.muted, fontsize=9)
    a.text(0.03, 0.72, r"$f(0)=0$ is defined anyway", transform=a.transAxes, color=p.amber, fontsize=9)

    for a in axes:
        a.set_xlabel("$x$")
        a.set_xlim(-1.6, 1.6)
        a.axhline(0, color=p.grid, linewidth=0.9)
        a.axvline(0, color=p.grid, linewidth=0.9)
    axes[0].set_ylabel("$f(x)$")
    axes[0].set_ylim(-0.3, 2.6)
    axes[1].set_ylim(-1.7, 1.7)
    axes[2].set_ylim(-1.7, 1.7)


def secant_convergence(fig, ax, p: Palette) -> None:
    """One-sided difference quotients against h, smooth versus corner."""
    fig.clear()
    axes = fig.subplots(1, 2)

    hs = np.logspace(-1, -8, 40)

    # A smooth function whose derivative at the point is not zero, so the
    # convergence is visible rather than trivially exact.
    f_smooth = lambda t: t**2 + 0.6 * t
    right_s = (f_smooth(0 + hs) - f_smooth(0)) / hs
    left_s = (f_smooth(0 - hs) - f_smooth(0)) / -hs

    a = axes[0]
    a.semilogx(hs, right_s, color=p.blue, linewidth=2, label="from the right")
    a.semilogx(hs, left_s, color=p.red, linewidth=2, linestyle="--", label="from the left")
    a.axhline(0.6, color=p.amber, linewidth=1.2, linestyle=":", label="true derivative 0.6")
    a.set_title(r"smooth: $x^2 + 0.6x$ at $x=0$")
    a.set_xlabel("step size $h$")
    a.set_ylabel("difference quotient")
    a.legend(loc="center right")
    a.invert_xaxis()

    right_c = (np.abs(0 + hs) - 0.0) / hs
    left_c = (np.abs(0 - hs) - 0.0) / -hs

    a = axes[1]
    a.semilogx(hs, right_c, color=p.blue, linewidth=2, label="from the right")
    a.semilogx(hs, left_c, color=p.red, linewidth=2, linestyle="--", label="from the left")
    a.fill_between(hs, left_c, right_c, color=p.amber, alpha=0.15)
    a.annotate(
        "gap stays at 2\nno matter how small $h$ gets",
        xy=(1e-5, 0.0), xytext=(1e-3, -0.55),
        color=p.amber, fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1),
    )
    a.set_title(r"corner: $|x|$ at $x=0$")
    a.set_xlabel("step size $h$")
    a.set_ylim(-1.6, 1.6)
    a.legend(loc="center right")
    a.invert_xaxis()


FIGURES = [
    figure("three-failures", three_failures, size=(9.4, 3.3), axes=False),
    figure("secant-convergence", secant_convergence, size=(9.0, 3.6), axes=False),
]

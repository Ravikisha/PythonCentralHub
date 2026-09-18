"""Figures for *Legendre-Fenchel Transform and Convex Conjugate*.

1. `the-conjugate-is-an-intercept` — Definition 7.4 read geometrically. Fix a
   slope s, slide a line of that slope up until it just touches the graph, and
   the NEGATIVE of its y-intercept is f*(s). Drawn for f(x) = x^2, where the
   answer s^2/4 is known and matches to 1.8e-15.

2. `f-double-star-is-the-convex-envelope` — the fact that ties this section back
   to Section 7.2. Transforming twice returns the original function when it is
   convex, and its convex ENVELOPE when it is not. For x^4 - 3x^2 the envelope is
   flat at -2.25 across the entire hill, losing 2.25 at the origin — the same
   information the duality gap loses.

3. `the-smoothed-hinge` — Exercise 7.11 worked out. The hinge loss, its conjugate
   (beta on [-1,0] and infinite elsewhere), and the Moreau envelope you get by
   adding a proximal term and conjugating back: differentiable everywhere, and
   sitting exactly gamma/2 below the hinge on the linear branch.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _conj(fv, xs, ss, chunk=200):
    """f*(s) = sup_x (s x - f(x)) on a grid, chunked over s."""
    out = np.empty(ss.size)
    for i in range(0, ss.size, chunk):
        blk = ss[i:i + chunk]
        out[i:i + chunk] = (blk[:, None] * xs[None, :] - fv[None, :]).max(axis=1)
    return out


def the_conjugate_is_an_intercept(fig, ax, p: Palette) -> None:
    """Definition 7.4 as a picture about tangent lines."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(-2.6, 2.6, 900)
    left.plot(xs, xs ** 2, color=p.blue, linewidth=2.6, label="$f(x) = x^2$")
    left.axhline(0, color=p.grid, linewidth=1.0)
    left.axvline(0, color=p.grid, linewidth=1.0)

    for s, col in ((1.0, p.green), (2.5, p.amber), (-2.0, p.purple)):
        x0 = s / 2.0                                # where the tangent touches
        c = x0 ** 2 - s * x0                        # the y-intercept
        left.plot(xs, s * xs + c, color=col, linewidth=1.7, linestyle="--")
        left.plot([x0], [x0 ** 2], "o", color=col, markersize=7, zorder=6)
        left.plot([0.0], [c], "s", color=col, markersize=7, zorder=6)
        left.annotate(f"$s={s}$", xy=(x0, x0 ** 2), xytext=(6, 8),
                      textcoords="offset points", fontsize=8.2, color=col,
                      family="monospace")
        left.annotate(f"$-c = {-c:.4f} = f^*({s})$", xy=(0.0, c),
                      xytext=(10, -3), textcoords="offset points",
                      fontsize=7.8, color=col, family="monospace")
    left.set_xlabel("$x$")
    left.set_ylabel("$f(x)$")
    left.set_ylim(-2.6, 6.8)
    left.set_title("Slide a line of slope $s$ up until it touches",
                   fontsize=9.8)
    left.legend(fontsize=8, loc="upper center")
    left.grid(alpha=0.18, linewidth=0.6)
    left.text(
        0.02, 0.03,
        "Eq 7.54: the line through $(x_0, f(x_0))$\nwith slope $s$ is "
        "$y - f(x_0) = s(x - x_0)$.\nIts intercept is $f(x_0) - sx_0$, and\n"
        "Eq 7.55 takes the infimum of that.\nThe conjugate is its NEGATIVE.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    # the conjugate itself, numeric against closed form
    xg = np.linspace(-40, 40, 80001)
    sg = np.linspace(-6, 6, 1201)
    num = _conj(xg ** 2, xg, sg)
    right.plot(sg, num, color=p.blue, linewidth=3.4, alpha=0.45,
               label="numeric, Definition 7.4 on a grid")
    right.plot(sg, sg ** 2 / 4, color=p.amber, linewidth=1.8, linestyle="--",
               label="$f^*(s) = s^2/4$")
    for s, col in ((1.0, p.green), (2.5, p.amber), (-2.0, p.purple)):
        right.plot([s], [s ** 2 / 4], "o", color=col, markersize=7, zorder=6)
    right.set_xlabel("$s$, a slope of $f$")
    right.set_ylabel("$f^*(s)$")
    right.set_title("The conjugate is a function of the SLOPE", fontsize=9.8)
    right.legend(fontsize=8, loc="upper center")
    right.grid(alpha=0.18, linewidth=0.6)
    right.text(
        0.03, 0.62,
        f"max |numeric $-\\ s^2/4$| = "
        f"{np.abs(num - sg ** 2 / 4).max():.1e}\n\n"
        "The maximiser is $x = s/2$, so\nthe slope of $f^*$ at $s$ is the $x$\n"
        "that produced it. The transform\nswaps the roles of position and\nslope.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "A convex function can be described by its tangent lines instead of "
        "its values",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "This is the whole content of Definition 7.4. A convex set is the "
        "intersection of its supporting half-planes; fill in a convex function "
        "and the same is true\nof its epigraph. So instead of listing "
        "$f(x)$ for every $x$, list the intercept of the supporting line for "
        "every slope $s$ — no information is lost, and\nfor a differentiable "
        "convex function the correspondence is one to one.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def f_double_star_is_the_convex_envelope(fig, ax, p: Palette) -> None:
    """Transform twice: identity for convex, envelope otherwise."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xg = np.linspace(-30, 30, 60001)
    sg = np.linspace(-40, 40, 4001)

    # convex case
    xd = np.linspace(-2.6, 2.6, 601)
    fs = _conj(xg ** 2, xg, sg)
    fss = _conj(fs, sg, xd)          # same shape of computation, roles swapped
    left.plot(xd, xd ** 2, color=p.blue, linewidth=3.4, alpha=0.45,
              label="$f(x) = x^2$")
    left.plot(xd, fss, color=p.green, linewidth=1.8, linestyle="--",
              label="$f^{**}$, transformed twice")
    err_convex = float(np.abs(fss - xd ** 2).max())

    # nonconvex case
    f2 = lambda t: t ** 4 - 3.0 * t ** 2
    xg2 = np.linspace(-6, 6, 120001)
    sg2 = np.linspace(-60, 60, 6001)
    fs2 = _conj(f2(xg2), xg2, sg2)
    xd2 = np.linspace(-2.2, 2.2, 2201)
    fss2 = _conj(fs2, sg2, xd2)
    well = -2.25
    edge = np.sqrt(1.5)

    right.plot(xd2, f2(xd2), color=p.red, linewidth=2.4,
               label="$f(x) = x^4 - 3x^2$")
    right.plot(xd2, fss2, color=p.green, linewidth=2.4, linestyle="--",
               label="$f^{**}$, the convex ENVELOPE")
    right.fill_between(xd2, fss2, f2(xd2), where=f2(xd2) > fss2 + 1e-9,
                       color=p.amber, alpha=0.20, linewidth=0,
                       label="what the transform threw away")
    right.plot([-edge, edge], [well, well], "o", color=p.blue, markersize=7,
               zorder=6)
    gap = float((f2(xd2) - fss2).max())
    right.annotate(
        f"$f(0) - f^{{**}}(0) = {gap:.6f}$\nthe hill is GONE",
        xy=(0.0, 0.5 * (f2(0.0) + well)), xytext=(0.0, 3.2),
        ha="center", fontsize=8.2, color=p.amber, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.2))
    right.text(0.0, well - 0.9,
               f"$f^{{**}}$ is flat at ${well}$ across\n"
               f"$[-{edge:.6f},\\ {edge:.6f}]$",
               ha="center", va="top", fontsize=7.8, color=p.green,
               family="monospace")

    for axx, ttl in ((left, "Convex in, the same function out"),
                     (right, "Nonconvex in, the envelope out")):
        axx.set_xlabel("$x$")
        axx.set_title(ttl, fontsize=9.8)
        axx.legend(fontsize=7.8, loc="upper center")
        axx.grid(alpha=0.18, linewidth=0.6)
    left.set_ylabel("value")
    left.text(0.03, 0.55,
              f"max |$f^{{**}} - f$| on this range:\n  {err_convex:.1e}\n\n"
              "For a convex function the\ntransform is an involution:\n"
              "applying it twice is the\nidentity, so nothing is lost.",
              transform=left.transAxes, ha="left", va="top", fontsize=7.6,
              color=p.fg, family="monospace")
    right.set_ylim(-4.2, 5.6)

    fig.suptitle(
        "Transforming twice recovers a convex function exactly, and a "
        "nonconvex one only up to its envelope",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"The right panel is the duality gap of $\\S7.2$ seen from the other "
        f"side. $f^{{**}}$ is the largest convex function below $f$, so it "
        f"cannot represent a hill:\nacross $[-1.2247,\\ 1.2247]$ it is a flat "
        f"$-2.25$, and at the origin it is {gap:.4f} below the true value. Any "
        "method that only ever sees $f^{**}$ — and the\nLagrangian dual is such "
        "a method, since $D$ is always concave — is blind to exactly that much.",
        ha="center", va="bottom", fontsize=8.1, color=p.muted)


def the_smoothed_hinge(fig, ax, p: Palette) -> None:
    """Exercise 7.11, worked and measured."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    hinge = lambda a: np.maximum(0.0, 1.0 - a)
    al = np.linspace(-1.6, 2.6, 1200)

    a1.plot(al, hinge(al), color=p.blue, linewidth=2.6,
            label="$L(\\alpha) = \\max(0, 1-\\alpha)$")
    a1.plot([1.0], [0.0], "o", color=p.red, markersize=9,
            markerfacecolor="none", markeredgewidth=2.0)
    a1.annotate("a KINK at $\\alpha = 1$:\nno derivative here, so\nL-BFGS cannot "
                "be used",
                xy=(1.0, 0.0), xytext=(0.30, 0.62),
                textcoords="axes fraction", fontsize=7.8, color=p.red,
                family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    a1.set_xlabel("$\\alpha$")
    a1.set_ylabel("loss")
    a1.set_title("The hinge loss", fontsize=9.6)
    a1.legend(fontsize=7.8, loc="upper right")
    a1.grid(alpha=0.18, linewidth=0.6)

    # the conjugate
    be = np.linspace(-1.7, 0.7, 1200)
    star = np.where((be >= -1.0) & (be <= 0.0), be, np.nan)
    a2.plot(be, star, color=p.green, linewidth=2.8,
            label="$L^*(\\beta) = \\beta$ on $[-1, 0]$")
    a2.axvspan(-1.7, -1.0, color=p.red, alpha=0.14, linewidth=0)
    a2.axvspan(0.0, 0.7, color=p.red, alpha=0.14, linewidth=0)
    a2.text(-1.35, -0.5, "$+\\infty$", ha="center", fontsize=13, color=p.red)
    a2.text(0.35, -0.5, "$+\\infty$", ha="center", fontsize=13, color=p.red)
    a2.plot([-1.0, 0.0], [-1.0, 0.0], "o", color=p.green, markersize=7)
    a2.set_xlabel("$\\beta$")
    a2.set_ylabel("$L^*(\\beta)$")
    a2.set_ylim(-1.25, 0.35)
    a2.set_title("Its conjugate", fontsize=9.6)
    a2.legend(fontsize=7.8, loc="lower right")
    a2.grid(alpha=0.18, linewidth=0.6)
    a2.text(0.03, 0.97,
            "measured on a grid:\nmax |$L^*(\\beta) - \\beta$| on\n"
            "$[-1,0]$ is $3.6\\times10^{-15}$.\n\n"
            "Outside, the supremum is\nunbounded — 29.0 and 30.0\n"
            "on an $\\alpha$ grid capped at 60.",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.4,
            color=p.fg, family="monospace")

    # the Moreau envelope for several gamma
    def smoothed(a, gam):
        return np.where(a >= 1.0, 0.0,
                        np.where(a >= 1.0 - gam,
                                 (1.0 - a) ** 2 / (2 * gam),
                                 1.0 - a - gam / 2))

    a3.plot(al, hinge(al), color=p.muted, linewidth=1.8, linestyle=":",
            label="the hinge")
    for gam, col in ((0.2, p.green), (0.6, p.amber), (1.2, p.purple)):
        a3.plot(al, smoothed(al, gam), color=col, linewidth=2.2,
                label=f"$\\gamma = {gam}$")
    a3.set_xlabel("$\\alpha$")
    a3.set_title("Add $\\frac{\\gamma}{2}\\beta^2$, conjugate back",
                 fontsize=9.6)
    a3.legend(fontsize=7.6, loc="upper right")
    a3.grid(alpha=0.18, linewidth=0.6)
    a3.text(
        0.03, 0.42,
        "three branches:\n"
        "  $0$ for $\\alpha \\geq 1$\n"
        "  $(1-\\alpha)^2/(2\\gamma)$ on $[1-\\gamma, 1]$\n"
        "  $1-\\alpha-\\gamma/2$ below that\n\n"
        "$C^1$ at both joins (measured\nslope jump $8\\times10^{-8}$), and it "
        "sits\nexactly $\\gamma/2$ below the hinge\non the linear branch.",
        transform=a3.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Exercise 7.11: smoothing a kink by a round trip through the conjugate",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The hinge is convex but not differentiable, so gradient methods such as "
        "L-BFGS do not apply. Conjugating gives a function on a box; adding a "
        "quadratic\nproximal term and conjugating back gives a differentiable "
        "loss. The price is a uniform shift: the smoothed loss is $\\gamma/2$ "
        "below the hinge wherever the\nhinge is linear, so $\\gamma$ trades "
        "smoothness against fidelity — and at $\\gamma = 0.6$ that shift is a "
        "measured $0.300000$.",
        ha="center", va="bottom", fontsize=8.1, color=p.muted)


FIGURES = [
    figure("the-conjugate-is-an-intercept", the_conjugate_is_an_intercept,
           size=(12.4, 4.9), axes=False),
    figure("f-double-star-is-the-convex-envelope",
           f_double_star_is_the_convex_envelope, size=(12.6, 5.0), axes=False),
    figure("the-smoothed-hinge", the_smoothed_hinge, size=(13.8, 4.9),
           axes=False),
]

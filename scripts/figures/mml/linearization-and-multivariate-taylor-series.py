"""Figures for *Linearization and Multivariate Taylor Series*.

1. `linear-then-quadratic` — Eq 5.148's linearisation and the second-order term
   that follows it, on one surface. Three panels: the function, the tangent plane,
   and the quadratic approximation, with the error of each measured on a disc
   around the expansion point. The linear model is exact along the contour through
   the point and wrong everywhere else; the quadratic one fixes the curvature.

2. `taylor-order-convergence` — the multivariate error, measured. On a disc of
   radius r the order-k Taylor error should scale like r^(k+1), and the figure
   fits the observed slope for k = 0, 1, 2 rather than asserting the exponent. It
   also counts the TERMS at each order, which is the cost the book's Eq 5.151
   hides: the number of k-th order partials in D variables grows combinatorially.

3. `laplace-approximation` — the reason §5.8 is in a machine-learning book. A
   second-order Taylor expansion of a log-density at its mode IS a Gaussian
   approximation, and the figure fits one to a skewed density, showing where it
   agrees and where it does not. The mismatch is measured as a mass error, not
   left as a visual impression.
"""

from __future__ import annotations

import math

import numpy as np

from _style import Palette, figure

# A surface with genuine curvature in both directions and a non-zero cross term.
f = lambda x, y: np.sin(x) * np.cos(0.8 * y) + 0.25 * x * y
fx = lambda x, y: np.cos(x) * np.cos(0.8 * y) + 0.25 * y
fy = lambda x, y: -0.8 * np.sin(x) * np.sin(0.8 * y) + 0.25 * x
fxx = lambda x, y: -np.sin(x) * np.cos(0.8 * y)
fxy = lambda x, y: -0.8 * np.cos(x) * np.sin(0.8 * y) + 0.25
fyy = lambda x, y: -0.64 * np.sin(x) * np.cos(0.8 * y)

X0, Y0 = 0.7, 0.5


def _t0(x, y):
    return np.full_like(np.asarray(x, dtype=float), f(X0, Y0))


def _t1(x, y):
    dx = x - X0
    dy = y - Y0
    return f(X0, Y0) + fx(X0, Y0) * dx + fy(X0, Y0) * dy


def _t2(x, y):
    dx = x - X0
    dy = y - Y0
    return _t1(x, y) + 0.5 * (
        fxx(X0, Y0) * dx**2 + 2 * fxy(X0, Y0) * dx * dy + fyy(X0, Y0) * dy**2
    )


def linear_then_quadratic(fig, ax, p: Palette) -> None:
    """The function, its tangent plane, and its quadratic model."""
    fig.clear()
    axes = fig.subplots(1, 3, sharex=True, sharey=True)

    g = np.linspace(-1.4, 2.8, 240)
    X, Y = np.meshgrid(g, g)
    Z = f(X, Y)
    levels = np.linspace(Z.min(), Z.max(), 13)

    # Error on a disc, so "how good" is a number and not an impression.
    th = np.linspace(0, 2 * np.pi, 400)
    rad = np.linspace(0, 1.0, 60)[1:]
    RR, TT = np.meshgrid(rad, th)
    PX = X0 + RR * np.cos(TT)
    PY = Y0 + RR * np.sin(TT)
    truth = f(PX, PY)

    for a, (name, approx, colour) in zip(
        axes,
        [
            ("$T_0$: the value", _t0, p.red),
            ("$T_1$: the tangent plane (Eq 5.148)", _t1, p.amber),
            ("$T_2$: plus the Hessian term", _t2, p.green),
        ],
    ):
        a.contour(X, Y, Z, levels=levels, colors=p.muted, linewidths=0.9, alpha=0.55)
        a.contour(X, Y, approx(X, Y), levels=levels, colors=colour,
                  linewidths=1.5, linestyles="--")
        a.plot([X0], [Y0], "o", color=p.fg, markersize=6, zorder=5)
        a.set_aspect("equal")
        a.set_title(name, fontsize=9.5, color=colour)
        a.set_xlabel("$x_1$")

        err = np.abs(truth - approx(PX, PY))
        a.text(
            0.5, -0.15,
            f"max error on the unit disc: {err.max():.4f}\n"
            f"mean error: {err.mean():.4f}",
            transform=a.transAxes, ha="center", va="top",
            color=p.fg, fontsize=7.6, family="monospace",
        )

    axes[0].set_ylabel("$x_2$")
    fig.text(
        0.5, 1.0,
        f"$f(x) = \\sin x_1\\cos(0.8x_2) + 0.25x_1x_2$ expanded at $({X0}, {Y0})$; "
        "grey is $f$, dashed is the approximation",
        ha="center", va="bottom", color=p.fg, fontsize=9.5,
    )


def taylor_order_convergence(fig, ax, p: Palette) -> None:
    """The error order, fitted; and the term count, which is the hidden cost."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1]})

    th = np.linspace(0, 2 * np.pi, 720)
    radii = np.logspace(0, -3, 22)

    fits = []
    for name, approx, colour, k in (
        ("$T_0$", _t0, p.red, 0),
        ("$T_1$", _t1, p.amber, 1),
        ("$T_2$", _t2, p.green, 2),
    ):
        errs = []
        for r in radii:
            px = X0 + r * np.cos(th)
            py = Y0 + r * np.sin(th)
            errs.append(float(np.abs(f(px, py) - approx(px, py)).max()))
        errs = np.array(errs)
        left.loglog(radii, np.maximum(errs, 1e-18), "o-", color=colour, linewidth=2.0,
                    markersize=3, label=f"{name}, expect $r^{{{k + 1}}}$")
        # Fit the slope where the error is above the round-off floor.
        m = (errs > 1e-13) & (radii < 0.3)
        slope = np.polyfit(np.log10(radii[m]), np.log10(errs[m]), 1)[0] if m.sum() > 3 else np.nan
        fits.append((name, k + 1, slope))

    left.set_xlabel("radius $r$ of the disc")
    left.set_ylabel("max error on the disc")
    left.invert_xaxis()
    left.set_title("the order is measured, not assumed", fontsize=9.5)
    left.legend(loc="upper left", fontsize=8.2)
    left.text(
        0.03, 0.03,
        "  model  expected  fitted\n"
        + "\n".join(f"  {n:<6} r^{e:<8} r^{s:.3f}" for n, e, s in fits),
        transform=left.transAxes, va="bottom",
        color=p.fg, fontsize=7.8, family="monospace",
    )

    # The term count: how many k-th order partial derivatives are there in D
    # variables? Multiset coefficient C(D + k - 1, k), and the running total.
    Ds = [1, 2, 3, 5, 10, 50, 100]
    ks = [0, 1, 2, 3]
    width = 0.2
    xpos = np.arange(len(Ds))
    for i, k in enumerate(ks):
        counts = [math.comb(D + k - 1, k) for D in Ds]
        right.bar(xpos + (i - 1.5) * width, counts, width=width,
                  label=f"order {k}", alpha=0.9)
    right.set_yscale("log")
    right.set_xticks(xpos, [str(D) for D in Ds])
    right.set_xlabel("number of variables $D$")
    right.set_ylabel("distinct partial derivatives")
    right.set_title("why nobody goes past second order", fontsize=9.5)
    right.legend(loc="upper left", fontsize=8)
    right.text(
        0.97, 0.03,
        "  D     order 2   order 3\n"
        + "\n".join(f"  {D:<5} {math.comb(D + 1, 2):<9} {math.comb(D + 2, 3)}" for D in Ds),
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace",
    )


def laplace_approximation(fig, ax, p: Palette) -> None:
    """A second-order expansion of a log-density is a Gaussian."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1]})

    # A skewed density: a Gamma-like shape, unnormalised.
    a, b = 4.0, 1.6
    logp = lambda x: (a - 1) * np.log(x) - b * x
    dlogp = lambda x: (a - 1) / x - b
    d2logp = lambda x: -(a - 1) / x**2

    mode = (a - 1) / b
    curv = -d2logp(mode)               # positive; the Gaussian precision
    sigma = 1 / np.sqrt(curv)

    xs = np.linspace(0.05, 8.0, 800)
    dens = np.exp(logp(xs))
    dens = dens / np.trapezoid(dens, xs)
    gauss = np.exp(-0.5 * ((xs - mode) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

    left.plot(xs, dens, color=p.fg, linewidth=2.4, label="the density")
    left.plot(xs, gauss, color=p.green, linewidth=2.2, linestyle="--",
              label="Laplace: $\\mathcal{N}$(mode, $-1/f''$)")
    left.axvline(mode, color=p.amber, linewidth=1.2, linestyle=":")
    left.plot([mode], [dens[np.argmin(np.abs(xs - mode))]], "o", color=p.amber, markersize=7)
    left.set_xlabel("$x$")
    left.set_ylabel("density")
    left.set_title("the quadratic expansion of $\\log p$ at its mode", fontsize=9.5)
    left.legend(loc="upper right", fontsize=8.2)

    l1 = float(np.trapezoid(np.abs(dens - gauss), xs))
    left.text(
        0.98, 0.45,
        f"mode          {mode:.4f}\n"
        f"-1/f''(mode)  {1 / curv:.4f}\n"
        f"sigma         {sigma:.4f}\n\n"
        f"true mean     {float(np.trapezoid(xs * dens, xs)):.4f}\n"
        f"true sd       "
        f"{float(np.sqrt(np.trapezoid((xs - np.trapezoid(xs * dens, xs)) ** 2 * dens, xs))):.4f}\n\n"
        f"total variation\n"
        f"distance      {0.5 * l1:.4f}",
        transform=left.transAxes, ha="right", va="center",
        color=p.fg, fontsize=7.4, family="monospace",
    )

    # The log scale is where the approximation's nature is visible: a parabola.
    right.plot(xs, logp(xs) - logp(mode), color=p.fg, linewidth=2.4, label="$\\log p$, centred")
    quad = -0.5 * curv * (xs - mode) ** 2
    right.plot(xs, quad, color=p.green, linewidth=2.2, linestyle="--",
               label="its second-order Taylor term")
    lin = dlogp(mode) * (xs - mode)
    right.plot(xs, lin, color=p.amber, linewidth=1.6, linestyle=":",
               label="first-order term (flat: the mode)")
    right.axvline(mode, color=p.amber, linewidth=1.0, linestyle=":")
    right.set_ylim(-6, 1)
    right.set_xlabel("$x$")
    right.set_ylabel("$\\log p(x) - \\log p(\\mathrm{mode})$")
    right.set_title("on a log scale the Gaussian is a parabola", fontsize=9.5)
    right.legend(loc="lower center", fontsize=7.8)
    right.text(
        0.03, 0.05,
        f"the first-order term vanishes because\n"
        f"the expansion point is a MODE: f'(mode)\n"
        f"= {dlogp(mode):.1e}. That is what makes the\n"
        f"quadratic term the leading one, and the\n"
        f"approximation a Gaussian rather than an\n"
        f"exponential.",
        transform=right.transAxes, va="bottom",
        color=p.muted, fontsize=7.4, family="monospace",
    )


FIGURES = [
    figure("linear-then-quadratic", linear_then_quadratic, size=(11.4, 4.4), axes=False),
    figure("taylor-order-convergence", taylor_order_convergence, size=(11.0, 4.6), axes=False),
    figure("laplace-approximation", laplace_approximation, size=(11.2, 4.6), axes=False),
]

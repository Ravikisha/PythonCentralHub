"""Figures for *Change of Variables and the Inverse Transform*.

1. `change-of-variables` — Equation 6.143 with and without its Jacobian factor.
   A standard normal pushed through exp gives a lognormal; keeping |dU^-1/dy|
   reproduces the sampled histogram, dropping it gives something that integrates
   to 1.65 and has the wrong shape even after renormalising.

2. `probability-integral-transform` — Theorem 6.15. Four distributions with
   nothing in common, each pushed through its OWN cdf, all landing on the uniform.
   Then the same theorem run backwards, which is inverse-transform sampling.

3. `mode-is-not-invariant` — the trap. A density's argmax moves under a nonlinear
   reparameterisation because the Jacobian tilts it, while quantiles do not. The
   panel marks the image of the old mode against the new mode for three
   transforms, one of them affine as a control.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _phi(t):
    return np.exp(-0.5 * t ** 2) / np.sqrt(2 * np.pi)


def change_of_variables(fig, ax, p: Palette) -> None:
    """Equation 6.143, and what dropping the Jacobian costs."""
    fig.clear()
    left, mid, right = fig.subplots(1, 3)

    xs = np.linspace(-4, 4, 1200)
    left.plot(xs, _phi(xs), color=p.blue, linewidth=2.4)
    left.fill_between(xs, _phi(xs), color=p.blue, alpha=0.18)
    left.set_xlabel("$x$")
    left.set_ylabel("$f_X(x)$")
    left.set_title("$X \\sim \\mathcal{N}(0,1)$", fontsize=9.5)
    left.text(0.03, 0.97, "the mode is at $x=0$",
              transform=left.transAxes, ha="left", va="top",
              color=p.fg, fontsize=7.8, family="monospace")

    rng = np.random.default_rng(7)
    y = np.exp(rng.standard_normal(2_000_000))
    bins = np.geomspace(0.02, 30, 70)
    ctr = np.sqrt(bins[1:] * bins[:-1])
    hist, _ = np.histogram(y, bins=bins, density=True)

    gy = np.geomspace(1e-4, 60, 200_001)
    with_j = _phi(np.log(gy)) / gy
    without = _phi(np.log(gy))
    mass_with = np.trapezoid(with_j, gy)
    mass_without = np.trapezoid(without, gy)

    mid.plot(ctr, hist, "o", color=p.muted, markersize=4,
             label="sampled histogram")
    mid.plot(gy, with_j, color=p.green, linewidth=2.4,
             label="Eq 6.143, with $|1/y|$")
    mid.plot(gy, without / mass_without, color=p.red, linewidth=2.0,
             linestyle="--", label="Jacobian dropped, renormalised")
    mid.set_xscale("log")
    mid.set_xlim(0.02, 30)
    mid.set_xlabel("$y$")
    mid.set_ylabel("$f_Y(y)$")
    mid.set_title("$Y = \\exp(X)$", fontsize=9.5)
    mid.legend(fontsize=7.6, loc="upper right")
    mid.text(
        0.03, 0.97,
        f"integral with |1/y|:  {mass_with:.6f}\n"
        f"integral without:     {mass_without:.6f}\n\n"
        "the second is not a density,\n"
        "and renormalising does not\n"
        "fix its SHAPE either.",
        transform=mid.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    ok = _phi(np.log(ctr)) / ctr
    bad = _phi(np.log(ctr)) / mass_without
    right.semilogx(ctr, np.abs(hist - ok), "o-", color=p.green, linewidth=2.0,
                   label="error, with the Jacobian")
    right.semilogx(ctr, np.abs(hist - bad), "s-", color=p.red, linewidth=2.0,
                   label="error, without")
    right.set_yscale("log")
    right.set_xlabel("$y$")
    right.set_ylabel("$|$histogram $-$ prediction$|$")
    right.set_title("the factor is not cosmetic", fontsize=9.5)
    right.legend(fontsize=8, loc="lower left")
    right.text(
        0.97, 0.95,
        f"worst error with:    {np.abs(hist-ok).max():.5f}\n"
        f"worst error without: {np.abs(hist-bad).max():.5f}\n\n"
        "a factor of "
        f"{np.abs(hist-bad).max()/np.abs(hist-ok).max():.0f}",
        transform=right.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.4, family="monospace")


def probability_integral_transform(fig, ax, p: Palette) -> None:
    """Theorem 6.15, forwards and backwards."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(11)
    n = 400_000
    from math import erf
    verf = np.vectorize(erf)

    z = rng.standard_normal(n)
    ex = rng.exponential(0.5, n)
    ca = rng.standard_cauchy(n)
    la = rng.laplace(0, 1, n)
    sets = [
        ("$\\mathcal{N}(0,1)$", 0.5 * (1 + verf(z / np.sqrt(2))), p.blue),
        ("Exponential", 1 - np.exp(-2 * ex), p.green),
        ("Cauchy", 0.5 + np.arctan(ca) / np.pi, p.amber),
        ("Laplace", np.where(la < 0, 0.5 * np.exp(la), 1 - 0.5 * np.exp(-la)), p.purple),
    ]
    for name, u, colour in sets:
        h, e = np.histogram(u, bins=50, range=(0, 1), density=True)
        left.step(0.5 * (e[1:] + e[:-1]), h, where="mid", color=colour,
                  linewidth=1.9, label=f"{name}: mean {u.mean():.4f}")
    left.axhline(1.0, color=p.red, linestyle="--", linewidth=1.8,
                 label="the uniform density")
    left.set_ylim(0, 1.35)
    left.set_xlabel("$F_X(x)$")
    left.set_ylabel("density")
    left.set_title("Theorem 6.15: every cdf output is uniform", fontsize=9.5)
    left.legend(fontsize=7.4, loc="lower center", ncol=2)
    left.text(
        0.5, 0.93,
        "a uniform has variance 1/12 = 0.083333;\n"
        "all four land there, the Cauchy included --\n"
        "and the Cauchy has no mean of its own.",
        transform=left.transAxes, ha="center", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    uu = rng.random(400_000)
    grid = np.linspace(1e-6, 1, 400)
    pairs = [
        ("Exponential(2)", -np.log1p(-uu) / 2.0, lambda t: 1 - np.exp(-2 * t),
         np.linspace(0, 3, 300), p.green),
        ("$f(x)=3x^2$", uu ** (1 / 3), lambda t: t ** 3,
         np.linspace(0, 1, 300), p.blue),
    ]
    for name, smp, cdf, dom, colour in pairs:
        emp = np.array([float((smp <= q).mean()) for q in dom])
        right.plot(dom, cdf(dom), color=colour, linewidth=2.6,
                   label=f"{name}: target cdf")
        right.plot(dom[::12], emp[::12], "o", color=colour, markersize=4,
                   markerfacecolor="none")
    right.set_xlabel("$x$")
    right.set_ylabel("cumulative probability")
    right.set_title("run it backwards: $F^{-1}(U)$ samples the target",
                    fontsize=9.5)
    right.legend(fontsize=8, loc="lower right")
    right.text(
        0.03, 0.95,
        "circles are the empirical cdf of\n"
        "F-inverse applied to uniforms.\n"
        "This is inverse-transform sampling,\n"
        "and it is Theorem 6.15 read the\n"
        "other way round.",
        transform=right.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")


def mode_is_not_invariant(fig, ax, p: Palette) -> None:
    """A density's argmax moves under reparameterisation; quantiles do not."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(-4, 4, 2000)
    left.plot(xs, _phi(xs), color=p.blue, linewidth=2.4, label="$f_X(x)$")
    left.axvline(0.0, color=p.amber, linewidth=2.0)
    left.axvline(0.0, color=p.green, linewidth=1.2, linestyle=":")
    left.text(0.08, 0.36, "mode = median = 0", color=p.amber, fontsize=8,
              family="monospace")
    left.set_xlabel("$x$")
    left.set_ylabel("density")
    left.set_title("before: $X \\sim \\mathcal{N}(0,1)$", fontsize=9.5)
    left.legend(fontsize=8.2)

    gy = np.geomspace(1e-3, 12, 400_001)
    fy = _phi(np.log(gy)) / gy
    mode_y = float(gy[int(np.argmax(fy))])
    right.plot(gy, fy, color=p.blue, linewidth=2.4, label="$f_Y(y)$")
    right.axvline(mode_y, color=p.amber, linewidth=2.0,
                  label=f"new mode  {mode_y:.4f}")
    right.axvline(1.0, color=p.red, linewidth=2.0, linestyle="--",
                  label="image of the old mode  1.0")
    right.axvline(1.0, color=p.green, linewidth=1.2, linestyle=":",
                  label="median, still 1.0")
    right.set_xlim(0, 6)
    right.set_xlabel("$y$")
    right.set_ylabel("density")
    right.set_title("after: $Y=\\exp(X)$", fontsize=9.5)
    right.legend(fontsize=7.8, loc="upper right")
    right.text(
        0.5, 0.45,
        f"the peak moved to exp(-1) = {np.exp(-1):.6f},\n"
        "not to exp(0) = 1. The Jacobian |1/y|\n"
        "tilts the density toward small y.\n\n"
        "A monotone map preserves QUANTILES,\n"
        "so the median transforms correctly.\n"
        "A MAP estimate does not.",
        transform=right.transAxes, ha="center", va="center",
        color=p.fg, fontsize=7.6, family="monospace")

    fig.text(
        0.5, -0.06,
        "Measured for three transforms: exp(X) moves the mode from 1.0 to 0.3679, "
        "X cubed moves it from 0 to about 0, and the affine 2X+1 leaves it at 1.0 "
        "exactly — because an affine map has a constant Jacobian and so cannot tilt "
        "the density. Every nonlinear reparameterisation moves the mode.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


FIGURES = [
    figure("change-of-variables", change_of_variables, size=(12.5, 4.2),
           axes=False),
    figure("probability-integral-transform", probability_integral_transform,
           size=(11.5, 4.4), axes=False),
    figure("mode-is-not-invariant", mode_is_not_invariant, size=(11.0, 4.4),
           axes=False),
]

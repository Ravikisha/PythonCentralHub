"""Figures for *Conjugacy and the Exponential Family*.

1. `named-distributions` — the book's Figures 6.10 and 6.11 side by side: the
   Binomial for the three values of mu the book plots, and the Beta for the five
   parameter pairs it lists, annotated with which of its four special cases each
   one is.

2. `conjugacy-updates-parameters` — Example 6.11 as a sequence. The posterior
   after 0, 1, 10, ... observations, all of them Beta, and beside it the thing
   conjugacy buys: two stored numbers however much data arrives, against a grid
   whose size is exponential in the dimension.

3. `sufficient-statistics` — Theorem 6.14, measured. Two visibly different
   datasets constructed to share the same n, sum and sum of squares, and their
   Gaussian log-likelihood surfaces, which are identical to 2e-13. The likelihood
   cannot tell them apart, which is what "sufficient" means.

4. `exponential-family-link` — the natural parameter of Example 6.14. The map
   theta = log(mu/(1-mu)) and its inverse the sigmoid, and the fact that
   differentiating the log-partition function A(theta) returns the mean.
"""

from __future__ import annotations

import math

import numpy as np

from _style import Palette, figure

GRID = np.linspace(1e-6, 1 - 1e-6, 4001)


def _beta_pdf(a, b, g=GRID):
    logc = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    return np.exp(logc + (a - 1) * np.log(g) + (b - 1) * np.log1p(-g))


def named_distributions(fig, ax, p: Palette) -> None:
    """Figures 6.10 and 6.11, with the book's own parameter choices."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    N = 15
    ks = np.arange(N + 1)
    for mu, colour in ((0.1, p.blue), (0.4, p.green), (0.75, p.amber)):
        pmf = np.array([math.comb(N, k) * mu ** k * (1 - mu) ** (N - k) for k in ks])
        left.plot(ks, pmf, "o-", color=colour, linewidth=1.8, markersize=4,
                  label=f"$\\mu = {mu}$")
        left.axvline(N * mu, color=colour, linestyle=":", linewidth=1.1)
    left.set_xlabel(f"number $m$ of observations $x = 1$ in $N = {N}$ experiments")
    left.set_ylabel("$p(m)$")
    left.set_title("Figure 6.10: the Binomial", fontsize=9.5)
    left.legend(fontsize=8.2)
    left.text(
        0.97, 0.97,
        "Eq 6.96  E[m] = N mu\n"
        "Eq 6.97  V[m] = N mu (1-mu)\n\n"
        "dotted lines mark the means:\n"
        f"{N*0.1:.1f}, {N*0.4:.1f}, {N*0.75:.2f}",
        transform=left.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    cases = [
        (0.5, 0.5, p.red, "$\\alpha,\\beta<1$: spikes at 0 and 1"),
        (1.0, 1.0, p.muted, "$\\alpha=\\beta=1$: uniform"),
        (2.0, 0.3, p.purple, "mass toward 1"),
        (4.0, 10.0, p.blue, "$\\alpha,\\beta>1$: unimodal"),
        (5.0, 1.0, p.amber, "mass toward 1"),
        (5.0, 5.0, p.green, "$\\alpha=\\beta>1$: mode at 1/2"),
    ]
    for a, b, colour, label in cases:
        right.plot(GRID, _beta_pdf(a, b), color=colour, linewidth=2.0,
                   label=f"$\\alpha={a:g},\\ \\beta={b:g}$")
    right.set_ylim(0, 4.2)
    right.set_xlabel("$\\mu$")
    right.set_ylabel("$p(\\mu\\mid\\alpha,\\beta)$")
    right.set_title("Figure 6.11: the Beta", fontsize=9.5)
    right.legend(fontsize=7.4, ncol=2, loc="upper center")
    right.text(
        0.5, 0.02,
        "Eq 6.99  E[mu] = a/(a+b),  and the four cases the book lists:\n"
        "a=b=1 uniform;  a,b<1 bimodal;  a,b>1 unimodal;  a=b>1 symmetric",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace")


def conjugacy_updates_parameters(fig, ax, p: Palette) -> None:
    """Example 6.11 in sequence, and the cost conjugacy avoids."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(21)
    truth = 0.62
    data = (rng.random(2000) < truth).astype(int)
    a0 = b0 = 1.0

    shown = [0, 5, 20, 100, 500, 2000]
    cols = [p.muted, p.purple, p.blue, p.green, p.amber, p.red]
    for n, colour in zip(shown, cols):
        h = int(data[:n].sum())
        a, b = a0 + h, b0 + (n - h)
        left.plot(GRID, _beta_pdf(a, b), color=colour, linewidth=2.0,
                  label=f"$n={n}$: Beta({a:.0f}, {b:.0f})")
    left.axvline(truth, color=p.fg, linestyle=":", linewidth=1.6)
    left.text(truth + 0.008, left.get_ylim()[1] * 0.55, f"truth {truth}",
              color=p.fg, fontsize=8, family="monospace", rotation=90)
    left.set_xlim(0.3, 0.9)
    left.set_xlabel("$\\mu$")
    left.set_ylabel("posterior density")
    left.set_title("every posterior is a Beta — Eq 6.104d", fontsize=9.5)
    left.legend(fontsize=7.4, loc="upper left")
    left.text(
        0.97, 0.97,
        "the update is arithmetic:\n"
        "alpha <- alpha + heads\n"
        "beta  <- beta  + tails\n\n"
        "no integral is ever computed",
        transform=left.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    Ds = np.arange(1, 11)
    grid_cost = 200.0 ** Ds
    right.semilogy(Ds, grid_cost, "o-", color=p.red, linewidth=2.2,
                   label="grid posterior: $200^D$ numbers")
    right.semilogy(Ds, np.full_like(Ds, 2, dtype=float), "s-", color=p.green,
                   linewidth=2.2, label="conjugate: $\\dim(\\gamma)$ numbers")
    right.axhline(1e9, color=p.muted, linestyle=":", linewidth=1.3)
    right.text(1.2, 1.6e9, "a billion", color=p.muted, fontsize=8,
               family="monospace")
    right.set_xlabel("dimension $D$ of the parameter")
    right.set_ylabel("numbers you must store")
    right.set_title("desideratum 2: the parameter count must not grow",
                    fontsize=9.5)
    right.legend(fontsize=8, loc="center right")
    right.text(
        0.03, 0.03,
        "measured on the left panel: after 100000\n"
        "observations the posterior was still two\n"
        "numbers, Beta(61789, 38213). A grid at the\n"
        "same resolution costs 200^D, which is\n"
        "1.0e+23 by D = 10.",
        transform=right.transAxes, ha="left", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace")


def sufficient_statistics(fig, ax, p: Palette) -> None:
    """Theorem 6.14: two datasets, one likelihood."""
    fig.clear()
    left, mid, right = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1, 1, 1.1]})

    rng = np.random.default_rng(4)
    d1 = rng.normal(2.0, 1.5, 400)
    d2 = rng.normal(-3.0, 4.0, 400)
    d2 = (d2 - d2.mean()) / d2.std() * d1.std() + d1.mean()

    bins = np.linspace(-3, 7, 46)
    left.hist(d1, bins=bins, color=p.blue, alpha=0.85)
    left.set_title("dataset 1", fontsize=9.5, color=p.blue)
    left.set_xlabel("$x$")
    left.set_ylabel("count")
    mid.hist(d2, bins=bins, color=p.amber, alpha=0.85)
    mid.set_title("dataset 2", fontsize=9.5, color=p.amber)
    mid.set_xlabel("$x$")
    for a, d in ((left, d1), (mid, d2)):
        a.text(
            0.03, 0.97,
            f"n        {d.size}\n"
            f"sum x    {d.sum():.6f}\n"
            f"sum x^2  {np.sum(d**2):.6f}",
            transform=a.transAxes, ha="left", va="top",
            color=p.fg, fontsize=7.2, family="monospace")

    mus = np.linspace(0.5, 3.5, 160)
    sds = np.linspace(0.9, 2.6, 160)
    MU, SD = np.meshgrid(mus, sds)

    def ll(d):
        n = d.size
        s1, s2 = d.sum(), np.sum(d ** 2)
        return (-0.5 * n * np.log(2 * np.pi * SD ** 2)
                - (s2 - 2 * MU * s1 + n * MU ** 2) / (2 * SD ** 2))

    L1, L2 = ll(d1), ll(d2)
    cs = right.contour(MU, SD, L1, levels=14, colors=p.blue, linewidths=1.4)
    right.contour(MU, SD, L2, levels=cs.levels, colors=p.amber, linewidths=1.4,
                  linestyles="--")
    right.plot([d1.mean()], [d1.std()], "o", color=p.green, markersize=8,
               zorder=5)
    right.set_xlabel("$\\mu$")
    right.set_ylabel("$\\sigma$")
    right.set_title("their log-likelihoods, overlaid", fontsize=9.5)
    right.text(
        0.03, 0.03,
        f"solid blue and dashed amber\n"
        f"coincide everywhere.\n"
        f"worst gap over the grid:\n"
        f"{np.abs(L1 - L2).max():.1e}\n\n"
        f"the data differs by up to\n"
        f"{np.abs(np.sort(d1)-np.sort(d2)).max():.4f} per order statistic.",
        transform=right.transAxes, ha="left", va="bottom",
        color=p.fg, fontsize=7.2, family="monospace")

    fig.text(
        0.5, -0.06,
        "The two histograms are different data. Because they share n, the sum and "
        "the sum of squares, Theorem 6.14 says the Gaussian likelihood cannot "
        "distinguish them — and the overlaid contours confirm it. Those two sums "
        "are the sufficient statistics, and everything else in the data is "
        "irrelevant to inferring mu and sigma.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


def exponential_family_link(fig, ax, p: Palette) -> None:
    """Example 6.14's natural parameter, and what A(theta) is for."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    mus = np.linspace(0.001, 0.999, 800)
    thetas = np.log(mus / (1 - mus))
    left.plot(mus, thetas, color=p.blue, linewidth=2.4,
              label="$\\theta = \\log\\frac{\\mu}{1-\\mu}$, Eq 6.115")
    left.axhline(0, color=p.muted, linewidth=1)
    left.axvline(0.5, color=p.muted, linewidth=1, linestyle=":")
    for m in (0.1, 0.3, 0.5, 0.7, 0.9):
        t = math.log(m / (1 - m))
        left.plot([m], [t], "o", color=p.amber, markersize=6, zorder=5)
        left.text(m + 0.015, t, f"{t:+.3f}", color=p.amber, fontsize=7.4,
                  family="monospace", va="center")
    left.set_xlabel("$\\mu \\in (0,1)$")
    left.set_ylabel("$\\theta \\in \\mathbb{R}$")
    left.set_ylim(-7, 7)
    left.set_title("the natural parameter is unbounded", fontsize=9.5)
    left.legend(fontsize=8.4, loc="upper left")
    left.text(
        0.97, 0.03,
        "Eq 6.118 inverts it:\n"
        "mu = 1/(1 + exp(-theta)),\n"
        "the SIGMOID. That is why a\n"
        "Bernoulli likelihood and\n"
        "logistic regression are the\n"
        "same statement.",
        transform=left.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace")

    th = np.linspace(-6, 6, 800)
    A = np.log1p(np.exp(th))
    dA = 1 / (1 + np.exp(-th))
    right.plot(th, A, color=p.purple, linewidth=2.4,
               label="$A(\\theta) = \\log(1+e^\\theta)$, Eq 6.117")
    right.plot(th, dA, color=p.green, linewidth=2.4,
               label="$\\mathrm{d}A/\\mathrm{d}\\theta = \\mu$")
    hh = 1e-6
    num = (np.log1p(np.exp(th + hh)) - np.log1p(np.exp(th - hh))) / (2 * hh)
    right.plot(th[::40], num[::40], "o", color=p.amber, markersize=5,
               label="the derivative, measured")
    right.set_xlabel("$\\theta$")
    right.set_ylabel("value")
    right.set_title("the log-partition function generates the mean",
                    fontsize=9.5)
    right.legend(fontsize=8, loc="upper left")
    right.text(
        0.97, 0.03,
        f"worst gap between the measured\n"
        f"derivative and the sigmoid:\n"
        f"{np.abs(num - dA).max():.1e}\n\n"
        "A(theta) is not bookkeeping --\n"
        "differentiating it hands you\n"
        "E[phi(x)].",
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace")


FIGURES = [
    figure("named-distributions", named_distributions, size=(11.5, 4.4),
           axes=False),
    figure("conjugacy-updates-parameters", conjugacy_updates_parameters,
           size=(11.5, 4.4), axes=False),
    figure("sufficient-statistics", sufficient_statistics, size=(12.5, 4.4),
           axes=False),
    figure("exponential-family-link", exponential_family_link, size=(11.0, 4.4),
           axes=False),
]

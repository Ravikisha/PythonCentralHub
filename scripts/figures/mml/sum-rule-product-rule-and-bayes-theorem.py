"""Figures for *Sum Rule, Product Rule, and Bayes' Theorem*.

1. `two-rules-one-table` — both rules acting on the same joint. The sum rule
   collapses an axis (Equation 6.20); the product rule splits a cell into a
   conditional times a marginal (Equation 6.22). Drawn on Section 6.2's counts so
   the arithmetic is already familiar, with the reconstruction error printed to
   show the factorisation is exact rather than approximate.

2. `base-rate-fallacy` — Bayes' theorem as the probabilistic inverse, measured.
   The posterior P(disease | positive) against prevalence for a test with 99%
   sensitivity and specificity, beside the number people actually quote (the
   sensitivity). They agree only where the disease is common. The right panel
   counts out a population of 100000 so the ratio is visible as bodies rather
   than as a formula.

3. `prior-updating` — the posterior as data arrives, for a well-chosen prior and
   for one that assigns zero mass to the truth. The first converges; the second
   is still exactly zero after four hundred observations, because the posterior is
   a product and nothing multiplies zero back to life.
"""

from __future__ import annotations

import math

import numpy as np

from _style import Palette, figure

N_IJ = np.array([
    [12, 30, 18, 8, 4],
    [6, 22, 40, 26, 10],
    [2, 8, 14, 30, 20],
])
SENS = SPEC = 0.99


def two_rules_one_table(fig, ax, p: Palette) -> None:
    """Equation 6.20 collapses an axis; Equation 6.22 splits a cell."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1]})

    N = N_IJ.sum()
    joint = N_IJ / N
    px = joint.sum(axis=0)
    py = joint.sum(axis=1)

    # ---- left: the joint with its margins, i.e. the sum rule.
    left.imshow(joint, cmap="viridis", aspect="auto", vmin=0, vmax=joint.max())
    for j in range(3):
        for i in range(5):
            left.text(i, j, f"{joint[j, i]:.3f}", ha="center", va="center",
                      color="white" if joint[j, i] < 0.6 * joint.max() else "black",
                      fontsize=8, family="monospace")
    # Marginals drawn just outside the grid.
    for i in range(5):
        left.text(i, 3.05, f"{px[i]:.3f}", ha="center", va="center",
                  color=p.amber, fontsize=8.4, family="monospace", weight="bold")
    for j in range(3):
        left.text(5.05, j, f"{py[j]:.3f}", ha="left", va="center",
                  color=p.green, fontsize=8.4, family="monospace", weight="bold")
    left.text(2.0, 3.62, "$p(x) = \\sum_y p(x,y)$  (Eq 6.20)", ha="center",
              color=p.amber, fontsize=9)
    left.text(5.05, -0.75, "$p(y)$", ha="left", color=p.green, fontsize=9)
    left.set_xticks(range(5), [f"$x_{i+1}$" for i in range(5)])
    left.set_yticks(range(3), [f"$y_{j+1}$" for j in range(3)])
    left.set_xlim(-0.6, 6.4)
    left.set_ylim(3.9, -1.0)
    left.set_title("the sum rule collapses an axis", fontsize=9.5)

    # ---- right: the product rule, cell by cell.
    cond = joint / px[None, :]
    recon = cond * px[None, :]
    err = np.abs(recon - joint).max()

    idx = np.arange(15)
    right.plot(idx, joint.ravel(), "o", color=p.blue, markersize=7,
               label="$p(x,y)$, the joint")
    right.plot(idx, (cond * px[None, :]).ravel(), "x", color=p.amber,
               markersize=9, markeredgewidth=2,
               label="$p(y|x)\\,p(x)$, Eq 6.22")
    right.set_xlabel("the fifteen cells of the table")
    right.set_ylabel("probability")
    right.set_title("the product rule is exact, not approximate", fontsize=9.5)
    right.legend(loc="upper right", fontsize=8.4)
    right.text(
        0.03, 0.95,
        f"worst gap over all 15 cells:\n{err:.1e}\n\n"
        "and the other factorisation,\n$p(x|y)\\,p(y)$, gives the same\n"
        "joint — which is the whole\nderivation of Bayes' theorem\n"
        "(Eq 6.24 to 6.26).",
        transform=right.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.8, family="monospace")


def base_rate_fallacy(fig, ax, p: Palette) -> None:
    """Bayes as the probabilistic inverse, against the number people quote."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    prev = np.geomspace(1e-5, 0.9, 500)
    post = SENS * prev / (SENS * prev + (1 - SPEC) * (1 - prev))

    left.semilogx(prev, post, color=p.blue, linewidth=2.4,
                  label="$P(\\mathrm{disease}\\mid+)$, Bayes")
    left.axhline(SENS, color=p.red, linestyle="--", linewidth=1.6,
                 label="$P(+\\mid\\mathrm{disease})$, the sensitivity")
    for q, colour in ((0.001, p.amber), (0.01, p.green)):
        v = SENS * q / (SENS * q + (1 - SPEC) * (1 - q))
        left.plot([q], [v], "o", color=colour, markersize=8, zorder=5)
        left.annotate(f"prevalence {q}\nposterior {v:.4f}",
                      xy=(q, v), xytext=(q * 1.6, v + 0.16),
                      color=colour, fontsize=8, family="monospace",
                      arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=1.1))
    left.set_xlabel("prevalence $P(\\mathrm{disease})$")
    left.set_ylabel("probability")
    left.set_ylim(-0.05, 1.15)
    left.set_title("the two conditionals are different numbers", fontsize=9.5)
    left.legend(loc="upper left", fontsize=8)
    left.text(
        0.97, 0.05,
        "sensitivity and specificity both 0.99.\n"
        "The two curves meet only where the\n"
        "disease is common. Quoting the flat\n"
        "line as 'the accuracy of a positive'\n"
        "is the base-rate fallacy.",
        transform=left.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")

    # ---- right: count out a population.
    POP = 100_000
    q = 0.001
    sick = POP * q
    tp = sick * SENS
    fn = sick - tp
    healthy = POP - sick
    fp = healthy * (1 - SPEC)
    tn = healthy - fp

    cats = ["true\npositives", "false\npositives", "false\nnegatives",
            "true\nnegatives"]
    vals = [tp, fp, fn, tn]
    colours = [p.green, p.red, p.amber, p.muted]
    bars = right.bar(cats, vals, color=colours, width=0.62)
    right.set_yscale("log")
    right.set_ylabel(f"people out of {POP:,}")
    for b, v in zip(bars, vals):
        right.text(b.get_x() + b.get_width() / 2, v * 1.25, f"{v:,.0f}",
                   ha="center", color=p.fg, fontsize=8.6, family="monospace")
    right.set_title(f"prevalence {q}: who tests positive", fontsize=9.5)
    right.text(
        0.5, 0.04,
        f"{tp:,.0f} true positives against {fp:,.0f} false ones.\n"
        f"P(disease | +) = {tp:,.0f} / {tp + fp:,.0f} = "
        f"{tp / (tp + fp):.4f}\n"
        f"The 99% test is right about the DISEASED;\n"
        f"there are simply far more healthy people.",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")


def prior_updating(fig, ax, p: Palette) -> None:
    """The posterior as data arrives — and the prior that can never recover."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    # ---- left: a continuous, conjugate update.
    a0, b0 = 2.0, 5.0
    rng = np.random.default_rng(7)
    truth = 0.65
    draws = rng.random(200) < truth
    grid = np.linspace(0, 1, 1000)

    def beta_pdf(a, b):
        logc = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.exp(logc + (a - 1) * np.log(grid) + (b - 1) * np.log1p(-grid))

    for n, colour, style in ((0, p.muted, "--"), (5, p.purple, "-"),
                             (20, p.blue, "-"), (50, p.green, "-"),
                             (200, p.amber, "-")):
        k = int(draws[:n].sum())
        pdf = beta_pdf(a0 + k, b0 + n - k)
        left.plot(grid, pdf, colour, linestyle=style, linewidth=2.0,
                  label=f"$n={n}$" + (" (prior)" if n == 0 else ""))
    left.axvline(truth, color=p.red, linestyle=":", linewidth=1.8)
    left.text(truth + 0.01, left.get_ylim()[1] * 0.9, f"truth {truth}",
              color=p.red, fontsize=8, family="monospace")
    left.set_xlabel("bias of the coin")
    left.set_ylabel("posterior density")
    left.set_title("a Beta prior, updated by Equation 6.23", fontsize=9.5)
    left.legend(loc="upper left", fontsize=8)
    left.text(
        0.97, 0.55,
        f"prior Beta({a0:.0f}, {b0:.0f}) has mean\n"
        f"{a0 / (a0 + b0):.4f} — deliberately wrong.\n"
        "The data moves it anyway, and\n"
        "the density concentrates as the\n"
        "evidence accumulates.",
        transform=left.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.8, family="monospace")

    # ---- right: the discrete case, with one state ruled out a priori.
    states = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    true_state = 0.7
    rng2 = np.random.default_rng(11)
    d2 = rng2.random(400) < true_state
    ns = np.array([0, 2, 5, 10, 20, 50, 100, 200, 400])

    good = np.full(5, 1 / 5)
    bad = np.array([0.25, 0.25, 0.25, 0.0, 0.25])
    mass_good, mass_bad = [], []
    for n in ns:
        k = int(d2[:n].sum())
        ll = states ** k * (1 - states) ** (n - k)
        for pr, out in ((good, mass_good), (bad, mass_bad)):
            post = pr * ll
            s = post.sum()
            out.append(post[3] / s if s > 0 else 0.0)

    right.plot(ns, mass_good, "o-", color=p.green, linewidth=2.2,
               label="prior with mass everywhere")
    right.plot(ns, mass_bad, "s-", color=p.red, linewidth=2.2,
               label="prior with $p(0.7) = 0$")
    right.set_xlabel("observations")
    right.set_ylabel("posterior mass on the true state")
    right.set_ylim(-0.05, 1.1)
    right.set_title("a zero in the prior is permanent", fontsize=9.5)
    right.legend(loc="center right", fontsize=8)
    right.text(
        0.03, 0.5,
        "the red line is exactly 0.0000000000\n"
        "at every sample size, including 400.\n\n"
        "Equation 6.23 multiplies by the prior,\n"
        "and nothing multiplies zero back up.\n"
        "This is why the book insists the prior\n"
        "be nonzero on every plausible state.",
        transform=right.transAxes, ha="left", va="center",
        color=p.fg, fontsize=7.8, family="monospace")


FIGURES = [
    figure("two-rules-one-table", two_rules_one_table, size=(11.5, 4.4),
           axes=False),
    figure("base-rate-fallacy", base_rate_fallacy, size=(11.5, 4.6),
           axes=False),
    figure("prior-updating", prior_updating, size=(11.5, 4.4), axes=False),
]

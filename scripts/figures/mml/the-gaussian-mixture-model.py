"""Figures for *The Gaussian Mixture Model* (Section 11.1).

1. `a-mixture-is-a-density` — Figure 11.2 rebuilt from Equation 11.5, with the
   best single Gaussian overlaid. The mixture integrates to 1.000000000000;
   the moment-matched Gaussian is 0.330585 nats away in KL and 0.352457 in
   total variation.

2. `mean-yes-variance-no` — the law of total variance on Equation 11.5. The
   mean is the weighted mean exactly; the variance is 7.79, of which the
   weighted component variances supply only 0.95 and the spread of the means
   supplies 6.84.

3. `modes-are-not-components` — two equal unit-variance Gaussians show one
   bump until their means are more than 2 standard deviations apart, measured
   to d = 1.0000000. Unequal weights push the threshold out to 1.657251.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

PI = np.array([0.5, 0.2, 0.3])
MU = np.array([-2.0, 1.0, 4.0])
VAR = np.array([0.5, 2.0, 1.0])


def _g(x, mu, var):
    x = np.asarray(x, float)
    return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)


def _mix(x, pi=PI, mu=MU, var=VAR):
    x = np.asarray(x, float)
    return (pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])).sum(1)


def _n_modes(pi, mu, var, lo=-12.0, hi=12.0, n=400001):
    g = np.linspace(lo, hi, n)
    y = _mix(g, pi, mu, var)
    idx = np.flatnonzero((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:])) + 1
    return len(idx), g[idx]


# --------------------------------------------------------------------------
# 1. Figure 11.2
# --------------------------------------------------------------------------

def a_mixture_is_a_density(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1.0]})

    x = np.linspace(-6, 9, 2000)
    cols = [p.blue, p.green, p.purple]
    for k in range(3):
        a1.plot(x, PI[k] * _g(x, MU[k], VAR[k]), color=cols[k], lw=1.6,
                ls="--",
                label=f"$\\pi_{k+1}\\mathcal{{N}}(x\\mid{MU[k]:.0f},"
                      f"{VAR[k]:g})$")
    y = _mix(x)
    a1.plot(x, y, color=p.amber, lw=2.8, label="GMM density")
    a1.fill_between(x, 0, y, color=p.amber, alpha=0.10)
    a1.set_xlabel("$x$")
    a1.set_ylabel("$p(x)$")
    a1.legend(fontsize=8.6)
    a1.set_title("Equation 11.5; the area is 1.000000000000", fontsize=10)

    mean = float((PI * MU).sum())
    var = float((PI * VAR).sum() + (PI * (MU - mean) ** 2).sum())
    a2.plot(x, y, color=p.amber, lw=2.6, label="the mixture")
    a2.plot(x, _g(x, mean, var), color=p.red, lw=2.0, ls="--",
            label=f"$\\mathcal{{N}}({mean:.1f}, {var:.2f})$, moment-matched")
    a2.fill_between(x, y, _g(x, mean, var), color=p.red, alpha=0.15)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$p(x)$")
    a2.legend(fontsize=9)
    a2.set_title("KL 0.330585 nats, total variation 0.352457", fontsize=10)
    fig.suptitle("A convex combination of Gaussians is a density, and is "
                 "not a Gaussian",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the law of total variance
# --------------------------------------------------------------------------

def mean_yes_variance_no(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    mean = float((PI * MU).sum())
    within = float((PI * VAR).sum())
    between = float((PI * (MU - mean) ** 2).sum())
    total = within + between

    x = np.linspace(-6, 9, 2000)
    a1.plot(x, _mix(x), color=p.amber, lw=2.4)
    a1.axvline(mean, color=p.red, lw=1.8, ls="--")
    a1.annotate(f"$\\mathbb{{E}}[x] = \\sum_k\\pi_k\\mu_k = {mean:.1f}$",
                (mean + 0.25, 0.285), fontsize=9.5, color=p.red)
    for k in range(3):
        a1.plot([MU[k]], [0.005], marker="^", ms=9, color=p.blue)
        a1.annotate(f"$\\mu_{k+1}$", (MU[k] - 0.2, 0.021), fontsize=9,
                    color=p.blue)
        a1.plot([MU[k] - np.sqrt(VAR[k]), MU[k] + np.sqrt(VAR[k])],
                [0.005, 0.005], color=p.blue, lw=2.0, alpha=0.6)
    a1.set_xlabel("$x$")
    a1.set_ylabel("$p(x)$")
    a1.set_ylim(-0.006, 0.32)
    a1.set_title("the means spread out; that spread is variance too",
                 fontsize=10)

    a2.bar(["within\n$\\sum\\pi_k\\sigma_k^2$",
            "between\n$\\sum\\pi_k(\\mu_k-\\mathbb{E}[x])^2$",
            "total\n$\\mathbb{V}[x]$"],
           [within, between, total],
           color=[p.blue, p.purple, p.amber], width=0.55)
    for k, v in enumerate([within, between, total]):
        a2.text(k, v + 0.16, f"{v:.2f}", ha="center", fontsize=10,
                color=p.fg)
    a2.set_ylim(0, total * 1.18)
    a2.set_ylabel("variance")
    a2.set_title(f"the between term is "
                 f"{100*between/total:.2f}% of the total", fontsize=10)
    fig.suptitle("The mean of a mixture is a weighted mean. The variance "
                 "is not a weighted variance.",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. modes
# --------------------------------------------------------------------------

def modes_are_not_components(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1.0]})

    pi2 = np.array([0.5, 0.5])
    v2 = np.array([1.0, 1.0])
    x = np.linspace(-6, 6, 3000)
    for d, col in ((0.6, p.blue), (0.9, p.green), (1.1, p.amber),
                   (1.8, p.purple)):
        k, _ = _n_modes(pi2, np.array([-d, d]), v2)
        a1.plot(x, _mix(x, pi2, np.array([-d, d]), v2), color=col, lw=2.0,
                label=f"$d$ = {d}, {k} mode" + ("s" if k != 1 else ""))
    a1.set_xlabel("$x$")
    a1.set_ylabel("$p(x)$")
    a1.legend(fontsize=9)
    a1.set_title("two unit-variance Gaussians at $\\pm d$", fontsize=10)

    ds = np.linspace(0.3, 2.2, 120)
    counts = [_n_modes(pi2, np.array([-d, d]), v2)[0] for d in ds]
    a2.step(ds, counts, where="mid", color=p.blue, lw=2.2)
    a2.axvline(1.0, color=p.red, lw=1.6, ls="--")
    a2.annotate("$d = 1.0000000$\nmeans exactly $2\\sigma$ apart",
                (1.06, 1.42), fontsize=9.5, color=p.red)
    a2.set_xlabel("$d$")
    a2.set_ylabel("number of modes")
    a2.set_yticks([0, 1, 2])
    a2.set_ylim(-0.3, 2.6)
    a2.set_title("the transition is sharp, and it is not at $d = 0$",
                 fontsize=10)
    fig.suptitle("Two components, one bump or two: the number of modes "
                 "is not $K$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("a-mixture-is-a-density", a_mixture_is_a_density, size=(9.4, 4.2),
           axes=False),
    figure("mean-yes-variance-no", mean_yes_variance_no, size=(9.4, 4.2),
           axes=False),
    figure("modes-are-not-components", modes_are_not_components,
           size=(9.4, 4.2), axes=False),
]

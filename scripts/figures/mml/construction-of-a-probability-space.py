"""Figures for *Construction of a Probability Space*.

1. `probability-space-three-objects` — the machinery of §6.1.2 drawn once, so the
   three objects stop blurring together. Omega on the left with its four outcomes
   and their measures, T on the right with the three states, and the arrows of the
   random variable X between them. The point of the picture is the pre-image of
   Equation 6.8: X = 1 has two arrows into it, and P(X = 1) is the sum of their
   two measures, which is why P_X is not P.

2. `frequentist-convergence` — the frequentist reading of P, measured. The
   empirical pmf of Example 6.1's game against the number of draws, over many
   independent runs, with the 1/sqrt(N) reference. The band is the interesting
   part: the definition says "in the limit of infinite data", and this is what the
   approach to that limit actually costs.

3. `two-wrong-shortcuts` — the two ways the pmf gets guessed instead of computed,
   plotted against the coin's bias. "Uniform on T" is never right. "Uniform on
   Omega" is right at exactly one value of p, and the figure marks it.
"""

from __future__ import annotations

import itertools
import math

import numpy as np

from _style import Palette, figure

P_DOLLAR = 0.3
OMEGA = list(itertools.product(["$", "£"], repeat=2))
X = {("$", "$"): 2, ("$", "£"): 1, ("£", "$"): 1, ("£", "£"): 0}
STATES = [0, 1, 2]


def _measure(o, p=P_DOLLAR):
    return math.prod(p if c == "$" else 1 - p for c in o)


def _pmf(p=P_DOLLAR):
    return {t: sum(_measure(o, p) for o in OMEGA if X[o] == t) for t in STATES}


def probability_space_three_objects(fig, ax, p: Palette) -> None:
    """Omega, X, T — and the pre-image that makes Equation 6.8 necessary."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.35, 1]})

    # ---- left: the mapping itself.
    left.set_xlim(0, 10)
    left.set_ylim(-0.6, 4.6)
    left.axis("off")

    pmf = _pmf()
    ys = {o: 3.9 - i * 1.1 for i, o in enumerate(OMEGA)}
    ty = {2: 3.35, 1: 2.25, 0: 1.15}

    left.text(1.6, 4.45, "$\\Omega$  (sample space)", ha="center", color=p.fg,
              fontsize=10, weight="bold")
    left.text(8.2, 4.45, "$\\mathcal{T}$  (target space)", ha="center", color=p.fg,
              fontsize=10, weight="bold")
    left.text(5.0, 4.45, "$X:\\Omega\\to\\mathcal{T}$", ha="center", color=p.amber,
              fontsize=10, weight="bold")

    for o in OMEGA:
        y = ys[o]
        colour = p.green if X[o] == 1 else p.muted
        left.add_patch(
            __import__("matplotlib").patches.FancyBboxPatch(
                (0.15, y - 0.32), 2.9, 0.64,
                boxstyle="round,pad=0.04", linewidth=1.3,
                edgecolor=colour, facecolor="none", zorder=3))
        left.text(0.35, y, f"({o[0]}, {o[1]})", va="center", color=p.fg,
                  fontsize=10, family="monospace")
        left.text(2.9, y, f"{_measure(o):.2f}", va="center", ha="right",
                  color=colour, fontsize=9.5, family="monospace")

    for t in STATES:
        n = sum(1 for o in OMEGA if X[o] == t)
        colour = p.green if t == 1 else p.blue
        left.add_patch(
            __import__("matplotlib").patches.FancyBboxPatch(
                (7.0, ty[t] - 0.32), 2.6, 0.64,
                boxstyle="round,pad=0.04", linewidth=1.4,
                edgecolor=colour, facecolor="none", zorder=3))
        left.text(7.25, ty[t], f"X = {t}", va="center", color=p.fg,
                  fontsize=10, family="monospace")
        left.text(9.45, ty[t], f"{pmf[t]:.2f}", va="center", ha="right",
                  color=colour, fontsize=9.5, family="monospace", weight="bold")
        left.text(9.9, ty[t], f"{n} arrow{'s' if n > 1 else ''}", va="center",
                  ha="left", color=p.muted, fontsize=7.6)

    for o in OMEGA:
        t = X[o]
        colour = p.green if t == 1 else p.muted
        left.annotate("", xy=(6.95, ty[t]), xytext=(3.15, ys[o]),
                      arrowprops=dict(arrowstyle="-|>", color=colour,
                                      linewidth=1.6 if t == 1 else 1.1,
                                      alpha=1.0 if t == 1 else 0.6))

    left.text(
        5.0, 0.15,
        "$X$ is a FUNCTION, and it collapses outcomes.\n"
        "Two outcomes map to $X=1$, so Eq 6.8 sums their\n"
        "measures:  $0.21 + 0.21 = 0.42$.\n"
        "That collapse is the whole reason $P_X \\neq P$.",
        ha="center", va="bottom", color=p.fg, fontsize=8.2, family="monospace")

    # ---- right: the resulting pmf, and that it sums to one.
    bars = right.bar([str(t) for t in STATES], [pmf[t] for t in STATES],
                     color=[p.blue, p.green, p.blue], width=0.58)
    for t, b in zip(STATES, bars):
        right.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.012,
                   f"{pmf[t]:.2f}", ha="center", color=p.fg, fontsize=9.5,
                   family="monospace")
    right.set_ylim(0, 0.62)
    right.set_xlabel("state in $\\mathcal{T}$: number of \\$ drawn")
    right.set_ylabel("$P_X$")
    right.set_title("the law of $X$, Eq 6.5 to 6.7", fontsize=9.5)
    right.text(
        0.97, 0.95,
        f"draw returns \\$ with p = {P_DOLLAR}\n"
        f"two draws, with replacement\n\n"
        f"sum of the pmf: {sum(pmf.values()):.10f}",
        transform=right.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.8, family="monospace")


def frequentist_convergence(fig, ax, p: Palette) -> None:
    """Relative frequency approaching P, and what the approach costs."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(6)
    Ns = np.array([10, 30, 100, 300, 1_000, 3_000, 10_000, 30_000, 100_000])
    RUNS = 200
    pmf = _pmf()
    truth = np.array([pmf[t] for t in STATES])

    # The empirical pmf of N draws is a multinomial count vector over the three
    # states, divided by N. Drawing the counts directly is the same distribution
    # as simulating N draws and costs O(RUNS) instead of O(RUNS * N).
    errs = np.zeros((len(Ns), RUNS))
    for i, N in enumerate(Ns):
        counts = rng.multinomial(N, truth, size=RUNS) / N
        errs[i] = np.abs(counts - truth).max(axis=1)

    med = np.median(errs, axis=1)
    lo = np.percentile(errs, 10, axis=1)
    hi = np.percentile(errs, 90, axis=1)

    left.fill_between(Ns, lo, hi, color=p.blue, alpha=0.22,
                      label="10th to 90th percentile")
    left.loglog(Ns, med, "o-", color=p.blue, linewidth=2.0, label="median error")
    ref = med[0] * np.sqrt(Ns[0] / Ns)
    left.loglog(Ns, ref, "--", color=p.amber, linewidth=1.7,
                label="$1/\\sqrt{N}$ reference")
    left.set_xlabel("number of draws $N$")
    left.set_ylabel("worst error in the pmf")
    left.set_title("relative frequency approaches $P$ — slowly", fontsize=9.5)
    left.legend(loc="lower left", fontsize=8)

    slope = np.polyfit(np.log(Ns), np.log(med), 1)[0]
    left.text(
        0.97, 0.95,
        f"{RUNS} independent runs per $N$\n"
        f"fitted slope: {slope:.3f}\n"
        f"(the theory says $-0.5$)\n\n"
        f"to get two decimal places\n"
        f"you need about $10^4$ draws",
        transform=left.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.8, family="monospace")

    # ---- right: one long run, all three states, converging.
    N = 20_000
    draws = rng.random((N, 2)) < P_DOLLAR
    k = draws.sum(axis=1)
    idx = np.arange(1, N + 1)
    for t, colour in zip(STATES, (p.blue, p.green, p.purple)):
        running = np.cumsum(k == t) / idx
        right.semilogx(idx, running, color=colour, linewidth=1.3,
                       label=f"$P(X={t})$")
        right.axhline(pmf[t], color=colour, linestyle=":", linewidth=1.2)
    right.set_xlabel("draws so far")
    right.set_ylabel("running relative frequency")
    right.set_ylim(0, 0.75)
    right.set_title("one run, with the true values dotted", fontsize=9.5)
    right.legend(loc="upper right", fontsize=8, ncol=3)
    right.text(
        0.03, 0.05,
        "the frequentist definition of $P$ is this limit.\n"
        "At $N=100$ the estimates are still wandering by\n"
        "several percent.",
        transform=right.transAxes, ha="left", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")


def two_wrong_shortcuts(fig, ax, p: Palette) -> None:
    """Guessing the pmf instead of computing it, across the whole range of p."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    ps = np.linspace(0, 1, 401)
    correct = np.array([[sum(_measure(o, q) for o in OMEGA if X[o] == t)
                         for t in STATES] for q in ps])
    counts = np.array([sum(1 for o in OMEGA if X[o] == t) for t in STATES])
    uni_omega = counts / len(OMEGA)
    uni_T = np.full(len(STATES), 1 / len(STATES))

    for i, (t, colour) in enumerate(zip(STATES, (p.blue, p.green, p.purple))):
        left.plot(ps, correct[:, i], color=colour, linewidth=2.0,
                  label=f"$P(X={t})$, computed")
        left.axhline(uni_omega[i], color=colour, linestyle="--", linewidth=1.1,
                     alpha=0.8)
    left.axvline(0.5, color=p.amber, linestyle=":", linewidth=1.6)
    left.plot([P_DOLLAR] * 3, correct[np.argmin(np.abs(ps - P_DOLLAR))], "o",
              color=p.red, markersize=6, zorder=5)
    left.set_xlabel("probability $p$ that a draw returns \\$")
    left.set_ylabel("probability")
    left.set_title("dashed: 'uniform on $\\Omega$'. Right at one $p$ only.",
                   fontsize=9.5)
    left.legend(loc="upper center", fontsize=7.6)
    left.text(
        0.5, 0.02,
        "the dashed lines cross the solid curves only at $p=0.5$\n"
        "(amber). The red dots mark Example 6.1's $p=0.3$.",
        transform=left.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")

    err_omega = np.abs(correct - uni_omega).max(axis=1)
    err_T = np.abs(correct - uni_T).max(axis=1)
    right.plot(ps, err_omega, color=p.green, linewidth=2.0,
               label="error of 'uniform on $\\Omega$'")
    right.plot(ps, err_T, color=p.red, linewidth=2.0,
               label="error of 'uniform on $\\mathcal{T}$'")
    right.axvline(0.5, color=p.amber, linestyle=":", linewidth=1.6)
    i3 = int(np.argmin(np.abs(ps - P_DOLLAR)))
    right.plot([P_DOLLAR, P_DOLLAR], [err_omega[i3], err_T[i3]], "o",
               color=p.fg, markersize=5, zorder=5)
    right.set_xlabel("probability $p$ that a draw returns \\$")
    right.set_ylabel("worst absolute error")
    right.set_title("how wrong each shortcut is", fontsize=9.5)
    right.legend(loc="upper center", fontsize=8)
    right.text(
        0.5, 0.03,
        f"at $p=0.3$:  uniform on $\\Omega$ is off by {err_omega[i3]:.4f},\n"
        f"uniform on $\\mathcal{{T}}$ by {err_T[i3]:.4f}.\n"
        f"'Uniform on $\\mathcal{{T}}$' is never exact — its smallest\n"
        f"error over all $p$ is {err_T.min():.4f}.",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")


FIGURES = [
    figure("probability-space-three-objects", probability_space_three_objects,
           size=(11.5, 4.8), axes=False),
    figure("frequentist-convergence", frequentist_convergence,
           size=(11.0, 4.4), axes=False),
    figure("two-wrong-shortcuts", two_wrong_shortcuts,
           size=(11.0, 4.4), axes=False),
]

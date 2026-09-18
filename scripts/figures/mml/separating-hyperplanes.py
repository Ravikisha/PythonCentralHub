"""Figures for *Separating Hyperplanes* (§12.1).

1. `the-hyperplane-and-its-normal` — Figure 12.2(b) drawn on the chapter's
   running example: the set {x : f(x) = 0}, the normal vector w, the intercept,
   and the two sides Equations 12.5 and 12.6 name.

2. `many-separators-one-margin` — Figure 12.3 measured. Every green line has
   zero training error; held-out accuracy across 9,628 of them spans 0.1119,
   and the margin bounds the worst case rather than the best one.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
W_STAR, B_STAR = np.array([1.0, 0.0]), -2.0


def _scatter(ax, p: Palette, size=90):
    pos, neg = X[Y > 0], X[Y < 0]
    ax.scatter(pos[:, 0], pos[:, 1], marker="x", s=size, lw=2.4,
               color=p.amber, label="$y = +1$", zorder=4)
    ax.scatter(neg[:, 0], neg[:, 1], marker="o", s=size, lw=2.0,
               facecolor="none", edgecolor=p.blue, label="$y = -1$",
               zorder=4)


# --------------------------------------------------------------------------
# 1. the hyperplane and its normal
# --------------------------------------------------------------------------

def hyperplane_and_normal(fig, ax, p: Palette) -> None:
    ax.axhspan(-100, 100, xmin=0.0, xmax=0.0)  # keep autoscale sane
    ax.set_xlim(-2.2, 7.2)
    ax.set_ylim(-2.6, 2.6)

    # the two half-spaces
    ax.axvspan(2.0, 7.2, color=p.amber, alpha=0.07)
    ax.axvspan(-2.2, 2.0, color=p.blue, alpha=0.07)

    ax.axvline(2.0, color=p.fg, lw=2.4)
    ax.annotate(r"$\{x : \langle w, x\rangle + b = 0\}$", (2.12, -2.32),
                fontsize=10.5, color=p.fg)

    # the normal vector, drawn from a point on the hyperplane
    ax.annotate("", xy=(3.4, 0.6), xytext=(2.0, 0.6),
                arrowprops=dict(arrowstyle="-|>", lw=2.4, color=p.red))
    ax.annotate("$w$", (3.5, 0.52), fontsize=13, color=p.red)

    # two points on the hyperplane, and the vector between them
    ax.plot([2.0, 2.0], [1.9, -1.4], "o", ms=7, color=p.purple, zorder=5)
    ax.annotate("", xy=(2.0, -1.4), xytext=(2.0, 1.9),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color=p.purple))
    ax.annotate("$x_a$", (1.55, 1.95), fontsize=11, color=p.purple)
    ax.annotate("$x_b$", (1.55, -1.62), fontsize=11, color=p.purple)
    ax.annotate(r"$\langle w,\, x_a - x_b\rangle = 0$", (-2.05, 1.35),
                fontsize=10.5, color=p.purple)

    ax.annotate("positive side\n" r"$\langle w,x\rangle + b \geq 0$",
                (4.6, -2.15), fontsize=9.5, color=p.amber, ha="center")
    ax.annotate("negative side\n" r"$\langle w,x\rangle + b < 0$",
                (-0.2, -2.15), fontsize=9.5, color=p.blue, ha="center")

    _scatter(ax, p)
    ax.set_xlabel("$x^{(1)}$")
    ax.set_ylabel("$x^{(2)}$")
    ax.legend(fontsize=9.5, loc="upper right")
    ax.set_title("Equation 12.3 names a set, and Equation 12.4 shows "
                 "$w$ is normal to it",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. many separators, one margin
# --------------------------------------------------------------------------

def many_separators(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.15]})

    def separates(w, b):
        return bool((Y * (X @ w + b) > 0).all())

    # --- left: a sample of the separating hyperplanes
    rg = np.random.default_rng(11)
    drawn = 0
    ys = np.array([-2.6, 2.6])
    while drawn < 60:
        th = rg.uniform(0, 2 * np.pi)
        w = np.array([np.cos(th), np.sin(th)])
        b = rg.uniform(-8, 8)
        if not separates(w, b):
            continue
        if abs(w[0]) < 1e-9:
            continue
        xs = (-b - w[1] * ys) / w[0]
        a1.plot(xs, ys, color=p.green, lw=1.0, alpha=0.30, zorder=1)
        drawn += 1
    a1.plot([2.0, 2.0], ys, color=p.fg, lw=2.8, zorder=3,
            label="the max-margin one")
    _scatter(a1, p, size=80)
    a1.set_xlim(-2.2, 7.2)
    a1.set_ylim(-2.6, 2.6)
    a1.set_xlabel("$x^{(1)}$")
    a1.set_ylabel("$x^{(2)}$")
    a1.legend(fontsize=8.5, loc="upper right")
    a1.set_title("60 of the 9,628 sampled separators\n"
                 "(every one has zero training error)", fontsize=10)

    # --- right: held-out accuracy against margin
    # the same held-out set and the same draws as the page's table, so the
    # star below carries the number the prose quotes
    MU_POS, MU_NEG, SD = np.array([4.5, 0.0]), np.array([0.0, 0.0]), 1.0
    M = 200000
    rt = np.random.default_rng(7)
    XT = np.vstack([rt.normal(MU_POS, SD, (M // 2, 2)),
                    rt.normal(MU_NEG, SD, (M // 2, 2))])
    YT = np.r_[np.ones(M // 2), -np.ones(M // 2)]

    rg2 = np.random.default_rng(11)
    accs, margins = [], []
    for _ in range(400000):
        th = rg2.uniform(0, 2 * np.pi)
        w = np.array([np.cos(th), np.sin(th)])
        b = rg2.uniform(-8, 8)
        if not separates(w, b):
            continue
        accs.append(float((np.sign(XT @ w + b) == YT).mean()))
        margins.append(float((Y * (X @ w + b)).min()))
    accs, margins = np.array(accs), np.array(margins)

    a2.scatter(margins, accs, s=5, alpha=0.16, color=p.green,
               edgecolor="none")
    edges = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    mids, worst, mean = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (margins >= lo) & (margins < hi)
        if m.sum():
            mids.append(0.5 * (lo + hi))
            worst.append(accs[m].min())
            mean.append(accs[m].mean())
    a2.plot(mids, worst, color=p.red, lw=2.4, marker="o",
            label="worst in the bin")
    a2.plot(mids, mean, color=p.purple, lw=2.4, marker="s",
            label="mean in the bin")

    W_BAYES = MU_POS - MU_NEG
    B_BAYES = -0.5 * (MU_POS @ MU_POS - MU_NEG @ MU_NEG)
    acc_bayes = float((np.sign(XT @ W_BAYES + B_BAYES) == YT).mean())
    acc_star = float((np.sign(XT @ W_STAR + B_STAR) == YT).mean())
    a2.axhline(acc_bayes, color=p.fg, ls="--", lw=1.5)
    a2.annotate(f"the Bayes rule, {acc_bayes:.4f}", (0.02, acc_bayes + 0.004),
                fontsize=9, color=p.fg)
    a2.plot([1.0], [acc_star], "*", ms=18, color=p.amber, zorder=6,
            markeredgecolor=p.fg, markeredgewidth=0.6)
    a2.annotate(f"max margin\n{acc_star:.4f}", (0.845, acc_star - 0.045),
                fontsize=9, color=p.amber, ha="center")
    a2.set_xlabel("margin on the training set")
    a2.set_ylabel("held-out accuracy")
    a2.set_ylim(0.855, 1.005)
    a2.legend(fontsize=8.5, loc="lower right")
    a2.set_title("the margin bounds the worst case,\nnot the best one",
                 fontsize=10)

    fig.suptitle("Zero training error does not pick a classifier — "
                 "Figure 12.3, measured",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-hyperplane-and-its-normal", hyperplane_and_normal,
           size=(8.4, 4.6)),
    figure("many-separators-one-margin", many_separators, size=(9.8, 4.5),
           axes=False),
]

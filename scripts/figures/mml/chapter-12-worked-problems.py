"""Figures for *Chapter 12 Worked Problems* (this module's own).

1. `the-price-of-a-unit` — problem 2. Scaling one feature by s and refitting
   is the same as minimising w1^2 + w2^2/s^2, so s is a price on using that
   feature. Here the cheap feature is the bad one, and held-out accuracy
   swings by 0.2638.

2. `two-knobs-not-one` — problem 5. C and gamma do not tune
   independently: a small gamma is rescued by a large C, and a large
   gamma is rescued by nothing.
"""

from __future__ import annotations

import numpy as np
from sklearn.svm import SVC

from _style import Palette, figure

SIG1, SD1 = 0.60, 1.00
SIG2, SD2 = 0.15, 0.05


def _make(rg, m):
    y = np.r_[np.ones(m // 2), -np.ones(m // 2)]
    return np.c_[rg.normal(SIG1 * y, SD1), rg.normal(SIG2 * y, SD2)], y


# --------------------------------------------------------------------------
# 1. the price of a unit
# --------------------------------------------------------------------------

def the_price_of_a_unit(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.05]})

    rg = np.random.default_rng(4)
    XA, YA = _make(rg, 200)
    XT, YT = _make(rg, 20000)

    def fit(s):
        m = SVC(C=1.0, kernel="linear", tol=1e-8).fit(
            XA * np.array([1.0, s]), YA)
        w = np.array([m.coef_[0, 0], m.coef_[0, 1] * s])
        b = float(m.intercept_[0])
        acc = float((np.where(XT @ w + b >= 0, 1.0, -1.0) == YT).mean())
        return w, b, acc

    a1.scatter(XA[YA > 0, 0], XA[YA > 0, 1], marker="x", s=30, lw=1.3,
               color=p.amber, label="$y = +1$", zorder=3)
    a1.scatter(XA[YA < 0, 0], XA[YA < 0, 1], marker="o", s=26, lw=1.1,
               facecolor="none", edgecolor=p.blue, label="$y = -1$", zorder=3)
    xs = np.array([-3.4, 3.4])
    for s, col, ls in ((0.1, p.red, "--"), (1.0, p.green, "-")):
        w, b, acc = fit(s)
        if abs(w[1]) > 1e-12:
            a1.plot(xs, (-b - w[0] * xs) / w[1], color=col, lw=2.6, ls=ls,
                    zorder=4, label=f"$s = {s:g}$: acc {acc:.4f}")
    a1.set_xlim(-3.4, 3.4)
    a1.set_ylim(-0.42, 0.42)
    a1.set_xlabel("$x^{(1)}$  (weak signal, ordinary scale)")
    a1.set_ylabel("$x^{(2)}$  (strong signal, tiny scale)")
    a1.legend(fontsize=8.2, loc="upper left", ncol=2, framealpha=0.93)
    a1.set_title("the same 200 points, two choices of unit", fontsize=10)

    ss = np.array([0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0, 20.0, 100.0])
    accs, shares = [], []
    for s in ss:
        w, b, acc = fit(float(s))
        accs.append(acc)
        shares.append(abs(w[1]) / np.linalg.norm(w))
    a2.semilogx(ss, accs, color=p.purple, lw=2.6, marker="o", ms=6,
                label="held-out accuracy")
    a2.axhline(float((np.where(XT[:, 0] >= 0, 1.0, -1.0) == YT).mean()),
               color=p.red, ls=":", lw=1.8)
    a2.axhline(float((np.where(XT[:, 1] >= 0, 1.0, -1.0) == YT).mean()),
               color=p.green, ls=":", lw=1.8)
    a2.annotate("$x^{(1)}$ alone", (0.055, 0.742), fontsize=9, color=p.red)
    a2.annotate("$x^{(2)}$ alone", (0.055, 0.972), fontsize=9, color=p.green)
    b2 = a2.twinx()
    b2.semilogx(ss, shares, color=p.blue, lw=2.0, ls="--", marker="s", ms=4)
    b2.set_ylabel(r"share of $\|w\|$ on $x^{(2)}$", color=p.blue)
    b2.tick_params(axis="y", labelcolor=p.blue)
    b2.set_ylim(-0.05, 1.08)
    b2.grid(False)
    a2.set_xlabel("$s$, the unit on $x^{(2)}$")
    a2.set_ylabel("held-out accuracy", color=p.purple)
    a2.tick_params(axis="y", labelcolor=p.purple)
    a2.set_ylim(0.70, 1.02)
    a2.set_title("accuracy swings by 0.2638 on a change of units",
                 fontsize=10)

    fig.suptitle("Problem 2: scaling a feature is pricing it, and the SVM "
                 "buys whatever is cheap",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. two knobs, not one
# --------------------------------------------------------------------------

def two_knobs_not_one(fig, ax, p: Palette) -> None:
    rg = np.random.default_rng(5)
    n1 = 100
    R = np.r_[rg.normal(1.0, 0.30, n1), rg.normal(2.6, 0.30, n1)]
    tt = rg.uniform(0, 2 * np.pi, 2 * n1)
    Xr = np.c_[R * np.cos(tt), R * np.sin(tt)]
    Yr = np.r_[np.ones(n1), -np.ones(n1)]
    R2 = np.r_[rg.normal(1.0, 0.30, 2000), rg.normal(2.6, 0.30, 2000)]
    t2 = rg.uniform(0, 2 * np.pi, 4000)
    XrT = np.c_[R2 * np.cos(t2), R2 * np.sin(t2)]
    YrT = np.r_[np.ones(2000), -np.ones(2000)]

    gammas = np.logspace(-2, 2, 9)
    Cs = np.logspace(-1, 3, 9)
    Z = np.zeros((len(gammas), len(Cs)))
    for i, g in enumerate(gammas):
        for j, C_ in enumerate(Cs):
            Z[i, j] = SVC(C=float(C_), kernel="rbf",
                          gamma=float(g)).fit(Xr, Yr).score(XrT, YrT)

    im = ax.imshow(Z, origin="lower", aspect="auto", cmap="viridis",
                   vmin=0.5, vmax=1.0)
    ax.set_xticks(range(len(Cs)))
    ax.set_xticklabels([f"{c:.3g}" for c in Cs], rotation=45,
                       fontsize=8)
    ax.set_yticks(range(len(gammas)))
    ax.set_yticklabels([f"{g:.3g}" for g in gammas], fontsize=8)
    ax.set_xlabel("$C$")
    ax.set_ylabel(r"$\gamma$")
    for i in range(len(gammas)):
        for j in range(len(Cs)):
            ax.text(j, i, f"{Z[i, j]:.2f}", ha="center", va="center",
                    fontsize=7.4,
                    color="white" if Z[i, j] < 0.85 else "black")
    fig.colorbar(im, ax=ax, label="held-out accuracy")
    ax.set_title(r"Problem 5: a small $\gamma$ is rescued by a large $C$;"
                 "\n" r"a large $\gamma$ is rescued by nothing",
                 fontsize=11, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-price-of-a-unit", the_price_of_a_unit, size=(10.0, 4.3),
           axes=False),
    figure("two-knobs-not-one", two_knobs_not_one, size=(7.6, 5.0)),
]

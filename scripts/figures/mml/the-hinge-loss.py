"""Figures for *The Hinge Loss* (§12.2.5).

1. `three-losses` — Figure 12.8, with the squared loss of Chapter 9 added to
   show what "not suitable for binary classification" means: it is the only
   one of the three that rises as the prediction becomes more confidently
   correct.

2. `an-outlier-that-is-not-in-doubt` — a correctly labelled point pushed far
   out on its own side. The hinge boundary does not move at all; the
   squared-loss boundary is dragged across two examples that were never in
   doubt.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])


def _pred(s):
    return np.where(s >= 0.0, 1.0, -1.0)


def _fit(XX, YY, C, loss):
    d = XX.shape[1]

    def obj(v):
        f = XX @ v[:d] + v[d]
        L = (np.maximum(0.0, 1 - YY * f).sum() if loss == "hinge"
             else ((YY - f) ** 2).sum())
        return 0.5 * v[:d] @ v[:d] + C * L

    out, bv = None, np.inf
    for s in range(30):
        rg = np.random.default_rng(s)
        r = minimize(obj, np.r_[rg.normal(0, 1, d), rg.normal(0, 1)],
                     method="Powell",
                     options={"maxiter": 400000, "xtol": 1e-13,
                              "ftol": 1e-15})
        if r.fun < bv - 1e-13:
            bv, out = r.fun, r.x.copy()
    return out


# --------------------------------------------------------------------------
# 1. three losses
# --------------------------------------------------------------------------

def three_losses(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.0]})

    t = np.linspace(-2.2, 3.2, 1200)
    z01 = np.where(t > 0, 0.0, 1.0)

    a1.step(t, z01, where="post", color=p.muted, lw=2.6,
            label="zero-one, $\\mathbb{1}(t \\leq 0)$")
    a1.plot(t, np.maximum(0.0, 1 - t), color=p.red, lw=2.8,
            label=r"hinge, $\max\{0,\, 1-t\}$")
    a1.fill_between(t, z01, np.maximum(0.0, 1 - t), color=p.red, alpha=0.10)
    a1.axvline(1.0, color=p.amber, ls="--", lw=1.5)
    a1.annotate("the hinge is zero\nfrom $t = 1$ onward", (1.12, 2.55),
                fontsize=9, color=p.amber)
    a1.annotate("the shaded band is what\nthe surrogate over-charges",
                (-2.1, 0.55), fontsize=8.8, color=p.red)
    a1.set_xlim(-2.2, 3.2)
    a1.set_ylim(-0.15, 3.4)
    a1.set_xlabel("$t = y f(x)$")
    a1.set_ylabel("loss")
    a1.legend(fontsize=9, loc="upper right")
    a1.set_title("Figure 12.8: a convex upper bound", fontsize=10)

    a2.step(t, z01, where="post", color=p.muted, lw=2.4,
            label="zero-one")
    a2.plot(t, np.maximum(0.0, 1 - t), color=p.red, lw=2.8, label="hinge")
    a2.plot(t, (1 - t) ** 2, color=p.blue, lw=2.6,
            label=r"squared, $(1-t)^2$")
    a2.axvline(1.0, color=p.amber, ls="--", lw=1.5)
    a2.annotate("confidently RIGHT,\nand the squared\nloss charges for it",
                (-0.55, 7.6), fontsize=9, color=p.blue)
    a2.annotate("", xy=(2.85, 3.3), xytext=(1.05, 6.9),
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color=p.blue))
    a2.set_xlim(-2.2, 3.2)
    a2.set_ylim(-0.3, 10.5)
    a2.set_xlabel("$t = y f(x)$")
    a2.legend(fontsize=9, loc="upper center")
    a2.set_title("why Chapter 9's loss will not do", fontsize=10)

    fig.suptitle("The hinge bounds the zero-one loss from above, and "
                 "stops charging once you are right",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. an outlier that is not in doubt
# --------------------------------------------------------------------------

def an_outlier_that_is_not_in_doubt(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    # --- left: the picture at one outlier distance
    DX = 20.0
    XX = np.vstack([X, [DX, 0.0]])
    YY = np.r_[Y, 1.0]
    vh, vs = _fit(XX, YY, 1.0, "hinge"), _fit(XX, YY, 1.0, "squared")
    bh = -vh[2] / vh[0]
    bs = -vs[2] / vs[0]

    pos, neg = XX[YY > 0], XX[YY < 0]
    a1.scatter(pos[:, 0], pos[:, 1], marker="x", s=95, lw=2.4,
               color=p.amber, label="$y = +1$", zorder=5)
    a1.scatter(neg[:, 0], neg[:, 1], marker="o", s=95, lw=2.1,
               facecolor="none", edgecolor=p.blue, label="$y = -1$",
               zorder=5)
    a1.axvline(bh, color=p.red, lw=2.6, label=f"hinge, $x = {bh:.3f}$")
    a1.axvline(bs, color=p.blue, lw=2.6, ls="--",
               label=f"squared, $x = {bs:.3f}$")
    wrong = XX[(_pred(XX @ vs[:2] + vs[2]) != YY)]
    a1.scatter(wrong[:, 0], wrong[:, 1], s=330, facecolor="none",
               edgecolor=p.red, lw=2.2, zorder=4,
               label="squared gets these wrong")
    a1.annotate("this point was never in doubt", (DX - 0.4, 0.42),
                fontsize=9, color=p.fg, ha="right")
    a1.set_xlim(-2.0, DX + 2.0)
    a1.set_ylim(-1.9, 1.9)
    a1.set_xlabel("$x^{(1)}$")
    a1.set_ylabel("$x^{(2)}$")
    a1.legend(fontsize=7.6, loc="upper right", ncol=1, framealpha=0.93)
    a1.set_title(f"one extra positive at $({DX:g}, 0)$", fontsize=10)

    # --- right: the boundary as the outlier walks away
    Ds = np.array([6.0, 8.0, 10.0, 14.0, 20.0, 30.0, 40.0, 60.0, 80.0])
    bhs, bss, ehs, ess = [], [], [], []
    for Dx in Ds:
        XX = np.vstack([X, [Dx, 0.0]])
        YY = np.r_[Y, 1.0]
        vh, vs = _fit(XX, YY, 1.0, "hinge"), _fit(XX, YY, 1.0, "squared")
        bhs.append(-vh[2] / vh[0])
        bss.append(-vs[2] / vs[0])
        ehs.append(int((_pred(XX @ vh[:2] + vh[2]) != YY).sum()))
        ess.append(int((_pred(XX @ vs[:2] + vs[2]) != YY).sum()))
    a2.plot(Ds, bhs, color=p.red, lw=2.6, marker="o",
            label="hinge boundary")
    a2.plot(Ds, bss, color=p.blue, lw=2.6, marker="s", ls="--",
            label="squared boundary")
    bad = np.array(ess) > 0
    a2.scatter(Ds[bad], np.array(bss)[bad], s=170, facecolor="none",
               edgecolor=p.red, lw=2.0, zorder=5,
               label="squared now misclassifies")
    a2.axhline(3.0, color=p.muted, ls=":", lw=1.5)
    a2.annotate("$x = 3$: past here the boundary\n"
                "has crossed two real examples",
                (26.0, 2.40), fontsize=8.6, color=p.muted)
    a2.set_xlabel("how far out the extra positive sits")
    a2.set_ylabel("decision boundary, $x^{(1)}$")
    a2.legend(fontsize=8.4, loc="lower right")
    a2.set_title("the hinge does not move; the squared loss drifts",
                 fontsize=10)

    fig.suptitle("A point that is already right costs the hinge nothing "
                 "— and the squared loss everything",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("three-losses", three_losses, size=(9.6, 4.2), axes=False),
    figure("an-outlier-that-is-not-in-doubt", an_outlier_that_is_not_in_doubt,
           size=(10.0, 4.3), axes=False),
]

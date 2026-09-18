"""Figures for *The Dual Support Vector Machine* (§12.3.1).

1. `who-carries-the-answer` — the representer theorem made visible: marker area
   is the dual multiplier, so the three support vectors are the only examples
   with any area at all, and 500 easy extras add none.

2. `alpha-against-the-margin` — the KKT picture, and a counterexample to the
   margin note: at C = 2 the on-margin examples sit AT the box bound, not
   strictly inside it.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
XB = np.vstack([X, [4.5, 0.0]])
YB = np.r_[Y, -1.0]
BIG = 1e6


def _dual(XX, YY, C, tries=25):
    n = len(XX)
    H = (YY[:, None] * YY[None, :]) * (XX @ XX.T)
    out, bv = None, np.inf
    for s in range(tries):
        rg = np.random.default_rng(s)
        a0 = np.clip(np.abs(rg.normal(0.3, 0.3, n)), 0, C)
        r = minimize(lambda a: 0.5 * a @ H @ a - a.sum(), a0,
                     jac=lambda a: H @ a - 1.0,
                     bounds=[(0.0, C)] * n,
                     constraints=[{"type": "eq", "fun": lambda a: YY @ a,
                                   "jac": lambda a: YY}],
                     method="SLSQP", options={"maxiter": 30000, "ftol": 1e-14})
        if r.success and r.fun < bv - 1e-13:
            bv, out = r.fun, np.clip(r.x, 0.0, C)
    return out


def _primal(XX, YY, C, tries=30):
    d = XX.shape[1]
    out, bv = None, np.inf
    for s in range(tries):
        rg = np.random.default_rng(s)
        r = minimize(lambda v: 0.5 * v[:d] @ v[:d]
                     + C * np.maximum(0.0, 1 - YY * (XX @ v[:d] + v[d])).sum(),
                     np.r_[rg.normal(0, 1, d), rg.normal(0, 1)],
                     method="Powell",
                     options={"maxiter": 400000, "xtol": 1e-13, "ftol": 1e-15})
        if r.fun < bv - 1e-13:
            bv, out = r.fun, r.x.copy()
    return out[:d], float(out[d])


# --------------------------------------------------------------------------
# 1. who carries the answer
# --------------------------------------------------------------------------

def who_carries_the_answer(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.12]})

    a = _dual(X, Y, BIG)
    w = a * Y @ X
    b = float(np.mean(Y[a > 1e-9] - X[a > 1e-9] @ w))

    for lev, col, st, lwd in ((0.0, p.fg, "-", 2.4), (1.0, p.amber, "--", 1.5),
                              (-1.0, p.blue, "--", 1.5)):
        a1.axvline((lev - b) / w[0], color=col, ls=st, lw=lwd)
    for n in range(len(X)):
        if Y[n] > 0:
            a1.scatter(X[n, 0], X[n, 1], marker="x", s=95, lw=2.3,
                       color=p.amber, zorder=5)
        else:
            a1.scatter(X[n, 0], X[n, 1], marker="o", s=95, lw=2.1,
                       facecolor="none", edgecolor=p.blue, zorder=5)
        if a[n] > 1e-9:
            a1.scatter(X[n, 0], X[n, 1], s=140 + 2400 * a[n],
                       facecolor="none", edgecolor=p.green, lw=2.4, zorder=4)
            a1.annotate(rf"$\alpha = {a[n]:.2f}$", (X[n, 0] + 0.22,
                                                    X[n, 1] + 0.30),
                        fontsize=9.5, color=p.green)
        else:
            a1.annotate(r"$\alpha = 0$", (X[n, 0] + 0.16, X[n, 1] + 0.22),
                        fontsize=8.2, color=p.muted)
    a1.set_xlim(-2.2, 7.6)
    a1.set_ylim(-2.0, 2.2)
    a1.set_xlabel("$x^{(1)}$")
    a1.set_ylabel("$x^{(2)}$")
    a1.set_title(r"3 of 8 examples have $\alpha_n > 0$"
                 "\n" r"and $\sum_n \alpha_n = \|w\|^2 = 1$", fontsize=10)

    # --- right: adding easy examples changes nothing
    rg = np.random.default_rng(7)
    counts = [0, 50, 150, 300, 500]
    svs, gaps, masses = [], [], []
    for k in counts:
        if k == 0:
            XL, YL = X, Y
        else:
            ep = rg.uniform([20, -5], [40, 5], (k // 2, 2))
            en = rg.uniform([-40, -5], [-20, 5], (k - k // 2, 2))
            XL = np.vstack([X, ep, en])
            YL = np.r_[Y, np.ones(k // 2), -np.ones(k - k // 2)]
        aL = _dual(XL, YL, BIG, tries=6)
        wL = aL * YL @ XL
        svs.append(int((aL > 1e-9).sum()))
        gaps.append(max(float(np.linalg.norm(wL - w)), 1e-16))
        masses.append(max(float(aL[8:].sum()) if k else 1e-16, 1e-16))

    tot = np.array(counts) + 8
    a2.plot(tot, svs, color=p.green, lw=2.6, marker="o", ms=7,
            label="support vectors")
    a2.plot(tot, tot, color=p.muted, lw=1.6, ls=":",
            label="total examples $N$")
    a2.set_xlabel("$N$, after adding easy examples far from the boundary")
    a2.set_ylabel("count")
    a2.set_yscale("log")
    a2.set_ylim(1, 900)
    a2.legend(fontsize=9, loc="upper left")
    for xt, s in zip(tot, svs):
        a2.annotate(f"{s}", (xt, s * 1.45), fontsize=9, color=p.green,
                    ha="center")
    a2.set_title("508 examples, still 3 support vectors", fontsize=10)

    fig.suptitle("Equation 12.38: the answer is a combination of the "
                 "examples, and almost all coefficients are zero",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. alpha against the margin
# --------------------------------------------------------------------------

def alpha_against_the_margin(fig, ax, p: Palette) -> None:
    fig.clear()
    axs = fig.subplots(1, 2, sharey=False)
    for a_ax, C in zip(axs, (0.5, 2.0)):
        w, b = _primal(XB, YB, C)
        al = _dual(XB, YB, C)
        m = YB * (XB @ w + b)

        a_ax.axhline(0.0, color=p.muted, ls=":", lw=1.4)
        a_ax.axhline(C, color=p.red, ls="--", lw=1.8)
        a_ax.axvline(1.0, color=p.amber, ls="--", lw=1.8)
        a_ax.annotate(rf"$\alpha = C = {C:g}$", (m.min() + 0.1, C * 1.02),
                      fontsize=9, color=p.red)
        a_ax.annotate(r"$y f(x) = 1$", (1.05, C * 0.5), fontsize=9,
                      color=p.amber, rotation=90, va="center")
        onm = np.abs(m - 1) <= 1e-5
        a_ax.scatter(m[~onm], al[~onm], s=95, color=p.blue, zorder=4,
                     label="off the margin")
        a_ax.scatter(m[onm], al[onm], s=170, marker="D", color=p.green,
                     edgecolor=p.fg, lw=0.8, zorder=5,
                     label="exactly on the margin")
        a_ax.set_xlabel("$y_n f(x_n)$")
        a_ax.set_ylim(-0.08 * C, 1.28 * C)
        a_ax.legend(fontsize=8.4, loc="upper right")
        verdict = ("the note holds" if (onm.any()
                   and (al[onm] > 1e-7).all() and (al[onm] < C - 1e-7).all())
                   else "the note FAILS here")
        a_ax.set_title(f"$C = {C:g}$  —  {verdict}", fontsize=10)
    axs[0].set_ylabel(r"$\alpha_n$")
    fig.suptitle("The margin note is a one-way implication, and the book "
                 "states it both ways",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("who-carries-the-answer", who_carries_the_answer, size=(10.0, 4.4),
           axes=False),
    figure("alpha-against-the-margin", alpha_against_the_margin,
           size=(9.6, 4.2), axes=False),
]

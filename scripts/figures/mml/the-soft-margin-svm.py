"""Figures for *The Soft Margin SVM* (§12.2.4).

1. `slack-in-the-picture` — Figure 12.7 on the running example plus one point
   that makes it non-separable, at three values of C. The slack of every
   violating example is drawn as the segment it would have to travel to reach
   its own margin.

2. `what-c-buys` — the whole trade-off as a sweep: margin, total slack and
   error count against C over five orders of magnitude, and the two limits.
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


def _solve(XX, YY, C, seed):
    n, d = XX.shape
    rg = np.random.default_rng(seed)
    v0 = np.r_[rg.normal(0, 1, d), rg.normal(0, 1),
               np.abs(rg.normal(1, 0.5, n))]
    return minimize(lambda v: 0.5 * v[:d] @ v[:d]
                    + C * np.maximum(v[d + 1:], 0.0).sum(), v0,
                    constraints=[{"type": "ineq",
                                  "fun": lambda v: YY * (XX @ v[:d] + v[d]) - 1 + v[d + 1:]},
                                 {"type": "ineq", "fun": lambda v: v[d + 1:]}],
                    method="SLSQP", options={"maxiter": 20000, "ftol": 1e-13})


def _best(XX, YY, C, tries=30):
    out, bv = None, np.inf
    d = XX.shape[1]
    for s in range(tries):
        r = _solve(XX, YY, C, s)
        if not r.success:
            continue
        w, b = r.x[:d], r.x[d]
        xi = np.maximum(0.0, 1 - YY * (XX @ w + b))
        val = 0.5 * w @ w + C * xi.sum()
        if val < bv - 1e-12:
            bv, out = val, (w.copy(), float(b), xi)
    return out



def _pred(scores):
    """Section 12.1's rule: f(x) >= 0 is classified +1, ties included."""
    return np.where(scores >= 0.0, 1.0, -1.0)

def _scatter(ax, p: Palette, XX, YY, size=80):
    pos, neg = XX[YY > 0], XX[YY < 0]
    ax.scatter(pos[:, 0], pos[:, 1], marker="x", s=size, lw=2.3,
               color=p.amber, zorder=5)
    ax.scatter(neg[:, 0], neg[:, 1], marker="o", s=size, lw=2.0,
               facecolor="none", edgecolor=p.blue, zorder=5)


# --------------------------------------------------------------------------
# 1. slack in the picture
# --------------------------------------------------------------------------

def slack_in_the_picture(fig, ax, p: Palette) -> None:
    fig.clear()
    axs = fig.subplots(1, 3, sharey=True)
    for a, C in zip(axs, (0.1, 1.0, 10.0)):
        got = _best(XB, YB, C)
        w, b, xi = got
        nw = np.linalg.norm(w)
        a.set_xlim(-1.8, 7.4)
        a.set_ylim(-2.1, 2.1)
        # the three level sets, as vertical-ish lines
        ys = np.array([-2.1, 2.1])
        for lev, col, lwd, st in ((0.0, p.fg, 2.4, "-"),
                                  (1.0, p.amber, 1.5, "--"),
                                  (-1.0, p.blue, 1.5, "--")):
            if abs(w[0]) > 1e-9:
                xs = (lev - b - w[1] * ys) / w[0]
                a.plot(xs, ys, color=col, lw=lwd, ls=st, zorder=2)
        # every slack, drawn as the distance to its own margin
        for n in range(len(XB)):
            if xi[n] <= 1e-6:
                continue
            step = YB[n] * xi[n] / (nw ** 2) * w
            a.annotate("", xy=tuple(XB[n] + step), xytext=tuple(XB[n]),
                       arrowprops=dict(arrowstyle="-|>", lw=1.7,
                                       color=p.red, alpha=0.85), zorder=4)
        _scatter(a, p, XB, YB)
        a.set_xlabel("$x^{(1)}$")
        a.set_title(f"$C = {C:g}$\nmargin {1/nw:.2f},  "
                    r"$\sum\xi_n$ = " + f"{xi.sum():.2f},  "
                    f"{int((_pred(XB @ w + b) != YB).sum())} wrong",
                    fontsize=9.5)
    axs[0].set_ylabel("$x^{(2)}$")
    fig.suptitle("Equation 12.26: the slack each example needs to reach "
                 "its own margin",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what C buys
# --------------------------------------------------------------------------

def what_c_buys(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.05, 1.0]})

    Cs = np.logspace(-4, 3, 22)
    margins, slacks, errs, norms = [], [], [], []
    for C in Cs:
        got = _best(XB, YB, float(C), tries=18)
        w, b, xi = got
        nw = np.linalg.norm(w)
        margins.append(1.0 / nw)
        slacks.append(float(xi.sum()))
        errs.append(int((_pred(XB @ w + b) != YB).sum()))
        norms.append(nw)

    a1.loglog(Cs, margins, color=p.blue, lw=2.4, marker="o", ms=4,
              label=r"margin $1/\|w\|$")
    a1.loglog(Cs, slacks, color=p.red, lw=2.4, marker="s", ms=4,
              label=r"total slack $\sum\xi_n$")
    a1.set_xlabel("$C$")
    a1.set_ylabel("value")
    a1.legend(fontsize=9, loc="upper right")
    a1.set_title("the trade Equation 12.26a makes", fontsize=10)

    a2.semilogx(Cs, errs, color=p.purple, lw=2.4, marker="o", ms=5,
                drawstyle="steps-mid")
    a2.set_xlabel("$C$")
    a2.set_ylabel("training examples misclassified")
    a2.set_ylim(-0.4, max(errs) + 0.6)
    a2.axhline(1, color=p.green, ls="--", lw=1.6)
    a2.annotate("1 is the floor: the intruder sits inside\n"
                "the positive hull, so no hyperplane can\n"
                "ever get it right",
                (1.3e-4, 2.05), fontsize=8.5, color=p.green, va="center")
    a2.set_title("and what it costs in errors", fontsize=10)

    fig.suptitle("$C$ is the price of a violation, and it buys margin "
                 "at the cost of accuracy",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("slack-in-the-picture", slack_in_the_picture, size=(10.0, 3.9),
           axes=False),
    figure("what-c-buys", what_c_buys, size=(9.6, 4.2), axes=False),
]

"""Figures for *Numerical Solution* (§12.5).

1. `the-subgradient` — Equation 12.54 drawn: the fan of lines that lie below
   the hinge at t = 1, and the resulting step function with a vertical segment
   where the derivative does not exist.

2. `what-it-costs-to-solve` — subgradient descent's convergence against the
   QP optimum, and the book's aside that standard-form convex solvers are "not
   often used in practice", timed.
"""

from __future__ import annotations

import time

import numpy as np
from scipy.optimize import minimize

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
XB = np.vstack([X, [4.5, 0.0]])
YB = np.r_[Y, -1.0]


def _obj(w, b, XX, YY, C):
    return 0.5 * w @ w + C * np.maximum(0.0, 1 - YY * (XX @ w + b)).sum()


# --------------------------------------------------------------------------
# 1. the subgradient
# --------------------------------------------------------------------------

def the_subgradient(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    t = np.linspace(-2.0, 3.2, 900)
    a1.plot(t, np.maximum(0.0, 1 - t), color=p.red, lw=3.0, zorder=4,
            label=r"$\ell(t) = \max\{0,\, 1-t\}$")
    for g, col in ((-1.0, p.blue), (-0.75, p.purple), (-0.5, p.green),
                   (-0.25, p.amber), (0.0, p.muted)):
        a1.plot(t, g * (t - 1.0), color=col, lw=1.5, ls="--", alpha=0.95,
                zorder=2)
    a1.plot([1.0], [0.0], "o", ms=9, color=p.fg, zorder=6)
    a1.annotate("every line through $(1, 0)$ with\n"
                r"slope in $[-1, 0]$ stays below $\ell$",
                (1.22, 1.55), fontsize=9, color=p.fg)
    a1.set_xlim(-2.0, 3.2)
    a1.set_ylim(-0.8, 3.2)
    a1.set_xlabel("$t = y f(x)$")
    a1.set_ylabel("loss")
    a1.legend(fontsize=9, loc="upper right")
    a1.set_title("the subdifferential at the hinge is an interval",
                 fontsize=10)

    tl = np.linspace(-2.0, 1.0, 400)
    tr = np.linspace(1.0, 3.2, 400)
    a2.plot(tl, np.full_like(tl, -1.0), color=p.red, lw=3.0)
    a2.plot(tr, np.zeros_like(tr), color=p.red, lw=3.0)
    a2.plot([1.0, 1.0], [-1.0, 0.0], color=p.red, lw=3.0, alpha=0.45)
    a2.plot([1.0], [-1.0], "o", ms=8, color=p.red)
    a2.plot([1.0], [0.0], "o", ms=8, color=p.red)
    a2.annotate(r"$g(1) \in [-1, 0]$", (1.12, -0.52), fontsize=10.5,
                color=p.red)
    a2.annotate(r"$g(t) = -1$", (-1.85, -0.9), fontsize=10, color=p.fg)
    a2.annotate(r"$g(t) = 0$", (2.1, 0.08), fontsize=10, color=p.fg)
    a2.axhline(0.0, color=p.grid, lw=1.0)
    a2.set_xlim(-2.0, 3.2)
    a2.set_ylim(-1.35, 0.45)
    a2.set_xlabel("$t = y f(x)$")
    a2.set_ylabel("subgradient $g(t)$")
    a2.set_title("Equation 12.54, with its one vertical segment",
                 fontsize=10)

    fig.suptitle("The hinge is differentiable everywhere except at one "
                 "point, and Equation 12.54 covers it",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what it costs to solve
# --------------------------------------------------------------------------

def what_it_costs_to_solve(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)
    C = 1.0

    # reference optimum
    best, bv = None, np.inf
    for s in range(30):
        rg = np.random.default_rng(s)
        r = minimize(lambda v: _obj(v[:2], v[2], XB, YB, C),
                     np.r_[rg.normal(0, 1, 2), rg.normal(0, 1)],
                     method="Powell",
                     options={"maxiter": 400000, "xtol": 1e-13, "ftol": 1e-15})
        if r.fun < bv - 1e-13:
            bv, best = r.fun, r.x.copy()
    f_star = bv

    rg = np.random.default_rng(0)
    w, b = rg.normal(0, 0.3, 2), float(rg.normal(0, 0.3))
    gaps, ks, run = [], [], _obj(w, b, XB, YB, C)
    for k in range(1, 200001):
        t = YB * (XB @ w + b)
        act = t < 1.0
        gw = w - C * (YB[act] @ XB[act]) if act.any() else w.copy()
        gb = -C * YB[act].sum() if act.any() else 0.0
        eta = 0.5 / k
        w, b = w - eta * gw, b - eta * gb
        run = min(run, _obj(w, b, XB, YB, C))
        if k in (1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000,
                 100000, 200000):
            ks.append(k)
            gaps.append(max(run - f_star, 1e-12))
    a1.loglog(ks, gaps, color=p.blue, lw=2.5, marker="o", ms=5,
              label="subgradient descent")
    ref = np.array(ks, dtype=float)
    a1.loglog(ref, gaps[0] / np.sqrt(ref), color=p.muted, lw=1.6, ls="--",
              label=r"$\propto 1/\sqrt{k}$")
    a1.set_xlabel("iterations $k$")
    a1.set_ylabel("objective gap to the optimum")
    a1.legend(fontsize=9, loc="lower left")
    a1.set_title("a subgradient is not a descent direction,\n"
                 "and the rate shows it", fontsize=10)

    # --- right: a specialised solver against a generic one
    try:
        from sklearn.svm import SVC
        Ns = [100, 200, 400, 800]
        tl, tg = [], []
        rg2 = np.random.default_rng(0)
        for N_ in Ns:
            mu = np.array([2.0, 0.0])
            Xl = np.vstack([rg2.normal(mu, 1.0, (N_ // 2, 2)),
                            rg2.normal(-mu, 1.0, (N_ // 2, 2))])
            Yl = np.r_[np.ones(N_ // 2), -np.ones(N_ // 2)]
            t0 = time.perf_counter()
            SVC(C=1.0, kernel="linear", tol=1e-8).fit(Xl, Yl)
            tl.append(max(time.perf_counter() - t0, 1e-5))
            Hl = (Yl[:, None] * Yl[None, :]) * (Xl @ Xl.T)
            t0 = time.perf_counter()
            minimize(lambda a: 0.5 * a @ Hl @ a - a.sum(), np.full(N_, 0.5),
                     jac=lambda a: Hl @ a - 1.0, bounds=[(0.0, 1.0)] * N_,
                     constraints=[{"type": "eq", "fun": lambda a: Yl @ a,
                                   "jac": lambda a: Yl}],
                     method="SLSQP", options={"maxiter": 120, "ftol": 1e-9})
            tg.append(max(time.perf_counter() - t0, 1e-5))
        a2.loglog(Ns, np.array(tl) * 1e3, color=p.green, lw=2.5, marker="o",
                  ms=6, label="LIBSVM (specialised)")
        a2.loglog(Ns, np.array(tg) * 1e3, color=p.red, lw=2.5, marker="s",
                  ms=6, label="generic SLSQP on 12.57")
        for n_, a_, b_ in zip(Ns, tl, tg):
            a2.annotate(f"{b_/a_:.0f}x", (n_, b_ * 1e3 * 1.6), fontsize=8.6,
                        color=p.red, ha="center")
        a2.set_xlabel("$N$")
        a2.set_ylabel("time to fit, milliseconds")
        a2.legend(fontsize=8.6, loc="upper left")
    except ImportError:
        a2.text(0.5, 0.5, "scikit-learn unavailable", ha="center",
                transform=a2.transAxes)
    a2.set_title("why the book says this approach is\n"
                 "'not often used in practice'", fontsize=10)

    fig.suptitle("Two ways to solve it, and the cost of each",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-subgradient", the_subgradient, size=(9.6, 4.2), axes=False),
    figure("what-it-costs-to-solve", what_it_costs_to_solve, size=(9.8, 4.3),
           axes=False),
]

"""Figures for *Maximum Likelihood and Its Obstacle* (Section 11.2's opening).

1. `log-of-a-sum` — why Equation 11.10 and not Equation 11.9. The product form
   underflows to exactly 0.0 by about N = 185; the sum of logs does not. And
   the K = 1 case of Equation 11.11, where the log does get inside.

2. `a-fixed-point-not-a-formula` — Equation 11.20's right-hand side plotted
   against its left. Feeding the answer back in moves it by 4.295713, then
   0.130775, then 0.018414 -- which is what "no closed-form solution" means.

3. `many-summits` — 400 random restarts on the book's seven points. 218 of
   them collapse a component onto a data point and report a HIGHER likelihood
   than any genuine fit; of the rest, only two distinct optima exist, and the
   book's initialisation reaches the worse one by 0.067161 nats.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

X = np.array([-3.0, -2.5, -1.0, 0.0, 2.0, 4.0, 5.0])
N = len(X)
MU0 = np.array([-4.0, 0.0, 8.0])
VAR0 = np.array([1.0, 0.2, 3.0])
PI0 = np.ones(3) / 3


def _g(x, mu, var):
    return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)


def _comp(x, pi, mu, var):
    return pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])


def _ll(x, pi, mu, var):
    return float(np.log(_comp(x, pi, mu, var).sum(1)).sum())


def _resp(x, pi, mu, var):
    W = _comp(x, pi, mu, var)
    return W / W.sum(1, keepdims=True)


# --------------------------------------------------------------------------
# 1. the log of a sum
# --------------------------------------------------------------------------

def log_of_a_sum(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    rng = np.random.default_rng(0)
    ns = np.arange(10, 320, 10)
    prod, sl = [], []
    for n in ns:
        xs = rng.normal(0, 3, int(n))
        W = _comp(xs, PI0, MU0, VAR0).sum(1)
        prod.append(float(np.prod(W)))
        sl.append(float(np.log(W).sum()))
    prod = np.array(prod)
    a1.semilogy(ns, np.maximum(prod, 1e-320), color=p.red, lw=2.2,
                marker="o", ms=3.5, label="Eq 11.9, the product")
    a1.axhline(5e-324, color=p.muted, lw=1.2, ls=":")
    a1.annotate("smallest positive float64", (12, 1.4e-323), fontsize=8.5,
                color=p.muted)
    dead = ns[prod == 0.0]
    if len(dead):
        a1.axvline(dead[0], color=p.amber, ls="--", lw=1.5)
        a1.annotate(f"exactly 0.0\nfrom N $\\approx$ 185", (dead[0] + 8, 1e-200),
                    fontsize=9.5, color=p.amber)
    a1.set_xlabel("$N$")
    a1.set_ylabel("$p(\\mathcal{X}\\mid\\theta)$")
    a1.set_ylim(1e-330, 1e5)
    a1.legend(fontsize=9, loc="upper right")
    a1.set_title("the product form dies; the log form does not", fontsize=10)

    a2.plot(ns, sl, color=p.blue, lw=2.4, marker="s", ms=3.5,
            label="Eq 11.10, the sum of logs")
    a2.set_xlabel("$N$")
    a2.set_ylabel("$\\log p(\\mathcal{X}\\mid\\theta)$")
    a2.legend(fontsize=9)
    a2.set_title("perfectly well-behaved, and linear in $N$", fontsize=10)
    fig.suptitle("Equation 11.10 is not cosmetic, and the sum inside it is "
                 "the whole problem",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the fixed point
# --------------------------------------------------------------------------

def a_fixed_point_not_a_formula(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.05, 1.0]})

    # the map mu_1 -> update(mu_1), with the other two held at their values
    grid = np.linspace(-6.0, 2.0, 400)
    out = []
    for m in grid:
        mu = np.array([m, MU0[1], MU0[2]])
        R = _resp(X, PI0, mu, VAR0)
        out.append(((R * X[:, None]).sum(0) / R.sum(0))[0])
    out = np.array(out)
    a1.plot(grid, out, color=p.blue, lw=2.4, label="Equation 11.20's output")
    a1.plot(grid, grid, color=p.muted, lw=1.4, ls=":", label="$y = x$")
    cross = grid[np.argmin(np.abs(out - grid))]
    a1.plot([cross], [cross], "o", ms=9, color=p.amber, zorder=5)
    a1.annotate(f"fixed point\n$\\mu_1 \\approx {cross:.3f}$",
                (cross + 0.25, cross - 1.1), fontsize=9.5, color=p.amber)
    for xv in X:
        a1.plot([xv], [-6.3], marker="|", ms=10, color=p.red)
    a1.set_xlabel("$\\mu_1$ put in")
    a1.set_ylabel("$\\mu_1$ that comes out")
    a1.legend(fontsize=9, loc="upper left")
    a1.set_title("the $\\mu_1$ slice, $\\mu_2$ and $\\mu_3$ held: a formula\nwould be a flat line", fontsize=10)

    mu = MU0.copy()
    moves = []
    for _ in range(8):
        R = _resp(X, PI0, mu, VAR0)
        nxt = (R * X[:, None]).sum(0) / R.sum(0)
        moves.append(float(np.abs(nxt - mu).max()))
        mu = nxt
    a2.semilogy(range(1, 9), moves, color=p.blue, lw=2.4, marker="o")
    for k, v in enumerate(moves[:4]):
        a2.annotate(f"{v:.6f}", (k + 1.1, v * 1.25), fontsize=9, color=p.fg)
    a2.set_xlabel("round")
    a2.set_ylabel("how far $\\mu$ moved")
    a2.set_title("plug the answer back in and it changes", fontsize=10)
    fig.suptitle("Equation 11.20 is a fixed-point condition, not a solution",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the summits
# --------------------------------------------------------------------------

def many_summits(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1.0]})

    rng = np.random.default_rng(3)
    Ls, mins = [], []
    for _ in range(400):
        pi = rng.dirichlet(np.ones(3))
        mu = rng.uniform(-6, 8, 3)
        var = np.exp(rng.uniform(-1.5, 1.5, 3))
        for _ in range(2000):
            R = _resp(X, pi, mu, var)
            Nk = R.sum(0)
            if Nk.min() < 1e-12:
                break
            mu = (R * X[:, None]).sum(0) / Nk
            var = np.maximum((R * (X[:, None] - mu[None, :]) ** 2).sum(0)
                             / Nk, 1e-10)
            pi = Nk / N
        Ls.append(_ll(X, pi, mu, var))
        mins.append(float(var.min()))
    Ls, mins = np.array(Ls), np.array(mins)
    bad = mins < 1e-6

    bins = np.linspace(-15, 7, 56)
    a1.hist(Ls[bad], bins=bins, color=p.red, alpha=0.75,
            label=f"a component collapsed ({int(bad.sum())})")
    a1.hist(Ls[~bad], bins=bins, color=p.blue, alpha=0.85,
            label=f"genuine fits ({int((~bad).sum())})")
    a1.axvline(-13.973323, color=p.amber, lw=1.8, ls="--")
    a1.annotate("the book's\n$-13.973323$", (-14.9, 62), fontsize=9,
                color=p.amber)
    a1.annotate("a better genuine\noptimum: $-13.906162$", (-12.6, 40),
                fontsize=9, color=p.blue,
                arrowprops=dict(arrowstyle="->", color=p.blue, lw=1.2))
    a1.set_xlabel("final log-likelihood")
    a1.set_ylabel("restarts")
    a1.legend(fontsize=8.8, loc="upper right")
    a1.set_title("higher likelihood, worse model", fontsize=10)

    vs = np.logspace(-1, -30, 60)
    lls = []
    for v in vs:
        lls.append(_ll(X, np.array([0.1, 0.45, 0.45]),
                       np.array([X[0], 0.0, 4.0]), np.array([v, 4.0, 4.0])))
    a2.semilogx(vs, lls, color=p.red, lw=2.4)
    a2.axhline(-13.973323, color=p.amber, lw=1.6, ls="--")
    a2.annotate("the book's converged fit", (2e-28, -12.6), fontsize=9,
                color=p.amber)
    a2.invert_xaxis()
    a2.set_xlabel("$\\sigma_1^2$, with $\\mu_1$ pinned to a data point")
    a2.set_ylabel("log-likelihood")
    a2.set_title("Section 11.5's singularity: unbounded above", fontsize=10)
    fig.suptitle("There is no maximum likelihood estimate here, only local "
                 "ones",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("log-of-a-sum", log_of_a_sum, size=(9.4, 4.2), axes=False),
    figure("a-fixed-point-not-a-formula", a_fixed_point_not_a_formula,
           size=(9.4, 4.2), axes=False),
    figure("many-summits", many_summits, size=(9.6, 4.3), axes=False),
]

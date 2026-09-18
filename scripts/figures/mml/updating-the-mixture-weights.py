"""Figures for *Updating the Mixture Weights* (Section 11.2.4).

1. `the-constraint-does-the-work` — the gradient of the log-likelihood in pi is
   strictly positive in every coordinate, so unconstrained ascent sends every
   weight off to infinity. The Lagrange multiplier comes out as exactly -N,
   measured to 0.0 from all three components.

2. `one-cycle-complete` — the three updates in order, with the log-likelihood
   after each: -28.325536, -16.004150, -14.547617, -14.410485. The book prints
   28.3 and 14.4 for the two ends.
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


def _resp(pi, mu, var):
    W = pi[None, :] * _g(X[:, None], mu[None, :], var[None, :])
    return W / W.sum(1, keepdims=True)


def _ll(pi, mu, var):
    W = pi[None, :] * _g(X[:, None], mu[None, :], var[None, :])
    return float(np.log(W.sum(1)).sum())


def _mix(xs, pi, mu, var):
    return (pi[None, :] * _g(xs[:, None], mu[None, :], var[None, :])).sum(1)


R0 = _resp(PI0, MU0, VAR0)
NK0 = R0.sum(0)
MU1 = (R0 * X[:, None]).sum(0) / NK0
VAR1 = (R0 * (X[:, None] - MU1[None, :]) ** 2).sum(0) / NK0
PI1 = NK0 / N


# --------------------------------------------------------------------------
# 1. the constraint
# --------------------------------------------------------------------------

def the_constraint_does_the_work(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    pi = PI0.copy()
    step = 0.02
    sums, mins = [], []
    for _ in range(40):
        sums.append(float(pi.sum()))
        mins.append(float(pi.min()))
        W = pi[None, :] * _g(X[:, None], MU1[None, :], VAR1[None, :])
        grad = (_g(X[:, None], MU1[None, :], VAR1[None, :])
                / W.sum(1, keepdims=True)).sum(0)
        pi = pi + step * grad
    a1.plot(sums, color=p.red, lw=2.4,
            label="unconstrained gradient ascent")
    a1.axhline(1.0, color=p.blue, lw=2.0, ls="--",
               label="Equation 11.42, always")
    a1.annotate("Equation 11.2's constraint", (1.2, 1.12), fontsize=9.5,
                color=p.blue)
    a1.set_xlabel("gradient step")
    a1.set_ylabel("$\\sum_k \\pi_k$")
    a1.legend(fontsize=9, loc="upper left")
    a1.set_title("the gradient is positive in every coordinate",
                 fontsize=10)

    lam = np.array([-NK0[k] / PI1[k] for k in range(3)])
    a2.bar([f"$k$={k+1}" for k in range(3)], lam, color=p.blue, width=0.5)
    a2.axhline(-N, color=p.amber, lw=2.0, ls="--")
    a2.annotate(f"$\\lambda = -N = {-N}$", (1.6, -N + 0.42), fontsize=10,
                color=p.amber)
    for k in range(3):
        a2.text(k, lam[k] - 0.55, f"{lam[k]:.6f}", ha="center", fontsize=9,
                color=p.fg)
    a2.set_ylim(-9.2, 0.6)
    a2.set_ylabel("$\\lambda$ solved from $\\pi_k = -N_k/\\lambda$")
    a2.set_title("Equation 11.48, from each component separately",
                 fontsize=10)
    fig.suptitle("The weights are the only update that needs a Lagrange "
                 "multiplier, and it is $-N$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. a full cycle
# --------------------------------------------------------------------------

def one_cycle_complete(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.85], hspace=0.55,
                          wspace=0.3, top=0.84)

    stages = [
        ("initialisation", PI0, MU0, VAR0),
        ("+ means\n(11.2.2)", PI0, MU1, VAR0),
        ("+ variances\n(11.2.3)", PI0, MU1, VAR1),
        ("+ weights\n(11.2.4)", PI1, MU1, VAR1),
    ]
    xs = np.linspace(-7, 13, 1400)
    cols = [p.blue, p.green, p.purple]
    for j, (ttl, pi, mu, var) in enumerate(stages):
        a = fig.add_subplot(gs[0, j])
        for k in range(3):
            a.plot(xs, pi[k] * _g(xs, mu[k], var[k]), color=cols[k], lw=1.2,
                   ls="--")
        a.plot(xs, _mix(xs, pi, mu, var), color=p.amber, lw=2.2)
        a.plot(X, np.zeros(N), "|", ms=10, color=p.red)
        a.set_xlim(-7, 11)
        a.set_ylim(-0.02, 0.62)
        a.set_xlabel("$x$")
        if j == 0:
            a.set_ylabel("$p(x)$")
        a.set_title(f"{ttl}\n$-L$ = {-_ll(pi, mu, var):.4f}", fontsize=9.5)

    b = fig.add_subplot(gs[1, :])
    vals = [-_ll(pi, mu, var) for _, pi, mu, var in stages]
    names = [t.replace("\n", " ") for t, *_ in stages]
    b.plot(range(4), vals, color=p.amber, lw=2.6, marker="o", ms=9)
    for j, v in enumerate(vals):
        b.annotate(f"{v:.6f}", (j, v + 0.9), ha="center", fontsize=9.5,
                   color=p.fg)
    for j in range(3):
        b.annotate(f"$-${vals[j]-vals[j+1]:.6f}",
                   (j + 0.5, 0.5 * (vals[j] + vals[j + 1]) - 1.6),
                   ha="center", fontsize=9, color=p.green)
    b.set_xticks(range(4))
    b.set_xticklabels(["initialisation", "+ means (11.2.2)",
                        "+ variances (11.2.3)", "+ weights (11.2.4)"],
                       fontsize=9)
    b.set_ylabel("negative log-likelihood")
    b.set_ylim(11, 31)
    b.set_title("the book prints 28.3 at the start and 14.4 at the end",
                fontsize=10)
    fig.suptitle("One complete update cycle, one update at a time",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-constraint-does-the-work", the_constraint_does_the_work,
           size=(9.4, 4.2), axes=False),
    figure("one-cycle-complete", one_cycle_complete, size=(9.6, 5.6),
           axes=False),
]

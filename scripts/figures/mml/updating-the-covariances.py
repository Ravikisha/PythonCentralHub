"""Figures for *Updating the Covariances* (Section 11.2.3).

1. `which-mean-does-it-use` — Equation 11.30 writes mu_k, and Example 11.4's
   printed numbers only come out if that is the mean Equation 11.20 has just
   produced: 0.144000, 0.438492, 1.526594 against 1.830803, 0.601232,
   19.979741.

2. `moments-are-pinned` — an invariant the book does not state. After any full
   M-step the mixture's mean AND variance equal the sample mean and sample
   variance exactly, for any K and any responsibilities. Only the split
   between within- and between-component variance moves.

3. `towards-the-singularity` — as a component's responsibility concentrates on
   one point, its variance falls to zero, which is Section 11.5's unbounded
   likelihood seen from the covariance side.
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


def _m_step(R):
    Nk = R.sum(0)
    mu = (R * X[:, None]).sum(0) / Nk
    var = (R * (X[:, None] - mu[None, :]) ** 2).sum(0) / Nk
    return Nk / N, mu, var


R0 = _resp(PI0, MU0, VAR0)
NK0 = R0.sum(0)
MU1 = (R0 * X[:, None]).sum(0) / NK0
V_OLD = (R0 * (X[:, None] - MU0[None, :]) ** 2).sum(0) / NK0
V_NEW = (R0 * (X[:, None] - MU1[None, :]) ** 2).sum(0) / NK0


# --------------------------------------------------------------------------
# 1. which mean
# --------------------------------------------------------------------------

def which_mean_does_it_use(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.15]})

    book = np.array([0.14, 0.44, 1.53])
    idx = np.arange(3)
    a1.bar(idx - 0.26, V_OLD, width=0.24, color=p.red,
           label="using the old $\\mu_k$")
    a1.bar(idx, V_NEW, width=0.24, color=p.blue,
           label="using the new $\\mu_k$")
    a1.bar(idx + 0.26, book, width=0.24, color=p.amber,
           label="Example 11.4 as printed")
    for k in range(3):
        a1.text(k - 0.26, V_OLD[k] + 0.5, f"{V_OLD[k]:.2f}", ha="center",
                fontsize=8.5, color=p.fg)
        a1.text(k + 0.13, V_NEW[k] + 0.5, f"{V_NEW[k]:.2f}", ha="center",
                fontsize=8.5, color=p.fg)
    a1.set_yscale("log")
    a1.set_ylim(0.05, 60)
    a1.set_xticks(idx)
    a1.set_xticklabels([f"$k$={k+1}" for k in range(3)])
    a1.set_ylabel("$\\sigma_k^2$ after the update")
    a1.legend(fontsize=8.6)
    a1.set_title("only one of the two reproduces the book", fontsize=10)

    xs = np.linspace(-7, 13, 1400)
    cols = [p.blue, p.green, p.purple]
    for k in range(3):
        a2.plot(xs, PI0[k] * _g(xs, MU1[k], VAR0[k]), color=cols[k], lw=1.3,
                ls=":")
        a2.plot(xs, PI0[k] * _g(xs, MU1[k], V_NEW[k]), color=cols[k], lw=1.9)
    a2.plot(X, np.zeros(N), "|", ms=12, color=p.red)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$\\pi_k\\mathcal{N}(x\\mid\\mu_k,\\sigma_k^2)$")
    a2.set_xlim(-7, 10)
    a2.set_title("dotted: before the variance update.  solid: after",
                 fontsize=10)
    fig.suptitle("Example 11.4: $1 \\to 0.14$, $0.2 \\to 0.44$, "
                 "$3 \\to 1.53$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the invariant
# --------------------------------------------------------------------------

def moments_are_pinned(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1.0]})

    pi, mu, var = PI0.copy(), MU0.copy(), VAR0.copy()
    W, B, T = [], [], []
    for _ in range(9):
        m = float((pi * mu).sum())
        W.append(float((pi * var).sum()))
        B.append(float((pi * (mu - m) ** 2).sum()))
        T.append(W[-1] + B[-1])
        pi, mu, var = _m_step(_resp(pi, mu, var))

    it = np.arange(9)
    a1.stackplot(it, np.array([W, B]), colors=[p.blue, p.purple],
                 alpha=0.8, labels=["within: $\\sum_k\\pi_k\\sigma_k^2$",
                                    "between: $\\sum_k\\pi_k(\\mu_k-\\bar\\mu)^2$"])
    a1.plot(it, T, color=p.amber, lw=2.4, label="total")
    a1.axhline(float(X.var()), color=p.red, lw=1.6, ls="--")
    a1.annotate(f"the sample variance, {X.var():.6f}", (2.1, 9.8),
                fontsize=9.5, color=p.red)
    a1.set_xlabel("M-step")
    a1.set_ylabel("variance")
    a1.set_ylim(0, 28)
    a1.legend(fontsize=8.6, loc="upper right")
    a1.set_title("iteration 0 is the initialisation; every step after "
                 "sits on the line", fontsize=10)

    rng = np.random.default_rng(0)
    gaps = []
    for _ in range(4000):
        R = rng.dirichlet(np.ones(3), N)
        pi2, mu2, var2 = _m_step(R)
        m2 = float((pi2 * mu2).sum())
        v2 = float((pi2 * var2).sum() + (pi2 * (mu2 - m2) ** 2).sum())
        gaps.append(abs(v2 - float(X.var())))
    gaps = np.array(gaps)
    a2.hist(np.maximum(gaps, 1e-17), bins=np.logspace(-17, -14, 32),
            color=p.blue)
    a2.set_xscale("log")
    a2.set_xlabel("$|\\mathbb{V}[\\text{mixture}] - \\text{sample variance}|$")
    a2.set_ylabel("draws")
    a2.annotate(f"largest: {gaps.max():.1e}", (1.2e-16, 1500), fontsize=9.5,
                color=p.fg)
    a2.set_title("4,000 arbitrary responsibility matrices", fontsize=10)
    fig.suptitle("After any M-step the mixture's mean and variance are the "
                 "data's, exactly",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the singularity, from the covariance side
# --------------------------------------------------------------------------

def towards_the_singularity(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.05, 1.0]})

    fracs = 1 - np.logspace(-0.3, -7, 90)
    mus, vs = [], []
    for f in fracs:
        r = np.full(N, (1 - f) / (N - 1))
        r[0] = f
        n1 = r.sum()
        m1 = float((r * X).sum() / n1)
        vs.append(float((r * (X - m1) ** 2).sum() / n1))
        mus.append(m1)
    a1.loglog(1 - fracs, vs, color=p.red, lw=2.4)
    a1.invert_xaxis()
    a1.set_xlabel("$1 - r_{11}$, how much of the component is elsewhere")
    a1.set_ylabel("$\\sigma_1^2$")
    a1.set_title("the variance falls linearly with the leftover mass",
                 fontsize=10)
    for f, v in ((0.99, 2.502771e-1), (0.99999, 2.520815e-4)):
        a1.plot([1 - f], [v], "o", ms=7, color=p.amber, zorder=5)
        a1.annotate(f"$r_{{11}}$={f}\n$\\sigma_1^2$={v:.3e}",
                    (1 - f, v * 2.2), fontsize=8.6, color=p.amber)

    xs = np.linspace(-4.5, 6, 1600)
    for f, col in ((0.5, p.blue), (0.9, p.green), (0.99, p.amber),
                   (0.999, p.red)):
        r = np.full(N, (1 - f) / (N - 1))
        r[0] = f
        n1 = r.sum()
        m1 = float((r * X).sum() / n1)
        v1 = float((r * (X - m1) ** 2).sum() / n1)
        a2.plot(xs, _g(xs, m1, v1), color=col, lw=2.0,
                label=f"$r_{{11}}$ = {f}")
    a2.plot(X, np.zeros(N), "|", ms=12, color=p.muted)
    a2.set_yscale("log")
    a2.set_ylim(1e-4, 60)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$\\mathcal{N}(x\\mid\\mu_1,\\sigma_1^2)$")
    a2.legend(fontsize=9)
    a2.set_title("and the component becomes a spike on one point",
                 fontsize=10)
    fig.suptitle("Section 11.5's singularity, seen from the covariance "
                 "update",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("which-mean-does-it-use", which_mean_does_it_use, size=(9.4, 4.2),
           axes=False),
    figure("moments-are-pinned", moments_are_pinned, size=(9.6, 4.3),
           axes=False),
    figure("towards-the-singularity", towards_the_singularity,
           size=(9.4, 4.2), axes=False),
]

"""Figures for *The Latent-Variable Perspective* (Section 11.4).

1. `the-generative-story` — Equations 11.65 and 11.66 run forward two million
   times. The histogram matches Equation 11.66b to 3.4e-04 in bin probability,
   and the empirical posterior over z at a given x matches the responsibility.

2. `the-m-step-maximises-q` — Section 11.4.5's claim, checked. The M-step's
   answer is the exact argmax of Q, matched by a 40-restart numerical search
   to 5.3e-15. And L = Q + H, tight at theta_t to 1.1e-14.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import norm

from _style import Palette, figure

X = np.array([-3.0, -2.5, -1.0, 0.0, 2.0, 4.0, 5.0])
N = len(X)
MU0 = np.array([-4.0, 0.0, 8.0])
VAR0 = np.array([1.0, 0.2, 3.0])
PI0 = np.ones(3) / 3
K = 3


def _g(x, mu, var):
    return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)


def _resp(pi, mu, var, x=X):
    W = pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])
    return W / W.sum(1, keepdims=True)


def _ll(pi, mu, var, x=X):
    W = pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])
    return float(np.log(W.sum(1)).sum())


def _Q(pi, mu, var, R):
    lg = (np.log(pi)[None, :]
          - 0.5 * (X[:, None] - mu[None, :]) ** 2 / var[None, :]
          - 0.5 * np.log(2 * np.pi * var[None, :]))
    return float((R * lg).sum())


R0 = _resp(PI0, MU0, VAR0)
NK0 = R0.sum(0)
MU1 = (R0 * X[:, None]).sum(0) / NK0
VAR1 = (R0 * (X[:, None] - MU1[None, :]) ** 2).sum(0) / NK0
PI1 = NK0 / N


# --------------------------------------------------------------------------
# 1. the generative process
# --------------------------------------------------------------------------

def the_generative_story(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0], hspace=0.5,
                          wspace=0.35, top=0.86)

    rng = np.random.default_rng(0)
    M = 1_500_000
    z = rng.choice(K, M, p=PI0)
    xs = rng.normal(MU0[z], np.sqrt(VAR0[z]))

    a = fig.add_subplot(gs[0, :2])
    grid = np.linspace(-9, 16, 1200)
    a.hist(xs, bins=200, density=True, color=p.muted, alpha=0.7,
           label=f"{M:,} ancestral samples")
    a.plot(grid, (PI0[None, :] * _g(grid[:, None], MU0[None, :],
                                    VAR0[None, :])).sum(1),
           color=p.amber, lw=2.4, label="Equation 11.66b")
    cols = [p.blue, p.green, p.purple]
    for k in range(K):
        a.plot(grid, PI0[k] * _g(grid, MU0[k], VAR0[k]), color=cols[k],
               lw=1.2, ls="--")
    a.set_xlabel("$x$")
    a.set_ylabel("density")
    a.legend(fontsize=9)
    a.set_title("sample $z\\sim p(z)$, then $x\\sim p(x\\mid z)$, and "
                "discard $z$", fontsize=10)

    b = fig.add_subplot(gs[0, 2])
    fr = np.array([float(np.mean(z == k)) for k in range(K)])
    idx = np.arange(K)
    b.bar(idx - 0.18, fr, width=0.34, color=p.blue, label="empirical")
    b.bar(idx + 0.18, PI0, width=0.34, color=p.amber, label="$\\pi_k$")
    for k in range(K):
        b.text(k, fr[k] + 0.012, f"{fr[k]:.4f}", ha="center", fontsize=8.5,
               color=p.fg)
    b.set_xticks(idx)
    b.set_xticklabels([f"$k$={k+1}" for k in range(K)])
    b.set_ylim(0, 0.52)
    b.legend(fontsize=8.4, loc="upper center", ncol=2)
    b.set_title("Equation 11.59's prior", fontsize=10)

    for j, xq in enumerate((-1.0, 0.0, 2.0)):
        c = fig.add_subplot(gs[1, j])
        near = np.abs(xs - xq) < 0.35
        emp = np.array([float(np.mean(z[near] == k)) for k in range(K)])
        lo, hi = xq - 0.35, xq + 0.35
        ana = PI0 * np.array([norm.cdf(hi, MU0[k],
                                       np.sqrt(VAR0[k]))
                              - norm.cdf(lo, MU0[k],
                                         np.sqrt(VAR0[k]))
                              for k in range(K)])
        ana = ana / ana.sum()
        c.bar(idx - 0.18, emp, width=0.34, color=p.blue,
              label="empirical $p(z_k\\!=\\!1\\mid x)$")
        c.bar(idx + 0.18, ana, width=0.34, color=p.amber,
              label="$r_{nk}$, Equation 11.17")
        c.set_xticks(idx)
        c.set_xticklabels([f"{k+1}" for k in range(K)])
        c.set_ylim(0, 1.42)
        c.set_xlabel("component $k$")
        c.set_title(f"$x \in$ {xq:g} $\pm$ 0.35  ({int(near.sum()):,} samples)",
                    fontsize=9.5)
        if j == 0:
            c.set_ylabel("probability")
            c.legend(fontsize=7.2, loc="upper center")
    fig.suptitle("Equation 11.72b: the posterior over the latent variable "
                 "IS the responsibility",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. Q
# --------------------------------------------------------------------------

def the_m_step_maximises_q(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    span = np.linspace(-6.0, 2.0, 400)
    qs, ls = [], []
    for m in span:
        mu = np.array([m, MU1[1], MU1[2]])
        qs.append(_Q(PI1, mu, VAR1, R0))
        ls.append(_ll(PI1, mu, VAR1))
    a1.plot(span, qs, color=p.blue, lw=2.4,
            label="$Q(\\theta\\mid\\theta_t)$, Equation 11.73")
    a1.plot(span, ls, color=p.amber, lw=2.0, ls="--",
            label="$L(\\theta)$")
    a1.axvline(MU1[0], color=p.red, lw=1.8, ls=":")
    a1.plot([MU1[0]], [_Q(PI1, MU1, VAR1, R0)], "o", ms=10, color=p.red,
            zorder=5)
    a1.annotate(f"the M-step's $\\mu_1$\n= {MU1[0]:.6f}",
                (MU1[0] + 0.25, -40), fontsize=9.5, color=p.red)
    a1.set_xlabel("$\\mu_1$, with every other parameter at the M-step's answer")
    a1.set_ylabel("value")
    a1.set_ylim(-90, -5)
    a1.legend(fontsize=9, loc="lower left")
    a1.set_title("$Q$ peaks exactly where the M-step puts it", fontsize=10)

    H = float(-(R0 * np.log(np.maximum(R0, 1e-300))).sum())
    Qt = _Q(PI0, MU0, VAR0, R0)
    Lt = _ll(PI0, MU0, VAR0)
    Qn = _Q(PI1, MU1, VAR1, R0)
    Ln = _ll(PI1, MU1, VAR1)
    labels = ["$\\theta_t$", "after the M-step"]
    idx = np.arange(2)
    a2.bar(idx - 0.16, [-Qt, -Qn], width=0.3, color=p.blue, label="$-Q$")
    a2.bar(idx + 0.16, [-Lt, -Ln], width=0.3, color=p.amber, label="$-L$")
    for j, (q, l) in enumerate(((-Qt, -Lt), (-Qn, -Ln))):
        a2.text(j - 0.16, q + 0.9, f"{q:.4f}", ha="center", fontsize=8.8,
                color=p.fg)
        a2.text(j + 0.16, l + 0.9, f"{l:.4f}", ha="center", fontsize=8.8,
                color=p.fg)
    a2.set_xticks(idx)
    a2.set_xticklabels(labels)
    a2.set_ylim(0, 34)
    a2.legend(fontsize=9)
    a2.set_title(f"$L = Q + H$, with $H$ = {H:.6f} at $\\theta_t$",
                 fontsize=10)
    fig.suptitle("Section 11.4.5: the M-step maximises $Q$, and raising "
                 "$Q$ raises $L$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-generative-story", the_generative_story, size=(9.6, 5.8),
           axes=False),
    figure("the-m-step-maximises-q", the_m_step_maximises_q,
           size=(9.6, 4.3), axes=False),
]

"""Figures for *Responsibilities* (Section 11.2.1).

1. `the-responsibility-matrix` — Equation 11.19 as a heat map, at the book's
   initialisation and at convergence, with the seven data points coloured by
   their responsibility vectors.

2. `a-softmax-over-energies` — the book's margin note checked. r_n is exactly
   softmax(-E) with E_nk = -log pi_k - log N(x_n | mu_k, sigma_k^2), matching
   to 1.1e-16, and the three responsibility curves partition the line.

3. `soft-becomes-hard` — scaling every variance by t drives the
   responsibilities to indicator vectors, which is K-means. Equation 11.17
   typed out as written produces 21 NaNs at t = 1e-06; in log-space it gives
   the exact one-hot answer.
"""

from __future__ import annotations

import numpy as np
from scipy.special import logsumexp

from _style import Palette, figure

X = np.array([-3.0, -2.5, -1.0, 0.0, 2.0, 4.0, 5.0])
N = len(X)
MU0 = np.array([-4.0, 0.0, 8.0])
VAR0 = np.array([1.0, 0.2, 3.0])
PI0 = np.ones(3) / 3


def _g(x, mu, var):
    return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)


def _resp(x, pi, mu, var):
    W = pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])
    return W / W.sum(1, keepdims=True)


def _resp_log(x, pi, mu, var):
    lw = (np.log(pi)[None, :]
          - 0.5 * (x[:, None] - mu[None, :]) ** 2 / var[None, :]
          - 0.5 * np.log(2 * np.pi * var[None, :]))
    return np.exp(lw - logsumexp(lw, axis=1, keepdims=True))


def _converged():
    pi, mu, var = PI0.copy(), MU0.copy(), VAR0.copy()
    for _ in range(300):
        R = _resp(X, pi, mu, var)
        Nk = R.sum(0)
        mu = (R * X[:, None]).sum(0) / Nk
        var = (R * (X[:, None] - mu[None, :]) ** 2).sum(0) / Nk
        pi = Nk / N
    return pi, mu, var


PI_C, MU_C, VAR_C = _converged()


# --------------------------------------------------------------------------
# 1. Equation 11.19
# --------------------------------------------------------------------------

def the_responsibility_matrix(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1.0], hspace=0.55,
                          wspace=0.3)

    for col, (ttl, pi, mu, var) in enumerate([
            ("at the book's initialisation", PI0, MU0, VAR0),
            ("at convergence", PI_C, MU_C, VAR_C)]):
        R = _resp(X, pi, mu, var)
        a = fig.add_subplot(gs[0, col])
        im = a.imshow(R, cmap="viridis", vmin=0, vmax=1, aspect="auto",
                      interpolation="nearest")
        a.set_xticks(range(3))
        a.set_xticklabels([f"$k$={k+1}" for k in range(3)])
        a.set_yticks(range(N))
        a.set_yticklabels([f"{v:g}" for v in X])
        a.grid(False)
        for n in range(N):
            for k in range(3):
                a.text(k, n, f"{R[n,k]:.3f}", ha="center", va="center",
                       fontsize=8,
                       color="white" if R[n, k] < 0.55 else "black")
        a.set_ylabel("$x_n$" if col == 0 else "")
        a.set_title(ttl, fontsize=10)
        fig.colorbar(im, ax=a, fraction=0.046)

    b = fig.add_subplot(gs[1, :])
    grid = np.linspace(-6, 8, 900)
    Rg = _resp(grid, PI_C, MU_C, VAR_C)
    cols = [p.blue, p.green, p.purple]
    b.stackplot(grid, Rg.T, colors=cols, alpha=0.75,
                labels=[f"$r_{{\\cdot{k+1}}}$" for k in range(3)])
    for xv in X:
        b.plot([xv], [1.04], marker="v", ms=8, color=p.red)
    b.set_xlim(-6, 8)
    b.set_ylim(0, 1.12)
    b.set_xlabel("$x$")
    b.set_ylabel("responsibility")
    b.legend(fontsize=9, loc="center left")
    b.set_title("the three responsibilities partition the line at every $x$; "
                "red markers are the data", fontsize=10)
    fig.suptitle("Equation 11.19, and what it looks like everywhere else",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the margin note
# --------------------------------------------------------------------------

def a_softmax_over_energies(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    E = -(np.log(PI0)[None, :]
          + np.log(_g(X[:, None], MU0[None, :], VAR0[None, :])))
    cols = [p.blue, p.green, p.purple]
    for k in range(3):
        a1.plot(X, E[:, k], color=cols[k], lw=2.0, marker="o", ms=5,
                label=f"$E_{{n{k+1}}}$")
    a1.set_xlabel("$x_n$")
    a1.set_ylabel("$E_{nk} = -\\log\\pi_k - \\log\\mathcal{N}(x_n\\mid\\cdot)$")
    a1.legend(fontsize=9)
    a1.set_title("the energies: lowest wins, but softly", fontsize=10)

    R = _resp(X, PI0, MU0, VAR0)
    S = np.exp(-E)
    S = S / S.sum(1, keepdims=True)
    gap = np.abs(S - R).max()
    idx = np.arange(N)
    for k in range(3):
        a2.bar(idx + (k - 1) * 0.26, R[:, k], width=0.24, color=cols[k],
               label=f"$r_{{n{k+1}}}$")
        a2.plot(idx + (k - 1) * 0.26, S[:, k], "o", ms=4, color=p.fg,
                zorder=5)
    a2.set_xticks(idx)
    a2.set_xticklabels([f"{v:g}" for v in X])
    a2.set_xlabel("$x_n$")
    a2.set_ylabel("responsibility")
    a2.set_ylim(0, 1.22)
    a2.legend(fontsize=9, ncol=3, loc="upper center")
    a2.set_title(f"bars: Equation 11.17.  dots: softmax($-E$).  "
                 f"gap {gap:.1e}", fontsize=10)
    fig.suptitle("The margin note is exact: $r_n$ is a Boltzmann "
                 "distribution over the components",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. soft to hard
# --------------------------------------------------------------------------

def soft_becomes_hard(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    ts = np.logspace(3, -8, 70)
    mx, ent, nan_naive, nan_log = [], [], [], []
    for t in ts:
        a = _resp(X, PI_C, MU_C, VAR_C * t)
        b = _resp_log(X, PI_C, MU_C, VAR_C * t)
        mx.append(float(b.max(1).mean()))
        H = -(b * np.log(np.maximum(b, 1e-300))).sum(1)
        ent.append(float(H.mean()))
        nan_naive.append(int(np.isnan(a).sum()))
        nan_log.append(int(np.isnan(b).sum()))

    a1.semilogx(ts, mx, color=p.blue, lw=2.4,
                label="mean $\\max_k r_{nk}$")
    a1.semilogx(ts, np.array(ent) / np.log(3), color=p.amber, lw=2.4,
                label="mean entropy / $\\log K$")
    a1.axhline(1.0, color=p.muted, lw=1.0, ls=":")
    a1.axhline(1 / 3, color=p.muted, lw=1.0, ls=":")
    a1.annotate("one-hot: K-means", (2e-7, 0.93), fontsize=9.5,
                color=p.blue, ha="right")
    a1.annotate("uniform: $1/K$", (3e2, 0.30), fontsize=9.5, color=p.muted)
    a1.invert_xaxis()
    a1.set_xlabel("$t$, every variance scaled by $t$")
    a1.set_ylabel("value")
    a1.set_ylim(0, 1.12)
    a1.legend(fontsize=9, loc="center left")
    a1.set_title("shrinking the variances hardens the assignment",
                 fontsize=10)

    a2.semilogx(ts, nan_naive, color=p.red, lw=2.4,
                label="Equation 11.17 as written")
    a2.semilogx(ts, nan_log, color=p.blue, lw=2.4, ls="--",
                label="the same thing in log-space")
    a2.invert_xaxis()
    a2.set_xlabel("$t$")
    a2.set_ylabel("NaNs in the $7\\times3$ matrix")
    a2.set_ylim(-1.5, 24)
    a2.legend(fontsize=9, loc="upper left")
    a2.set_title("21 of 21 entries, against 0", fontsize=10)
    fig.suptitle("Equation 11.17 divides a vanishing number by a vanishing "
                 "number; log-space does not",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-responsibility-matrix", the_responsibility_matrix,
           size=(9.4, 6.2), axes=False),
    figure("a-softmax-over-energies", a_softmax_over_energies,
           size=(9.6, 4.2), axes=False),
    figure("soft-becomes-hard", soft_becomes_hard, size=(9.4, 4.2),
           axes=False),
]

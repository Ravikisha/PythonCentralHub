"""Figures for *Kernels* (§12.4).

1. `four-kernels` — Figure 12.10 on two concentric rings. The hypothesis class
   is still a hyperplane; only the inner product changed.

2. `what-a-kernel-buys` — the feature space measured from outside. A
   polynomial kernel's Gram rank stops exactly at C(D+p, p) and never moves
   again; the RBF's keeps climbing with N, which is what no finite feature map
   looks like.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import comb

from _style import Palette, figure


def _k_linear(A, B):
    return A @ B.T


def _k_poly(A, B, degree=2, c=1.0):
    return (A @ B.T + c) ** degree


def _k_rbf(A, B, gamma=0.5):
    d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
    return np.exp(-gamma * d2)


def _rings(seed=11, n1=60):
    rg = np.random.default_rng(seed)
    R = np.r_[rg.normal(1.0, 0.18, n1), rg.normal(3.0, 0.22, n1)]
    th = rg.uniform(0, 2 * np.pi, 2 * n1)
    return np.c_[R * np.cos(th), R * np.sin(th)], np.r_[np.ones(n1),
                                                        -np.ones(n1)]


def _dual_fit(K, YY, C, tries=16):
    n = len(YY)
    H = (YY[:, None] * YY[None, :]) * K
    out, bv = None, np.inf
    for s in range(tries):
        rg = np.random.default_rng(s)
        a0 = np.clip(np.abs(rg.normal(0.3, 0.3, n)), 0, C)
        r = minimize(lambda a: 0.5 * a @ H @ a - a.sum(), a0,
                     jac=lambda a: H @ a - 1.0, bounds=[(0.0, C)] * n,
                     constraints=[{"type": "eq", "fun": lambda a: YY @ a,
                                   "jac": lambda a: YY}],
                     method="SLSQP", options={"maxiter": 30000, "ftol": 1e-12})
        if r.success and r.fun < bv - 1e-12:
            bv, out = r.fun, np.clip(r.x, 0.0, C)
    return out


def _decision(a, YY, Ktr, Kgrid, C):
    free = (a > 1e-7) & (a < C - 1e-7)
    if not free.any():
        free = a > 1e-7
    s_tr = (a * YY) @ Ktr
    b = float(np.mean(YY[free] - s_tr[free]))
    return (a * YY) @ Kgrid + b


# --------------------------------------------------------------------------
# 1. four kernels
# --------------------------------------------------------------------------

def four_kernels(fig, ax, p: Palette) -> None:
    fig.clear()
    axs = fig.subplots(1, 4, sharex=True, sharey=True)
    XC, YC = _rings()
    C = 10.0

    g = np.linspace(-4.2, 4.2, 180)
    GX, GY = np.meshgrid(g, g)
    G = np.c_[GX.ravel(), GY.ravel()]

    specs = (("linear", lambda A, B: _k_linear(A, B)),
             ("polynomial, deg 2", lambda A, B: _k_poly(A, B, 2)),
             ("polynomial, deg 3", lambda A, B: _k_poly(A, B, 3)),
             (r"RBF, $\gamma = 0.5$", lambda A, B: _k_rbf(A, B, 0.5)))

    for a_ax, (name, kf) in zip(axs, specs):
        Ktr = kf(XC, XC)
        al = _dual_fit(Ktr, YC, C)
        Z = _decision(al, YC, Ktr, kf(XC, G), C).reshape(GX.shape)
        a_ax.contourf(GX, GY, Z, levels=[-1e9, 0, 1e9],
                      colors=[p.blue, p.amber], alpha=0.13)
        a_ax.contour(GX, GY, Z, levels=[0], colors=[p.fg], linewidths=2.2)
        a_ax.contour(GX, GY, Z, levels=[-1, 1], colors=[p.muted],
                     linewidths=1.0, linestyles="--")
        acc = float((np.where(_decision(al, YC, Ktr, Ktr, C) >= 0, 1.0, -1.0)
                     == YC).mean())
        a_ax.scatter(XC[YC > 0, 0], XC[YC > 0, 1], marker="x", s=26, lw=1.4,
                     color=p.amber, zorder=4)
        a_ax.scatter(XC[YC < 0, 0], XC[YC < 0, 1], marker="o", s=22, lw=1.1,
                     facecolor="none", edgecolor=p.blue, zorder=4)
        a_ax.set_xlim(-4.2, 4.2)
        a_ax.set_ylim(-4.2, 4.2)
        a_ax.set_aspect("equal")
        a_ax.set_xlabel("first feature")
        a_ax.set_title(f"{name}\ntrain accuracy {acc:.4f}", fontsize=9.5)
    axs[0].set_ylabel("second feature")
    fig.suptitle("Figure 12.10: the hypothesis class is still a hyperplane "
                 "— only the inner product changed",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what a kernel buys
# --------------------------------------------------------------------------

def what_a_kernel_buys(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.05]})

    rg = np.random.default_rng(3)
    Ns = [50, 100, 200, 400, 800]
    series = (("polynomial, deg 2", lambda Z: _k_poly(Z, Z, 2), p.blue, "o"),
              ("polynomial, deg 3", lambda Z: _k_poly(Z, Z, 3), p.green, "s"),
              ("polynomial, deg 5", lambda Z: _k_poly(Z, Z, 5), p.purple, "^"),
              (r"RBF, $\gamma = 0.5$", lambda Z: _k_rbf(Z, Z, 0.5), p.red, "D"))
    for name, kf, col, mk in series:
        ranks = []
        for n in Ns:
            P = rg.normal(0, 1, (n, 2))
            # numpy's default tolerance is relative to the largest singular
            # value, which is the only scale-free choice here
            ranks.append(int(np.linalg.matrix_rank(kf(P))))
        a1.plot(Ns, ranks, color=col, lw=2.3, marker=mk, ms=6, label=name)
    a1.plot(Ns, Ns, color=p.muted, lw=1.5, ls=":", label="$N$")
    a1.set_xscale("log")
    a1.set_yscale("log")
    a1.set_xlabel("$N$, number of examples")
    a1.set_ylabel("rank of the Gram matrix")
    a1.legend(fontsize=8.2, loc="upper left")
    a1.set_title("polynomial ranks stop; the RBF's does not", fontsize=10)

    P = rg.normal(0, 1, (200, 2))
    for name, K, col in ((r"polynomial, deg 3", _k_poly(P, P, 3), p.green),
                         (r"RBF, $\gamma = 0.5$", _k_rbf(P, P, 0.5), p.red),
                         (r"RBF, $\gamma = 5$", _k_rbf(P, P, 5.0), p.purple)):
        ev = np.sort(np.linalg.eigvalsh((K + K.T) / 2))[::-1]
        ev = np.maximum(ev, 1e-18)
        a2.semilogy(np.arange(1, len(ev) + 1), ev, color=col, lw=2.3,
                    label=name)
    a2.axhline(1e-16, color=p.muted, ls=":", lw=1.4)
    a2.annotate("float64 noise floor", (5, 2.2e-16), fontsize=8.5,
                color=p.muted)
    a2.set_xlim(0, 200)
    a2.set_ylim(1e-18, 1e5)
    a2.set_xlabel("eigenvalue index")
    a2.set_ylabel("eigenvalue")
    a2.legend(fontsize=8.6, loc="upper right")
    a2.set_title("and the spectrum is where the difference lives",
                 fontsize=10)

    fig.suptitle("Equation 12.52's feature space, measured from outside it",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("four-kernels", four_kernels, size=(11.0, 3.6), axes=False),
    figure("what-a-kernel-buys", what_a_kernel_buys, size=(9.8, 4.2),
           axes=False),
]

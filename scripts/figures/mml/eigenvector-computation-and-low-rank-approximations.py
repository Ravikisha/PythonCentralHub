"""Figures for *Eigenvector Computation and Low-Rank Approximations* (10.4).

1. `svd-and-eigendecomposition` — Equation 10.49's lambda_d = sigma_d^2 / N
   measured to 1.4e-13, and Eckart-Young's spectral-norm error measured to be
   exactly sigma_(M+1), against the best of 400 random rank-M subspaces.

2. `squaring-costs-accuracy` — the relative error of the smallest eigenvalue
   against the condition number of X. Forming X X-transpose squares it:
   at cond 1e10, eigh's worst relative error is 5.3e+03 and 18 of 200
   eigenvalues come back negative, while the SVD route holds 3.2e-07.

3. `power-iteration` — Equation 10.52's convergence, measured. The angle to
   b_1 falls by lambda_2/lambda_1 per step: predicted 0.578708, observed
   0.578541 by step 25. A near-tie at the top costs 1,769 steps against 27.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]
_N, _D = _A8.shape
_X = (_A8 - _A8.mean(0)).T
_S = _X @ _X.T / _N
_W, _V = np.linalg.eigh(_S)
_LAM, _PC = _W[::-1], _V[:, ::-1]
_U, _SIG, _VT = np.linalg.svd(_X, full_matrices=False)


# --------------------------------------------------------------------------
# 1. two decompositions, one answer
# --------------------------------------------------------------------------

def svd_and_eigendecomposition(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    d = np.arange(1, 53)                       # the 52 nonzero ones
    a1.plot(d, _SIG[:52] ** 2 / _N, color=p.blue, lw=4.0, alpha=0.5,
            label="$\\sigma_d^2 / N$, from the SVD of $X$")
    a1.plot(d, _LAM[:52], color=p.amber, lw=1.6, ls="--",
            label="$\\lambda_d$, from the eigendecomposition of $S$")
    a1.set_yscale("log")
    a1.set_xlabel("index $d$")
    a1.set_ylabel("value")
    a1.legend(fontsize=9, loc="lower left")
    a1.set_title("Equation 10.49, measured to 1.4e-13", fontsize=10)

    Ms = [1, 2, 3, 5, 8, 10, 15, 20]
    ey, nxt, rnd = [], [], []
    rng = np.random.default_rng(3)
    for M in Ms:
        XM = _U[:, :M] @ np.diag(_SIG[:M]) @ _VT[:M]
        ey.append(float(np.linalg.norm(_X - XM, 2)))
        nxt.append(float(_SIG[M]))
        best = np.inf
        for _ in range(400):
            Q = np.linalg.qr(rng.standard_normal((_D, M)))[0]
            best = min(best, float(np.linalg.norm(_X - Q @ (Q.T @ _X), 2)))
        rnd.append(best)
    a2.plot(Ms, ey, color=p.blue, lw=4.0, alpha=0.5, marker="o",
            label="$\\|X - \\tilde{X}_M\\|_2$, truncated SVD")
    a2.plot(Ms, nxt, color=p.amber, lw=1.6, ls="--", marker="s", ms=4,
            label="$\\sigma_{M+1}$")
    a2.plot(Ms, rnd, color=p.red, lw=1.6, marker="^", ms=5,
            label="best of 400 random rank-$M$")
    a2.set_xlabel("$M$")
    a2.set_ylabel("spectral norm of the error")
    a2.legend(fontsize=9)
    a2.set_title("Eckart-Young: the error is the next singular value",
                 fontsize=10)
    fig.suptitle("The SVD of X and the eigendecomposition of S are the "
                 "same computation",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what forming X X^T costs
# --------------------------------------------------------------------------

def squaring_costs_accuracy(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    rng = np.random.default_rng(0)
    n = 200
    Q1 = np.linalg.qr(rng.standard_normal((n, n)))[0]
    Q2 = np.linalg.qr(rng.standard_normal((n, n)))[0]

    expos = np.arange(1, 11)
    e_eig, e_svd, negs = [], [], []
    for e in expos:
        s = np.logspace(0, -float(e), n)
        A = Q1 @ np.diag(s) @ Q2.T
        tru = s ** 2
        le = np.linalg.eigvalsh(A @ A.T)[::-1]
        ls = np.linalg.svd(A, compute_uv=False) ** 2
        e_eig.append(float((np.abs(le - tru) / tru).max()))
        e_svd.append(float((np.abs(ls - tru) / tru).max()))
        negs.append(int((le < 0).sum()))

    k = 10.0 ** expos
    a1.loglog(k, e_eig, color=p.red, lw=2.2, marker="o",
              label="eigenvalues of $XX^\\top$")
    a1.loglog(k, e_svd, color=p.blue, lw=2.2, marker="s",
              label="squared singular values of $X$")
    a1.loglog(k, 2.2e-16 * k, color=p.blue, lw=1.1, ls=":",
              label="$\\epsilon\\,\\kappa$")
    a1.loglog(k, 2.2e-16 * k ** 2, color=p.red, lw=1.1, ls=":",
              label="$\\epsilon\\,\\kappa^2$")
    a1.axhline(1.0, color=p.fg, lw=1.2, ls="--")
    a1.annotate("100% relative error", (1.5e1, 3.0), fontsize=9, color=p.fg)
    a1.set_xlabel("$\\kappa(X)$")
    a1.set_ylabel("worst relative error over the spectrum")
    a1.legend(fontsize=8.6, loc="lower right")
    a1.set_title("the damage is at the bottom of the spectrum",
                 fontsize=10)

    a2.bar([f"$10^{{{e}}}$" for e in expos], negs, color=p.red, width=0.6)
    a2.set_xlabel("$\\kappa(X)$")
    a2.set_ylabel("eigenvalues returned negative")
    a2.set_title("of 200, from eigh($XX^\\top$); the SVD route gives 0",
                 fontsize=10)
    fig.suptitle("Forming $XX^\\top$ squares the condition number, and "
                 "Equation 10.44 sums the small end",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. Equation 10.52
# --------------------------------------------------------------------------

def power_iteration(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1.0]})

    u = np.random.default_rng(1).standard_normal(_D)
    u /= np.linalg.norm(u)
    angs = []
    for _ in range(40):
        u = _S @ u
        u /= np.linalg.norm(u)
        angs.append(np.degrees(np.arccos(min(1.0, abs(u @ _PC[:, 0])))))
    angs = np.array(angs)
    ok = angs > 0
    ks = np.arange(1, 41)
    ratio = _LAM[1] / _LAM[0]

    a1.semilogy(ks[ok], angs[ok], color=p.blue, lw=2.2, marker="o", ms=4,
                label="measured angle to $b_1$")
    a1.semilogy(ks, angs[0] * ratio ** (ks - 1), color=p.amber, lw=1.5,
                ls="--",
                label=f"$(\\lambda_2/\\lambda_1)^k$ = ${ratio:.6f}^k$")
    a1.axvline(int(np.argmax(~ok)) + 1, color=p.green, ls=":", lw=1.4)
    a1.annotate("exactly 0 from\nstep 40", (30.5, 1e-8), fontsize=9,
                color=p.green)
    a1.set_xlabel("iteration $k$")
    a1.set_ylabel("angle to $b_1$, degrees")
    a1.legend(fontsize=9)
    a1.set_title("Equation 10.52 on the digit-'8' covariance", fontsize=10)

    gaps = [0.99, 0.9, 0.7, 0.5, 0.3]
    steps = []
    for g in gaps:
        d = np.array([1.0, g] + list(np.linspace(0.4, 0.01, _D - 2)))
        Sg = _PC @ np.diag(d) @ _PC.T
        v = np.random.default_rng(2).standard_normal(_D)
        v /= np.linalg.norm(v)
        k = 0
        while k < 20000:
            v = Sg @ v
            v /= np.linalg.norm(v)
            k += 1
            if np.degrees(np.arccos(min(1.0, abs(v @ _PC[:, 0])))) < 1e-6:
                break
        steps.append(k)
    bars = a2.bar([f"{g:.2f}" for g in gaps], steps, color=p.blue, width=0.6)
    for bar, v in zip(bars, steps):
        a2.text(bar.get_x() + bar.get_width() / 2, v * 1.15, str(v),
                ha="center", fontsize=9, color=p.fg)
    a2.set_yscale("log")
    a2.set_ylim(10, 6000)
    a2.set_xlabel("$\\lambda_2 / \\lambda_1$")
    a2.set_ylabel("steps to reach $10^{-6}$ degrees")
    a2.set_title("a near-tie at the top is what makes it slow",
                 fontsize=10)
    fig.suptitle("Power iteration converges at exactly the rate the "
                 "spectrum dictates",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("svd-and-eigendecomposition", svd_and_eigendecomposition,
           size=(9.4, 4.3), axes=False),
    figure("squaring-costs-accuracy", squaring_costs_accuracy,
           size=(9.6, 4.4), axes=False),
    figure("power-iteration", power_iteration, size=(9.4, 4.3), axes=False),
]

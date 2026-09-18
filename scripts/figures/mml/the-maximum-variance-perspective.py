"""Figures for *The Maximum Variance Perspective* (Section 10.2).

1. `variance-around-the-circle` — Equation 10.10 as a one-dimensional search.
   b(theta)' S b(theta) traced over every unit vector in the plane; the maximum
   sits exactly at the leading eigenvector and equals lambda_1, the minimum at
   the other eigenvector and equals lambda_2.

2. `the-spectrum` — Example 10.2's Figure 10.5 on 174 images of the digit "8".
   Eigenvalues in descending order and the cumulative captured variance, with
   the measured crossings: 50% at M = 5, 90% at M = 18, 99% at M = 36. Twelve
   eigenvalues fall below 1e-10, one per dead border pixel.

3. `deflation-moves-the-spectrum` — Equation 10.17 applied 0, 1, 2 and 3 times.
   Each deflation sends one eigenvalue to machine zero (measured, S-hat b_i
   has norm 1.0e-14) and leaves every other one untouched to 7.8e-14. That is
   Equation 10.21, and it is why one eigendecomposition suffices.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]
_N, _D = _A8.shape
_X = (_A8 - _A8.mean(0)).T                 # D x N
_S = _X @ _X.T / _N
_W, _V = np.linalg.eigh(_S)
_LAM = _W[::-1]
_PC = _V[:, ::-1]
_TOT = _LAM.sum()


# --------------------------------------------------------------------------
# 1. Equation 10.10 is a search over a circle
# --------------------------------------------------------------------------

def variance_around_the_circle(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1.0], hspace=0.45,
                          wspace=0.3)

    rng = np.random.default_rng(3)
    t = rng.normal(0, 2.0, 220)
    P2 = np.c_[t, 0.55 * t + rng.normal(0, 0.9, 220)]
    P2 -= P2.mean(0)
    S2 = P2.T @ P2 / len(P2)
    w2, V2 = np.linalg.eigh(S2)
    lam1, lam2 = w2[1], w2[0]
    b1 = V2[:, 1] * np.sign(V2[0, 1])

    th = np.linspace(0, np.pi, 400)
    bb = np.c_[np.cos(th), np.sin(th)]
    var = np.einsum("ij,jk,ik->i", bb, S2, bb)
    th1 = np.arctan2(b1[1], b1[0]) % np.pi

    a = fig.add_subplot(gs[0, :2])
    a.plot(np.degrees(th), var, color=p.blue, lw=2.2)
    a.axhline(lam1, color=p.amber, ls="--", lw=1.4)
    a.axhline(lam2, color=p.green, ls="--", lw=1.4)
    a.axvline(np.degrees(th1), color=p.amber, ls=":", lw=1.4)
    a.annotate(f"$\\lambda_1$ = {lam1:.4f}", (4, lam1 + 0.13), fontsize=9.5,
               color=p.amber)
    a.annotate(f"$\\lambda_2$ = {lam2:.4f}", (4, lam2 + 0.13), fontsize=9.5,
               color=p.green)
    a.set_xlabel("direction of $b$, degrees")
    a.set_ylabel("$b^\\top S\\, b$")
    a.set_xlim(0, 180)
    a.set_title("Equation 10.10, evaluated at every unit vector",
                fontsize=10)

    # three sampled directions, drawn on the cloud
    picks = [(0.0, p.purple), (np.degrees(th1), p.amber), (140.0, p.red)]
    b = fig.add_subplot(gs[0, 2])
    b.scatter(P2[:, 0], P2[:, 1], s=9, color=p.muted, alpha=0.55)
    for deg, col in picks:
        d = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
        b.plot([-6 * d[0], 6 * d[0]], [-6 * d[1], 6 * d[1]], color=col,
               lw=1.9)
        a.scatter([deg], [d @ S2 @ d], s=55, color=col, zorder=6)
    b.set_xlim(-7, 7)
    b.set_ylim(-7, 7)
    b.set_aspect("equal")
    b.set_xlabel("$x_1$")
    b.set_title("three of those directions", fontsize=10)

    # the projected coordinates at each of the three
    for k, (deg, col) in enumerate(picks):
        c = fig.add_subplot(gs[1, k])
        d = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
        z = P2 @ d
        c.hist(z, bins=26, color=col, alpha=0.85)
        c.set_xlim(-8, 8)
        c.set_xlabel("$z = b^\\top x$")
        c.set_title(f"{deg:.0f}$^\\circ$: variance {z.var():.4f}",
                    fontsize=9.5)
        if k == 0:
            c.set_ylabel("count")

    fig.suptitle("The variance kept is a function of the direction, "
                 "and it peaks at an eigenvector",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. Figure 10.5 rebuilt
# --------------------------------------------------------------------------

def the_spectrum(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    idx = np.arange(1, _D + 1)
    a1.plot(idx, np.maximum(_LAM, 1e-16), color=p.blue, lw=1.8,
            marker="o", ms=3)
    a1.set_yscale("log")
    a1.set_xlabel("index $m$")
    a1.set_ylabel("$\\lambda_m$")
    a1.set_title("eigenvalues of S, descending (log scale)", fontsize=10)
    a1.axvline(52.5, color=p.red, ls="--", lw=1.3)
    a1.annotate("12 fall to machine zero\n(the dead border pixels)", (53.5, 1e-8),
                fontsize=9, color=p.red)
    a1.annotate(f"$\\lambda_1$ = {_LAM[0]:.2f}", (2.5, _LAM[0] * 0.55),
                fontsize=9.5, color=p.fg)

    cum = np.cumsum(_LAM) / _TOT
    a2.plot(idx, 100 * cum, color=p.blue, lw=2.2)
    for q, col in ((0.5, p.green), (0.9, p.amber), (0.99, p.red)):
        M = int(np.searchsorted(cum, q) + 1)
        a2.axhline(100 * q, color=col, ls=":", lw=1.2)
        a2.plot([M], [100 * cum[M - 1]], "o", ms=7, color=col)
        a2.annotate(f"{q:.0%} at M = {M}", (M + 1.5, 100 * q - 5.0),
                    fontsize=9.5, color=col)
    a2.set_xlabel("number of principal components $M$")
    a2.set_ylabel("captured variance, %")
    a2.set_ylim(0, 104)
    a2.set_title("Equation 10.24 as a share of the total, 741.158872",
                 fontsize=10)
    fig.suptitle("Example 10.2 on 174 images of the digit '8'",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. Equation 10.17 and what it does to the spectrum
# --------------------------------------------------------------------------

def deflation_moves_the_spectrum(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.35, 1.0]})

    cols = [p.blue, p.amber, p.green, p.purple]
    K = 10
    for m in range(4):
        B = _PC[:, :m] if m else np.zeros((_D, 0))
        Xh = _X - B @ B.T @ _X
        wh = np.linalg.eigvalsh(Xh @ Xh.T / _N)[::-1]
        a1.plot(np.arange(1, K + 1), wh[:K], color=cols[m], lw=1.9,
                marker="o", ms=5,
                label=f"after removing {m} component" + ("s" if m != 1 else ""))
    a1.set_xlabel("index, within the deflated spectrum")
    a1.set_ylabel("eigenvalue")
    a1.set_xticks(range(1, K + 1))
    a1.legend(fontsize=8.6)
    a1.set_title("each deflation drops one value and slides the rest left",
                 fontsize=10)

    # the used-up directions, and what S-hat does to them
    B3 = _PC[:, :3]
    Sh = (_X - B3 @ B3.T @ _X) @ (_X - B3 @ B3.T @ _X).T / _N
    norms = [float(np.linalg.norm(Sh @ _PC[:, i])) for i in range(6)]
    bars = a2.bar([f"$b_{{{i+1}}}$" for i in range(6)],
                  np.maximum(norms, 1e-16),
                  color=[p.red] * 3 + [p.blue] * 3, width=0.6)
    a2.set_yscale("log")
    a2.set_ylabel("$\\|\\hat{S}\\, b_i\\|$")
    a2.set_ylim(1e-16, 1e4)
    for bar, v in zip(bars, norms):
        a2.text(bar.get_x() + bar.get_width() / 2, v * 2.2,
                f"{v:.1e}", ha="center", fontsize=8, color=p.fg)
    a2.set_title("Equation 10.22: the first three are now null vectors",
                 fontsize=10)
    fig.suptitle("Equation 10.17's deflation is a proof device, "
                 "not an algorithm",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("variance-around-the-circle", variance_around_the_circle,
           size=(9.6, 6.0), axes=False),
    figure("the-spectrum", the_spectrum, size=(9.4, 4.3), axes=False),
    figure("deflation-moves-the-spectrum", deflation_moves_the_spectrum,
           size=(9.4, 4.3), axes=False),
]

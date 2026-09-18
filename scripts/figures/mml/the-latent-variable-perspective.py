"""Figures for *The Latent Variable Perspective* (Section 10.7).

1. `the-generative-process` — Example 10.5 rebuilt. A grid of latent vectors
   decoded into images, over the training codes. Measured, querying 2 standard
   deviations out puts 6.2 percent of pixels outside the valid range, 4 out
   puts 28.1 percent and 8 out puts 48.4 percent.

2. `the-posterior-ignores-the-data` — Equation 10.75's C is diagonal with
   entries sigma^2 / lambda_m, measured to 9.7e-16 against the Woodbury form,
   and changes by exactly 0 across 200 different observations.

3. `ppca-shrinks` — the posterior mean's reconstruction is the PCA projection
   scaled by (lambda_m - sigma^2)/lambda_m per axis, measured to the sixth
   decimal at four noise levels, and converging to PCA as sigma goes to 0.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]
_N, _D = _A8.shape
_MU = _A8.mean(0)
_X = (_A8 - _MU).T
_S = _X @ _X.T / _N
_W, _V = np.linalg.eigh(_S)
_LAM, _PC = _W[::-1], _V[:, ::-1]


# --------------------------------------------------------------------------
# 1. Example 10.5
# --------------------------------------------------------------------------

def the_generative_process(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(3, 5, height_ratios=[1.35, 1.0, 0.40], hspace=0.5,
                          wspace=0.3)

    Z = _PC[:, :2].T @ _X
    sdz = Z.std(1)
    a = fig.add_subplot(gs[0, :3])
    a.scatter(Z[0], Z[1], s=12, color=p.blue, alpha=0.55,
              label="training codes")
    picks = [(-2, -2), (-2, 2), (0, 0), (2, -2), (2, 2)]
    for k, (u, v) in enumerate(picks):
        a.scatter([u * sdz[0]], [v * sdz[1]], s=90, marker="X", color=p.amber,
                  zorder=6)
        a.annotate(str(k + 1), (u * sdz[0], v * sdz[1]),
                   textcoords="offset points", xytext=(7, 5), fontsize=10,
                   color=p.amber)
    for r, col in ((1, p.green), (2, p.amber), (4, p.red)):
        th = np.linspace(0, 2 * np.pi, 200)
        a.plot(r * sdz[0] * np.cos(th), r * sdz[1] * np.sin(th), color=col,
               lw=1.2, ls="--")
    a.set_xlabel("$z_1$")
    a.set_ylabel("$z_2$")
    a.legend(fontsize=9, loc="lower left")
    a.set_title("the latent space, with 1, 2 and 4 sd rings", fontsize=10)

    b = fig.add_subplot(gs[0, 3:])
    outs = []
    rs = [0, 1, 2, 4, 8]
    for r in rs:
        zq = np.array([r * sdz[0], 0.0])
        xq = _PC[:, :2] @ zq + _MU
        outs.append(100 * float(((xq < -0.5) | (xq > 16.5)).mean()))
    b.plot(rs, outs, color=p.red, lw=2.2, marker="o")
    for r, o in zip(rs, outs):
        b.annotate(f"{o:.1f}%", (r, o + 2.5), fontsize=9, color=p.fg,
                   ha="center")
    b.set_xlabel("standard deviations from the mean code")
    b.set_ylabel("% of pixels out of range")
    b.set_ylim(-4, 60)
    b.set_title("querying away from the data", fontsize=10)

    for k, (u, v) in enumerate(picks):
        c = fig.add_subplot(gs[1, k])
        zq = np.array([u * sdz[0], v * sdz[1]])
        xq = _PC[:, :2] @ zq + _MU
        c.imshow(np.clip(xq, 0, 16).reshape(8, 8), cmap="gray", vmin=0,
                 vmax=16, interpolation="nearest")
        c.set_xticks([])
        c.set_yticks([])
        c.grid(False)
        for s in c.spines.values():
            s.set_visible(True)
            s.set_color(p.amber)
        c.set_title(f"{k+1}: $z$ = ({u}, {v}) sd", fontsize=9)

    d = fig.add_subplot(gs[2, :])
    d.axis("off")
    d.text(0.5, 0.55,
           "Equation 10.65: $z_n \\sim \\mathcal{N}(0, I)$     "
           "$\\longrightarrow$     "
           "Equation 10.66: $x_n \\mid z_n \\sim "
           "\\mathcal{N}(Bz_n + \\mu,\\ \\sigma^2 I)$",
           ha="center", va="center", fontsize=12, color=p.fg,
           transform=d.transAxes)
    fig.suptitle("Example 10.5: the code is a place you can go, not just a "
                 "summary",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. Equation 10.75
# --------------------------------------------------------------------------

def the_posterior_ignores_the_data(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    M, sig2 = 5, 4.0
    B = _PC[:, :M] * np.sqrt(np.maximum(_LAM[:M] - sig2, 0.0))
    Cinv = np.linalg.inv(B @ B.T + sig2 * np.eye(_D))
    C = np.eye(M) - B.T @ Cinv @ B

    idx = np.arange(M)
    a1.bar(idx - 0.18, np.diag(C), width=0.36, color=p.blue,
           label="measured diag($C$)")
    a1.bar(idx + 0.18, sig2 / _LAM[:M], width=0.36, color=p.amber,
           label="$\\sigma^2/\\lambda_m$")
    for k in range(M):
        a1.text(k, np.diag(C)[k] + 0.004, f"{np.diag(C)[k]:.6f}",
                ha="center", fontsize=8.2, color=p.fg)
    off = float(np.abs(C - np.diag(np.diag(C))).max())
    a1.set_xticks(idx)
    a1.set_xticklabels([f"$m$={k+1}" for k in range(M)])
    a1.set_ylim(0, max(np.diag(C)) * 1.35)
    a1.set_ylabel("posterior variance")
    a1.legend(fontsize=9)
    a1.set_title(f"$C$ is diagonal (largest off-diagonal {off:.1e})",
                 fontsize=10)

    rs = np.random.default_rng(1)
    ms, cs = [], []
    for _ in range(200):
        xq = _A8[rs.integers(_N)] - _MU
        ms.append(float(np.linalg.norm(B.T @ Cinv @ xq)))
        C2 = np.eye(M) - B.T @ Cinv @ B
        cs.append(float(np.abs(C2 - C).max()))
    a2.plot(ms, color=p.blue, lw=1.2, label="$\\|m\\|$, Equation 10.74")
    a2.plot(np.maximum(cs, 1e-18), color=p.red, lw=2.0,
            label="$\\max|C - C_0|$, Equation 10.75")
    a2.set_yscale("symlog", linthresh=1e-17)
    a2.set_yticks([0, 1e-16, 1e-12, 1e-8, 1e-4, 1e0])
    a2.set_xlabel("observation index")
    a2.set_ylabel("value")
    a2.legend(fontsize=9)
    a2.set_title("over 200 observations: $m$ moves, $C$ does not",
                 fontsize=10)
    fig.suptitle("The posterior covariance does not depend on what you "
                 "observed",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the shrinkage
# --------------------------------------------------------------------------

def ppca_shrinks(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    M = 5
    x0 = _A8[0] - _MU
    z_pca = _PC[:, :M].T @ x0

    s2s = np.logspace(-3, np.log10(_LAM[M - 1] * 0.98), 60)
    for m in range(M):
        meas = []
        for s2 in s2s:
            B = _PC[:, :M] * np.sqrt(np.maximum(_LAM[:M] - s2, 1e-300))
            Ci = np.linalg.inv(B @ B.T + s2 * np.eye(_D))
            z_eq = _PC[:, :M].T @ (B @ (B.T @ Ci @ x0))
            meas.append(z_eq[m] / z_pca[m])
        a1.semilogx(s2s, meas, lw=2.0, label=f"axis {m+1}")
    a1.semilogx(s2s, [1.0] * len(s2s), color=p.fg, lw=1.0, ls=":")
    a1.annotate("PCA", (1.5e-3, 1.006), fontsize=9.5, color=p.fg)
    a1.set_xlabel("$\\sigma^2$")
    a1.set_ylabel("reconstruction / PCA projection")
    a1.set_ylim(0, 1.09)
    a1.legend(fontsize=8.6, loc="lower left")
    a1.set_title("PPCA shrinks each axis by "
                 "$(\\lambda_m - \\sigma^2)/\\lambda_m$", fontsize=10)

    rows = [1.0, 4.0, 16.0, 40.0]
    width = 0.18
    for k, s2 in enumerate(rows):
        B = _PC[:, :M] * np.sqrt(np.maximum(_LAM[:M] - s2, 0.0))
        Ci = np.linalg.inv(B @ B.T + s2 * np.eye(_D))
        z_eq = _PC[:, :M].T @ (B @ (B.T @ Ci @ x0))
        meas = np.array([z_eq[m] / z_pca[m] for m in range(M)])
        pred = (_LAM[:M] - s2) / _LAM[:M]
        a2.bar(np.arange(M) + (k - 1.5) * width, meas, width=width,
               label=f"$\\sigma^2$ = {s2:.0f}")
        a2.plot(np.arange(M) + (k - 1.5) * width, pred, "o", ms=4,
                color=p.fg, zorder=5)
    a2.set_xticks(range(M))
    a2.set_xticklabels([f"$m$={k+1}" for k in range(M)])
    a2.set_ylabel("shrinkage factor")
    a2.set_ylim(0, 1.15)
    a2.legend(fontsize=8.4, ncol=2)
    a2.set_title("dots are the predicted factor, bars the measured one",
                 fontsize=10)
    fig.suptitle("PPCA's reconstruction is PCA's, pulled towards the mean",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-generative-process", the_generative_process, size=(9.6, 6.6),
           axes=False),
    figure("the-posterior-ignores-the-data", the_posterior_ignores_the_data,
           size=(9.4, 4.3), axes=False),
    figure("ppca-shrinks", ppca_shrinks, size=(9.4, 4.3), axes=False),
]

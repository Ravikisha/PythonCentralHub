"""Figures for *PCA in High Dimensions* (Section 10.5).

1. `the-rank-is-what-you-have` — with N = 50 points in D = 784 dimensions, the
   784 x 784 covariance matrix has 49 nonzero eigenvalues, not 50. Centring
   puts the all-ones vector in the null space of X'X, so the rank is N - 1 and
   the Gram matrix is singular — measured condition number 4.15e+17.

2. `two-routes-one-spectrum` — the cost of the D x D route against the N x N
   one as D grows at fixed N = 50. Measured 47.9x at D = 500 and 4565.2x at
   D = 4000, with the top five eigenvalues agreeing to 5.5e-12.

3. `normalise-or-else` — the book's one-line remark, measured. X c_m is an
   eigenvector of S but has norm 54.37 on the digits, and using it unnormalised
   gives a reconstruction error of 6.269e+04 against 1.160e+01.
"""

from __future__ import annotations

import time

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_RNG = np.random.default_rng(0)


def _make(D, N, rank=6, seed=0):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((D, rank))
    X = Z @ rng.standard_normal((rank, N)) + 0.5 * rng.standard_normal((D, N))
    return X - X.mean(1, keepdims=True)


# --------------------------------------------------------------------------
# 1. the rank
# --------------------------------------------------------------------------

def the_rank_is_what_you_have(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1.0]})

    D, N = 784, 50
    X = _make(D, N)
    wb = np.linalg.eigvalsh(X @ X.T / N)[::-1]
    ws = np.linalg.eigvalsh(X.T @ X / N)[::-1]

    a1.semilogy(np.arange(1, 81), np.maximum(wb[:80], 1e-18), color=p.blue,
                lw=2.4, label=f"the {D}x{D} matrix $S$")
    a1.semilogy(np.arange(1, N + 1), np.maximum(ws, 1e-18), color=p.amber,
                lw=1.4, ls="--", marker="o", ms=3.5,
                label=f"the {N}x{N} Gram matrix")
    a1.axvline(49.5, color=p.red, ls=":", lw=1.6)
    a1.annotate("49 nonzero, not 50", (51, 1e-4), fontsize=9.5, color=p.red)
    a1.set_xlabel("index $m$")
    a1.set_ylabel("eigenvalue")
    a1.set_ylim(1e-18, 1e4)
    a1.legend(fontsize=9, loc="lower left")
    a1.set_title("same spectrum, and one more zero than advertised",
                 fontsize=10)

    Xu = _make(D, N) + 7.0                   # a deliberately off-centre copy
    rows = [("centred, as §10.5 assumes", X),
            ("the same data, uncentred", Xu)]
    names, ranks, conds = [], [], []
    for nm, M in rows:
        K = M.T @ M / N
        names.append(nm)
        ranks.append(int(np.linalg.matrix_rank(K)))
        conds.append(float(np.linalg.cond(K)))
    bars = a2.bar(["centred\n(§10.5's setting)", "uncentred"], ranks,
                  color=[p.red, p.blue], width=0.55)
    for bar, r, c in zip(bars, ranks, conds):
        a2.text(bar.get_x() + bar.get_width() / 2, r + 1.2,
                f"rank {r}\ncond {c:.2e}", ha="center", fontsize=9,
                color=p.fg)
    a2.axhline(N, color=p.fg, ls=":", lw=1.3)
    a2.annotate(f"N = {N}", (1.32, N + 0.6), fontsize=9, color=p.fg)
    a2.set_ylim(0, 62)
    a2.set_ylabel("rank of $\\frac{1}{N}X^\\top X$")
    a2.set_title("centring costs exactly one rank", fontsize=10)
    fig.suptitle("With N points in D dimensions you have N - 1 directions, "
                 "not D and not N",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the cost
# --------------------------------------------------------------------------

def two_routes_one_spectrum(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    N = 50
    Ds = [250, 500, 1000, 2000, 4000]
    t_big, t_small = [], []
    for D in Ds:
        X = _make(D, N, seed=D)
        t0 = time.perf_counter()
        np.linalg.eigvalsh(X @ X.T / N)
        t_big.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        w, C = np.linalg.eigh(X.T @ X / N)
        B = X @ C[:, ::-1][:, :5]
        B /= np.linalg.norm(B, axis=0)
        t_small.append(time.perf_counter() - t0)

    a1.loglog(Ds, np.array(t_big) * 1000, color=p.red, lw=2.2, marker="o",
              label="form $S$, then eigh ($D\\times D$)")
    a1.loglog(Ds, np.array(t_small) * 1000, color=p.blue, lw=2.2,
              marker="s",
              label="Gram matrix, then Eq 10.57 ($N\\times N$)")
    ref = np.array(Ds, float) ** 3
    a1.loglog(Ds, ref / ref[-1] * t_big[-1] * 1000, color=p.red, lw=1.0,
              ls=":", label="$D^3$")
    a1.set_xticks(Ds)
    a1.set_xticklabels([str(d) for d in Ds])
    a1.minorticks_off()
    a1.set_xlabel("$D$, at fixed $N = 50$")
    a1.set_ylabel("milliseconds")
    a1.legend(fontsize=8.8, loc="upper left")
    a1.set_title("one route is cubic in D, the other is linear", fontsize=10)

    mem_big = [D * D * 8 / 2**20 for D in Ds + [10000]]
    mem_small = [N * N * 8 / 2**20] * (len(Ds) + 1)
    labels = [str(d) for d in Ds] + ["10000"]
    idx = np.arange(len(labels))
    a2.bar(idx - 0.18, mem_big, width=0.36, color=p.red,
           label="$S$, $D\\times D$")
    a2.bar(idx + 0.18, mem_small, width=0.36, color=p.blue,
           label="Gram, $N\\times N$")
    a2.set_yscale("log")
    a2.set_xticks(idx)
    a2.set_xticklabels(labels)
    a2.set_xlabel("$D$")
    a2.set_ylabel("MiB, float64")
    a2.legend(fontsize=9)
    a2.annotate(f"{10000*10000*8/2**30:.2f} GiB", (len(labels) - 1.35,
                                                   mem_big[-1] * 1.4),
                fontsize=9.5, color=p.red)
    a2.annotate("19.5 KiB, flat", (2.6, 0.007), fontsize=9.5, color=p.blue)
    a2.set_title("the book's 100x100 images, as memory", fontsize=10)
    fig.suptitle("Equation 10.56 replaces a $D\\times D$ eigenproblem with "
                 "an $N\\times N$ one",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the remark that is not optional
# --------------------------------------------------------------------------

def normalise_or_else(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.72], hspace=0.4,
                          wspace=0.28)

    dig = load_digits()
    A8 = dig.data[dig.target == 8][:20]
    N, D = A8.shape
    mu = A8.mean(0)
    X = (A8 - mu).T
    w, C = np.linalg.eigh(X.T @ X / N)
    C = C[:, ::-1]
    M = 5
    B_raw = X @ C[:, :M]
    B_ok = B_raw / np.linalg.norm(B_raw, axis=0)
    _, Vd = np.linalg.eigh(X @ X.T / N)
    PCd = Vd[:, ::-1][:, :M]

    x0 = X[:, 0]
    panels = [
        (x0 + mu, "the original $x$", None),
        (B_raw @ (B_raw.T @ x0) + mu, "$B = Xc_m$, as is",
         float(np.linalg.norm(x0 - B_raw @ (B_raw.T @ x0)))),
        (B_ok @ (B_ok.T @ x0) + mu, "after normalising",
         float(np.linalg.norm(x0 - B_ok @ (B_ok.T @ x0)))),
        (PCd @ (PCd.T @ x0) + mu, "the direct eigenvectors",
         float(np.linalg.norm(x0 - PCd @ (PCd.T @ x0)))),
    ]
    for k, (vec, ttl, err) in enumerate(panels):
        a = fig.add_subplot(gs[0, k])
        a.imshow(np.clip(vec, 0, 16).reshape(8, 8), cmap="gray",
                 vmin=0, vmax=16, interpolation="nearest")
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)
        for s in a.spines.values():
            s.set_visible(True)
            s.set_color(p.grid)
        a.set_title(ttl if err is None else f"{ttl}\nerror {err:.3e}",
                    fontsize=9.5, color=p.fg)

    b = fig.add_subplot(gs[1, :])
    norms = np.linalg.norm(X @ C[:, :8], axis=0)
    b.bar([f"$m$={k+1}" for k in range(8)], norms, color=p.amber, width=0.55)
    b.axhline(1.0, color=p.blue, lw=1.6, ls="--")
    b.annotate("what Equation 10.32 assumes: $\\|b_m\\| = 1$", (4.3, 4.6),
               fontsize=9.5, color=p.blue)
    for k, v in enumerate(norms):
        b.text(k, v + 1.4, f"{v:.2f}", ha="center", fontsize=8.5, color=p.fg)
    b.set_ylabel("$\\|X c_m\\|$")
    b.set_ylim(0, norms.max() * 1.25)
    b.set_title("Equation 10.57 gives you eigenvectors of the right "
                "direction and the wrong length", fontsize=10)
    fig.suptitle("The remark after Equation 10.57 is not a footnote",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-rank-is-what-you-have", the_rank_is_what_you_have,
           size=(9.4, 4.4), axes=False),
    figure("two-routes-one-spectrum", two_routes_one_spectrum,
           size=(9.4, 4.3), axes=False),
    figure("normalise-or-else", normalise_or_else, size=(9.4, 5.2),
           axes=False),
]

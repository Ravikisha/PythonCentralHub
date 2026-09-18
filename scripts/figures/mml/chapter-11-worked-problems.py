"""Figures for *Chapter 11 Worked Problems* (this module's own).

1. `choosing-k` — the contrast with page 1009. Training log-likelihood rises to
   K = 6 and stops only because EM stops; held-out log-likelihood peaks at the
   true K = 3, BIC picks 3 and AIC picks 4.

2. `floors-and-kernels` — the price a variance floor puts on page 1102's
   unbounded likelihood, which is exactly half the natural log of ten per
   decade, and the GMM against kernel density estimation: 8 stored numbers
   beating 600 stored points by 13.7 nats of held-out log-likelihood.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import gaussian_kde

from _style import Palette, figure

TRUE_PI = np.array([0.45, 0.30, 0.25])
TRUE_MU = np.array([-3.0, 0.5, 4.0])
TRUE_VAR = np.array([0.8, 0.5, 1.2])


def _g(x, mu, var):
    return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)


def _resp(x, pi, mu, var):
    W = pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])
    return W / W.sum(1, keepdims=True)


def _ll(x, pi, mu, var):
    W = pi[None, :] * _g(x[:, None], mu[None, :], var[None, :])
    return float(np.log(W.sum(1)).sum())


def _em(x, K, seed, floor=1e-6, iters=500):
    r = np.random.default_rng(seed)
    pi = r.dirichlet(np.ones(K))
    mu = r.choice(x, K, replace=False)
    var = np.full(K, float(x.var()))
    prev = _ll(x, pi, mu, var)
    for _ in range(iters):
        R = _resp(x, pi, mu, var)
        Nk = R.sum(0)
        if Nk.min() < 1e-12:
            break
        mu = (R * x[:, None]).sum(0) / Nk
        var = np.maximum((R * (x[:, None] - mu[None, :]) ** 2).sum(0) / Nk,
                         floor)
        pi = Nk / len(x)
        cur = _ll(x, pi, mu, var)
        if abs(cur - prev) < 1e-10 * max(1.0, abs(cur)):
            break
        prev = cur
    return pi, mu, var, _ll(x, pi, mu, var)


def _best(x, K, tries=12, seed0=0, floor=1e-6):
    best = None
    for t in range(tries):
        c = _em(x, K, seed0 + t, floor)
        if best is None or c[3] > best[3]:
            best = c
    return best


def _data():
    rng = np.random.default_rng(42)
    z1 = rng.choice(3, 600, p=TRUE_PI)
    tr = rng.normal(TRUE_MU[z1], np.sqrt(TRUE_VAR[z1]))
    z2 = rng.choice(3, 600, p=TRUE_PI)
    te = rng.normal(TRUE_MU[z2], np.sqrt(TRUE_VAR[z2]))
    return tr, te


# --------------------------------------------------------------------------
# 1. choosing K
# --------------------------------------------------------------------------

def choosing_k(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    tr, te = _data()
    n = len(tr)
    Ks = list(range(1, 9))
    Ltr, Lte, bic, aic = [], [], [], []
    for K in Ks:
        pi, mu, var, L = _best(tr, K)
        Ltr.append(L)
        Lte.append(_ll(te, pi, mu, var))
        q = 3 * K - 1
        bic.append(-2 * L + q * np.log(n))
        aic.append(-2 * L + 2 * q)

    a1.plot(Ks, Ltr, color=p.red, lw=2.4, marker="o",
            label="training $L$")
    a1.plot(Ks, Lte, color=p.blue, lw=2.4, marker="s",
            label="held-out $L$")
    kbest = Ks[int(np.argmax(Lte))]
    a1.axvline(3, color=p.amber, ls="--", lw=1.6)
    a1.annotate("the true $K$ = 3", (3.12, -1500), fontsize=9.5,
                color=p.amber)
    a1.plot([kbest], [max(Lte)], "o", ms=11, color=p.blue, zorder=5)
    a1.set_xlabel("$K$")
    a1.set_ylabel("log-likelihood")
    a1.legend(fontsize=9, loc="lower right")
    a1.set_title("training fit keeps climbing; held-out fit turns at 3",
                 fontsize=10)

    a2.plot(Ks, bic, color=p.purple, lw=2.4, marker="o", label="BIC")
    a2.plot(Ks, aic, color=p.green, lw=2.4, marker="s", label="AIC")
    kb, ka = Ks[int(np.argmin(bic))], Ks[int(np.argmin(aic))]
    a2.plot([kb], [min(bic)], "o", ms=11, color=p.purple, zorder=5)
    a2.plot([ka], [min(aic)], "s", ms=10, color=p.green, zorder=5)
    span = max(max(bic), max(aic)) - min(min(bic), min(aic))
    a2.set_ylim(min(min(bic), min(aic)) - 0.16 * span,
                max(max(bic), max(aic)) + 0.05 * span)
    a2.annotate(f"BIC: $K$ = {kb}", (kb + 0.15, min(bic) + 0.035 * span),
                fontsize=9.5, color=p.purple)
    a2.annotate(f"AIC: $K$ = {ka}", (ka + 0.15, min(aic) - 0.075 * span),
                fontsize=9.5, color=p.green)
    a2.axvline(3, color=p.amber, ls="--", lw=1.6)
    a2.set_xlabel("$K$")
    a2.set_ylabel("criterion (lower is better)")
    a2.legend(fontsize=9)
    a2.set_title("BIC's heavier penalty picks the true $K$", fontsize=10)
    fig.suptitle("Unlike page 1009's reconstruction error, a held-out "
                 "likelihood can choose $K$",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. floors and kernels
# --------------------------------------------------------------------------

def floors_and_kernels(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.05, 1.0]})

    tr, te = _data()

    # The singularity, analytically. A component that has collapsed onto one
    # of N points with weight 1/N contributes log(1/N) - 0.5*log(2*pi*v),
    # which diverges as v goes to zero. Equation 11.10 has no upper bound.
    n_small = 60
    v = np.logspace(-13, 0, 400)
    contrib = np.log(1.0 / n_small) - 0.5 * np.log(2 * np.pi * v)
    a1.semilogx(v, contrib, color=p.red, lw=2.6)
    lines = []
    for fl, lab in ((1e-12, "$10^{-12}$"), (1e-6, "$10^{-6}$"),
                    (1e-2, "$10^{-2}$")):
        cap = np.log(1.0 / n_small) - 0.5 * np.log(2 * np.pi * fl)
        a1.axvline(fl, color=p.muted, ls=":", lw=1.3)
        a1.plot([fl], [cap], "o", ms=8, color=p.blue, zorder=5)
        lines.append(f"floor {lab} caps it at {cap:+.1f}")
    a1.text(0.97, 0.95, "\n".join(lines), transform=a1.transAxes,
            ha="right", va="top", fontsize=9, color=p.blue, linespacing=1.6)
    a1.axhline(0, color=p.grid, lw=1.0)
    per_decade = 0.5 * np.log(10)
    a1.set_xlabel("variance of the collapsing component")
    a1.set_ylabel("its contribution to $L$, in nats")
    a1.set_title("a floor prices the singularity; it does not remove it\n"
                 f"(every decade is worth $\\frac{{1}}{{2}}\\ln 10$ = "
                 f"{per_decade:.4f} nats)",
                 fontsize=9.5)

    pi3, mu3, var3, _ = _best(tr, 3)
    rows = [("GMM, $K$ = 3", 8, _ll(te, pi3, mu3, var3))]
    for name, bw in (("KDE, Scott", None), ("KDE, $h$ = 0.2", 0.2),
                     ("KDE, $h$ = 0.5", 0.5), ("KDE, $h$ = 1.5", 1.5)):
        kde = gaussian_kde(tr, bw_method=bw)
        rows.append((name, len(tr), float(np.log(kde(te)).sum())))
    names = [r[0] for r in rows]
    vals = [r[2] for r in rows]
    cols = [p.blue] + [p.muted] * 4
    a2.barh(names[::-1], vals[::-1], color=cols[::-1], height=0.55)
    for j, v in enumerate(vals[::-1]):
        a2.text(v + 8, j, f"{v:.1f}", va="center", fontsize=9, color=p.fg)
    a2.set_xlim(-1750, -1250)
    a2.set_xlabel("held-out log-likelihood")
    a2.set_title("8 stored numbers against 600 stored points",
                 fontsize=10)
    fig.suptitle("Two practical questions Section 11.5 raises and does "
                 "not answer",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("choosing-k", choosing_k, size=(9.4, 4.3), axes=False),
    figure("floors-and-kernels", floors_and_kernels, size=(9.6, 4.3),
           axes=False),
]

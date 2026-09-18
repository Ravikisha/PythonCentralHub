"""Figures for *Updating the Means* (Section 11.2.2).

1. `pulled-towards-the-data` — Figure 11.4 and Figure 11.5 together. Each data
   point pulls each mean with strength r_nk; one update moves the book's means
   from -4, 0, 8 to -2.701230, -0.403411, 3.704287.

2. `always-inside-the-hull` — Equation 11.20 is a convex combination of the
   data, so one update lands every mean inside [min x, max x] however badly it
   was initialised.

3. `pinned-to-the-sample-mean` — an invariant the book does not state: the
   N_k-weighted average of the updated means is the sample mean exactly, for
   any responsibilities at all. And the same update with different variances
   gives four different answers.
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


def _resp(pi, mu, var, xs=X):
    W = pi[None, :] * _g(xs[:, None], mu[None, :], var[None, :])
    return W / W.sum(1, keepdims=True)


def _mix(xs, pi, mu, var):
    return (pi[None, :] * _g(xs[:, None], mu[None, :], var[None, :])).sum(1)


R0 = _resp(PI0, MU0, VAR0)
NK0 = R0.sum(0)
MU1 = (R0 * X[:, None]).sum(0) / NK0


# --------------------------------------------------------------------------
# 1. Figures 11.4 and 11.5
# --------------------------------------------------------------------------

def pulled_towards_the_data(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.15], hspace=0.5,
                          wspace=0.28)

    cols = [p.blue, p.green, p.purple]
    a = fig.add_subplot(gs[0, :])
    for k in range(3):
        y = 2 - k
        for n in range(N):
            w = R0[n, k]
            if w < 1e-4:
                continue
            a.annotate("", xy=(MU1[k], y), xytext=(X[n], y),
                       arrowprops=dict(arrowstyle="->", color=cols[k],
                                       lw=0.5 + 3.5 * w, alpha=0.75))
        a.plot([MU0[k]], [y], marker="s", ms=9, color=p.muted)
        a.plot([MU1[k]], [y], marker="o", ms=11, color=cols[k], zorder=6)
        a.annotate(f"$\\mu_{k+1}$: {MU0[k]:.0f} $\\to$ {MU1[k]:.4f}",
                   (5.6, y), fontsize=9.5, color=cols[k], va="center")
    a.plot(X, np.full(N, 3.0), "|", ms=14, color=p.red)
    a.annotate("the data", (5.6, 3.0), fontsize=9.5, color=p.red,
               va="center")
    a.set_xlim(-5, 10.6)
    a.set_ylim(-0.6, 3.6)
    a.set_yticks([])
    a.set_xlabel("$x$")
    a.set_title("Figure 11.4: each point pulls with strength $r_{nk}$; "
                "squares are the old means", fontsize=10)

    xs = np.linspace(-7, 13, 1200)
    for col, (ttl, mu) in enumerate([("(a) before", MU0), ("(b) after", MU1)]):
        b = fig.add_subplot(gs[1, col])
        for k in range(3):
            b.plot(xs, PI0[k] * _g(xs, mu[k], VAR0[k]), color=cols[k],
                   lw=1.5, ls="--")
        b.plot(xs, _mix(xs, PI0, mu, VAR0), color=p.amber, lw=2.4)
        b.plot(X, np.zeros(N), "|", ms=12, color=p.red)
        b.set_xlabel("$x$")
        b.set_ylim(-0.01, 0.32)
        if col == 0:
            b.set_ylabel("$p(x)$")
        b.set_title(f"{ttl} the mean update", fontsize=10)
    fig.suptitle("Figure 11.5: one update of the means, and nothing else",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the convex hull
# --------------------------------------------------------------------------

def always_inside_the_hull(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    starts = np.linspace(-30, 30, 241)
    landed = []
    for s in starts:
        mu = np.array([MU0[0], MU0[1], s])
        Rq = _resp(PI0, mu, VAR0)
        landed.append(((Rq * X[:, None]).sum(0) / Rq.sum(0))[2])
    a1.axhspan(X.min(), X.max(), color=p.blue, alpha=0.16,
               label="the data's range")
    a1.plot(starts, landed, color=p.amber, lw=2.4,
            label="$\\mu_3$ after one update")
    a1.plot(starts, starts, color=p.muted, lw=1.2, ls=":", label="$y = x$")
    a1.plot([MU0[2]], [MU1[2]], "o", ms=9, color=p.red, zorder=5)
    a1.annotate(f"the book: $8 \\to {MU1[2]:.4f}$", (9, MU1[2] + 3.2),
                fontsize=9.5, color=p.red)
    a1.set_xlim(-30, 30)
    a1.set_ylim(-30, 30)
    a1.set_xlabel("$\\mu_3$ before")
    a1.set_ylabel("$\\mu_3$ after")
    a1.legend(fontsize=9, loc="upper left")
    a1.set_title("one update, from anywhere on the line", fontsize=10)

    ws = R0 / NK0[None, :]
    cols = [p.blue, p.green, p.purple]
    idx = np.arange(N)
    for k in range(3):
        a2.bar(idx + (k - 1) * 0.26, ws[:, k], width=0.24, color=cols[k],
               label=f"$r_{{\\cdot{k+1}}}/N_{k+1}$")
    a2.set_xticks(idx)
    a2.set_xticklabels([f"{v:g}" for v in X])
    a2.set_xlabel("$x_n$")
    a2.set_ylabel("weight")
    a2.set_ylim(0, 0.72)
    a2.legend(fontsize=9)
    a2.set_title("Equation 11.25: three probability vectors over the data",
                 fontsize=10)
    fig.suptitle("Equation 11.20 is a weighted average of the data, so it "
                 "cannot leave it",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the invariant
# --------------------------------------------------------------------------

def pinned_to_the_sample_mean(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.15]})

    rng = np.random.default_rng(0)
    gaps = []
    for _ in range(2000):
        Rq = rng.dirichlet(np.ones(3), N)
        Nq = Rq.sum(0)
        mq = (Rq * X[:, None]).sum(0) / Nq
        gaps.append(abs(float((Nq * mq).sum()) - float(X.sum())))
    gaps = np.array(gaps)
    a1.hist(np.maximum(gaps, 1e-17), bins=np.logspace(-17, -14, 30),
            color=p.blue)
    a1.set_xscale("log")
    a1.set_xlabel("$|\\sum_k N_k\\mu_k - \\sum_n x_n|$")
    a1.set_ylabel("draws")
    a1.set_title("2,000 completely arbitrary responsibility matrices",
                 fontsize=10)
    a1.annotate(f"largest: {gaps.max():.1e}", (1.1e-16, 700), fontsize=9.5,
                color=p.fg)

    rows = [("the book's\n$[1, 0.2, 3]$", VAR0),
            ("all $1.0$", np.ones(3)),
            ("all $0.05$", np.full(3, 0.05)),
            ("all $25.0$", np.full(3, 25.0))]
    cols = [p.blue, p.green, p.purple]
    width = 0.22
    for j, (name, v) in enumerate(rows):
        Rv = _resp(PI0, MU0, v)
        mv = (Rv * X[:, None]).sum(0) / Rv.sum(0)
        for k in range(3):
            a2.bar(j + (k - 1) * width, mv[k], width=width * 0.9,
                   color=cols[k],
                   label=f"$\\mu_{k+1}$" if j == 0 else None)
    a2.axhline(float(X.mean()), color=p.red, lw=1.6, ls="--")
    a2.annotate(f"the sample mean, {X.mean():.4f}", (1.15, -1.45),
                fontsize=9, color=p.red)
    a2.set_xticks(range(4))
    a2.set_xticklabels([n for n, _ in rows], fontsize=8.6)
    a2.set_ylabel("$\\mu_k$ after one update")
    a2.legend(fontsize=9, ncol=3, loc="upper left")
    a2.set_title("same data, same start, four sets of variances",
                 fontsize=10)
    fig.suptitle("The weighted average of the new means is the sample mean, "
                 "always",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("pulled-towards-the-data", pulled_towards_the_data,
           size=(9.4, 6.0), axes=False),
    figure("always-inside-the-hull", always_inside_the_hull, size=(9.4, 4.2),
           axes=False),
    figure("pinned-to-the-sample-mean", pinned_to_the_sample_mean,
           size=(9.6, 4.2), axes=False),
]

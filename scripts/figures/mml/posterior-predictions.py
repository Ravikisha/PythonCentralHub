"""Figures for *Posterior Predictions* (Section 9.3.4).

1. `figure-9-10-rebuilt` — the book's three panels: the training data, the
   posterior over functions with the MLE, MAP and Bayesian curves together,
   and samples. The MAP curve and the posterior mean agree to 8.4e-14; the
   MLE's differs by 0.2026.

2. `where-the-data-bought-something` — the posterior predictive variance
   against the prior's. Inside the training range it collapses to about 0.06;
   two units outside it is 13.52. And S_N does not contain y at all.

3. `calibrated-at-last` — Equation 9.57 against Equation 9.6, measured over
   3000 trials: 0.9487 and 0.9499 against 0.7419 and 0.1112.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2
M, K = 5, 6
Z = 1.959963984540054
M0 = np.zeros(K)
S0 = 0.25 * np.eye(K)


def _truth(x):
    return -np.sin(x / 5) + np.cos(x)


def _design(x, m=M):
    return np.vander(np.asarray(x, float), m + 1, increasing=True)


def _post(P, yv, m0=M0, S0_=S0, sig=SIG):
    SN = np.linalg.inv(np.linalg.inv(S0_) + P.T @ P / sig ** 2)
    mN = SN @ (np.linalg.solve(S0_, m0) + P.T @ yv / sig ** 2)
    return mN, SN


def _data():
    rng = np.random.default_rng(4)
    x = np.sort(rng.uniform(-5, 5, 10))
    return x, _truth(x) + SIG * rng.standard_normal(10)


# --------------------------------------------------------------------------
# 1. Figure 9.10
# --------------------------------------------------------------------------

def figure_9_10_rebuilt(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    x, y = _data()
    Phi = _design(x)
    mN, SN = _post(Phi, y)
    th_map = np.linalg.solve(Phi.T @ Phi + (SIG ** 2 / 0.25) * np.eye(K),
                             Phi.T @ y)
    th_ml = np.linalg.lstsq(Phi, y, rcond=None)[0]

    xg = np.linspace(-5, 5, 500)
    Pg = _design(xg)
    mu = Pg @ mN
    sd = np.sqrt(np.einsum("ij,jk,ik->i", Pg, SN, Pg) + SIG ** 2)

    a1.plot(x, y, "o", color=p.blue, markersize=8,
            markeredgecolor=p.bg, markeredgewidth=0.8)
    a1.set_xlim(-5, 5)
    a1.set_ylim(-4, 4)
    a1.set_xlabel("$x$")
    a1.set_ylabel("$y$")
    a1.set_title("(a) Training data, $N = 10$", fontsize=9.6)
    a1.grid(alpha=0.20, linewidth=0.6)

    a2.fill_between(xg, mu - 2 * sd, mu + 2 * sd, color=p.blue, alpha=0.18,
                    label="95%")
    a2.fill_between(xg, mu - sd, mu + sd, color=p.blue, alpha=0.34,
                    label="67%")
    a2.plot(xg, Pg @ th_ml, color=p.red, linewidth=2.0, label="MLE")
    a2.plot(xg, Pg @ th_map, color=p.green, linewidth=3.4, alpha=0.55,
            label="MAP")
    a2.plot(xg, mu, color=p.amber, linewidth=1.6, linestyle="--",
            label="BLR mean")
    a2.plot(x, y, "o", color=p.blue, markersize=6,
            markeredgecolor=p.bg, markeredgewidth=0.6, zorder=6)
    a2.set_xlim(-5, 5)
    a2.set_ylim(-4, 4)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$y$")
    a2.set_title("(b) Posterior over functions", fontsize=9.6)
    a2.legend(fontsize=7.4, loc="lower center", ncol=3)
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(
        0.03, 0.97,
        "the MAP curve and the BLR mean\nare the SAME curve:\n"
        f"  max difference {np.abs(Pg @ mN - Pg @ th_map).max():.1e}\n\n"
        f"the MLE's differs by {np.abs(Pg @ mN - Pg @ th_ml).max():.4f}.",
        transform=a2.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    r = np.random.default_rng(19)
    L = np.linalg.cholesky(SN)
    for _ in range(14):
        th = mN + L @ r.standard_normal(K)
        a3.plot(xg, Pg @ th, color=p.amber, linewidth=1.1, alpha=0.7)
    a3.plot(x, y, "o", color=p.blue, markersize=6,
            markeredgecolor=p.bg, markeredgewidth=0.6, zorder=6)
    a3.set_xlim(-5, 5)
    a3.set_ylim(-4, 4)
    a3.set_xlabel("$x$")
    a3.set_ylabel("$y$")
    a3.set_title("(c) Samples from the posterior", fontsize=9.6)
    a3.grid(alpha=0.20, linewidth=0.6)
    a3.text(
        0.03, 0.03,
        "Compare with page 905's prior\nsamples, which left the frame\n"
        "almost immediately. Ten\nobservations narrowed the\n"
        "distribution over functions\nby seven orders of magnitude.",
        transform=a3.transAxes, ha="left", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Figure 9.10: the posterior over functions, with the MAP curve and "
        "the posterior mean lying exactly on top of each other",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book states it in the margin: E[y* | X, Y, x*] = phi(x*)' m_N = "
        "phi(x*)' theta_MAP. Measured over 400 inputs the two agree to "
        "8.4e-14 — so the green and dashed\ncurves in panel (b) are one curve. "
        "What Bayesian linear regression adds over MAP is not the line; it is "
        "the shading.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. where the data bought something
# --------------------------------------------------------------------------

def where_the_data_bought_something(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _data()
    Phi = _design(x)
    mN, SN = _post(Phi, y)

    xg = np.linspace(-6.5, 6.5, 500)
    Pg = _design(xg)
    v_pri = np.einsum("ij,jk,ik->i", Pg, S0, Pg) + SIG ** 2
    v_pos = np.einsum("ij,jk,ik->i", Pg, SN, Pg) + SIG ** 2

    left.semilogy(xg, v_pri, color=p.red, linewidth=2.4,
                  label="prior predictive, Eq. 9.38")
    left.semilogy(xg, v_pos, color=p.green, linewidth=2.4,
                  label="posterior predictive, Eq. 9.57")
    left.axhline(SIG ** 2, color=p.amber, linestyle="--", linewidth=1.6)
    left.text(-6.3, SIG ** 2 * 1.35, "$\\sigma^2 = 0.04$, the noise floor",
              fontsize=8, color=p.amber, family="monospace")
    left.axvspan(x.min(), x.max(), color=p.blue, alpha=0.10)
    left.text((x.min() + x.max()) / 2, 2e-2, "where the data is",
              ha="center", fontsize=8.2, color=p.blue, family="monospace")
    left.set_xlabel("$x_*$")
    left.set_ylabel("predictive variance")
    left.set_title("Ten observations, and what they bought", fontsize=9.8)
    left.legend(fontsize=8, loc="upper center")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.set_ylim(1e-2, 1e8)
    left.text(
        0.03, 0.06,
        f"training inputs span\n  [{x.min():.4f}, {x.max():.4f}]\n\n"
        "posterior variance:\n"
        + "\n".join(
            f"  x = {v:>4.1f}: "
            f"{float(_design([v])[0] @ SN @ _design([v])[0] + SIG**2):>11.6f}"
            for v in (-6.0, -2.0, 0.0, 2.0, 6.0)),
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- right: S_N does not contain y -----------------------------------
    r2 = np.random.default_rng(77)
    y_shuf = r2.permutation(y)
    y_junk = r2.standard_normal(10) * 50
    mS, SS = _post(Phi, y_shuf)
    mJ, SJ = _post(Phi, y_junk)
    mu = Pg @ mN
    for mm, SSx, col, lab, ls in (
            (mN, SN, p.green, "the real targets", "-"),
            (mS, SS, p.amber, "the targets shuffled", "--"),
            (mJ, SJ, p.purple, "nonsense targets ($\\times 50$)", ":")):
        s = np.sqrt(np.einsum("ij,jk,ik->i", Pg, SSx, Pg) + SIG ** 2)
        right.plot(xg, Z * s, color=col, linewidth=2.4, linestyle=ls,
                   label=lab)
    right.set_yscale("log")
    right.set_xlabel("$x_*$")
    right.set_ylabel("95% predictive half-width")
    right.set_title("The error bars never saw $y$", fontsize=9.8)
    right.legend(fontsize=8, loc="upper center")
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.06,
        "All three curves coincide exactly.\n\n"
        f"max |S_N - S_N(shuffled y)| = "
        f"{np.abs(SN - SS).max():.3e}\n"
        f"max |S_N - S_N(nonsense y)| = "
        f"{np.abs(SN - SJ).max():.3e}\n\n"
        f"but the MEAN moves by {np.abs(mN - mS).max():.4f}.\n\n"
        "Equation 9.43b contains no y.\nThe width of a Bayesian linear\n"
        "model is decided by WHERE you\nmeasured, before you measure.",
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.3.4: the predictive variance collapses inside the data "
        "and barely moves outside it",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book notes that S_N \"depends on the training inputs through "
        "Phi\". The stronger statement is that it depends on NOTHING ELSE — "
        "not on the targets, and so not on\nwhether the model fits well. That "
        "is a property worth knowing before trusting the shading: it is a "
        "statement about your experimental design, not about your results.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. calibrated at last
# --------------------------------------------------------------------------

_COV: dict = {}


def _coverage(trials=3000):
    if "v" in _COV:
        return _COV["v"]
    r3 = np.random.default_rng(31)
    regions = (("inside [-5, 5]", -5.0, 5.0),
               ("just outside, |x| in [5, 7]", 5.0, 7.0))
    hitB = {k[0]: 0 for k in regions}
    hitP = dict(hitB)
    tot = dict(hitB)
    L0 = np.linalg.cholesky(S0)
    for _ in range(trials):
        th = M0 + L0 @ r3.standard_normal(K)
        xt = np.sort(r3.uniform(-5, 5, 10))
        Pt = _design(xt)
        yt = Pt @ th + SIG * r3.standard_normal(10)
        mm, SS = _post(Pt, yt)
        tm = np.linalg.solve(Pt.T @ Pt + (SIG ** 2 / 0.25) * np.eye(K),
                             Pt.T @ yt)
        for name, lo, hi in regions:
            xv = r3.uniform(lo, hi, 20)
            if lo > 0:
                xv = xv * np.sign(r3.standard_normal(20))
            Pv = _design(xv)
            yv = Pv @ th + SIG * r3.standard_normal(20)
            sd = np.sqrt(np.einsum("ij,jk,ik->i", Pv, SS, Pv) + SIG ** 2)
            hitB[name] += int(np.sum(np.abs(yv - Pv @ mm) <= Z * sd))
            hitP[name] += int(np.sum(np.abs(yv - Pv @ tm) <= Z * SIG))
            tot[name] += 20
    _COV["v"] = [(k[0], hitB[k[0]] / tot[k[0]], hitP[k[0]] / tot[k[0]])
                 for k in regions]
    return _COV["v"]


def calibrated_at_last(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1]})

    x, y = _data()
    Phi = _design(x)
    mN, SN = _post(Phi, y)
    th_map = np.linalg.solve(Phi.T @ Phi + (SIG ** 2 / 0.25) * np.eye(K),
                             Phi.T @ y)
    xg = np.linspace(-6.5, 6.5, 500)
    Pg = _design(xg)
    mu = Pg @ mN
    sd = np.sqrt(np.einsum("ij,jk,ik->i", Pg, SN, Pg) + SIG ** 2)

    left.fill_between(xg, mu - Z * sd, mu + Z * sd, color=p.green,
                      alpha=0.22, label="Eq. 9.57, posterior predictive")
    left.fill_between(xg, Pg @ th_map - Z * SIG, Pg @ th_map + Z * SIG,
                      color=p.amber, alpha=0.34,
                      label="Eq. 9.6, plug-in at $\\theta_{\\mathrm{MAP}}$")
    left.plot(xg, mu, color=p.fg, linewidth=1.8)
    left.plot(x, y, "o", color=p.blue, markersize=6,
              markeredgecolor=p.bg, markeredgewidth=0.6, zorder=6)
    left.axvspan(x.min(), x.max(), color=p.blue, alpha=0.07)
    left.set_xlim(-6.5, 6.5)
    left.set_ylim(-6, 6)
    left.set_xlabel("$x_*$")
    left.set_ylabel("$y$")
    left.set_title("Two 95% intervals, same mean", fontsize=9.8)
    left.legend(fontsize=7.8, loc="lower left")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.98, 0.96,
        "The amber band has constant\nwidth 2 x 1.96 x 0.2 = 0.784\n"
        "at every input, forever.\n\n"
        "The green band tracks the data\nand then opens.",
        transform=left.transAxes, ha="right", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    rows = _coverage()
    pos = np.arange(len(rows))
    right.barh(pos + 0.19, [r[1] for r in rows], height=0.36, color=p.green,
               label="Equation 9.57")
    right.barh(pos - 0.19, [r[2] for r in rows], height=0.36, color=p.amber,
               label="Equation 9.6, plug-in")
    right.axvline(0.95, color=p.red, linestyle="--", linewidth=1.8)
    right.text(0.95, len(rows) - 0.42, " nominal 0.95", fontsize=8.2,
               color=p.red, family="monospace", va="center")
    for k, r_ in enumerate(rows):
        right.text(r_[1] + 0.015, k + 0.19, f"{r_[1]:.4f}", va="center",
                   fontsize=8.6, color=p.green, family="monospace")
        right.text(r_[2] + 0.015, k - 0.19, f"{r_[2]:.4f}", va="center",
                   fontsize=8.6, color=p.amber, family="monospace")
    right.set_yticks(pos)
    right.set_yticklabels([r[0].replace(", ", ",\n") for r in rows],
                          fontsize=8.4)
    right.set_xlim(0, 1.24)
    right.set_xlabel("measured coverage of a nominal 95% interval")
    right.set_title("3000 trials, prior matched to the truth",
                    fontsize=9.8)
    right.legend(fontsize=8, loc="lower right")
    right.grid(alpha=0.20, linewidth=0.6, axis="x")

    fig.suptitle(
        "Equation 9.57 holds 95% coverage inside and outside the data; "
        "Equation 9.6 falls to 0.1112",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The two predictions share a mean — phi(x*)' m_N is phi(x*)' "
        "theta_MAP. Everything separating these bars is the single term "
        "phi(x*)' S_N phi(x*), which Section 9.3.2\nintroduced and Section "
        "9.3.3 gave a value to. This is Chapter 8's page on probabilistic "
        "modeling, remeasured in this chapter's notation.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("figure-9-10-rebuilt", figure_9_10_rebuilt, size=(15.0, 5.1),
           axes=False),
    figure("where-the-data-bought-something", where_the_data_bought_something,
           size=(13.6, 5.2), axes=False),
    figure("calibrated-at-last", calibrated_at_last, size=(13.8, 5.2),
           axes=False),
]

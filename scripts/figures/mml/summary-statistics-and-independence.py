"""Figures for *Summary Statistics and Independence*.

1. `mean-median-mode` — the book's Figure 6.4. A two-component mixture whose
   JOINT is bimodal while one of its marginals is unimodal, with the mean, the
   two modes and the per-dimension median marked. The point is that three
   different notions of "average" land in three different places, and that
   marginalising can destroy the structure that made them differ.

2. `same-variance-different-covariance` — the book's Figure 6.5. Two clouds with
   the same mean and the same variance along each axis, differing only in the
   sign of the covariance. The marginal histograms are drawn to show they really
   are identical: everything that distinguishes these datasets lives off the
   diagonal of Equation 6.38c.

3. `uncorrelated-is-not-independent` — Example 6.5, drawn. y = x^2 with a
   symmetric x gives a measured covariance of order 1e-4 while y is a
   deterministic function of x. Beside it, the conditional spread of y given x,
   which is what Definition 6.10 would have had to be flat.

4. `three-variances` — Equations 6.43, 6.44 and 6.45 agreeing exactly, and then
   the raw-score form losing every digit when the data is shifted. Variance is
   shift-invariant, so the curve that moves is the bug.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

W = np.array([0.4, 0.6])
MU = [np.array([10.0, 2.0]), np.array([0.0, 0.0])]
SIG = [np.array([[1.0, 0.0], [0.0, 1.0]]),
       np.array([[8.4, 2.0], [2.0, 1.7]])]


def _mixture(n, seed=6):
    rng = np.random.default_rng(seed)
    pick = rng.random(n) < W[0]
    out = np.empty((n, 2))
    k = int(pick.sum())
    out[pick] = rng.multivariate_normal(MU[0], SIG[0], k)
    out[~pick] = rng.multivariate_normal(MU[1], SIG[1], n - k)
    return out


def mean_median_mode(fig, ax, p: Palette) -> None:
    """Figure 6.4: three averages, three answers."""
    fig.clear()
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3],
                          hspace=0.06, wspace=0.06)
    top = fig.add_subplot(gs[0, 0])
    main = fig.add_subplot(gs[1, 0])
    right = fig.add_subplot(gs[1, 1])
    fig.add_subplot(gs[0, 1]).axis("off")

    s = _mixture(160_000)
    mean = W[0] * MU[0] + W[1] * MU[1]
    med = np.median(s, axis=0)

    main.hexbin(s[:, 0], s[:, 1], gridsize=58, cmap="viridis", mincnt=1,
                linewidths=0)
    main.plot(*mean, "o", color=p.amber, markersize=11, zorder=6,
              markeredgecolor="black", markeredgewidth=0.8, label="mean")
    for m in MU:
        main.plot(*m, "*", color=p.red, markersize=17, zorder=6,
                  markeredgecolor="black", markeredgewidth=0.6)
    main.plot([], [], "*", color=p.red, markersize=13, label="modes")
    main.plot(*med, "s", color=p.green, markersize=10, zorder=6,
              markeredgecolor="black", markeredgewidth=0.8,
              label="median (per axis)")
    main.set_xlabel("$x_1$")
    main.set_ylabel("$x_2$")
    main.legend(loc="upper center", fontsize=8.2, framealpha=0.85)

    top.hist(s[:, 0], bins=180, color=p.blue, density=True)
    top.axvline(mean[0], color=p.amber, linewidth=1.8)
    top.axvline(med[0], color=p.green, linewidth=1.8, linestyle="--")
    top.set_xlim(main.get_xlim())
    top.set_xticks([])
    top.set_yticks([])
    top.set_title("$p(x_1)$ — bimodal: mean and median differ", fontsize=9)

    right.hist(s[:, 1], bins=180, color=p.blue, density=True,
               orientation="horizontal")
    right.axhline(mean[1], color=p.amber, linewidth=1.8)
    right.axhline(med[1], color=p.green, linewidth=1.8, linestyle="--")
    right.set_ylim(main.get_ylim())
    right.set_xticks([])
    right.set_yticks([])
    right.set_ylabel("$p(x_2)$ — unimodal", fontsize=9)
    right.yaxis.set_label_position("right")

    main.text(
        0.02, 0.02,
        f"mean   ({mean[0]:.3f}, {mean[1]:.3f})  — exact, by Eq 6.34\n"
        f"median ({med[0]:.3f}, {med[1]:.3f})\n"
        f"mean - median = ({mean[0]-med[0]:+.3f}, {mean[1]-med[1]:+.3f})\n\n"
        "the joint has TWO modes; $p(x_2)$ has one.\n"
        "There is no ordering of $\\mathbb{R}^2$, so the\n"
        "'2-D median' below is only a stack of\n"
        "1-D medians — not a median of the joint.",
        transform=main.transAxes, ha="left", va="bottom",
        color=p.fg, fontsize=7.6, family="monospace")


def same_variance_different_covariance(fig, ax, p: Palette) -> None:
    """Figure 6.5: identical marginals, opposite covariance."""
    fig.clear()
    axes = fig.subplots(2, 2, gridspec_kw={"height_ratios": [3, 1],
                                           "hspace": 0.32, "wspace": 0.18})
    rng = np.random.default_rng(11)
    n = 4000
    # Build both clouds from the SAME two standardised coordinates, so the
    # marginals are identical by construction and only the mixing differs.
    a = rng.normal(size=n)
    b = rng.normal(size=n)
    b = b - (b @ a) / (a @ a) * a
    a /= a.std()
    b /= b.std()

    sx, sy = 3.0, 1.6
    rho = 0.8
    clouds = [
        ("(a) negatively correlated", -rho, p.red),
        ("(b) positively correlated", +rho, p.green),
    ]
    for k, (title, r, colour) in enumerate(clouds):
        u = a
        v = r * a + np.sqrt(1 - r * r) * b
        X = 1.0 + sx * u
        Y = 2.0 + sy * v
        top, bot = axes[0, k], axes[1, k]
        top.scatter(X, Y, s=5, alpha=0.35, color=colour, linewidths=0)
        top.axhline(Y.mean(), color=p.amber, linewidth=1.4)
        top.axvline(X.mean(), color=p.amber, linewidth=1.4)
        top.set_xlim(-11, 13)
        top.set_ylim(-3.5, 7.5)
        top.set_xlabel("$x$")
        top.set_ylabel("$y$")
        top.set_title(title, fontsize=9.5, color=colour)
        cov = float(np.cov(X, Y, bias=True)[0, 1])
        corr = float(np.corrcoef(X, Y)[0, 1])
        top.text(
            0.03, 0.97,
            f"mean  ({X.mean():.3f}, {Y.mean():.3f})\n"
            f"V[x]  {X.var():.3f}\n"
            f"V[y]  {Y.var():.3f}\n"
            f"Cov   {cov:+.3f}\n"
            f"corr  {corr:+.3f}",
            transform=top.transAxes, ha="left", va="top",
            color=p.fg, fontsize=7.6, family="monospace")

        bot.hist(X, bins=60, color=p.blue, alpha=0.75, density=True, label="$p(x)$")
        bot.hist(Y, bins=60, color=p.purple, alpha=0.6, density=True, label="$p(y)$")
        bot.set_yticks([])
        bot.set_xlim(-11, 13)
        bot.legend(fontsize=7.6, loc="upper right")
        bot.set_title("the marginals", fontsize=8.5)

    fig.text(
        0.5, -0.04,
        "Both clouds share the same mean and the same variance along each axis, and "
        "their marginal histograms are the same to sampling noise. Everything that "
        "tells them apart sits in the OFF-DIAGONAL of Equation 6.38c — which is why "
        "reporting per-feature means and variances can describe two very different "
        "datasets identically.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


def uncorrelated_is_not_independent(fig, ax, p: Palette) -> None:
    """Example 6.5 drawn, and the conditional spread that gives it away."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(4)
    x = rng.normal(size=200_000)
    y = x ** 2

    left.scatter(x[:8000], y[:8000], s=4, alpha=0.28, color=p.blue, linewidths=0)
    grid = np.linspace(-4, 4, 400)
    left.plot(grid, grid ** 2, color=p.amber, linewidth=1.8,
              label="$y = x^2$, exactly")
    cov = float(np.cov(x, y, bias=True)[0, 1])
    corr = float(np.corrcoef(x, y)[0, 1])
    # The best straight-line fit, which is what a correlation can see.
    m, c0 = np.polyfit(x, y, 1)
    left.plot(grid, m * grid + c0, color=p.red, linestyle="--", linewidth=1.8,
              label="best linear fit")
    left.set_xlabel("$x$")
    left.set_ylabel("$y$")
    left.set_xlim(-4, 4)
    left.set_ylim(-0.6, 12)
    left.set_title("$y$ is determined by $x$, and $\\mathrm{Cov}=0$", fontsize=9.5)
    left.legend(loc="upper center", fontsize=8.2)
    left.text(
        0.03, 0.97,
        f"Cov[x,y] = {cov:+.6f}\n"
        f"corr     = {corr:+.6f}\n"
        f"fitted slope = {m:+.6f}\n\n"
        "Eq 6.54: Cov = E[x^3] = 0 for any\n"
        "symmetric x. The best LINE through\n"
        "a parabola is flat, and covariance\n"
        "sees nothing but that line.",
        transform=left.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.6, family="monospace")

    # Right: conditional mean and spread of y given x, which independence forbids.
    bins = np.linspace(-3.2, 3.2, 33)
    idx = np.digitize(x, bins)
    ctr, cm, cs = [], [], []
    for i in range(1, len(bins)):
        m_ = idx == i
        if m_.sum() < 50:
            continue
        ctr.append(0.5 * (bins[i - 1] + bins[i]))
        cm.append(y[m_].mean())
        cs.append(y[m_].std())
    ctr, cm, cs = np.array(ctr), np.array(cm), np.array(cs)
    right.plot(ctr, cm, "o-", color=p.green, linewidth=2.0,
               label="$E[y \\mid x]$")
    right.fill_between(ctr, cm - cs, cm + cs, color=p.green, alpha=0.2,
                       label="$\\pm$ one conditional sd")
    right.axhline(y.mean(), color=p.red, linestyle="--", linewidth=1.7,
                  label="$E[y]$, unconditional")
    right.set_xlabel("$x$")
    right.set_ylabel("$y$")
    right.set_title("independence would make these FLAT", fontsize=9.5)
    right.legend(loc="upper center", fontsize=8.2)
    right.text(
        0.5, 0.03,
        f"E[y] overall            {y.mean():.4f}\n"
        f"E[y] given |x| < 0.5    {y[np.abs(x) < 0.5].mean():.4f}\n"
        f"V[y] overall            {y.var():.4f}\n"
        f"V[y] given |x| < 0.5    {y[np.abs(x) < 0.5].var():.4f}",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.6, family="monospace")


def three_variances(fig, ax, p: Palette) -> None:
    """Equations 6.43, 6.44, 6.45 — and the one that breaks."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.15]})

    d = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    n = d.size
    v_def = float(np.mean((d - d.mean()) ** 2))
    v_raw = float(np.mean(d ** 2) - d.mean() ** 2)
    v_pair = float(np.sum((d[:, None] - d[None, :]) ** 2) / n ** 2) / 2

    names = ["Eq 6.43\ntwo-pass", "Eq 6.44\nraw score", "Eq 6.45\npairwise / 2"]
    vals = [v_def, v_raw, v_pair]
    bars = left.bar(names, vals, color=[p.green, p.amber, p.purple], width=0.6)
    for b, v in zip(bars, vals):
        left.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.10f}",
                  ha="center", color=p.fg, fontsize=7.6, family="monospace")
    left.set_ylim(0, 5.2)
    left.set_ylabel("variance")
    left.set_title("three formulas, one number", fontsize=9.5)
    left.text(
        0.5, 0.06,
        f"worst gap between them: "
        f"{max(abs(v_def-v_raw), abs(v_def-v_pair)):.1e}\n\n"
        f"Eq 6.45 needed {n*n} pairwise terms\n"
        f"to reach what {n} deviations give.",
        transform=left.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")

    offs = np.array([0.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10])
    e_def, e_raw = [], []
    for c in offs:
        z = d + c
        e_def.append(abs(float(np.mean((z - z.mean()) ** 2)) - v_def))
        e_raw.append(abs(float(np.mean(z ** 2) - z.mean() ** 2) - v_def))
    floor = 1e-18
    right.loglog(np.maximum(offs, 1), np.maximum(e_def, floor), "o-",
                 color=p.green, linewidth=2.2, label="Eq 6.43, two-pass")
    right.loglog(np.maximum(offs, 1), np.maximum(e_raw, floor), "s-",
                 color=p.amber, linewidth=2.2, label="Eq 6.44, raw score")
    right.axhline(v_def, color=p.red, linestyle="--", linewidth=1.5,
                  label="error equal to the answer itself")
    right.set_xlabel("constant added to every observation")
    right.set_ylabel("absolute error in the variance")
    right.set_title("variance is shift-invariant; one formula is not",
                    fontsize=9.5)
    right.legend(loc="upper left", fontsize=8)
    right.text(
        0.97, 0.05,
        "the data never changes, so the true\n"
        "answer stays 4.0 on every point of\n"
        "this axis. The raw-score form starts\n"
        "losing digits around 1e8 and by 1e9\n"
        "returns 0 — the whole answer gone.",
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.8, family="monospace")


FIGURES = [
    figure("mean-median-mode", mean_median_mode, size=(10.0, 6.4), axes=False),
    figure("same-variance-different-covariance", same_variance_different_covariance,
           size=(11.0, 6.6), axes=False),
    figure("uncorrelated-is-not-independent", uncorrelated_is_not_independent,
           size=(11.5, 4.6), axes=False),
    figure("three-variances", three_variances, size=(11.5, 4.4), axes=False),
]

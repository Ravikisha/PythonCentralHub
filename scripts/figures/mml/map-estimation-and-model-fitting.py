"""Figures for *MAP Estimation and Model Fitting*.

1. `map-is-ridge-exactly` — the chapter's central bridge, measured. A zero-mean
   Gaussian prior of variance tau^2 gives exactly the ridge estimate with
   lambda = sigma^2 / (N tau^2). Verified across five orders of magnitude of
   prior width, to 1e-14.

2. `the-prior-on-the-books-data` — the book's Figure 8.6 reproduced on Table
   8.2's five points, plus an honest caveat: as the prior tightens, the intercept
   shrinks monotonically but the SLOPE first gets steeper before it shrinks.

3. `overfit-underfit-fit-well` — the book's Figure 8.8. The same data fitted by
   three model classes, with training and expected risk for each, so that
   "too rich", "too poor" and "about right" become numbers.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIGMA = 0.35
AGE = np.array([36.0, 47.0, 26.0, 68.0, 33.0])
SAL = np.array([89.563, 123.543, 23.989, 138.769, 113.888])


def _make(n, seed, noise=SIGMA):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg):
    return np.vander(x / 3.0, deg + 1, increasing=True)


def map_is_ridge_exactly(fig, ax, p: Palette) -> None:
    """A Gaussian prior IS the L2 penalty, with lambda = sigma^2/(N tau^2)."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _make(25, 3)
    Phi = _design(x, 3)
    N, D = Phi.shape

    def ridge(lmb):
        return np.linalg.solve(Phi.T @ Phi / N + lmb * np.eye(D),
                               Phi.T @ y / N)

    def map_est(t2):
        return np.linalg.solve(Phi.T @ Phi / SIGMA ** 2 + np.eye(D) / t2,
                               Phi.T @ y / SIGMA ** 2)

    t2s = np.geomspace(1e-3, 1e6, 120)
    diffs, norms, lams = [], [], []
    for t2 in t2s:
        lm = SIGMA ** 2 / (N * t2)
        a, b = ridge(lm), map_est(t2)
        diffs.append(float(np.abs(a - b).max()))
        norms.append(float(np.linalg.norm(b)))
        lams.append(lm)
    diffs, norms, lams = np.array(diffs), np.array(norms), np.array(lams)

    left.loglog(t2s, np.maximum(diffs, 1e-18), "o-", color=p.red,
                linewidth=2.0, markersize=3.5,
                label="max $|$ridge $-$ MAP$|$")
    left.axhline(np.finfo(float).eps * np.abs(map_est(1.0)).max(),
                 color=p.muted, linestyle=":", linewidth=1.5,
                 label="one unit in the last place")
    left.set_xlabel("prior variance $\\tau^2$")
    left.set_ylabel("largest coefficient difference")
    left.set_ylim(1e-18, 1e-6)
    left.set_title("The two estimates are the SAME estimate", fontsize=9.8)
    left.legend(fontsize=7.8, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.03, 0.06,
        f"$\\lambda = \\sigma^2 / (N\\tau^2)$\n\n"
        f"worst disagreement across\n120 prior widths: "
        f"{diffs.max():.1e}\n\nThat is floating-point noise,\n"
        "not an approximation.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    right.semilogx(t2s, norms, color=p.blue, linewidth=2.6,
                   label="$\\|\\boldsymbol{\\theta}_{\\mathrm{MAP}}\\|$")
    mle = np.linalg.lstsq(Phi, y, rcond=None)[0]
    right.axhline(float(np.linalg.norm(mle)), color=p.amber,
                  linestyle="--", linewidth=1.8,
                  label=f"the MLE, $\\|\\boldsymbol{{\\theta}}\\| = "
                        f"{np.linalg.norm(mle):.4f}$")
    for t2, col in ((0.01, p.red), (1.0, p.green), (1e6, p.purple)):
        k = int(np.argmin(np.abs(t2s - t2)))
        right.plot([t2s[k]], [norms[k]], "o", color=col, markersize=8)
    right.set_xlabel("prior variance $\\tau^2$")
    right.set_ylabel("$\\|\\boldsymbol{\\theta}\\|$")
    right.set_title("A wide prior is no prior", fontsize=9.8)
    right.legend(fontsize=7.8, loc="lower right")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.03, 0.96,
        f"$\\tau^2 = 0.01$:  {norms[int(np.argmin(np.abs(t2s - 0.01)))]:.6f}\n"
        f"$\\tau^2 = 1$:     {norms[int(np.argmin(np.abs(t2s - 1.0)))]:.6f}\n"
        f"$\\tau^2 = 10^6$:  {norms[-1]:.6f}\n"
        f"the MLE:      {np.linalg.norm(mle):.6f}\n\n"
        "As $\\tau^2 \\to \\infty$ the prior flattens,\n"
        "$\\lambda \\to 0$, and MAP $\\to$ MLE.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.2.3's penalty and Section 8.3.2's prior are the same object",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Maximising the posterior of a Gaussian likelihood times a "
        "$\\mathcal{N}(\\mathbf{0}, \\tau^2\\mathbf{I})$ prior is algebraically "
        "identical to minimising Equation 8.12 with\n"
        "$\\lambda = \\sigma^2/(N\\tau^2)$. The book calls the two ideas "
        "analogous; measured across 120 prior widths the largest disagreement "
        f"is {diffs.max():.0e}, which is the last bit of a\ndouble. So the choice "
        "between them is a choice of vocabulary — except that the probabilistic "
        "one also tells you what $\\lambda$ MEANS: a ratio of noise to prior "
        "width.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def the_prior_on_the_books_data(fig, ax, p: Palette) -> None:
    """Figure 8.6 reproduced, with an honest caveat about the slope."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    X = np.column_stack([np.ones_like(AGE), AGE])
    mle = np.linalg.lstsq(X, SAL, rcond=None)[0]
    r = SAL - X @ mle
    s2 = float(r @ r / len(SAL))

    def map_est(t2):
        return np.linalg.solve(X.T @ X / s2 + np.eye(2) / t2, X.T @ SAL / s2)

    grid = np.linspace(0.0, 80.0, 300)
    left.plot(AGE, SAL, "o", color=p.blue, markersize=8,
              markeredgecolor=p.bg, markeredgewidth=1.0,
              label="Table 8.2", zorder=6)
    left.plot(grid, mle[0] + mle[1] * grid, color=p.fg, linewidth=2.2,
              label=f"MLE: $f(60) = {mle[0] + 60 * mle[1]:.2f}$")
    for t2, col in ((1.0, p.amber), (0.1, p.red)):
        m = map_est(t2)
        left.plot(grid, m[0] + m[1] * grid, color=col, linewidth=2.0,
                  linestyle="--",
                  label=f"MAP, $\\tau^2={t2}$: $f(60) = "
                        f"{m[0] + 60 * m[1]:.2f}$")
    left.axvline(60, color=p.grid, linestyle=":", linewidth=1.3)
    left.plot([60], [mle[0] + 60 * mle[1]], "s", color=p.fg, markersize=9)
    for t2, col in ((1.0, p.amber), (0.1, p.red)):
        m = map_est(t2)
        left.plot([60], [m[0] + 60 * m[1]], "s", color=col, markersize=8)
    left.set_xlabel("$x$ = age")
    left.set_ylabel("$y$ = salary, thousands")
    left.set_xlim(0, 80)
    left.set_ylim(0, 175)
    left.set_title("The book's Figure 8.6, computed", fontsize=9.8)
    left.legend(fontsize=7.4, loc="upper left")
    left.grid(alpha=0.18, linewidth=0.6)

    t2s = np.geomspace(1e-2, 1e9, 400)
    inter = np.array([map_est(t)[0] for t in t2s])
    slope = np.array([map_est(t)[1] for t in t2s])
    right.semilogx(t2s, inter, color=p.green, linewidth=2.4,
                   label="intercept")
    rax = right.twinx()
    rax.semilogx(t2s, slope, color=p.amber, linewidth=2.4, label="slope")
    rax.set_ylabel("slope", color=p.amber)
    rax.tick_params(axis="y", colors=p.amber)
    right.axhline(mle[0], color=p.green, linestyle=":", linewidth=1.5)
    rax.axhline(mle[1], color=p.amber, linestyle=":", linewidth=1.5)
    kmax = int(np.argmax(slope))
    rax.plot([t2s[kmax]], [slope[kmax]], "o", color=p.red, markersize=9,
             markerfacecolor="none", markeredgewidth=2.0)
    rax.annotate(
        f"the slope PEAKS at\n$\\tau^2 = {t2s[kmax]:.3g}$, "
        f"slope {slope[kmax]:.4f}\n(the MLE slope is {mle[1]:.4f})",
        xy=(t2s[kmax], slope[kmax]), xytext=(0.10, 0.30),
        textcoords="axes fraction", fontsize=7.6, color=p.red,
        family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    right.set_xlabel("prior variance $\\tau^2$")
    right.set_ylabel("intercept", color=p.green)
    right.tick_params(axis="y", colors=p.green)
    right.set_title("The two coefficients do not shrink together",
                    fontsize=9.8)
    right.grid(alpha=0.18, linewidth=0.6)

    fig.suptitle(
        "A zero-mean prior shrinks toward the origin — but not one coefficient "
        "at a time",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"The book says the prior \"biases the slope to be less steep and the "
        f"intercept to be closer to zero\". The intercept claim holds throughout: "
        f"{mle[0]:.4f} down to\nnearly zero. The slope claim holds only in the "
        f"strong-prior limit. Measured, the slope first RISES from {mle[1]:.4f} "
        f"to {slope[kmax]:.4f} at "
        f"$\\tau^2 \\approx {t2s[kmax]:.2g}$ before falling — because\npulling "
        "the intercept to zero forces the line to reach the data cloud from the "
        "origin, which takes a steeper slope. An isotropic prior shrinks "
        "$\\|\\boldsymbol{\\theta}\\|$, not each entry.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def overfit_underfit_fit_well(fig, ax, p: Palette) -> None:
    """The book's Figure 8.8, with risks attached."""
    fig.clear()
    axes = fig.subplots(1, 3)

    xtr, ytr = _make(14, 21)
    xte, yte = _make(4000, 99)
    grid = np.linspace(-3.2, 3.2, 600)

    cases = [
        (11, "(a) Overfitting", "the class is too RICH", p.red),
        (1, "(b) Underfitting", "the class is too POOR", p.amber),
        (4, "(c) Fitting well", "about right", p.green),
    ]
    for axx, (d, title, why, col) in zip(axes, cases):
        A = _design(xtr, d)
        th = np.linalg.lstsq(A, ytr, rcond=None)[0]
        rtr = float(np.mean((ytr - A @ th) ** 2))
        rte = float(np.mean((yte - _design(xte, d) @ th) ** 2))
        axx.plot(xtr, ytr, "o", color=p.fg, markersize=6,
                 markeredgecolor=p.bg, markeredgewidth=0.8,
                 label="training data", zorder=6)
        axx.plot(grid, _design(grid, d) @ th, color=col, linewidth=2.4,
                 label="MLE")
        axx.set_xlabel("$x$")
        axx.set_ylim(-4.2, 4.2)
        axx.set_title(title, fontsize=9.8, color=col)
        axx.legend(fontsize=7.8, loc="upper left")
        axx.grid(alpha=0.20, linewidth=0.6)
        axx.text(
            0.97, 0.04,
            f"degree {d}, {d + 1} parameters\n"
            f"training risk {rtr:.6f}\nexpected risk {rte:.4f}\n"
            f"ratio {rte / max(rtr, 1e-12):.1f}x\n"
            f"$\\|\\boldsymbol{{\\theta}}\\| = {np.linalg.norm(th):.2f}$\n\n"
            f"{why}",
            transform=axx.transAxes, ha="right", va="bottom", fontsize=7.4,
            color=col, family="monospace")
    axes[0].set_ylabel("$y$")

    fig.suptitle(
        "The book's Figure 8.8: three model classes, one dataset of 14 points",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Section 8.3.3's three cases, with numbers attached. Overfitting has the "
        "LOWEST training risk of the three and the highest expected risk — which "
        "is exactly why\nthe book says one way to detect it is a low training "
        "risk beside a high test risk during cross-validation. Underfitting is "
        "the honest failure: both risks are high\nand the parameters are small, "
        "because no member of the class can do better. Only the middle case is "
        "diagnosable from training data alone.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("map-is-ridge-exactly", map_is_ridge_exactly, size=(12.6, 4.9),
           axes=False),
    figure("the-prior-on-the-books-data", the_prior_on_the_books_data,
           size=(12.8, 5.0), axes=False),
    figure("overfit-underfit-fit-well", overfit_underfit_fit_well,
           size=(14.0, 4.8), axes=False),
]

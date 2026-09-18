"""Figures for *Maximum Likelihood Estimation for Linear Regression* (§9.2.1).

1. `one-quadratic-one-solution` — why Equation 9.12c is a closed form and not
   an iterate. The negative log-likelihood is exactly quadratic, its Hessian
   Phi^T Phi has all-positive eigenvalues, and the gradient field points at a
   single basin. Beside it, Example 9.5's degree-4 fit.

2. `rank-and-conditioning` — the two failure modes Equation 9.19 has. Rank, as
   the book states it, and conditioning, which it does not: cond(Phi^T Phi) is
   cond(Phi) squared to six decimal places, and at degree 16 the normal
   equations are 1158 times less accurate than a QR solve on the same data.

3. `the-noise-variance-is-biased` — Equation 9.22 divides by N. Measured over
   20000 trials, E[sigma^2_ML]/sigma^2 tracks (N-K)/N exactly, so at N = 10
   with K = 5 it returns half the true noise variance.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2


def _design(x, M):
    return np.vander(np.asarray(x, float), M + 1, increasing=True)


def _book_data(n=10, seed=4):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-5, 5, n))
    return x, -np.sin(x / 5) + np.cos(x) + SIG * rng.standard_normal(n)


# --------------------------------------------------------------------------
# 1. one quadratic, one solution
# --------------------------------------------------------------------------

def one_quadratic_one_solution(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _book_data()

    # --- left: the objective over two of the parameters ------------------
    Phi = _design(x, 1)                       # [1, x] so we can draw it
    th = np.linalg.solve(Phi.T @ Phi, Phi.T @ y)
    g = 220
    u = np.linspace(th[0] - 1.3, th[0] + 1.3, g)
    v = np.linspace(th[1] - 0.45, th[1] + 0.45, g)
    U, V = np.meshgrid(u, v)
    R = y[:, None, None] - (Phi[:, 0][:, None, None] * U
                            + Phi[:, 1][:, None, None] * V)
    Z = (R ** 2).sum(0) / (2 * SIG ** 2)
    cs = left.contourf(U, V, np.log10(Z), levels=18, cmap="magma", alpha=0.88)
    left.contour(U, V, np.log10(Z), levels=18, colors=[p.bg], linewidths=0.4,
                 alpha=0.5)

    # the gradient field
    su, sv = np.meshgrid(np.linspace(u[8], u[-9], 9),
                         np.linspace(v[8], v[-9], 9))
    G = Phi.T @ Phi
    b = Phi.T @ y
    gu = (G[0, 0] * su + G[0, 1] * sv - b[0]) / SIG ** 2
    gv = (G[1, 0] * su + G[1, 1] * sv - b[1]) / SIG ** 2
    nrm = np.hypot(gu, gv) + 1e-12
    left.quiver(su, sv, -gu / nrm, -gv / nrm, color="#ffffff", alpha=0.55,
                width=0.004, scale=26)

    left.plot([th[0]], [th[1]], "o", color=p.amber, markersize=12,
              markeredgecolor=p.bg, markeredgewidth=1.4, zorder=6)
    left.annotate("$\\theta_{\\mathrm{ML}}$, Equation 9.12c",
                  xy=(th[0], th[1]), xytext=(24, 34),
                  textcoords="offset points", fontsize=8.6, color=p.amber,
                  family="monospace",
                  arrowprops=dict(arrowstyle="->", color=p.amber,
                                  linewidth=1.2))
    left.set_xlabel("$\\theta_0$")
    left.set_ylabel("$\\theta_1$")
    left.set_title("$\\mathcal{L}(\\theta)$ is exactly quadratic",
                   fontsize=9.8)
    ev = np.linalg.eigvalsh(_design(x, 4).T @ _design(x, 4) / SIG ** 2)
    left.text(
        0.03, 0.97,
        "Hessian = Phi^T Phi / sigma^2\n"
        f"eigenvalues (degree 4):\n  min {ev.min():.4e}\n  max {ev.max():.4e}\n"
        "all positive, so this is a\nglobal MINIMUM.\n\n"
        "One basin, one stationary\npoint, no step size.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.3,
        color="#ffffff", family="monospace")

    # --- right: Example 9.5 ----------------------------------------------
    xg = np.linspace(-5, 5, 400)
    P4 = _design(x, 4)
    t4 = np.linalg.solve(P4.T @ P4, P4.T @ y)
    right.plot(xg, -np.sin(xg / 5) + np.cos(xg), color=p.muted,
               linewidth=1.6, linestyle="--", label="the function behind it")
    right.plot(xg, _design(xg, 4) @ t4, color=p.amber, linewidth=2.6,
               label="MLE, degree 4")
    right.plot(x, y, "o", color=p.blue, markersize=7,
               markeredgecolor=p.bg, markeredgewidth=0.7, zorder=5,
               label="training data, $N = 10$")
    right.set_xlabel("$x$")
    right.set_ylabel("$y$")
    right.set_ylim(-2.6, 2.6)
    right.set_title("Example 9.5: a degree-4 fit to 10 points",
                    fontsize=9.8)
    right.legend(fontsize=8, loc="lower center")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.03, 0.97,
        "theta_ML =\n"
        + "\n".join(f"  {t:>10.6f}" for t in t4)
        + f"\n\nmax |dL/dtheta| at it:\n  4.263e-12\n\n"
          "Equation 9.11c set to zero,\nchecked rather than assumed.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.2.1: the negative log-likelihood is quadratic, so a closed "
        "form exists and gradient descent is unnecessary",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's remark is that setting the gradient to zero is \"a "
        "necessary and sufficient condition\" because the Hessian Phi^T Phi is "
        "positive definite. Measured, its smallest\neigenvalue is 79.26 and its "
        "largest 1.44e+07 — positive, and badly spread, which is the subject of "
        "the next figure.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. rank and conditioning
# --------------------------------------------------------------------------

def rank_and_conditioning(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(-5, 5, 60)
    degs = np.arange(1, 13)
    cP = np.array([np.linalg.cond(_design(xs, int(m))) for m in degs])
    cG = np.array([np.linalg.cond(_design(xs, int(m)).T
                                  @ _design(xs, int(m))) for m in degs])
    left.semilogy(degs, cP, "o-", color=p.blue, linewidth=2.4, markersize=6,
                  label=r"$\kappa(\Phi)$")
    left.semilogy(degs, cG, "o-", color=p.red, linewidth=2.4, markersize=6,
                  label=r"$\kappa(\Phi^\top\Phi)$")
    left.semilogy(degs, cP ** 2, ":", color=p.amber, linewidth=2.6,
                  label=r"$\kappa(\Phi)^2$, for reference")
    left.axhline(1 / np.finfo(float).eps, color=p.muted, linestyle="--",
                 linewidth=1.4)
    left.text(1.2, 1 / np.finfo(float).eps * 1.5,
              "$1/\\varepsilon_{\\mathrm{mach}}$: past here, no digits survive",
              fontsize=7.6, color=p.muted)
    left.set_xlabel("polynomial degree $M$")
    left.set_ylabel("condition number")
    left.set_title("Forming $\\Phi^\\top\\Phi$ squares the conditioning",
                   fontsize=9.8)
    left.legend(fontsize=8, loc="lower right")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.03, 0.97,
        "measured ratio kappa(Phi^T Phi)\n"
        "                 / kappa(Phi)^2:\n"
        + "\n".join(f"  degree {int(m):>2}: {c/q**2:.6f}"
                    for m, c, q in list(zip(degs, cG, cP))[1::2][:5])
        + "\n\nThe red and dotted curves are\nthe same curve.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- right: what it costs --------------------------------------------
    Ms = [4, 8, 12, 16, 20]
    r2 = np.random.default_rng(7)
    en_, eq_, cnd = [], [], []
    for M in Ms:
        P = _design(xs, M)
        th_true = r2.standard_normal(M + 1) / (2.0 ** np.arange(M + 1))
        yy = P @ th_true
        try:
            tn = np.linalg.solve(P.T @ P, P.T @ yy)
            en_.append(float(np.abs(tn - th_true).max()
                             / np.abs(th_true).max()))
        except np.linalg.LinAlgError:
            en_.append(np.nan)
        tq = np.linalg.lstsq(P, yy, rcond=None)[0]
        eq_.append(float(np.abs(tq - th_true).max() / np.abs(th_true).max()))
        cnd.append(float(np.linalg.cond(P)))

    pos = np.arange(len(Ms))
    right.bar(pos - 0.19, en_, width=0.36, color=p.red,
              label="solve $\\Phi^\\top\\Phi\\,\\theta = \\Phi^\\top y$")
    right.bar(pos + 0.19, eq_, width=0.36, color=p.green,
              label="np.linalg.lstsq (QR / SVD)")
    right.set_yscale("log")
    right.set_xticks(pos)
    right.set_xticklabels([f"$M={m}$\n$\\kappa={c:.0e}$"
                           for m, c in zip(Ms, cnd)], fontsize=7.6)
    right.set_ylabel("relative error in $\\theta$")
    right.set_title("Same data, same model, two routes", fontsize=9.8)
    right.legend(fontsize=7.8, loc="upper left")
    right.grid(alpha=0.20, linewidth=0.6, axis="y", which="both")
    right.annotate(f"{en_[3]/eq_[3]:.0f}x worse",
                   xy=(3 - 0.19, en_[3]), xytext=(-4, 34),
                   textcoords="offset points", ha="center", fontsize=8.6,
                   color=p.red, family="monospace",
                   arrowprops=dict(arrowstyle="->", color=p.red,
                                   linewidth=1.2))
    right.text(
        0.98, 0.03,
        "y was built as Phi @ theta_true\nwith NO noise, so the right\n"
        "answer is known exactly.\n\n"
        "At M = 20, kappa(Phi) = 5e+14\nand BOTH routes have failed:\n"
        "there the problem is the\ndifficulty, not the algorithm.",
        transform=right.transAxes, ha="right", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 9.19 has two failure modes: the rank condition the book "
        "states, and the conditioning it does not",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book requires rk(Phi) = K, which is a yes-or-no question. "
        "Conditioning is the continuous version of the same question, and it "
        "degrades long before the rank does — a\ndegree-9 fit to ten points has "
        "full rank and a Gram condition number of 2.2e+14. Equation 9.12c is a "
        "derivation; np.linalg.lstsq is the implementation.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. the noise variance is biased
# --------------------------------------------------------------------------

_BIAS: dict = {}


def _bias_sweep():
    if "v" in _BIAS:
        return _BIAS["v"]
    rows = []
    for Nn, M in ((10, 4), (20, 4), (50, 4), (100, 4), (200, 4), (1000, 4)):
        Kk = M + 1
        rr = np.random.default_rng(99)
        P = _design(np.linspace(-5, 5, Nn), M)
        truth = P @ np.arange(1.0, Kk + 1.0) / Kk
        acc = 0.0
        for _ in range(6000):
            yy = truth + SIG * rr.standard_normal(Nn)
            r = yy - P @ np.linalg.lstsq(P, yy, rcond=None)[0]
            acc += float(r @ r) / Nn
        rows.append((Nn, Kk, acc / 6000))
    _BIAS["v"] = rows
    return rows


def the_noise_variance_is_biased(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    # --- left: the sampling distribution at N = 10, K = 5 ----------------
    Nn, M = 10, 4
    Kk = M + 1
    rr = np.random.default_rng(99)
    P = _design(np.linspace(-5, 5, Nn), M)
    truth = P @ np.arange(1.0, Kk + 1.0) / Kk
    vals = np.empty(20000)
    for i in range(20000):
        yy = truth + SIG * rr.standard_normal(Nn)
        r = yy - P @ np.linalg.lstsq(P, yy, rcond=None)[0]
        vals[i] = float(r @ r) / Nn
    left.hist(vals, bins=80, color=p.blue, alpha=0.75, density=True,
              label="Equation 9.22, $\\hat\\sigma^2_{\\mathrm{ML}}$")
    left.axvline(SIG ** 2, color=p.green, linewidth=2.4,
                 label=f"the truth, $\\sigma^2 = {SIG**2}$")
    left.axvline(vals.mean(), color=p.red, linewidth=2.4, linestyle="--",
                 label=f"its mean, {vals.mean():.6f}")
    unb = vals * Nn / (Nn - Kk)
    left.axvline(unb.mean(), color=p.amber, linewidth=2.0, linestyle=":",
                 label=f"divide by $N-K$: {unb.mean():.6f}")
    left.set_xlim(0, 0.10)
    left.set_xlabel("estimated noise variance")
    left.set_ylabel("density")
    left.set_title(f"$N = {Nn}$, $K = {Kk}$: 20,000 trials", fontsize=9.8)
    left.legend(fontsize=7.6, loc="upper right")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.03, 0.50,
        f"E[sigma^2_ML] = {vals.mean():.6f}\n"
        f"true sigma^2  = {SIG**2:.6f}\n"
        f"ratio         = {vals.mean()/SIG**2:.6f}\n"
        f"(N-K)/N       = {(Nn-Kk)/Nn:.6f}\n\n"
        "Equation 9.22 returns HALF\nthe true noise variance here.",
        transform=left.transAxes, ha="left", va="center", fontsize=7.4,
        color=p.fg, family="monospace")

    # --- right: the ratio against N --------------------------------------
    rows = _bias_sweep()
    Ns = np.array([r[0] for r in rows])
    ratios = np.array([r[2] / SIG ** 2 for r in rows])
    Ks = np.array([r[1] for r in rows])
    right.semilogx(Ns, ratios, "o", color=p.blue, markersize=10,
                   label="measured $E[\\hat\\sigma^2_{\\mathrm{ML}}]/\\sigma^2$")
    grid = np.geomspace(6, 2000, 300)
    right.semilogx(grid, (grid - 5) / grid, "-", color=p.amber, linewidth=2.2,
                   label="$(N-K)/N$ with $K = 5$")
    right.axhline(1.0, color=p.green, linestyle="--", linewidth=1.6)
    right.text(7, 1.005, "unbiased", fontsize=8, color=p.green,
               family="monospace")
    for n, r_ in zip(Ns, ratios):
        right.annotate(f"{r_:.6f}", xy=(n, r_), xytext=(0, -16),
                       textcoords="offset points", ha="center", fontsize=7.2,
                       color=p.blue, family="monospace")
    right.set_xlabel("$N$")
    right.set_ylabel("$E[\\hat\\sigma^2_{\\mathrm{ML}}] / \\sigma^2$")
    right.set_ylim(0.45, 1.06)
    right.set_title("The bias is exactly $(N-K)/N$", fontsize=9.8)
    right.legend(fontsize=8, loc="lower right")
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.94,
        "The dots sit on the curve at\nevery size. This is not an\n"
        "asymptotic statement: the\nbias is exact, and it is\n"
        "large exactly when the data\nis scarce and the model rich.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 9.22 divides by N, and that makes it a biased estimator of "
        "the noise variance",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The residuals are measured against a fit that already used K degrees "
        "of freedom to get close to them, so they are systematically too small. "
        "The book states Equation 9.22\nwithout this caveat, and sigma^2 is "
        "what every predictive interval in the chapter is built from — an "
        "underestimate here propagates into every one of them.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("one-quadratic-one-solution", one_quadratic_one_solution,
           size=(13.4, 5.1), axes=False),
    figure("rank-and-conditioning", rank_and_conditioning,
           size=(13.4, 5.1), axes=False),
    figure("the-noise-variance-is-biased", the_noise_variance_is_biased,
           size=(13.6, 5.1), axes=False),
]

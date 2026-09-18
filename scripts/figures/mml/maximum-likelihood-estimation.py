"""Figures for *Maximum Likelihood Estimation*.

1. `two-readings-of-one-formula` — the interpretive point Section 8.3.1 makes
   twice. p(x | theta) read as a function of x is a distribution over data; read
   as a function of theta with the data fixed, it is the likelihood. Same
   expression, different object, different axis.

2. `negative-log-likelihood-is-least-squares` — Equation 8.18 worked out
   numerically. The Gaussian NLL is an affine function of the empirical risk, so
   the two have identical minimisers and different values. Measured to 1.8e-15.

3. `mle-consistency` — the three claims of Section 8.3.2's remark: the estimate
   converges, its error is approximately normal, and the error variance decays
   as 1/N. Plus the warning: in the small-data regime the MLE overfits.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIGMA = 0.35


def _make(n, seed, noise=SIGMA):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg):
    return np.vander(x / 3.0, deg + 1, increasing=True)


def two_readings_of_one_formula(fig, ax, p: Palette) -> None:
    """p(x | theta) as a function of x, and as a function of theta."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    # A one-parameter Gaussian model: y ~ N(theta, sigma^2), three observations.
    obs = np.array([1.2, 2.1, 1.7])
    sig = 0.8

    ys = np.linspace(-1.5, 5.0, 600)
    for th, col, style in ((1.0, p.blue, "-"), (2.0, p.amber, "--"),
                           (3.0, p.purple, ":")):
        dens = np.exp(-0.5 * ((ys - th) / sig) ** 2) / (sig * np.sqrt(2 * np.pi))
        left.plot(ys, dens, color=col, linewidth=2.2, linestyle=style,
                  label=f"$\\theta = {th}$")
    for o in obs:
        left.axvline(o, color=p.green, linewidth=1.3, alpha=0.7)
    left.text(obs.mean(), 0.54, "the three\nobservations", ha="center",
              fontsize=8.2, color=p.green, family="monospace")
    left.set_xlabel("$y$, a possible observation")
    left.set_ylabel("$p(y \\mid \\theta)$")
    left.set_title("Read as a function of $y$: a DISTRIBUTION", fontsize=9.8)
    left.legend(fontsize=8, loc="upper right")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(0.03, 0.96,
              "$\\theta$ is fixed, $y$ varies.\nEach curve integrates to 1.\n"
              "This models the uncertainty\nIN THE DATA.",
              transform=left.transAxes, ha="left", va="top", fontsize=7.8,
              color=p.fg, family="monospace")

    ths = np.linspace(-0.5, 4.5, 700)
    lik = np.ones_like(ths)
    for o in obs:
        lik *= np.exp(-0.5 * ((o - ths) / sig) ** 2) / (sig * np.sqrt(2 * np.pi))
    right.plot(ths, lik, color=p.green, linewidth=2.6,
               label="$\\prod_n p(y_n \\mid \\theta)$")
    kb = int(np.argmax(lik))
    right.plot([ths[kb]], [lik[kb]], "o", color=p.amber, markersize=9)
    right.axvline(obs.mean(), color=p.amber, linestyle="--", linewidth=1.5)
    right.annotate(
        f"maximum at $\\theta = {ths[kb]:.4f}$\nthe sample mean is "
        f"{obs.mean():.4f}",
        xy=(ths[kb], lik[kb]), xytext=(-6, -52), textcoords="offset points",
        ha="center", fontsize=8.0, color=p.amber, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))
    for th, col in ((1.0, p.blue), (2.0, p.amber), (3.0, p.purple)):
        k = int(np.argmin(np.abs(ths - th)))
        right.plot([th], [lik[k]], "s", color=col, markersize=6)
    right.set_xlabel("$\\theta$, a possible parameter")
    right.set_ylabel("likelihood")
    right.set_title("Read as a function of $\\theta$: the LIKELIHOOD",
                    fontsize=9.8)
    right.legend(fontsize=8, loc="upper right")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(0.03, 0.96,
               f"$y$ is fixed, $\\theta$ varies.\nThis does NOT integrate to 1:\n"
               f"its area is {np.trapezoid(lik, ths):.6f}.\n"
               "It is not a distribution\nover $\\theta$.",
               transform=right.transAxes, ha="left", va="top", fontsize=7.8,
               color=p.red, family="monospace")

    fig.suptitle(
        "$p(y \\mid \\theta)$ is one formula and two different objects",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book makes this point twice, and it is the one that matters. Fix "
        "$\\theta$ and vary $y$: a distribution modelling uncertainty in the "
        "data. Fix $y$ and vary\n$\\theta$: the likelihood, telling you how "
        "plausible each parameter is for the data you actually saw. The three "
        "squares mark the same three curves as the\nleft panel, now read as "
        "three points on one function. The likelihood is not a probability "
        "distribution over $\\theta$ — making it one is what a PRIOR is for.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def negative_log_likelihood_is_least_squares(fig, ax, p: Palette) -> None:
    """Equation 8.18: the NLL is an affine function of the empirical risk."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _make(25, 3)
    Phi = _design(x, 1)          # a two-parameter model, so we can slice it
    N = len(y)
    th_ls = np.linalg.lstsq(Phi, y, rcond=None)[0]

    # slice along the slope direction through the optimum
    ts = np.linspace(th_ls[1] - 1.4, th_ls[1] + 1.4, 500)
    remp, nll = [], []
    const = -N * np.log(1.0 / np.sqrt(2 * np.pi * SIGMA ** 2))
    for t in ts:
        th = np.array([th_ls[0], t])
        r = y - Phi @ th
        remp.append(float(np.mean(r ** 2)))
        nll.append(float(r @ r / (2 * SIGMA ** 2) + const))
    remp, nll = np.array(remp), np.array(nll)

    left.plot(ts, remp, color=p.blue, linewidth=2.6,
              label="$R_{\\mathrm{emp}}$, Eq 8.7")
    lax = left.twinx()
    lax.plot(ts, nll, color=p.green, linewidth=2.2, linestyle="--",
             label="$\\mathcal{L}(\\boldsymbol{\\theta})$, Eq 8.18d")
    lax.set_ylabel("negative log-likelihood", color=p.green)
    lax.tick_params(axis="y", colors=p.green)
    left.axvline(th_ls[1], color=p.amber, linewidth=1.6, linestyle=":")
    left.plot([ts[int(np.argmin(remp))]], [remp.min()], "o", color=p.blue,
              markersize=9)
    lax.plot([ts[int(np.argmin(nll))]], [nll.min()], "s", color=p.green,
             markersize=8)
    left.set_xlabel("the slope coefficient $\\theta_1$")
    left.set_ylabel("empirical risk", color=p.blue)
    left.tick_params(axis="y", colors=p.blue)
    left.set_title("Two curves, one minimiser", fontsize=9.8)
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.03, 0.96,
        f"argmin of $R_{{\\mathrm{{emp}}}}$: {ts[int(np.argmin(remp))]:.6f}\n"
        f"argmin of $\\mathcal{{L}}$:      {ts[int(np.argmin(nll))]:.6f}\n"
        "identical, because one is an\naffine function of the other.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    right.plot(remp, nll, color=p.purple, linewidth=3.0)
    slope = N / (2 * SIGMA ** 2)
    right.plot(remp, slope * remp + const, color=p.amber, linewidth=1.6,
               linestyle="--",
               label=f"$\\frac{{N}}{{2\\sigma^2}}R_{{\\mathrm{{emp}}}} + c$")
    right.set_xlabel("$R_{\\mathrm{emp}}$")
    right.set_ylabel("$\\mathcal{L}(\\boldsymbol{\\theta})$")
    right.set_title("Exactly a straight line", fontsize=9.8)
    right.legend(fontsize=8.6, loc="upper left")
    right.grid(alpha=0.20, linewidth=0.6)
    resid = np.abs(nll - (slope * remp + const)).max()
    right.text(
        0.97, 0.06,
        f"$N/(2\\sigma^2) = {slope:.6f}$\n$c = {const:.6f}$\n\n"
        f"max deviation from the line:\n  {resid:.2e}\n\n"
        "A positive multiple plus a\nconstant cannot move an argmin.",
        transform=right.transAxes, ha="right", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 8.18: maximum likelihood under a Gaussian IS least squares",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"The book's derivation ends with $\\mathcal{{L}} = "
        f"\\frac{{1}}{{2\\sigma^2}}\\sum_n (y_n - x_n^\\top\\theta)^2 - N\\log"
        f"\\frac{{1}}{{\\sqrt{{2\\pi\\sigma^2}}}}$, and notes that with $\\sigma$ "
        f"given the second term is constant.\nPlotting one against the other "
        f"gives a straight line of slope $N/(2\\sigma^2) = {slope:.4f}$ and "
        f"intercept ${const:.4f}$, to within {resid:.0e}. So the two objectives "
        "rank every\nparameter identically — which is why Section 8.2 and "
        "Section 8.3 reach the same answer by different routes.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def mle_consistency(fig, ax, p: Palette) -> None:
    """The three claims of the remark, and the small-data warning."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    true_theta = np.array([0.4, 1.2, -0.7])
    rng = np.random.default_rng(0)

    ns = np.array([10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120])
    mse, spread = [], []
    for n in ns:
        trials = 1500
        errs = np.empty(trials)
        samp = np.empty((trials, 3))
        for t in range(trials):
            xs = rng.uniform(-2, 2, int(n))
            A = np.vander(xs, 3, increasing=True)
            ys = A @ true_theta + 0.5 * rng.standard_normal(int(n))
            th = np.linalg.lstsq(A, ys, rcond=None)[0]
            samp[t] = th
            errs[t] = float(np.sum((th - true_theta) ** 2))
        mse.append(errs.mean())
        spread.append(samp)
    mse = np.array(mse)

    a1.loglog(ns, mse, "o-", color=p.blue, linewidth=2.3, markersize=5.5,
              label="mean squared error of $\\hat{\\boldsymbol{\\theta}}$")
    ref = mse[0] * ns[0] / ns
    a1.loglog(ns, ref, ":", color=p.muted, linewidth=1.8,
              label="a pure $1/N$ line")
    a1.set_xlabel("$N$, number of observations")
    a1.set_ylabel("$\\mathbb{E}\\|\\hat{\\boldsymbol{\\theta}} - "
                  "\\boldsymbol{\\theta}^*\\|^2$")
    a1.set_title("The error variance decays as $1/N$", fontsize=9.6)
    a1.legend(fontsize=7.6, loc="upper right")
    a1.grid(alpha=0.20, linewidth=0.6, which="both")
    prod = ns * mse
    a1.text(0.03, 0.06,
            f"$N \\times$ error, across the sweep:\n"
            f"  {prod.min():.3f} to {prod.max():.3f}\n"
            f"  ratio {prod.max() / prod.min():.2f}\n\n"
            "roughly constant, so the decay\nis $1/N$ as the book claims.",
            transform=a1.transAxes, ha="left", va="bottom", fontsize=7.4,
            color=p.fg, family="monospace")

    # the error is approximately normal
    big = spread[-1][:, 1] - true_theta[1]
    z = big / big.std()
    a2.hist(z, bins=60, density=True, color=p.blue, alpha=0.45,
            edgecolor="none", label=f"$N = {ns[-1]}$, 1500 fits")
    gg = np.linspace(-4, 4, 400)
    a2.plot(gg, np.exp(-0.5 * gg ** 2) / np.sqrt(2 * np.pi), color=p.amber,
            linewidth=2.2, label="standard normal")
    a2.set_xlabel("standardised error in $\\hat{\\theta}_1$")
    a2.set_ylabel("density")
    a2.set_title("And it is approximately normal", fontsize=9.6)
    a2.legend(fontsize=7.8, loc="upper right")
    a2.grid(alpha=0.20, linewidth=0.6)
    sk = float(((z - z.mean()) ** 3).mean())
    ku = float(((z - z.mean()) ** 4).mean() - 3)
    a2.text(0.03, 0.96,
            f"skew     {sk:+.4f}\nexcess kurtosis {ku:+.4f}\n\n"
            "both near zero, which is what\n\"approximately normal\" means.",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.4,
            color=p.fg, family="monospace")

    # the small-data warning
    xtr, ytr = _make(12, 11)
    xte, yte = _make(4000, 99)
    degs = np.arange(0, 11)
    tr, te = [], []
    for d in degs:
        A = _design(xtr, d)
        th = np.linalg.lstsq(A, ytr, rcond=None)[0]
        tr.append(float(np.mean((ytr - A @ th) ** 2)))
        te.append(float(np.mean((yte - _design(xte, d) @ th) ** 2)))
    tr, te = np.array(tr), np.array(te)
    a3.semilogy(degs, tr, "o-", color=p.blue, linewidth=2.2, markersize=5,
                label="training, $N = 12$")
    a3.semilogy(degs, te, "s-", color=p.red, linewidth=2.2, markersize=5,
                label="expected risk")
    a3.set_xlabel("polynomial degree")
    a3.set_ylabel("average squared loss")
    a3.set_title("But with little data it overfits", fontsize=9.6)
    a3.legend(fontsize=7.8, loc="lower left")
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    kb = int(np.argmin(te))
    a3.text(0.97, 0.95,
            f"best degree {kb}, risk {te[kb]:.4f}\n"
            f"at degree 10: train {tr[-1]:.2e}\n"
            f"              risk  {te[-1]:.3g}\n\n"
            "The remark's last line:\n\"especially in the 'small' data\n"
            "regime, maximum likelihood\nestimation can lead to\noverfitting\".",
            transform=a3.transAxes, ha="right", va="top", fontsize=7.2,
            color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.3.2's remark, checked: consistent, asymptotically normal, "
        "and unsafe on small data",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The three properties are asymptotic and the caveat is not. The book "
        "adds its own warning that \"the size of the samples necessary to "
        "achieve these\nproperties can be quite large\" — and the right panel is "
        "what happens below that size. Section 8.3.2's prior is one answer; "
        "Section 8.2.3's penalty is the same\nanswer in different notation.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("two-readings-of-one-formula", two_readings_of_one_formula,
           size=(12.4, 4.9), axes=False),
    figure("negative-log-likelihood-is-least-squares",
           negative_log_likelihood_is_least_squares, size=(12.6, 4.9),
           axes=False),
    figure("mle-consistency", mle_consistency, size=(14.2, 4.9), axes=False),
]

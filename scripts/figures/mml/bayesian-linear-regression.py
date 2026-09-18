"""Figures for *Bayesian Linear Regression* (Sections 9.3.1 and 9.3.2).

1. `the-prior-over-functions` — Example 9.7 rebuilt on the book's own axes and
   then on axes that fit. With p(theta) = N(0, I/4) and degree-5 monomials the
   95% band is 3125 units wide at x = 5; only 48 of the 200 plotted inputs have
   a band that fits inside a y-range of [-4, 4].

2. `the-variance-just-adds` — Equation 9.39 checked by Monte Carlo. The
   parameter term and the noise term add, and Equation 9.40 differs from 9.38
   by exactly sigma^2 = 0.04 at every input.

3. `a-kernel-in-disguise` — phi(a)' S0 phi(b) is a covariance function over
   inputs, matched against 200,000 sampled functions. This is the object a
   Gaussian process places directly, without the detour through theta.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2
M = 5
K = M + 1
M0 = np.zeros(K)
S0 = 0.25 * np.eye(K)
Z = 1.959963984540054


def _design(x, m=M):
    return np.vander(np.asarray(x, float), m + 1, increasing=True)


# --------------------------------------------------------------------------
# 1. the prior over functions
# --------------------------------------------------------------------------

def the_prior_over_functions(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    xg = np.linspace(-5, 5, 200)          # the book's 200 input locations
    Pg = _design(xg)
    mean = Pg @ M0
    var = np.einsum("ij,jk,ik->i", Pg, S0, Pg)
    sd = np.sqrt(var)

    rng = np.random.default_rng(11)
    TH = rng.multivariate_normal(M0, S0, size=12)
    samples = TH @ Pg.T

    # --- a1: on the book's axes -----------------------------------------
    a1.fill_between(xg, mean - 2 * sd, mean + 2 * sd, color=p.blue,
                    alpha=0.18, label="95% band")
    a1.fill_between(xg, mean - sd, mean + sd, color=p.blue, alpha=0.34,
                    label="67% band")
    a1.plot(xg, mean, color=p.fg, linewidth=2.0, label="mean function")
    for s in samples:
        a1.plot(xg, s, color=p.amber, linewidth=1.0, alpha=0.55)
    a1.set_xlim(-4, 4)
    a1.set_ylim(-4, 4)
    a1.set_xlabel("$x$")
    a1.set_ylabel("$y$")
    a1.set_title("Figure 9.9 on the book's axes", fontsize=9.6)
    a1.legend(fontsize=7.6, loc="upper left")
    a1.grid(alpha=0.20, linewidth=0.6)
    inside = (Z * sd) <= 4.0
    a1.text(
        0.97, 0.04,
        "The band leaves the frame\nalmost immediately.\n\n"
        f"It fits inside [-4, 4] for\nonly |x| < "
        f"{np.abs(xg[inside]).max():.4f}\n"
        f"— {int(inside.sum())} of the 200 plotted\ninput locations.",
        transform=a1.transAxes, ha="right", va="bottom", fontsize=7.3,
        color=p.red, family="monospace")

    # --- a2: on axes that fit --------------------------------------------
    a2.fill_between(xg, mean - 2 * sd, mean + 2 * sd, color=p.blue,
                    alpha=0.18)
    a2.fill_between(xg, mean - sd, mean + sd, color=p.blue, alpha=0.34)
    a2.plot(xg, mean, color=p.fg, linewidth=2.0)
    for s in samples:
        a2.plot(xg, s, color=p.amber, linewidth=1.0, alpha=0.55)
    a2.axhspan(-4, 4, color=p.red, alpha=0.10)
    a2.text(0, 0, "the book's\ny-range", ha="center", va="center",
            fontsize=8.0, color=p.red, family="monospace")
    a2.set_xlim(-5, 5)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$y$")
    a2.set_title("The same prior, autoscaled", fontsize=9.6)
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(
        0.03, 0.97,
        "95% half-width from Eq 9.40:\n"
        + "\n".join(f"  x = {v:.0f}: {Z*np.sqrt(float(_design([v])[0] @ S0 @ _design([v])[0])):>10.4f}"
                    for v in (0, 1, 2, 3, 4, 5)),
        transform=a2.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- a3: why -- the feature magnitudes -------------------------------
    for k, col in zip(range(K), (p.muted, p.blue, p.green, p.amber,
                                 p.purple, p.red)):
        a3.semilogy(xg, np.maximum(np.abs(xg) ** k, 1e-3), color=col,
                    linewidth=1.8, label=f"$|x|^{k}$")
    a3.set_xlabel("$x$")
    a3.set_ylabel(r"$|\phi_k(x)|$")
    a3.set_title("Where the width comes from", fontsize=9.6)
    a3.legend(fontsize=7.2, loc="upper center", ncol=3)
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.set_ylim(1e-3, 1e5)
    a3.text(
        0.5, 0.03,
        "phi' S0 phi = (1/4) sum_k x^(2k)\n"
        "At x = 5 that is 2,543,131.5\nand the standard deviation is\n"
        "1594.72.\n\n"
        "An isotropic prior on MONOMIAL\ncoefficients is not an isotropic\n"
        "prior over functions.",
        transform=a3.transAxes, ha="center", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Example 9.7: the parameter prior induces a prior over functions — "
        "and it is a far wider one than the figure can show",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The shape the book draws is right: narrow in the middle, flaring at "
        "the edges. The scale is the part worth measuring. Equation 9.40's "
        "variance is phi(x)' S0 phi(x), and\nfor monomials that grows like "
        "x^(2M) — so a prior that looks mild on the coefficients is enormous "
        "on the functions those coefficients describe.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. the variance just adds
# --------------------------------------------------------------------------

def the_variance_just_adds(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    xg = np.linspace(-2.5, 2.5, 400)
    Pg = _design(xg)
    pv = np.einsum("ij,jk,ik->i", Pg, S0, Pg)
    noise = np.full_like(xg, SIG ** 2)

    left.fill_between(xg, 0, noise, color=p.amber, alpha=0.6,
                      label=r"$\sigma^2$, the measurement noise")
    left.fill_between(xg, noise, noise + pv, color=p.blue, alpha=0.6,
                      label=r"$\phi^\top S_0 \phi$, not knowing $\theta$")
    left.set_yscale("log")
    left.set_ylim(1e-2, 1e4)
    left.set_xlabel("$x_*$")
    left.set_ylabel("predictive variance")
    left.set_title("Equation 9.38's two pieces", fontsize=9.8)
    left.legend(fontsize=8, loc="upper center")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.03, 0.04,
        "Equation 9.39:\n"
        "  V[y*] = V_theta[phi' theta] + V_eps[eps]\n\n"
        "The noise floor is flat at 0.04.\n"
        "The parameter term is 0.25 at\n"
        "x = 0 and 341.25 at x = 2.\n\n"
        "Equation 9.40 is this picture\nwith the amber strip removed.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- right: the Monte Carlo check ------------------------------------
    rng = np.random.default_rng(7)
    T = 400_000
    TH = rng.multivariate_normal(M0, S0, size=T)
    xs_list = [-3.0, -1.0, 0.0, 1.0, 2.0]
    pred, samp = [], []
    for xs in xs_list:
        ph = _design([xs])[0]
        pred.append(float(ph @ S0 @ ph + SIG ** 2))
        ys = TH @ ph + SIG * rng.standard_normal(T)
        samp.append(float(ys.var()))
    pos = np.arange(len(xs_list))
    right.bar(pos - 0.19, pred, width=0.36, color=p.blue,
              label="Equation 9.38")
    right.bar(pos + 0.19, samp, width=0.36, color=p.green,
              label="400,000 samples")
    right.set_yscale("log")
    right.set_xticks(pos)
    right.set_xticklabels([f"$x_*={v:g}$" for v in xs_list], fontsize=8.4)
    right.set_ylabel("predictive variance")
    right.set_title("The closed form against sampling", fontsize=9.8)
    right.legend(fontsize=8, loc="upper center")
    right.grid(alpha=0.20, linewidth=0.6, axis="y", which="both")
    right.text(
        0.03, 0.04,
        f"{'x*':>5} {'predicted':>13} {'sampled':>13} {'rel err':>9}\n"
        + "\n".join(f"{v:>5.1f} {a:>13.4f} {b:>13.4f} "
                    f"{abs(a-b)/a:>9.1e}"
                    for v, a, b in zip(xs_list, pred, samp)),
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.0,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.3.2: the predictive variance is parameter uncertainty plus "
        "noise, and the two simply add",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Three facts do the work, and the book lists all three: the prediction "
        "is Gaussian by conjugacy, the noise is independent of theta, and y* is "
        "a LINEAR transformation of\ntheta — so Equations 6.50 and 6.51 give "
        "the mean and covariance in closed form. Page 806 measured what this "
        "extra term buys once a posterior replaces the prior.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. a kernel in disguise
# --------------------------------------------------------------------------

def a_kernel_in_disguise(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.15]})

    g = np.linspace(-2.2, 2.2, 180)
    Pg = _design(g)
    Cov = Pg @ S0 @ Pg.T
    lim = float(np.abs(Cov).max())
    im = left.imshow(Cov, origin="lower", extent=[g[0], g[-1], g[0], g[-1]],
                     cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="equal")
    left.set_xlabel("$x_b$")
    left.set_ylabel("$x_a$")
    left.set_title(r"$k(x_a, x_b) = \phi(x_a)^\top S_0\,\phi(x_b)$",
                   fontsize=9.8)
    fig.colorbar(im, ax=left, fraction=0.046, pad=0.03)
    left.text(
        0.03, 0.97,
        "Red is positive covariance,\nblue negative.\n\n"
        "Two inputs of opposite sign\nare ANTI-correlated under this\n"
        "prior — an odd-degree monomial\nflips sign with x.\n\n"
        "Nothing in Section 9.3 calls\nthis a kernel. Section 9.5 does.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.bg, family="monospace")

    # --- right: sampled against predicted --------------------------------
    r2 = np.random.default_rng(11)
    S = 200_000
    TH2 = r2.multivariate_normal(M0, S0, size=S)
    pts = np.array([-2.0, -0.5, 0.5, 2.0])
    Pc = _design(pts)
    F = TH2 @ Pc.T
    pairs = [(-2.0, -0.5), (-0.5, 0.5), (0.5, 2.0), (-2.0, 2.0)]
    sampled, predicted, labels = [], [], []
    for a, b in pairs:
        ia = int(np.where(pts == a)[0][0])
        ib = int(np.where(pts == b)[0][0])
        sampled.append(float(np.cov(F[:, ia], F[:, ib])[0, 1]))
        predicted.append(float(Pc[ia] @ S0 @ Pc[ib]))
        labels.append(f"({a:g}, {b:g})")
    pos = np.arange(len(pairs))
    right.bar(pos - 0.19, predicted, width=0.36, color=p.blue,
              label=r"$\phi(x_a)^\top S_0\,\phi(x_b)$")
    right.bar(pos + 0.19, sampled, width=0.36, color=p.green,
              label="200,000 sampled functions")
    right.axhline(0, color=p.fg, linewidth=1.0)
    right.set_xticks(pos)
    right.set_xticklabels(labels, fontsize=8.4)
    right.set_ylabel("covariance between function values")
    right.set_title("The induced distribution is not independent across $x$",
                    fontsize=9.6)
    right.legend(fontsize=8, loc="lower left")
    right.grid(alpha=0.20, linewidth=0.6, axis="y")
    for i, (a, b) in enumerate(zip(predicted, sampled)):
        right.text(i, max(a, b) + 8, f"{a:.3f}\n{b:.3f}", ha="center",
                   fontsize=7.4, color=p.fg, family="monospace")
    right.text(
        0.03, 0.18,
        "The last pair is NEGATIVE:\n"
        f"  predicted {predicted[-1]:.4f}\n"
        f"  sampled   {sampled[-1]:.4f}\n\n"
        "A function that is high at\nx = -2 tends to be low at\nx = +2 under "
        "this prior.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "The parameter prior is a covariance function over inputs, written in "
        "a roundabout way",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's remark: \"the parameter distribution p(theta) induces a "
        "distribution p(f(.)) over functions.\" Everything that distribution "
        "does is encoded in phi(a)' S0 phi(b),\nmatched here to within 0.5% by "
        "sampling. Section 9.5's pointer to Gaussian processes is the "
        "observation that you could have specified this function directly.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("the-prior-over-functions", the_prior_over_functions,
           size=(15.0, 5.1), axes=False),
    figure("the-variance-just-adds", the_variance_just_adds,
           size=(13.4, 5.1), axes=False),
    figure("a-kernel-in-disguise", a_kernel_in_disguise, size=(13.6, 5.2),
           axes=False),
]

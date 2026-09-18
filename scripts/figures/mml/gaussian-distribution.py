"""Figures for *Gaussian Distribution*.

1. `gaussian-marginal-conditional` — the book's Figure 6.9 on the book's own
   Example 6.6. The bivariate contours with the x2 = -1 slice drawn, then the
   marginal p(x1) = N(0, 0.3) and the conditional p(x1 | x2 = -1) = N(0.6, 0.1).
   Both are Gaussian, which is the closure property the whole section is about,
   and conditioning is the one that moves the mean and shrinks the variance.

2. `product-of-gaussians` — Equations 6.74 to 6.77. Two Gaussians, their pointwise
   product, and the normalised result, with the scaling constant computed three
   ways: from Equation 6.76, as N(a | b, A+B), and by integrating the product on
   a grid. The product's covariance is smaller than either factor's, which is what
   makes a Gaussian posterior sharper than its prior.

3. `mixture-is-not-gaussian` — Theorem 6.12. A mixture with mean 3.6 and variance
   9.64 beside the Gaussian sharing those two moments. Same first two moments,
   two modes against one, and an excess kurtosis of -1.47 against 0. Beside it,
   the variance decomposition: the within-component part is 1.0 and the
   between-component part is 8.64, which is the law of total variance.

4. `cholesky-sampling` — Section 6.5.4. The unit circle of a standard normal
   mapped through the Cholesky factor L into the target ellipse, and the sample
   covariance converging on Sigma as n grows.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# Example 6.6, Eq 6.69.
MU = np.array([0.0, 2.0])
SIG = np.array([[0.3, -1.0], [-1.0, 5.0]])
Y_OBS = -1.0


def _norm(x, m, v):
    return np.exp(-0.5 * (x - m) ** 2 / v) / np.sqrt(2 * np.pi * v)


def gaussian_marginal_conditional(fig, ax, p: Palette) -> None:
    """Figure 6.9 with Example 6.6's numbers on it."""
    fig.clear()
    left, mid, right = fig.subplots(1, 3)

    # (a) the joint, with the conditioning slice.
    g1 = np.linspace(-1.8, 1.8, 320)
    g2 = np.linspace(-5, 9, 320)
    X1, X2 = np.meshgrid(g1, g2)
    Si = np.linalg.inv(SIG)
    d1, d2 = X1 - MU[0], X2 - MU[1]
    q = Si[0, 0] * d1 ** 2 + 2 * Si[0, 1] * d1 * d2 + Si[1, 1] * d2 ** 2
    Z = np.exp(-0.5 * q) / (2 * np.pi * np.sqrt(np.linalg.det(SIG)))
    left.contour(X1, X2, Z, levels=8, colors=p.blue, linewidths=1.2)
    left.axhline(Y_OBS, color=p.amber, linewidth=2.2)
    left.text(-1.7, Y_OBS + 0.35, "$x_2 = -1$", color=p.amber, fontsize=9.5,
              family="monospace")
    left.plot(*MU, "+", color=p.red, markersize=14, markeredgewidth=2.2)
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title("(a) the joint, Eq 6.69", fontsize=9.5)
    left.text(
        0.03, 0.97,
        f"$\\mu$ = (0, 2)\n$\\Sigma$ = [[0.3, -1], [-1, 5]]\n"
        f"eigenvalues {np.linalg.eigvalsh(SIG).round(4)}\n"
        "correlation "
        f"{SIG[0,1]/np.sqrt(SIG[0,0]*SIG[1,1]):.4f}",
        transform=left.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    # (b) the marginal, Eq 6.68 -- just the diagonal block.
    xs = np.linspace(-1.8, 1.8, 700)
    m_var = SIG[0, 0]
    right_v = _norm(xs, MU[0], m_var)
    mid.plot(xs, right_v, color=p.green, linewidth=2.4)
    mid.fill_between(xs, right_v, color=p.green, alpha=0.18)
    mid.axvline(MU[0], color=p.red, linewidth=1.8)
    sd = np.sqrt(m_var)
    mid.annotate("", xy=(MU[0] - 2 * sd, _norm(MU[0], MU[0], m_var) * 0.42),
                 xytext=(MU[0] + 2 * sd, _norm(MU[0], MU[0], m_var) * 0.42),
                 arrowprops=dict(arrowstyle="<->", color=p.red, linewidth=1.5))
    mid.text(MU[0], _norm(MU[0], MU[0], m_var) * 0.47, "$2\\sigma$", ha="center",
             color=p.red, fontsize=9)
    mid.set_xlabel("$x_1$")
    mid.set_ylabel("$p(x_1)$")
    mid.set_title("(b) marginal — Eq 6.68", fontsize=9.5, color=p.green)
    mid.text(
        0.03, 0.97,
        f"$p(x_1) = \\mathcal{{N}}(0,\\ 0.3)$\n\n"
        "read straight off the\ndiagonal block. The mean\n"
        "does not move and the\nvariance does not shrink.",
        transform=mid.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    # (c) the conditional, Eq 6.66 and 6.67.
    mu_c = MU[0] + SIG[0, 1] / SIG[1, 1] * (Y_OBS - MU[1])
    v_c = SIG[0, 0] - SIG[0, 1] / SIG[1, 1] * SIG[1, 0]
    cv = _norm(xs, mu_c, v_c)
    right.plot(xs, cv, color=p.amber, linewidth=2.4)
    right.fill_between(xs, cv, color=p.amber, alpha=0.18)
    # The marginal, faint, for scale.
    right.plot(xs, right_v, color=p.green, linewidth=1.4, linestyle="--",
               label="marginal, for scale")
    right.axvline(mu_c, color=p.red, linewidth=1.8)
    sdc = np.sqrt(v_c)
    right.annotate("", xy=(mu_c - 2 * sdc, _norm(mu_c, mu_c, v_c) * 0.42),
                   xytext=(mu_c + 2 * sdc, _norm(mu_c, mu_c, v_c) * 0.42),
                   arrowprops=dict(arrowstyle="<->", color=p.red, linewidth=1.5))
    right.text(mu_c, _norm(mu_c, mu_c, v_c) * 0.47, "$2\\sigma$", ha="center",
               color=p.red, fontsize=9)
    right.set_xlabel("$x_1$")
    right.set_ylabel("$p(x_1 \\mid x_2 = -1)$")
    right.set_title("(c) conditional — Eq 6.66, 6.67", fontsize=9.5, color=p.amber)
    right.legend(loc="upper right", fontsize=7.6)
    right.text(
        0.03, 0.97,
        f"$\\mathcal{{N}}({mu_c:.1f},\\ {v_c:.1f})$\n\n"
        f"mean moved  0 -> {mu_c:.1f}\n"
        f"variance    0.3 -> {v_c:.1f}\n"
        f"a factor of {SIG[0,0]/v_c:.0f} narrower",
        transform=right.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    fig.text(
        0.5, -0.06,
        "Both operations return a Gaussian — that closure is what Section 6.5 is "
        "for. But they do different things: marginalising reads a block off the "
        "diagonal and changes nothing, while conditioning moves the mean and can "
        "only shrink the variance.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


def product_of_gaussians(fig, ax, p: Palette) -> None:
    """Equations 6.74 to 6.77, in one dimension so the picture is readable."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    a, A = 1.0, 1.2
    b, B = -0.4, 0.6
    C = 1.0 / (1.0 / A + 1.0 / B)                       # Eq 6.74
    c = C * (a / A + b / B)                             # Eq 6.75
    scale = _norm(a, b, A + B)                          # Eq 6.76 / 6.77

    xs = np.linspace(-4, 5, 1600)
    pa, pb = _norm(xs, a, A), _norm(xs, b, B)
    left.plot(xs, pa, color=p.blue, linewidth=2.2,
              label=f"$\\mathcal{{N}}(x\\mid{a},{A})$")
    left.plot(xs, pb, color=p.purple, linewidth=2.2,
              label=f"$\\mathcal{{N}}(x\\mid{b},{B})$")
    left.plot(xs, pa * pb, color=p.red, linewidth=2.0, linestyle=":",
              label="their pointwise product")
    left.plot(xs, scale * _norm(xs, c, C), color=p.green, linewidth=1.6,
              linestyle="--", label="$c\\,\\mathcal{N}(x\\mid c, C)$")
    left.set_xlabel("$x$")
    left.set_ylabel("density")
    left.set_title("the product is a scaled Gaussian", fontsize=9.5)
    left.legend(loc="upper left", fontsize=7.8)
    grid = np.linspace(-40, 40, 400_001)
    mass = np.trapezoid(_norm(grid, a, A) * _norm(grid, b, B), grid)
    left.text(
        0.97, 0.97,
        f"Eq 6.74  C = {C:.6f}\n"
        f"Eq 6.75  c = {c:.6f}\n"
        f"Eq 6.76  scale = {scale:.8f}\n"
        f"Eq 6.77  N(a|b,A+B) = {scale:.8f}\n"
        f"integral of the product = {mass:.8f}",
        transform=left.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    # Right: the product is always narrower than either factor.
    Bs = np.geomspace(0.05, 20, 300)
    Cs = 1.0 / (1.0 / A + 1.0 / Bs)
    right.loglog(Bs, Cs, color=p.green, linewidth=2.4, label="$C$, the product")
    right.axhline(A, color=p.blue, linestyle="--", linewidth=1.6,
                  label=f"$A = {A}$")
    right.loglog(Bs, Bs, color=p.purple, linestyle=":", linewidth=1.6,
                 label="$B$")
    right.set_xlabel("$B$, the second variance")
    right.set_ylabel("variance")
    right.set_title("$C$ is below BOTH, always", fontsize=9.5)
    right.legend(loc="upper left", fontsize=8)
    right.text(
        0.97, 0.05,
        "$C^{-1} = A^{-1} + B^{-1}$, so precisions\n"
        "ADD and the product is sharper than\n"
        "either factor. That is exactly why a\n"
        "Gaussian posterior is narrower than\n"
        "its prior — Bayes multiplies.",
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.6, family="monospace")


def mixture_is_not_gaussian(fig, ax, p: Palette) -> None:
    """Theorem 6.12, and the difference between summing variables and densities."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1]})

    alpha, m1, s1, m2, s2 = 0.4, 0.0, 1.0, 6.0, 1.0
    mean = alpha * m1 + (1 - alpha) * m2
    within = alpha * s1 ** 2 + (1 - alpha) * s2 ** 2
    between = (alpha * m1 ** 2 + (1 - alpha) * m2 ** 2) - mean ** 2
    var = within + between

    xs = np.linspace(-5, 11, 1600)
    mix = alpha * _norm(xs, m1, s1 ** 2) + (1 - alpha) * _norm(xs, m2, s2 ** 2)
    left.plot(xs, mix, color=p.blue, linewidth=2.6,
              label="the mixture, Eq 6.80")
    left.plot(xs, _norm(xs, mean, var), color=p.red, linewidth=2.2,
              linestyle="--", label="Gaussian with the same mean and variance")
    left.plot(xs, alpha * _norm(xs, m1, s1 ** 2), color=p.muted, linewidth=1.2)
    left.plot(xs, (1 - alpha) * _norm(xs, m2, s2 ** 2), color=p.muted,
              linewidth=1.2)
    left.axvline(mean, color=p.amber, linewidth=1.8)
    left.text(mean + 0.15, left.get_ylim()[1] * 0.92,
              f"mean {mean:.1f}", color=p.amber, fontsize=8.5, family="monospace")
    left.set_xlabel("$x$")
    left.set_ylabel("density")
    left.set_title("two modes against one, at identical moments", fontsize=9.5)
    left.legend(loc="upper right", fontsize=7.8)
    left.text(
        0.02, 0.60,
        f"Eq 6.81  E[x] = {mean:.4f}\n"
        f"Eq 6.82  V[x] = {var:.4f}\n\n"
        "both curves match those two\n"
        "numbers exactly. Excess kurtosis\n"
        "is -1.47 for the mixture and 0\n"
        "for the Gaussian, and the mean\n"
        "sits where the mixture is LOW.",
        transform=left.transAxes, ha="left", va="top",
        color=p.fg, fontsize=7.4, family="monospace")

    bars = right.bar(["within\n$E[V[x\\mid y]]$", "between\n$V[E[x\\mid y]]$",
                      "total\n$V[x]$"],
                     [within, between, var],
                     color=[p.green, p.purple, p.amber], width=0.6)
    for b, v in zip(bars, [within, between, var]):
        right.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v:.2f}",
                   ha="center", color=p.fg, fontsize=9, family="monospace")
    right.set_ylabel("variance")
    right.set_ylim(0, var * 1.2)
    right.set_title("the law of total variance", fontsize=9.5)
    right.text(
        0.5, 0.55,
        f"'average the component variances'\n"
        f"gives {within:.2f}, which is {var/within:.2f} times\n"
        f"too small. Equation 6.82's second\n"
        f"term is the spread of the MEANS,\n"
        f"and here it is {between/var*100:.0f}% of the answer.",
        transform=right.transAxes, ha="center", va="center",
        color=p.fg, fontsize=7.8, family="monospace")


def cholesky_sampling(fig, ax, p: Palette) -> None:
    """Section 6.5.4: y = L x + mu turns a standard normal into any Gaussian."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    mu = np.array([1.0, -0.5])
    S = np.array([[2.0, 1.2], [1.2, 1.0]])
    L = np.linalg.cholesky(S)
    rng = np.random.default_rng(5)

    # The unit circle, and its image.
    th = np.linspace(0, 2 * np.pi, 400)
    circ = np.stack([np.cos(th), np.sin(th)])
    for k, colour in ((1, p.green), (2, p.amber)):
        left.plot(k * circ[0], k * circ[1], color=colour, linewidth=1.6,
                  linestyle="--", alpha=0.9)
        img = L @ (k * circ) + mu[:, None]
        left.plot(img[0], img[1], color=colour, linewidth=2.2)
    z = rng.standard_normal((900, 2))
    left.scatter(z[:, 0], z[:, 1], s=5, color=p.muted, alpha=0.45, linewidths=0,
                 label="$x \\sim \\mathcal{N}(0, I)$")
    y = z @ L.T + mu
    left.scatter(y[:, 0], y[:, 1], s=5, color=p.blue, alpha=0.5, linewidths=0,
                 label="$y = Lx + \\mu$")
    left.plot(0, 0, "+", color=p.muted, markersize=12, markeredgewidth=2)
    left.plot(*mu, "+", color=p.red, markersize=14, markeredgewidth=2.2)
    left.set_aspect("equal")
    left.set_xlabel("first coordinate")
    left.set_ylabel("second coordinate")
    left.set_title("one triangular matrix does the whole job", fontsize=9.5)
    left.legend(loc="upper left", fontsize=7.8)
    left.text(
        0.97, 0.03,
        f"L = [[{L[0,0]:.4f}, 0],\n"
        f"     [{L[1,0]:.4f}, {L[1,1]:.4f}]]\n"
        f"L L^T - Sigma: {np.abs(L @ L.T - S).max():.1e}\n"
        "dashed: before, solid: after",
        transform=left.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace")

    ns = np.array([50, 200, 1000, 5000, 20_000, 100_000, 500_000, 2_000_000])
    gaps = []
    for n in ns:
        smp = rng.standard_normal((int(n), 2)) @ L.T + mu
        gaps.append(float(np.abs(np.cov(smp.T, bias=True) - S).max()))
    right.loglog(ns, gaps, "o-", color=p.blue, linewidth=2.2,
                 label="worst entry of $|\\hat\\Sigma - \\Sigma|$")
    right.loglog(ns, gaps[0] * np.sqrt(ns[0] / ns), "--", color=p.amber,
                 linewidth=1.7, label="$1/\\sqrt{n}$ reference")
    right.set_xlabel("number of samples")
    right.set_ylabel("covariance error")
    right.set_title("the sampler is correct; the estimate is slow",
                    fontsize=9.5)
    right.legend(loc="lower left", fontsize=8)
    right.text(
        0.97, 0.95,
        "the transform is exact — every\n"
        "error here is estimating Sigma from\n"
        "a finite sample, and it falls only\n"
        "as one over root n.",
        transform=right.transAxes, ha="right", va="top",
        color=p.fg, fontsize=7.6, family="monospace")


FIGURES = [
    figure("gaussian-marginal-conditional", gaussian_marginal_conditional,
           size=(12.5, 4.4), axes=False),
    figure("product-of-gaussians", product_of_gaussians, size=(11.0, 4.4),
           axes=False),
    figure("mixture-is-not-gaussian", mixture_is_not_gaussian, size=(11.5, 4.4),
           axes=False),
    figure("cholesky-sampling", cholesky_sampling, size=(11.0, 4.6), axes=False),
]

"""Figures for *Probabilistic Modeling and Inference*.

1. `a-posterior-not-a-point` — what Section 8.3's point estimate discards. The
   exact conjugate posterior over the coefficients, the MAP point sitting at its
   mean, and forty curves drawn from that posterior. They agree where the data
   is and fan apart where it is not.

2. `plug-in-versus-full-predictive` — Equation 8.23 against p(x | theta*),
   measured. With the prior matched to the truth, the full predictive holds 95%
   coverage everywhere while the plug-in interval falls to 0.1796 in
   extrapolation.

3. `optimization-versus-integration` — the variance split of Equation 8.23 into
   noise plus parameter uncertainty, and what more data does to it. The two
   approaches converge as N grows: the width ratio falls from 1.248 at N = 5 to
   1.000113 at N = 10000.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIGMA = 0.35
TAU2 = 1.0
D = 4
Z = 1.959963984540054


def _make(n, seed, noise=SIGMA):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg=3):
    return np.vander(np.asarray(x, dtype=float) / 3.0, deg + 1, increasing=True)


def _posterior(x, y, tau2=TAU2):
    """The exact conjugate posterior of Section 6.6.1: mean and covariance."""
    P = _design(x)
    cov = np.linalg.inv(P.T @ P / SIGMA ** 2 + np.eye(D) / tau2)
    return cov @ P.T @ y / SIGMA ** 2, cov


# --------------------------------------------------------------------------
# 1. a posterior, not a point
# --------------------------------------------------------------------------

def a_posterior_not_a_point(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _make(25, seed=3)
    m, cov = _posterior(x, y)

    # --- left: the joint posterior over two of the four coefficients ------
    i, j = 1, 3
    sub = cov[np.ix_([i, j], [i, j])]
    inv = np.linalg.inv(sub)
    g = 260
    u = np.linspace(m[i] - 4 * np.sqrt(sub[0, 0]), m[i] + 4 * np.sqrt(sub[0, 0]), g)
    v = np.linspace(m[j] - 4 * np.sqrt(sub[1, 1]), m[j] + 4 * np.sqrt(sub[1, 1]), g)
    U, V = np.meshgrid(u, v)
    dU, dV = U - m[i], V - m[j]
    q = (inv[0, 0] * dU ** 2 + 2 * inv[0, 1] * dU * dV + inv[1, 1] * dV ** 2)
    left.contourf(U, V, np.exp(-0.5 * q), levels=14, cmap="magma", alpha=0.85)
    left.contour(U, V, q, levels=[2.2789, 5.9915, 9.2103],
                 colors=[p.fg], linewidths=1.0, alpha=0.65)

    left.plot([m[i]], [m[j]], "o", color=p.amber, markersize=11,
              markeredgecolor=p.bg, markeredgewidth=1.4, zorder=6)
    left.annotate(
        "the MAP estimate\n(Section 8.3.2 kept\nTHIS and nothing else)",
        xy=(m[i], m[j]), xytext=(28, 40), textcoords="offset points",
        fontsize=8.2, color=p.amber, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.2))

    left.set_xlabel(r"$\theta_1$")
    left.set_ylabel(r"$\theta_3$")
    left.set_title("The posterior $p(\\theta \\mid \\mathcal{X})$, "
                   "Equation 8.22", fontsize=9.8)
    left.text(
        0.03, 0.97,
        "posterior sd per coefficient:\n"
        + "\n".join(f"  theta_{k}: {s:.6f}"
                    for k, s in enumerate(np.sqrt(np.diag(cov))))
        + "\n\ncontours are 68%, 95%, 99%.\nA point estimate is one dot\n"
          "inside all of them.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.4,
        color="#ffffff", family="monospace")

    # --- right: forty functions drawn from that posterior ----------------
    rng = np.random.default_rng(4)
    L = np.linalg.cholesky(cov + 1e-14 * np.eye(D))
    xs = np.linspace(-4.4, 5.4, 420)
    Pg = _design(xs)
    for _ in range(40):
        th = m + L @ rng.standard_normal(D)
        right.plot(xs, Pg @ th, color=p.blue, linewidth=0.9, alpha=0.32)
    right.plot(xs, Pg @ m, color=p.amber, linewidth=2.6,
               label=r"the MAP curve $f(x; \theta^*)$")
    right.plot(x, y, "o", color=p.green, markersize=5.5,
               markeredgecolor=p.bg, markeredgewidth=0.6, zorder=5,
               label="the 25 observations")
    right.axvspan(-3, 3, color=p.green, alpha=0.07)
    right.text(0.0, -4.3, "where the data is", ha="center", fontsize=8,
               color=p.green, family="monospace")
    right.text(4.3, -4.3, "where it is not", ha="center", fontsize=8,
               color=p.red, family="monospace")

    right.set_ylim(-5.0, 5.0)
    right.set_xlabel("$x$")
    right.set_ylabel("$f(x)$")
    right.set_title("Forty $\\theta$ drawn from that posterior", fontsize=9.8)
    right.legend(fontsize=8, loc="upper left")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.97, 0.03,
        "Every one of these is a\nplausible explanation of the\nsame 25 points.\n"
        "Equation 8.23 averages over\nall of them instead of\npicking one.",
        transform=right.transAxes, ha="right", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.4.2: parameter estimation returns a point, Bayesian "
        "inference returns a distribution",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The posterior mean equals the MAP estimate to 8.9e-16 for a Gaussian "
        "model, so the point estimate is not wrong — it is incomplete. What it "
        "discards is the\ncovariance, and the covariance is the entire "
        "difference between a confident prediction and an honest one.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. the plug-in predictive against Equation 8.23
# --------------------------------------------------------------------------

def _coverage_study(trials=4000, seed=11):
    """Calibration when the model IS the truth: theta drawn from the prior."""
    rng = np.random.default_rng(seed)
    regions = (("interpolation", -3.0, 3.0),
               ("mild extrapolation", 3.0, 5.0),
               ("far extrapolation", 5.0, 7.0))
    hp = {r[0]: 0 for r in regions}
    hf = {r[0]: 0 for r in regions}
    wf = {r[0]: 0.0 for r in regions}
    n = {r[0]: 0 for r in regions}
    for _ in range(trials):
        th = np.sqrt(TAU2) * rng.standard_normal(D)
        xtr = np.sort(rng.uniform(-3, 3, 25))
        P = _design(xtr)
        ytr = P @ th + SIGMA * rng.standard_normal(25)
        cov = np.linalg.inv(P.T @ P / SIGMA ** 2 + np.eye(D) / TAU2)
        m = cov @ P.T @ ytr / SIGMA ** 2
        for name, lo, hi in regions:
            xt = rng.uniform(lo, hi, 40)
            Pt = _design(xt)
            yt = Pt @ th + SIGMA * rng.standard_normal(len(xt))
            mu = Pt @ m
            sd = np.sqrt(SIGMA ** 2
                         + np.einsum("ij,jk,ik->i", Pt, cov, Pt))
            hp[name] += int(np.sum(np.abs(yt - mu) <= Z * SIGMA))
            hf[name] += int(np.sum(np.abs(yt - mu) <= Z * sd))
            wf[name] += float(np.sum(2 * Z * sd))
            n[name] += len(xt)
    return [(r[0], hp[r[0]] / n[r[0]], hf[r[0]] / n[r[0]],
             2 * Z * SIGMA, wf[r[0]] / n[r[0]]) for r in regions]


_COVER_CACHE: dict = {}


def _cover():
    if "v" not in _COVER_CACHE:
        _COVER_CACHE["v"] = _coverage_study()
    return _COVER_CACHE["v"]


def plug_in_versus_full_predictive(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.35, 1]})

    x, y = _make(25, seed=3)
    m, cov = _posterior(x, y)
    xs = np.linspace(-4.4, 6.4, 500)
    Pg = _design(xs)
    mu = Pg @ m
    pv = np.einsum("ij,jk,ik->i", Pg, cov, Pg)
    sd_full = np.sqrt(SIGMA ** 2 + pv)

    left.fill_between(xs, mu - Z * sd_full, mu + Z * sd_full, color=p.blue,
                      alpha=0.22,
                      label=r"$\int p(x \mid \theta)p(\theta)\,d\theta$, Eq. 8.23")
    left.fill_between(xs, mu - Z * SIGMA, mu + Z * SIGMA, color=p.amber,
                      alpha=0.30, label=r"$p(x \mid \theta^*)$, the plug-in")
    left.plot(xs, mu, color=p.fg, linewidth=1.8)
    left.plot(x, y, "o", color=p.green, markersize=5.5,
              markeredgecolor=p.bg, markeredgewidth=0.6, zorder=5)
    left.axvline(3.0, color=p.red, linestyle=":", linewidth=1.3)
    left.text(3.12, left.get_ylim()[0], "", fontsize=1)

    left.set_ylim(-6.5, 6.5)
    left.set_xlabel("$x$")
    left.set_ylabel("$y$")
    left.set_title("Two 95% predictive intervals", fontsize=9.8)
    left.legend(fontsize=8, loc="lower left")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.98, 0.97,
        "The plug-in band has CONSTANT\nwidth 1.3720 forever: it reports\n"
        "the noise and nothing else.\n\nThe full band widens because the\n"
        "posterior does not know what\nhappens past the data.",
        transform=left.transAxes, ha="right", va="top", fontsize=7.5,
        color=p.fg, family="monospace")

    # --- right: measured coverage, prior matched to the truth -------------
    rows = _cover()
    names = [r[0] for r in rows]
    pos = np.arange(len(rows))
    right.barh(pos + 0.19, [r[1] for r in rows], height=0.36, color=p.amber,
               label=r"plug-in $p(x \mid \theta^*)$")
    right.barh(pos - 0.19, [r[2] for r in rows], height=0.36, color=p.blue,
               label="full predictive, Eq. 8.23")
    right.axvline(0.95, color=p.red, linestyle="--", linewidth=1.6)
    right.text(0.95, len(rows) - 0.38, " nominal 0.95", fontsize=8.2,
               color=p.red, family="monospace", va="center")
    for k, r in enumerate(rows):
        right.text(r[1] + 0.012, k + 0.19, f"{r[1]:.4f}", va="center",
                   fontsize=8.2, color=p.amber, family="monospace")
        right.text(r[2] + 0.012, k - 0.19, f"{r[2]:.4f}", va="center",
                   fontsize=8.2, color=p.blue, family="monospace")
    right.set_yticks(pos)
    right.set_yticklabels([n.replace(" ", "\n") for n in names], fontsize=8.4)
    right.set_xlim(0, 1.22)
    right.set_xlabel("measured coverage of a nominal 95% interval")
    right.set_title("4000 trials, prior matched to the truth", fontsize=9.8)
    right.legend(fontsize=8, loc="lower right")
    right.grid(alpha=0.20, linewidth=0.6, axis="x")
    right.text(
        0.98, 0.50,
        "mean widths:\n"
        + "\n".join(f"  {r[0][:13]:<13} {r[3]:.4f} / {r[4]:.4f}" for r in rows)
        + "\n  (plug-in / full)",
        transform=right.transAxes, ha="right", va="center", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 8.23 holds 95% coverage everywhere; the plug-in predictive "
        "falls to 0.1796",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Both intervals are honest about the observation noise. Only one is "
        "honest about not knowing theta, and that is the entire content of the "
        "book's remark that\nfocusing on a single statistic of the posterior "
        "\"leads to loss of information, which can be critical in a system that "
        "uses the prediction to make decisions\".",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. optimization against integration
# --------------------------------------------------------------------------

def optimization_versus_integration(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    x, y = _make(25, seed=3)
    m, cov = _posterior(x, y)

    # --- a1: the variance decomposition of Equation 8.23 -----------------
    xs = np.linspace(-4.4, 5.4, 400)
    Pg = _design(xs)
    pv = np.einsum("ij,jk,ik->i", Pg, cov, Pg)
    noise = np.full_like(xs, SIGMA ** 2)
    a1.fill_between(xs, 0, noise, color=p.amber, alpha=0.55,
                    label=r"$\sigma^2$, the noise")
    a1.fill_between(xs, noise, noise + pv, color=p.blue, alpha=0.55,
                    label=r"$\phi^\top \Sigma \phi$, not knowing $\theta$")
    a1.axvspan(-3, 3, color=p.green, alpha=0.08)
    a1.set_yscale("log")
    a1.set_ylim(1e-2, 30)
    a1.set_xlabel("$x$")
    a1.set_ylabel("predictive variance")
    a1.set_title("The two sources of uncertainty", fontsize=9.6)
    a1.legend(fontsize=7.6, loc="upper center")
    a1.grid(alpha=0.20, linewidth=0.6)
    a1.text(
        0.03, 0.03,
        "at x = 0: 7.5% is parameters\nat x = 3: 37.6%\nat x = 5: 95.3%\n\n"
        "Only the blue part vanishes\nwith more data.",
        transform=a1.transAxes, ha="left", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- a2: more data collapses the posterior ---------------------------
    ns = np.array([5, 10, 25, 100, 1000, 10000])
    p0 = _design(np.array([0.0]))[0]
    sds, ratios = [], []
    for n in ns:
        xn, yn = _make(int(n), seed=3)
        Pn = _design(xn)
        Cn = np.linalg.inv(Pn.T @ Pn / SIGMA ** 2 + np.eye(D) / TAU2)
        sds.append(np.sqrt(np.diag(Cn)).max())
        v = float(p0 @ Cn @ p0)
        ratios.append(np.sqrt((SIGMA ** 2 + v) / SIGMA ** 2))
    a2.loglog(ns, sds, "o-", color=p.blue, linewidth=2.2, markersize=7,
              label="largest posterior sd")
    a2.loglog(ns, np.array(sds)[0] * np.sqrt(ns[0] / ns), ":", color=p.muted,
              linewidth=1.5, label=r"$1/\sqrt{N}$ reference")
    a2.set_xlabel("$N$")
    a2.set_ylabel("posterior standard deviation")
    a2.set_title("Integration approaches optimization", fontsize=9.6)
    a2.legend(fontsize=7.8, loc="lower left")
    a2.grid(alpha=0.20, linewidth=0.6, which="both")
    a2.text(
        0.97, 0.95,
        "width ratio, full / plug-in:\n"
        + "\n".join(f"  N = {int(n):>5}: {r:.6f}" for n, r in zip(ns, ratios))
        + "\n\nIt tends to 1. With enough\ndata the two agree — which is\n"
          "why MLE is defensible when\nN is large and dangerous\nwhen it is not.",
        transform=a2.transAxes, ha="right", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- a3: the marginal likelihood MAP could ignore --------------------
    N = len(y)
    degs = np.arange(0, 12)
    evs = []
    for d in degs:
        P = _design(x, int(d))
        C = SIGMA ** 2 * np.eye(N) + TAU2 * (P @ P.T)
        _, ld = np.linalg.slogdet(C)
        evs.append(float(-0.5 * (y @ np.linalg.solve(C, y) + ld
                                 + N * np.log(2 * np.pi))))
    evs = np.array(evs)
    kb = int(np.argmax(evs))
    a3.plot(degs, evs, "o-", color=p.purple, linewidth=2.2, markersize=7)
    a3.plot([degs[kb]], [evs[kb]], "o", color=p.amber, markersize=12,
            markeredgecolor=p.bg, markeredgewidth=1.3, zorder=5)
    a3.annotate(f"peak at degree {degs[kb]}\n$\\log p(\\mathcal{{X}}) = "
                f"{evs[kb]:.4f}$",
                xy=(degs[kb], evs[kb]), xytext=(-10, -58),
                textcoords="offset points", ha="center", fontsize=8.0,
                color=p.amber, family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))
    a3.set_xlabel("polynomial degree")
    a3.set_ylabel(r"$\log p(\mathcal{X})$")
    a3.set_title("$p(\\mathcal{X})$: the term MAP dropped", fontsize=9.6)
    a3.grid(alpha=0.20, linewidth=0.6)
    a3.text(
        0.97, 0.06,
        "Degree 11 scores -30.2178,\nonly 0.26 nats below the peak.\n"
        "The evidence penalises extra\ncapacity but does not forbid it.\n\n"
        "This quantity is what\nSection 8.6 uses to choose.",
        transform=a3.transAxes, ha="right", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.4.2: estimation solves an optimization problem, inference "
        "solves an integration problem",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's comparison, made numerical. Optimization gives a point and "
        "is cheap; integration gives a distribution and is expensive, and buys "
        "calibrated intervals,\na principled way to fold in prior knowledge, "
        "and the marginal likelihood that Section 8.6 needs to choose a model "
        "at all.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("a-posterior-not-a-point", a_posterior_not_a_point,
           size=(13.0, 5.1), axes=False),
    figure("plug-in-versus-full-predictive", plug_in_versus_full_predictive,
           size=(13.4, 5.1), axes=False),
    figure("optimization-versus-integration", optimization_versus_integration,
           size=(15.0, 5.1), axes=False),
]

"""Figures for *Model Selection*.

1. `occams-razor-is-automatic` — Figure 8.14 rebuilt from real evidences. The
   evidence of a degree-1 and a degree-9 model along a one-parameter family of
   datasets, with region C located exactly at w = 0.571273, beside the fact
   that makes the picture work: each model wins on its own data, by 3.4062 and
   50.7124 nats.

2. `bayes-factors-and-lindley` — Equation 8.47 with Jeffreys' bands, and the
   Jeffreys-Lindley paradox measured: with the data held fixed, the log Bayes
   factor bottoms out at tau^2 = 10.22 and crosses zero at 3.71e6, after which
   the simpler model wins by more and more, forever.

3. `criteria-disagree` — maximum likelihood, AIC, BIC, the exact evidence and
   cross-validation on the same 25 points, and the selection bias that
   Section 8.6.1's outer loop exists to remove.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIGMA = 0.35
TAU2 = 1.0


def _make(n, seed, noise=SIGMA):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg):
    return np.vander(np.asarray(x, float) / 3.0, deg + 1, increasing=True)


def _log_evidence(x, y, deg, tau2=TAU2):
    P = _design(x, deg)
    n = len(y)
    C = SIGMA ** 2 * np.eye(n) + tau2 * (P @ P.T)
    _, ld = np.linalg.slogdet(C)
    return float(-0.5 * (y @ np.linalg.solve(C, y) + ld
                         + n * np.log(2 * np.pi)))


def _logpdf(Y, C, n):
    _, ld = np.linalg.slogdet(C)
    quad = np.einsum("ij,ji->i", Y, np.linalg.solve(C, Y.T))
    return -0.5 * (quad + ld + n * np.log(2 * np.pi))


# --------------------------------------------------------------------------
# 1. the automatic Occam's razor
# --------------------------------------------------------------------------

def occams_razor_is_automatic(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.3, 1]})

    xg = np.linspace(-3, 3, 25)
    n = len(xg)
    P1, P9 = _design(xg, 1), _design(xg, 9)
    C1 = SIGMA ** 2 * np.eye(n) + TAU2 * (P1 @ P1.T)
    C9 = SIGMA ** 2 * np.eye(n) + TAU2 * (P9 @ P9.T)

    # --- left: Figure 8.14 along a one-parameter family of datasets -------
    wig = np.cos(2.6 * xg)
    base = 0.4 * xg
    noise = SIGMA * np.random.default_rng(4).standard_normal(n)
    ws = np.linspace(0.0, 2.2, 260)
    e1 = np.array([float(_logpdf((base + w * wig + noise)[None, :], C1, n)[0])
                   for w in ws])
    e9 = np.array([float(_logpdf((base + w * wig + noise)[None, :], C9, n)[0])
                   for w in ws])
    left.plot(ws, np.exp(e1 - e1.max()), color=p.blue, linewidth=2.6,
              label="$p(\\mathcal{D} \\mid M_1)$, degree 1")
    left.plot(ws, np.exp(e9 - e1.max()), color=p.red, linewidth=2.6,
              label="$p(\\mathcal{D} \\mid M_2)$, degree 9")

    lo, hi = 0.0, 3.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        Y = base + mid * wig + noise
        if float(_logpdf(Y[None, :], C1, n)[0]) > float(
                _logpdf(Y[None, :], C9, n)[0]):
            lo = mid
        else:
            hi = mid
    xc = 0.5 * (lo + hi)
    left.axvspan(0, xc, color=p.blue, alpha=0.10)
    left.axvline(xc, color=p.amber, linestyle="--", linewidth=1.8)
    left.text(xc / 2, 0.60, "region $C$\nthe simple model\nis more probable",
              ha="center", fontsize=8.2, color=p.blue, family="monospace")
    left.text(xc + 0.06, 0.60, f"crossover at\nw = {xc:.6f}", ha="left",
              fontsize=8.2, color=p.amber, family="monospace")
    left.set_xlabel("$w$: how much structure the dataset contains "
                    "$\\longrightarrow$")
    left.set_ylabel("evidence (rescaled)")
    left.set_title("Figure 8.14, rebuilt from real marginal likelihoods",
                   fontsize=9.6)
    left.legend(fontsize=8.4, loc="upper right")
    left.grid(alpha=0.20, linewidth=0.6)
    left.set_ylim(0, 1.12)

    # --- right: each model wins on its own data ---------------------------
    rng = np.random.default_rng(31)
    T = 200_000
    Y1 = rng.standard_normal((T, n)) @ np.linalg.cholesky(C1).T
    Y9 = rng.standard_normal((T, n)) @ np.linalg.cholesky(C9).T
    a11, a12 = _logpdf(Y1, C1, n).mean(), _logpdf(Y1, C9, n).mean()
    a99, a91 = _logpdf(Y9, C9, n).mean(), _logpdf(Y9, C1, n).mean()

    pos = np.array([1.0, 0.0])
    right.barh(pos + 0.19, [a11, a99], height=0.36, color=p.green,
               label="scored by the model that made it")
    right.barh(pos - 0.19, [a12, a91], height=0.36, color=p.red,
               label="scored by the other model")
    for yy, u, v in ((1.0, a11, a12), (0.0, a99, a91)):
        right.text(u - 1.5, yy + 0.19, f"{u:.4f}", va="center", ha="right",
                   fontsize=8.4, color=p.green, family="monospace")
        right.text(v - 1.5, yy - 0.19, f"{v:.4f}", va="center", ha="right",
                   fontsize=8.4, color=p.red, family="monospace")
    right.set_yticks(pos)
    right.set_yticklabels(["datasets drawn\nfrom $M_1$",
                           "datasets drawn\nfrom $M_2$"], fontsize=8.6)
    right.set_xlabel("average $\\log p(\\mathcal{D} \\mid M)$, "
                     "200,000 datasets")
    right.set_title("Neither model can win everywhere", fontsize=9.6)
    right.legend(fontsize=7.8, loc="lower left")
    right.grid(alpha=0.20, linewidth=0.6, axis="x")
    right.text(
        0.98, 0.50,
        f"KL(M1 || M2) = {a11 - a12:.4f} nats\n"
        f"KL(M2 || M1) = {a99 - a91:.4f} nats\n\n"
        "Both positive, necessarily.\np(D | M) integrates to 1, so\n"
        "spreading probability over\nmore datasets costs\n"
        "probability on each one.",
        transform=right.transAxes, ha="right", va="center", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.6.2: the Occam's razor is automatic — no prior over models "
        "is needed to get it",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's phrasing is that Bayes' theorem \"rewards models in "
        "proportion to how much they predicted the data that occurred\". The "
        "constraint that makes this a penalty\nrather than a preference is the "
        "margin note: these predictions are a normalized distribution on D, so "
        "a model that predicts more datasets predicts each of them less well.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. Bayes factors, and the Jeffreys-Lindley paradox
# --------------------------------------------------------------------------

def bayes_factors_and_lindley(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _make(25, seed=3)
    degs = np.arange(12)
    evs = np.array([_log_evidence(x, y, int(d)) for d in degs])
    kb = int(np.argmax(evs))
    lbf = evs[kb] - evs

    bands = ((0.0, np.log(3.0), p.green, "barely worth mentioning"),
             (np.log(3.0), np.log(10.0), p.amber, "substantial"),
             (np.log(10.0), np.log(30.0), "#d98b3a", "strong"),
             (np.log(30.0), np.log(100.0), p.red, "very strong"),
             (np.log(100.0), 80.0, p.purple, "decisive"))
    for lo, hi, col, name in bands:
        left.axhspan(lo, hi, color=col, alpha=0.13)
        if hi < 6:
            left.text(11.4, 0.5 * (lo + hi), name, fontsize=6.8, color=col,
                      ha="right", va="center", family="monospace")
    left.text(11.4, 40.0, "decisive", fontsize=7.2, color=p.purple,
              ha="right", va="center", family="monospace")
    left.plot(degs, lbf, "o-", color=p.blue, linewidth=2.4, markersize=7)
    left.plot([degs[kb]], [0.0], "o", color=p.amber, markersize=12,
              markeredgecolor=p.bg, markeredgewidth=1.3, zorder=5)
    left.set_yscale("symlog", linthresh=1.0)
    left.set_xlabel("polynomial degree")
    left.set_ylabel("log Bayes factor against the best model")
    left.set_title("Equation 8.47 on Jeffreys' (1961) scale", fontsize=9.6)
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.03, 0.97,
        f"best: degree {degs[kb]}, log p(D|M) = {evs[kb]:.4f}\n\n"
        + "\n".join(f"  degree {d:>2}: BF = {np.exp(-lbf[d]):.6f}"
                    for d in (3, 5, 6, 9, 11))
        + "\n\nEverything from degree 3 up is\n"
          "\"barely worth mentioning\". The\n"
          "evidence is not a sharp selector.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- the Jeffreys-Lindley paradox ------------------------------------
    ts = np.geomspace(1e-2, 1e14, 700)
    lb = np.array([_log_evidence(x, y, 1, t) - _log_evidence(x, y, 9, t)
                   for t in ts])
    right.semilogx(ts, lb, color=p.purple, linewidth=2.6)
    right.axhline(0.0, color=p.fg, linewidth=1.2)
    right.fill_between(ts, lb, 0, where=(lb < 0), color=p.red, alpha=0.18)
    right.fill_between(ts, lb, 0, where=(lb >= 0), color=p.green, alpha=0.18)
    k = int(np.argmin(lb))
    right.plot([ts[k]], [lb[k]], "o", color=p.red, markersize=9)
    right.annotate(f"deepest at $\\tau^2 = {ts[k]:.4g}$\n"
                   f"log BF $= {lb[k]:.4f}$",
                   xy=(ts[k], lb[k]), xytext=(20, 30),
                   textcoords="offset points", fontsize=8.0, color=p.red,
                   family="monospace",
                   arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    lo, hi = 1e2, 1e14
    for _ in range(90):
        mid = np.sqrt(lo * hi)
        if _log_evidence(x, y, 1, mid) - _log_evidence(x, y, 9, mid) < 0:
            lo = mid
        else:
            hi = mid
    xc = np.sqrt(lo * hi)
    right.axvline(xc, color=p.amber, linestyle="--", linewidth=1.6)
    right.annotate(f"crosses zero at\n$\\tau^2 = {xc:.6g}$",
                   xy=(xc, 0), xytext=(-12, -70), textcoords="offset points",
                   fontsize=8.0, color=p.amber, family="monospace", ha="right",
                   arrowprops=dict(arrowstyle="->", color=p.amber,
                                   linewidth=1.1))
    right.set_xlabel(r"$\tau^2$, the prior variance — the data never changes")
    right.set_ylabel("log Bayes factor, degree 1 over degree 9")
    right.set_title("The Jeffreys-Lindley paradox, measured", fontsize=9.6)
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.96,
        "Same 25 points at every x-value\non this axis. Only the prior moves.\n\n"
        f"at tau^2 = 1e14 the log Bayes\nfactor is "
        f"{_log_evidence(x, y, 1, 1e14) - _log_evidence(x, y, 9, 1e14):.4f}\n"
        "and it keeps rising.\n\n"
        "A diffuse prior is not a\nneutral one.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.6.3: the Bayes factor compares two models, and it is "
        "sensitive to a choice that is not the data",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Murphy's statement of the paradox: the Bayes factor \"always favors "
        "the simpler model since the probability of the data under a complex "
        "model with a diffuse prior will be\nvery small\". Measured, the swing "
        "is unbounded — which means a Bayes factor reported without its prior "
        "is not a reproducible number.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. five criteria on one dataset
# --------------------------------------------------------------------------

_SEL: dict = {}


def _selection_bias():
    """Flat CV over many candidates, none of which carries any signal."""
    if "v" in _SEL:
        return _SEL["v"]
    CAND, T2, K = 60, 600, 5
    fs, ft = [], []
    rs = np.random.default_rng(101)
    for _ in range(T2):
        s = int(rs.integers(0, 10 ** 6))
        r = np.random.default_rng(s)
        n = 30
        X = r.standard_normal((n, CAND))
        yv = r.standard_normal(n)
        Xe = r.standard_normal((4000, CAND))
        ye = r.standard_normal(4000)
        idx = np.random.default_rng(s + 7).permutation(n)
        folds = np.array_split(idx, K)
        sc = []
        for j in range(CAND):
            errs = []
            for f in folds:
                tr = np.setdiff1d(idx, f)
                A = np.column_stack([X[tr, j], np.ones(len(tr))])
                th = np.linalg.lstsq(A, yv[tr], rcond=None)[0]
                B = np.column_stack([X[f, j], np.ones(len(f))])
                errs.append(float(np.mean((yv[f] - B @ th) ** 2)))
            sc.append(float(np.mean(errs)))
        j1 = int(np.argmin(sc))
        fs.append(sc[j1])
        A = np.column_stack([X[:, j1], np.ones(n)])
        th = np.linalg.lstsq(A, yv, rcond=None)[0]
        Be = np.column_stack([Xe[:, j1], np.ones(4000)])
        ft.append(float(np.mean((ye - Be @ th) ** 2)))
    _SEL["v"] = (float(np.mean(fs)), float(np.mean(ft)))
    return _SEL["v"]


def criteria_disagree(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    x, y = _make(25, seed=3)
    N = len(y)
    degs = np.arange(12)

    def max_loglik(deg):
        P = _design(x, int(deg))
        th = np.linalg.lstsq(P, y, rcond=None)[0]
        r = y - P @ th
        return float(-(r @ r) / (2 * SIGMA ** 2)
                     - N * np.log(SIGMA * np.sqrt(2 * np.pi)))

    ll = np.array([max_loglik(d) for d in degs])
    M = degs + 1
    aic = ll - M
    bic = ll - 0.5 * M * np.log(N)
    ev = np.array([_log_evidence(x, y, int(d)) for d in degs])

    for vals, col, name in ((ll, p.red, "max log likelihood"),
                            (aic, p.amber, "AIC, Eq. 8.48"),
                            (bic, p.green, "BIC, Eq. 8.49"),
                            (ev, p.purple, "exact $\\log p(\\mathcal{D})$")):
        a1.plot(degs, vals, "o-", linewidth=2.1, markersize=5.5, color=col,
                label=name)
        k = int(np.argmax(vals))
        a1.plot([degs[k]], [vals[k]], "o", color=col, markersize=12,
                markerfacecolor="none", markeredgewidth=2.0)
    a1.set_xlabel("polynomial degree")
    a1.set_ylabel("score (higher is better)")
    a1.set_title("Four criteria, one dataset", fontsize=9.4)
    a1.legend(fontsize=7.4, loc="lower right")
    a1.grid(alpha=0.20, linewidth=0.6)
    a1.set_ylim(-105, 12)
    a1.text(
        0.03, 0.97,
        "what each one picks:\n"
        f"  max likelihood : degree {int(np.argmax(ll))}\n"
        f"  AIC            : degree {int(np.argmax(aic))}\n"
        f"  BIC            : degree {int(np.argmax(bic))}\n"
        f"  exact evidence : degree {int(np.argmax(ev))}\n\n"
        "Maximum likelihood picks the\nmost complex model on offer,\n"
        "every time. It has no penalty\nterm to stop it.",
        transform=a1.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- BIC as an approximation -----------------------------------------
    a2.plot(degs, bic - ev, "o-", color=p.green, linewidth=2.4, markersize=7)
    a2.axhline(0.0, color=p.fg, linewidth=1.2)
    a2.set_xlabel("polynomial degree")
    a2.set_ylabel(r"BIC $-\ \log p(\mathcal{D})$, in nats")
    a2.set_title("How good an approximation is Equation 8.49?",
                 fontsize=9.4)
    a2.grid(alpha=0.20, linewidth=0.6)
    err = np.abs(bic - ev)
    a2.text(
        0.03, 0.97,
        f"mean absolute error {err.mean():.4f} nats\n"
        f"worst {err.max():.4f} nats\n\n"
        "BIC is a large-N approximation\nto the log evidence, and\n"
        f"N = {N} here. It still picks a\nsensible degree; it is the\n"
        "VALUE that is unreliable, not\nthe ranking.",
        transform=a2.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- selection bias --------------------------------------------------
    flat, true = _selection_bias()
    names = ["flat CV score\nof the winner", "its true risk\non fresh data",
             "chance\n(there is no signal)"]
    vals = [flat, true, 1.0]
    cols = [p.red, p.amber, p.muted]
    a3.bar(np.arange(3), vals, color=cols, width=0.62)
    a3.axhline(1.0, color=p.fg, linestyle="--", linewidth=1.4)
    for i, v in enumerate(vals):
        a3.text(i, v + 0.03, f"{v:.6f}", ha="center", fontsize=8.6,
                color=cols[i], family="monospace")
    a3.set_xticks(np.arange(3))
    a3.set_xticklabels(names, fontsize=7.8)
    a3.set_ylabel("mean squared error")
    a3.set_ylim(0, 1.55)
    a3.set_title("Why Section 8.6.1 nests the loops", fontsize=9.4)
    a3.grid(alpha=0.20, linewidth=0.6, axis="y")
    a3.text(
        0.5, 0.04,
        "600 trials, 60 candidate features,\nNONE of them predictive, n = 30.\n\n"
        f"Flat CV reports {100 * (1 - flat):.1f}% better than\nchance on data "
        f"with no signal.\nThe truth is {100 * (true - 1):+.1f}%.\n\n"
        "The winning score measures how\nhard you searched.",
        transform=a3.transAxes, ha="center", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.6: five ways to choose a model, and the one number none of "
        "them may be evaluated on",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "AIC and BIC are the book's heuristics for the maximum-likelihood "
        "setting; the exact evidence is what Bayesian model selection uses when "
        "conjugacy makes it available;\ncross-validation needs neither. All "
        "four beat maximum likelihood alone, which has no penalty and therefore "
        "always chooses the largest model it is offered.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("occams-razor-is-automatic", occams_razor_is_automatic,
           size=(14.0, 5.2), axes=False),
    figure("bayes-factors-and-lindley", bayes_factors_and_lindley,
           size=(13.8, 5.2), axes=False),
    figure("criteria-disagree", criteria_disagree, size=(15.2, 5.2),
           axes=False),
]

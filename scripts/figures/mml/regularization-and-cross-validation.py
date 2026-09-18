"""Figures for *Regularization and Cross-Validation*.

1. `the-regularization-path` — Equation 8.12. Sweeping lambda on a degree-12 fit
   to 25 points: the training risk rises modestly, the expected risk falls
   sharply, and the parameter norm collapses by three orders of magnitude. The
   penalty buys generalisation with training accuracy, at a very good rate.

2. `cross-validation-bias` — Equation 8.13, and the honest news about it. K-fold
   cross-validation is BIASED upward, badly so at small K, because each fold
   trains on less data than the full-data predictor whose risk you want.

3. `k-fold-partition` — the book's Figure 8.4 drawn, with the standard error
   sigma over root K that its margin note defines, and the embarrassingly
   parallel structure that makes the K-fold cost tolerable.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from _style import Palette, figure


def _make(n, seed, noise=0.35):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg):
    return np.vander(x / 3.0, deg + 1, increasing=True)


def _ridge(A, y, lam):
    """argmin (1/N)||y - A th||^2 + lam ||th||^2, i.e. Equation 8.12."""
    n, m = A.shape
    if lam <= 0:
        return np.linalg.lstsq(A, y, rcond=None)[0]
    return np.linalg.solve(A.T @ A / n + lam * np.eye(m), A.T @ y / n)


def the_regularization_path(fig, ax, p: Palette) -> None:
    """Equation 8.12 as lambda sweeps."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xtr, ytr = _make(25, 3)
    xte, yte = _make(4000, 99)
    deg = 12
    A, B = _design(xtr, deg), _design(xte, deg)

    lams = np.concatenate([[0.0], np.geomspace(1e-9, 1e2, 400)])
    rtr, rte, nrm = [], [], []
    for lam in lams:
        th = _ridge(A, ytr, lam)
        rtr.append(float(np.mean((ytr - A @ th) ** 2)))
        rte.append(float(np.mean((yte - B @ th) ** 2)))
        nrm.append(float(np.linalg.norm(th)))
    rtr, rte, nrm = np.array(rtr), np.array(rte), np.array(nrm)
    # index 0 is lambda = 0; plot the rest on a log axis
    ls, tr, te, nm = lams[1:], rtr[1:], rte[1:], nrm[1:]
    kb = int(np.argmin(te))

    left.loglog(ls, tr, color=p.blue, linewidth=2.3,
                label="training risk")
    left.loglog(ls, te, color=p.red, linewidth=2.3,
                label="expected risk, 4000 unseen points")
    left.axhline(rte[0], color=p.red, linestyle=":", linewidth=1.5)
    left.axhline(rtr[0], color=p.blue, linestyle=":", linewidth=1.5)
    left.plot([ls[kb]], [te[kb]], "o", color=p.green, markersize=10,
              markerfacecolor="none", markeredgewidth=2.0)
    left.annotate(
        f"best $\\lambda \\approx {ls[kb]:.1e}$\nexpected risk {te[kb]:.6f}",
        xy=(ls[kb], te[kb]), xytext=(0.06, 0.14),
        textcoords="axes fraction", fontsize=8.0, color=p.green,
        family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.green, linewidth=1.1))
    left.set_xlabel("regularisation parameter $\\lambda$")
    left.set_ylabel("average squared loss")
    left.set_title("Equation 8.12: the trade, priced", fontsize=9.8)
    left.legend(fontsize=7.8, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.97, 0.05,
        f"dotted lines are $\\lambda = 0$:\n"
        f"  training {rtr[0]:.6f}\n  expected {rte[0]:.6f}\n\n"
        f"at the best $\\lambda$: training rises\n"
        f"{100 * (tr[kb] / rtr[0] - 1):.0f}%, expected falls "
        f"{100 * (1 - te[kb] / rte[0]):.0f}%",
        transform=left.transAxes, ha="right", va="bottom", fontsize=7.4,
        color=p.fg, family="monospace")

    right.loglog(ls, nm, color=p.purple, linewidth=2.4)
    right.axhline(nrm[0], color=p.purple, linestyle=":", linewidth=1.5)
    right.plot([ls[kb]], [nm[kb]], "o", color=p.green, markersize=10,
               markerfacecolor="none", markeredgewidth=2.0)
    right.set_xlabel("regularisation parameter $\\lambda$")
    right.set_ylabel("$\\|\\boldsymbol{\\theta}\\|$")
    right.set_title("What the penalty actually does", fontsize=9.8)
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.05, 0.16,
        f"$\\lambda = 0$: {nrm[0]:.1f}  (dotted)\n"
        f"best $\\lambda$: {nm[kb]:.4f}\n"
        f"a factor of {nrm[0] / nm[kb]:.0f}\n\n"
        "The penalty does not make the fit\nsmoother by magic — it makes large\n"
        "coefficients expensive, and large\ncoefficients were the symptom.",
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Regularisation buys expected risk with training risk, at a very "
        "favourable exchange rate",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"A degree-12 polynomial fitted to 25 points. Unregularised it has "
        f"$\\|\\boldsymbol{{\\theta}}\\| = {nrm[0]:.0f}$ and an expected risk of "
        f"{rte[0]:.4f}. At $\\lambda \\approx {ls[kb]:.0e}$ the training risk "
        f"rises by\n{100 * (tr[kb] / rtr[0] - 1):.0f}% — from {rtr[0]:.4f} to "
        f"{tr[kb]:.4f} — and the expected risk falls by "
        f"{100 * (1 - te[kb] / rte[0]):.0f}%, to {te[kb]:.4f}. The parameter norm "
        f"drops by a factor of {nrm[0] / nm[kb]:.0f}.\nPast the optimum the "
        "penalty dominates and both risks rise together: that is underfitting "
        "again, arrived at from the other side.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def cross_validation_bias(fig, ax, p: Palette) -> None:
    """Equation 8.13 is an estimate, and not an unbiased one."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xtr, ytr = _make(25, 3)
    xte, yte = _make(4000, 99)
    deg = 5
    A = _design(xtr, deg)
    th_full = np.linalg.lstsq(A, ytr, rcond=None)[0]
    truth = float(np.mean((yte - _design(xte, deg) @ th_full) ** 2))

    def kfold(K, seed):
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(ytr))
        folds = np.array_split(idx, K)
        out = []
        for k in range(K):
            va = folds[k]
            tr = np.concatenate([folds[j] for j in range(K) if j != k])
            Ak = _design(xtr[tr], deg)
            thk = np.linalg.lstsq(Ak, ytr[tr], rcond=None)[0]
            out.append(float(np.mean((ytr[va] - _design(xtr[va], deg) @ thk) ** 2)))
        return np.array(out)

    Ks = [2, 3, 5, 10, 25]
    means, spreads, ses = [], [], []
    for K in Ks:
        m = np.array([kfold(K, s).mean() for s in range(40)])
        means.append(m.mean())
        spreads.append(m.std())
        r0 = kfold(K, 0)
        ses.append(r0.std(ddof=1) / np.sqrt(K))
    means, spreads, ses = np.array(means), np.array(spreads), np.array(ses)

    left.errorbar(Ks, means, yerr=spreads, fmt="o-", color=p.blue,
                  linewidth=2.2, markersize=6, capsize=4,
                  label="mean over 40 shuffles, $\\pm$ 1 sd")
    left.axhline(truth, color=p.green, linestyle="--", linewidth=1.8,
                 label=f"risk of the full-data fit = {truth:.6f}")
    left.set_yscale("log")
    left.set_xlabel("$K$, number of folds")
    left.set_ylabel("estimated risk (Eq 8.13)")
    left.set_xticks(Ks)
    left.set_title("K-fold is biased UPWARD, badly at small $K$",
                   fontsize=9.8)
    left.legend(fontsize=7.6, loc="upper right")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    for K, m in zip(Ks, means):
        left.annotate(f"{m:.4f}", xy=(K, m), xytext=(6, -12),
                      textcoords="offset points", fontsize=7.4,
                      color=p.blue, family="monospace")

    right.semilogy(Ks, means - truth, "o-", color=p.amber, linewidth=2.3,
                   markersize=6, label="bias, estimate $-$ truth")
    right.semilogy(Ks, ses, "s-", color=p.purple, linewidth=2.0,
                   markersize=5, label="standard error, $\\sigma/\\sqrt{K}$")
    right.semilogy(Ks, spreads, "^-", color=p.red, linewidth=2.0,
                   markersize=5, label="spread over 40 shuffles")
    right.set_xlabel("$K$")
    right.set_ylabel("magnitude")
    right.set_xticks(Ks)
    right.set_title("Bias, and the two kinds of noise", fontsize=9.8)
    right.legend(fontsize=7.6, loc="upper right")
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.06,
        f"$K = 2$: bias ${means[0] - truth:+.3f}$, an overestimate\n"
        f"    of {means[0] / truth:.0f}x the true risk\n"
        f"$K = 25$ (leave-one-out): bias "
        f"${means[-1] - truth:+.6f}$\n\n"
        "The book names both error sources: a\nfinite training set gives a worse "
        "$f^{(k)}$,\nand a finite validation set estimates\nits risk badly.",
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 8.13 approximates the expected risk — and the approximation "
        "has a direction",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"A degree-5 fit to 25 points, whose full-data risk on 4000 unseen points "
        f"is {truth:.6f}. Two-fold cross-validation estimates that at "
        f"{means[0]:.4f} — an\noverestimate by a factor of {means[0] / truth:.0f} "
        "— because each fold trains on only 12 points, and a degree-5 model needs "
        "6 parameters. The bias falls\nmonotonically with $K$ and is "
        f"{means[-1] - truth:+.6f} at leave-one-out. So $K$ trades bias against "
        "cost, and the book's warning about small validation\nsets giving noisy "
        "estimates is the other half of the same trade.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def k_fold_partition(fig, ax, p: Palette) -> None:
    """The book's Figure 8.4, drawn, plus what each run costs."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.25, 1.0])

    K = 5
    left.axis("off")
    left.set_xlim(-0.6, 6.4)
    left.set_ylim(-1.4, K + 1.0)
    left.set_title("$K = 5$ folds: five runs, each with a different held-out "
                   "chunk", fontsize=9.6)
    for k in range(K):
        y = K - 1 - k
        for c in range(K):
            val = (c == k)
            left.add_patch(Rectangle(
                (c * 1.1, y), 1.0, 0.78,
                facecolor=(p.amber if val else p.blue),
                alpha=(0.42 if val else 0.22),
                edgecolor=(p.amber if val else p.blue), linewidth=1.4,
                hatch=("///" if val else None)))
        left.text(-0.2, y + 0.39, f"run {k + 1}", ha="right", va="center",
                  fontsize=8.6, color=p.fg, family="monospace")
        left.text(5.75, y + 0.39, f"$\\mathcal{{V}}^{{({k + 1})}}$",
                  ha="left", va="center", fontsize=8.4, color=p.amber)
    left.add_patch(Rectangle((0.0, K + 0.15), 1.0, 0.5, facecolor=p.blue,
                             alpha=0.22, edgecolor=p.blue, linewidth=1.3))
    left.text(1.2, K + 0.4, "training, $\\mathcal{R}$", fontsize=8.4,
              color=p.blue, va="center")
    left.add_patch(Rectangle((2.9, K + 0.15), 1.0, 0.5, facecolor=p.amber,
                             alpha=0.42, edgecolor=p.amber, linewidth=1.3,
                             hatch="///"))
    left.text(4.1, K + 0.4, "validation, $\\mathcal{V}$", fontsize=8.4,
              color=p.amber, va="center")
    left.text(
        -0.5, -0.35,
        "$\\mathcal{D} = \\mathcal{R} \\cup \\mathcal{V}$ with "
        "$\\mathcal{R} \\cap \\mathcal{V} = \\emptyset$: every point is used for "
        "validation exactly once,\nand for training exactly $K - 1$ times. "
        "Equation 8.13 averages the $K$ risks.",
        fontsize=8.2, color=p.muted, va="top")

    # what K costs and buys
    right.axis("off")
    right.set_xlim(0, 10)
    right.set_ylim(-0.8, 8.6)
    right.set_title("What $K$ costs and what it buys", fontsize=9.6)
    heads = ("$K$", "train size", "fits", "bias", "noise in each fold")
    xs = (0.15, 1.3, 3.4, 4.5, 6.4)
    for hx, h in zip(xs, heads):
        right.text(hx, 8.05, h, fontsize=8.4, color=p.fg, weight="bold")
    right.plot([0.1, 9.9], [7.85, 7.85], color=p.grid, linewidth=1.2)
    rowsd = [
        (2, "12 or 13", 2, "+4.98", "large: 12 or 13 held out", p.red),
        (3, 17, 3, "+0.44", "moderate", p.amber),
        (5, 20, 5, "+0.039", "modest", p.green),
        (10, 22, 10, "+0.017", "small", p.green),
        (25, 24, 25, "+0.000063", "each fold has ONE point", p.purple),
    ]
    for k, (kk, tsz, fits, bias, noise, col) in enumerate(rowsd):
        y = 7.1 - k * 1.15
        right.text(xs[0], y, str(kk), fontsize=8.8, color=col,
                   family="monospace")
        right.text(xs[1], y, f"{tsz} of 25", fontsize=8.0, color=col,
                   family="monospace")
        right.text(xs[2], y, str(fits), fontsize=8.4, color=col,
                   family="monospace")
        right.text(xs[3], y, bias, fontsize=8.4, color=col,
                   family="monospace")
        right.text(xs[4], y, noise, fontsize=8.0, color=p.muted)
    right.text(
        0.15, 0.55,
        "The standard error is $\\sigma/\\sqrt{K}$, where $\\sigma$ is the "
        "standard deviation of the $K$\nfold risks — so cross-validation "
        "reports not just an estimate but an uncertainty.\n\n"
        "The book's other note: cross-validation is EMBARRASSINGLY PARALLEL. "
        "With $K$\nmachines it costs no more wall-clock time than a single "
        "assessment.",
        fontsize=8.2, color=p.fg, va="bottom")

    fig.suptitle(
        "Section 8.2.4: use every point for validation exactly once",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The tension the book names: you want a large training set AND a large "
        "validation set, from one finite dataset. $K$-fold resolves it by using "
        "every point for\nboth, at different times — at the cost of $K$ training "
        "runs. Large $K$ means each predictor sees nearly all the data (low bias) "
        "but each risk estimate rests on\nvery few points (high per-fold noise); "
        "the average over folds is what tames the second.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


FIGURES = [
    figure("the-regularization-path", the_regularization_path,
           size=(12.4, 4.9), axes=False),
    figure("cross-validation-bias", cross_validation_bias, size=(12.6, 4.9),
           axes=False),
    figure("k-fold-partition", k_fold_partition, size=(13.2, 4.9), axes=False),
]

"""Figures for *Empirical Risk Minimization*.

1. `empirical-versus-expected-risk` — Equation 8.6 against Equation 8.10. The
   empirical risk on the training set falls monotonically with model complexity
   and the expected risk, estimated on 4000 held-out points, turns. The gap
   between them is the whole subject of Sections 8.2.3 and 8.2.4.

2. `the-hypothesis-class` — Section 8.2.1. The affine class of Equations 8.4 and
   8.5 drawn against richer nested classes, showing that a bigger class always
   achieves at least as low an empirical risk because it CONTAINS the smaller one.

3. `loss-is-not-the-performance-measure` — the book's remark at the end of
   Section 8.2.2. Squared loss, absolute loss and a zero-one style measure rank
   the same two predictors differently, so optimising one does not optimise
   another.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _make(n, seed, noise=0.35):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3, 3, n))
    return x, np.sin(1.4 * x) + 0.3 * x + noise * rng.standard_normal(n)


def _design(x, deg):
    return np.vander(x / 3.0, deg + 1, increasing=True)


def _sweep(max_deg=15):
    if getattr(_sweep, "_memo", None) is not None:
        return _sweep._memo
    xtr, ytr = _make(25, 3)
    xte, yte = _make(4000, 99)
    out = []
    for d in range(max_deg + 1):
        A = _design(xtr, d)
        th = np.linalg.lstsq(A, ytr, rcond=None)[0]
        out.append((d,
                    float(np.mean((ytr - A @ th) ** 2)),
                    float(np.mean((yte - _design(xte, d) @ th) ** 2)),
                    float(np.linalg.norm(th))))
    _sweep._memo = (xtr, ytr, xte, yte, out)
    return _sweep._memo


def empirical_versus_expected_risk(fig, ax, p: Palette) -> None:
    """Eq 8.6 falls forever; Eq 8.10 turns."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xtr, ytr, xte, yte, rows = _sweep()
    deg = np.array([r[0] for r in rows])
    rtr = np.array([r[1] for r in rows])
    rte = np.array([r[2] for r in rows])
    nrm = np.array([r[3] for r in rows])
    best = int(deg[np.argmin(rte)])

    left.semilogy(deg, rtr, "o-", color=p.blue, linewidth=2.2, markersize=5,
                  label="$R_{\\mathrm{emp}}$ on 25 training points, Eq 8.6")
    left.semilogy(deg, rte, "s-", color=p.red, linewidth=2.2, markersize=5,
                  label="$R_{\\mathrm{true}}$ estimated on 4000 unseen, Eq 8.10")
    left.axvline(best, color=p.green, linestyle="--", linewidth=1.6)
    left.text(best + 0.2, rte.max() * 0.3,
              f"lowest expected\nrisk: degree {best}", fontsize=8.2,
              color=p.green, family="monospace")
    left.fill_between(deg, rtr, rte, where=rte > rtr, color=p.amber,
                      alpha=0.16, linewidth=0, label="the generalisation gap")
    left.set_xlabel("polynomial degree, i.e. size of the hypothesis class")
    left.set_ylabel("average squared loss")
    left.set_title("The two risks separate", fontsize=9.8)
    left.legend(fontsize=7.4, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.97, 0.05,
        f"degree {best}: {rtr[best]:.4f} train, {rte[best]:.4f} test\n"
        f"degree 15: {rtr[-1]:.4f} train, {rte[-1]:.2f} test\n"
        f"the ratio grows to {rte[-1] / rtr[-1]:.0f}x",
        transform=left.transAxes, ha="right", va="bottom", fontsize=7.6,
        color=p.fg, family="monospace")

    right.semilogy(deg, nrm, "o-", color=p.purple, linewidth=2.3,
                   markersize=5.5)
    right.axvline(best, color=p.green, linestyle="--", linewidth=1.6)
    right.set_xlabel("polynomial degree")
    right.set_ylabel("$\\|\\boldsymbol{\\theta}\\|$")
    right.set_title("And the parameters blow up", fontsize=9.8)
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.95,
        f"at the best degree: {nrm[best]:.4f}\n"
        f"at degree 15:      {nrm[-1]:.1f}\n"
        f"a factor of {nrm[-1] / nrm[best]:.0f}\n\n"
        "The book's remark that \"the magnitude\nof the parameter values becomes\n"
        "relatively large if we run into\noverfitting\" (Bishop, 2006),\nmeasured.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Equation 8.6 is what you can compute; Equation 8.10 is what you want",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"The empirical risk falls at every step from degree 0 to 15 — it must, "
        f"since a larger class contains the smaller one. The expected risk turns "
        f"at degree {best}\nand reaches {rte[-1]:.1f} by degree 15, "
        f"{rte[-1] / rtr[-1]:.0f} times the training figure. Overfitting is "
        "precisely the statement that $R_{\\mathrm{emp}}$ UNDERESTIMATES "
        "$R_{\\mathrm{true}}$, and the\nright panel shows the symptom the book "
        "names: the fitted parameters grow without bound.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def the_hypothesis_class(fig, ax, p: Palette) -> None:
    """Section 8.2.1: what the class can reach, and why bigger never fits worse."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xtr, ytr, xte, yte, rows = _sweep()
    grid = np.linspace(-3.2, 3.2, 600)
    left.plot(xtr, ytr, "o", color=p.fg, markersize=6,
              markeredgecolor=p.bg, markeredgewidth=0.8,
              label="25 training points", zorder=6)
    for d, col, lab in ((1, p.red, "affine, Eq 8.4"),
                        (3, p.amber, "degree 3"),
                        (6, p.green, "degree 6")):
        A = _design(xtr, d)
        th = np.linalg.lstsq(A, ytr, rcond=None)[0]
        left.plot(grid, _design(grid, d) @ th, color=col, linewidth=2.2,
                  label=f"{lab}, $R_{{\\mathrm{{emp}}}} = {rows[d][1]:.4f}$")
    left.set_xlabel("$x$")
    left.set_ylabel("$y$")
    left.set_ylim(-2.6, 2.6)
    left.set_title("Three nested hypothesis classes", fontsize=9.8)
    left.legend(fontsize=7.6, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.97, 0.04,
        "the affine class of Eq 8.4 is a\nSTRAIGHT LINE: no choice of\n"
        "$\\boldsymbol{\\theta}$ makes it bend.",
        transform=left.transAxes, ha="right", va="bottom", fontsize=7.6,
        color=p.red, family="monospace")

    deg = np.array([r[0] for r in rows])
    rtr = np.array([r[1] for r in rows])
    right.plot(deg, rtr, "o-", color=p.blue, linewidth=2.3, markersize=5.5)
    diffs = np.diff(rtr)
    right.set_xlabel("polynomial degree")
    right.set_ylabel("$R_{\\mathrm{emp}}$, training risk")
    right.set_title("A bigger class can never fit worse", fontsize=9.8)
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.97, 0.95,
        f"increases in $R_{{\\mathrm{{emp}}}}$ as the\n"
        f"degree grows: {int((diffs > 1e-12).sum())} of {diffs.size}\n\n"
        "This is not luck. A degree-$d$\npolynomial is a special case of\n"
        "a degree-$(d{+}1)$ one, with the\ntop coefficient set to zero —\n"
        "so the larger class can always\nmatch the smaller one's best fit.",
        transform=right.transAxes, ha="right", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.2.1: choosing the class is the first of the four design "
        "choices, and it caps everything",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Left: the affine class cannot bend, so no amount of optimisation "
        "recovers the curve — that is underfitting, and it is a property of the "
        "CLASS rather than\nof the search. Right: enlarging the class never "
        "raises the training risk, which is exactly why training risk cannot be "
        "used to choose a class. The\nmonotone curve on the right is the reason "
        "Sections 8.2.3 and 8.2.4 exist.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def loss_is_not_the_performance_measure(fig, ax, p: Palette) -> None:
    """The book's closing remark of Section 8.2.2, made concrete."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    # Two predictors on the same data: one with many small errors, one with
    # few large ones. Different losses rank them differently.
    rng = np.random.default_rng(5)
    n = 200
    truth = np.zeros(n)
    a = 0.55 * np.ones(n)                     # A: every prediction off by 0.55
    b = np.zeros(n)
    b[:12] = 3.4                              # B: 12 big misses, rest exact
    preds = {"A: many small errors": (a, p.blue),
             "B: a few large errors": (b, p.amber)}

    losses = {
        "squared, $(y-\\hat y)^2$": lambda r: r ** 2,
        "absolute, $|y-\\hat y|$": lambda r: np.abs(r),
        "tolerance, $\\mathbf{1}[|y-\\hat y| > 1]$": lambda r: (np.abs(r) > 1.0).astype(float),
    }
    names = list(losses)
    width = 0.36
    idx = np.arange(len(names))
    vals = {}
    for k, (pname, (pv, col)) in enumerate(preds.items()):
        r = truth - pv
        v = [losses[nm](r).mean() for nm in names]
        vals[pname] = v
        left.bar(idx + (k - 0.5) * width, v, width, color=col, alpha=0.75,
                 label=pname)
        for i, q in enumerate(v):
            left.text(i + (k - 0.5) * width, q + 0.012, f"{q:.4f}",
                      ha="center", fontsize=7.4, color=col,
                      family="monospace")
    left.set_xticks(idx)
    left.set_xticklabels(names, fontsize=8.0)
    left.set_ylabel("average loss over 200 points")
    left.set_title("Three measures, two predictors", fontsize=9.8)
    left.legend(fontsize=8, loc="upper left")
    left.grid(alpha=0.20, axis="y", linewidth=0.6)

    right.axis("off")
    right.set_xlim(0, 10)
    right.set_ylim(0, 10)
    right.set_title("Who wins depends on what you measure", fontsize=9.8)
    ka, kb = list(preds)
    for i, nm in enumerate(names):
        y = 8.2 - i * 2.3
        va, vb = vals[ka][i], vals[kb][i]
        win = ka if va < vb else kb
        col = p.blue if win == ka else p.amber
        right.text(0.3, y, nm, fontsize=9.4, color=p.fg)
        right.text(0.7, y - 0.65, f"A = {va:.4f}", fontsize=8.6,
                   color=p.blue, family="monospace")
        right.text(0.7, y - 1.15, f"B = {vb:.4f}", fontsize=8.6,
                   color=p.amber, family="monospace")
        right.text(5.6, y - 0.9, f"{win.split(':')[0]} wins", fontsize=9.4,
                   color=col)
        ratio = ("outright" if min(va, vb) <= 1e-12
                 else f"by {max(va, vb) / min(va, vb):.2f}x")
        right.text(7.6, y - 0.9, ratio, fontsize=8.4, color=col,
                   family="monospace")
    right.text(
        0.3, 1.0,
        "Squared loss punishes the twelve large errors hardest: A wins, 0.3025\n"
        "against 0.6936. Absolute loss REVERSES that — B wins, 0.2040 against\n"
        "0.5500 — because A is wrong on all 200 points and B on only 12. The\n"
        "tolerance measure scores A at exactly 0, since 0.55 is below the\n"
        "threshold. Same two predictors, three measures, two different winners.",
        fontsize=8.2, color=p.fg, va="bottom")

    fig.suptitle(
        "The loss you optimise and the measure you are judged on are two "
        "different choices",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's own remark: \"in principle, the design of the loss function "
        "for empirical risk minimization should correspond directly to the "
        "performance measure\n... In practice, there is often a mismatch\", "
        "usually for reasons of implementation or optimisation. This is what a "
        "mismatch costs: an honest reversal of\nthe ranking, not a small "
        "discrepancy.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


FIGURES = [
    figure("empirical-versus-expected-risk", empirical_versus_expected_risk,
           size=(12.2, 4.9), axes=False),
    figure("the-hypothesis-class", the_hypothesis_class, size=(12.4, 4.9),
           axes=False),
    figure("loss-is-not-the-performance-measure",
           loss_is_not_the_performance_measure, size=(12.6, 4.9), axes=False),
]

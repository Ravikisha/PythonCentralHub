"""Figures for *Overfitting in Linear Regression* (Section 9.2.2).

1. `figure-9-5-rebuilt` — the book's six polynomial fits, M = 0, 1, 3, 4, 6, 9,
   each carrying its own training and test RMSE. At M = 9 = N - 1 the curve
   interpolates every point (training RMSE 6.5e-11) and the test RMSE is 100.85.

2. `training-and-test-error` — Figure 9.6, with the parameter norm beside it.
   The training curve is monotone non-increasing at every one of nine steps;
   the test curve bottoms out at M = 4, exactly as the book reports.

3. `which-degree-really` — Figure 9.6 is one draw of a random experiment.
   Repeated 2000 times, M = 4 wins 46.1% of the time, M = 6 wins 20.8%, and
   M = 1 wins 11.3%. Beside it, the null space that makes M >= N ill-posed.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2
NTR = 10


def _truth(x):
    return -np.sin(x / 5) + np.cos(x)


def _design(x, M):
    return np.vander(np.asarray(x, float), M + 1, increasing=True)


def _train(seed=4):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-5, 5, NTR))
    return x, _truth(x) + SIG * rng.standard_normal(NTR)


def _test():
    xte = np.linspace(-5, 5, 200)
    return xte, _truth(xte) + SIG * np.random.default_rng(1234).standard_normal(200)


def _rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


# --------------------------------------------------------------------------
# 1. Figure 9.5
# --------------------------------------------------------------------------

def figure_9_5_rebuilt(fig, ax, p: Palette) -> None:
    fig.clear()
    axes = fig.subplots(2, 3).ravel()
    x, y = _train()
    xte, yte = _test()
    xg = np.linspace(-5, 5, 500)

    for axx, M in zip(axes, (0, 1, 3, 4, 6, 9)):
        P = _design(x, M)
        th = np.linalg.lstsq(P, y, rcond=None)[0]
        rtr = _rmse(y, P @ th)
        rte = _rmse(yte, _design(xte, M) @ th)
        col = p.green if M == 4 else (p.red if M >= 6 else p.amber)
        axx.plot(xg, _truth(xg), color=p.muted, linewidth=1.4, linestyle="--")
        axx.plot(xg, _design(xg, M) @ th, color=col, linewidth=2.4)
        axx.plot(x, y, "o", color=p.blue, markersize=5.5,
                 markeredgecolor=p.bg, markeredgewidth=0.6, zorder=5)
        axx.set_xlim(-5, 5)
        axx.set_ylim(-4, 4)
        axx.set_title(f"$M = {M}$", fontsize=10, color=col)
        axx.grid(alpha=0.18, linewidth=0.5)
        axx.tick_params(labelsize=7.5)
        axx.text(0.03, 0.03,
                 f"train {rtr:.6f}\ntest  {rte:.4f}",
                 transform=axx.transAxes, ha="left", va="bottom",
                 fontsize=7.6, color=col, family="monospace")
        if M == 4:
            axx.text(0.97, 0.97, "best test RMSE", transform=axx.transAxes,
                     ha="right", va="top", fontsize=7.4, color=p.green,
                     family="monospace")
        if M == 9:
            axx.text(0.97, 0.97, "$M = N-1$:\npasses through\nevery point",
                     transform=axx.transAxes, ha="right", va="top",
                     fontsize=7.2, color=p.red, family="monospace")

    fig.suptitle(
        "Figure 9.5: maximum likelihood fits for six polynomial degrees, with "
        "the errors each one actually achieves",
        y=0.985, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Dashed grey is the function that generated the data. Reading the two "
        "numbers in each panel together is the whole lesson: the training error "
        "falls at every step while the\ntest error bottoms out at M = 4 and "
        "then leaves — reaching 100.85 at M = 9, where the fit is perfect.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. Figure 9.6
# --------------------------------------------------------------------------

def training_and_test_error(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _train()
    xte, yte = _test()
    Ms = np.arange(10)
    tr, te, nr = [], [], []
    for M in Ms:
        P = _design(x, int(M))
        th = np.linalg.lstsq(P, y, rcond=None)[0]
        tr.append(_rmse(y, P @ th))
        te.append(_rmse(yte, _design(xte, int(M)) @ th))
        nr.append(float(np.linalg.norm(th)))
    tr, te, nr = np.array(tr), np.array(te), np.array(nr)

    left.semilogy(Ms, np.maximum(tr, 1e-11), "o-", color=p.blue,
                  linewidth=2.4, markersize=7, label="training error")
    left.semilogy(Ms, te, "o-", color=p.amber, linewidth=2.4, markersize=7,
                  label="test error")
    kb = int(np.argmin(te))
    left.plot([Ms[kb]], [te[kb]], "o", color=p.green, markersize=13,
              markerfacecolor="none", markeredgewidth=2.4, zorder=6)
    left.annotate(f"best test RMSE\n$M = {Ms[kb]}$, {te[kb]:.6f}",
                  xy=(Ms[kb], te[kb]), xytext=(-2, -66),
                  textcoords="offset points", ha="center", fontsize=8.2,
                  color=p.green, family="monospace",
                  arrowprops=dict(arrowstyle="->", color=p.green,
                                  linewidth=1.2))
    left.axvspan(5.5, 9.5, color=p.red, alpha=0.08)
    left.text(7.5, 2e-9, "\"from degree 6 onward the\ntest error increases\n"
                         "significantly\"", ha="center", fontsize=7.4,
              color=p.red, family="monospace")
    left.set_xlabel("degree of polynomial $M$")
    left.set_ylabel("RMSE")
    left.set_title("Figure 9.6, rebuilt", fontsize=9.8)
    left.legend(fontsize=8.4, loc="center left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.text(
        0.03, 0.03,
        "training RMSE never rises:\n9 steps, 0 increases.\n"
        f"at M = 9 it is {tr[9]:.1e}\nand the test RMSE is {te[9]:.2f}.\n\n"
        "Note M = 3, where the test\nerror bumps UP before the\nreal minimum.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    right.semilogy(Ms, nr, "o-", color=p.purple, linewidth=2.4, markersize=7)
    right.plot([Ms[kb]], [nr[kb]], "o", color=p.green, markersize=13,
               markerfacecolor="none", markeredgewidth=2.4, zorder=6)
    right.set_xlabel("degree of polynomial $M$")
    right.set_ylabel(r"$\|\theta_{\mathrm{ML}}\|$")
    right.set_title("The parameter norm, the one training-side warning",
                    fontsize=9.8)
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.03, 0.95,
        "\n".join(f"  M = {int(m)}: ||theta|| = {v:.4f}"
                  for m, v in zip(Ms, nr))
        + "\n\nThe book: 'the magnitude of\nthe parameter values becomes\n"
          "relatively large if we run\ninto overfitting'. Section 9.2.3\n"
          "acts on exactly this.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.1,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.2.2: the training error never increases with capacity, and "
        "that is precisely why it cannot be trusted",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "A richer model class contains the poorer one, so its best fit cannot "
        "be worse on the training set — the monotonicity is a theorem, not an "
        "observation. The test curve is\nfree of that constraint, and the gap "
        "between the two is the only thing on this page that carries "
        "information about generalization.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. one draw of a random experiment
# --------------------------------------------------------------------------

_SWEEP: dict = {}


def _degree_sweep(trials=2000):
    if "v" in _SWEEP:
        return _SWEEP["v"]
    xte, yte = _test()
    counts = np.zeros(10, dtype=int)
    best = []
    for s in range(trials):
        rng = np.random.default_rng(10_000 + s)
        xs = np.sort(rng.uniform(-5, 5, NTR))
        ys = _truth(xs) + SIG * rng.standard_normal(NTR)
        sc = []
        for M in range(10):
            Pm = _design(xs, M)
            t = np.linalg.lstsq(Pm, ys, rcond=None)[0]
            sc.append(_rmse(yte, _design(xte, M) @ t))
        k = int(np.argmin(sc))
        counts[k] += 1
        best.append(sc[k])
    _SWEEP["v"] = (counts, float(np.median(best)), trials)
    return _SWEEP["v"]


def which_degree_really(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    counts, med, trials = _degree_sweep()
    Ms = np.arange(10)
    cols = [p.green if m == 4 else p.blue for m in Ms]
    left.bar(Ms, counts / trials, color=cols, width=0.68)
    for m, c in zip(Ms, counts):
        if c:
            left.text(m, c / trials + 0.008, f"{c/trials:.1%}", ha="center",
                      fontsize=7.8,
                      color=p.green if m == 4 else p.blue,
                      family="monospace")
    left.set_xticks(Ms)
    left.set_xlabel("degree with the lowest test RMSE")
    left.set_ylabel("share of draws")
    left.set_ylim(0, 0.56)
    left.set_title(f"{trials} fresh draws of the same experiment",
                   fontsize=9.8)
    left.grid(alpha=0.20, linewidth=0.6, axis="y")
    left.text(
        0.97, 0.95,
        "The book reports M = 4 for\nits own draw, and M = 4 is\n"
        f"indeed the modal answer —\nbut only {counts[4]/trials:.1%} of the time.\n\n"
        f"M = 6 wins {counts[6]/trials:.1%}, M = 1 wins {counts[1]/trials:.1%}.\n\n"
        f"median best test RMSE\nacross draws: {med:.6f}",
        transform=left.transAxes, ha="right", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- right: the null space at M >= N ---------------------------------
    x, y = _train()
    M = 10
    P = _design(x, M)
    th_min = np.linalg.lstsq(P, y, rcond=None)[0]
    ns = np.linalg.svd(P)[2][int(np.linalg.matrix_rank(P)):]
    xg = np.linspace(-5, 5, 500)
    for c, col, lw in ((0.0, p.amber, 3.0), (1.0, p.blue, 1.6),
                       (50.0, p.purple, 1.6), (5000.0, p.red, 1.6)):
        alt = th_min + c * ns[0]
        lab = ("minimum-norm (lstsq)" if c == 0
               else f"$+\\ {c:g}\\times$ null vector")
        right.plot(xg, _design(xg, M) @ alt, color=col, linewidth=lw,
                   label=lab, alpha=0.9 if c == 0 else 0.85)
    right.plot(x, y, "o", color=p.green, markersize=7,
               markeredgecolor=p.bg, markeredgewidth=0.7, zorder=6,
               label="the 10 training points")
    right.set_xlim(-5, 5)
    right.set_ylim(-4, 4)
    right.set_xlabel("$x$")
    right.set_ylabel("$y$")
    right.set_title("$M = 10 > N$: infinitely many estimators",
                    fontsize=9.8)
    right.legend(fontsize=7.2, loc="lower center", ncol=2)
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.03, 0.95,
        f"rk(Phi) = {int(np.linalg.matrix_rank(P))}, K = {P.shape[1]}\n"
        f"null space dimension: {ns.shape[0]}\n\n"
        "All four curves pass through\nall ten points to 1e-7 or\nbetter.\n\n"
        "The book: 'there are infinitely\nmany possible maximum\n"
        "likelihood estimators'.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Figure 9.6 is one draw of a random experiment, and past $M = N$ the "
        "estimator stops being unique at all",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's own bound is that for a training set of size N it suffices "
        "to test 0 <= M <= N-1, because beyond it Phi^T Phi is no longer "
        "invertible. The right panel is what\nthat means concretely: add any "
        "multiple of a null vector and you get a different parameter vector "
        "that fits the training data exactly as well.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("figure-9-5-rebuilt", figure_9_5_rebuilt, size=(13.6, 7.0),
           axes=False),
    figure("training-and-test-error", training_and_test_error,
           size=(13.4, 5.1), axes=False),
    figure("which-degree-really", which_degree_really, size=(13.6, 5.1),
           axes=False),
]

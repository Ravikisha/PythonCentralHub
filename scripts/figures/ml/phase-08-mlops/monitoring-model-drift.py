"""Figures for *Monitoring Model Drift*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import TRAIN_ANGLE, psi, stream  # noqa: E402
from _style import Palette, figure  # noqa: E402


def drift_types(fig, axes, p: Palette) -> None:
    """Input monitoring is neither necessary nor sufficient for catching decay."""
    from sklearn.linear_model import LogisticRegression

    X_tr, y_tr = stream(4000, seed=1)
    model = LogisticRegression().fit(X_tr, y_tr)

    scenarios = [
        ("No drift", *stream(2000, seed=2)),
        ("Covariate shift\nP(X) moves", *stream(2000, shift=1.5, seed=3)),
        ("Concept shift\nP(y|X) moves",
         *stream(2000, angle_deg=TRAIN_ANGLE + 90, seed=4)),
    ]

    names, accs, psis = [], [], []
    for name, Xc, yc in scenarios:
        names.append(name)
        accs.append(model.score(Xc, yc))
        psis.append(psi(X_tr[:, 0], Xc[:, 0]))

    axs = fig.subplots(1, 2)
    cols = [p.green, p.amber, p.red]

    b1 = axs[0].bar(names, accs, color=cols)
    for b, v in zip(b1, accs):
        axs[0].annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v + 0.015),
                        ha="center", fontsize=10, color=p.fg)
    axs[0].axhline(0.5, color=p.muted, ls="--", lw=1.3, label="coin flip")
    axs[0].set_ylim(0, 1.15)
    axs[0].set_ylabel("accuracy on live data")
    axs[0].set_title("What it costs you", fontsize=11)
    axs[0].legend(loc="lower left", fontsize=9)

    b2 = axs[1].bar(names, psis, color=cols)
    for b, v in zip(b2, psis):
        axs[1].annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v + 0.06),
                        ha="center", fontsize=10, color=p.fg)
    axs[1].axhline(0.25, color=p.red, ls="--", lw=1.4, label="PSI 0.25 — 'large drift'")
    axs[1].set_ylim(0, 2.5)
    axs[1].set_ylabel("input PSI (feature 0)")
    axs[1].set_title("What input monitoring sees", fontsize=11)
    axs[1].legend(loc="upper left", fontsize=9)

    fig.suptitle("The alarm fires on the harmless one and stays silent on the "
                 "damaging one", fontsize=11, color=p.muted)


def psi_sensitivity(fig, axes, p: Palette) -> None:
    """How much shift each drift statistic needs before it notices."""
    from scipy.stats import ks_2samp

    rng = np.random.default_rng(0)
    ref = rng.normal(0, 1, 4000)
    shifts = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0]

    psis, kss = [], []
    for s in shifts:
        cur = rng.normal(s, 1, 2000)
        psis.append(psi(ref, cur))
        kss.append(ks_2samp(ref, cur).statistic)

    axes.plot(shifts, psis, "o-", color=p.blue, label="PSI")
    axes.plot(shifts, kss, "o-", color=p.amber, label="KS statistic")
    axes.axhline(0.1, color=p.green, ls="--", lw=1.3)
    axes.axhline(0.25, color=p.red, ls="--", lw=1.3)
    axes.annotate("PSI 0.10 — investigate", (0.02, 0.125), color=p.green, fontsize=9)
    axes.annotate("PSI 0.25 — act", (0.02, 0.275), color=p.red, fontsize=9)

    cross = next((s for s, v in zip(shifts, psis) if v > 0.25), None)
    if cross is not None:
        axes.axvline(cross, color=p.muted, ls=":", lw=1.2)
        axes.annotate(f"PSI crosses 0.25\nat a {cross} sd shift",
                      (cross + 0.03, 0.62), color=p.muted, fontsize=9)

    axes.set_xlabel("shift in the feature mean (standard deviations)")
    axes.set_ylabel("drift statistic")
    axes.set_title("Neither statistic notices a small shift, and both scream "
                   "at a large one")
    axes.legend(loc="upper left")


def detection_delay(fig, axes, p: Palette) -> None:
    """Labels arrive late, so the dashboard is a picture of the past."""
    from sklearn.linear_model import LogisticRegression

    X_tr, y_tr = stream(4000, seed=1)
    model = LogisticRegression().fit(X_tr, y_tr)

    LAG = 30
    days = list(range(0, 91, 5))

    def angle(day):
        return TRAIN_ANGLE + (0.0 if day < 20 else min((day - 20) * 1.5, 90.0))

    true_acc, seen_acc, psi_vals = [], [], []
    for d in days:
        Xd, yd = stream(1000, angle_deg=angle(d), seed=100 + d)
        true_acc.append(model.score(Xd, yd))
        psi_vals.append(psi(X_tr[:, 0], Xd[:, 0]))

        sd = d - LAG
        if sd < 0:
            seen_acc.append(np.nan)
        else:
            Xs, ys = stream(1000, angle_deg=angle(sd), seed=100 + sd)
            seen_acc.append(model.score(Xs, ys))

    axes.plot(days, true_acc, "o-", color=p.red, lw=2.4,
              label="true accuracy today")
    axes.plot(days, seen_acc, "o-", color=p.blue, lw=2.4,
              label=f"accuracy your dashboard shows (labels lag {LAG} days)")
    axes.plot(days, psi_vals, "-", color=p.muted, lw=1.6,
              label="input PSI — never leaves the floor")
    axes.axhline(0.5, color=p.muted, ls="--", lw=1.2)
    axes.axvline(20, color=p.amber, ls=":", lw=1.4)
    axes.annotate("drift starts", (21, 0.30), color=p.amber, fontsize=9)

    worst = int(np.nanargmax(np.array(true_acc) * -1))
    axes.annotate(
        f"day {days[worst]}: really {true_acc[worst]:.3f},\n"
        f"dashboard says {seen_acc[worst]:.3f}",
        (days[worst] - 30, 0.15), color=p.fg, fontsize=9)

    axes.set_xlabel("days since deployment")
    axes.set_ylabel("accuracy  /  PSI")
    axes.set_ylim(0, 1.15)
    axes.set_title("Concept drift: invisible to inputs, and 30 days stale in "
                   "the metrics")
    axes.legend(loc="lower left", fontsize=9)


FIGURES = [
    figure("drift-types", drift_types, size=(8.8, 3.8), axes=False),
    figure("psi-sensitivity", psi_sensitivity, size=(7.8, 4.2)),
    figure("detection-delay", detection_delay, size=(8.2, 4.4)),
]

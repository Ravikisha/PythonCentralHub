"""Figures for *Fairness Metrics and Bias Auditing*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import (group_metrics, solve_threshold, unequal_base_rates)  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _setup():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y, group = unequal_base_rates()
    X_tr, X_te, y_tr, y_te, g_tr, g_te = train_test_split(
        X, y, group, test_size=0.4, random_state=0, stratify=y)
    model = RandomForestClassifier(n_estimators=400, random_state=0).fit(X_tr, y_tr)
    proba = model.predict_proba(X_te)[:, 1]
    return proba, y_te, g_te, model.score(X_te, y_te)


def _gaps(rows):
    return {
        "demographic parity": abs(rows[0]["selection"] - rows[1]["selection"]),
        "equal opportunity": abs(rows[0]["tpr"] - rows[1]["tpr"]),
        "predictive parity": abs(rows[0]["precision"] - rows[1]["precision"]),
    }


def base_rates(fig, axes, p: Palette) -> None:
    """The whole tension comes from one fact: the base rates differ."""
    proba, y_te, g_te, acc = _setup()
    rows = group_metrics(proba, y_te, g_te, {0: 0.5, 1: 0.5})

    labels = ["group 0", "group 1"]
    base = [r["base_rate"] for r in rows]
    sel = [r["selection"] for r in rows]

    idx = np.arange(2)
    axes.bar(idx - 0.2, base, 0.4, color=p.muted, label="true base rate")
    axes.bar(idx + 0.2, sel, 0.4, color=p.blue,
             label="selection rate at threshold 0.50")
    for i, (b, s) in enumerate(zip(base, sel)):
        axes.annotate(f"{b:.4f}", (i - 0.2, b + 0.02), ha="center", fontsize=9,
                      color=p.muted)
        axes.annotate(f"{s:.4f}", (i + 0.2, s + 0.02), ha="center", fontsize=9,
                      color=p.blue)
    axes.set_xticks(idx)
    axes.set_xticklabels(labels)
    axes.set_ylim(0, 1.05)
    axes.set_ylabel("rate")
    axes.set_title(f"Base rates {base[0]:.4f} and {base[1]:.4f} — model accuracy "
                   f"{acc:.4f}, no measurement bias anywhere")
    axes.legend(loc="upper right", fontsize=9)


def impossibility(fig, axes, p: Palette) -> None:
    """Three policies. Every one of them leaves at least one criterion violated."""
    proba, y_te, g_te, acc = _setup()

    one = group_metrics(proba, y_te, g_te, {0: 0.5, 1: 0.5})
    t_dp = solve_threshold(proba, y_te, g_te, 1, one[0]["selection"], "selection")
    dp = group_metrics(proba, y_te, g_te, {0: 0.5, 1: t_dp})
    t_eo = solve_threshold(proba, y_te, g_te, 1, one[0]["tpr"], "tpr")
    eo = group_metrics(proba, y_te, g_te, {0: 0.5, 1: t_eo})

    policies = [
        ("One threshold\nfor everyone", one),
        (f"Force demographic\nparity (thr {t_dp:.3f})", dp),
        (f"Force equal\nopportunity (thr {t_eo:.3f})", eo),
    ]
    criteria = ["demographic parity", "equal opportunity", "predictive parity"]
    grid = np.array([[_gaps(rows)[c] for c in criteria] for _, rows in policies])

    im = axes.imshow(grid, cmap="RdYlGn_r", vmin=0, vmax=0.65, aspect="auto")
    axes.set_xticks(range(len(criteria)))
    axes.set_xticklabels([c.replace(" ", "\n") for c in criteria], fontsize=9.5)
    axes.set_yticks(range(len(policies)))
    axes.set_yticklabels([name for name, _ in policies], fontsize=9)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            satisfied = grid[i, j] < 0.05
            axes.annotate(f"{grid[i, j]:.4f}", (j, i), ha="center", va="center",
                          fontsize=11,
                          fontweight="bold" if satisfied else "normal",
                          color="black")
            if satisfied:
                from matplotlib.patches import Rectangle
                axes.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                         edgecolor="black", lw=2.4))
    axes.grid(False)
    axes.set_title("Gap between groups — boxed cells are the criterion each "
                   "policy satisfies")
    cb = fig.colorbar(im, ax=axes, fraction=0.03)
    cb.set_label("gap (lower is fairer)", color=p.fg)
    cb.ax.tick_params(colors=p.muted)


def cost_of_parity(fig, axes, p: Palette) -> None:
    """What forcing demographic parity does to the people it is meant to help."""
    proba, y_te, g_te, acc = _setup()

    one = group_metrics(proba, y_te, g_te, {0: 0.5, 1: 0.5})
    t_dp = solve_threshold(proba, y_te, g_te, 1, one[0]["selection"], "selection")
    dp = group_metrics(proba, y_te, g_te, {0: 0.5, 1: t_dp})

    metrics = ["selection", "tpr", "fpr", "precision"]
    labels = ["selection rate", "true positive rate", "false positive rate",
              "precision"]
    idx = np.arange(len(metrics))

    before = [one[1][m] for m in metrics]
    after = [dp[1][m] for m in metrics]

    axes.bar(idx - 0.2, before, 0.4, color=p.muted, label="threshold 0.50")
    axes.bar(idx + 0.2, after, 0.4, color=p.amber,
             label=f"threshold {t_dp:.3f} (parity)")
    for i, (b, a) in enumerate(zip(before, after)):
        axes.annotate(f"{b:.3f}", (i - 0.2, b + 0.02), ha="center", fontsize=8.5,
                      color=p.muted)
        axes.annotate(f"{a:.3f}", (i + 0.2, a + 0.02), ha="center", fontsize=8.5,
                      color=p.amber)
    axes.set_xticks(idx)
    axes.set_xticklabels(labels, rotation=16, ha="right", fontsize=9)
    axes.set_ylim(0, 1.12)
    axes.set_ylabel("rate, group 1 only")
    axes.set_title("Group 1 under parity: more selected and more true positives, "
                   "but precision collapses")
    axes.legend(loc="upper right", fontsize=9)


FIGURES = [
    figure("base-rates", base_rates, size=(7.6, 3.6)),
    figure("impossibility", impossibility, size=(8.4, 3.6)),
    figure("cost-of-parity", cost_of_parity, size=(8.0, 3.8)),
]

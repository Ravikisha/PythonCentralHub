"""Figures for *K-Fold Cross-Validation*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def fold_diagram(fig, ax, p: Palette) -> None:
    """What 5-fold cross-validation actually does to the rows."""
    k = 5
    n = 40
    ax.axis("off")
    row_h = 0.14

    for i in range(k):
        y = 0.82 - i * (row_h + 0.05)
        for j in range(n):
            in_val = (j // (n // k)) == i
            color = p.amber if in_val else p.blue
            ax.add_patch(__import__("matplotlib").patches.Rectangle(
                (0.14 + j * 0.019, y), 0.017, row_h * 0.72,
                facecolor=color, alpha=0.85 if in_val else 0.45, edgecolor="none"))
        ax.text(0.11, y + row_h * 0.36, f"fold {i + 1}", ha="right", va="center",
                fontsize=9, color=p.fg)
        ax.text(0.90, y + row_h * 0.36, f"score$_{i + 1}$", ha="left", va="center",
                fontsize=9, color=p.muted)

    ax.text(0.14, 0.93, "training rows", fontsize=9, color=p.blue)
    ax.text(0.36, 0.93, "validation rows", fontsize=9, color=p.amber)
    ax.text(0.5, 0.04,
            "Every row is validated exactly once and trained on exactly k-1 times.\n"
            "The reported score is the mean of the five, and its spread is the uncertainty.",
            ha="center", fontsize=9, color=p.fg)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("5-fold cross-validation", fontsize=11.5, fontweight="bold", color=p.fg)


def single_split_variance(fig, ax, p: Palette) -> None:
    """How much a score moves purely by choosing a different random split."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = load_breast_cancer(return_X_y=True)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))

    holdout = []
    for seed in range(60):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                                  random_state=seed, stratify=y)
        holdout.append(model.fit(X_tr, y_tr).score(X_te, y_te))

    cv_means = []
    for seed in range(60):
        from sklearn.model_selection import StratifiedKFold
        cv = StratifiedKFold(5, shuffle=True, random_state=seed)
        cv_means.append(cross_val_score(model, X, y, cv=cv).mean())

    ax.hist(holdout, bins=18, color=p.red, alpha=0.62, label=(
        f"single 80/20 split  ·  sd {np.std(holdout):.4f}"))
    ax.hist(cv_means, bins=18, color=p.green, alpha=0.72, label=(
        f"5-fold CV mean  ·  sd {np.std(cv_means):.4f}"))

    ax.set_xlabel("reported accuracy")
    ax.set_ylabel("how often, out of 60 seeds")
    ax.set_title("The same model, the same data, 60 different random seeds")
    ax.legend(loc="upper left", fontsize=8.5)


def cv_strategies(fig, axes, p: Palette) -> None:
    """Four splitters, and the row assignment each produces."""
    from sklearn.model_selection import (GroupKFold, KFold, StratifiedKFold,
                                         TimeSeriesSplit)

    n = 40
    rng = np.random.default_rng(0)
    y = np.r_[np.zeros(32, dtype=int), np.ones(8, dtype=int)]
    groups = np.repeat(np.arange(10), 4)

    axs = fig.subplots(4, 1, sharex=True)
    setups = [
        ("KFold", KFold(4), None, None),
        ("StratifiedKFold", StratifiedKFold(4), y, None),
        ("GroupKFold", GroupKFold(4), None, groups),
        ("TimeSeriesSplit", TimeSeriesSplit(4), None, None),
    ]

    for ax, (name, splitter, strat, grp) in zip(axs, setups):
        X = np.zeros((n, 1))
        for i, (tr, va) in enumerate(splitter.split(X, strat, grp)):
            ax.scatter(tr, np.full(len(tr), i), marker="_", s=140, linewidth=7,
                       color=p.blue, alpha=0.55)
            ax.scatter(va, np.full(len(va), i), marker="_", s=140, linewidth=7,
                       color=p.amber)
        ax.set_ylabel(name, fontsize=8, rotation=0, ha="right", va="center")
        ax.set_yticks([])
        ax.set_ylim(-0.7, 3.7)
        ax.grid(False)
    axs[-1].set_xlabel("row index")
    fig.suptitle("Blue trains, amber validates — four different notions of a fair split",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("fold-diagram", fold_diagram, size=(8.4, 4.2)),
    figure("single-split-variance", single_split_variance, size=(8.2, 4.4)),
    figure("cv-strategies", cv_strategies, size=(8.6, 4.6), axes=False),
]

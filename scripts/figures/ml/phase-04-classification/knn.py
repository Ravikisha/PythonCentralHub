"""Figures for *K-Nearest Neighbors (KNN)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface, two_moons  # noqa: E402
from _style import Palette, figure  # noqa: E402


def k_effect(fig, axes, p: Palette) -> None:
    """k controls how much the boundary is allowed to wobble."""
    from sklearn.neighbors import KNeighborsClassifier

    X, y = two_moons()
    axs = fig.subplots(1, 3, sharey=True)
    for ax, k in zip(axs, (1, 15, 101)):
        model = KNeighborsClassifier(k).fit(X, y)
        decision_surface(ax, model, X, y, p)
        label = {1: "memorises every point", 15: "smooth and sensible",
                 101: "almost the majority class"}[k]
        ax.set_title(f"k = {k}\n{label}", fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("$x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("Small k means high variance, large k means high bias",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def error_vs_k(fig, ax, p: Palette) -> None:
    """Training and cross-validated accuracy as k grows."""
    from sklearn.model_selection import cross_val_score
    from sklearn.neighbors import KNeighborsClassifier

    X, y = two_moons(n=300)
    ks = list(range(1, 60, 2))
    train, cv = [], []
    for k in ks:
        model = KNeighborsClassifier(k)
        train.append(model.fit(X, y).score(X, y))
        cv.append(cross_val_score(model, X, y, cv=5).mean())

    ax.plot(ks, train, color=p.blue, label="training accuracy")
    ax.plot(ks, cv, color=p.amber, marker="o", markersize=3, label="5-fold CV accuracy")
    best = ks[int(np.argmax(cv))]
    ax.axvline(best, color=p.green, linestyle="--", linewidth=1.3,
               label=f"best k = {best}")

    ax.set_xlabel("k")
    ax.set_ylabel("accuracy")
    ax.set_title("k = 1 is perfect on the training set and mediocre everywhere else")
    ax.legend(loc="lower left", fontsize=8.5)


def scaling_matters(fig, axes, p: Palette) -> None:
    """One feature on a wider range hijacks the distance metric entirely."""
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(1)
    n = 160
    # x1 is informative but small in magnitude; x2 is pure noise on a huge scale
    x1 = rng.normal(0, 1, n)
    y = (x1 > 0).astype(int)
    x2 = rng.normal(0, 300, n)
    X = np.c_[x1, x2]

    axs = fig.subplots(1, 2, sharey=True)
    for ax, (model, title) in zip(
        axs,
        [
            (KNeighborsClassifier(11), "Raw features"),
            (make_pipeline(StandardScaler(), KNeighborsClassifier(11)), "Standardised"),
        ],
    ):
        model.fit(X, y)
        acc = model.score(X, y)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], color=p.blue, s=20, alpha=0.8,
                   edgecolor="none")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], color=p.amber, s=20, alpha=0.8,
                   edgecolor="none")
        ax.axvline(0, color=p.green, linestyle="--", linewidth=1.4)
        ax.set_title(f"{title}\ntraining accuracy {acc:.2f}", fontsize=10)
        ax.set_xlabel("$x_1$  (informative, sd = 1)")
    axs[0].set_ylabel("$x_2$  (noise, sd = 300)")
    fig.suptitle("The true boundary is the green line; only one of these models finds it",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("k-effect", k_effect, size=(9.2, 3.6), axes=False),
    figure("error-vs-k", error_vs_k, size=(8.0, 4.2)),
    figure("scaling-matters", scaling_matters, size=(8.6, 4.0), axes=False),
]

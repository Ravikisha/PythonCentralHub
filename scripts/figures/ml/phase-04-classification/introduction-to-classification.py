"""Figures for *Introduction to Classification*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface, imbalanced_blobs, two_moons  # noqa: E402
from _style import Palette, figure  # noqa: E402


def boundaries_three_models(fig, axes, p: Palette) -> None:
    """Three classifiers, one dataset — the boundary is the model's signature."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier

    X, y = two_moons()
    axs = fig.subplots(1, 3, sharey=True)
    models = [
        (LogisticRegression(), "Logistic Regression\none straight line"),
        (KNeighborsClassifier(15), "KNN, k=15\nlocal and wobbly"),
        (DecisionTreeClassifier(max_depth=5, random_state=0), "Decision Tree\naxis-aligned steps"),
    ]
    for ax, (model, title) in zip(axs, models):
        model.fit(X, y)
        decision_surface(ax, model, X, y, p)
        acc = model.score(X, y)
        ax.set_title(f"{title}\ntraining accuracy {acc:.2f}", fontsize=9)
        ax.set_xlabel("$x_1$")
        ax.set_xticks([])
        ax.set_yticks([])
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("Every classifier draws a boundary; the shape it can draw is the model",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def accuracy_paradox(fig, axes, p: Palette) -> None:
    """98% accuracy from a model that has never predicted the positive class."""
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, recall_score

    X, y = imbalanced_blobs()
    axs = fig.subplots(1, 2, width_ratios=[1.15, 1])

    axs[0].scatter(X[y == 0, 0], X[y == 0, 1], color=p.blue, s=14, alpha=0.5,
                   edgecolor="none", label=f"negative ({(y == 0).sum()})")
    axs[0].scatter(X[y == 1, 0], X[y == 1, 1], color=p.amber, s=42,
                   edgecolor=p.bg, linewidth=0.6, label=f"positive ({(y == 1).sum()})")
    axs[0].legend(loc="upper left", fontsize=8)
    axs[0].set_title("2% of the rows are positive", fontsize=10)
    axs[0].set_xticks([])
    axs[0].set_yticks([])

    models = [
        ("always\nnegative", DummyClassifier(strategy="most_frequent")),
        ("logistic\nregression", LogisticRegression()),
    ]
    labels, accs, recalls = [], [], []
    for name, model in models:
        model.fit(X, y)
        pred = model.predict(X)
        labels.append(name)
        accs.append(accuracy_score(y, pred))
        recalls.append(recall_score(y, pred, zero_division=0))

    idx = np.arange(len(labels))
    axs[1].bar(idx - 0.19, accs, width=0.36, color=p.blue, label="accuracy")
    axs[1].bar(idx + 0.19, recalls, width=0.36, color=p.amber, label="recall on positives")
    for i, (a, r) in enumerate(zip(accs, recalls)):
        axs[1].annotate(f"{a:.2f}", (i - 0.19, a), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8.5)
        axs[1].annotate(f"{r:.2f}", (i + 0.19, r), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8.5)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels(labels)
    axs[1].set_ylim(0, 1.12)
    axs[1].legend(loc="upper center", fontsize=8)
    axs[1].set_title("Accuracy hides the failure; recall exposes it", fontsize=10)

    fig.suptitle("The accuracy paradox on a 2% positive class",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("boundaries-three-models", boundaries_three_models, size=(9.2, 3.6), axes=False),
    figure("accuracy-paradox", accuracy_paradox, size=(8.6, 4.0), axes=False),
]

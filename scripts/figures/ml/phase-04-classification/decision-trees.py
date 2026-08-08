"""Figures for *Decision Trees - Entropy and Gini Impurity*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface, iris_two_features, two_moons  # noqa: E402
from _style import Palette, figure  # noqa: E402


def impurity_curves(fig, ax, p: Palette) -> None:
    """Gini, entropy and misclassification error over a binary node."""
    q = np.linspace(1e-6, 1 - 1e-6, 500)
    gini = 2 * q * (1 - q)
    entropy = -(q * np.log2(q) + (1 - q) * np.log2(1 - q))
    error = np.minimum(q, 1 - q)

    ax.plot(q, entropy, color=p.blue, label="entropy (bits)")
    ax.plot(q, entropy / 2, color=p.blue, linestyle=":", linewidth=1.3,
            label="entropy / 2 (rescaled)")
    ax.plot(q, gini, color=p.amber, label="Gini impurity")
    ax.plot(q, error, color=p.red, linestyle="--", label="misclassification error")

    ax.axvline(0.5, color=p.muted, linewidth=1, linestyle=":")
    ax.set_xlabel("proportion of class 1 in the node")
    ax.set_ylabel("impurity")
    ax.set_title("All three peak at a 50/50 node; only two of them are smooth")
    ax.legend(loc="lower center", fontsize=8.5)


def depth_effect(fig, axes, p: Palette) -> None:
    """Depth is the capacity dial, and it overfits fast."""
    from sklearn.tree import DecisionTreeClassifier

    X, y = two_moons(n=200, noise=0.3, seed=8)
    axs = fig.subplots(1, 3, sharey=True)
    for ax, depth in zip(axs, (1, 4, None)):
        model = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X, y)
        decision_surface(ax, model, X, y, p)
        name = "unlimited" if depth is None else str(depth)
        ax.set_title(f"max_depth = {name}\n{model.get_n_leaves()} leaves  ·  "
                     f"train acc {model.score(X, y):.2f}", fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("$x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("Boundaries are always axis-aligned rectangles — depth just adds more of them",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def depth_vs_accuracy(fig, ax, p: Palette) -> None:
    """Where the tree stops learning and starts memorising."""
    from sklearn.model_selection import cross_val_score
    from sklearn.tree import DecisionTreeClassifier

    X, y = two_moons(n=300, noise=0.3, seed=9)
    depths = list(range(1, 21))
    train, cv = [], []
    for d in depths:
        model = DecisionTreeClassifier(max_depth=d, random_state=0)
        train.append(model.fit(X, y).score(X, y))
        cv.append(cross_val_score(model, X, y, cv=5).mean())

    ax.plot(depths, train, color=p.blue, marker="o", markersize=3.5,
            label="training accuracy")
    ax.plot(depths, cv, color=p.amber, marker="s", markersize=3.5,
            label="5-fold CV accuracy")
    best = depths[int(np.argmax(cv))]
    ax.axvline(best, color=p.green, linestyle="--", linewidth=1.3,
               label=f"best depth = {best}")

    ax.set_xticks(depths[::2])
    ax.set_xlabel("max_depth")
    ax.set_ylabel("accuracy")
    ax.set_title("Training accuracy reaches 1.0 and stays there; CV accuracy peaks and declines")
    ax.legend(loc="lower right", fontsize=8.5)


def iris_tree_boundary(fig, ax, p: Palette) -> None:
    """A depth-2 tree on iris — the boundary you can read off the tree itself."""
    from sklearn.tree import DecisionTreeClassifier

    X, y, names = iris_two_features()
    model = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
    decision_surface(ax, model, X, y, p)

    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, [n.replace("_", " ") for n in names], loc="upper left", fontsize=8.5)
    ax.set_xlabel("petal length (cm)")
    ax.set_ylabel("petal width (cm)")
    ax.set_title("Two splits, three regions — every edge is one if-statement")


FIGURES = [
    figure("impurity-curves", impurity_curves, size=(8.0, 4.4)),
    figure("depth-effect", depth_effect, size=(9.2, 3.6), axes=False),
    figure("depth-vs-accuracy", depth_vs_accuracy, size=(8.0, 4.2)),
    figure("iris-tree-boundary", iris_tree_boundary, size=(7.4, 4.6)),
]

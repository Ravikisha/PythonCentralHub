"""Shared datasets for the Phase 04 classification figures.

Keeping the data in one place means the decision-boundary plots on the KNN, SVM,
tree and logistic-regression pages all show the *same* points, so a reader can
compare boundaries across pages rather than across datasets.
"""

import numpy as np


def two_moons(n=220, noise=0.22, seed=3):
    from sklearn.datasets import make_moons

    return make_moons(n_samples=n, noise=noise, random_state=seed)


def iris_two_features():
    """Petal length and petal width — the two features that separate iris best."""
    from sklearn.datasets import load_iris

    data = load_iris()
    return data.data[:, (2, 3)], data.target, data.target_names


def imbalanced_blobs(n=1000, positive_rate=0.02, seed=7):
    """A deliberately skewed binary problem for the accuracy-paradox figures."""
    rng = np.random.default_rng(seed)
    n_pos = int(n * positive_rate)
    n_neg = n - n_pos
    neg = rng.normal(loc=(0.0, 0.0), scale=1.0, size=(n_neg, 2))
    pos = rng.normal(loc=(1.6, 1.6), scale=1.1, size=(n_pos, 2))
    X = np.vstack([neg, pos])
    y = np.r_[np.zeros(n_neg, dtype=int), np.ones(n_pos, dtype=int)]
    order = rng.permutation(len(y))
    return X[order], y[order]


def decision_surface(ax, model, X, y, palette, resolution=300, alpha=0.22):
    """Shade the plane by predicted class, then scatter the training points."""
    from matplotlib.colors import ListedColormap

    pad = 0.6
    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, resolution),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, resolution),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    zz = model.predict(grid).reshape(xx.shape)

    classes = np.unique(y)
    colors = [palette.blue, palette.amber, palette.green][: len(classes)]
    ax.contourf(xx, yy, zz, levels=len(classes) - 1 if len(classes) > 2 else 1,
                colors=colors, alpha=alpha)
    ax.contour(xx, yy, zz, levels=len(classes) - 1 if len(classes) > 2 else 1,
               colors=[palette.fg], linewidths=1.1)

    for cls, color in zip(classes, colors):
        mask = y == cls
        ax.scatter(X[mask, 0], X[mask, 1], color=color, s=22,
                   edgecolor=palette.bg, linewidth=0.6, label=f"class {cls}")
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    return ListedColormap(colors)

"""Figures for *Support Vector Machines (SVM)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface, two_moons  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _linearly_separable(seed=4, n=40):
    rng = np.random.default_rng(seed)
    a = rng.normal(loc=(1.2, 1.2), scale=0.55, size=(n // 2, 2))
    b = rng.normal(loc=(3.6, 3.4), scale=0.55, size=(n // 2, 2))
    X = np.vstack([a, b])
    y = np.r_[np.zeros(n // 2, dtype=int), np.ones(n // 2, dtype=int)]
    return X, y


def margin_and_support_vectors(fig, ax, p: Palette) -> None:
    """The decision boundary, the margin, and the handful of points that set it."""
    from sklearn.svm import SVC

    X, y = _linearly_separable()
    model = SVC(kernel="linear", C=1000).fit(X, y)   # large C ≈ hard margin

    ax.scatter(X[y == 0, 0], X[y == 0, 1], color=p.blue, s=34, edgecolor=p.bg,
               linewidth=0.6, label="class 0", zorder=3)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], color=p.amber, s=34, edgecolor=p.bg,
               linewidth=0.6, label="class 1", zorder=3)

    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - 0.8, X[:, 0].max() + 0.8, 300),
        np.linspace(X[:, 1].min() - 0.8, X[:, 1].max() + 0.8, 300),
    )
    zz = model.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contour(xx, yy, zz, levels=[-1, 0, 1], colors=[p.muted, p.green, p.muted],
               linestyles=["--", "-", "--"], linewidths=[1.2, 2.0, 1.2])
    ax.contourf(xx, yy, zz, levels=[-1, 1], colors=[p.green], alpha=0.10)

    sv = model.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], s=190, facecolors="none", edgecolors=p.red,
               linewidth=1.8, label=f"{len(sv)} support vectors", zorder=4)

    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("The margin is set by three points; the other 37 could move freely")
    ax.legend(loc="upper left", fontsize=8.5)


def soft_margin_C(fig, axes, p: Palette) -> None:
    """C is the price of a margin violation."""
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    X, y = two_moons(n=160, noise=0.32, seed=5)
    axs = fig.subplots(1, 3, sharey=True)
    for ax, C in zip(axs, (0.01, 1.0, 100.0)):
        model = make_pipeline(StandardScaler(), SVC(kernel="linear", C=C)).fit(X, y)
        decision_surface(ax, model, X, y, p)
        n_sv = int(model[-1].n_support_.sum())
        ax.set_title(f"C = {C:g}\n{n_sv} support vectors  ·  acc {model.score(X, y):.2f}",
                     fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("$x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("Low C tolerates violations for a wider margin; high C refuses to",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def rbf_gamma(fig, axes, p: Palette) -> None:
    """Gamma sets how far the influence of a single training point reaches."""
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    X, y = two_moons(n=200, noise=0.26, seed=6)
    axs = fig.subplots(1, 3, sharey=True)
    for ax, gamma in zip(axs, (0.1, 1.0, 30.0)):
        model = make_pipeline(StandardScaler(), SVC(kernel="rbf", gamma=gamma, C=10))
        model.fit(X, y)
        decision_surface(ax, model, X, y, p)
        label = {0.1: "too smooth", 1.0: "about right", 30.0: "islands around points"}[gamma]
        ax.set_title(f"gamma = {gamma:g}\n{label}", fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("$x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("The RBF kernel: gamma is an inverse radius of influence",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("margin-and-support-vectors", margin_and_support_vectors, size=(7.6, 5.0)),
    figure("soft-margin-c", soft_margin_C, size=(9.2, 3.6), axes=False),
    figure("rbf-gamma", rbf_gamma, size=(9.2, 3.6), axes=False),
]

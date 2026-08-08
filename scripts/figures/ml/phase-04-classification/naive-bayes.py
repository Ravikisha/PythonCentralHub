"""Figures for *Naive Bayes Classifier*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface  # noqa: E402
from _style import Palette, figure  # noqa: E402


def class_conditionals(fig, ax, p: Palette) -> None:
    """What GaussianNB actually fits: one bell curve per class per feature."""
    from scipy.stats import norm

    grid = np.linspace(-4, 9, 500)
    classes = [
        ("class 0", 1.0, 1.1, 0.6, p.blue),
        ("class 1", 4.5, 1.4, 0.4, p.amber),
    ]

    posterior_num = []
    for name, mu, sigma, prior, color in classes:
        density = norm.pdf(grid, mu, sigma)
        ax.plot(grid, density, color=color, label=f"{name}: $\\mu$={mu}, $\\sigma$={sigma}")
        ax.fill_between(grid, density, alpha=0.12, color=color)
        posterior_num.append(prior * density)

    total = posterior_num[0] + posterior_num[1]
    boundary = grid[np.argmin(np.abs(posterior_num[0] - posterior_num[1]))]
    ax.axvline(boundary, color=p.green, linestyle="--", linewidth=1.5,
               label=f"decision boundary at x = {boundary:.2f}")

    ax2 = ax.twinx()
    ax2.plot(grid, posterior_num[1] / total, color=p.green, linewidth=1.2, alpha=0.65)
    ax2.set_ylabel("P(class 1 | x)", color=p.green)
    ax2.tick_params(axis="y", colors=p.green)
    ax2.grid(False)
    ax2.set_ylim(0, 1.02)

    ax.set_xlabel("feature value")
    ax.set_ylabel("class-conditional density  P(x | class)")
    ax.set_title("Priors times likelihoods, normalised — that is the whole classifier")
    ax.legend(loc="upper right", fontsize=8.5)


def independence_assumption(fig, axes, p: Palette) -> None:
    """Naive Bayes assumes axis-aligned ellipses; correlated data is not that."""
    from sklearn.naive_bayes import GaussianNB
    from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

    rng = np.random.default_rng(11)
    n = 200
    cov = np.array([[1.0, 0.92], [0.92, 1.0]])
    a = rng.multivariate_normal([0, 0], cov, n // 2)
    b = rng.multivariate_normal([2.0, 2.0], cov, n // 2)
    X = np.vstack([a, b])
    y = np.r_[np.zeros(n // 2, dtype=int), np.ones(n // 2, dtype=int)]

    axs = fig.subplots(1, 2, sharey=True)
    for ax, (model, title) in zip(
        axs,
        [
            (GaussianNB(), "Gaussian Naive Bayes\nassumes the features are independent"),
            (QuadraticDiscriminantAnalysis(), "QDA\nmodels the covariance"),
        ],
    ):
        model.fit(X, y)
        decision_surface(ax, model, X, y, p)
        ax.set_title(f"{title}\ntraining accuracy {model.score(X, y):.3f}", fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("$x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.suptitle("Features correlated at 0.92 — and Naive Bayes still classifies well",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("class-conditionals", class_conditionals, size=(8.0, 4.6)),
    figure("independence-assumption", independence_assumption, size=(8.6, 4.2), axes=False),
]

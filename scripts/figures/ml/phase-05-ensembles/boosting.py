"""Figures for *AdaBoost* and *Gradient Boosting*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def alpha_curve(fig, ax, p: Palette) -> None:
    """The AdaBoost predictor weight as a function of its error rate."""
    eps = np.linspace(0.001, 0.999, 500)
    alpha = 0.5 * np.log((1 - eps) / eps)

    ax.plot(eps, alpha, color=p.blue, linewidth=2.2)
    ax.axvline(0.5, color=p.muted, linestyle="--", linewidth=1.3)
    ax.axhline(0, color=p.muted, linewidth=1)
    ax.set_ylim(-3, 3)

    for e in (0.1, 0.3, 0.5, 0.7):
        a = 0.5 * np.log((1 - e) / e)
        ax.plot([e], [a], marker="o", color=p.amber, markersize=7)
        ax.annotate(f"ε={e}\nα={a:+.2f}", (e, a), textcoords="offset points",
                    xytext=(8, 8 if a >= 0 else -26), fontsize=8.5, color=p.amber)

    ax.annotate("worse than chance:\nthe vote is inverted", (0.72, -2.2),
                fontsize=8.5, color=p.red)
    ax.set_xlabel("weighted error rate of the weak learner, ε")
    ax.set_ylabel("predictor weight α")
    ax.set_title("A learner at exactly 50% gets zero say; below 50% its vote is flipped")


def weight_evolution(fig, axes, p: Palette) -> None:
    """Sample weights after each AdaBoost round — misclassified points grow."""
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.tree import DecisionTreeClassifier

    rng = np.random.default_rng(3)
    n = 40
    X = rng.uniform(-3, 3, (n, 2))
    y = (X[:, 0] + 0.6 * X[:, 1] + rng.normal(0, 0.9, n) > 0).astype(int)

    axs = fig.subplots(1, 4, sharey=True)
    weights = np.full(n, 1 / n)

    for round_idx, ax in enumerate(axs):
        stump = DecisionTreeClassifier(max_depth=1, random_state=0)
        stump.fit(X, y, sample_weight=weights)
        pred = stump.predict(X)
        wrong = pred != y
        err = float(weights[wrong].sum() / weights.sum())
        err = min(max(err, 1e-6), 1 - 1e-6)
        alpha = 0.5 * np.log((1 - err) / err)

        for cls, color in ((0, p.blue), (1, p.amber)):
            mask = y == cls
            ax.scatter(X[mask, 0], X[mask, 1], s=weights[mask] * n * 130 + 8,
                       color=color, alpha=0.85, edgecolor=p.bg, linewidth=0.6)
        ax.scatter(X[wrong, 0], X[wrong, 1], s=140, facecolors="none",
                   edgecolors=p.red, linewidth=1.3)
        ax.set_title(f"round {round_idx + 1}\nε={err:.2f}  α={alpha:+.2f}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])

        weights = weights * np.exp(alpha * np.where(wrong, 1, -1))
        weights = weights / weights.sum()

    fig.suptitle("Point size is its weight; red rings mark this round's mistakes",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def residual_shrinking(fig, axes, p: Palette) -> None:
    """Gradient boosting, three stages, each fitting what the last one missed."""
    from sklearn.tree import DecisionTreeRegressor

    rng = np.random.default_rng(1)
    x = np.sort(rng.uniform(-2.2, 2.2, 90)).reshape(-1, 1)
    y = 0.7 * x.ravel() ** 2 + 0.4 * np.sin(4 * x.ravel()) + rng.normal(0, 0.14, 90)

    grid = np.linspace(-2.4, 2.4, 300).reshape(-1, 1)
    axs = fig.subplots(2, 3, sharex=True)

    residual = y.copy()
    running = np.zeros_like(grid.ravel())

    for stage in range(3):
        tree = DecisionTreeRegressor(max_depth=2, random_state=0).fit(x, residual)

        top = axs[0, stage]
        top.scatter(x, residual, s=13, color=p.amber, edgecolor="none")
        top.plot(grid, tree.predict(grid), color=p.red, linewidth=1.8)
        top.axhline(0, color=p.muted, linewidth=1, linestyle="--")
        top.set_title(f"stage {stage + 1}: fit the residual\nMSE {np.mean(residual ** 2):.4f}",
                      fontsize=9)
        top.tick_params(labelsize=7)

        running = running + tree.predict(grid)
        bottom = axs[1, stage]
        bottom.scatter(x, y, s=13, color=p.blue, edgecolor="none")
        bottom.plot(grid, running, color=p.green, linewidth=2.0)
        bottom.set_title("running ensemble", fontsize=9)
        bottom.tick_params(labelsize=7)

        residual = residual - tree.predict(x)

    axs[0, 0].set_ylabel("residual", fontsize=8.5)
    axs[1, 0].set_ylabel("y", fontsize=8.5)
    fig.suptitle("Each tree learns only what the previous ones got wrong",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def learning_rate_grid(fig, ax, p: Palette) -> None:
    """The shrinkage trade: small steps need more of them, and generalise better."""
    from sklearn.datasets import make_hastie_10_2
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split

    X, y = make_hastie_10_2(n_samples=2400, random_state=0)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.35, random_state=0)

    for lr, color in ((1.0, p.red), (0.3, p.amber), (0.1, p.blue), (0.03, p.green)):
        model = GradientBoostingClassifier(n_estimators=1200, learning_rate=lr,
                                           max_depth=3, random_state=0)
        model.fit(X_tr, y_tr)
        errors = [1 - (pred == y_te).mean()
                  for pred in model.staged_predict(X_te)]
        best = int(np.argmin(errors))
        ax.plot(errors, color=color, linewidth=1.4, alpha=0.9,
                label=f"lr={lr}  best {min(errors):.4f} at {best + 1} trees")
        ax.plot([best], [errors[best]], marker="o", color=color, markersize=6)

    ax.set_xscale("log")
    ax.set_ylim(0.05, 0.35)
    ax.set_xlabel("number of trees (log scale)")
    ax.set_ylabel("held-out error rate")
    ax.set_title("Shrinkage buys nothing for free: ten times smaller steps need "
                 "roughly ten times more of them")
    ax.legend(loc="upper right", fontsize=8.5)


FIGURES = [
    figure("alpha-curve", alpha_curve, size=(8.2, 4.4)),
    figure("weight-evolution", weight_evolution, size=(9.4, 3.2), axes=False),
    figure("residual-shrinking", residual_shrinking, size=(9.0, 5.0), axes=False),
    figure("learning-rate-grid", learning_rate_grid, size=(8.2, 4.6)),
]

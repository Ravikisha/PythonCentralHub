"""Figures for *Bagging - Random Forest Regressor/Classifier*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def bootstrap_coverage(fig, ax, p: Palette) -> None:
    """What fraction of the training set each bootstrap sample actually contains."""
    n_values = np.arange(1, 201)
    included = 1 - (1 - 1 / n_values) ** n_values

    ax.plot(n_values, included, color=p.blue, linewidth=2.0)
    ax.axhline(1 - 1 / np.e, color=p.amber, linestyle="--", linewidth=1.6,
               label=f"limit = 1 - 1/e = {1 - 1/np.e:.4f}")
    ax.annotate(f"the other {1/np.e:.1%} are out-of-bag\nand cost nothing to evaluate on",
                (70, 0.70), fontsize=9, color=p.fg)

    ax.set_xlabel("training set size n")
    ax.set_ylabel("expected fraction of rows drawn at least once")
    ax.set_ylim(0.5, 1.02)
    ax.set_title("A bootstrap sample of size n contains about 63.2% of the distinct rows")
    ax.legend(loc="lower right")


def variance_reduction(fig, axes, p: Palette) -> None:
    """One tree against a forest, on the same data — the boundary and the score."""
    from sklearn.datasets import make_moons
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier

    X, y = make_moons(n_samples=300, noise=0.32, random_state=4)
    axs = fig.subplots(1, 3, sharey=True)
    pad = 0.6
    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, 260),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, 260),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]

    models = [
        ("one tree", DecisionTreeClassifier(random_state=0)),
        ("10 trees", RandomForestClassifier(n_estimators=10, random_state=0)),
        ("300 trees", RandomForestClassifier(n_estimators=300, random_state=0)),
    ]
    for ax, (name, model) in zip(axs, models):
        model.fit(X, y)
        zz = model.predict_proba(grid)[:, 1].reshape(xx.shape)
        ax.contourf(xx, yy, zz, levels=12, cmap="coolwarm_r", alpha=0.55)
        ax.contour(xx, yy, zz, levels=[0.5], colors=[p.fg], linewidths=1.4)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], color=p.blue, s=11, edgecolor="none")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], color=p.amber, s=11, edgecolor="none")
        ax.set_title(name, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Averaging turns a jagged, overconfident boundary into a smooth one",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def n_estimators_curve(fig, ax, p: Palette) -> None:
    """Where adding trees stops paying, and why it never starts hurting."""
    from sklearn.datasets import make_moons
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = make_moons(n_samples=800, noise=0.32, random_state=4)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)

    counts = [1, 2, 3, 5, 8, 12, 20, 35, 60, 100, 200, 400]
    test, oob = [], []
    for n in counts:
        model = RandomForestClassifier(n_estimators=n, oob_score=True,
                                       bootstrap=True, random_state=0, n_jobs=-1)
        model.fit(X_tr, y_tr)
        test.append(model.score(X_te, y_te))
        oob.append(model.oob_score_)

    ax.plot(counts, test, color=p.blue, marker="o", markersize=4, label="held-out accuracy")
    ax.plot(counts, oob, color=p.amber, marker="s", markersize=4, label="out-of-bag estimate")
    ax.set_xscale("log")
    ax.set_xlabel("number of trees (log scale)")
    ax.set_ylabel("accuracy")
    ax.set_title("Performance plateaus; more trees never overfit, they only cost time")
    ax.legend(loc="lower right")


def importance_bias(fig, axes, p: Palette) -> None:
    """Impurity importance favours high-cardinality features; permutation does not."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split

    rng = np.random.default_rng(0)
    n = 1200
    signal = rng.normal(size=n)
    y = (signal + rng.normal(0, 0.6, n) > 0).astype(int)

    X = np.c_[
        signal,                                  # informative, continuous
        (signal > 0).astype(float),              # informative, binary
        rng.normal(size=n),                      # noise, continuous
        rng.integers(0, 2, n).astype(float),     # noise, binary
    ]
    names = ["signal\n(continuous)", "signal\n(binary)", "noise\n(continuous)", "noise\n(binary)"]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
    model = RandomForestClassifier(n_estimators=250, random_state=0, n_jobs=-1)
    model.fit(X_tr, y_tr)

    perm = permutation_importance(model, X_te, y_te, n_repeats=15, random_state=0,
                                  n_jobs=-1)

    axs = fig.subplots(1, 2, sharey=False)
    idx = np.arange(len(names))
    axs[0].bar(idx, model.feature_importances_, color=p.red, width=0.6)
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels(names, fontsize=8)
    axs[0].set_ylabel("impurity importance")
    axs[0].set_title("Impurity: the noise column with\nmany split points scores highly",
                     fontsize=9.5)

    axs[1].bar(idx, perm.importances_mean, yerr=perm.importances_std,
               color=p.green, width=0.6, capsize=3)
    axs[1].axhline(0, color=p.muted, linewidth=1)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels(names, fontsize=8)
    axs[1].set_ylabel("permutation importance")
    axs[1].set_title("Permutation: measured on held-out data,\nnoise scores about zero",
                     fontsize=9.5)

    fig.suptitle("The same forest, two importance measures, two different stories",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("bootstrap-coverage", bootstrap_coverage, size=(8.2, 4.4)),
    figure("variance-reduction", variance_reduction, size=(9.2, 3.6), axes=False),
    figure("n-estimators-curve", n_estimators_curve, size=(8.2, 4.4)),
    figure("importance-bias", importance_bias, size=(8.8, 4.2), axes=False),
]

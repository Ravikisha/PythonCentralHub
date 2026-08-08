"""Figures for *Introduction to Regression Analysis*."""

import numpy as np

from _style import Palette, figure


def regression_vs_classification(fig, axes, p: Palette) -> None:
    """The same features, two different target types — two different jobs."""
    axs = fig.subplots(1, 2)
    rng = np.random.default_rng(5)
    x = rng.uniform(0, 10, 60)

    y_cont = 3 * x + 8 + rng.normal(0, 5, 60)
    axs[0].scatter(x, y_cont, color=p.blue, s=24, alpha=0.8, edgecolor="none")
    axs[0].plot([0, 10], [8, 38], color=p.amber, linewidth=2.0)
    axs[0].set_title("Regression: predict a number\noutput lives on a continuous line", fontsize=9.5)
    axs[0].set_ylabel("price ($k)")

    label = (y_cont > y_cont.mean()).astype(int)
    axs[1].scatter(x[label == 0], np.zeros((label == 0).sum()) + 0.05,
                   color=p.blue, s=24, alpha=0.8, edgecolor="none", label="cheap")
    axs[1].scatter(x[label == 1], np.ones((label == 1).sum()) - 0.05,
                   color=p.amber, s=24, alpha=0.8, edgecolor="none", label="expensive")
    axs[1].axvline(x[label == 1].min(), color=p.green, linestyle="--", linewidth=1.4)
    axs[1].set_yticks([0, 1])
    axs[1].set_yticklabels(["class 0", "class 1"])
    axs[1].set_title("Classification: predict a label\noutput is one of a finite set", fontsize=9.5)
    axs[1].legend(loc="center right", fontsize=8)

    for ax in axs:
        ax.set_xlabel("size (100 sqft)")
    fig.suptitle("Same features, different target type", fontsize=11.5,
                 fontweight="bold", color=p.fg)


def baseline_comparison(fig, ax, p: Palette) -> None:
    """Every model must beat the mean baseline before it means anything."""
    from sklearn.datasets import load_diabetes
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor

    data = load_diabetes()
    models = [
        ("mean baseline", DummyRegressor(strategy="mean"), p.muted),
        ("linear regression", LinearRegression(), p.blue),
        ("decision tree", DecisionTreeRegressor(random_state=0), p.red),
        ("random forest", RandomForestRegressor(n_estimators=120, random_state=0), p.green),
    ]

    names, rmses, colors = [], [], []
    for name, model, color in models:
        scores = cross_val_score(model, data.data, data.target, cv=5,
                                 scoring="neg_root_mean_squared_error")
        names.append(name)
        rmses.append(-scores.mean())
        colors.append(color)

    bars = ax.bar(names, rmses, color=colors, width=0.6)
    for bar, value in zip(bars, rmses):
        ax.annotate(f"{value:.1f}", (bar.get_x() + bar.get_width() / 2, value),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9)
    ax.axhline(rmses[0], color=p.muted, linestyle="--", linewidth=1.2)

    ax.set_ylabel("5-fold CV RMSE (lower is better)")
    ax.set_title("A model is only worth reporting once it beats the dashed baseline")


FIGURES = [
    figure("regression-vs-classification", regression_vs_classification, size=(8.4, 4.0), axes=False),
    figure("baseline-comparison", baseline_comparison, size=(8.0, 4.4)),
]

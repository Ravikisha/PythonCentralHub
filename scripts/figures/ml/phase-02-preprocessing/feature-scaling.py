"""Figures for *Feature Scaling (Normalization & Standardization)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load  # noqa: E402
from _style import Palette, figure  # noqa: E402


def three_scalers(fig, axes, p: Palette) -> None:
    """The same column under four treatments — shape survives, range does not."""
    from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

    df = load()
    x = df[["median_income"]].values
    axs = fig.subplots(1, 4, sharey=True)

    treatments = [
        ("raw", x, p.blue),
        ("MinMaxScaler", MinMaxScaler().fit_transform(x), p.amber),
        ("StandardScaler", StandardScaler().fit_transform(x), p.green),
        ("RobustScaler", RobustScaler().fit_transform(x), p.purple),
    ]
    for ax, (name, values, color) in zip(axs, treatments):
        ax.hist(values.ravel(), bins=45, color=color, edgecolor="none", alpha=0.85)
        lo, hi = float(values.min()), float(values.max())
        ax.set_title(f"{name}\n[{lo:.2f}, {hi:.2f}]", fontsize=9)
        ax.tick_params(labelsize=7.5)
        ax.set_yticks([])
    fig.suptitle("Scaling moves and stretches the axis; it never changes the shape",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def outlier_sensitivity(fig, ax, p: Palette) -> None:
    """One extreme value, and what each scaler does to everybody else."""
    from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

    base = np.array([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
    dirty = np.vstack([base, [[1000.0]]])

    rows = [
        ("MinMaxScaler", MinMaxScaler(), p.amber),
        ("StandardScaler", StandardScaler(), p.green),
        ("RobustScaler", RobustScaler(), p.purple),
    ]
    for i, (name, scaler, color) in enumerate(rows):
        scaled = scaler.fit_transform(dirty).ravel()
        normal, outlier = scaled[:-1], scaled[-1]
        span = normal.max() - normal.min()
        ax.scatter(normal, np.full(len(normal), i), color=color, s=40,
                   edgecolor=p.bg, linewidth=0.6, zorder=3)
        ax.annotate(f"{name}: the ten normal points now span {span:.3f}"
                    f"   (outlier at {outlier:.1f})",
                    (0, i + 0.22), fontsize=8.5, color=color)

    ax.set_yticks([])
    ax.set_ylim(-0.6, 3.0)
    ax.set_xlim(-1.2, 2.2)
    ax.set_xlabel("scaled value")
    ax.set_title("Values 1 to 10 plus one reading of 1000, after each scaler")


def scaling_changes_models(fig, ax, p: Palette) -> None:
    """Which models care, measured rather than asserted."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression, SGDRegressor
    from sklearn.model_selection import cross_val_score
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVR

    df = load().dropna()
    X = df.select_dtypes("number").drop(columns=["median_house_value"]).values
    y = df["median_house_value"].values
    subset = np.random.default_rng(0).choice(len(y), 3000, replace=False)
    X, y = X[subset], y[subset]

    models = [
        ("Linear\nRegression", LinearRegression()),
        ("SGD\nRegressor", SGDRegressor(max_iter=2000, tol=1e-4, random_state=0)),
        ("KNN", KNeighborsRegressor(10)),
        ("SVR\n(RBF)", SVR()),
        ("Random\nForest", RandomForestRegressor(n_estimators=60, random_state=0, n_jobs=-1)),
    ]

    raw, scaled = [], []
    for _, model in models:
        r = -cross_val_score(model, X, y, cv=3,
                             scoring="neg_root_mean_squared_error").mean()
        s = -cross_val_score(make_pipeline(StandardScaler(), model), X, y, cv=3,
                             scoring="neg_root_mean_squared_error").mean()
        raw.append(min(r, 1e6))
        scaled.append(min(s, 1e6))

    idx = np.arange(len(models))
    ax.bar(idx - 0.19, raw, width=0.36, color=p.red, label="raw features")
    ax.bar(idx + 0.19, scaled, width=0.36, color=p.green, label="standardised")
    for i, (r, s) in enumerate(zip(raw, scaled)):
        change = (s - r) / r * 100
        ax.annotate(f"{change:+.0f}%", (i + 0.19, s), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8)

    ax.set_yscale("log")
    ax.set_xticks(idx)
    ax.set_xticklabels([n for n, _ in models], fontsize=8.5)
    ax.set_ylabel("3-fold CV RMSE, log scale ($)")
    ax.set_title("Distance and gradient models transform; trees and closed forms do not")
    ax.legend(loc="upper right")


FIGURES = [
    figure("three-scalers", three_scalers, size=(9.2, 3.6), axes=False),
    figure("outlier-sensitivity", outlier_sensitivity, size=(8.4, 3.4)),
    figure("scaling-changes-models", scaling_changes_models, size=(8.4, 4.6)),
]

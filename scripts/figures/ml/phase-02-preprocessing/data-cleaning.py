"""Figures for *Data Cleaning & Handling Missing Values*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load  # noqa: E402
from _style import Palette, figure  # noqa: E402


def missing_pattern(fig, axes, p: Palette) -> None:
    """Where the holes are, and whether the rows with holes look different."""
    df = load()
    axs = fig.subplots(1, 2, width_ratios=[1, 1.2])

    counts = df.isna().sum().sort_values(ascending=False)
    axs[0].barh([c.replace("_", " ") for c in counts.index], counts.values,
                color=[p.red if v else p.blue for v in counts.values], height=0.62)
    axs[0].annotate(f"{counts.iloc[0]} rows  ({counts.iloc[0] / len(df):.2%})",
                    (counts.iloc[0], 0), textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=8.5, color=p.red)
    axs[0].set_xlim(0, counts.iloc[0] * 1.6)
    axs[0].set_xlabel("missing values")
    axs[0].set_title("One column, 207 holes", fontsize=10)

    missing = df["total_bedrooms"].isna()
    axs[1].hist(df.loc[~missing, "median_house_value"], bins=40, density=True,
                color=p.blue, alpha=0.6, label="rows with data")
    axs[1].hist(df.loc[missing, "median_house_value"], bins=40, density=True,
                color=p.amber, alpha=0.6, label="rows missing total_bedrooms")
    axs[1].set_xlabel("median house value ($)")
    axs[1].set_yticks([])
    axs[1].set_title("Do the incomplete rows differ? Check before dropping", fontsize=10)
    axs[1].legend(loc="upper right", fontsize=8)

    fig.suptitle("Missing data has a shape — look at it before choosing a strategy",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def imputation_strategies(fig, ax, p: Palette) -> None:
    """Mean, median and zero, drawn on the distribution they are filling."""
    df = load()
    col = df["total_bedrooms"].dropna()

    ax.hist(col, bins=80, range=(0, 2500), color=p.blue, edgecolor="none", alpha=0.8)
    ax.axvline(col.median(), color=p.green, linewidth=2.0,
               label=f"median = {col.median():.0f}")
    ax.axvline(col.mean(), color=p.amber, linewidth=2.0,
               label=f"mean = {col.mean():.1f}")
    ax.axvline(0, color=p.red, linewidth=2.0, label="zero fill = 0")

    ax.set_xlabel("total bedrooms")
    ax.set_ylabel("districts")
    ax.set_title("A right-skewed column: the mean sits 24% above the median")
    ax.legend(loc="upper right")


def strategy_comparison(fig, ax, p: Palette) -> None:
    """Does the choice actually change the model? Measure instead of guessing."""
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder

    df = load()
    y = df["median_house_value"]
    X = df.drop(columns=["median_house_value"])
    num_cols = X.select_dtypes("number").columns.tolist()
    cat_cols = ["ocean_proximity"]

    results = {}
    for name, strategy in [("mean", "mean"), ("median", "median"),
                           ("constant 0", "constant"), ("most frequent", "most_frequent")]:
        imputer = (SimpleImputer(strategy="constant", fill_value=0)
                   if strategy == "constant" else SimpleImputer(strategy=strategy))
        pre = ColumnTransformer([
            ("num", imputer, num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ])
        model = make_pipeline(pre, RandomForestRegressor(n_estimators=60, random_state=0,
                                                         n_jobs=-1))
        score = -cross_val_score(model, X, y, cv=3,
                                 scoring="neg_root_mean_squared_error").mean()
        results[name] = score

    # dropping the rows entirely, for comparison
    complete = df.dropna()
    Xc = complete.drop(columns=["median_house_value"])
    pre = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])
    model = make_pipeline(pre, RandomForestRegressor(n_estimators=60, random_state=0,
                                                     n_jobs=-1))
    results["drop rows"] = -cross_val_score(
        model, Xc, complete["median_house_value"], cv=3,
        scoring="neg_root_mean_squared_error").mean()

    names = list(results)
    values = [results[n] for n in names]
    colors = [p.green if n == "median" else p.blue for n in names]
    bars = ax.bar(names, values, color=colors, width=0.6)
    for bar, v in zip(bars, values):
        ax.annotate(f"{v:,.0f}", (bar.get_x() + bar.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)

    ax.set_ylim(min(values) * 0.97, max(values) * 1.02)
    ax.set_ylabel("3-fold CV RMSE ($)")
    ax.set_title("Five strategies for 1% of one column — and almost no difference")


FIGURES = [
    figure("missing-pattern", missing_pattern, size=(8.8, 4.0), axes=False),
    figure("imputation-strategies", imputation_strategies, size=(8.0, 4.4)),
    figure("strategy-comparison", strategy_comparison, size=(8.0, 4.4)),
]

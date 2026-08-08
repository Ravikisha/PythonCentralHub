"""Figures for *End-to-End Machine Learning Project (California Housing)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load, with_income_cat  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _prepared():
    """The full Phase 02 pipeline, plus a stratified train/test split."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.model_selection import StratifiedShuffleSplit
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    df = with_income_cat(load())
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(df, df["income_cat"]))
    train = df.iloc[train_idx].drop(columns=["income_cat"])
    test = df.iloc[test_idx].drop(columns=["income_cat"])

    y_train = train["median_house_value"]
    y_test = test["median_house_value"]
    X_train = train.drop(columns=["median_house_value"])
    X_test = test.drop(columns=["median_house_value"])

    num_cols = X_train.select_dtypes("number").columns.tolist()
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["ocean_proximity"]),
    ])
    return pre, X_train, X_test, y_train, y_test, num_cols


def model_comparison(fig, ax, p: Palette) -> None:
    """Three candidates, training error against cross-validated error."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.tree import DecisionTreeRegressor

    pre, X_train, _, y_train, _, _ = _prepared()
    models = [
        ("Linear\nRegression", LinearRegression()),
        ("Decision\nTree", DecisionTreeRegressor(random_state=42)),
        ("Random\nForest", RandomForestRegressor(n_estimators=80, random_state=42, n_jobs=-1)),
    ]

    train_rmse, cv_rmse = [], []
    for _, model in models:
        pipe = make_pipeline(pre, model)
        pipe.fit(X_train, y_train)
        train_rmse.append(mean_squared_error(y_train, pipe.predict(X_train)) ** 0.5)
        cv_rmse.append(-cross_val_score(pipe, X_train, y_train, cv=5,
                                        scoring="neg_root_mean_squared_error").mean())

    idx = np.arange(len(models))
    ax.bar(idx - 0.19, train_rmse, width=0.36, color=p.blue, label="training RMSE")
    ax.bar(idx + 0.19, cv_rmse, width=0.36, color=p.amber, label="5-fold CV RMSE")
    for i, (t, c) in enumerate(zip(train_rmse, cv_rmse)):
        ax.annotate(f"{t:,.0f}", (i - 0.19, t), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8)
        ax.annotate(f"{c:,.0f}", (i + 0.19, c), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8)

    ax.set_xticks(idx)
    ax.set_xticklabels([n for n, _ in models])
    ax.set_ylabel("RMSE ($)")
    ax.set_title("The tree's training RMSE of zero is the clearest overfit in the curriculum")
    ax.legend(loc="upper left")


def feature_importances(fig, ax, p: Palette) -> None:
    """What the tuned forest actually used."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import make_pipeline

    pre, X_train, _, y_train, _, num_cols = _prepared()
    pipe = make_pipeline(pre, RandomForestRegressor(n_estimators=120, random_state=42,
                                                    n_jobs=-1))
    pipe.fit(X_train, y_train)

    cat_names = list(pipe[0].named_transformers_["cat"].categories_[0])
    names = num_cols + cat_names
    importances = pipe[-1].feature_importances_
    order = np.argsort(importances)

    colors = [p.amber if names[i] in cat_names else p.blue for i in order]
    ax.barh([names[i].replace("_", " ") for i in order], importances[order],
            color=colors, height=0.66)
    for rank, i in enumerate(order):
        ax.annotate(f"{importances[i]:.3f}", (importances[i], rank),
                    textcoords="offset points", xytext=(5, 0), va="center", fontsize=7.5)

    ax.set_xlim(0, importances.max() * 1.22)
    ax.set_xlabel("impurity-based importance")
    ax.set_title("median income dominates; INLAND is the one category that matters")


def residual_analysis(fig, axes, p: Palette) -> None:
    """Where the final model is wrong, and whether the errors are structured."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error
    from sklearn.pipeline import make_pipeline

    pre, X_train, X_test, y_train, y_test, _ = _prepared()
    pipe = make_pipeline(pre, RandomForestRegressor(n_estimators=120, random_state=42,
                                                    n_jobs=-1))
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    rmse = mean_squared_error(y_test, pred) ** 0.5

    axs = fig.subplots(1, 2)
    lim = [0, 520000]
    axs[0].plot(lim, lim, color=p.muted, linestyle="--", linewidth=1.3)
    axs[0].scatter(y_test, pred, s=7, alpha=0.22, color=p.blue, edgecolor="none")
    axs[0].set_xlim(lim)
    axs[0].set_ylim(lim)
    axs[0].set_xlabel("actual value ($)")
    axs[0].set_ylabel("predicted ($)")
    axs[0].set_title(f"Predicted against actual  ·  test RMSE ${rmse:,.0f}", fontsize=10)

    resid = y_test - pred
    axs[1].scatter(pred, resid, s=7, alpha=0.22, color=p.amber, edgecolor="none")
    axs[1].axhline(0, color=p.muted, linestyle="--", linewidth=1.3)
    axs[1].set_xlabel("predicted ($)")
    axs[1].set_ylabel("residual ($)")
    axs[1].set_title("Residuals — note the diagonal edge from the price cap", fontsize=10)

    fig.suptitle("The capped districts form the straight line of errors on the right",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("model-comparison", model_comparison, size=(8.0, 4.4)),
    figure("feature-importances", feature_importances, size=(8.0, 4.8)),
    figure("residual-analysis", residual_analysis, size=(8.8, 4.2), axes=False),
]

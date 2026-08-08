"""Figures for *Transformation Pipelines & Custom Transformers*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def leakage_demo(fig, ax, p: Palette) -> None:
    """Feature selection outside the CV loop invents skill from pure noise.

    Every column here is random and unrelated to the target, so the honest
    cross-validated accuracy is 0.50. Selecting the 'best' features on the whole
    dataset before splitting produces a confident, entirely fictional score.
    """
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline

    rng = np.random.default_rng(0)
    n_samples, n_features = 120, 3000
    X = rng.normal(size=(n_samples, n_features))
    y = rng.integers(0, 2, n_samples)          # no relationship whatsoever

    # Wrong: choose features using every row, including the ones held out later
    leaked = SelectKBest(f_classif, k=20).fit_transform(X, y)
    leaky_score = cross_val_score(LogisticRegression(max_iter=2000), leaked, y, cv=5).mean()

    # Right: selection happens inside each fold
    honest = make_pipeline(SelectKBest(f_classif, k=20),
                           LogisticRegression(max_iter=2000))
    honest_score = cross_val_score(honest, X, y, cv=5).mean()

    bars = ax.bar(["select before splitting\n(leaky)", "select inside a pipeline\n(honest)"],
                  [leaky_score, honest_score], color=[p.red, p.green], width=0.5)
    ax.axhline(0.5, color=p.muted, linestyle="--", linewidth=1.4,
               label="true accuracy: 0.50 (the target is random)")
    for bar, v in zip(bars, [leaky_score, honest_score]):
        ax.annotate(f"{v:.3f}", (bar.get_x() + bar.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 5), ha="center", fontsize=10)

    ax.set_ylim(0, 1.0)
    ax.set_ylabel("5-fold CV accuracy")
    ax.set_title("120 rows, 3000 random columns, a random target — and one of these lies")
    ax.legend(loc="upper right", fontsize=8.5)


def pipeline_diagram(fig, ax, p: Palette) -> None:
    """What ColumnTransformer plus Pipeline actually assembles."""
    ax.axis("off")

    def box(x, y, w, h, text, color, fontsize=8.5):
        rect = ax.add_patch(
            __import__("matplotlib").patches.FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.012",
                linewidth=1.4, edgecolor=color,
                facecolor=color, alpha=0.16))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, color=p.fg)
        return rect

    def arrow(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="->", color=p.muted, linewidth=1.3))

    box(0.01, 0.42, 0.15, 0.16, "raw\nDataFrame", p.muted)

    box(0.22, 0.62, 0.26, 0.24,
        "numeric columns\nSimpleImputer(median)\nAttributeAdder\nStandardScaler", p.blue, 8)
    box(0.22, 0.14, 0.26, 0.24,
        "categorical columns\nOneHotEncoder", p.amber, 8)

    box(0.54, 0.38, 0.18, 0.24, "ColumnTransformer\nhstack", p.green, 8.5)
    box(0.78, 0.42, 0.2, 0.16, "estimator\n.fit / .predict", p.purple, 8.5)

    arrow(0.16, 0.52, 0.22, 0.72)
    arrow(0.16, 0.48, 0.22, 0.28)
    arrow(0.48, 0.72, 0.54, 0.55)
    arrow(0.48, 0.28, 0.54, 0.45)
    arrow(0.72, 0.50, 0.78, 0.50)

    ax.text(0.5, 0.03,
            "One object. fit() learns every parameter from the training fold only; "
            "predict() replays them.",
            ha="center", fontsize=8.5, color=p.muted)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("The whole preprocessing graph, as a single estimator",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("leakage-demo", leakage_demo, size=(8.0, 4.4)),
    figure("pipeline-diagram", pipeline_diagram, size=(9.0, 3.8)),
]

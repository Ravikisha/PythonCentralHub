"""Figures for *Creating a Test Set (Avoiding Data Snooping)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load, with_income_cat  # noqa: E402
from _style import Palette, figure  # noqa: E402


def income_categories(fig, axes, p: Palette) -> None:
    """The continuous feature, and the five buckets used to stratify on it."""
    df = with_income_cat(load())
    axs = fig.subplots(1, 2, width_ratios=[1.3, 1])

    axs[0].hist(df["median_income"], bins=50, color=p.blue, edgecolor="none", alpha=0.85)
    for edge in (1.5, 3.0, 4.5, 6.0):
        axs[0].axvline(edge, color=p.amber, linestyle="--", linewidth=1.3)
    axs[0].set_xlabel("median income (tens of thousands of $)")
    axs[0].set_ylabel("districts")
    axs[0].set_title("Continuous, right-skewed, cut at 1.5 / 3 / 4.5 / 6", fontsize=10)

    counts = df["income_cat"].value_counts().sort_index()
    axs[1].bar(counts.index.astype(str), counts.values, color=p.green, width=0.65)
    for i, v in enumerate(counts.values):
        axs[1].annotate(f"{v / len(df):.1%}", (i, v), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8.5)
    axs[1].set_xlabel("income category")
    axs[1].set_ylabel("districts")
    axs[1].set_title("Five strata, none of them tiny", fontsize=10)

    fig.suptitle("Stratifying needs a categorical column, so bucket the continuous one",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def sampling_bias(fig, ax, p: Palette) -> None:
    """How far each sampling scheme drifts from the population proportions."""
    from sklearn.model_selection import StratifiedShuffleSplit, train_test_split

    df = with_income_cat(load())
    overall = df["income_cat"].value_counts(normalize=True).sort_index()

    _, random_test = train_test_split(df, test_size=0.2, random_state=42)
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    _, strat_idx = next(splitter.split(df, df["income_cat"]))
    strat_test = df.iloc[strat_idx]

    random_err = 100 * (random_test["income_cat"].value_counts(normalize=True).sort_index()
                        / overall - 1)
    strat_err = 100 * (strat_test["income_cat"].value_counts(normalize=True).sort_index()
                       / overall - 1)

    idx = np.arange(len(overall))
    ax.bar(idx - 0.19, random_err.values, width=0.36, color=p.red, label="random split")
    ax.bar(idx + 0.19, strat_err.values, width=0.36, color=p.green, label="stratified split")
    ax.axhline(0, color=p.muted, linewidth=1.1)

    for i, v in enumerate(random_err.values):
        ax.annotate(f"{v:+.1f}%", (i - 0.19, v), textcoords="offset points",
                    xytext=(0, 5 if v > 0 else -13), ha="center", fontsize=8)

    ax.set_xticks(idx)
    ax.set_xticklabels([f"cat {c}" for c in overall.index])
    ax.set_ylabel("test-set proportion error (%)")
    ax.set_title("A random split misrepresents the rarest strata by 4 to 5 percent")
    ax.legend(loc="lower left")


FIGURES = [
    figure("income-categories", income_categories, size=(8.8, 4.0), axes=False),
    figure("sampling-bias", sampling_bias, size=(8.0, 4.4)),
]

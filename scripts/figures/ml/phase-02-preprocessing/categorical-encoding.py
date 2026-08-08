"""Figures for *Handling Text & Categorical Attributes*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load  # noqa: E402
from _style import Palette, figure  # noqa: E402


def category_counts(fig, ax, p: Palette) -> None:
    """The one text column, and the tiny category that will break a naive split."""
    df = load()
    counts = df["ocean_proximity"].value_counts()

    colors = [p.red if v < 50 else p.blue for v in counts.values]
    bars = ax.bar(counts.index, counts.values, color=colors, width=0.62)
    for bar, v in zip(bars, counts.values):
        ax.annotate(f"{v:,}", (bar.get_x() + bar.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)

    ax.set_yscale("log")
    ax.set_ylabel("districts (log scale)")
    ax.set_title("ISLAND has 5 rows out of 20,640 — a category a random split can lose entirely")
    ax.tick_params(axis="x", labelsize=8.5)


def ordinal_vs_onehot(fig, axes, p: Palette) -> None:
    """Ordinal invents an ordering; one-hot refuses to."""
    axs = fig.subplots(1, 2, width_ratios=[1, 1.35])

    cats = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
    codes = np.arange(len(cats))
    axs[0].scatter(codes, np.zeros_like(codes), s=90, color=p.red, zorder=3,
                   edgecolor=p.bg, linewidth=0.7)
    for c, name in zip(codes, cats):
        axs[0].annotate(name, (c, 0.06), rotation=45, ha="left", fontsize=7.5,
                        color=p.fg)
    axs[0].annotate("this spacing is a claim:\nISLAND is 'between'\nINLAND and NEAR BAY",
                    (1.1, -0.55), fontsize=8.5, color=p.red)
    axs[0].set_ylim(-0.9, 0.7)
    axs[0].set_yticks([])
    axs[0].set_xticks(codes)
    axs[0].set_xlabel("OrdinalEncoder value")
    axs[0].set_title("Ordinal: one column, a false ordering", fontsize=10)

    grid = np.eye(len(cats))
    axs[1].imshow(grid, cmap="Blues", vmin=0, vmax=1.6)
    axs[1].set_xticks(range(len(cats)))
    axs[1].set_xticklabels(cats, rotation=45, ha="right", fontsize=7.5)
    axs[1].set_yticks(range(len(cats)))
    axs[1].set_yticklabels(cats, fontsize=7.5)
    axs[1].grid(False)
    for i in range(len(cats)):
        for j in range(len(cats)):
            axs[1].annotate(f"{int(grid[i, j])}", (j, i), ha="center", va="center",
                            fontsize=9, color=p.bg if grid[i, j] else p.fg)
    axs[1].set_xlabel("generated columns")
    axs[1].set_ylabel("original value")
    axs[1].set_title("One-hot: five columns, every pair equidistant", fontsize=10)

    fig.suptitle("The encoder chooses what the model is allowed to believe about the categories",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def cardinality_explosion(fig, ax, p: Palette) -> None:
    """Why one-hot stops being an option, and what the alternatives cost."""
    cardinalities = np.array([2, 5, 20, 100, 1000, 50000])
    labels = ["binary\nflag", "ocean\nproximity", "US state\n(+DC)", "product\ncategory",
              "postcode", "user ID"]

    ax.bar(labels, cardinalities, color=[p.blue if c <= 100 else p.red for c in cardinalities],
           width=0.6)
    for i, c in enumerate(cardinalities):
        ax.annotate(f"{c:,} columns", (i, c), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8.5)
    ax.axhline(100, color=p.amber, linestyle="--", linewidth=1.4,
               label="rough point where one-hot stops being sensible")

    ax.set_yscale("log")
    ax.set_ylabel("columns produced by one-hot (log scale)")
    ax.set_title("One-hot creates one column per distinct value, with no upper bound")
    ax.legend(loc="upper left", fontsize=8.5)


FIGURES = [
    figure("category-counts", category_counts, size=(8.0, 4.2)),
    figure("ordinal-vs-onehot", ordinal_vs_onehot, size=(8.8, 4.2), axes=False),
    figure("cardinality-explosion", cardinality_explosion, size=(8.0, 4.2)),
]

"""Figures for *Exploratory Data Analysis & Correlations*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load  # noqa: E402
from _style import Palette, figure  # noqa: E402


def geographic_scatter(fig, ax, p: Palette) -> None:
    """Longitude against latitude — the map draws itself, and price follows the coast."""
    from matplotlib.colors import LinearSegmentedColormap

    df = load()
    cmap = LinearSegmentedColormap.from_list("pch", [p.blue, p.green, p.amber, p.red])

    sc = ax.scatter(df["longitude"], df["latitude"], c=df["median_house_value"],
                    s=df["population"] / 120, cmap=cmap, alpha=0.42,
                    edgecolor="none")
    bar = fig.colorbar(sc, ax=ax)
    bar.set_label("median house value ($)")

    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title("California, plotted from two columns nobody labelled as coordinates")


def correlation_heatmap(fig, ax, p: Palette) -> None:
    """The full numeric correlation matrix, ordered by correlation with the target."""
    from matplotlib.colors import LinearSegmentedColormap

    df = load().select_dtypes("number")
    order = df.corr()["median_house_value"].sort_values(ascending=False).index
    corr = df[order].corr()

    cmap = LinearSegmentedColormap.from_list("pchdiv", [p.red, p.bg, p.blue])
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax, shrink=0.82)

    labels = [c.replace("_", " ") for c in corr.columns]
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7.5)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.grid(False)

    for i in range(len(labels)):
        for j in range(len(labels)):
            v = corr.values[i, j]
            ax.annotate(f"{v:.2f}", (j, i), ha="center", va="center", fontsize=6.5,
                        color=p.fg if abs(v) < 0.6 else p.bg)

    ax.set_title("Only one feature correlates strongly with price")


def income_vs_value(fig, ax, p: Palette) -> None:
    """The strongest relationship, and the data-quality artefacts it exposes."""
    df = load()
    ax.scatter(df["median_income"], df["median_house_value"], s=6, alpha=0.16,
               color=p.blue, edgecolor="none")

    for line in (500001, 450000, 350000, 280000):
        ax.axhline(line, color=p.red if line == 500001 else p.muted,
                   linestyle="--", linewidth=1.4 if line == 500001 else 1.0,
                   alpha=1.0 if line == 500001 else 0.7)
    ax.annotate("the $500,001 cap — 965 districts", (0.6, 505000), fontsize=8.5,
                color=p.red)
    ax.annotate("fainter horizontal lines at 450k, 350k, 280k", (0.6, 300000),
                fontsize=8.5, color=p.muted)

    ax.set_xlabel("median income (tens of thousands of $)")
    ax.set_ylabel("median house value ($)")
    ax.set_ylim(0, 540000)
    ax.set_title("Correlation 0.69 — and four horizontal artefacts a model would learn")


def engineered_features(fig, ax, p: Palette) -> None:
    """Ratios beat raw counts, because a count only means something per household."""
    df = load()
    df = df.assign(
        rooms_per_household=df["total_rooms"] / df["households"],
        bedrooms_per_room=df["total_bedrooms"] / df["total_rooms"],
        population_per_household=df["population"] / df["households"],
    )
    corr = df.select_dtypes("number").corr()["median_house_value"].drop("median_house_value")
    corr = corr.sort_values()

    engineered = {"rooms_per_household", "bedrooms_per_room", "population_per_household"}
    colors = [p.amber if name in engineered else p.blue for name in corr.index]

    ax.barh([c.replace("_", " ") for c in corr.index], corr.values, color=colors, height=0.66)
    ax.axvline(0, color=p.muted, linewidth=1.1)
    for i, v in enumerate(corr.values):
        ax.annotate(f"{v:+.3f}", (v, i), textcoords="offset points",
                    xytext=(6 if v > 0 else -6, 0), ha="left" if v > 0 else "right",
                    va="center", fontsize=8)

    ax.set_xlim(-0.35, 0.28)
    ax.set_xlabel("correlation with median house value")
    ax.set_title("Amber bars are engineered ratios; two of them beat every raw count")


FIGURES = [
    figure("geographic-scatter", geographic_scatter, size=(7.6, 6.0)),
    figure("correlation-heatmap", correlation_heatmap, size=(7.8, 6.4)),
    figure("income-vs-value", income_vs_value, size=(8.0, 4.8)),
    figure("engineered-features", engineered_features, size=(8.0, 4.6)),
]

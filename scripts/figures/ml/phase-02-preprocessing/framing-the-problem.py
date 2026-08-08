"""Figures for *Framing an ML Problem & Getting the Data*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _housing import load  # noqa: E402
from _style import Palette, figure  # noqa: E402


def target_distribution(fig, ax, p: Palette) -> None:
    """The target, with the artificial ceiling that the raw histogram exposes."""
    df = load()
    y = df["median_house_value"]

    ax.hist(y, bins=60, color=p.blue, edgecolor="none", alpha=0.85)
    capped = int((y == 500001).sum())
    ax.axvline(500001, color=p.red, linestyle="--", linewidth=1.6,
               label=f"hard cap at $500,001 — {capped} districts")
    ax.axvline(y.median(), color=p.amber, linewidth=1.6,
               label=f"median ${y.median():,.0f}")

    ax.set_xlabel("median house value ($)")
    ax.set_ylabel("districts")
    ax.set_title("Always plot the target first — this one has a ceiling somebody imposed")
    ax.legend(loc="upper right", fontsize=8.5)


def feature_histograms(fig, axes, p: Palette) -> None:
    """Nine histograms: skew, caps and unit mismatches in one screen."""
    df = load()
    cols = ["median_income", "housing_median_age", "total_rooms", "total_bedrooms",
            "population", "households", "latitude", "longitude", "median_house_value"]
    axs = fig.subplots(3, 3)
    for ax, col in zip(axs.ravel(), cols):
        ax.hist(df[col].dropna(), bins=40, color=p.blue, edgecolor="none", alpha=0.85)
        ax.set_title(col, fontsize=8.5)
        ax.tick_params(labelsize=7)
        ax.set_yticks([])
    fig.suptitle("Nine features, nine different scales — and several heavy right tails",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def rmse_vs_mae(fig, ax, p: Palette) -> None:
    """How the two candidate performance measures respond to one bad district."""
    rng = np.random.default_rng(0)
    truth = rng.normal(200_000, 60_000, 400)
    base_error = rng.normal(0, 30_000, 400)

    outlier_sizes = np.linspace(0, 900_000, 40)
    rmses, maes = [], []
    for size in outlier_sizes:
        err = base_error.copy()
        err[0] = size
        rmses.append(float(np.sqrt((err**2).mean())))
        maes.append(float(np.abs(err).mean()))

    ax.plot(outlier_sizes / 1000, np.array(rmses) / 1000, color=p.blue, label="RMSE")
    ax.plot(outlier_sizes / 1000, np.array(maes) / 1000, color=p.amber, label="MAE")

    ax.set_xlabel("error on a single district ($ thousands)")
    ax.set_ylabel("reported metric ($ thousands)")
    ax.set_title("One badly predicted district out of 400, and what each measure reports")
    ax.legend(loc="upper left")


FIGURES = [
    figure("target-distribution", target_distribution, size=(8.0, 4.4)),
    figure("feature-histograms", feature_histograms, size=(8.6, 6.2), axes=False),
    figure("rmse-vs-mae", rmse_vs_mae, size=(8.0, 4.2)),
]

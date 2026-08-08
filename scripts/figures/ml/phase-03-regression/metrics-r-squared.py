"""Figures for *Metrics — R-Squared and Adjusted R-Squared*."""

import numpy as np

from _style import Palette, figure

X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
Y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])
PRED = 0.6 * X + 2.2
MEAN = Y.mean()


def variance_decomposition(fig, axes, p: Palette) -> None:
    """SST versus SSE on the same five points — the ratio that defines R-squared."""
    axs = fig.subplots(1, 2, sharey=True)

    axs[0].axhline(MEAN, color=p.muted, linestyle="--", linewidth=1.4)
    for xi, yi in zip(X, Y):
        axs[0].plot([xi, xi], [yi, MEAN], color=p.red, linewidth=2.0)
    axs[0].scatter(X, Y, color=p.amber, s=60, zorder=3, edgecolor=p.bg, linewidth=0.8)
    axs[0].set_title("Baseline: always predict $\\bar{y}=4$\nSST = 6.0", fontsize=10)

    axs[1].plot(X, PRED, color=p.blue, linewidth=2.0)
    for xi, yi, yh in zip(X, Y, PRED):
        axs[1].plot([xi, xi], [yi, yh], color=p.green, linewidth=2.0)
    axs[1].scatter(X, Y, color=p.amber, s=60, zorder=3, edgecolor=p.bg, linewidth=0.8)
    axs[1].set_title("Model: $\\hat{y}=0.6x+2.2$\nSSE = 2.4", fontsize=10)

    for ax in axs:
        ax.set_xlabel("$x$")
        ax.set_ylim(1.4, 6.0)
    axs[0].set_ylabel("$y$")
    fig.suptitle("$R^2 = 1 - 2.4/6.0 = 0.60$ — the model removes 60% of the baseline error",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def r2_inflation(fig, ax, p: Palette) -> None:
    """R-squared always rises with junk features; adjusted R-squared does not."""
    rng = np.random.default_rng(3)
    n = 60
    x_real = rng.normal(size=(n, 2))
    y = 3 * x_real[:, 0] - 2 * x_real[:, 1] + rng.normal(0, 1.5, n)

    ks, r2s, adj = [], [], []
    features = x_real.copy()
    for k in range(2, 41):
        if features.shape[1] < k:  # append pure noise columns
            features = np.c_[features, rng.normal(size=(n, k - features.shape[1]))]
        design = np.c_[np.ones(n), features]
        coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        resid = y - design @ coef
        r2 = 1 - (resid**2).sum() / ((y - y.mean()) ** 2).sum()
        ks.append(k)
        r2s.append(r2)
        adj.append(1 - (1 - r2) * (n - 1) / (n - k - 1))

    ax.plot(ks, r2s, color=p.blue, label="$R^2$")
    ax.plot(ks, adj, color=p.amber, label="adjusted $R^2$")
    ax.axvline(2, color=p.green, linestyle="--", linewidth=1.3,
               label="2 genuinely useful features")

    ax.set_xlabel("number of features (only the first two carry signal)")
    ax.set_ylabel("score")
    ax.set_title("Add pure noise columns: $R^2$ climbs anyway, adjusted $R^2$ punishes you")
    ax.legend(loc="lower left")


def anscombe(fig, axes, p: Palette) -> None:
    """Four datasets, one R-squared. Why you always plot as well as score."""
    quartet = {
        "I": ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
              [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
        "II": ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
               [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
        "III": ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
                [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
        "IV": ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
               [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
    }
    axs = fig.subplots(1, 4, sharex=True, sharey=True)
    grid = np.linspace(2, 20, 50)
    for ax, (name, (xs, ys)) in zip(axs, quartet.items()):
        xs, ys = np.array(xs, float), np.array(ys, float)
        coef = np.polyfit(xs, ys, 1)
        pred = np.polyval(coef, xs)
        r2 = 1 - ((ys - pred) ** 2).sum() / ((ys - ys.mean()) ** 2).sum()
        ax.scatter(xs, ys, color=p.amber, s=28, edgecolor="none")
        ax.plot(grid, np.polyval(coef, grid), color=p.blue, linewidth=1.6)
        ax.set_title(f"{name}   $R^2$ = {r2:.2f}", fontsize=9.5)
        ax.set_xlabel("$x$")
    axs[0].set_ylabel("$y$")
    fig.suptitle("Anscombe's quartet: identical fits and identical $R^2$, four different stories",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("variance-decomposition", variance_decomposition, size=(8.4, 4.2), axes=False),
    figure("r2-inflation", r2_inflation, size=(8.0, 4.4)),
    figure("anscombe", anscombe, size=(9.4, 3.2), axes=False),
]

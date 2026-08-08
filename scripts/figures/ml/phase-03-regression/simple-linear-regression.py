"""Figures for *Simple Linear Regression*.

The five-point dataset is the one the page works through by hand. It is chosen
so every intermediate quantity is exact: slope 0.6, intercept 2.2, SSE 2.4,
SST 6, R-squared 0.6. Plot and prose therefore agree to the last digit.
"""

import numpy as np

from _style import Palette, figure

# Ad spend (thousands of $) -> sales (thousands of units).
X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
Y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])

SLOPE = 0.6
INTERCEPT = 2.2
PRED = SLOPE * X + INTERCEPT  # 2.8, 3.4, 4.0, 4.6, 5.2


def fit_and_residuals(fig, ax, p: Palette) -> None:
    """Scatter, the fitted line, and a vertical stem for every residual."""
    grid = np.linspace(0.5, 5.5, 100)
    ax.plot(
        grid,
        SLOPE * grid + INTERCEPT,
        color=p.blue,
        zorder=2,
        label=f"$\\hat{{y}} = {SLOPE}x + {INTERCEPT}$",
    )

    for xi, yi, yh in zip(X, Y, PRED):
        ax.plot([xi, xi], [yi, yh], color=p.red, linewidth=1.6, alpha=0.9, zorder=1)

    ax.scatter(X, Y, color=p.amber, edgecolor=p.bg, linewidth=0.8, s=70, zorder=3,
               label="observed")
    ax.scatter(X, PRED, color=p.blue, edgecolor=p.bg, linewidth=0.8, s=34,
               marker="s", zorder=3, label="predicted")

    ax.annotate(
        "residual $y_3 - \\hat{y}_3 = +1.0$",
        xy=(3.0, 4.5),
        xytext=(3.35, 3.0),
        color=p.red,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1),
    )

    ax.set_xlabel("ad spend (thousands of $)")
    ax.set_ylabel("sales (thousands of units)")
    ax.set_title("Least squares minimises the total squared length of the red stems")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(1.5, 6.0)
    ax.legend(loc="lower right")


def candidate_lines(fig, ax, p: Palette) -> None:
    """Three candidate lines with their SSE — only one is the least-squares fit."""
    grid = np.linspace(0.5, 5.5, 100)
    candidates = [
        (0.6, 2.2, p.blue, "least squares"),
        (1.0, 1.0, p.amber, "too steep"),
        (0.2, 3.4, p.purple, "too flat"),
    ]

    for slope, intercept, color, label in candidates:
        sse = float(((Y - (slope * X + intercept)) ** 2).sum())
        style = "-" if label == "least squares" else "--"
        ax.plot(
            grid,
            slope * grid + intercept,
            color=color,
            linestyle=style,
            linewidth=2.2 if style == "-" else 1.6,
            label=f"$y={slope}x+{intercept}$  ·  SSE = {sse:.1f}",
        )

    ax.scatter(X, Y, color=p.fg, edgecolor=p.bg, linewidth=0.8, s=60, zorder=3)
    ax.set_xlabel("ad spend (thousands of $)")
    ax.set_ylabel("sales (thousands of units)")
    ax.set_title("Every other line scores worse: SSE is smallest at the OLS solution")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(1.0, 6.5)
    ax.legend(loc="lower right")


def residual_plot(fig, ax, p: Palette) -> None:
    """Residuals against fitted values — the diagnostic that reveals bad fits."""
    resid = Y - PRED

    ax.axhline(0, color=p.muted, linewidth=1.2, linestyle="--")
    ax.vlines(PRED, 0, resid, color=p.blue, linewidth=1.6, alpha=0.85)
    ax.scatter(PRED, resid, color=p.amber, edgecolor=p.bg, linewidth=0.8, s=70, zorder=3)

    for xi, ri in zip(PRED, resid):
        ax.annotate(f"{ri:+.1f}", xy=(xi, ri), xytext=(0, 9 if ri > 0 else -16),
                    textcoords="offset points", ha="center", fontsize=8.5, color=p.muted)

    ax.set_xlabel("fitted value $\\hat{y}$")
    ax.set_ylabel("residual $y - \\hat{y}$")
    ax.set_ylim(-1.4, 1.6)
    ax.set_title("Residuals sum to zero and show no pattern — the linear fit is honest")


def real_data_diabetes(fig, ax, p: Palette) -> None:
    """The same model on a real dataset: BMI against disease progression.

    Real data is noisy. The line is still the best straight summary, but it
    explains only about a third of the variance — which is the point.
    """
    from sklearn.datasets import load_diabetes
    from sklearn.linear_model import LinearRegression

    data = load_diabetes()
    bmi = data.data[:, 2].reshape(-1, 1)  # column 2 is the standardised BMI
    target = data.target

    model = LinearRegression().fit(bmi, target)
    r2 = model.score(bmi, target)

    grid = np.linspace(bmi.min(), bmi.max(), 100).reshape(-1, 1)
    ax.scatter(bmi, target, color=p.blue, alpha=0.45, s=22, edgecolor="none",
               label=f"{len(target)} patients")
    ax.plot(grid, model.predict(grid), color=p.amber, linewidth=2.4,
            label=f"OLS fit  ·  $R^2$ = {r2:.2f}")

    ax.set_xlabel("body mass index (standardised)")
    ax.set_ylabel("disease progression after one year")
    ax.set_title("Real data scatters widely around the line — one feature explains only part of it")
    ax.legend(loc="upper left")


FIGURES = [
    figure("fit-and-residuals", fit_and_residuals, size=(8.0, 4.8)),
    figure("candidate-lines", candidate_lines, size=(8.0, 4.6)),
    figure("residual-plot", residual_plot, size=(8.0, 3.6)),
    figure("real-data-diabetes", real_data_diabetes, size=(8.0, 4.6)),
]

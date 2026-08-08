"""Figures for *SHAP Values from Scratch*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import LINEAR_COEFS, LINEAR_NAMES, exact_shapley, known_linear  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _fitted():
    from sklearn.linear_model import LinearRegression

    X, y = known_linear()
    model = LinearRegression().fit(X, y)
    return X, y, model


def shap_waterfall(fig, axes, p: Palette) -> None:
    """One prediction, decomposed exactly. The bars must reach the prediction."""
    X, y, model = _fitted()
    background = X.mean(axis=0)
    x = X[0]
    phi = exact_shapley(model.predict, x, background)

    base = float(model.predict(background.reshape(1, -1))[0])
    pred = float(model.predict(x.reshape(1, -1))[0])

    order = np.argsort(-np.abs(phi))
    running = base
    ticks, labels = [], []
    for row, j in enumerate(order):
        left = min(running, running + phi[j])
        axes.barh(row, abs(phi[j]), left=left,
                  color=p.blue if phi[j] > 0 else p.red, height=0.62)
        axes.annotate(f"{phi[j]:+.4f}",
                      (max(running, running + phi[j]) + 0.05, row),
                      va="center", fontsize=9, color=p.fg)
        ticks.append(row)
        labels.append(f"{LINEAR_NAMES[j]} = {x[j]:+.3f}")
        running += phi[j]

    axes.axvline(base, color=p.muted, ls="--", lw=1.6)
    axes.axvline(pred, color=p.amber, ls="--", lw=2)
    axes.annotate(f"base value {base:+.4f}", (base, len(order) - 0.35),
                  color=p.muted, fontsize=9, ha="right")
    axes.annotate(f"prediction {pred:+.4f}", (pred, -0.75), color=p.amber,
                  fontsize=9, ha="center")

    axes.set_yticks(ticks)
    axes.set_yticklabels(labels, fontsize=9)
    axes.invert_yaxis()
    axes.set_xlabel("model output")
    error = abs(phi.sum() + base - pred)
    axes.set_title(f"base {base:+.4f} + contributions {phi.sum():+.4f} = "
                   f"{pred:+.4f}   (error {error:.1e})")


def shap_recovers_the_truth(fig, axes, p: Palette) -> None:
    """Mean absolute SHAP against the coefficients that actually generated y."""
    X, y, model = _fitted()
    background = X.mean(axis=0)
    phis = np.array([exact_shapley(model.predict, X[i], background)
                     for i in range(120)])
    mean_abs = np.abs(phis).mean(axis=0)

    axs = fig.subplots(1, 2)

    idx = np.arange(len(LINEAR_NAMES))
    axs[0].bar(idx - 0.2, np.abs(LINEAR_COEFS), 0.4, color=p.muted,
               label="|true coefficient|")
    axs[0].bar(idx + 0.2, mean_abs, 0.4, color=p.blue, label="mean |SHAP|")
    for i, v in enumerate(mean_abs):
        axs[0].annotate(f"{v:.4f}", (i + 0.2, v + 0.06), ha="center",
                        fontsize=8.5, color=p.muted)
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels(LINEAR_NAMES, rotation=18, ha="right", fontsize=9)
    axs[0].set_title("Global importance recovers the ranking", fontsize=10.5)
    axs[0].legend(fontsize=8.5)

    for j, col in zip(range(len(LINEAR_NAMES)),
                      [p.blue, p.red, p.green, p.muted]):
        axs[1].scatter(X[:120, j], phis[:, j], s=9, alpha=0.6, color=col,
                       label=LINEAR_NAMES[j])
    axs[1].axhline(0, color=p.muted, lw=1)
    axs[1].set_xlabel("feature value")
    axs[1].set_ylabel("SHAP value")
    axs[1].set_title("Each feature's contribution is linear in its value",
                     fontsize=10.5)
    axs[1].legend(fontsize=8, loc="upper left")

    fig.suptitle("Exact Shapley values on a model whose coefficients are "
                 "3, -2, 1 and 0", fontsize=10.5, color=p.muted)


def shapley_cost(fig, axes, p: Palette) -> None:
    """Why every production library approximates: the subset count is 2^p."""
    ps = np.arange(1, 26)
    subsets = 2.0 ** ps

    axes.plot(ps, subsets, "o-", color=p.blue)
    axes.set_yscale("log")
    axes.set_xlabel("number of features, p")
    axes.set_ylabel("subsets to evaluate, 2^p (log scale)")

    for mark, note in ((4, "this page: 16"), (10, "1,024"), (20, "1,048,576")):
        axes.scatter([mark], [2.0 ** mark], s=110, facecolors="none",
                     edgecolors=p.amber, linewidths=2, zorder=5)
        axes.annotate(note, (mark + 0.4, 2.0 ** mark * 0.35), color=p.amber,
                      fontsize=9)

    axes.axhline(1e6, color=p.red, ls="--", lw=1.3)
    axes.annotate("a million model calls per explained row", (1.2, 1.6e6),
                  color=p.red, fontsize=9)
    axes.set_title("Exact Shapley is O(2^p) — fine at 4 features, hopeless at 20")


FIGURES = [
    figure("shap-waterfall", shap_waterfall, size=(8.2, 3.4)),
    figure("shap-recovers-the-truth", shap_recovers_the_truth, size=(8.8, 3.6),
           axes=False),
    figure("shapley-cost", shapley_cost, size=(7.6, 3.8)),
]

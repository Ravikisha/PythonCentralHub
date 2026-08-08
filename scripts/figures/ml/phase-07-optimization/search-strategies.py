"""Figures for *GridSearchCV*, *RandomizedSearchCV* and *The ML Pipeline*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def grid_heatmap(fig, ax, p: Palette) -> None:
    """Every combination the grid tried, and where the winner sits."""
    from matplotlib.colors import LinearSegmentedColormap
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import GridSearchCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    X, y = load_breast_cancer(return_X_y=True)
    Cs = np.logspace(-2, 3, 6)
    gammas = np.logspace(-4, 1, 6)

    search = GridSearchCV(
        make_pipeline(StandardScaler(), SVC()),
        {"svc__C": Cs, "svc__gamma": gammas},
        cv=5, n_jobs=-1,
    ).fit(X, y)

    scores = search.cv_results_["mean_test_score"].reshape(len(Cs), len(gammas))
    cmap = LinearSegmentedColormap.from_list("pch", [p.bg, p.blue, p.green, p.amber])
    im = ax.imshow(scores, cmap=cmap, origin="lower", aspect="auto")
    fig.colorbar(im, ax=ax, label="5-fold CV accuracy")

    ax.set_xticks(range(len(gammas)))
    ax.set_xticklabels([f"{g:.0e}" for g in gammas], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(Cs)))
    ax.set_yticklabels([f"{c:.0e}" for c in Cs], fontsize=8)
    ax.set_xlabel("gamma")
    ax.set_ylabel("C")
    ax.grid(False)

    for i in range(len(Cs)):
        for j in range(len(gammas)):
            ax.annotate(f"{scores[i, j]:.3f}", (j, i), ha="center", va="center",
                        fontsize=6.5,
                        color=p.bg if scores[i, j] > scores.max() - 0.05 else p.fg)

    best_i, best_j = np.unravel_index(scores.argmax(), scores.shape)
    ax.scatter([best_j], [best_i], s=340, facecolors="none", edgecolors=p.red,
               linewidth=2.4)
    ax.set_title(f"36 fits, best {scores.max():.4f} at C={Cs[best_i]:.0e}, "
                 f"gamma={gammas[best_j]:.0e}")


def grid_versus_random(fig, axes, p: Palette) -> None:
    """The classic coverage argument: when one parameter matters and one does not."""
    axs = fig.subplots(1, 2, sharey=True)
    rng = np.random.default_rng(3)

    def important(x):
        return np.exp(-((x - 0.62) ** 2) / 0.02)

    for ax, mode in zip(axs, ("grid", "random")):
        if mode == "grid":
            g = np.linspace(0.08, 0.92, 5)
            xs, ys = np.meshgrid(g, g)
            xs, ys = xs.ravel(), ys.ravel()
            title = "Grid: 25 fits, 5 distinct values\nof the parameter that matters"
        else:
            xs = rng.uniform(0.02, 0.98, 25)
            ys = rng.uniform(0.02, 0.98, 25)
            title = "Random: 25 fits, 25 distinct values\nof the parameter that matters"

        curve = np.linspace(0, 1, 300)
        ax.plot(curve, 0.08 + 0.16 * important(curve), color=p.green, linewidth=1.6)
        ax.fill_between(curve, 0.08, 0.08 + 0.16 * important(curve),
                        color=p.green, alpha=0.16)

        ax.scatter(xs, ys, color=p.amber, s=34, edgecolor=p.bg, linewidth=0.6, zorder=3)
        for x in xs:
            ax.plot([x, x], [0, 0.06], color=p.amber, linewidth=1.2, alpha=0.75)

        best = important(xs).max()
        ax.set_title(f"{title}\nbest value of the useful parameter reached: {best:.2f}",
                     fontsize=9)
        ax.set_xlabel("parameter that matters")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
    axs[0].set_ylabel("parameter that does not")
    fig.suptitle("Same budget of 25 fits, five times the resolution where it counts",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def budget_curve(fig, ax, p: Palette) -> None:
    """How good a random search gets, as a function of how many samples it draws."""
    rng = np.random.default_rng(7)
    trials = 4000
    budgets = np.arange(1, 61)

    quantiles = []
    for b in budgets:
        draws = rng.random((trials, b))
        quantiles.append(draws.max(axis=1))

    median = [np.median(q) for q in quantiles]
    p10 = [np.quantile(q, 0.10) for q in quantiles]

    ax.plot(budgets, median, color=p.blue, label="median result")
    ax.fill_between(budgets, p10, 1.0, color=p.blue, alpha=0.12,
                    label="10th to 100th percentile")
    ax.axhline(0.95, color=p.amber, linestyle="--", linewidth=1.4,
               label="top 5% of the space")
    n95 = int(np.ceil(np.log(1 - 0.95) / np.log(1 - 0.05)))
    ax.axvline(n95, color=p.green, linestyle="--", linewidth=1.4,
               label=f"{n95} draws gives 95% chance of landing there")

    ax.set_xlabel("number of random draws")
    ax.set_ylabel("quality percentile reached")
    ax.set_ylim(0, 1.02)
    ax.set_title("Random search needs 60 draws to be 95% sure of hitting the top 5%")
    ax.legend(loc="lower right", fontsize=8.5)


def nested_cv(fig, ax, p: Palette) -> None:
    """Why tuning and evaluating on the same folds overstates the score."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import GridSearchCV, KFold, cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    X, y = load_breast_cancer(return_X_y=True)
    grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [1e-4, 1e-3, 1e-2, 1e-1]}
    pipe = make_pipeline(StandardScaler(), SVC())

    flat, nested = [], []
    for seed in range(8):
        inner = KFold(4, shuffle=True, random_state=seed)
        outer = KFold(4, shuffle=True, random_state=seed + 100)
        search = GridSearchCV(pipe, grid, cv=inner, n_jobs=-1)
        search.fit(X, y)
        flat.append(search.best_score_)
        nested.append(cross_val_score(search, X, y, cv=outer, n_jobs=-1).mean())

    idx = np.arange(len(flat))
    ax.plot(idx, flat, color=p.red, marker="o", label="best inner-CV score (optimistic)")
    ax.plot(idx, nested, color=p.green, marker="s", label="nested CV score (honest)")
    ax.fill_between(idx, nested, flat, color=p.red, alpha=0.12)

    gap = np.mean(np.array(flat) - np.array(nested))
    ax.set_xlabel("random seed")
    ax.set_ylabel("accuracy")
    ax.set_title(f"Reporting the tuning score overstates accuracy by {gap:.4f} on average")
    ax.legend(loc="lower right", fontsize=8.5)


FIGURES = [
    figure("grid-heatmap", grid_heatmap, size=(8.2, 5.0)),
    figure("grid-versus-random", grid_versus_random, size=(8.8, 4.2), axes=False),
    figure("budget-curve", budget_curve, size=(8.2, 4.4)),
    figure("nested-cv", nested_cv, size=(8.2, 4.4)),
]

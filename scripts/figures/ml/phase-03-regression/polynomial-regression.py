"""Figures for *Polynomial Regression*."""

import numpy as np

from _style import Palette, figure

RNG = np.random.default_rng(7)
N = 120
X = np.sort(RNG.uniform(-3, 3, N))
TRUE = 0.5 * X**2 + X + 2
Y = TRUE + RNG.normal(0, 1.1, N)

# The 40-point subset used for the three-panel under/over-fit picture: a small
# sample makes the degree-15 wiggle obvious in a way 120 points would smooth over.
SMALL = np.sort(RNG.choice(N, 40, replace=False))
XS, YS = X[SMALL], Y[SMALL]


def _polyfit_predict(x_train, y_train, degree, x_eval):
    coef = np.polyfit(x_train, y_train, degree)
    return np.polyval(coef, x_eval)


def degree_comparison(fig, axes, p: Palette) -> None:
    """Degree 1, 2 and 15 on identical data: underfit, fit, overfit."""
    axs = fig.subplots(1, 3, sharey=True)
    grid = np.linspace(-3.2, 3.2, 400)
    setups = [
        (1, "degree 1 — underfits", p.red),
        (2, "degree 2 — fits", p.green),
        (15, "degree 15 — overfits", p.purple),
    ]
    for ax, (deg, title, color) in zip(axs, setups):
        ax.scatter(XS, YS, color=p.blue, s=18, alpha=0.75, edgecolor="none")
        ax.plot(grid, _polyfit_predict(XS, YS, deg, grid), color=color, linewidth=2.1)
        train_mse = float(((YS - _polyfit_predict(XS, YS, deg, XS)) ** 2).mean())
        ax.set_title(f"{title}\ntrain MSE = {train_mse:.2f}", fontsize=9.5)
        ax.set_xlabel("$x$")
        ax.set_ylim(-2, 10)
    axs[0].set_ylabel("$y$")
    fig.suptitle("The same 40 points, three model capacities",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def bias_variance_by_degree(fig, ax, p: Palette) -> None:
    """Train and cross-validated error against polynomial degree — the U-curve.

    A single train/validation split on this much data is noisy enough to pick a
    silly winner, so the validation number is a 5-fold cross-validation mean.
    """
    from sklearn.model_selection import KFold

    degrees = list(range(1, 19))
    folds = list(KFold(n_splits=5, shuffle=True, random_state=1).split(X))
    train, val, sem = [], [], []
    for d in degrees:
        train.append(((Y - _polyfit_predict(X, Y, d, X)) ** 2).mean())
        fold_errors = []
        for tr_idx, va_idx in folds:
            pred = _polyfit_predict(X[tr_idx], Y[tr_idx], d, X[va_idx])
            fold_errors.append(((Y[va_idx] - pred) ** 2).mean())
        val.append(float(np.mean(fold_errors)))
        sem.append(float(np.std(fold_errors, ddof=1) / np.sqrt(len(fold_errors))))

    val_arr, sem_arr = np.array(val), np.array(sem)
    ax.plot(degrees, train, color=p.blue, marker="o", markersize=4, label="training MSE")
    ax.plot(degrees, val_arr, color=p.amber, marker="s", markersize=4, label="5-fold CV MSE")
    ax.fill_between(degrees, val_arr - sem_arr, val_arr + sem_arr,
                    color=p.amber, alpha=0.16, linewidth=0)

    # One-standard-error rule: the simplest model within 1 SE of the best score.
    best_i = int(val_arr.argmin())
    threshold = val_arr[best_i] + sem_arr[best_i]
    chosen = degrees[int(np.argmax(val_arr <= threshold))]
    ax.axvline(chosen, color=p.green, linestyle="--", linewidth=1.4,
               label=f"1-SE rule picks degree {chosen}")

    ax.set_yscale("log")
    ax.set_xlabel("polynomial degree")
    ax.set_ylabel("MSE (log scale)")
    ax.set_title("Training error only ever falls; CV error flattens, then climbs")
    ax.legend(loc="upper center", fontsize=8.5)


def learning_curves(fig, axes, p: Palette) -> None:
    """Learning curves for an underfitting and an overfitting model."""
    from sklearn.model_selection import learning_curve
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression

    axs = fig.subplots(1, 2, sharey=True)
    for ax, deg, title in ((axs[0], 1, "Degree 1 — high bias"),
                           (axs[1], 15, "Degree 15 — high variance")):
        model = make_pipeline(PolynomialFeatures(deg), LinearRegression())
        sizes, train_scores, val_scores = learning_curve(
            model, XS.reshape(-1, 1), YS, cv=5,
            train_sizes=np.linspace(0.2, 1.0, 8),
            scoring="neg_mean_squared_error",
        )
        ax.plot(sizes, -train_scores.mean(axis=1), color=p.blue, marker="o",
                markersize=4, label="training")
        ax.plot(sizes, -val_scores.mean(axis=1), color=p.amber, marker="s",
                markersize=4, label="validation")
        ax.set_yscale("log")
        ax.set_xlabel("training set size")
        ax.set_title(title, fontsize=10)
    axs[0].set_ylabel("MSE (log scale)")
    axs[0].legend(loc="upper right", fontsize=8)
    fig.suptitle("Curves that meet high = underfitting; a persistent gap = overfitting",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("degree-comparison", degree_comparison, size=(9.0, 3.8), axes=False),
    figure("degree-error-curve", bias_variance_by_degree, size=(8.0, 4.4)),
    figure("learning-curves", learning_curves, size=(8.6, 4.0), axes=False),
]

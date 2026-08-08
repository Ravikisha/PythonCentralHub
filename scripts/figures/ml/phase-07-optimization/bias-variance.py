"""Figures for *Bias vs Variance Tradeoff* and *Underfitting vs Overfitting*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402

TRUE_FN = lambda x: np.sin(1.5 * x) + 0.35 * x  # noqa: E731
NOISE = 0.35
X_EVAL = np.linspace(0, 6, 200)


def _sample(rng, n=30):
    x = rng.uniform(0, 6, n)
    return x, TRUE_FN(x) + rng.normal(0, NOISE, n)


def many_fits(fig, axes, p: Palette) -> None:
    """Fifty models of each capacity, fitted on fifty different samples."""
    axs = fig.subplots(1, 3, sharey=True)
    rng = np.random.default_rng(0)

    for ax, degree, title in zip(axs, (1, 4, 15),
                                 ("degree 1 — high bias",
                                  "degree 4 — balanced",
                                  "degree 15 — high variance")):
        preds = []
        for _ in range(50):
            x, y = _sample(rng)
            coef = np.polyfit(x, y, degree)
            preds.append(np.polyval(coef, X_EVAL))
            ax.plot(X_EVAL, preds[-1], color=p.blue, alpha=0.09, linewidth=1)
        mean_pred = np.mean(preds, axis=0)
        ax.plot(X_EVAL, mean_pred, color=p.amber, linewidth=2.2, label="average fit")
        ax.plot(X_EVAL, TRUE_FN(X_EVAL), color=p.green, linewidth=2.0,
                linestyle="--", label="truth")
        ax.set_ylim(-2.5, 4.5)
        ax.set_title(title, fontsize=9.5)
        ax.set_xlabel("$x$")
    axs[0].set_ylabel("$y$")
    axs[0].legend(loc="upper left", fontsize=8)
    fig.suptitle("Bias is how far the average fit sits from the truth; variance is the spread",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def decomposition(fig, ax, p: Palette) -> None:
    """The three terms, measured by simulation across model capacity."""
    rng = np.random.default_rng(1)
    degrees = list(range(1, 13))
    n_runs = 200

    bias2, variance, total = [], [], []
    truth = TRUE_FN(X_EVAL)

    for degree in degrees:
        preds = np.empty((n_runs, len(X_EVAL)))
        for r in range(n_runs):
            x, y = _sample(rng)
            preds[r] = np.polyval(np.polyfit(x, y, degree), X_EVAL)
        mean_pred = preds.mean(axis=0)
        b2 = float(((mean_pred - truth) ** 2).mean())
        var = float(preds.var(axis=0).mean())
        bias2.append(b2)
        variance.append(var)
        total.append(b2 + var + NOISE**2)

    ax.plot(degrees, bias2, color=p.blue, marker="o", markersize=4, label="bias$^2$")
    ax.plot(degrees, variance, color=p.amber, marker="s", markersize=4, label="variance")
    ax.plot(degrees, total, color=p.green, marker="^", markersize=4,
            label="total expected error")
    ax.axhline(NOISE**2, color=p.muted, linestyle=":", linewidth=1.4,
               label=f"irreducible noise = {NOISE**2:.3f}")
    best = degrees[int(np.argmin(total))]
    ax.axvline(best, color=p.red, linestyle="--", linewidth=1.3,
               label=f"minimum at degree {best}")

    ax.set_yscale("log")
    ax.set_xticks(degrees)
    ax.set_xlabel("polynomial degree (model capacity)")
    ax.set_ylabel("error contribution, log scale")
    ax.set_title("Bias falls and variance rises; their sum has a minimum")
    ax.legend(loc="upper center", fontsize=8, ncol=2)


def complexity_curve(fig, ax, p: Palette) -> None:
    """Training against validation error as capacity grows — the U you tune against."""
    from sklearn.model_selection import KFold

    rng = np.random.default_rng(4)
    x, y = _sample(rng, n=120)
    degrees = list(range(1, 16))
    folds = list(KFold(5, shuffle=True, random_state=0).split(x))

    train, val = [], []
    for degree in degrees:
        coef = np.polyfit(x, y, degree)
        train.append(float(((y - np.polyval(coef, x)) ** 2).mean()))
        errs = []
        for tr, va in folds:
            c = np.polyfit(x[tr], y[tr], degree)
            errs.append(float(((y[va] - np.polyval(c, x[va])) ** 2).mean()))
        val.append(float(np.mean(errs)))

    ax.plot(degrees, train, color=p.blue, marker="o", markersize=4, label="training MSE")
    ax.plot(degrees, val, color=p.amber, marker="s", markersize=4, label="5-fold CV MSE")
    best = degrees[int(np.argmin(val))]
    ax.axvline(best, color=p.green, linestyle="--", linewidth=1.4,
               label=f"best degree = {best}")

    ax.annotate("underfitting\nboth errors high", (1.6, max(train) * 0.55),
                fontsize=8.5, color=p.muted)
    ax.annotate("overfitting\ngap opens", (11.2, max(val) * 0.4),
                fontsize=8.5, color=p.muted)

    ax.set_yscale("log")
    ax.set_xticks(degrees)
    ax.set_xlabel("polynomial degree")
    ax.set_ylabel("MSE, log scale")
    ax.set_title("One curve tells you which of the two problems you have")
    ax.legend(loc="upper center", fontsize=8.5)


def learning_curves(fig, axes, p: Palette) -> None:
    """Fixed capacity, growing data — the diagnostic that says whether more data helps."""
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import learning_curve
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures

    rng = np.random.default_rng(5)
    x, y = _sample(rng, n=200)
    axs = fig.subplots(1, 2, sharey=True)

    for ax, degree, label in ((axs[0], 1, "Degree 1 — too rigid"),
                              (axs[1], 15, "Degree 15 — flexible")):
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        sizes, tr, va = learning_curve(
            model, x.reshape(-1, 1), y, cv=5,
            train_sizes=np.linspace(0.1, 1.0, 10),
            scoring="neg_mean_squared_error",
        )
        train_mse, val_mse = -tr.mean(axis=1), -va.mean(axis=1)
        gain = (val_mse[0] - val_mse[-1]) / val_mse[0]

        ax.plot(sizes, train_mse, color=p.blue, marker="o", markersize=4,
                label="training")
        ax.plot(sizes, val_mse, color=p.amber, marker="s", markersize=4,
                label="validation")
        ax.fill_between(sizes, train_mse, val_mse, color=p.muted, alpha=0.14)
        ax.axhline(val_mse[-1], color=p.green, linestyle=":", linewidth=1.2)
        ax.set_yscale("log")
        ax.set_xlabel("training samples")
        ax.set_title(f"{label}\nvalidation MSE {val_mse[0]:.3f} → {val_mse[-1]:.3f}"
                     f"  ({gain:+.0%})", fontsize=9.5)
    axs[0].set_ylabel("MSE, log scale")
    axs[0].legend(loc="upper right", fontsize=8.5)
    fig.suptitle("Does more data help? Only one of these two curves is still falling",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("many-fits", many_fits, size=(9.2, 3.6), axes=False),
    figure("decomposition", decomposition, size=(8.2, 4.8)),
    figure("complexity-curve", complexity_curve, size=(8.2, 4.6)),
    figure("learning-curves", learning_curves, size=(8.8, 4.0), axes=False),
]

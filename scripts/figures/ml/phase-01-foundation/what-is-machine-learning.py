"""Figures for *What is Machine Learning?*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import linear_with_noise  # noqa: E402
from _style import Palette, figure  # noqa: E402


def experience_improves_performance(fig, axes, p: Palette) -> None:
    """Mitchell's definition, plotted: P goes up as E goes up, for fixed T."""
    from collections import Counter

    from sklearn.datasets import load_digits
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = load_digits(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    sizes = [10, 25, 50, 100, 200, 400, 800, len(X_tr)]
    scores = []
    for n in sizes:
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
        m.fit(X_tr[:n], y_tr[:n])
        scores.append(m.score(X_te, y_te))

    baseline = Counter(y_te).most_common(1)[0][1] / len(y_te)
    axes.plot(sizes, scores, "o-", color=p.amber, lw=2.4,
              label="T = label a handwritten digit")
    axes.axhline(baseline, color=p.muted, ls="--", lw=1.4,
                 label=f"always guess the most common digit ({baseline:.4f})")
    for n, s in zip(sizes, scores):
        if n in (sizes[0], sizes[-1]):
            axes.annotate(f"{s:.4f}", (n, s + 0.035), ha="center", fontsize=9,
                          color=p.fg)
    axes.set_xscale("log")
    axes.set_ylim(0, 1.08)
    axes.set_xlabel("E — labelled examples the model has seen")
    axes.set_ylabel("P — accuracy on held-out images")
    axes.set_title("T is fixed. E goes up. P follows. That is the definition.")
    axes.legend(loc="lower right")


def what_fitting_means(fig, axes, p: Palette) -> None:
    """A model is a small set of numbers chosen to minimise an error."""
    from sklearn.linear_model import LinearRegression

    x, y = linear_with_noise(n=40, seed=1)
    X = x.reshape(-1, 1)
    fitted = LinearRegression().fit(X, y)

    axs = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.1]})

    grid = np.linspace(-3, 3, 200).reshape(-1, 1)
    axs[0].scatter(x, y, s=22, c=p.blue, alpha=0.8, edgecolors="none")
    for slope, col, lw in ((0.2, p.muted, 1.2), (1.4, p.muted, 1.2),
                           (float(fitted.coef_[0]), p.amber, 2.6)):
        axs[0].plot(grid, slope * grid + fitted.intercept_, color=col, lw=lw)
    axs[0].set_title(f"The fitted line: slope {fitted.coef_[0]:.4f}", fontsize=10)
    axs[0].set_xticks([])
    axs[0].set_yticks([])

    slopes = np.linspace(-0.5, 2.2, 300)
    errors = [((y - (s * x + fitted.intercept_)) ** 2).mean() for s in slopes]
    axs[1].plot(slopes, errors, color=p.blue, lw=2.2)
    best = float(fitted.coef_[0])
    axs[1].axvline(best, color=p.amber, ls="--", lw=1.8)
    axs[1].scatter([best], [((y - fitted.predict(X)) ** 2).mean()], s=80,
                   c=p.amber, zorder=5)
    axs[1].annotate(f"minimum at slope {best:.4f}\nMSE "
                    f"{((y - fitted.predict(X)) ** 2).mean():.4f}",
                    (best + 0.08, max(errors) * 0.55), fontsize=9, color=p.amber)
    axs[1].set_xlabel("candidate slope")
    axs[1].set_ylabel("mean squared error")
    axs[1].set_title("'Learning' is finding the bottom of this curve",
                     fontsize=10)


def ml_is_not_magic(fig, axes, p: Palette) -> None:
    """A model cannot recover a signal that is not in the features."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    rng = np.random.default_rng(0)
    n = 3000
    y = rng.integers(0, 2, n)

    informative = np.column_stack([
        y + rng.normal(0, 1.1, n), rng.normal(0, 1, n), rng.normal(0, 1, n)])
    useless = rng.normal(0, 1, (n, 3))

    models = [
        ("logistic", lambda: make_pipeline(StandardScaler(),
                                           LogisticRegression(max_iter=2000))),
        ("RBF SVM", lambda: make_pipeline(StandardScaler(), SVC())),
        ("random forest", lambda: RandomForestClassifier(n_estimators=300,
                                                         random_state=0)),
    ]

    x = np.arange(len(models))
    width = 0.36
    for i, (label, X) in enumerate([("features carry signal", informative),
                                    ("features are pure noise", useless)]):
        scores = [cross_val_score(f(), X, y, cv=5).mean() for _, f in models]
        bars = axes.bar(x + (i - 0.5) * width, scores, width,
                        color=p.green if i == 0 else p.red, label=label)
        for b, s in zip(bars, scores):
            axes.annotate(f"{s:.3f}", (b.get_x() + b.get_width() / 2, s + 0.006),
                          ha="center", fontsize=9, color=p.muted)
    axes.axhline(0.5, color=p.muted, ls="--", lw=1.4, label="coin flip")
    axes.set_xticks(x)
    axes.set_xticklabels([m[0] for m in models])
    axes.set_ylabel("5-fold accuracy")
    axes.set_ylim(0.4, 0.95)
    axes.set_title("No algorithm can extract a signal the features do not carry")
    axes.legend(loc="upper right", fontsize=9, ncol=3)


FIGURES = [
    figure("experience-improves-performance", experience_improves_performance,
           size=(7.6, 4.0)),
    figure("what-fitting-means", what_fitting_means, size=(8.6, 3.6), axes=False),
    figure("ml-is-not-magic", ml_is_not_magic, size=(7.8, 4.0)),
]

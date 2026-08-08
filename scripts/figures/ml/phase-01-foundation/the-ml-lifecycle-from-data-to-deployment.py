"""Figures for *The ML Lifecycle - From Data to Deployment*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def data_beats_model(fig, axes, p: Palette) -> None:
    """Changing the data helps more than changing the algorithm."""
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.datasets import make_classification
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    X, y = make_classification(n_samples=1200, n_features=20, n_informative=8,
                               n_redundant=4, class_sep=0.9, random_state=5)
    rng = np.random.default_rng(0)

    # Three data conditions, all fed the SAME four models.
    clean = (X, y)
    noisy_labels = (X, np.where(rng.random(len(y)) < 0.15, 1 - y, y))
    fewer_rows = (X[:150], y[:150])

    models = [
        ("logistic", lambda: make_pipeline(StandardScaler(),
                                           LogisticRegression(max_iter=2000))),
        ("RBF SVM", lambda: make_pipeline(StandardScaler(), SVC())),
        ("random forest", lambda: RandomForestClassifier(n_estimators=200,
                                                         random_state=0)),
        ("grad. boosting", lambda: HistGradientBoostingClassifier(random_state=0)),
    ]
    conditions = [("clean, n=1200", clean),
                  ("15% of labels flipped", noisy_labels),
                  ("clean but n=150", fewer_rows)]

    x = np.arange(len(models))
    width = 0.26
    grid = {}
    for i, (label, (Xi, yi)) in enumerate(conditions):
        scores = [cross_val_score(f(), Xi, yi, cv=5).mean() for _, f in models]
        grid[label] = scores
        axes.bar(x + (i - 1) * width, scores, width,
                 color=[p.green, p.red, p.amber][i], label=label)

    clean = grid["clean, n=1200"]
    algo_spread = max(clean) - min(clean)
    noise_cost = max(clean) - max(grid["15% of labels flipped"])
    axes.set_xticks(x)
    axes.set_xticklabels([m[0] for m in models])
    axes.set_ylabel("5-fold accuracy")
    axes.set_ylim(0.5, 1.12)
    axes.set_title(f"Two levers, the same size: {algo_spread:.4f} from the "
                   f"algorithm, {noise_cost:.4f} from the labels")
    axes.legend(loc="upper left", fontsize=9, ncol=3)


def overfitting_gap(fig, axes, p: Palette) -> None:
    """Train and validation scores diverge as model capacity grows."""
    from sklearn.datasets import make_moons
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier

    X, y = make_moons(n_samples=600, noise=0.32, random_state=0)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.35,
                                              random_state=0, stratify=y)
    depths = list(range(1, 21))
    tr, te = [], []
    for d in depths:
        m = DecisionTreeClassifier(max_depth=d, random_state=0).fit(X_tr, y_tr)
        tr.append(m.score(X_tr, y_tr))
        te.append(m.score(X_te, y_te))

    best = int(np.argmax(te))
    axes.plot(depths, tr, "o-", color=p.blue, label="training accuracy")
    axes.plot(depths, te, "o-", color=p.amber, label="held-out accuracy")
    axes.axvline(depths[best], color=p.green, ls="--", lw=1.5,
                 label=f"best depth {depths[best]} ({te[best]:.4f})")
    axes.fill_between(depths, te, tr, color=p.red, alpha=0.12)
    axes.annotate("the gap IS the overfitting", (13, (tr[12] + te[12]) / 2),
                  color=p.red, fontsize=9, ha="center")
    axes.set_xlabel("decision tree max_depth")
    axes.set_ylabel("accuracy")
    axes.set_xticks(depths[::2])
    axes.set_title("More capacity always helps the training set")
    axes.legend(loc="center right", fontsize=9)


def no_free_lunch(fig, axes, p: Palette) -> None:
    """Four models, four datasets, no column that wins everywhere."""
    from sklearn.datasets import (load_breast_cancer, load_digits, load_wine,
                                  make_moons)
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    datasets = [
        ("moons", *make_moons(n_samples=600, noise=0.25, random_state=0)),
        ("wine", *load_wine(return_X_y=True)),
        ("breast cancer", *load_breast_cancer(return_X_y=True)),
        ("digits", *load_digits(return_X_y=True)),
    ]
    models = [
        ("logistic", lambda: make_pipeline(StandardScaler(),
                                           LogisticRegression(max_iter=3000))),
        ("naive Bayes", lambda: GaussianNB()),
        ("5-NN", lambda: make_pipeline(StandardScaler(),
                                       KNeighborsClassifier(5))),
        ("random forest", lambda: RandomForestClassifier(n_estimators=200,
                                                         random_state=0)),
    ]

    grid = np.zeros((len(datasets), len(models)))
    for i, (_, X, y) in enumerate(datasets):
        for j, (_, f) in enumerate(models):
            grid[i, j] = cross_val_score(f(), X, y, cv=5).mean()

    im = axes.imshow(grid, cmap="viridis", aspect="auto")
    axes.set_xticks(range(len(models)))
    axes.set_xticklabels([m[0] for m in models])
    axes.set_yticks(range(len(datasets)))
    axes.set_yticklabels([d[0] for d in datasets])
    for i in range(len(datasets)):
        winner = int(np.argmax(grid[i]))
        for j in range(len(models)):
            axes.annotate(f"{grid[i, j]:.3f}", (j, i), ha="center", va="center",
                          color="white" if grid[i, j] < grid.max() - 0.12 else "black",
                          fontsize=10,
                          fontweight="bold" if j == winner else "normal")
        axes.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"])
                       .Rectangle((winner - 0.5, i - 0.5), 1, 1, fill=False,
                                  edgecolor="red", lw=2.2))
    axes.grid(False)
    axes.set_title("Best model per row is boxed — the box never stays in "
                   "one column")
    fig.colorbar(im, ax=axes, fraction=0.03).ax.tick_params(colors=p.muted)


def train_dev_split(fig, axes, p: Palette) -> None:
    """How the train-dev set separates overfitting from data mismatch."""
    axes.axis("off")
    blocks = [
        ("TRAIN\nweb photos", 0.0, 0.40, p.blue),
        ("TRAIN-DEV\nweb photos\n(held out)", 0.42, 0.16, p.purple),
        ("DEV\nphone photos", 0.60, 0.20, p.amber),
        ("TEST\nphone photos", 0.82, 0.18, p.green),
    ]
    for label, x0, w, col in blocks:
        axes.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"])
                       .Rectangle((x0, 0.55), w, 0.28, facecolor=col, alpha=0.25,
                                  edgecolor=col, lw=2))
        axes.annotate(label, (x0 + w / 2, 0.69), ha="center", va="center",
                      fontsize=9, color=p.fg)

    gaps = [
        ("train → train-dev gap\n= VARIANCE\n(overfitting)", 0.30, p.purple),
        ("train-dev → dev gap\n= DATA MISMATCH\n(distributions differ)", 0.55, p.amber),
        ("dev → test gap\n= OVERFITTING THE DEV SET\n(too much tuning)", 0.80, p.green),
    ]
    for label, x, col in gaps:
        axes.annotate("", xy=(x + 0.06, 0.50), xytext=(x - 0.06, 0.50),
                      arrowprops=dict(arrowstyle="<->", color=col, lw=1.8))
        axes.annotate(label, (x, 0.30), ha="center", va="center", fontsize=8.5,
                      color=col)
    axes.set_xlim(-0.02, 1.02)
    axes.set_ylim(0.1, 0.95)
    axes.set_title("The train-dev set tells you WHICH problem you have")


FIGURES = [
    figure("data-beats-model", data_beats_model, size=(8.2, 4.2)),
    figure("overfitting-gap", overfitting_gap, size=(7.8, 4.2)),
    figure("no-free-lunch", no_free_lunch, size=(8.0, 3.8)),
    figure("train-dev-split", train_dev_split, size=(8.6, 3.2)),
]

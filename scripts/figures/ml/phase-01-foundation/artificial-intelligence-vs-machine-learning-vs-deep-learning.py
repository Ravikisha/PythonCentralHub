"""Figures for *Artificial Intelligence vs Machine Learning vs Deep Learning*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import tabular_task  # noqa: E402
from _style import Palette, figure  # noqa: E402


def nested_fields(fig, axes, p: Palette) -> None:
    """The containment relationship, with a real example in each ring."""
    from matplotlib.patches import Ellipse

    rings = [
        (5.4, 3.6, p.blue, "ARTIFICIAL INTELLIGENCE"),
        (3.7, 2.5, p.amber, "MACHINE LEARNING"),
        (2.0, 1.35, p.green, "DEEP LEARNING"),
    ]
    for w, h, col, label in rings:
        axes.add_patch(Ellipse((0, 0), w * 2, h * 2, facecolor=col, alpha=0.16,
                               edgecolor=col, lw=2))
        axes.annotate(label, (0, h - 0.42), ha="center", color=col, fontsize=10,
                      fontweight="bold")

    axes.annotate("chess engines · A* search\nexpert systems", (0, -2.85),
                  ha="center", color=p.blue, fontsize=8.5)
    axes.annotate("linear regression · random forests\nk-means · gradient boosting",
                  (0, -1.95), ha="center", color=p.amber, fontsize=8.5)
    axes.annotate("CNNs · transformers\nlarge language models", (0, -0.55),
                  ha="center", color=p.green, fontsize=8.5)

    axes.set_xlim(-6, 6)
    axes.set_ylim(-4.1, 4.1)
    axes.set_aspect("equal")
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    axes.set_title("Every deep learning system is machine learning; "
                   "most AI never was")


def where_deep_learning_wins(fig, axes, p: Palette) -> None:
    """Raw pixels versus structured columns — the same four models on both."""
    from sklearn.datasets import load_digits
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    digits = load_digits()
    Xt, yt = tabular_task()

    models = [
        ("logistic", lambda: make_pipeline(StandardScaler(),
                                           LogisticRegression(max_iter=2000))),
        ("random forest", lambda: RandomForestClassifier(n_estimators=200,
                                                         random_state=0)),
        ("grad. boosting", lambda: HistGradientBoostingClassifier(random_state=0)),
        ("neural net", lambda: make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=900,
                          random_state=0))),
    ]

    tasks = [("Raw pixels\n(digits, 64 features)", digits.data, digits.target),
             ("Structured columns\n(20 tabular features)", Xt, yt)]

    x = np.arange(len(models))
    width = 0.36
    for i, (name, X, y) in enumerate(tasks):
        scores = [cross_val_score(f(), X, y, cv=5).mean() for _, f in models]
        bars = axes.bar(x + (i - 0.5) * width, scores, width,
                        color=p.blue if i == 0 else p.amber, label=name)
        for b, s in zip(bars, scores):
            axes.annotate(f"{s:.3f}", (b.get_x() + b.get_width() / 2, s + 0.006),
                          ha="center", fontsize=8.5, color=p.muted)

    axes.set_xticks(x)
    axes.set_xticklabels([m[0] for m in models])
    axes.set_ylabel("5-fold accuracy")
    axes.set_ylim(0.6, 1.10)
    axes.set_title("At this scale there is no deep-learning advantage at all")
    axes.legend(loc="upper left", fontsize=9, ncol=2)


def data_hunger(fig, axes, p: Palette) -> None:
    """Neural nets need data to overtake; small-n favours the classical model."""
    from sklearn.datasets import load_digits
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    d = load_digits()
    X_tr, X_te, y_tr, y_te = train_test_split(
        d.data, d.target, test_size=0.3, random_state=0, stratify=d.target)

    sizes = [40, 80, 160, 320, 640, 1000, len(X_tr)]
    curves = {"logistic regression": [], "neural net (128, 64)": []}
    for n in sizes:
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
        lr.fit(X_tr[:n], y_tr[:n])
        curves["logistic regression"].append(lr.score(X_te, y_te))

        nn = make_pipeline(StandardScaler(),
                           MLPClassifier(hidden_layer_sizes=(128, 64),
                                         max_iter=1200, random_state=0))
        nn.fit(X_tr[:n], y_tr[:n])
        curves["neural net (128, 64)"].append(nn.score(X_te, y_te))

    for (name, ys), col, dy in zip(curves.items(), (p.blue, p.amber),
                                   (0.014, -0.026)):
        axes.plot(sizes, ys, "o-", color=col, label=name)
        axes.annotate(f"{ys[0]:.4f}", (sizes[0] * 1.06, ys[0] + dy),
                      fontsize=9, color=col, ha="left")
        axes.annotate(f"{ys[-1]:.4f}", (sizes[-1] * 0.94, ys[-1] + dy),
                      fontsize=9, color=col, ha="right")

    cross = next((s for s, a, b in zip(sizes, curves["logistic regression"],
                                       curves["neural net (128, 64)"]) if b > a),
                 None)
    if cross:
        axes.axvline(cross, color=p.muted, ls=":", lw=1.3)
        axes.annotate(f"the curves cross\nat about {cross} examples",
                      (cross * 1.1, 0.80), fontsize=9, color=p.muted)

    axes.set_xscale("log")
    axes.set_ylim(0.72, 1.02)
    axes.set_xlabel("training examples")
    axes.set_ylabel("test accuracy")
    axes.set_title("The simpler model wins when data is scarce")
    axes.legend(loc="lower right")


FIGURES = [
    figure("nested-fields", nested_fields, size=(7.6, 4.6)),
    figure("where-deep-learning-wins", where_deep_learning_wins, size=(8.4, 4.2)),
    figure("data-hunger", data_hunger, size=(7.6, 4.0)),
]

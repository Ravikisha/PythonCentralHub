"""Figures for *Evaluating Models: Generalization and Validation*.

``holdout-variance``
    Thirty different random hold-out splits of the same data, scored with the
    same model. The spread is the reason single-split numbers cannot be trusted.

``leakage``
    Three ways to leak information, each measured against the honest procedure,
    on data with no signal at all — so any accuracy above chance is pure leak.

``learning-curve``
    Training and validation accuracy against training-set size, which is how you
    tell "needs more data" from "needs a different model".
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

SPLITS = 30
SUBSET = 600            # small enough that split choice matters
SIZES = (200, 500, 1000, 2000, 4000, 8000)


@functools.lru_cache(maxsize=1)
def _holdout_spread() -> dict:
    """Same model, same data, 30 different random hold-out splits."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold

    data = dataset("fashion", limit=SUBSET, flat=True)
    x = np.concatenate([data["x_train"], data["x_test"]])[:SUBSET]
    y = np.concatenate([data["y_train"], data["y_test"]])[:SUBSET]

    scores = []
    rng = np.random.default_rng(0)
    for _ in range(SPLITS):
        order = rng.permutation(len(x))
        cut = int(0.8 * len(x))
        train, test = order[:cut], order[cut:]
        model = LogisticRegression(max_iter=400).fit(x[train], y[train])
        scores.append(float(model.score(x[test], y[test])))

    folds = []
    for train, test in KFold(n_splits=5, shuffle=True,
                             random_state=0).split(x):
        model = LogisticRegression(max_iter=400).fit(x[train], y[train])
        folds.append(float(model.score(x[test], y[test])))
    return {"holdout": scores, "folds": folds}


def holdout_variance(fig, axes, p: Palette) -> None:
    result = _holdout_spread()
    left, right = fig.subplots(1, 2)
    scores = np.array(result["holdout"])

    left.hist(scores, bins=12, color=p.blue, alpha=0.85)
    left.axvline(scores.mean(), color=p.amber, lw=2.0,
                 label=f"mean {scores.mean():.4f}")
    left.axvline(scores.min(), color=p.red, lw=1.4, ls="--",
                 label=f"worst {scores.min():.4f}")
    left.axvline(scores.max(), color=p.green, lw=1.4, ls="--",
                 label=f"best {scores.max():.4f}")
    left.set_xlabel("hold-out accuracy")
    left.set_ylabel("splits")
    left.set_title(f"{SPLITS} random 80/20 splits of the same {SUBSET} rows",
                   fontsize=10)
    left.legend(fontsize=8)

    folds = np.array(result["folds"])
    positions = np.arange(len(folds))
    right.bar(positions, folds, 0.55, color=p.blue)
    right.axhline(folds.mean(), color=p.amber, lw=2.0, ls="--",
                  label=f"5-fold mean {folds.mean():.4f} "
                        f"(sd {folds.std(ddof=1):.4f})")
    for x, value in zip(positions, folds):
        right.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                       xytext=(0, 3), ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([f"fold {i + 1}" for i in positions], fontsize=8)
    right.set_ylabel("accuracy")
    right.set_ylim(0, max(folds) * 1.3)
    right.set_title("5-fold cross-validation on the same rows", fontsize=10)
    right.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _leakage() -> dict:
    """Pure noise: random features, random labels. Any lift is a leak."""
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold, cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(0)
    n, features = 200, 2000
    x = rng.standard_normal((n, features))
    y = rng.integers(0, 2, n)
    chance = float(max(np.mean(y), 1 - np.mean(y)))

    honest = make_pipeline(SelectKBest(f_classif, k=20),
                           LogisticRegression(max_iter=500))
    selection = [
        ("selection inside|each fold (honest)",
         float(cross_val_score(honest, x, y, cv=5).mean()), True),
        ("selection using|every row first",
         float(cross_val_score(LogisticRegression(max_iter=500),
                               SelectKBest(f_classif, k=20).fit_transform(x, y),
                               y, cv=5).mean()), False),
        ("scaling too,|before the split",
         float(cross_val_score(
             LogisticRegression(max_iter=500),
             SelectKBest(f_classif, k=20).fit_transform(
                 StandardScaler().fit_transform(x), y),
             y, cv=5).mean()), False),
    ]

    # Duplicated rows only leak once a model can memorise, and only once the
    # split is shuffled so the two copies can land on opposite sides.
    small = x[:, :20]
    shuffled = KFold(n_splits=5, shuffle=True, random_state=0)
    duplicates = [
        ("1-NN, no duplicates|(honest)",
         float(cross_val_score(KNeighborsClassifier(n_neighbors=1), small, y,
                               cv=shuffled).mean()), True),
        ("1-NN, every row|appears twice",
         float(cross_val_score(KNeighborsClassifier(n_neighbors=1),
                               np.repeat(small, 2, axis=0), np.repeat(y, 2),
                               cv=shuffled).mean()), False),
    ]
    return {"selection": selection, "duplicates": duplicates,
            "chance": chance}


def leakage(fig, axes, p: Palette) -> None:
    info = _leakage()
    left, right = fig.subplots(1, 2)

    for ax, rows, title in ((left, info["selection"],
                             "feature selection, logistic regression"),
                            (right, info["duplicates"],
                             "duplicated rows, 1-nearest-neighbour")):
        labels = [r[0].replace("|", "\n") for r in rows]
        values = [r[1] for r in rows]
        positions = np.arange(len(labels))
        ax.bar(positions, values, 0.5,
               color=[p.green if r[2] else p.red for r in rows])
        for x, value in zip(positions, values):
            ax.annotate(f"{value:.4f}", (x, value),
                        textcoords="offset points", xytext=(0, 4),
                        ha="center", fontsize=9, color=p.fg)
        ax.axhline(info["chance"], color=p.amber, lw=1.8, ls="--",
                   label=f"guessing: {info['chance']:.4f}")
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, fontsize=7.5)
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("5-fold cross-validated accuracy")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8, loc="upper left")

@functools.lru_cache(maxsize=1)
def _learning_curve() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=max(SIZES), flat=True)
    train, validation = [], []
    for size in SIZES:
        seed_everything(0)
        model = keras.Sequential([
            keras.layers.Input((784,)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(10, activation="softmax"),
        ])
        model.compile(keras.optimizers.Adam(1e-3),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        model.fit(data["x_train"][:size], data["y_train"][:size], epochs=25,
                  batch_size=64, verbose=0)
        train.append(float(model.evaluate(data["x_train"][:size],
                                          data["y_train"][:size],
                                          verbose=0)[1]))
        validation.append(float(model.evaluate(data["x_test"], data["y_test"],
                                              verbose=0)[1]))
    return {"train": train, "validation": validation}


def learning_curve(fig, axes, p: Palette) -> None:
    result = _learning_curve()
    ax = fig.subplots(1, 1)
    ax.plot(SIZES, result["train"], "o-", ms=6, lw=2.0, color=p.blue,
            label="training accuracy")
    ax.plot(SIZES, result["validation"], "o-", ms=6, lw=2.0, color=p.green,
            label="validation accuracy")
    for size, train, validation in zip(SIZES, result["train"],
                                       result["validation"]):
        ax.annotate(f"{train - validation:+.3f}", (size, train),
                    textcoords="offset points", xytext=(0, 8), ha="center",
                    fontsize=7.5, color=p.muted)
    ax.set_xscale("log")
    ax.set_xticks(list(SIZES))
    ax.set_xticklabels([f"{s:,}" for s in SIZES], fontsize=8)
    ax.set_xlabel("training rows")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0.6, 1.05)
    ax.set_title("The gap above each point is train minus validation",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("holdout-variance", holdout_variance, size=(9.2, 3.6), axes=False),
    figure("leakage", leakage, size=(9.2, 3.8), axes=False),
    figure("learning-curve", learning_curve, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    result = _holdout_spread()
    scores = np.array(result["holdout"])
    folds = np.array(result["folds"])
    print(f"=== {SPLITS} random 80/20 hold-out splits of {SUBSET} rows ===")
    print(f"mean {scores.mean():.4f}  sd {scores.std(ddof=1):.4f}  "
          f"min {scores.min():.4f}  max {scores.max():.4f}  "
          f"range {scores.max() - scores.min():.4f}")
    print(f"5-fold: {[round(f, 4) for f in folds]}")
    print(f"5-fold mean {folds.mean():.4f}  sd {folds.std(ddof=1):.4f}")

    print("\n=== leakage on pure noise (labels are random) ===")
    info = _leakage()
    print(f"guessing the majority class scores {info['chance']:.4f}")
    for group in ("selection", "duplicates"):
        for label, value, honest in info[group]:
            mark = "honest" if honest else "LEAK  "
            print(f"  {mark}  {label.replace('|', ' '):34s} {value:.4f}")

    print("\n=== learning curve ===")
    curve = _learning_curve()
    print(f"{'rows':>8} {'train':>8} {'validation':>11} {'gap':>8}")
    for size, train, validation in zip(SIZES, curve["train"],
                                       curve["validation"]):
        print(f"{size:8d} {train:8.4f} {validation:11.4f} "
              f"{train - validation:8.4f}")

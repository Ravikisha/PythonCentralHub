"""Figures for *First Example: Classifying Newswires (Reuters, Multiclass)*.

``reuters-imbalance``
    46 classes ranked by size, with the majority-class and uniform-guess
    baselines drawn on the same axis. The imbalance is the whole reason
    accuracy alone is a poor score here.

``reuters-bottleneck``
    The same network with a 64-unit and a 4-unit second layer. Squeezing 46
    classes through 4 units destroys information no later layer can recover.

``reuters-confusion``
    Where the trained model's errors actually land: a confusion matrix over the
    ten largest classes.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

NUM_WORDS = 10000
CLASSES = 46
EPOCHS = 20
SPLIT = 7000


def _multi_hot(sequences, dimension: int = NUM_WORDS) -> np.ndarray:
    out = np.zeros((len(sequences), dimension), dtype="float32")
    for i, sequence in enumerate(sequences):
        out[i, sequence] = 1.0
    return out


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    (raw_train, y_train), (raw_test, y_test) = tf().keras.datasets.reuters.load_data(
        num_words=NUM_WORDS)
    x = _multi_hot(raw_train)
    return {
        "counts": np.bincount(y_train, minlength=CLASSES),
        "x_train": x[:SPLIT], "y_train": y_train[:SPLIT],
        "x_val": x[SPLIT:], "y_val": y_train[SPLIT:],
        "x_test": _multi_hot(raw_test), "y_test": y_test,
    }


@functools.lru_cache(maxsize=4)
def _run(second_layer: int) -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((NUM_WORDS,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(second_layer, activation="relu"),
        keras.layers.Dense(CLASSES, activation="softmax"),
    ])
    model.compile("rmsprop", "sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=512, verbose=0,
                        validation_data=(data["x_val"], data["y_val"]))
    predictions = model.predict(data["x_test"], verbose=0).argmax(axis=1)
    return {
        "history": {k: [float(v) for v in vals]
                    for k, vals in history.history.items()},
        "test_accuracy": float((predictions == data["y_test"]).mean()),
        "predictions": predictions,
    }


def reuters_imbalance(fig, axes, p: Palette) -> None:
    counts = _data()["counts"]
    ax = fig.subplots(1, 1)
    ranked = np.sort(counts)[::-1]
    positions = np.arange(len(ranked))
    ax.bar(positions, ranked, color=p.blue)
    total = ranked.sum()

    ax.set_yscale("log")
    ax.set_xlabel("class, largest to smallest (46 topics)")
    ax.set_ylabel("training examples (log scale)")
    ax.annotate(f"largest: {ranked[0]:,} examples\n"
                f"= {ranked[0] / total:.1%} of the data",
                (0, ranked[0]), textcoords="offset points", xytext=(14, -4),
                fontsize=8, color=p.amber)
    ax.annotate(f"smallest: {ranked[-1]} examples", xy=(len(ranked) - 1,
                ranked[-1]), xytext=(len(ranked) - 4, 90), ha="right",
                fontsize=8, color=p.red,
                arrowprops=dict(arrowstyle="->", color=p.red, lw=1.0))
    ax.set_ylim(6, ranked[0] * 3)
    ax.set_title(f"Top 3 topics cover {ranked[:3].sum() / total:.1%} of "
                 f"{total:,} newswires", fontsize=10.5)


def reuters_bottleneck(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for units, color in ((64, p.blue), (4, p.red)):
        run = _run(units)
        curve = run["history"]["val_loss"]
        best = int(np.argmin(curve)) + 1
        left.plot(epochs, curve, "o-", ms=3, lw=1.8, color=color,
                  label=f"{units} units — best {min(curve):.4f} "
                        f"at epoch {best}")
        left.scatter([best], [min(curve)], s=70, facecolors="none",
                     edgecolors=color, lw=1.6, zorder=5)
        right.plot(epochs, run["history"]["val_accuracy"], "o-", ms=3, lw=1.8,
                   color=color,
                   label=f"{units} units — test {run['test_accuracy']:.4f}")

    left.set_xlabel("epoch")
    left.set_ylabel("validation loss")
    left.set_title("loss", fontsize=10)
    left.legend(fontsize=7.5)

    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_ylim(0, 1.0)
    right.set_title("validation accuracy", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


def reuters_confusion(fig, axes, p: Palette) -> None:
    data = _data()
    predictions = _run(64)["predictions"]
    ax = fig.subplots(1, 1)

    top = np.argsort(-data["counts"])[:10]
    matrix = np.zeros((10, 10))
    for i, true_class in enumerate(top):
        rows = data["y_test"] == true_class
        if not rows.any():
            continue
        for j, predicted_class in enumerate(top):
            matrix[i, j] = (predictions[rows] == predicted_class).sum()
        matrix[i] /= rows.sum()

    ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1, interpolation="nearest")
    for i in range(10):
        for j in range(10):
            if matrix[i, j] >= 0.05:
                # The Blues colormap does not follow the page theme, so the
                # text contrast must not either.
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center",
                        fontsize=7,
                        color="#ffffff" if matrix[i, j] > 0.5 else "#1f2933")
    ax.set_xticks(range(10))
    ax.set_xticklabels([str(c) for c in top], fontsize=8)
    ax.set_yticks(range(10))
    ax.set_yticklabels([f"{c} (n={int((data['y_test'] == c).sum())})"
                        for c in top], fontsize=7.5)
    ax.set_xlabel("predicted class id")
    ax.set_ylabel("true class id")
    ax.set_title("Row-normalised errors, ten largest topics", fontsize=10.5)
    ax.grid(False)


FIGURES = [
    figure("reuters-imbalance", reuters_imbalance, size=(7.6, 3.6), axes=False),
    figure("reuters-bottleneck", reuters_bottleneck, size=(9.0, 3.4), axes=False),
    figure("reuters-confusion", reuters_confusion, size=(6.8, 4.4), axes=False),
]


if __name__ == "__main__":
    data = _data()
    counts = data["counts"]
    total = counts.sum()
    print(f"train {total:,}  classes {CLASSES}")
    print(f"largest class {int(np.argmax(counts))}: {counts.max():,} "
          f"({counts.max() / total:.4f})   smallest {counts[counts > 0].min()}")
    for units in (64, 4):
        run = _run(units)
        h = run["history"]
        print(f"\n== second layer {units} units ==")
        print(f"  final val loss {h['val_loss'][-1]:.4f}  "
              f"val acc {h['val_accuracy'][-1]:.4f}  "
              f"test acc {run['test_accuracy']:.4f}")
        print(f"  best val loss {min(h['val_loss']):.4f} at epoch "
              f"{int(np.argmin(h['val_loss'])) + 1}")
    predictions = _run(64)["predictions"]
    print("\nper-class recall for the five largest test classes:")
    for c in np.argsort(-counts)[:5]:
        rows = data["y_test"] == c
        print(f"  class {c:2d}  n={int(rows.sum()):4d}  "
              f"recall {(predictions[rows] == c).mean():.4f}")

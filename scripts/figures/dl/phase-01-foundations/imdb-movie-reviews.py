"""Figures for *First Example: Classifying Movie Reviews (IMDB, Binary)*.

``review-lengths``
    What the raw data actually looks like: a long-tailed length distribution,
    and how sparse the multi-hot encoding of it is.

``imdb-overfitting``
    Training and validation curves for the 16-16-1 network. Validation loss
    turns upward while validation accuracy is still climbing — the reason the
    two curves need separate reading.

``imdb-regularisation``
    The same network with dropout and with L2, against the unregularised
    baseline. Both delay the turn; neither removes it.
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
EPOCHS = 20
SPLIT = 15000          # train on the first 15,000, validate on the last 10,000


def _multi_hot(sequences, dimension: int = NUM_WORDS) -> np.ndarray:
    out = np.zeros((len(sequences), dimension), dtype="float32")
    for i, sequence in enumerate(sequences):
        out[i, sequence] = 1.0
    return out


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    (raw_train, y_train), _ = tf().keras.datasets.imdb.load_data(
        num_words=NUM_WORDS)
    x = _multi_hot(raw_train)
    return {
        "raw": raw_train,
        "lengths": np.array([len(r) for r in raw_train]),
        "x_train": x[:SPLIT], "y_train": y_train[:SPLIT],
        "x_val": x[SPLIT:], "y_val": y_train[SPLIT:],
        "density": float(x.mean()),
    }


def _build(regularisation: str = "none"):
    keras = tf().keras
    penalty = keras.regularizers.l2(0.001) if regularisation == "l2" else None
    layers = [keras.layers.Input((NUM_WORDS,))]
    for _ in range(2):
        layers.append(keras.layers.Dense(16, activation="relu",
                                         kernel_regularizer=penalty))
        if regularisation == "dropout":
            layers.append(keras.layers.Dropout(0.5))
    layers.append(keras.layers.Dense(1, activation="sigmoid"))
    model = keras.Sequential(layers)
    model.compile("rmsprop", "binary_crossentropy", metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=4)
def _history(regularisation: str = "none") -> dict:
    data = _data()
    seed_everything(0)
    model = _build(regularisation)
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=512, verbose=0,
                        validation_data=(data["x_val"], data["y_val"]))
    return {k: [float(v) for v in vals] for k, vals in history.history.items()}


def review_lengths(fig, axes, p: Palette) -> None:
    data = _data()
    left, right = fig.subplots(1, 2)

    lengths = data["lengths"]
    left.hist(lengths, bins=60, range=(0, 1200), color=p.blue, alpha=0.85)
    median = int(np.median(lengths))
    left.axvline(median, color=p.amber, lw=1.8,
                 label=f"median {median} tokens")
    left.axvline(lengths.mean(), color=p.red, lw=1.8, ls="--",
                 label=f"mean {lengths.mean():.0f} tokens")
    left.set_xlabel("tokens in a review")
    left.set_ylabel("reviews")
    left.set_title(f"length is long-tailed (max {lengths.max()})", fontsize=10)
    left.legend(fontsize=7.5)

    # The multi-hot matrix as it is stored: 50 reviews across all 10,000
    # columns. The dense stripe on the left is the common-word end of the
    # vocabulary — indices are assigned by frequency rank.
    patch = np.zeros((50, NUM_WORDS), dtype="float32")
    for i, sequence in enumerate(data["raw"][:50]):
        patch[i, list(sequence)] = 1.0
    right.imshow(patch, aspect="auto", cmap="Blues", interpolation="nearest")
    right.set_xlabel("token index (all 10,000 columns)")
    right.set_ylabel("review")
    right.set_title(f"multi-hot is {100 * data['density']:.2f}% ones "
                    f"({patch[:, 2000:].mean() * 100:.2f}% past index 2,000)",
                    fontsize=10)
    right.grid(False)


def imdb_overfitting(fig, axes, p: Palette) -> None:
    history = _history("none")
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    best = int(np.argmin(history["val_loss"])) + 1

    left.plot(epochs, history["loss"], "o-", ms=3, color=p.blue, label="training")
    left.plot(epochs, history["val_loss"], "o-", ms=3, color=p.red,
              label="validation")
    left.axvline(best, color=p.amber, lw=1.6, ls="--",
                 label=f"best val loss: epoch {best}")
    left.set_xlabel("epoch")
    left.set_ylabel("binary cross-entropy")
    left.set_title("loss — validation turns upward", fontsize=10)
    left.legend(fontsize=7.5)

    right.plot(epochs, history["accuracy"], "o-", ms=3, color=p.blue,
               label="training")
    right.plot(epochs, history["val_accuracy"], "o-", ms=3, color=p.red,
               label="validation")
    right.axvline(best, color=p.amber, lw=1.6, ls="--")
    right.set_xlabel("epoch")
    right.set_ylabel("accuracy")
    right.set_ylim(0.7, 1.02)
    right.set_title("accuracy — a flatter, later story", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


def imdb_regularisation(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    epochs = range(1, EPOCHS + 1)
    styles = {"none": (p.red, "no regularisation"),
              "l2": (p.blue, "L2 = 0.001"),
              "dropout": (p.green, "dropout 0.5")}
    for name, (color, label) in styles.items():
        curve = _history(name)["val_loss"]
        best = int(np.argmin(curve)) + 1
        ax.plot(epochs, curve, "o-", ms=3, lw=1.8, color=color,
                label=f"{label} — best {min(curve):.4f} at epoch {best}")
        ax.scatter([best], [min(curve)], s=70, facecolors="none",
                   edgecolors=color, lw=1.6, zorder=5)
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation loss")
    ax.set_title("Regularisation moves the turning point, it does not remove it",
                 fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("review-lengths", review_lengths, size=(9.0, 3.4), axes=False),
    figure("imdb-overfitting", imdb_overfitting, size=(9.0, 3.4), axes=False),
    figure("imdb-regularisation", imdb_regularisation, size=(7.4, 3.8),
           axes=False),
]


if __name__ == "__main__":
    data = _data()
    lengths = data["lengths"]
    print(f"reviews {len(lengths):,}  median {int(np.median(lengths))}  "
          f"mean {lengths.mean():.1f}  max {lengths.max()}")
    print(f"multi-hot density {data['density']:.5f}")
    for name in ("none", "l2", "dropout"):
        h = _history(name)
        best = int(np.argmin(h["val_loss"])) + 1
        print(f"\n== {name} ==")
        print(f"  best val loss {min(h['val_loss']):.4f} at epoch {best}  "
              f"(val acc there {h['val_accuracy'][best - 1]:.4f})")
        print(f"  epoch 20: train loss {h['loss'][-1]:.4f}  "
              f"val loss {h['val_loss'][-1]:.4f}  "
              f"val acc {h['val_accuracy'][-1]:.4f}")

"""Figures for *Batch Normalization*.

``bn-depth``
    A 10-layer sigmoid network with and without BatchNormalization. This is the
    case BN was invented for, and the gap is not subtle.

``bn-learning-rate``
    Final validation accuracy across four learning rates, with and without BN.
    BN's most practical benefit is tolerating a rate that would otherwise fail.

``bn-batch-size``
    BN's weakness: the statistics are estimated per batch, so a small batch means
    a noisy estimate.
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

LIMIT = 8000
DEPTH = 10
WIDTH = 100
RATES = (0.01, 0.1, 0.5, 1.0)
BATCHES = (4, 16, 64, 256)


def _model(normalise: bool, activation: str = "sigmoid", depth: int = DEPTH,
           seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((784,))]
    for _ in range(depth):
        layers.append(keras.layers.Dense(WIDTH, use_bias=not normalise))
        if normalise:
            layers.append(keras.layers.BatchNormalization())
        layers.append(keras.layers.Activation(activation))
    layers.append(keras.layers.Dense(10, activation="softmax"))
    return keras.Sequential(layers)


@functools.lru_cache(maxsize=1)
def _depth_runs() -> dict:
    keras = tf().keras
    data = dataset("mnist", limit=LIMIT, flat=True)
    out = {}
    for label, normalise in (("no BN", False), ("with BN", True)):
        model = _model(normalise)
        model.compile(keras.optimizers.SGD(0.1),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        history = model.fit(data["x_train"], data["y_train"], epochs=20,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[label] = {
            "loss": [float(v) for v in history.history["loss"]],
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
            "trainable": int(sum(np.prod(w.shape)
                                 for w in model.trainable_weights)),
        }
    return out


def bn_depth(fig, axes, p: Palette) -> None:
    runs = _depth_runs()
    left, right = fig.subplots(1, 2)
    colors = {"no BN": p.red, "with BN": p.green}
    for label, run in runs.items():
        epochs = range(1, len(run["loss"]) + 1)
        left.plot(epochs, run["loss"], "o-", ms=3, lw=1.8, color=colors[label],
                  label=label)
        right.plot(epochs, run["val_accuracy"], "o-", ms=3, lw=1.8,
                   color=colors[label],
                   label=f"{label} — {run['val_accuracy'][-1]:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("training loss")
    left.set_title(f"{DEPTH} sigmoid layers of {WIDTH}, SGD 0.1", fontsize=10)
    left.legend(fontsize=8)
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_ylim(0, 1.0)
    right.set_title("validation accuracy", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


@functools.lru_cache(maxsize=1)
def _rate_runs() -> dict:
    keras = tf().keras
    data = dataset("mnist", limit=LIMIT, flat=True)
    out = {}
    for label, normalise in (("no BN", False), ("with BN", True)):
        scores = []
        for rate in RATES:
            model = _model(normalise, activation="relu", depth=5)
            model.compile(keras.optimizers.SGD(rate),
                          "sparse_categorical_crossentropy",
                          metrics=["accuracy"])
            history = model.fit(data["x_train"], data["y_train"], epochs=10,
                                batch_size=128, verbose=0,
                                validation_data=(data["x_test"],
                                                 data["y_test"]))
            scores.append(float(history.history["val_accuracy"][-1]))
        out[label] = scores
    return out


def bn_learning_rate(fig, axes, p: Palette) -> None:
    runs = _rate_runs()
    ax = fig.subplots(1, 1)
    positions = np.arange(len(RATES))
    width = 0.38
    for offset, (label, color) in zip((-width / 2, width / 2),
                                      (("no BN", p.red), ("with BN", p.green))):
        scores = runs[label]
        ax.bar(positions + offset, scores, width, color=color, label=label)
        for x, value in zip(positions + offset, scores):
            ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                        xytext=(0, 3), ha="center", fontsize=7, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"lr = {r:g}" for r in RATES])
    ax.set_ylabel("validation accuracy after 10 epochs")
    ax.set_ylim(0, 1.15)
    ax.set_title("5 relu layers of 100 — how much learning rate can it take?",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")


@functools.lru_cache(maxsize=1)
def _batch_runs() -> dict:
    keras = tf().keras
    data = dataset("mnist", limit=4000, flat=True)
    out = {}
    for label, normalise in (("no BN", False), ("with BN", True)):
        scores = []
        for batch in BATCHES:
            model = _model(normalise, activation="relu", depth=3)
            model.compile(keras.optimizers.SGD(0.05),
                          "sparse_categorical_crossentropy",
                          metrics=["accuracy"])
            history = model.fit(data["x_train"], data["y_train"], epochs=4,
                                batch_size=batch, verbose=0,
                                validation_data=(data["x_test"],
                                                 data["y_test"]))
            scores.append(float(history.history["val_accuracy"][-1]))
        out[label] = scores
    return out


def bn_batch_size(fig, axes, p: Palette) -> None:
    runs = _batch_runs()
    ax = fig.subplots(1, 1)
    for label, color in (("no BN", p.red), ("with BN", p.green)):
        ax.plot(BATCHES, runs[label], "o-", ms=6, lw=2.0, color=color,
                label=label)
        for x, value in zip(BATCHES, runs[label]):
            ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=7.5, color=color)
    ax.set_xscale("log", base=2)
    ax.set_xticks(list(BATCHES))
    ax.set_xticklabels([str(b) for b in BATCHES])
    ax.set_xlabel("batch size")
    ax.set_ylabel("validation accuracy after 4 epochs")
    ax.set_title("BN estimates its statistics from the batch it is given",
                 fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("bn-depth", bn_depth, size=(9.2, 3.4), axes=False),
    figure("bn-learning-rate", bn_learning_rate, size=(7.8, 3.6), axes=False),
    figure("bn-batch-size", bn_batch_size, size=(7.4, 3.6), axes=False),
]


if __name__ == "__main__":
    print(f"=== {DEPTH} sigmoid layers, SGD 0.1, 20 epochs ===")
    for label, run in _depth_runs().items():
        print(f"{label:9s} final loss {run['loss'][-1]:.4f}  "
              f"final val acc {run['val_accuracy'][-1]:.4f}  "
              f"best {max(run['val_accuracy']):.4f}  "
              f"params {run['params']:,} (trainable {run['trainable']:,})")

    print("\n=== learning rate tolerance, 5 relu layers, 10 epochs ===")
    runs = _rate_runs()
    print(f"{'rate':>8} {'no BN':>10} {'with BN':>10}")
    for index, rate in enumerate(RATES):
        print(f"{rate:8g} {runs['no BN'][index]:10.4f} "
              f"{runs['with BN'][index]:10.4f}")

    print("\n=== batch size, 3 relu layers, 4 epochs, 4000 rows ===")
    runs = _batch_runs()
    print(f"{'batch':>8} {'no BN':>10} {'with BN':>10}")
    for index, batch in enumerate(BATCHES):
        print(f"{batch:8d} {runs['no BN'][index]:10.4f} "
              f"{runs['with BN'][index]:10.4f}")

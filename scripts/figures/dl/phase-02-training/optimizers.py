"""Figures for *Backpropagation and Optimizers (Adam, SGD)*.

``optimizer-comparison``
    Seven optimizers, one architecture, one seed, one dataset. Training loss and
    validation accuracy per epoch, so the "Adam always wins" claim can be
    checked rather than repeated.

``optimizer-paths``
    The same four update rules on a two-parameter anisotropic bowl, drawn as
    paths. This is where momentum's overshoot and Adam's per-axis scaling become
    visible instead of abstract.

``optimizer-memory``
    How much extra state each optimizer keeps per parameter, and what that costs
    for a model with 100 million of them.
"""

from __future__ import annotations

import functools
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, mlp, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPOCHS = 15
LIMIT = 8000


def _optimizers() -> dict:
    keras = tf().keras
    return {
        "SGD": lambda: keras.optimizers.SGD(0.1),
        "momentum 0.9": lambda: keras.optimizers.SGD(0.1, momentum=0.9),
        "Nesterov": lambda: keras.optimizers.SGD(0.1, momentum=0.9,
                                                 nesterov=True),
        "AdaGrad": lambda: keras.optimizers.Adagrad(0.01),
        "RMSprop": lambda: keras.optimizers.RMSprop(0.001),
        "Adam": lambda: keras.optimizers.Adam(0.001),
        "Nadam": lambda: keras.optimizers.Nadam(0.001),
    }


# Extra state each optimizer stores per parameter, counted from the Keras
# implementations: momentum keeps one velocity, Adam keeps m and v.
SLOTS = {"SGD": 0, "momentum 0.9": 1, "Nesterov": 1, "AdaGrad": 1,
         "RMSprop": 1, "Adam": 2, "Nadam": 2}


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=True)
    out = {}
    for name, factory in _optimizers().items():
        seed_everything(0)
        model = mlp([128], 784, 10, activation="relu", seed=0)
        model.compile(factory(), "sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        start = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[name] = {
            "loss": [float(v) for v in history.history["loss"]],
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "seconds": time.perf_counter() - start,
            "params": int(model.count_params()),
        }
    return out


def optimizer_comparison(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    # Colour by family (plain SGD, accumulating, Adam-style), dash by variant —
    # seven distinct colours would be unreadable and would hide the grouping.
    styles = {
        "SGD": (p.blue, "-"), "momentum 0.9": (p.blue, "--"),
        "Nesterov": (p.blue, ":"),
        "AdaGrad": (p.amber, "-"), "RMSprop": (p.amber, "--"),
        "Adam": (p.green, "-"), "Nadam": (p.green, "--"),
    }

    for name, run in runs.items():
        color, dash = styles[name]
        left.plot(epochs, run["loss"], lw=1.7, color=color, ls=dash, label=name)
        right.plot(epochs, run["val_accuracy"], lw=1.7, color=color, ls=dash,
                   label=f"{name} — {run['val_accuracy'][-1]:.4f}")

    left.set_yscale("log")
    left.set_xlabel("epoch")
    left.set_ylabel("training loss (log scale)")
    left.set_title("training loss", fontsize=10)
    left.legend(fontsize=7)

    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title("validation accuracy", fontsize=10)
    right.legend(fontsize=7, loc="lower right")


@functools.lru_cache(maxsize=1)
def _paths() -> dict:
    """Four update rules on L(a, b) = a^2 + 10 b^2, run through real Keras."""
    keras = tf().keras
    tensorflow = tf()
    recipes = {
        "SGD 0.05": lambda: keras.optimizers.SGD(0.05),
        "momentum 0.9": lambda: keras.optimizers.SGD(0.05, momentum=0.9),
        "RMSprop 0.05": lambda: keras.optimizers.RMSprop(0.05),
        "Adam 0.05": lambda: keras.optimizers.Adam(0.05),
    }
    out = {}
    for name, factory in recipes.items():
        point = tensorflow.Variable([2.6, 1.0])
        optimizer = factory()
        path = [point.numpy().copy()]
        for _ in range(60):
            with tensorflow.GradientTape() as tape:
                loss = point[0] ** 2 + 10 * point[1] ** 2
            optimizer.apply_gradients([(tape.gradient(loss, point), point)])
            path.append(point.numpy().copy())
        path = np.array(path)
        out[name] = {"path": path,
                     "final": float(path[-1][0] ** 2 + 10 * path[-1][1] ** 2)}
    return out


def optimizer_paths(fig, axes, p: Palette) -> None:
    paths = _paths()
    grid = fig.subplots(1, 4)
    a = np.linspace(-3.2, 3.2, 200)
    b = np.linspace(-1.6, 1.6, 200)
    A, B = np.meshgrid(a, b)
    Z = A ** 2 + 10 * B ** 2

    for ax, (name, info) in zip(grid, paths.items()):
        ax.contour(A, B, Z, levels=10, colors=p.grid, linewidths=0.6)
        path = info["path"]
        ax.plot(path[:, 0], path[:, 1], "o-", ms=2.2, lw=1.2, color=p.blue)
        ax.scatter([0], [0], marker="*", s=100, color=p.amber, zorder=5)
        ax.set_title(f"{name}\nfinal loss {info['final']:.2e}", fontsize=8.5)
        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-1.6, 1.6)
        ax.set_xlabel("a")
    grid[0].set_ylabel("b")


def optimizer_memory(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    names = list(SLOTS)
    # A 100M-parameter model in float32: weights plus optimizer slots.
    weights_gb = 100e6 * 4 / 1e9
    totals = [weights_gb * (1 + SLOTS[n]) for n in names]
    positions = np.arange(len(names))

    ax.bar(positions, [weights_gb] * len(names), 0.55, color=p.blue,
           label="weights")
    ax.bar(positions, [t - weights_gb for t in totals], 0.55,
           bottom=[weights_gb] * len(names), color=p.amber,
           label="optimizer state")
    for x, total, name in zip(positions, totals, names):
        ax.annotate(f"{total:.2f} GB\n{SLOTS[name]} slots", (x, total),
                    textcoords="offset points", xytext=(0, 4), ha="center",
                    fontsize=7.5, color=p.fg)

    ax.set_xticks(positions)
    ax.set_xticklabels(names, fontsize=8, rotation=20, ha="right")
    ax.set_ylabel("memory for a 100M-parameter model (GB, float32)")
    ax.set_ylim(0, max(totals) * 1.3)
    ax.set_title("What the optimizer costs before a single activation is stored",
                 fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("optimizer-comparison", optimizer_comparison, size=(9.4, 3.6),
           axes=False),
    figure("optimizer-paths", optimizer_paths, size=(9.6, 2.8), axes=False),
    figure("optimizer-memory", optimizer_memory, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    runs = _runs()
    print(f"Fashion-MNIST {LIMIT} rows, 1x128 relu, batch 128, {EPOCHS} epochs")
    print(f"{'optimizer':14s} {'final loss':>11} {'final val acc':>14} "
          f"{'best val acc':>13} {'epoch':>6} {'seconds':>8}")
    for name, run in runs.items():
        best = int(np.argmax(run["val_accuracy"])) + 1
        print(f"{name:14s} {run['loss'][-1]:11.6f} "
              f"{run['val_accuracy'][-1]:14.4f} "
              f"{max(run['val_accuracy']):13.4f} {best:6d} "
              f"{run['seconds']:8.2f}")
    print(f"\nparameters: {next(iter(runs.values()))['params']:,}")

    print("\nepochs to first reach 0.84 validation accuracy:")
    for name, run in runs.items():
        hit = next((i + 1 for i, v in enumerate(run["val_accuracy"])
                    if v >= 0.84), None)
        print(f"  {name:14s} {hit if hit else 'never'}")

    print("\n2-parameter bowl, 60 steps:")
    for name, info in _paths().items():
        print(f"  {name:14s} final loss {info['final']:.4e}")

    print("\noptimizer state for a 100M-parameter model:")
    for name, slots in SLOTS.items():
        print(f"  {name:14s} {slots} extra slot(s) -> "
              f"{100e6 * 4 * (1 + slots) / 1e9:.2f} GB")

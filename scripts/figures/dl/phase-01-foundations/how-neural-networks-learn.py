"""Figures for *How Neural Networks Learn (Gradient-Based Optimization)*.

``learning-rate-sweep``
    The same model and seed trained at five learning rates. One diverges, one
    crawls, and the useful range is narrower than most tutorials imply.

``batch-size-tradeoff``
    Accuracy and wall-clock time against batch size. Small batches take more
    steps but each step is cheaper; the total is not monotonic.

``loss-descent``
    Gradient descent on a two-parameter quadratic bowl at three step sizes,
    drawn as paths over the contours — the picture behind "too big a step
    oscillates".
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

from _dl import dataset, mlp, seed_everything, tf, train  # noqa: E402
from _style import Palette, figure  # noqa: E402

RATES = (0.0001, 0.001, 0.01, 0.1, 1.0)
# batch=8 is measured once in the page prose: 8,000 steps took 2,047.93s
# here, far too slow to re-run on every figure build.
BATCHES = (32, 128, 512, 2048)


@functools.lru_cache(maxsize=1)
def _rate_sweep() -> dict:
    data = dataset("mnist", limit=8000, flat=True)
    out = {}
    for rate in RATES:
        seed_everything(0)
        model = mlp([64], 784, 10, activation="relu", seed=0)
        model.compile(tf().keras.optimizers.SGD(learning_rate=rate),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        history = model.fit(data["x_train"], data["y_train"], epochs=15,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[rate] = {
            "loss": [float(v) for v in history.history["loss"]],
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
        }
    return out


def learning_rate_sweep(fig, axes, p: Palette) -> None:
    results = _rate_sweep()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(RATES, p.cycle))

    for rate in RATES:
        losses = results[rate]["loss"]
        finite = [v if np.isfinite(v) and v < 1e4 else np.nan for v in losses]
        left.plot(range(1, len(finite) + 1), finite, "o-", ms=3, lw=1.8,
                  color=colors[rate], label=f"lr={rate:g}")
        right.plot(range(1, len(losses) + 1), results[rate]["val_accuracy"],
                   "o-", ms=3, lw=1.8, color=colors[rate], label=f"lr={rate:g}")

    left.set_yscale("log")
    left.set_xlabel("epoch")
    left.set_ylabel("training loss (log scale)")
    left.set_title("loss", fontsize=10.5)
    left.legend(fontsize=7.5)

    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_ylim(0, 1.0)
    right.set_title("validation accuracy", fontsize=10.5)
    right.legend(fontsize=7.5, loc="lower right")


@functools.lru_cache(maxsize=1)
def _batch_sweep() -> dict:
    data = dataset("mnist", limit=8000, flat=True)
    out = {}
    for batch in BATCHES:
        seed_everything(0)
        model = mlp([64], 784, 10, activation="relu", seed=0)
        model.compile(tf().keras.optimizers.SGD(learning_rate=0.1),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        start = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=8,
                            batch_size=batch, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        seconds = time.perf_counter() - start
        steps = int(np.ceil(len(data["x_train"]) / batch)) * 8
        out[batch] = {"seconds": seconds, "steps": steps,
                      "val_accuracy": float(history.history["val_accuracy"][-1])}
    return out


def batch_size_tradeoff(fig, axes, p: Palette) -> None:
    results = _batch_sweep()
    ax = fig.subplots(1, 1)
    twin = ax.twinx()
    positions = np.arange(len(BATCHES))

    accuracies = [results[b]["val_accuracy"] for b in BATCHES]
    ax.bar(positions, accuracies, 0.5, color=p.blue, label="validation accuracy")
    for x, value in zip(positions, accuracies):
        ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=7.5, color=p.fg)

    seconds = [results[b]["seconds"] for b in BATCHES]
    twin.plot(positions, seconds, "o-", color=p.amber, lw=2.0, label="seconds")
    for x, value, batch in zip(positions, seconds, BATCHES):
        twin.annotate(f"{value:.1f}s\n{results[batch]['steps']} steps",
                      (x, value), textcoords="offset points", xytext=(8, -2),
                      fontsize=7, color=p.amber)

    ax.set_xticks(positions)
    ax.set_xticklabels([str(b) for b in BATCHES])
    ax.set_xlabel("batch size")
    ax.set_ylabel("validation accuracy after 8 epochs")
    ax.set_ylim(0, 1.05)
    twin.set_ylabel("wall clock seconds", color=p.amber)
    twin.tick_params(axis="y", colors=p.amber)
    twin.grid(False)
    ax.set_title("Same data, same epochs, same learning rate — only the batch size",
                 fontsize=10.5)


def loss_descent(fig, axes, p: Palette) -> None:
    # A simple anisotropic bowl: L(a, b) = a^2 + 10 b^2. The condition number is
    # 10, which is all it takes to make one learning rate wrong for both axes.
    grid = fig.subplots(1, 3)
    a = np.linspace(-3, 3, 200)
    b = np.linspace(-2.8, 2.8, 200)
    A, B = np.meshgrid(a, b)
    Z = A ** 2 + 10 * B ** 2

    for ax, rate in zip(grid, (0.02, 0.09, 0.101)):
        ax.contour(A, B, Z, levels=12, colors=p.grid, linewidths=0.7)
        point = np.array([2.6, 1.0])
        path = [point.copy()]
        for _ in range(40):
            gradient = np.array([2 * point[0], 20 * point[1]])
            point = point - rate * gradient
            if not np.all(np.isfinite(point)) or np.abs(point).max() > 1e3:
                break
            path.append(point.copy())
        path = np.array(path)
        start_loss = 2.6 ** 2 + 10 * 1.0 ** 2
        final = float(path[-1][0] ** 2 + 10 * path[-1][1] ** 2)
        # Diverging means the loss ended above where it started — the only test
        # that does not depend on the plotting window.
        diverged = final > start_loss
        ax.plot(path[:, 0], path[:, 1], "o-", ms=3, lw=1.4,
                color=p.red if diverged else p.green)
        ax.scatter([0], [0], marker="*", s=110, color=p.amber, zorder=5)
        ax.set_title(f"lr={rate:g} — {'DIVERGING' if diverged else 'converging'}\n"
                     f"loss {start_loss:.1f} -> {final:.3g} in {len(path) - 1} steps",
                     fontsize=9)
        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-2.8, 2.8)
        ax.set_xlabel("a")
    grid[0].set_ylabel("b")


FIGURES = [
    figure("learning-rate-sweep", learning_rate_sweep, size=(9.2, 3.4), axes=False),
    figure("batch-size-tradeoff", batch_size_tradeoff, size=(7.6, 3.6), axes=False),
    figure("loss-descent", loss_descent, size=(9.4, 3.0), axes=False),
]


if __name__ == "__main__":
    print("== learning rate sweep (MNIST 8k, 1x64 relu, SGD, 15 epochs) ==")
    for rate, info in _rate_sweep().items():
        losses = info["loss"]
        final = losses[-1]
        print(f"lr={rate:<8g} final loss {final:14.6f}  "
              f"final val acc {info['val_accuracy'][-1]:.4f}  "
              f"{'DIVERGED' if not np.isfinite(final) or final > 1e3 else ''}")
    print("\n== batch size (SGD lr=0.1, 8 epochs) ==")
    for batch, info in _batch_sweep().items():
        print(f"batch {batch:5d}  steps {info['steps']:5d}  "
              f"{info['seconds']:6.2f}s  val acc {info['val_accuracy']:.4f}")

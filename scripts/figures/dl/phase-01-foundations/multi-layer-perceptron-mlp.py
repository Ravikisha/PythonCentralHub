"""Figures for *Multi-Layer Perceptron (MLP)*.

``width-vs-depth``
    MNIST accuracy for networks with roughly the same parameter budget spent
    three ways: wide and shallow, balanced, narrow and deep. Three seeds each.

``universal-approximation``
    One hidden layer fitting a sine wave at four widths. The theorem says any
    continuous function is reachable with enough units; the panels show what
    "enough" looks like and where the fit is still wrong.

``dead-units``
    How many hidden units never fire on any test input, measured at four
    depths. A dead ReLU unit is a parameter you are paying for and a gradient
    path that is switched off, and the count grows with depth -- which is part
    of why "just add layers" stops working before the theory says it should.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, mlp, seed_everything, tf, train  # noqa: E402
from _style import Palette, figure  # noqa: E402

# (label, hidden layer widths) — chosen so the parameter counts are comparable.
SHAPES = [
    ("1 x 128", [128]),
    ("2 x 90", [90, 90]),
    ("4 x 60", [60, 60, 60, 60]),
    ("8 x 40", [40] * 8),
]
SEEDS = (0, 1, 2)
WIDTHS = (1, 3, 8, 40)


@functools.lru_cache(maxsize=1)
def _width_vs_depth() -> dict:
    data = dataset("mnist", limit=8000, flat=True)
    out = {}
    for label, widths in SHAPES:
        scores, params = [], 0
        for seed in SEEDS:
            seed_everything(seed)
            model = mlp(widths, 784, 10, activation="relu", seed=seed)
            history = train(model, data, epochs=6, batch_size=128)
            scores.append(history["val_accuracy"][-1])
            params = history["params"]
        out[label] = {"scores": scores, "params": params}
    return out


def width_vs_depth(fig, axes, p: Palette) -> None:
    results = _width_vs_depth()
    ax = fig.subplots(1, 1)
    labels = [label for label, _ in SHAPES]
    positions = np.arange(len(labels))
    means = [float(np.mean(results[l]["scores"])) for l in labels]
    lows = [float(np.mean(results[l]["scores"]) - np.min(results[l]["scores"])) for l in labels]
    highs = [float(np.max(results[l]["scores"]) - np.mean(results[l]["scores"])) for l in labels]

    ax.bar(positions, means, 0.55, color=p.blue, yerr=[lows, highs], capsize=4,
           ecolor=p.muted)
    for x, label, mean in zip(positions, labels, means):
        ax.annotate(f"{mean:.4f}", (x, mean), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=8, color=p.fg)
        ax.annotate(f"{results[label]['params']:,} params", (x, 0.04),
                    ha="center", fontsize=7.5, color=p.muted)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel("MNIST validation accuracy")
    ax.set_ylim(0, 1.02)
    ax.set_title("Similar parameter budgets, spent on width or on depth (3 seeds)",
                 fontsize=10.5)


@functools.lru_cache(maxsize=1)
def _approximation() -> dict:
    keras = tf().keras
    rng = np.random.default_rng(0)
    x = np.linspace(-3, 3, 400).astype("float32")
    y = np.sin(2.0 * x) + 0.3 * np.sin(6.0 * x)
    out = {"x": x, "y": y, "fits": {}}
    for width in WIDTHS:
        seed_everything(0)
        model = keras.Sequential([
            keras.layers.Input((1,)),
            keras.layers.Dense(width, activation="tanh"),
            keras.layers.Dense(1),
        ])
        model.compile(keras.optimizers.Adam(0.01), "mse")
        model.fit(x, y, epochs=600, batch_size=64, verbose=0)
        prediction = model.predict(x, verbose=0).ravel()
        out["fits"][width] = {
            "prediction": prediction,
            "mse": float(np.mean((prediction - y) ** 2)),
            "params": int(model.count_params()),
        }
    return out


def universal_approximation(fig, axes, p: Palette) -> None:
    data = _approximation()
    grid = fig.subplots(1, len(WIDTHS))
    for ax, width in zip(grid, WIDTHS):
        fit = data["fits"][width]
        ax.plot(data["x"], data["y"], color=p.muted, lw=1.6, label="target")
        ax.plot(data["x"], fit["prediction"], color=p.amber, lw=2.0, label="fit")
        ax.set_title(f"{width} hidden unit{'s' if width > 1 else ''}\n"
                     f"MSE {fit['mse']:.4f} · {fit['params']} params", fontsize=9)
        ax.set_ylim(-1.8, 1.8)
        ax.set_xticks([-3, 0, 3])
        if width != WIDTHS[0]:
            ax.set_yticks([])
    grid[0].set_ylabel("y")
    grid[0].legend(fontsize=7.5, loc="lower right")


DEPTHS = (1, 2, 4, 8)
UNITS = 64


@functools.lru_cache(maxsize=1)
def _dead_units() -> dict:
    """Fraction of hidden units that output zero for every test input."""
    keras = tf().keras
    data = dataset("mnist", limit=8000, flat=True)
    rows = []
    for depth in DEPTHS:
        shares, accuracies = [], []
        for seed in SEEDS:
            seed_everything(seed)
            inputs = keras.layers.Input((784,))
            hidden = inputs
            taps = []
            for _ in range(depth):
                hidden = keras.layers.Dense(UNITS, activation="relu")(hidden)
                taps.append(hidden)
            outputs = keras.layers.Dense(10, activation="softmax")(hidden)
            model = keras.Model(inputs, outputs)
            model.compile("adam", "sparse_categorical_crossentropy",
                          metrics=["accuracy"])
            model.fit(data["x_train"], data["y_train"], epochs=8,
                      batch_size=128, verbose=0)
            accuracies.append(model.evaluate(data["x_test"], data["y_test"],
                                             verbose=0)[1])
            probe = keras.Model(inputs, taps)
            activations = probe.predict(data["x_test"][:2000], verbose=0)
            if depth == 1:
                activations = [activations]
            dead = sum(int((layer.max(axis=0) == 0).sum())
                       for layer in activations)
            shares.append(dead / (depth * UNITS))
        rows.append({"depth": depth,
                     "share": float(np.mean(shares)),
                     "worst": float(np.max(shares)),
                     "accuracy": float(np.mean(accuracies)),
                     "units": depth * UNITS})
    return {"rows": rows}


def dead_units(fig, axes, p: Palette) -> None:
    rows = _dead_units()["rows"]
    left, right = fig.subplots(1, 2)
    depths = [row["depth"] for row in rows]
    shares = [row["share"] for row in rows]
    left.bar(np.arange(len(rows)), shares, color=p.red, width=0.6)
    for index, row in enumerate(rows):
        left.annotate(f"{row['share']:.1%}\nof {row['units']}",
                      (index, row["share"]), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=8,
                      color=p.fg)
    left.set_xticks(np.arange(len(rows)))
    left.set_xticklabels([f"{depth} x {UNITS}" for depth in depths])
    left.set_xlabel("hidden layers")
    left.set_ylabel("share of units that never fire")
    left.set_title(f"measured over 2,000 test images, {len(SEEDS)} seeds",
                   fontsize=10)

    accuracies = [row["accuracy"] for row in rows]
    right.plot(depths, accuracies, "o-", color=p.blue, lw=1.8, ms=6)
    for depth, value in zip(depths, accuracies):
        right.annotate(f"{value:.4f}", (depth, value), xytext=(0, 7),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(depths)
    right.set_xlabel("hidden layers")
    right.set_ylabel("test accuracy")
    right.set_title("what the extra depth bought", fontsize=10)


FIGURES = [
    figure("width-vs-depth", width_vs_depth, size=(7.4, 3.6), axes=False),
    figure("dead-units", dead_units, size=(8.6, 3.8), axes=False),
    figure("universal-approximation", universal_approximation, size=(9.6, 2.9), axes=False),
]


if __name__ == "__main__":
    print("=== dead ReLU units by depth ===")
    print(f"{'layers':>7} {'units':>7} {'dead share':>12} {'worst seed':>12} "
          f"{'accuracy':>10}")
    for row in _dead_units()["rows"]:
        print(f"{row['depth']:7d} {row['units']:7d} {row['share']:12.4f} "
              f"{row['worst']:12.4f} {row['accuracy']:10.4f}")
    print()

    print("== width vs depth (MNIST, 8k rows, 6 epochs, 3 seeds) ==")
    for label, info in _width_vs_depth().items():
        scores = info["scores"]
        print(f"{label:8s} params {info['params']:7,d}  mean {np.mean(scores):.4f}  "
              f"min {np.min(scores):.4f}  max {np.max(scores):.4f}")
    print("\n== universal approximation (sin(2x) + 0.3 sin(6x), 600 epochs) ==")
    for width, fit in _approximation()["fits"].items():
        print(f"width {width:3d}  params {fit['params']:5d}  MSE {fit['mse']:.6f}")

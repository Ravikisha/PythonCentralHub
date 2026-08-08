"""Figures for *Activation Functions*: the curves, their derivatives, and what
each one costs once the network gets deep.

Two figures:

``activation-curves``
    The four activations and their exact derivatives. Nothing is fitted here —
    the point is the y-axis of the right panel: the sigmoid derivative peaks at
    0.25, so eight stacked sigmoid layers can multiply a gradient by at most
    0.25 ** 8, which is where "vanishing gradient" comes from arithmetically.

``activation-depth``
    The same MLP trained on MNIST at depth 2 and depth 8 with each activation,
    three seeds each, reported as mean and range. Shallow networks barely care
    which activation they use; deep ones care enormously.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# `..` holds _dl.py, `../..` holds _style.py — both needed when this module is
# run directly (`python scripts/figures/dl/<phase>/<page>.py`) to print numbers.
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, mlp, seed_everything, tf, train  # noqa: E402
from _style import Palette, figure  # noqa: E402

ACTIVATIONS = ("sigmoid", "tanh", "relu")
DEPTHS = (2, 8)
SEEDS = (0, 1, 2)


def _curves():
    z = np.linspace(-6, 6, 601)
    sigmoid = 1 / (1 + np.exp(-z))
    tanh = np.tanh(z)
    relu = np.maximum(z, 0.0)
    leaky = np.where(z > 0, z, 0.01 * z)
    values = {"sigmoid": sigmoid, "tanh": tanh, "ReLU": relu, "leaky ReLU": leaky}
    derivatives = {
        "sigmoid": sigmoid * (1 - sigmoid),
        "tanh": 1 - tanh ** 2,
        "ReLU": (z > 0).astype(float),
        "leaky ReLU": np.where(z > 0, 1.0, 0.01),
    }
    return z, values, derivatives


def activation_curves(fig, axes, p: Palette) -> None:
    z, values, derivatives = _curves()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(values, p.cycle))

    # ReLU and leaky ReLU differ only by 0.01z on the negative side, so drawing
    # both solid hides one completely. Leaky goes on top, dashed.
    styles = {"sigmoid": dict(lw=2.0), "tanh": dict(lw=2.0),
              "ReLU": dict(lw=3.2), "leaky ReLU": dict(lw=1.6, ls="--")}

    for name, curve in values.items():
        left.plot(z, curve, color=colors[name], label=name, **styles[name])
    left.axhline(0, color=p.grid, lw=0.8)
    left.axvline(0, color=p.grid, lw=0.8)
    left.set_title("activation", fontsize=10.5)
    left.set_xlabel("z")
    left.set_ylim(-1.5, 3.0)
    left.legend(fontsize=8, loc="upper left")

    for name, curve in derivatives.items():
        right.plot(z, curve, color=colors[name], label=name, **styles[name])
    right.axhline(0.25, color=p.red, lw=1.2, ls="--")
    right.annotate("sigmoid derivative peaks at 0.25", xy=(-5.8, 0.34),
                   color=p.red, fontsize=8, ha="left")
    right.set_title("derivative — the factor each layer multiplies by", fontsize=10.5)
    right.set_xlabel("z")
    right.set_ylim(-0.05, 1.25)
    right.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.0, 0.88))


@functools.lru_cache(maxsize=1)
def _depth_study() -> dict:
    """Train every (activation, depth, seed) combination and keep val accuracy."""
    data = dataset("mnist", limit=8000, flat=True)
    results: dict[tuple[str, int], list[float]] = {}
    for activation in ACTIVATIONS:
        for depth in DEPTHS:
            scores = []
            for seed in SEEDS:
                seed_everything(seed)
                model = mlp([32] * depth, 784, 10, activation=activation, seed=seed)
                history = train(model, data, epochs=4, batch_size=128)
                scores.append(history["val_accuracy"][-1])
            results[(activation, depth)] = scores
    return results


def activation_depth(fig, axes, p: Palette) -> None:
    results = _depth_study()
    ax = fig.subplots(1, 1)
    width = 0.35
    positions = np.arange(len(ACTIVATIONS))
    colors = {2: p.blue, 8: p.amber}

    for offset, depth in zip((-width / 2, width / 2), DEPTHS):
        means = [float(np.mean(results[(a, depth)])) for a in ACTIVATIONS]
        spread = [
            [float(np.mean(results[(a, depth)]) - np.min(results[(a, depth)])) for a in ACTIVATIONS],
            [float(np.max(results[(a, depth)]) - np.mean(results[(a, depth)])) for a in ACTIVATIONS],
        ]
        ax.bar(positions + offset, means, width, color=colors[depth],
               label=f"{depth} hidden layers", yerr=spread, capsize=3,
               ecolor=p.muted)
        for x, mean in zip(positions + offset, means):
            ax.annotate(f"{mean:.4f}", (x, mean), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=7.5, color=p.fg)

    ax.set_xticks(positions)
    ax.set_xticklabels(ACTIVATIONS)
    ax.set_ylabel("MNIST validation accuracy")
    ax.set_ylim(0, 1.02)
    ax.set_title("Same width, same data, same epochs — only the activation and depth change",
                 fontsize=10)
    # Lower-right sits on top of an amber bar and becomes unreadable; the space
    # above the sigmoid pair is free.
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9)


@functools.lru_cache(maxsize=1)
def _gradient_by_layer() -> dict:
    """Mean |dL/dW| for every layer of an 8-hidden-layer net, at initialisation.

    One batch, no training: this is the gradient the *first* update would use, so
    it isolates the activation's effect from anything the optimiser does later.
    """
    keras = tf().keras
    data = dataset("mnist", limit=8000, flat=True)
    xb = data["x_train"][:256]
    yb = data["y_train"][:256]
    loss_fn = keras.losses.SparseCategoricalCrossentropy()
    out = {}
    for activation in ACTIVATIONS:
        seed_everything(0)
        layers = [keras.layers.Input((784,))]
        for _ in range(8):
            layers.append(keras.layers.Dense(32, activation=activation))
        layers.append(keras.layers.Dense(10, activation="softmax"))
        model = keras.Sequential(layers)
        with tf().GradientTape() as tape:
            loss = loss_fn(yb, model(xb, training=True))
        grads = tape.gradient(loss, model.trainable_variables)
        out[activation] = [
            float(tf().reduce_mean(tf().abs(g)))
            for g, v in zip(grads, model.trainable_variables) if "kernel" in v.name
        ]
    return out


def gradient_by_layer(fig, axes, p: Palette) -> None:
    results = _gradient_by_layer()
    ax = fig.subplots(1, 1)
    colors = {"sigmoid": p.blue, "tanh": p.green, "relu": p.amber}
    layers = np.arange(1, 10)

    for activation, values in results.items():
        ax.semilogy(layers, values, "o-", color=colors[activation], lw=2.0,
                    label=activation, markersize=5)
    ax.set_xlabel("layer (1 = closest to the input, 9 = output)")
    ax.set_ylabel("mean |dL/dW|  (log scale)")
    ax.set_title("The gradient that reaches layer 1, before any training",
                 fontsize=10.5)
    ax.legend(fontsize=8)
    ratio = results["sigmoid"][0] / results["sigmoid"][7]
    ax.annotate(f"sigmoid: layer 1 gets {1 / ratio:,.0f}x less\nthan layer 8",
                xy=(1, results["sigmoid"][0]), xytext=(2.4, results["sigmoid"][0] * 6),
                color=p.red, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=p.red, lw=1.0))


# Every draw function here builds its own axes with fig.subplots, so pass
# axes=False and let _style skip the automatic add_subplot — otherwise an empty
# set of axes is rendered underneath the real one.
FIGURES = [
    figure("activation-curves", activation_curves, size=(9.0, 3.4), axes=False),
    figure("activation-depth", activation_depth, size=(7.2, 3.6), axes=False),
    figure("gradient-by-layer", gradient_by_layer, size=(7.2, 3.6), axes=False),
]


if __name__ == "__main__":                      # quick numbers for the page prose
    results = _depth_study()
    for key in sorted(results):
        scores = results[key]
        print(f"{key[0]:>8} depth {key[1]}: mean {np.mean(scores):.4f} "
              f"min {np.min(scores):.4f} max {np.max(scores):.4f}")

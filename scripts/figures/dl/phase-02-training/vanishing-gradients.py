"""Figures for *Vanishing & Exploding Gradients*.

``gradient-norms``
    The gradient norm reaching each layer of a 20-layer network, for three
    activation-and-initialisation pairings. On a log axis, because the range is
    several orders of magnitude.

``activation-variance``
    Forward activation standard deviation by depth for four initialisation
    scales. Shows the signal dying or blowing up before any gradient is
    involved.

``clipping``
    A run that explodes, and the same run with ``clipnorm=1.0``.
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

DEPTH = 20
WIDTH = 60
LIMIT = 8000

RECIPES = {
    "sigmoid + Glorot": ("sigmoid", "glorot_uniform"),
    "tanh + Glorot": ("tanh", "glorot_uniform"),
    "relu + He": ("relu", "he_normal"),
}


def _deep_model(activation: str, initializer: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((784,))]
    for index in range(DEPTH):
        layers.append(keras.layers.Dense(WIDTH, activation=activation,
                                         kernel_initializer=initializer,
                                         name=f"h{index:02d}"))
    layers.append(keras.layers.Dense(10, activation="softmax", name="out"))
    return keras.Sequential(layers)


@functools.lru_cache(maxsize=1)
def _gradient_norms() -> dict:
    """One backward pass per recipe; report the norm per hidden layer kernel."""
    tensorflow = tf()
    data = dataset("mnist", limit=LIMIT, flat=True)
    x = data["x_train"][:128]
    y = data["y_train"][:128]
    out = {}
    for label, (activation, initializer) in RECIPES.items():
        model = _deep_model(activation, initializer)
        with tensorflow.GradientTape() as tape:
            predictions = model(x, training=True)
            loss = tensorflow.reduce_mean(
                tf().keras.losses.sparse_categorical_crossentropy(
                    y, predictions))
        gradients = tape.gradient(loss, model.trainable_variables)
        norms = []
        for variable, gradient in zip(model.trainable_variables, gradients):
            if "kernel" in variable.name and variable.shape[-1] == WIDTH:
                norms.append(float(tensorflow.norm(gradient).numpy()))
        out[label] = {"norms": norms, "loss": float(loss.numpy())}
    return out


def gradient_norms(fig, axes, p: Palette) -> None:
    results = _gradient_norms()
    ax = fig.subplots(1, 1)
    colors = dict(zip(results, p.cycle))

    for label, info in results.items():
        norms = info["norms"]
        ax.plot(range(1, len(norms) + 1), norms, "o-", ms=3.5, lw=1.8,
                color=colors[label],
                label=f"{label} — layer 1 / layer {len(norms)} = "
                      f"{norms[0] / norms[-1]:.1e}")
    ax.set_yscale("log")
    ax.set_xlabel("hidden layer (1 = nearest the input)")
    ax.set_ylabel("gradient norm of the layer's kernel (log scale)")
    ax.set_xticks(range(1, DEPTH + 1, 2))
    ax.set_title(f"One backward pass through {DEPTH} hidden layers",
                 fontsize=10.5)
    ax.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _forward_variance() -> dict:
    """Activation spread by depth for four initialisation scales."""
    rng = np.random.default_rng(0)
    x = rng.standard_normal((512, WIDTH)).astype("float32")
    out = {}
    for label, scale in (("0.5 / sqrt(n)", 0.5), ("1.0 / sqrt(n)", 1.0),
                         ("sqrt(2/n) — He", np.sqrt(2.0)),
                         ("2.0 / sqrt(n)", 2.0)):
        signal = x.copy()
        spreads = [float(signal.std())]
        for _ in range(DEPTH):
            weights = rng.standard_normal((WIDTH, WIDTH)) * scale / np.sqrt(WIDTH)
            signal = np.maximum(signal @ weights, 0.0)      # relu
            spreads.append(float(signal.std()))
        out[label] = spreads
    return out


def activation_variance(fig, axes, p: Palette) -> None:
    results = _forward_variance()
    ax = fig.subplots(1, 1)
    colors = dict(zip(results, p.cycle))
    for label, spreads in results.items():
        finite = [v if v > 1e-30 else np.nan for v in spreads]
        ax.plot(range(len(finite)), finite, "o-", ms=3, lw=1.8,
                color=colors[label],
                label=f"{label} — layer {DEPTH}: {spreads[-1]:.2e}")
    ax.set_yscale("log")
    ax.axhline(1.0, color=p.grid, lw=1.0, ls="--")
    ax.set_xlabel("layer")
    ax.set_ylabel("activation standard deviation (log scale)")
    ax.set_title("ReLU layers, random weights, no training at all",
                 fontsize=10.5)
    ax.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _clipping() -> dict:
    keras = tf().keras
    data = dataset("mnist", limit=LIMIT, flat=True)
    out = {}
    for label, clip in (("no clipping", None), ("clipnorm = 1.0", 1.0)):
        seed_everything(0)
        model = keras.Sequential([
            keras.layers.Input((784,)),
            keras.layers.Dense(128, activation="relu",
                               kernel_initializer=keras.initializers.RandomNormal(
                                   stddev=1.0, seed=0)),
            keras.layers.Dense(128, activation="relu",
                               kernel_initializer=keras.initializers.RandomNormal(
                                   stddev=1.0, seed=1)),
            keras.layers.Dense(10, activation="softmax"),
        ])
        optimizer = (keras.optimizers.SGD(0.5, clipnorm=clip) if clip
                     else keras.optimizers.SGD(0.5))
        model.compile(optimizer, "sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        history = model.fit(data["x_train"], data["y_train"], epochs=12,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[label] = {
            "loss": [float(v) for v in history.history["loss"]],
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
        }
    return out


def clipping(fig, axes, p: Palette) -> None:
    results = _clipping()
    left, right = fig.subplots(1, 2)
    colors = {"no clipping": p.red, "clipnorm = 1.0": p.green}
    for label, info in results.items():
        epochs = range(1, len(info["loss"]) + 1)
        losses = [v if np.isfinite(v) else np.nan for v in info["loss"]]
        left.plot(epochs, losses, "o-", ms=3, lw=1.8, color=colors[label],
                  label=label)
        right.plot(epochs, info["val_accuracy"], "o-", ms=3, lw=1.8,
                   color=colors[label],
                   label=f"{label} — {info['val_accuracy'][-1]:.4f}")
    left.set_yscale("log")
    left.set_xlabel("epoch")
    left.set_ylabel("training loss (log scale)")
    left.set_title("loss: stddev-1.0 init, SGD at 0.5", fontsize=10)
    left.legend(fontsize=8)
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_ylim(0, 1.0)
    right.set_title("validation accuracy", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("gradient-norms", gradient_norms, size=(8.2, 3.8), axes=False),
    figure("activation-variance", activation_variance, size=(8.0, 3.8),
           axes=False),
    figure("clipping", clipping, size=(9.2, 3.4), axes=False),
]


if __name__ == "__main__":
    print(f"=== gradient norms, {DEPTH} hidden layers of {WIDTH} units ===")
    for label, info in _gradient_norms().items():
        norms = info["norms"]
        print(f"{label:18s} loss {info['loss']:.4f}")
        print(f"  layer  1: {norms[0]:.4e}   layer {len(norms)}: {norms[-1]:.4e}"
              f"   ratio {norms[0] / norms[-1]:.4e}")
        print(f"  min {min(norms):.4e}  max {max(norms):.4e}")

    print("\n=== forward activation spread by depth (relu) ===")
    for label, spreads in _forward_variance().items():
        print(f"{label:18s} layer 0 {spreads[0]:.4f}  layer 5 {spreads[5]:.4e}  "
              f"layer {DEPTH} {spreads[-1]:.4e}")

    print("\n=== gradient clipping ===")
    for label, info in _clipping().items():
        print(f"{label:16s} epoch 1 loss {info['loss'][0]:.4f}  "
              f"final loss {info['loss'][-1]:.4f}  "
              f"final val acc {info['val_accuracy'][-1]:.4f}")

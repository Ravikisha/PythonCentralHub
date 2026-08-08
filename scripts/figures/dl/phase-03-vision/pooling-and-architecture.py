"""Figures for *Pooling & CNN Architecture*.

``pooling-on-an-image``
    Max and average pooling applied to a real image at two window sizes, so the
    difference between "keep the strongest response" and "keep the mean" is
    visible rather than described.

``downsampling-options``
    Four ways to halve the resolution — max pool, average pool, strided
    convolution, and no downsampling at all — trained identically.

``memory-profile``
    Activation memory per layer for a small convnet, which is what actually
    limits the batch size you can fit.
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

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 8000
EPOCHS = 12
BATCH = 128


def _pool(image: np.ndarray, size: int, how: str) -> np.ndarray:
    height = image.shape[0] // size * size
    width = image.shape[1] // size * size
    blocks = image[:height, :width].reshape(height // size, size,
                                            width // size, size)
    return blocks.max(axis=(1, 3)) if how == "max" else blocks.mean(axis=(1, 3))


@functools.lru_cache(maxsize=1)
def _sample() -> dict:
    data = dataset("fashion", limit=200, flat=False)
    grey = data["x_train"][7][..., 0]
    return {"grey": grey,
            "pools": {(size, how): _pool(grey, size, how)
                      for size in (2, 4) for how in ("max", "mean")}}


def pooling_on_an_image(fig, axes, p: Palette) -> None:
    info = _sample()
    grid = fig.subplots(1, 5)
    grid[0].imshow(info["grey"], cmap="gray")
    grid[0].set_title(f"input {info['grey'].shape[0]}x{info['grey'].shape[1]}",
                      fontsize=9)
    order = [(2, "max"), (2, "mean"), (4, "max"), (4, "mean")]
    for ax, key in zip(grid[1:], order):
        pooled = info["pools"][key]
        ax.imshow(pooled, cmap="gray")
        ax.set_title(f"{key[1]} pool {key[0]}x{key[0]}\n"
                     f"{pooled.shape[0]}x{pooled.shape[1]}, mean "
                     f"{pooled.mean():.3f}", fontsize=8.5)
    for ax in grid:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def _model(kind: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((28, 28, 1))]
    for filters in (32, 64):
        layers.append(keras.layers.Conv2D(filters, 3, padding="same",
                                          activation="relu"))
        if kind == "max pool":
            layers.append(keras.layers.MaxPooling2D(2))
        elif kind == "average pool":
            layers.append(keras.layers.AveragePooling2D(2))
        elif kind == "strided conv":
            layers.append(keras.layers.Conv2D(filters, 3, strides=2,
                                              padding="same",
                                              activation="relu"))
        # "no downsampling" adds nothing
    layers.append(keras.layers.Flatten())
    layers.append(keras.layers.Dense(64, activation="relu"))
    layers.append(keras.layers.Dense(10, activation="softmax"))
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


KINDS = ("max pool", "average pool", "strided conv", "no downsampling")


@functools.lru_cache(maxsize=1)
def _downsampling_runs() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=False)
    out = {}
    for kind in KINDS:
        model = _model(kind)
        started = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=BATCH, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[kind] = {
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
        }
    return out


def downsampling_options(fig, axes, p: Palette) -> None:
    runs = _downsampling_runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for (kind, run), color in zip(runs.items(), p.cycle):
        left.plot(epochs, run["val_accuracy"], lw=1.8, color=color,
                  label=f"{kind} — {run['val_accuracy'][-1]:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_title("Fashion-MNIST, 8,000 rows, 12 epochs", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    names = list(runs)
    params = [runs[k]["params"] for k in names]
    accuracies = [runs[k]["val_accuracy"][-1] for k in names]
    for name, param, accuracy, color in zip(names, params, accuracies, p.cycle):
        right.scatter([param], [accuracy], s=110, color=color, label=name)
        right.annotate(f"{runs[name]['seconds']:.0f}s", (param, accuracy),
                       textcoords="offset points", xytext=(8, -3), fontsize=8,
                       color=color)
    right.set_xscale("log")
    right.set_xlabel("parameters (log scale)")
    right.set_ylabel("final validation accuracy")
    right.set_title("accuracy against size and time", fontsize=10)
    right.legend(fontsize=7.5, loc="lower left")


def memory_profile(fig, axes, p: Palette) -> None:
    keras = tf().keras
    model = _model("max pool")
    ax = fig.subplots(1, 1)
    names, activations, weights = [], [], []
    for layer in model.layers:
        shape = layer.output.shape[1:]
        if None in shape:
            continue
        names.append(f"{type(layer).__name__}\n{tuple(int(s) for s in shape)}")
        activations.append(int(np.prod([int(s) for s in shape])) * 4)
        weights.append(int(sum(np.prod(w.shape) for w in layer.weights)) * 4)

    positions = np.arange(len(names))
    ax.bar(positions - 0.2, activations, 0.38, color=p.blue,
           label="activations per image (bytes)")
    ax.bar(positions + 0.2, [max(w, 1) for w in weights], 0.38, color=p.amber,
           label="weights (bytes)")
    for x, value in zip(positions - 0.2, activations):
        ax.annotate(f"{value:,}", (x, value), textcoords="offset points",
                    xytext=(0, 3), ha="center", fontsize=7, color=p.fg)
    ax.set_yscale("log")
    ax.set_xticks(positions)
    ax.set_xticklabels(names, fontsize=7)
    ax.set_ylabel("bytes, float32 (log scale)")
    ax.set_title(f"Per-image activation memory: "
                 f"{sum(activations):,} bytes total, weights "
                 f"{sum(weights):,}", fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("pooling-on-an-image", pooling_on_an_image, size=(9.6, 2.4),
           axes=False),
    figure("downsampling-options", downsampling_options, size=(9.4, 3.6),
           axes=False),
    figure("memory-profile", memory_profile, size=(9.0, 3.8), axes=False),
]


if __name__ == "__main__":
    info = _sample()
    print("=== pooling one image ===")
    print(f"input {info['grey'].shape}  mean {info['grey'].mean():.4f}  "
          f"max {info['grey'].max():.4f}")
    for (size, how), pooled in info["pools"].items():
        print(f"{how:5s} pool {size}x{size} -> {pooled.shape}  "
              f"mean {pooled.mean():.4f}  max {pooled.max():.4f}")
    print("max pooling raises the mean because it keeps the largest value in")
    print("every window; average pooling preserves it")

    print("\n=== downsampling options ===")
    print(f"{'kind':18s} {'params':>10} {'final val acc':>14} {'best':>8} "
          f"{'seconds':>9}")
    for kind, run in _downsampling_runs().items():
        print(f"{kind:18s} {run['params']:10,} {run['val_accuracy'][-1]:14.4f} "
              f"{max(run['val_accuracy']):8.4f} {run['seconds']:9.1f}")

    print("\n=== activation memory, max-pool model ===")
    model = _model("max pool")
    total_activations = 0
    for layer in model.layers:
        shape = layer.output.shape[1:]
        if None in shape:
            continue
        dims = [int(s) for s in shape]
        activation_bytes = int(np.prod(dims)) * 4
        weight_bytes = int(sum(np.prod(w.shape) for w in layer.weights)) * 4
        total_activations += activation_bytes
        print(f"{type(layer).__name__:16s} {str(tuple(dims)):18s} "
              f"activations {activation_bytes:9,} bytes  "
              f"weights {weight_bytes:9,} bytes")
    print(f"total activations per image: {total_activations:,} bytes")
    for batch in (32, 128, 512):
        print(f"  batch {batch:4d}: {total_activations * batch / 1e6:8.2f} MB "
              f"of activations (forward only)")

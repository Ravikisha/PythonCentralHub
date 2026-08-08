"""Figures for *Normalisation Beyond Batch: Layer, Group and Instance*.

``norm-axes``
    Which axes each normaliser reduces over, computed on a real tensor rather
    than asserted — the number of independent mean/variance pairs each one
    estimates is the whole story.

``norm-batch-size``
    The measurement that decides which to use: accuracy against batch size for
    four normalisers.

``norm-statistics``
    How many values each normaliser averages over to estimate one mean, as a
    function of batch size — the reason BN degrades and the others do not.
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

LIMIT = 4000
EPOCHS = 6
BATCHES = (4, 16, 64, 256)
SHAPE = (8, 4, 4, 6)          # batch, height, width, channels
GROUPS = 3


def _reference(x: np.ndarray, kind: str, groups: int = GROUPS) -> np.ndarray:
    """Normalise by hand so each definition is explicit."""
    epsilon = 1e-3
    if kind == "batch":                       # per channel, over N, H, W
        axes = (0, 1, 2)
    elif kind == "layer":                     # per sample, over H, W, C
        axes = (1, 2, 3)
    elif kind == "instance":                  # per sample and channel, over H, W
        axes = (1, 2)
    elif kind == "group":
        batch, height, width, channels = x.shape
        grouped = x.reshape(batch, height, width, groups, channels // groups)
        mean = grouped.mean(axis=(1, 2, 4), keepdims=True)
        variance = grouped.var(axis=(1, 2, 4), keepdims=True)
        return ((grouped - mean) / np.sqrt(variance + epsilon)).reshape(x.shape)
    else:
        raise ValueError(kind)
    mean = x.mean(axis=axes, keepdims=True)
    variance = x.var(axis=axes, keepdims=True)
    return (x - mean) / np.sqrt(variance + epsilon)


def _statistic_count(kind: str, batch: int, height: int = 4, width: int = 4,
                     channels: int = 6, groups: int = GROUPS) -> int:
    """How many values go into one mean estimate."""
    if kind == "batch":
        return batch * height * width
    if kind == "layer":
        return height * width * channels
    if kind == "instance":
        return height * width
    return height * width * (channels // groups)


KINDS = ("batch", "layer", "group", "instance")


@functools.lru_cache(maxsize=1)
def _axis_demo() -> dict:
    rng = np.random.default_rng(0)
    x = (rng.standard_normal(SHAPE) * np.array([1.0, 3.0, 0.5, 8.0, 2.0, 0.2])
         + np.array([0.0, 5.0, -2.0, 20.0, 1.0, -0.5])).astype("float32")
    out = {"input": x, "results": {}}
    for kind in KINDS:
        normalised = _reference(x, kind)
        out["results"][kind] = {
            "normalised": normalised,
            "pairs": {"batch": SHAPE[3], "layer": SHAPE[0],
                      "instance": SHAPE[0] * SHAPE[3],
                      "group": SHAPE[0] * GROUPS}[kind],
            "values_per_estimate": _statistic_count(kind, SHAPE[0]),
            "channel_means": normalised.mean(axis=(0, 1, 2)),
            "sample_means": normalised.mean(axis=(1, 2, 3)),
        }
    return out


def norm_axes(fig, axes, p: Palette) -> None:
    info = _axis_demo()
    grid = fig.subplots(1, 5)
    grid[0].imshow(info["input"].mean(axis=(1, 2)), aspect="auto", cmap="RdBu_r")
    grid[0].set_title(f"input, per sample x channel\nspread "
                      f"{info['input'].std():.2f}", fontsize=8.5)
    for ax, kind in zip(grid[1:], KINDS):
        result = info["results"][kind]
        ax.imshow(result["normalised"].mean(axis=(1, 2)), aspect="auto",
                  cmap="RdBu_r", vmin=-2, vmax=2)
        ax.set_title(f"{kind} norm\n{result['pairs']} mean/var pairs",
                     fontsize=8.5)
    for ax in grid:
        ax.set_xlabel("channel", fontsize=8)
        ax.set_ylabel("sample", fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def _model(kind: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((28, 28, 1))]
    for filters in (32, 64):
        layers.append(keras.layers.Conv2D(filters, 3, padding="same",
                                          use_bias=False))
        if kind == "batch":
            # momentum=0.9, not the 0.99 default: a large batch means FEWER
            # optimiser steps, so the default moving average never converges
            # and BN would appear to get worse as the batch grows.
            layers.append(keras.layers.BatchNormalization(momentum=0.9))
        elif kind == "layer":
            layers.append(keras.layers.LayerNormalization())
        elif kind == "group":
            layers.append(keras.layers.GroupNormalization(groups=8))
        layers.append(keras.layers.Activation("relu"))
        layers.append(keras.layers.MaxPooling2D(2))
    layers.append(keras.layers.GlobalAveragePooling2D())
    layers.append(keras.layers.Dense(10, activation="softmax"))
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


VARIANTS = ("none", "batch", "layer", "group")


@functools.lru_cache(maxsize=1)
def _batch_runs() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=False)
    out = {}
    for kind in VARIANTS:
        scores = []
        for batch in BATCHES:
            model = _model(kind)
            history = model.fit(data["x_train"], data["y_train"],
                                epochs=EPOCHS, batch_size=batch, verbose=0,
                                validation_data=(data["x_test"],
                                                 data["y_test"]))
            scores.append(float(history.history["val_accuracy"][-1]))
        out[kind] = scores
    return out


def norm_batch_size(fig, axes, p: Palette) -> None:
    runs = _batch_runs()
    ax = fig.subplots(1, 1)
    colors = {"none": p.muted, "batch": p.red, "layer": p.blue,
              "group": p.green}
    for kind, scores in runs.items():
        ax.plot(BATCHES, scores, "o-", ms=6, lw=2.0, color=colors[kind],
                label=f"{kind} — batch {BATCHES[0]}: {scores[0]:.4f}, "
                      f"batch {BATCHES[-1]}: {scores[-1]:.4f}")
        for batch, score in zip(BATCHES, scores):
            ax.annotate(f"{score:.3f}", (batch, score),
                        textcoords="offset points", xytext=(0, 7),
                        ha="center", fontsize=7, color=colors[kind])
    ax.set_xscale("log", base=2)
    ax.set_xticks(list(BATCHES))
    ax.set_xticklabels([str(b) for b in BATCHES])
    ax.set_xlabel("batch size")
    ax.set_ylabel(f"validation accuracy after {EPOCHS} epochs")
    ax.set_title(f"Fashion-MNIST, {LIMIT} rows — which normaliser survives a small "
                 f"batch?", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower right")


def norm_statistics(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    batches = np.array([1, 2, 4, 8, 16, 32, 64, 128])
    colors = {"batch": p.red, "layer": p.blue, "group": p.green,
              "instance": p.amber}
    # A 16x16 feature map with 64 channels, groups of 8 — a realistic block.
    for kind, color in colors.items():
        counts = [_statistic_count(kind, int(b), height=16, width=16,
                                   channels=64, groups=8) for b in batches]
        ax.plot(batches, counts, "o-", ms=5, lw=1.9, color=color,
                label=f"{kind} norm — {counts[0]:,} at batch 1")
    ax.axhline(30, color=p.grid, lw=1.4, ls="--")
    ax.annotate("below ~30 values an estimate is mostly noise", (1.1, 34),
                fontsize=8, color=p.muted)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(list(batches))
    ax.set_xticklabels([str(b) for b in batches])
    ax.set_xlabel("batch size")
    ax.set_ylabel("values averaged for one mean estimate (log scale)")
    ax.set_title("16x16 feature map, 64 channels, groups of 8", fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("norm-axes", norm_axes, size=(9.6, 2.6), axes=False),
    figure("norm-batch-size", norm_batch_size, size=(8.0, 3.8), axes=False),
    figure("norm-statistics", norm_statistics, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    keras = tf().keras
    info = _axis_demo()
    x = info["input"]
    print(f"=== a {SHAPE} tensor, channels deliberately on different scales ===")
    print(f"per-channel means {np.round(x.mean(axis=(0, 1, 2)), 3).tolist()}")
    print(f"per-channel stds  {np.round(x.std(axis=(0, 1, 2)), 3).tolist()}")

    print(f"\n{'normaliser':12s} {'mean/var pairs':>15} "
          f"{'values per estimate':>21} {'max |mine - keras|':>20}")
    layers = {
        "batch": keras.layers.BatchNormalization(epsilon=1e-3),
        "layer": keras.layers.LayerNormalization(epsilon=1e-3, axis=(1, 2, 3)),
        "group": keras.layers.GroupNormalization(groups=GROUPS, epsilon=1e-3),
        "instance": keras.layers.GroupNormalization(groups=SHAPE[3],
                                                   epsilon=1e-3),
    }
    for kind in KINDS:
        mine = info["results"][kind]["normalised"]
        theirs = layers[kind](x, training=True).numpy()
        print(f"{kind:12s} {info['results'][kind]['pairs']:15d} "
              f"{info['results'][kind]['values_per_estimate']:21d} "
              f"{np.abs(mine - theirs).max():20.2e}")

    print("\nafter normalising, what is actually centred:")
    for kind in KINDS:
        result = info["results"][kind]
        print(f"  {kind:9s} per-channel means "
              f"{np.abs(result['channel_means']).max():.2e}  "
              f"per-sample means {np.abs(result['sample_means']).max():.2e}")

    print(f"\n=== accuracy against batch size, {EPOCHS} epochs ===")
    runs = _batch_runs()
    print(f"{'normaliser':12s} " + " ".join(f"{b:>9}" for b in BATCHES))
    for kind, scores in runs.items():
        print(f"{kind:12s} " + " ".join(f"{s:9.4f}" for s in scores))

    print("\n=== values per mean estimate, 16x16x64 feature map ===")
    print(f"{'batch':>7} {'batch norm':>12} {'layer norm':>12} "
          f"{'group norm':>12} {'instance':>10}")
    for batch in (1, 2, 8, 32, 128):
        row = [_statistic_count(kind, batch, 16, 16, 64, 8) for kind in
               ("batch", "layer", "group", "instance")]
        print(f"{batch:7d} {row[0]:12,} {row[1]:12,} {row[2]:12,} {row[3]:10,}")

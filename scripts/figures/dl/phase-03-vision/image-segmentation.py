"""Figures for *Image Segmentation*.

The dataset is generated here rather than downloaded: 64x64 scenes containing a
disc, a square and a triangle on a noisy background, with an exact per-pixel
label map. Synthetic data is the honest choice for a page about segmentation
mechanics — every mask is known to be correct, and the whole page runs on a CPU
in a couple of minutes.

``segmentation-samples``
    Inputs, ground-truth masks and predictions side by side.

``upsampling-comparison``
    Three ways to get the resolution back — transposed convolution, upsampling
    plus convolution, and no skip connections at all.

``iou-by-class``
    Per-class IoU, which is where a segmentation model's real behaviour shows.
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

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

SIDE = 64
TRAIN = 1200
TEST = 300
EPOCHS = 12
CLASS_NAMES = ("background", "disc", "square", "triangle")


def _scene(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    image = rng.normal(0.5, 0.06, (SIDE, SIDE)).astype("float32")
    mask = np.zeros((SIDE, SIDE), "int32")
    ys, xs = np.mgrid[0:SIDE, 0:SIDE]

    radius = rng.integers(7, 12)
    cy, cx = rng.integers(radius, SIDE - radius, 2)
    disc = (ys - cy) ** 2 + (xs - cx) ** 2 <= radius ** 2
    image[disc] = 0.9
    mask[disc] = 1

    size = rng.integers(10, 18)
    sy, sx = rng.integers(0, SIDE - size, 2)
    image[sy:sy + size, sx:sx + size] = 0.15
    mask[sy:sy + size, sx:sx + size] = 2

    height = rng.integers(12, 20)
    ty, tx = rng.integers(0, SIDE - height, 2)
    for row in range(height):
        half = int((row / height) * height / 2)
        left = max(tx + height // 2 - half, 0)
        right = min(tx + height // 2 + half + 1, SIDE)
        image[ty + row, left:right] = 0.65
        mask[ty + row, left:right] = 3
    return np.clip(image, 0, 1)[..., None], mask


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    rng = np.random.default_rng(0)
    images, masks = [], []
    for _ in range(TRAIN + TEST):
        image, mask = _scene(rng)
        images.append(image)
        masks.append(mask)
    images = np.stack(images)
    masks = np.stack(masks)
    counts = np.bincount(masks.ravel(), minlength=4)
    return {"x_train": images[:TRAIN], "y_train": masks[:TRAIN],
            "x_test": images[TRAIN:], "y_test": masks[TRAIN:],
            "pixel_share": counts / counts.sum()}


def _model(kind: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((SIDE, SIDE, 1))
    down1 = keras.layers.Conv2D(16, 3, padding="same", activation="relu")(inputs)
    pooled1 = keras.layers.MaxPooling2D(2)(down1)
    down2 = keras.layers.Conv2D(32, 3, padding="same",
                                activation="relu")(pooled1)
    pooled2 = keras.layers.MaxPooling2D(2)(down2)
    middle = keras.layers.Conv2D(64, 3, padding="same",
                                 activation="relu")(pooled2)

    if kind == "upsample + conv":
        x = keras.layers.UpSampling2D(2)(middle)
        x = keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
        x = keras.layers.Concatenate()([x, down2])
        x = keras.layers.UpSampling2D(2)(x)
        x = keras.layers.Conv2D(16, 3, padding="same", activation="relu")(x)
        x = keras.layers.Concatenate()([x, down1])
    elif kind == "no skips":
        x = keras.layers.Conv2DTranspose(32, 3, strides=2, padding="same",
                                         activation="relu")(middle)
        x = keras.layers.Conv2DTranspose(16, 3, strides=2, padding="same",
                                         activation="relu")(x)
    else:                                     # transposed conv with skips
        x = keras.layers.Conv2DTranspose(32, 3, strides=2, padding="same",
                                         activation="relu")(middle)
        x = keras.layers.Concatenate()([x, down2])
        x = keras.layers.Conv2DTranspose(16, 3, strides=2, padding="same",
                                         activation="relu")(x)
        x = keras.layers.Concatenate()([x, down1])

    outputs = keras.layers.Conv2D(4, 1, activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


KINDS = ("transposed conv + skips", "upsample + conv", "no skips")


def _iou(truth: np.ndarray, predicted: np.ndarray) -> list[float]:
    out = []
    for index in range(4):
        intersection = float(((truth == index) & (predicted == index)).sum())
        union = float(((truth == index) | (predicted == index)).sum())
        out.append(intersection / union if union else float("nan"))
    return out


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    data = _data()
    out = {}
    for kind in KINDS:
        model = _model(kind)
        started = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=32, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        probabilities = model.predict(data["x_test"], verbose=0)
        predicted = probabilities.argmax(axis=-1)
        out[kind] = {
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "iou": _iou(data["y_test"], predicted),
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
            "predicted": predicted,
        }
    return out


def segmentation_samples(fig, axes, p: Palette) -> None:
    data = _data()
    predicted = _runs()[KINDS[0]]["predicted"]
    grid = fig.subplots(3, 4)
    for column in range(4):
        grid[0][column].imshow(data["x_test"][column][..., 0], cmap="gray")
        grid[0][column].set_title(f"input {column}", fontsize=8)
        grid[1][column].imshow(data["y_test"][column], cmap="tab10", vmin=0,
                               vmax=9)
        grid[1][column].set_title("true mask", fontsize=8)
        grid[2][column].imshow(predicted[column], cmap="tab10", vmin=0, vmax=9)
        wrong = float((predicted[column] != data["y_test"][column]).mean())
        grid[2][column].set_title(f"predicted — {wrong:.3%} wrong", fontsize=8)
    for row in grid:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


def upsampling_comparison(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for (kind, run), color in zip(runs.items(), p.cycle):
        left.plot(epochs, run["val_accuracy"], lw=1.8, color=color,
                  label=f"{kind} — {run['val_accuracy'][-1]:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation pixel accuracy")
    left.set_title(f"{TRAIN} synthetic scenes, {EPOCHS} epochs", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    names = list(runs)
    positions = np.arange(len(names))
    means = [float(np.nanmean(runs[k]["iou"])) for k in names]
    best = max(means)
    right.bar(positions, means, 0.5,
              color=[p.green if abs(m - best) < 1e-9 else p.blue
                     for m in means])
    for x, value, key in zip(positions, means, names):
        right.annotate(f"{value:.4f}\n{runs[key]['params']:,} params",
                       (x, value), textcoords="offset points", xytext=(0, 4),
                       ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([n.replace(" + ", "\n+ ") for n in names],
                          fontsize=7.5)
    right.set_ylim(0, 1.15)
    right.set_ylabel("mean IoU over four classes")
    right.set_title("mean intersection over union", fontsize=10)


def iou_by_class(fig, axes, p: Palette) -> None:
    runs = _runs()
    data = _data()
    ax = fig.subplots(1, 1)
    positions = np.arange(len(CLASS_NAMES))
    width = 0.26
    for offset, (kind, color) in zip((-width, 0, width),
                                    zip(KINDS, (p.green, p.blue, p.red))):
        ax.bar(positions + offset, runs[kind]["iou"], width, color=color,
               label=kind)
    for index, share in enumerate(data["pixel_share"]):
        ax.annotate(f"{share:.1%} of pixels", (index, 1.04),
                    ha="center", fontsize=7.5, color=p.muted)
    ax.set_xticks(positions)
    ax.set_xticklabels(CLASS_NAMES, fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("intersection over union")
    ax.set_title("IoU per class, with each class's share of all pixels",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")


FIGURES = [
    figure("segmentation-samples", segmentation_samples, size=(8.0, 6.0),
           axes=False),
    figure("upsampling-comparison", upsampling_comparison, size=(9.4, 3.6),
           axes=False),
    figure("iou-by-class", iou_by_class, size=(8.0, 3.8), axes=False),
]


if __name__ == "__main__":
    data = _data()
    print(f"=== synthetic scenes: {TRAIN} train, {TEST} test, "
          f"{SIDE}x{SIDE} ===")
    print(f"pixel share per class: " +
          "  ".join(f"{name} {share:.4f}"
                    for name, share in zip(CLASS_NAMES, data["pixel_share"])))
    print(f"predicting 'background' everywhere would score "
          f"{data['pixel_share'][0]:.4f} pixel accuracy")

    print(f"\n=== three upsampling designs, {EPOCHS} epochs ===")
    print(f"{'design':26s} {'params':>9} {'pixel acc':>10} {'mean IoU':>9} "
          f"{'seconds':>9}")
    runs = _runs()
    for kind, run in runs.items():
        print(f"{kind:26s} {run['params']:9,} "
              f"{run['val_accuracy'][-1]:10.4f} "
              f"{float(np.nanmean(run['iou'])):9.4f} {run['seconds']:9.1f}")

    print("\n=== IoU per class ===")
    print(f"{'design':26s} " + " ".join(f"{name:>11}" for name in CLASS_NAMES))
    for kind, run in runs.items():
        print(f"{kind:26s} " + " ".join(f"{v:11.4f}" for v in run["iou"]))
    print("\npixel accuracy is dominated by the background; IoU is not, which")
    print("is why segmentation is reported with IoU")

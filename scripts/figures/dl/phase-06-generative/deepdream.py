"""Figures for *DeepDream*.

DeepDream is gradient ascent on an activation instead of descent on a loss. That
makes it the cheapest possible demonstration that a trained network holds a
generative model of its own features -- and it needs no generator, no
discriminator and no second training run.

There are no pretrained ImageNet weights cached on this machine, so the features
come from a small convnet trained here on Fashion-MNIST. That is a real
limitation and it changes what the dreams look like: the features are
garment-shaped, not dog-shaped.

``layer-depth``
    What each layer dreams, from the first convolution to the last, with the
    activation gain each one achieves.

``step-size``
    Step size against activation gain and against how far the image travelled --
    the two failure modes are a step too small to matter and one that saturates.

``octaves``
    The multi-scale trick, measured: dreaming at several resolutions produces
    larger structures than dreaming at one.
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

LIMIT = 12000
EPOCHS = 12
SIZE = 56                      # dreams are run at 2x the training resolution
STEPS = 40
STEP_SIZE = 0.05
STEP_SIZES = (0.005, 0.02, 0.05, 0.2, 0.5)
OCTAVES = (1, 2, 3)
OCTAVE_SCALE = 1.3


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("fashion", limit=LIMIT, flat=False)


@functools.lru_cache(maxsize=1)
def _features() -> dict:
    """A small convnet trained here, because no pretrained weights are cached.

    Fully convolutional up to the head, so the same weights accept a larger
    input than they were trained on -- which is what dreaming at 56x56 needs.
    """
    keras = tf().keras
    data = _data()
    seed_everything(0)
    inputs = keras.layers.Input((None, None, 1))
    x = keras.layers.Conv2D(16, 3, padding="same", activation="relu",
                            name="conv1")(inputs)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Conv2D(32, 3, padding="same", activation="relu",
                            name="conv2")(x)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Conv2D(64, 3, padding="same", activation="relu",
                           name="conv3")(x)
    pooled = keras.layers.GlobalAveragePooling2D()(x)
    outputs = keras.layers.Dense(10, activation="softmax")(pooled)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "seconds": time.perf_counter() - started}


def _layer_names() -> tuple:
    model = _features()["model"]
    return tuple(layer.name for layer in model.layers
                 if layer.name.startswith("conv"))


@functools.lru_cache(maxsize=16)
def _extractor(layer: str):
    keras = tf().keras
    model = _features()["model"]
    return keras.Model(model.inputs, model.get_layer(layer).output)


def _start_image(seed: int = 0) -> np.ndarray:
    """Mild noise around mid grey: a blank canvas has no gradient to amplify."""
    rng = np.random.default_rng(seed)
    return np.clip(0.5 + rng.normal(0, 0.05, (1, SIZE, SIZE, 1)),
                   0, 1).astype("float32")


def _dream(layer: str, image=None, steps=None, step_size=None) -> dict:
    """Gradient ASCENT on the mean activation of one layer."""
    tensorflow = tf()
    extractor = _extractor(layer)
    current = _start_image() if image is None else image.copy()
    steps = STEPS if steps is None else int(steps)
    step_size = STEP_SIZE if step_size is None else float(step_size)
    start = float(extractor.predict(current, verbose=0).mean())
    original = current.copy()
    for _ in range(steps):
        tensor = tensorflow.convert_to_tensor(current)
        with tensorflow.GradientTape() as tape:
            tape.watch(tensor)
            activation = tensorflow.reduce_mean(extractor(tensor))
        gradient = tape.gradient(activation, tensor).numpy()
        # Normalise the gradient: its raw scale depends on the layer, so a
        # single step size would mean something different at every depth.
        gradient /= (np.abs(gradient).std() + 1e-8)
        current = np.clip(current + step_size * gradient, 0, 1).astype("float32")
    end = float(extractor.predict(current, verbose=0).mean())
    return {"image": current, "start": start, "end": end,
            "gain": end / start if start else float("nan"),
            "travel": float(np.abs(current - original).mean())}


@functools.lru_cache(maxsize=1)
def _depth_runs() -> dict:
    return {layer: _dream(layer) for layer in _layer_names()}


@functools.lru_cache(maxsize=1)
def _step_runs() -> dict:
    layer = _layer_names()[-1]
    return {size: _dream(layer, step_size=size) for size in STEP_SIZES}


def _octave_dream(layer: str, octaves: int) -> dict:
    """Dream at increasing resolutions, carrying the result upward.

    Small images make small features; starting small and scaling up is how the
    original DeepDream produced structures larger than one receptive field.
    """
    tensorflow = tf()
    base = _start_image()
    size = max(8, int(SIZE / OCTAVE_SCALE ** (octaves - 1)))
    current = tensorflow.image.resize(base, (size, size)).numpy()
    for octave in range(int(octaves)):
        result = _dream(layer, current, steps=max(1, STEPS // max(1, octaves)))
        current = result["image"]
        if octave + 1 < octaves:
            size = int(size * OCTAVE_SCALE)
            current = tensorflow.image.resize(current, (size, size)).numpy()
    final = tensorflow.image.resize(current, (SIZE, SIZE)).numpy()
    extractor = _extractor(layer)
    return {"image": final,
            "activation": float(extractor.predict(final, verbose=0).mean()),
            "roughness": float(np.abs(np.diff(final[0, :, :, 0], axis=0)).mean())}


@functools.lru_cache(maxsize=1)
def _octave_runs() -> dict:
    layer = _layer_names()[-1]
    return {count: _octave_dream(layer, count) for count in OCTAVES}


def layer_depth(fig, axes, p: Palette) -> None:
    runs = _depth_runs()
    layers = list(runs)
    top = fig.subplots(2, 1, height_ratios=(1.0, 0.85))
    strip, bars = top
    canvas = np.concatenate([runs[layer]["image"][0, :, :, 0]
                             for layer in layers], axis=1)
    strip.imshow(canvas, cmap="gray")
    strip.set_title(" | ".join(layers) + "   (the same noise image, "
                    f"{STEPS} ascent steps each)", fontsize=9.5)
    strip.set_xticks([])
    strip.set_yticks([])
    strip.grid(False)

    positions = np.arange(len(layers))
    gains = [runs[layer]["gain"] for layer in layers]
    bars.bar(positions, gains, 0.5, color=p.blue)
    for x, layer in zip(positions, layers):
        entry = runs[layer]
        bars.annotate(f"{entry['gain']:.2f}x\n{entry['start']:.3f} -> "
                      f"{entry['end']:.3f}", (x, entry["gain"]),
                      textcoords="offset points", xytext=(0, 4), ha="center",
                      fontsize=7.5, color=p.fg)
    bars.set_xticks(positions)
    bars.set_xticklabels(layers)
    bars.set_ylim(0, max(gains) * 1.35)
    bars.set_ylabel("mean activation, after / before")
    bars.set_title("deeper layers gain more, because they have more to gain",
                   fontsize=9.5)


def step_size(fig, axes, p: Palette) -> None:
    runs = _step_runs()
    sizes = list(runs)
    top, bottom = fig.subplots(2, 1, height_ratios=(1.0, 0.9))
    canvas = np.concatenate([runs[size]["image"][0, :, :, 0] for size in sizes],
                            axis=1)
    top.imshow(canvas, cmap="gray")
    top.set_title("step size " + ", ".join(str(s) for s in sizes), fontsize=9.5)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    gains = [runs[size]["gain"] for size in sizes]
    travel = [runs[size]["travel"] for size in sizes]
    bottom.plot(sizes, gains, "o-", ms=6, lw=2.0, color=p.green,
                label="activation gain")
    for size, value in zip(sizes, gains):
        bottom.annotate(f"{value:.2f}x", (size, value), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=7.5,
                        color=p.green)
    twin = bottom.twinx()
    twin.plot(sizes, travel, "s--", ms=5, lw=1.8, color=p.amber,
              label="mean pixel change")
    twin.set_ylabel("mean |pixel change|")
    bottom.set_xscale("log")
    bottom.minorticks_off()
    bottom.set_xticks(sizes)
    bottom.set_xticklabels([str(s) for s in sizes])
    bottom.set_xlabel("step size")
    bottom.set_ylabel("activation gain")
    lines = bottom.get_lines() + twin.get_lines()
    bottom.legend(lines, [line.get_label() for line in lines], fontsize=8,
                  loc="upper left")
    bottom.set_title("a bigger step is not a better dream once the pixels clip",
                     fontsize=9.5)


def octaves(fig, axes, p: Palette) -> None:
    runs = _octave_runs()
    counts = list(runs)
    top, bottom = fig.subplots(2, 1, height_ratios=(1.0, 0.75))
    canvas = np.concatenate([runs[count]["image"][0, :, :, 0]
                             for count in counts], axis=1)
    top.imshow(canvas, cmap="gray")
    top.set_title(", ".join(f"{count} octave" + ("s" if count > 1 else "")
                            for count in counts), fontsize=9.5)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    positions = np.arange(len(counts))
    width = 0.38
    activation = [runs[count]["activation"] for count in counts]
    roughness = [runs[count]["roughness"] for count in counts]
    bottom.bar(positions - width / 2, activation, width * 0.9, color=p.blue,
               label="mean activation reached")
    for x, value in zip(positions - width / 2, activation):
        bottom.annotate(f"{value:.3f}", (x, value), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=7,
                        color=p.fg)
    scale = max(activation) / max(roughness) if max(roughness) else 1.0
    bottom.bar(positions + width / 2, [r * scale for r in roughness],
               width * 0.9, color=p.amber,
               label="fine-scale roughness (scaled)")
    for x, value in zip(positions + width / 2, roughness):
        bottom.annotate(f"{value:.4f}", (x, value * scale), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=7,
                        color=p.fg)
    bottom.set_xticks(positions)
    bottom.set_xticklabels([f"{count} octave" + ("s" if count > 1 else "")
                            for count in counts])
    bottom.set_ylabel("activation / scaled roughness")
    bottom.set_title("more octaves: bigger structures, less pixel-scale noise",
                     fontsize=9.5)
    bottom.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("layer-depth", layer_depth, size=(9.0, 5.0), axes=False),
    figure("step-size", step_size, size=(9.2, 5.0), axes=False),
    figure("octaves", octaves, size=(8.4, 4.6), axes=False),
]


if __name__ == "__main__":
    info = _features()
    print(f"=== the feature network (trained here, not downloaded) ===")
    print(f"{info['model'].count_params():,} parameters, {EPOCHS} epochs on "
          f"Fashion-MNIST, {info['seconds']:.0f}s")
    print(f"validation accuracy {info['accuracy']:.4f}")
    print("no ImageNet weights are cached on this machine, so the dreams below")
    print("amplify garment features -- the mechanism is identical, the visual")
    print("vocabulary is not")

    print(f"\n=== what each layer dreams ({STEPS} steps, step {STEP_SIZE}) ===")
    runs = _depth_runs()
    print(f"{'layer':8s} {'activation before':>18} {'after':>9} {'gain':>8} "
          f"{'mean pixel change':>18}")
    for layer, entry in runs.items():
        print(f"{layer:8s} {entry['start']:18.4f} {entry['end']:9.4f} "
              f"{entry['gain']:8.2f} {entry['travel']:18.4f}")

    print(f"\n=== step size, on {_layer_names()[-1]} ===")
    steps = _step_runs()
    print(f"{'step':>8} {'activation before':>18} {'after':>9} {'gain':>8} "
          f"{'mean pixel change':>18}")
    for size, entry in steps.items():
        print(f"{size:8.3f} {entry['start']:18.4f} {entry['end']:9.4f} "
              f"{entry['gain']:8.2f} {entry['travel']:18.4f}")
    print("the gradient is normalised by its own standard deviation before each")
    print("step, so these step sizes are comparable across layers")

    print(f"\n=== octaves (multi-scale), on {_layer_names()[-1]} ===")
    octave_runs = _octave_runs()
    print(f"{'octaves':>8} {'activation':>11} {'roughness':>10}")
    for count, entry in octave_runs.items():
        print(f"{count:8d} {entry['activation']:11.4f} "
              f"{entry['roughness']:10.4f}")
    print("total ascent steps are held roughly constant across the octave")
    print("counts, so this compares HOW the steps are spent, not how many")

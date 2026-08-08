"""Figures for *Mixed Precision and Multi-GPU Training*.

Mixed precision is a GPU feature. This machine has no GPU, and rather than
describe a speed-up that cannot be shown, this module measures what the policy
actually does on a CPU -- which is a useful result in its own right, because
"turn on mixed precision for a free 2x" is advice people apply on hardware
where it does nothing or hurts.

What IS measurable here, and matters everywhere:

``policy``
    What `set_global_policy` changes about a model: variable dtypes, activation
    dtypes, and where the float32 boundary sits.

``cpu-cost``
    Step time under each policy on this CPU, which is the claim the advice
    makes and the one that fails here.

``overflow``
    Why loss scaling exists, in float16 arithmetic -- the gradient values that
    silently become zero without it.
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

LIMIT = 6000
EPOCHS = 3
BATCH = 128
TIMED_STEPS = 40
POLICIES = ("float32", "mixed_float16", "float64")


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


def _build(keras, policy: str):
    """A convnet built under a given dtype policy."""
    keras.mixed_precision.set_global_policy(policy)
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(16, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(32, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation="relu"),
        # The output layer is forced back to float32 even under a mixed
        # policy: a float16 softmax loses precision exactly where it matters.
        # The softmax belongs here too -- the loss below expects probabilities,
        # and feeding it raw logits trains against nonsense without erroring.
        keras.layers.Dense(10, activation="softmax", dtype="float32"),
    ])
    return model


@functools.lru_cache(maxsize=4)
def _describe(policy: str) -> dict:
    """What the policy changed, layer by layer."""
    keras = tf().keras
    model = _build(keras, policy)
    layers = []
    for layer in model.layers:
        if not layer.weights:
            continue
        layers.append({
            "name": layer.name,
            "variable": str(layer.weights[0].dtype).replace("<dtype: '", "")
                        .replace("'>", ""),
            "compute": str(layer.compute_dtype),
        })
    keras.mixed_precision.set_global_policy("float32")
    return {"layers": layers,
            "parameters": int(model.count_params())}


@functools.lru_cache(maxsize=4)
def _timed(policy: str) -> dict:
    """Step time and accuracy under one policy."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    model = _build(keras, policy)
    optimizer = keras.optimizers.Adam(1e-3)
    if policy == "mixed_float16":
        # Without this, small gradients underflow to zero in float16.
        optimizer = keras.mixed_precision.LossScaleOptimizer(optimizer)
    model.compile(optimizer, "sparse_categorical_crossentropy",
                  metrics=["accuracy"])

    # Time the step on a FRESH model, so the repeated updates on one batch do
    # not handicap the accuracy run that follows.
    timer = _build(keras, policy)
    timing_optimizer = keras.optimizers.Adam(1e-3)
    if policy == "mixed_float16":
        timing_optimizer = keras.mixed_precision.LossScaleOptimizer(
            timing_optimizer)
    timer.compile(timing_optimizer, "sparse_categorical_crossentropy")
    images = data["x_train"][:BATCH]
    labels = data["y_train"][:BATCH]
    timer.train_on_batch(images, labels)          # warm-up / trace
    started = time.perf_counter()
    for _ in range(TIMED_STEPS):
        timer.train_on_batch(images, labels)
    per_step = (time.perf_counter() - started) / TIMED_STEPS * 1000.0

    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=BATCH, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    seconds = time.perf_counter() - started
    keras.mixed_precision.set_global_policy("float32")
    del tensorflow
    return {"per_step_ms": per_step, "seconds": seconds,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "curve": [float(v) for v in history.history["val_accuracy"]]}


@functools.lru_cache(maxsize=1)
def _overflow() -> dict:
    """Where float16 runs out of range, and what loss scaling recovers."""
    magnitudes = np.array([1e-1, 1e-3, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10])
    as_float16 = magnitudes.astype("float16").astype("float64")
    survived = as_float16 > 0
    scaled = (magnitudes * 1024.0).astype("float16").astype("float64") / 1024.0
    scaled_survived = scaled > 0
    finfo = np.finfo(np.float16)
    return {"magnitudes": magnitudes, "as_float16": as_float16,
            "survived": survived, "scaled": scaled,
            "scaled_survived": scaled_survived,
            "smallest_normal": float(finfo.tiny),
            "smallest_subnormal": float(finfo.smallest_subnormal),
            "largest": float(finfo.max)}


def policy(fig, axes, p: Palette) -> None:
    described = {name: _describe(name) for name in ("float32",
                                                    "mixed_float16")}
    left, right = fig.subplots(1, 2)
    layers = [entry["name"] for entry in described["float32"]["layers"]]
    positions = np.arange(len(layers))
    left.axis("off")
    left.set_title("what set_global_policy('mixed_float16') changes",
                   fontsize=10)
    rows = [("layer", "variables", "computes in")]
    for entry in described["mixed_float16"]["layers"]:
        rows.append((entry["name"], entry["variable"], entry["compute"]))
    for index, row in enumerate(rows):
        weight = "bold" if index == 0 else "normal"
        colour = p.fg if index == 0 else p.muted
        for column, value in enumerate(row):
            left.text(0.02 + column * 0.36, 0.92 - index * 0.115, value,
                      fontsize=8.5, color=colour, weight=weight,
                      transform=left.transAxes, family="monospace")

    both = ("float32", "mixed_float16")
    width = 0.38
    for index, name in enumerate(both):
        computes = [1.0 if entry["compute"] == "float16" else 0.0
                    for entry in described[name]["layers"]]
        right.bar(positions + (index - 0.5) * width, computes, width * 0.9,
                  color=p.amber if index else p.blue, label=name)
    right.set_xticks(positions)
    right.set_xticklabels(layers, fontsize=7.5, rotation=20, ha="right")
    right.set_yticks([0, 1])
    right.set_yticklabels(["float32", "float16"])
    right.set_ylim(-0.1, 1.5)
    right.set_title("the final layer stays float32 by design", fontsize=10)
    right.legend(fontsize=8, loc="upper left")


def cpu_cost(fig, axes, p: Palette) -> None:
    runs = {name: _timed(name) for name in POLICIES}
    left, right = fig.subplots(1, 2)
    names = list(runs)
    positions = np.arange(len(names))
    per_step = [runs[name]["per_step_ms"] for name in names]
    baseline = runs["float32"]["per_step_ms"]
    colours = [p.blue, p.red, p.muted]
    left.bar(positions, per_step, 0.5, color=colours)
    for x, name in zip(positions, names):
        value = runs[name]["per_step_ms"]
        left.annotate(f"{value:.2f} ms\n({value / baseline:.2f}x)", (x, value),
                      xytext=(0, 4), textcoords="offset points", ha="center",
                      fontsize=8, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(names, fontsize=8.5)
    left.set_ylim(0, max(per_step) * 1.35)
    left.set_ylabel(f"ms per step (mean of {TIMED_STEPS})")
    left.set_title(f"on a CPU with {os.cpu_count()} cores and no GPU",
                   fontsize=10)

    for name, colour in zip(names, colours):
        curve = runs[name]["curve"]
        right.plot(range(1, len(curve) + 1), curve, "o-", ms=5, lw=1.9,
                   color=colour,
                   label=f"{name} ({runs[name]['accuracy']:.4f})")
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title("accuracy is unaffected -- only the speed claim fails",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def overflow(fig, axes, p: Palette) -> None:
    info = _overflow()
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(info["magnitudes"]))
    left.bar(positions, np.where(info["survived"], 1.0, 0.0), 0.38,
             color=p.blue, label="plain float16")
    left.bar(positions + 0.4, np.where(info["scaled_survived"], 1.0, 0.0),
             0.38, color=p.green, label="scaled by 1024 first")
    left.set_xticks(positions + 0.2)
    left.set_xticklabels([f"{m:.0e}" for m in info["magnitudes"]],
                         fontsize=7.5, rotation=30, ha="right")
    left.set_yticks([0, 1])
    left.set_yticklabels(["lost", "survives"])
    left.set_ylim(-0.1, 1.6)
    left.set_xlabel("gradient magnitude")
    left.set_title("what float16 can still represent", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    ranges = {
        "float16": (info["smallest_subnormal"], info["largest"]),
        "float32": (float(np.finfo(np.float32).smallest_subnormal),
                    float(np.finfo(np.float32).max)),
    }
    for index, (name, (low, high)) in enumerate(ranges.items()):
        right.plot([low, high], [index, index], lw=8,
                   color=p.amber if index == 0 else p.blue,
                   solid_capstyle="butt")
        right.annotate(f"{low:.1e}", (low, index), xytext=(0, 10),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
        right.annotate(f"{high:.1e}", (high, index), xytext=(0, 10),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    right.set_xscale("log")
    right.set_yticks([0, 1])
    right.set_yticklabels(list(ranges))
    right.set_ylim(-0.6, 1.6)
    right.set_xlabel("representable magnitude (log)")
    right.set_title("loss scaling moves gradients into the usable band",
                    fontsize=10)


FIGURES = [
    figure("policy", policy, size=(9.6, 3.4), axes=False),
    figure("cpu-cost", cpu_cost, size=(9.4, 3.4), axes=False),
    figure("overflow", overflow, size=(9.6, 3.4), axes=False),
]


if __name__ == "__main__":
    print("=== what the policy changes ===")
    for name in ("float32", "mixed_float16"):
        described = _describe(name)
        print(f"\n[{name}]  {described['parameters']:,} parameters")
        print(f"{'layer':22s} {'variables':>12} {'computes in':>13}")
        for entry in described["layers"]:
            print(f"{entry['name']:22s} {entry['variable']:>12} "
                  f"{entry['compute']:>13}")
    print("\nunder a mixed policy the VARIABLES stay float32 and the")
    print("COMPUTATION happens in float16; the last layer is pinned back to")
    print("float32 so the softmax and the loss keep their precision")

    print(f"\n=== step time on this CPU (no GPU available) ===")
    runs = {name: _timed(name) for name in POLICIES}
    baseline = runs["float32"]["per_step_ms"]
    print(f"{'policy':16s} {'ms/step':>9} {'relative':>9} {'3 epochs':>10} "
          f"{'accuracy':>9}")
    for name, entry in runs.items():
        print(f"{name:16s} {entry['per_step_ms']:9.2f} "
              f"{entry['per_step_ms'] / baseline:8.2f}x "
              f"{entry['seconds']:10.1f} {entry['accuracy']:9.4f}")
    ratio = runs["mixed_float16"]["per_step_ms"] / baseline
    verdict = "slower" if ratio > 1.02 else ("faster" if ratio < 0.98
                                             else "unchanged")
    print(f"mixed precision is {verdict} here ({ratio:.2f}x). float16 is a")
    print("GPU tensor-core feature; a CPU has no float16 execution units, so")
    print("the values are converted back and forth for nothing")

    info = _overflow()
    print(f"\n=== why loss scaling exists ===")
    print(f"float16 range: smallest subnormal "
          f"{info['smallest_subnormal']:.1e}, smallest normal "
          f"{info['smallest_normal']:.1e}, largest {info['largest']:.1e}")
    print(f"{'gradient':>10} {'as float16':>12} {'survives':>9} "
          f"{'scaled x1024':>13} {'survives':>9}")
    for index, magnitude in enumerate(info["magnitudes"]):
        print(f"{magnitude:10.0e} {info['as_float16'][index]:12.2e} "
              f"{str(bool(info['survived'][index])):>9} "
              f"{info['scaled'][index]:13.2e} "
              f"{str(bool(info['scaled_survived'][index])):>9}")
    print("a gradient that underflows to zero contributes nothing and raises")
    print("no error, which is why LossScaleOptimizer multiplies the loss")
    print("before the backward pass and divides it out afterwards")

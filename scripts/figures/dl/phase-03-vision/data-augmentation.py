"""Figures for *Data Augmentation for Small Datasets*.

``augmented-samples``
    One image put through the augmentation pipeline eight times, so "believable
    variety" is something you can check rather than trust.

``augmentation-effect``
    With and without augmentation at four training-set sizes. The benefit is
    entirely a function of how little data you have.

``augmentation-strength``
    Four strengths on the same 1,000 rows, including one strong enough to hurt.
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

SIZES = (500, 2000, 8000)
# Augmentation makes every epoch a slightly different task, so the augmented
# model converges later. A 15-epoch budget measured the epoch budget rather
# than the augmentation: the augmented runs finished at 0.51 *training*
# accuracy, still underfit, and lost by 0.16-0.20 everywhere.
EPOCHS = 40
BATCH = 64
# keras' RandomRotation factor is in turns, so 0.15 is +/-54 degrees -- far
# past anything a photograph of a shirt would show. These are turns too.
STRENGTHS = {"none": 0.0, "light": 0.03, "medium": 0.08, "heavy": 0.20}
# The size used for the per-epoch and strength panels; the middle of SIZES.
SWEEP_SIZE = SIZES[len(SIZES) // 2]


def _augmenter(strength: float):
    keras = tf().keras
    if not strength:
        return None
    return keras.Sequential([
        keras.layers.RandomFlip("horizontal"),
        keras.layers.RandomRotation(strength),
        keras.layers.RandomZoom(strength),
        keras.layers.RandomTranslation(strength, strength),
    ], name="augment")


@functools.lru_cache(maxsize=1)
def _samples() -> dict:
    seed_everything(0)
    data = dataset("fashion", limit=200, flat=False)
    image = data["x_train"][7]
    augment = _augmenter(STRENGTHS["medium"])
    batch = np.repeat(image[None, ...], 8, axis=0)
    augmented = augment(batch, training=True).numpy()
    return {"original": image, "augmented": augmented}


def augmented_samples(fig, axes, p: Palette) -> None:
    info = _samples()
    grid = fig.subplots(1, 9)
    grid[0].imshow(info["original"][..., 0], cmap="gray")
    grid[0].set_title("original", fontsize=8.5)
    for index, ax in enumerate(grid[1:]):
        ax.imshow(np.clip(info["augmented"][index][..., 0], 0, 1),
                  cmap="gray")
        ax.set_title(f"#{index + 1}", fontsize=8.5)
    for ax in grid:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def _model(strength: float, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((28, 28, 1))]
    augment = _augmenter(strength)
    if augment is not None:
        layers.append(augment)
    for filters in (32, 64):
        layers += [keras.layers.Conv2D(filters, 3, padding="same",
                                       activation="relu"),
                   keras.layers.MaxPooling2D(2)]
    layers += [keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
               keras.layers.GlobalAveragePooling2D(),
               keras.layers.Dense(64, activation="relu"),
               keras.layers.Dense(10, activation="softmax")]
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def _fit(strength: float, size: int) -> dict:
    data = dataset("fashion", limit=8000, flat=False)
    model = _model(strength)
    history = model.fit(data["x_train"][:size], data["y_train"][:size],
                        epochs=EPOCHS, batch_size=BATCH, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "accuracy": [float(v) for v in history.history["accuracy"]]}


@functools.lru_cache(maxsize=1)
def _size_runs() -> dict:
    out = {}
    for size in SIZES:
        for label in ("none", "medium"):
            out[(label, size)] = _fit(STRENGTHS[label], size)
    return out


@functools.lru_cache(maxsize=1)
def _strength_runs() -> dict:
    return {label: _fit(strength, SWEEP_SIZE)
            for label, strength in STRENGTHS.items()}


def augmentation_effect(fig, axes, p: Palette) -> None:
    runs = _size_runs()
    left, right = fig.subplots(1, 2)
    plain = [max(runs[("none", s)]["val_accuracy"]) for s in SIZES]
    augmented = [max(runs[("medium", s)]["val_accuracy"]) for s in SIZES]
    left.plot(SIZES, plain, "o-", ms=6, lw=2.0, color=p.red,
              label="no augmentation")
    left.plot(SIZES, augmented, "o-", ms=6, lw=2.0, color=p.green,
              label="medium augmentation")
    for size, a, b in zip(SIZES, plain, augmented):
        left.annotate(f"{b - a:+.4f}", (size, b), textcoords="offset points",
                      xytext=(0, 8), ha="center", fontsize=8, color=p.green)
    left.set_xscale("log")
    left.set_xticks(list(SIZES))
    left.set_xticklabels([f"{s:,}" for s in SIZES])
    left.set_xlabel("training rows")
    left.set_ylabel("best validation accuracy")
    left.set_title("the gain shrinks as data grows", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    epochs = range(1, EPOCHS + 1)
    for label, color in (("none", p.red), ("medium", p.green)):
        run = runs[(label, SWEEP_SIZE)]
        right.plot(epochs, run["accuracy"], lw=1.4, ls="--", color=color)
        right.plot(epochs, run["val_accuracy"], lw=2.0, color=color,
                   label=f"{label} — gap "
                         f"{run['accuracy'][-1] - run['val_accuracy'][-1]:+.4f}")
    right.set_xlabel("epoch")
    right.set_ylabel("accuracy")
    right.set_title(f"{SWEEP_SIZE:,} rows: dashed = train, solid = validation",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def augmentation_strength(fig, axes, p: Palette) -> None:
    runs = _strength_runs()
    ax = fig.subplots(1, 1)
    labels = list(runs)
    best = [max(runs[k]["val_accuracy"]) for k in labels]
    train = [runs[k]["accuracy"][-1] for k in labels]
    positions = np.arange(len(labels))
    winner = max(best)
    ax.bar(positions - 0.2, train, 0.38, color=p.muted,
           label="final training accuracy")
    ax.bar(positions + 0.2, best, 0.38,
           color=[p.green if abs(b - winner) < 1e-9 else p.blue for b in best],
           label="best validation accuracy")
    for x, value in zip(positions + 0.2, best):
        ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    for x, value in zip(positions - 0.2, train):
        ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8, color=p.muted)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{k}\n({STRENGTHS[k]:g})" for k in labels],
                       fontsize=8.5)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("accuracy")
    ax.set_title(f"{SWEEP_SIZE:,} Fashion-MNIST rows, {EPOCHS} epochs, "
                 f"{len(STRENGTHS)} strengths", fontsize=10.5)
    ax.legend(fontsize=8, loc="upper right")


@functools.lru_cache(maxsize=1)
def _robustness() -> dict:
    """Score each strength on a canonical test set and on shifted/rotated ones.

    Fashion-MNIST is centred and pose-normalised, so augmentation only costs
    accuracy on the canonical test set. The question this answers is what it
    buys: performance when the test data is *not* in the canonical pose.
    """
    keras = tf().keras
    data = dataset("fashion", limit=8000, flat=False)
    x_test, y_test = data["x_test"], data["y_test"]
    perturbations = {"canonical": None,
                     "shifted 15%": keras.layers.RandomTranslation(0.15, 0.15),
                     "rotated 10%": keras.layers.RandomRotation(0.10)}
    variants = {}
    for label, layer in perturbations.items():
        if layer is None:
            variants[label] = x_test
        else:
            seed_everything(1)
            variants[label] = layer(x_test, training=True).numpy()
    out = {}
    for label, strength in STRENGTHS.items():
        model = _model(strength)
        model.fit(data["x_train"][:SWEEP_SIZE], data["y_train"][:SWEEP_SIZE],
                  epochs=EPOCHS, batch_size=BATCH, verbose=0)
        for name, x in variants.items():
            out[(label, name)] = float(
                model.evaluate(x, y_test, verbose=0)[1])
    return out


def augmentation_robustness(fig, axes, p: Palette) -> None:
    runs = _robustness()
    ax = fig.subplots(1, 1)
    conditions = ("canonical", "shifted 15%", "rotated 10%")
    labels = list(STRENGTHS)
    positions = np.arange(len(conditions))
    width = 0.8 / len(labels)
    colors = dict(zip(labels, (p.red, p.blue, p.green, p.purple)))
    for index, label in enumerate(labels):
        offset = (index - (len(labels) - 1) / 2) * width
        values = [runs[(label, condition)] for condition in conditions]
        ax.bar(positions + offset, values, width * 0.92, color=colors[label],
               label=f"{label} ({STRENGTHS[label]:g})")
        for x, value in zip(positions + offset, values):
            ax.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                        xytext=(0, 3), ha="center", fontsize=6.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(conditions)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("test accuracy")
    ax.set_title(f"{SWEEP_SIZE:,} rows, {EPOCHS} epochs — the same models on a "
                 f"canonical and a perturbed test set", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper right", ncol=2)


FIGURES = [
    figure("augmented-samples", augmented_samples, size=(9.6, 1.9), axes=False),
    figure("augmentation-robustness", augmentation_robustness, size=(8.4, 3.8),
           axes=False),
    figure("augmentation-effect", augmentation_effect, size=(9.4, 3.6),
           axes=False),
    figure("augmentation-strength", augmentation_strength, size=(7.8, 3.8),
           axes=False),
]


if __name__ == "__main__":
    info = _samples()
    original, augmented = info["original"], info["augmented"]
    print("=== what augmentation does to one image ===")
    print(f"original mean {original.mean():.4f}  std {original.std():.4f}")
    differences = [float(np.abs(a - original).mean()) for a in augmented]
    print(f"mean absolute pixel change across 8 draws: "
          f"min {min(differences):.4f}  max {max(differences):.4f}")
    print(f"none of the 8 draws is identical to the original: "
          f"{all(d > 1e-6 for d in differences)}")

    print(f"\n=== augmentation against training-set size, {EPOCHS} epochs ===")
    runs = _size_runs()
    print(f"{'rows':>7} {'no aug':>9} {'medium aug':>12} {'gain':>8} "
          f"{'train gap (no aug)':>19} {'train gap (aug)':>16}")
    for size in SIZES:
        plain = runs[("none", size)]
        aug = runs[("medium", size)]
        best_plain, best_aug = max(plain["val_accuracy"]), max(aug["val_accuracy"])
        print(f"{size:7d} {best_plain:9.4f} {best_aug:12.4f} "
              f"{best_aug - best_plain:+8.4f} "
              f"{plain['accuracy'][-1] - plain['val_accuracy'][-1]:19.4f} "
              f"{aug['accuracy'][-1] - aug['val_accuracy'][-1]:16.4f}")

    print(f"\n=== when each run reaches its own best, {EPOCHS} epochs ===")
    print(f"{'rows':>7} {'setup':10s} {'best epoch':>11} "
          f"{'acc at epoch 15':>16} {'best acc':>9}")
    for size in SIZES:
        for label in ("none", "medium"):
            curve = runs[(label, size)]["val_accuracy"]
            print(f"{size:7d} {label:10s} {curve.index(max(curve)) + 1:11d} "
                  f"{curve[14]:16.4f} {max(curve):9.4f}")
    print("a 15-epoch budget measures the budget, not the augmentation: the")
    print("augmented run is still climbing when the plain one has stopped")

    print(f"\n=== canonical against perturbed test sets, {SWEEP_SIZE:,} rows ===")
    robustness = _robustness()
    conditions = ("canonical", "shifted 15%", "rotated 10%")
    print(f"{'strength':10s} " + " ".join(f"{c:>13}" for c in conditions)
          + f" {'shift cost':>11}")
    for label in STRENGTHS:
        values = [robustness[(label, condition)] for condition in conditions]
        print(f"{label:10s} " + " ".join(f"{v:13.4f}" for v in values)
              + f" {values[0] - values[1]:11.4f}")
    print("augmentation trades canonical accuracy for accuracy on data that is")
    print("not in the canonical pose; whether that is a good trade depends")
    print("entirely on what the deployment data looks like")

    print(f"\n=== strength sweep on {SWEEP_SIZE:,} rows ===")
    print(f"{'strength':10s} {'value':>7} {'best val acc':>13} "
          f"{'final train acc':>16}")
    for label, run in _strength_runs().items():
        print(f"{label:10s} {STRENGTHS[label]:7g} "
              f"{max(run['val_accuracy']):13.4f} {run['accuracy'][-1]:16.4f}")

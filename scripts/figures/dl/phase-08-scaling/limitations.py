"""Figures for *Limitations and the Future of Deep Learning*.

A closing chapter about what deep learning cannot do is usually an essay. It
does not have to be: each of the classic limitations is a claim about a model's
behaviour, and every one of them can be measured on the model this module
trains.

``shift``
    Accuracy under transformations a human would not notice -- rotation, shift,
    a change of contrast -- against the model's confidence on the same inputs.

``fragility``
    The smallest pixel perturbation that flips a prediction, found by gradient
    ascent on the loss.

``data-hunger``
    The learning curve against training-set size, extrapolated to ask what
    reaching human accuracy would cost.
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
EPOCHS = 8
EVAL = 2000
SIZES = (250, 500, 1000, 2000, 4000, 8000, 12000)
ANGLES = (0, 5, 10, 15, 30, 45)
SHIFTS = (0, 1, 2, 3, 4, 6)
EPSILONS = (0.0, 0.01, 0.03, 0.05, 0.1, 0.2)
ATTACK_SAMPLES = 200


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


def _build(keras):
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(32, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(64, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(10),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _model() -> dict:
    keras = tf().keras
    data = _data()
    model = _build(keras)
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "parameters": int(model.count_params()),
            "seconds": time.perf_counter() - started}


def _score(model, images, labels) -> dict:
    tensorflow = tf()
    logits = model.predict(images, verbose=0, batch_size=512)
    probabilities = tensorflow.nn.softmax(logits).numpy()
    predicted = probabilities.argmax(axis=1)
    return {"accuracy": float((predicted == labels).mean()),
            "confidence": float(probabilities.max(axis=1).mean()),
            "predicted": predicted}


def _rotate(images, degrees: float):
    """Rotate about the centre with nearest-neighbour sampling."""
    if degrees == 0:
        return images
    radians = np.deg2rad(degrees)
    size = images.shape[1]
    centre = (size - 1) / 2.0
    rows, columns = np.meshgrid(np.arange(size), np.arange(size),
                                indexing="ij")
    y = rows - centre
    x = columns - centre
    source_y = np.cos(radians) * y + np.sin(radians) * x + centre
    source_x = -np.sin(radians) * y + np.cos(radians) * x + centre
    source_y = np.clip(np.round(source_y).astype(int), 0, size - 1)
    source_x = np.clip(np.round(source_x).astype(int), 0, size - 1)
    return images[:, source_y, source_x, :]


def _shift(images, pixels: int):
    if pixels == 0:
        return images
    return np.roll(images, shift=(pixels, pixels), axis=(1, 2))


@functools.lru_cache(maxsize=1)
def _shift_runs() -> dict:
    data = _data()
    model = _model()["model"]
    images = data["x_test"][:EVAL]
    labels = data["y_test"][:EVAL]
    rotations = {angle: _score(model, _rotate(images, angle), labels)
                 for angle in ANGLES}
    translations = {pixels: _score(model, _shift(images, pixels), labels)
                    for pixels in SHIFTS}
    contrast = {}
    for factor in (1.0, 0.75, 0.5, 0.25):
        contrast[factor] = _score(model, np.clip(images * factor, 0, 1), labels)
    inverted = _score(model, 1.0 - images, labels)
    return {"rotations": rotations, "shifts": translations,
            "contrast": contrast, "inverted": inverted}


@functools.lru_cache(maxsize=1)
def _attack() -> dict:
    """Fast gradient sign: one step of gradient ASCENT on the loss."""
    tensorflow = tf()
    keras = tf().keras
    data = _data()
    model = _model()["model"]
    images = data["x_test"][:ATTACK_SAMPLES].astype("float32")
    labels = data["y_test"][:ATTACK_SAMPLES]
    loss_function = keras.losses.SparseCategoricalCrossentropy(
        from_logits=True)

    tensor = tensorflow.convert_to_tensor(images)
    with tensorflow.GradientTape() as tape:
        tape.watch(tensor)
        loss = loss_function(labels, model(tensor, training=False))
    direction = np.sign(tape.gradient(loss, tensor).numpy())

    out = {}
    for epsilon in EPSILONS:
        attacked = np.clip(images + epsilon * direction, 0, 1)
        scored = _score(model, attacked, labels)
        out[epsilon] = {**scored,
                        "mean_change": float(np.abs(attacked - images).mean()),
                        "example": attacked[0]}
    # For comparison: random noise of the same magnitude.
    rng = np.random.default_rng(0)
    random_direction = np.sign(rng.normal(0, 1, images.shape))
    random_scores = {}
    for epsilon in EPSILONS:
        noisy = np.clip(images + epsilon * random_direction, 0, 1)
        random_scores[epsilon] = _score(model, noisy, labels)
    return {"attack": out, "random": random_scores,
            "clean": images[0], "labels": labels}


@functools.lru_cache(maxsize=1)
def _data_hunger() -> dict:
    keras = tf().keras
    data = _data()
    out = {}
    for size in SIZES:
        model = _build(keras)
        model.fit(data["x_train"][:size], data["y_train"][:size],
                  epochs=EPOCHS, batch_size=128, verbose=0)
        scored = _score(model, data["x_test"][:EVAL], data["y_test"][:EVAL])
        out[size] = scored["accuracy"]
    # Fit error = a * n^(-b), the usual power law, in log space.
    sizes = np.array(SIZES, dtype="float64")
    errors = np.array([1.0 - out[size] for size in SIZES])
    slope, intercept = np.polyfit(np.log(sizes), np.log(errors), 1)
    def predict_size(target_error):
        return float(np.exp((np.log(target_error) - intercept) / slope))
    return {"accuracy": out, "slope": float(slope),
            "intercept": float(intercept),
            "for_99": predict_size(0.01),
            "for_995": predict_size(0.005)}


def shift(fig, axes, p: Palette) -> None:
    runs = _shift_runs()
    baseline = runs["rotations"][0]["accuracy"]
    left, right = fig.subplots(1, 2)
    angles = list(runs["rotations"])
    accuracies = [runs["rotations"][a]["accuracy"] for a in angles]
    confidences = [runs["rotations"][a]["confidence"] for a in angles]
    left.plot(angles, accuracies, "o-", ms=6, lw=2.0, color=p.blue,
              label="accuracy")
    left.plot(angles, confidences, "s--", ms=5, lw=1.8, color=p.amber,
              label="mean confidence")
    for angle, value in zip(angles, accuracies):
        left.annotate(f"{value:.3f}", (angle, value), xytext=(0, -14),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.blue)
    left.set_xlabel("rotation (degrees)")
    left.set_ylabel("on 2,000 held-out digits")
    left.set_ylim(0, 1.1)
    left.set_title(f"a {baseline:.4f} model, rotated", fontsize=10)
    left.legend(fontsize=8, loc="lower left")

    pixels = list(runs["shifts"])
    shifted = [runs["shifts"][s]["accuracy"] for s in pixels]
    right.plot(pixels, shifted, "o-", ms=6, lw=2.0, color=p.green,
               label="shifted diagonally")
    contrast_levels = list(runs["contrast"])
    right.plot([0, 1, 2, 3],
               [runs["contrast"][c]["accuracy"] for c in contrast_levels],
               "^--", ms=6, lw=1.8, color=p.purple,
               label="contrast 1.0, 0.75, 0.5, 0.25")
    right.axhline(runs["inverted"]["accuracy"], color=p.red, lw=1.4, ls=":",
                  label=f"inverted ({runs['inverted']['accuracy']:.4f})")
    for pixel, value in zip(pixels, shifted):
        right.annotate(f"{value:.3f}", (pixel, value), xytext=(0, 8),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.green)
    right.set_xlabel("pixels shifted / contrast step")
    right.set_ylabel("accuracy")
    right.set_ylim(0, 1.1)
    right.set_title("transformations a human would not notice", fontsize=10)
    right.legend(fontsize=7.5, loc="lower left")


def fragility(fig, axes, p: Palette) -> None:
    info = _attack()
    left, right = fig.subplots(1, 2, width_ratios=(1.1, 1.0))
    epsilons = list(info["attack"])
    attacked = [info["attack"][e]["accuracy"] for e in epsilons]
    random = [info["random"][e]["accuracy"] for e in epsilons]
    confidence = [info["attack"][e]["confidence"] for e in epsilons]
    left.plot(epsilons, attacked, "o-", ms=6, lw=2.0, color=p.red,
              label="adversarial direction")
    left.plot(epsilons, random, "s-", ms=6, lw=2.0, color=p.muted,
              label="random noise, same size")
    left.plot(epsilons, confidence, "^--", ms=5, lw=1.6, color=p.amber,
              label="confidence under attack")
    for epsilon, value in zip(epsilons, attacked):
        left.annotate(f"{value:.3f}", (epsilon, value), xytext=(0, -14),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.red)
    left.set_xlabel("perturbation size (fraction of the pixel range)")
    left.set_ylabel(f"accuracy on {ATTACK_SAMPLES} digits")
    left.set_ylim(0, 1.1)
    left.set_title("the same budget, spent two ways", fontsize=10)
    left.legend(fontsize=7.5, loc="center right")

    worst = epsilons[int(np.argmin(attacked))]
    strip = np.concatenate([
        info["clean"][:, :, 0],
        info["attack"][worst]["example"][:, :, 0],
        np.abs(info["attack"][worst]["example"] - info["clean"])[:, :, 0] * 5,
    ], axis=1)
    right.imshow(strip, cmap="gray")
    right.set_title(f"clean | attacked (eps={worst:g}) | difference x5",
                    fontsize=9.5)
    right.set_xticks([])
    right.set_yticks([])
    right.grid(False)


def data_hunger(fig, axes, p: Palette) -> None:
    info = _data_hunger()
    sizes = list(info["accuracy"])
    accuracies = [info["accuracy"][size] for size in sizes]
    errors = [1.0 - value for value in accuracies]
    left, right = fig.subplots(1, 2)
    left.plot(sizes, accuracies, "o-", ms=6, lw=2.0, color=p.blue)
    for size, value in zip(sizes, accuracies):
        left.annotate(f"{value:.3f}", (size, value), xytext=(0, 8),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.blue)
    left.set_xscale("log")
    left.set_xlabel("training examples (log)")
    left.set_ylabel(f"accuracy on {EVAL:,} held-out digits")
    left.set_ylim(0, 1.05)
    left.set_title(f"{EPOCHS} epochs at every size", fontsize=10)

    right.plot(sizes, errors, "o", ms=7, color=p.red, label="measured error")
    fitted = np.exp(info["intercept"]) * np.array(sizes, "float64") ** info["slope"]
    right.plot(sizes, fitted, lw=1.8, ls="--", color=p.muted,
               label=f"power law, exponent {info['slope']:.3f}")
    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("training examples (log)")
    right.set_ylabel("error rate (log)")
    right.set_title("a straight line on log-log is a power law", fontsize=10)
    right.legend(fontsize=8, loc="lower left")


FIGURES = [
    figure("shift", shift, size=(9.6, 3.5), axes=False),
    figure("fragility", fragility, size=(9.6, 3.5), axes=False),
    figure("data-hunger", data_hunger, size=(9.4, 3.4), axes=False),
]


if __name__ == "__main__":
    info = _model()
    print("=== the model whose limits are being measured ===")
    print(f"{info['parameters']:,} parameters, {EPOCHS} epochs, "
          f"{info['seconds']:.0f}s, test accuracy {info['accuracy']:.4f}")

    runs = _shift_runs()
    baseline = runs["rotations"][0]["accuracy"]
    print(f"\n=== transformations a human would shrug at ===")
    print(f"{'rotation':>10} {'accuracy':>9} {'confidence':>11} {'drop':>8}")
    for angle, entry in runs["rotations"].items():
        # "deg" rather than the degree sign: this log is redirected to a file
        # and the console encoding mangles non-ASCII on the way through.
        print(f"{angle:7d}deg {entry['accuracy']:9.4f} "
              f"{entry['confidence']:11.4f} "
              f"{entry['accuracy'] - baseline:+8.4f}")
    print(f"\n{'shift':>10} {'accuracy':>9} {'confidence':>11} {'drop':>8}")
    for pixels, entry in runs["shifts"].items():
        print(f"{pixels:8d}px {entry['accuracy']:9.4f} "
              f"{entry['confidence']:11.4f} "
              f"{entry['accuracy'] - baseline:+8.4f}")
    print(f"\n{'contrast':>10} {'accuracy':>9} {'confidence':>11}")
    for factor, entry in runs["contrast"].items():
        print(f"{factor:10.2f} {entry['accuracy']:9.4f} "
              f"{entry['confidence']:11.4f}")
    print(f"{'inverted':>10} {runs['inverted']['accuracy']:9.4f} "
          f"{runs['inverted']['confidence']:11.4f}")
    print("a convolution is translation-equivariant, not rotation-invariant,")
    print("and nothing in the architecture knows that brightness is not")
    print("semantic -- those facts have to arrive through the training data")

    attack = _attack()
    print(f"\n=== one gradient step, {ATTACK_SAMPLES} digits ===")
    print(f"{'epsilon':>8} {'adversarial':>12} {'random noise':>13} "
          f"{'confidence':>11} {'mean change':>12}")
    for epsilon in EPSILONS:
        entry = attack["attack"][epsilon]
        print(f"{epsilon:8.2f} {entry['accuracy']:12.4f} "
              f"{attack['random'][epsilon]['accuracy']:13.4f} "
              f"{entry['confidence']:11.4f} {entry['mean_change']:12.4f}")
    print("the same perturbation budget destroys the model when aimed along")
    print("the loss gradient and barely registers when spent at random --")
    print("which is what makes this a property of the model, not of noise")

    hunger = _data_hunger()
    print(f"\n=== what accuracy costs in examples ===")
    print(f"{'examples':>10} {'accuracy':>9} {'error':>8}")
    for size, accuracy in hunger["accuracy"].items():
        print(f"{size:10,} {accuracy:9.4f} {1 - accuracy:8.4f}")
    print(f"error follows a power law with exponent {hunger['slope']:.3f}")
    print(f"extrapolating: 99% accuracy needs about "
          f"{hunger['for_99']:,.0f} examples, 99.5% about "
          f"{hunger['for_995']:,.0f}")
    print("that extrapolation is the point: every additional nine costs")
    print("roughly an order of magnitude more data, which is the shape of the")
    print("problem rather than a fact about MNIST")

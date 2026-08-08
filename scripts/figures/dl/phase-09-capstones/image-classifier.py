"""Figures for *Capstone 1: An Image Classifier, End to End*.

The capstone is the whole module applied to one problem: start with a baseline
that needs no learning, add capacity until it stops helping, regularise, then
ship the result. Every rung of that ladder is measured on the same held-out
split so the gaps are attributable.

Fashion-MNIST rather than MNIST, deliberately: MNIST is easy enough that a
linear model reaches 0.92 and the later rungs have nothing left to show.

``ladder``
    Every model from a constant predictor to an augmented convnet, on one axis.

``robustness``
    What augmentation actually bought, tested on shifted and rotated versions
    of the test set rather than on the clean one.

``deployment``
    The chosen model through pruning and TFLite conversion: size, accuracy and
    single-sample latency at each step.
"""

from __future__ import annotations

import functools
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 12000
EPOCHS = 12
AUGMENT_EPOCHS = 24        # augmentation needs a longer budget to pay off
EVAL = 3000
SPARSITY = 0.6
LATENCY_SAMPLES = 200
CLASSES = ("t-shirt", "trouser", "pullover", "dress", "coat",
           "sandal", "shirt", "sneaker", "bag", "boot")


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("fashion", limit=LIMIT, flat=False)


def _evaluate(predictions, labels) -> float:
    return float((predictions == labels).mean())


@functools.lru_cache(maxsize=1)
def _baselines() -> dict:
    """Two models that involve no gradient descent at all."""
    data = _data()
    train = data["x_train"].reshape(len(data["x_train"]), -1)
    test = data["x_test"][:EVAL].reshape(-1, 784)
    labels = data["y_test"][:EVAL]

    majority = int(np.bincount(data["y_train"]).argmax())
    constant = _evaluate(np.full(len(labels), majority), labels)

    centroids = np.stack([train[data["y_train"] == index].mean(axis=0)
                          for index in range(10)])
    distances = ((test[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    centroid = _evaluate(distances.argmin(axis=1), labels)
    return {"always predict the most common class": constant,
            "nearest class centroid": centroid,
            "majority_class": majority}


def _train(kind: str, epochs: int = None, augment: bool = False) -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(0)
    epochs = EPOCHS if epochs is None else epochs
    layers = [keras.layers.Input((28, 28, 1))]
    if augment:
        layers += [keras.layers.RandomTranslation(0.08, 0.08),
                   keras.layers.RandomRotation(0.03),
                   keras.layers.RandomZoom(0.08)]
    if kind == "linear":
        layers += [keras.layers.Flatten()]
    elif kind == "mlp":
        layers += [keras.layers.Flatten(),
                   keras.layers.Dense(128, activation="relu"),
                   keras.layers.Dense(64, activation="relu")]
    else:
        layers += [keras.layers.Conv2D(32, 3, activation="relu"),
                   keras.layers.MaxPooling2D(),
                   keras.layers.Conv2D(64, 3, activation="relu"),
                   keras.layers.MaxPooling2D(),
                   keras.layers.Flatten(),
                   keras.layers.Dense(128, activation="relu"),
                   keras.layers.Dropout(0.3)]
    layers.append(keras.layers.Dense(10, activation="softmax"))
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=epochs,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"][:EVAL],
                                         data["y_test"][:EVAL]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "train_accuracy": float(history.history["accuracy"][-1]),
            "parameters": int(model.count_params()),
            "epochs": epochs,
            "seconds": time.perf_counter() - started,
            "curve": [float(v) for v in history.history["val_accuracy"]]}


@functools.lru_cache(maxsize=8)
def _model(kind: str, augment: bool = False) -> dict:
    return _train(kind, AUGMENT_EPOCHS if augment else EPOCHS, augment)


@functools.lru_cache(maxsize=1)
def _ladder() -> dict:
    baselines = _baselines()
    out = {
        "constant": {"accuracy": baselines["always predict the most common class"],
                     "parameters": 0, "seconds": 0.0},
        "centroid": {"accuracy": baselines["nearest class centroid"],
                     "parameters": 7840, "seconds": 0.0},
    }
    for label, kind, augment in (("linear", "linear", False),
                                 ("MLP", "mlp", False),
                                 ("convnet", "convnet", False),
                                 ("convnet + augmentation", "convnet", True)):
        info = _model(kind, augment)
        out[label] = {"accuracy": info["accuracy"],
                      "train_accuracy": info["train_accuracy"],
                      "parameters": info["parameters"],
                      "seconds": info["seconds"],
                      "epochs": info["epochs"]}
    return out


def _shift(images, pixels: int):
    return np.roll(images, shift=(pixels, pixels), axis=(1, 2))


def _rotate(images, degrees: float):
    if degrees == 0:
        return images
    radians = np.deg2rad(degrees)
    size = images.shape[1]
    centre = (size - 1) / 2.0
    rows, columns = np.meshgrid(np.arange(size), np.arange(size),
                                indexing="ij")
    y = rows - centre
    x = columns - centre
    source_y = np.clip(np.round(np.cos(radians) * y + np.sin(radians) * x
                                + centre).astype(int), 0, size - 1)
    source_x = np.clip(np.round(-np.sin(radians) * y + np.cos(radians) * x
                                + centre).astype(int), 0, size - 1)
    return images[:, source_y, source_x, :]


@functools.lru_cache(maxsize=1)
def _robustness() -> dict:
    """The two convnets on transformed test sets, not the clean one."""
    data = _data()
    labels = data["y_test"][:EVAL]
    images = data["x_test"][:EVAL]
    out = {}
    for label, augment in (("convnet", False), ("convnet + augmentation", True)):
        model = _model("convnet", augment)["model"]
        scores = {"clean": _evaluate(
            model.predict(images, verbose=0, batch_size=512).argmax(axis=1),
            labels)}
        for pixels in (1, 2, 3):
            scores[f"shift {pixels}px"] = _evaluate(
                model.predict(_shift(images, pixels), verbose=0,
                              batch_size=512).argmax(axis=1), labels)
        for degrees in (10, 20):
            scores[f"rotate {degrees}"] = _evaluate(
                model.predict(_rotate(images, degrees), verbose=0,
                              batch_size=512).argmax(axis=1), labels)
        out[label] = scores
    return out


def _prune(model, sparsity: float):
    keras = tf().keras
    clone = keras.models.clone_model(model)
    clone.set_weights([w.copy() for w in model.get_weights()])
    weights = []
    for array in clone.get_weights():
        if array.ndim < 2:
            weights.append(array)
            continue
        threshold = np.quantile(np.abs(array), sparsity)
        weights.append(np.where(np.abs(array) < threshold, 0.0, array))
    clone.set_weights(weights)
    return clone


@functools.lru_cache(maxsize=1)
def _deployment() -> dict:
    """The chosen model, pruned then converted, measured at every step."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    images = data["x_test"][:EVAL]
    labels = data["y_test"][:EVAL]
    chosen = _model("convnet", True)
    model = chosen["model"]

    def keras_bytes(target):
        handle = tempfile.NamedTemporaryFile(suffix=".keras", delete=False)
        handle.close()
        target.save(handle.name)
        size = os.path.getsize(handle.name)
        os.unlink(handle.name)
        return size

    def keras_latency(target):
        started = time.perf_counter()
        target.predict(images[:LATENCY_SAMPLES], batch_size=1, verbose=0)
        return (time.perf_counter() - started) / LATENCY_SAMPLES * 1000.0

    out = {"trained (Keras)": {
        "accuracy": chosen["accuracy"],
        "bytes": keras_bytes(model),
        "milliseconds": keras_latency(model),
    }}

    pruned = _prune(model, SPARSITY)
    pruned.compile(keras.optimizers.Adam(1e-4),
                   "sparse_categorical_crossentropy", metrics=["accuracy"])
    masks = [(np.abs(w) > 0).astype("float32") if w.ndim >= 2 else None
             for w in pruned.get_weights()]
    immediate = float(pruned.evaluate(images, labels, verbose=0)[1])
    for _ in range(3):
        pruned.fit(data["x_train"], data["y_train"], epochs=1, batch_size=128,
                   verbose=0)
        pruned.set_weights([w * m if m is not None else w
                            for w, m in zip(pruned.get_weights(), masks)])
    out[f"pruned {SPARSITY:.0%}"] = {
        "accuracy": float(pruned.evaluate(images, labels, verbose=0)[1]),
        "immediate": immediate,
        "bytes": keras_bytes(pruned),
        "milliseconds": keras_latency(pruned),
        "sparsity": float(np.mean([(w == 0).mean()
                                   for w in pruned.get_weights()
                                   if w.ndim >= 2])),
    }

    for label, target, quantise in (("TFLite float32", model, False),
                                    ("TFLite int8", pruned, True)):
        converter = tensorflow.lite.TFLiteConverter.from_keras_model(target)
        if quantise:
            converter.optimizations = [tensorflow.lite.Optimize.DEFAULT]
        blob = converter.convert()
        interpreter = tensorflow.lite.Interpreter(model_content=blob)
        interpreter.allocate_tensors()
        inp = interpreter.get_input_details()[0]
        outp = interpreter.get_output_details()[0]
        predictions = []
        started = time.perf_counter()
        for image in images[:LATENCY_SAMPLES]:
            interpreter.set_tensor(inp["index"], image[None, ...])
            interpreter.invoke()
            predictions.append(
                int(np.argmax(interpreter.get_tensor(outp["index"])[0])))
        milliseconds = (time.perf_counter() - started) / LATENCY_SAMPLES * 1000
        full = []
        for image in images:
            interpreter.set_tensor(inp["index"], image[None, ...])
            interpreter.invoke()
            full.append(int(np.argmax(interpreter.get_tensor(outp["index"])[0])))
        out[label] = {"accuracy": _evaluate(np.array(full), labels),
                      "bytes": len(blob), "milliseconds": milliseconds}
    return out


def ladder(fig, axes, p: Palette) -> None:
    runs = _ladder()
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    labels = list(runs)
    positions = np.arange(len(labels))
    accuracies = [runs[label]["accuracy"] for label in labels]
    colours = [p.muted, p.muted, p.blue, p.blue, p.green, p.amber]
    left.barh(positions, accuracies, 0.55, color=colours)
    previous = None
    for y, label in zip(positions, labels):
        value = runs[label]["accuracy"]
        gain = "" if previous is None else f"  ({value - previous:+.4f})"
        left.annotate(f"{value:.4f}{gain}", (value, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
        previous = value
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xlim(0, 1.28)
    left.set_xlabel(f"accuracy on {EVAL:,} held-out garments")
    left.set_title("each rung against the one below it", fontsize=10)

    trained = [label for label in labels if "parameters" in runs[label]
               and runs[label]["parameters"] > 0]
    sizes = [runs[label]["parameters"] for label in trained]
    scores = [runs[label]["accuracy"] for label in trained]
    right.scatter(sizes, scores, s=90, color=p.blue)
    for label, size, score in zip(trained, sizes, scores):
        right.annotate(label, (size, score), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    right.set_xscale("log")
    right.set_xlabel("parameters (log)")
    right.set_ylabel("accuracy")
    right.set_title("capacity is not the whole story", fontsize=10)


def robustness(fig, axes, p: Palette) -> None:
    runs = _robustness()
    conditions = list(runs["convnet"])
    positions = np.arange(len(conditions))
    width = 0.38
    for index, (label, colour) in enumerate((("convnet", p.blue),
                                             ("convnet + augmentation",
                                              p.green))):
        values = [runs[label][condition] for condition in conditions]
        axes.bar(positions + (index - 0.5) * width, values, width * 0.9,
                 color=colour, label=label)
        for x, value in zip(positions + (index - 0.5) * width, values):
            axes.annotate(f"{value:.3f}", (x, value), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=6.5, color=p.fg)
    axes.set_xticks(positions)
    axes.set_xticklabels(conditions, fontsize=8, rotation=15, ha="right")
    axes.set_ylim(0, 1.15)
    axes.set_ylabel(f"accuracy on {EVAL:,} garments")
    axes.set_title("augmentation is bought on the transformed test sets, "
                   "not the clean one", fontsize=10)
    axes.legend(fontsize=8, loc="lower left")


def deployment(fig, axes, p: Palette) -> None:
    runs = _deployment()
    labels = list(runs)
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(labels))
    sizes = [runs[label]["bytes"] / 1024 for label in labels]
    baseline = sizes[0]
    left.barh(positions, sizes, 0.55, color=p.blue)
    for y, size in zip(positions, sizes):
        left.annotate(f"{size:,.0f} KB ({baseline / size:.1f}x)", (size, y),
                      xytext=(6, 0), textcoords="offset points", va="center",
                      fontsize=8, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, max(sizes) * 1.5)
    left.set_xlabel("size on disk (KB)")
    left.set_title("shipping the model", fontsize=10)

    accuracies = [runs[label]["accuracy"] for label in labels]
    times = [runs[label]["milliseconds"] for label in labels]
    right.scatter(times, accuracies, s=90, color=p.green)
    for label, time_value, accuracy in zip(labels, times, accuracies):
        right.annotate(label, (time_value, accuracy), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    right.set_xscale("log")
    right.set_xlabel("milliseconds per sample, batch of 1 (log)")
    right.set_ylabel("accuracy")
    right.set_title("what the deployment path cost", fontsize=10)


FIGURES = [
    figure("ladder", ladder, size=(9.8, 3.5), axes=False),
    figure("robustness", robustness, size=(9.2, 3.4)),
    figure("deployment", deployment, size=(9.6, 3.5), axes=False),
]


if __name__ == "__main__":
    baselines = _baselines()
    print("=== the problem ===")
    print(f"Fashion-MNIST, {LIMIT:,} training images, {EVAL:,} held out.")
    print("Ten garment classes, balanced, so the constant baseline is 1/10.")

    print(f"\n=== the ladder ===")
    runs = _ladder()
    print(f"{'model':26s} {'parameters':>12} {'epochs':>7} {'seconds':>8} "
          f"{'accuracy':>9} {'gain':>8}")
    previous = None
    for label, entry in runs.items():
        gain = "" if previous is None else f"{entry['accuracy'] - previous:+8.4f}"
        print(f"{label:26s} {entry['parameters']:12,} "
              f"{entry.get('epochs', 0):7d} {entry['seconds']:8.0f} "
              f"{entry['accuracy']:9.4f} {gain:>8}")
        previous = entry["accuracy"]
    convnet = runs["convnet"]
    print(f"the convnet's training accuracy was "
          f"{convnet.get('train_accuracy', 0):.4f} against "
          f"{convnet['accuracy']:.4f} held out -- that gap is what")
    print("augmentation is being asked to close")

    print(f"\n=== what augmentation actually bought ===")
    robust = _robustness()
    conditions = list(robust["convnet"])
    print(f"{'condition':14s} {'convnet':>9} {'augmented':>11} {'delta':>8}")
    for condition in conditions:
        plain = robust["convnet"][condition]
        augmented = robust["convnet + augmentation"][condition]
        print(f"{condition:14s} {plain:9.4f} {augmented:11.4f} "
              f"{augmented - plain:+8.4f}")
    print("the clean column is the one everyone reports; the others are where")
    print("the technique is actually spent")

    print(f"\n=== deployment ===")
    deploy = _deployment()
    print(f"{'artefact':20s} {'KB':>10} {'accuracy':>9} {'ms/sample':>11}")
    for label, entry in deploy.items():
        print(f"{label:20s} {entry['bytes'] / 1024:10,.1f} "
              f"{entry['accuracy']:9.4f} {entry['milliseconds']:11.3f}")
    pruned_key = f"pruned {SPARSITY:.0%}"
    print(f"pruning zeroed {deploy[pruned_key]['sparsity']:.1%} of the weight "
          f"matrices; accuracy went {deploy[pruned_key]['immediate']:.4f} "
          f"-> {deploy[pruned_key]['accuracy']:.4f} after fine-tuning")
    print("the .keras file does not shrink when pruned -- zeros are stored")
    print("like any other float, which is why the size win comes from TFLite")

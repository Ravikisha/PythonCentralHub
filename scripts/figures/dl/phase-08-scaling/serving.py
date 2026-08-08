"""Figures for *Serving Models with TensorFlow Serving*.

The TensorFlow Serving binary is a separate C++ server and is not installed on
this machine. What it serves, however, is an ordinary SavedModel directory, and
everything about that artefact is inspectable and measurable here: what it
contains, what its signature promises, how long a request takes, and what
happens when the preprocessing lives outside it.

``artefact``
    What a SavedModel actually contains on disk, and how its size compares with
    the Keras and TFLite formats from the other pages.

``latency``
    Request latency against batch size, through the loaded SavedModel -- the
    curve that decides whether batching requests is worth it.

``skew``
    Training/serving skew, measured: the same model served with the
    preprocessing left out, and how far the predictions move.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 8000
EPOCHS = 5
EVAL = 2000
BATCHES = (1, 2, 8, 32, 128)
REQUESTS = 60


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


@functools.lru_cache(maxsize=1)
def _model() -> dict:
    """A model that does its own preprocessing, so serving cannot get it wrong."""
    keras = tf().keras
    data = _data()
    seed_everything(0)
    inputs = keras.layers.Input((28, 28, 1), name="image")
    # The scaling lives INSIDE the model. Anything outside it has to be
    # reproduced exactly by every caller, which is where skew comes from.
    x = keras.layers.Rescaling(1.0 / 255.0)(inputs)
    x = keras.layers.Conv2D(16, 3, activation="relu")(x)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Conv2D(32, 3, activation="relu")(x)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Flatten()(x)
    x = keras.layers.Dense(64, activation="relu")(x)
    outputs = keras.layers.Dense(10, activation="softmax", name="probabilities")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    # Training data is fed in RAW units, matching what a client would send.
    history = model.fit(data["x_train"] * 255.0, data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"] * 255.0,
                                         data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "parameters": int(model.count_params())}


def _directory_report(path: str) -> dict:
    """Every file in the SavedModel, with its size."""
    entries = []
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            full = os.path.join(root, name)
            size = os.path.getsize(full)
            total += size
            entries.append({"name": os.path.relpath(full, path).replace("\\", "/"),
                            "bytes": size})
    entries.sort(key=lambda entry: entry["bytes"], reverse=True)
    return {"entries": entries, "bytes": total}


@functools.lru_cache(maxsize=1)
def _exported() -> dict:
    """Export the SavedModel and read back everything it advertises."""
    tensorflow = tf()
    model = _model()["model"]
    root = tempfile.mkdtemp(prefix="served-")
    # A version number in the path is what lets TF Serving hot-swap models.
    path = os.path.join(root, "1")
    started = time.perf_counter()
    model.export(path)
    export_seconds = time.perf_counter() - started

    report = _directory_report(path)
    loaded = tensorflow.saved_model.load(path)
    serving = loaded.signatures["serving_default"]
    inputs = {name: {"shape": [int(d) if d is not None else -1
                               for d in spec.shape],
                     "dtype": spec.dtype.name}
              for name, spec in serving.structured_input_signature[1].items()}
    outputs = {name: {"shape": [int(d) if d is not None else -1
                                for d in spec.shape],
                      "dtype": spec.dtype.name}
               for name, spec in serving.structured_outputs.items()}

    keras_handle = tempfile.NamedTemporaryFile(suffix=".keras", delete=False)
    keras_handle.close()
    model.save(keras_handle.name)
    keras_bytes = os.path.getsize(keras_handle.name)
    os.unlink(keras_handle.name)

    return {"path": path, "root": root, "report": report,
            "inputs": inputs, "outputs": outputs,
            "export_seconds": export_seconds,
            "keras_bytes": keras_bytes,
            "signatures": list(loaded.signatures)}


@functools.lru_cache(maxsize=1)
def _latency() -> dict:
    """Request latency against batch size, through the served signature."""
    tensorflow = tf()
    data = _data()
    exported = _exported()
    loaded = tensorflow.saved_model.load(exported["path"])
    serving = loaded.signatures["serving_default"]
    key = next(iter(exported["inputs"]))
    images = (data["x_test"] * 255.0).astype("float32")

    out = {}
    for size in BATCHES:
        batch = tensorflow.constant(images[:size])
        serving(**{key: batch})                  # warm-up / trace
        started = time.perf_counter()
        for _ in range(REQUESTS):
            serving(**{key: batch})
        elapsed = (time.perf_counter() - started) / REQUESTS
        out[size] = {"per_request_ms": elapsed * 1000.0,
                     "per_sample_ms": elapsed / size * 1000.0,
                     "throughput": size / elapsed}
    return out


@functools.lru_cache(maxsize=1)
def _skew() -> dict:
    """What happens when the client preprocesses differently to training."""
    tensorflow = tf()
    data = _data()
    exported = _exported()
    loaded = tensorflow.saved_model.load(exported["path"])
    serving = loaded.signatures["serving_default"]
    key = next(iter(exported["inputs"]))
    output_key = next(iter(exported["outputs"]))
    labels = data["y_test"][:EVAL]
    raw = (data["x_test"][:EVAL] * 255.0).astype("float32")

    def predict(batch):
        result = serving(**{key: tensorflow.constant(batch)})[output_key]
        return np.asarray(result)

    correct = predict(raw)
    variants = {
        "correct (raw 0-255)": raw,
        "client also divided by 255": raw / 255.0,
        "client centred to [-1, 1]": raw / 127.5 - 1.0,
        "pixels inverted (255 - x)": 255.0 - raw,
    }
    out = {}
    for label, batch in variants.items():
        probabilities = predict(batch)
        out[label] = {
            "accuracy": float((probabilities.argmax(axis=1) == labels).mean()),
            "agreement": float((probabilities.argmax(axis=1)
                                == correct.argmax(axis=1)).mean()),
            "confidence": float(probabilities.max(axis=1).mean()),
        }
    return out


def artefact(fig, axes, p: Palette) -> None:
    exported = _exported()
    left, right = fig.subplots(1, 2, width_ratios=(1.2, 1.0))
    entries = exported["report"]["entries"][:6]
    positions = np.arange(len(entries))
    sizes = [entry["bytes"] / 1024 for entry in entries]
    left.barh(positions, sizes, 0.55, color=p.blue)
    for y, entry in zip(positions, entries):
        left.annotate(f"{entry['bytes'] / 1024:,.1f} KB",
                      (entry["bytes"] / 1024, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels([entry["name"] for entry in entries], fontsize=7.5)
    left.invert_yaxis()
    left.set_xlim(0, max(sizes) * 1.45)
    left.set_xlabel("kilobytes")
    left.set_title(f"inside the SavedModel "
                   f"({exported['report']['bytes'] / 1024:,.0f} KB total)",
                   fontsize=10)

    formats = (("SavedModel", exported["report"]["bytes"] / 1024, p.blue),
               (".keras file", exported["keras_bytes"] / 1024, p.amber))
    positions = np.arange(len(formats))
    right.bar(positions, [entry[1] for entry in formats], 0.5,
              color=[entry[2] for entry in formats])
    for x, entry in zip(positions, formats):
        right.annotate(f"{entry[1]:,.0f} KB", (x, entry[1]), xytext=(0, 4),
                       textcoords="offset points", ha="center", fontsize=9,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([entry[0] for entry in formats])
    right.set_ylim(0, max(entry[1] for entry in formats) * 1.3)
    right.set_ylabel("kilobytes")
    right.set_title("the two things 'saving a model' can mean", fontsize=10)


def latency(fig, axes, p: Palette) -> None:
    runs = _latency()
    left, right = fig.subplots(1, 2)
    sizes = list(runs)
    per_request = [runs[size]["per_request_ms"] for size in sizes]
    per_sample = [runs[size]["per_sample_ms"] for size in sizes]
    left.plot(sizes, per_request, "o-", ms=7, lw=2.0, color=p.red,
              label="per request")
    left.plot(sizes, per_sample, "s-", ms=6, lw=2.0, color=p.green,
              label="per sample")
    for size, value in zip(sizes, per_sample):
        left.annotate(f"{value:.3f}", (size, value), xytext=(0, -14),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.green)
    left.set_xscale("log", base=2)
    left.set_yscale("log")
    left.set_xticks(sizes)
    left.set_xticklabels([str(size) for size in sizes])
    left.minorticks_off()
    left.set_xlabel("batch size")
    left.set_ylabel("milliseconds (log)")
    left.set_title(f"mean of {REQUESTS} requests", fontsize=10)
    left.legend(fontsize=8, loc="center left")

    throughput = [runs[size]["throughput"] for size in sizes]
    right.plot(sizes, throughput, "o-", ms=7, lw=2.0, color=p.blue)
    for size, value in zip(sizes, throughput):
        right.annotate(f"{value:,.0f}/s", (size, value), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.blue)
    right.set_xscale("log", base=2)
    right.set_xticks(sizes)
    right.set_xticklabels([str(size) for size in sizes])
    right.minorticks_off()
    right.set_xlabel("batch size")
    right.set_ylabel("samples per second")
    right.set_title("why a server batches incoming requests", fontsize=10)


def skew(fig, axes, p: Palette) -> None:
    runs = _skew()
    labels = list(runs)
    positions = np.arange(len(labels))
    width = 0.38
    accuracies = [runs[label]["accuracy"] for label in labels]
    agreements = [runs[label]["agreement"] for label in labels]
    axes.bar(positions - width / 2, accuracies, width * 0.9, color=p.blue,
             label="accuracy")
    axes.bar(positions + width / 2, agreements, width * 0.9, color=p.amber,
             label="agreement with the correct call")
    for x, value in zip(positions - width / 2, accuracies):
        axes.annotate(f"{value:.4f}", (x, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    axes.set_xticks(positions)
    axes.set_xticklabels(labels, fontsize=8, rotation=12, ha="right")
    axes.set_ylim(0, 1.2)
    axes.set_title("the same server, four client preprocessing conventions",
                   fontsize=10)
    axes.legend(fontsize=8, loc="upper right")


FIGURES = [
    figure("artefact", artefact, size=(9.8, 3.4), axes=False),
    figure("latency", latency, size=(9.4, 3.4), axes=False),
    figure("skew", skew, size=(8.8, 3.4)),
]


if __name__ == "__main__":
    info = _model()
    exported = _exported()
    print("=== the model being served ===")
    print(f"{info['parameters']:,} parameters, test accuracy "
          f"{info['accuracy']:.4f}")
    print("the rescaling layer is INSIDE the model, so a client sends raw")
    print("0-255 pixels and cannot get the preprocessing wrong")

    print(f"\n=== what export() wrote ({exported['export_seconds']:.1f}s) ===")
    print(f"{'file':44s} {'KB':>10}")
    for entry in exported["report"]["entries"]:
        print(f"{entry['name']:44s} {entry['bytes'] / 1024:10,.1f}")
    print(f"{'TOTAL':44s} {exported['report']['bytes'] / 1024:10,.1f}")
    print(f"the same model as a .keras file: "
          f"{exported['keras_bytes'] / 1024:,.1f} KB")
    print("the directory is versioned (.../1), which is what lets a server")
    print("load a new version and drain the old one without downtime")

    print(f"\n=== the serving signature ===")
    print(f"signatures available: {exported['signatures']}")
    for name, spec in exported["inputs"].items():
        print(f"  input  {name:20s} shape {spec['shape']} {spec['dtype']}")
    for name, spec in exported["outputs"].items():
        print(f"  output {name:20s} shape {spec['shape']} {spec['dtype']}")
    print("a -1 in the shape is the batch dimension: the signature accepts any")
    print("number of images per request, which is what makes batching possible")

    print(f"\n=== latency against batch size ({REQUESTS} requests each) ===")
    print(f"{'batch':>7} {'ms/request':>12} {'ms/sample':>11} "
          f"{'samples/s':>12}")
    for size, entry in _latency().items():
        print(f"{size:7d} {entry['per_request_ms']:12.3f} "
              f"{entry['per_sample_ms']:11.4f} {entry['throughput']:12,.0f}")
    single = _latency()[1]["per_sample_ms"]
    largest = _latency()[max(BATCHES)]["per_sample_ms"]
    print(f"per-sample cost falls {single / largest:.1f}x from batch 1 to "
          f"batch {max(BATCHES)} -- the fixed per-request overhead is spread")
    print("over more samples, which is exactly why servers batch")

    print(f"\n=== training/serving skew, on {EVAL:,} digits ===")
    print(f"{'client preprocessing':30s} {'accuracy':>9} {'agreement':>10} "
          f"{'confidence':>11}")
    for label, entry in _skew().items():
        print(f"{label:30s} {entry['accuracy']:9.4f} "
              f"{entry['agreement']:10.4f} {entry['confidence']:11.4f}")
    print("every one of these calls succeeds and returns confident-looking")
    print("probabilities. Nothing raises. The only signal that three of them")
    print("are wrong is that the accuracy collapsed -- which a production")
    print("server has no way to measure without labels")

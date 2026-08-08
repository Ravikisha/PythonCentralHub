"""Figures for *Deploying to Mobile & Edge with TensorFlow Lite*.

Conversion and quantisation are the two claims on this page and both are
checkable: a converted model has a size in bytes, an accuracy on the same test
set, and a latency per sample. Nothing here is estimated.

``size-and-accuracy``
    Model size against test accuracy for four conversions, with the Keras
    baseline as the reference.

``latency``
    Per-sample inference time for each conversion, measured through the TFLite
    interpreter rather than through Keras.

``disagreement``
    Where the quantised models actually differ from the float one -- which
    predictions changed, and how confident the float model was about them.
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
EPOCHS = 6
EVAL = 2000
LATENCY_SAMPLES = 300
REPRESENTATIVE = 200


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


@functools.lru_cache(maxsize=1)
def _model() -> dict:
    """A small convnet -- big enough that weight quantisation has something to do."""
    keras = tf().keras
    data = _data()
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(16, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(32, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    keras_size = _keras_bytes(model)
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "parameters": int(model.count_params()),
            "bytes": keras_size,
            "seconds": time.perf_counter() - started}


def _keras_bytes(model) -> int:
    """On-disk size of the saved Keras model, for a like-for-like comparison."""
    handle = tempfile.NamedTemporaryFile(suffix=".keras", delete=False)
    handle.close()
    model.save(handle.name)
    size = os.path.getsize(handle.name)
    os.unlink(handle.name)
    return size


def _representative():
    data = _data()
    for row in data["x_train"][:REPRESENTATIVE]:
        yield [row[None, ...].astype("float32")]


@functools.lru_cache(maxsize=1)
def _conversions() -> dict:
    """Four conversions of the same trained model."""
    tensorflow = tf()
    model = _model()["model"]
    out = {}

    def convert(label, configure):
        converter = tensorflow.lite.TFLiteConverter.from_keras_model(model)
        configure(converter)
        started = time.perf_counter()
        blob = converter.convert()
        out[label] = {"bytes": len(blob), "blob": blob,
                      "convert_seconds": time.perf_counter() - started}

    convert("float32 (no options)", lambda c: None)

    def dynamic(converter):
        converter.optimizations = [tensorflow.lite.Optimize.DEFAULT]

    convert("dynamic-range int8", dynamic)

    def float16(converter):
        converter.optimizations = [tensorflow.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tensorflow.float16]

    convert("float16 weights", float16)

    def full_int8(converter):
        converter.optimizations = [tensorflow.lite.Optimize.DEFAULT]
        converter.representative_dataset = _representative
        converter.target_spec.supported_ops = [
            tensorflow.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tensorflow.int8
        converter.inference_output_type = tensorflow.int8

    convert("full int8", full_int8)
    return out


def _run_interpreter(blob, images, measure_latency: bool = False) -> dict:
    """Score a TFLite model one sample at a time, as an edge device would."""
    tensorflow = tf()
    interpreter = tensorflow.lite.Interpreter(model_content=blob)
    interpreter.allocate_tensors()
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    scale, zero_point = input_detail["quantization"]
    predictions = []
    confidences = []
    started = time.perf_counter()
    count = LATENCY_SAMPLES if measure_latency else len(images)
    for image in images[:count]:
        row = image[None, ...].astype("float32")
        if input_detail["dtype"] == np.int8:
            # A fully quantised model takes int8 in and gives int8 out, so the
            # caller has to apply the scale and zero point itself.
            row = np.round(row / scale + zero_point).astype(np.int8)
        interpreter.set_tensor(input_detail["index"], row)
        interpreter.invoke()
        result = interpreter.get_tensor(output_detail["index"])[0]
        if output_detail["dtype"] == np.int8:
            out_scale, out_zero = output_detail["quantization"]
            result = (result.astype("float32") - out_zero) * out_scale
        predictions.append(int(np.argmax(result)))
        confidences.append(float(np.max(result)))
    elapsed = time.perf_counter() - started
    return {"predictions": np.array(predictions),
            "confidence": np.array(confidences),
            "milliseconds": elapsed / count * 1000.0}


@functools.lru_cache(maxsize=1)
def _scored() -> dict:
    data = _data()
    images = data["x_test"][:EVAL]
    labels = data["y_test"][:EVAL]
    baseline = _model()
    keras_predictions = baseline["model"].predict(images, verbose=0)
    float_labels = keras_predictions.argmax(axis=1)

    started = time.perf_counter()
    baseline["model"].predict(images[:LATENCY_SAMPLES], batch_size=1, verbose=0)
    keras_latency = (time.perf_counter() - started) / LATENCY_SAMPLES * 1000.0

    out = {"Keras (float32)": {
        "bytes": baseline["bytes"],
        "accuracy": float((float_labels == labels).mean()),
        "milliseconds": keras_latency,
        "agreement": 1.0,
        "predictions": float_labels,
    }}
    for label, entry in _conversions().items():
        scored = _run_interpreter(entry["blob"], images)
        timed = _run_interpreter(entry["blob"], images, measure_latency=True)
        out[label] = {
            "bytes": entry["bytes"],
            "accuracy": float((scored["predictions"] == labels).mean()),
            "milliseconds": timed["milliseconds"],
            "agreement": float((scored["predictions"] == float_labels).mean()),
            "predictions": scored["predictions"],
            "convert_seconds": entry["convert_seconds"],
        }
    out["_labels"] = labels
    out["_float"] = float_labels
    out["_confidence"] = keras_predictions.max(axis=1)
    return out


def size_and_accuracy(fig, axes, p: Palette) -> None:
    scored = _scored()
    labels = [key for key in scored if not key.startswith("_")]
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(labels))
    sizes = [scored[label]["bytes"] / 1024 for label in labels]
    left.barh(positions, sizes, 0.55, color=p.blue)
    baseline = sizes[0]
    for y, (label, size) in enumerate(zip(labels, sizes)):
        left.annotate(f"{size:,.0f} KB  ({baseline / size:.2f}x smaller)",
                      (size, y), xytext=(6, 0), textcoords="offset points",
                      va="center", fontsize=7.5, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, max(sizes) * 1.55)
    left.set_xlabel("model size on disk (KB)")
    left.set_title("what conversion costs in bytes", fontsize=10)

    accuracies = [scored[label]["accuracy"] for label in labels]
    right.barh(positions, accuracies, 0.55, color=p.green)
    for y, (label, value) in enumerate(zip(labels, accuracies)):
        drop = accuracies[0] - value
        right.annotate(f"{value:.4f}   ({drop:+.4f})", (value, y),
                       xytext=(6, 0), textcoords="offset points", va="center",
                       fontsize=7.5, color=p.fg)
    right.set_yticks(positions)
    right.set_yticklabels([])
    right.set_xlim(0, 1.28)
    right.axvline(accuracies[0], color=p.muted, lw=1.2, ls="--")
    right.set_xlabel(f"accuracy on {EVAL:,} held-out digits")
    right.set_title("and what it costs in accuracy", fontsize=10)


def latency(fig, axes, p: Palette) -> None:
    scored = _scored()
    labels = [key for key in scored if not key.startswith("_")]
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(labels))
    times = [scored[label]["milliseconds"] for label in labels]
    left.barh(positions, times, 0.55, color=p.amber)
    for y, value in zip(positions, times):
        left.annotate(f"{value:.3f} ms", (value, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, max(times) * 1.4)
    left.set_xlabel(f"milliseconds per sample "
                    f"({LATENCY_SAMPLES} samples, batch of 1)")
    left.set_title("single-sample latency, as an edge device sees it",
                   fontsize=10)

    sizes = [scored[label]["bytes"] / 1024 for label in labels]
    right.scatter(sizes, [scored[label]["accuracy"] for label in labels],
                  s=90, color=p.purple)
    for label, size in zip(labels, sizes):
        right.annotate(label, (size, scored[label]["accuracy"]),
                       xytext=(0, 9), textcoords="offset points", ha="center",
                       fontsize=7.5, color=p.fg)
    right.set_xscale("log")
    right.set_xlabel("size (KB, log)")
    right.set_ylabel("accuracy")
    right.set_title("the actual trade-off", fontsize=10)


def disagreement(fig, axes, p: Palette) -> None:
    scored = _scored()
    labels = [key for key in scored
              if not key.startswith("_") and key != "Keras (float32)"]
    float_labels = scored["_float"]
    truth = scored["_labels"]
    confidence = scored["_confidence"]
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(labels))
    disagreements = [1.0 - scored[label]["agreement"] for label in labels]
    left.bar(positions, disagreements, 0.5, color=p.red)
    for x, label in zip(positions, labels):
        changed = int(round(disagreements[x] * len(truth)))
        left.annotate(f"{disagreements[x]:.4f}\n({changed} of {len(truth):,})",
                      (x, disagreements[x]), xytext=(0, 4),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=8, rotation=12, ha="right")
    left.set_ylim(0, max(disagreements + [0.001]) * 1.6)
    left.set_ylabel("share of predictions that changed")
    left.set_title("quantisation changes few answers", fontsize=10)

    worst = labels[int(np.argmax(disagreements))]
    changed = scored[worst]["predictions"] != float_labels
    if changed.any():
        right.hist(confidence[~changed], bins=24, alpha=0.6, color=p.muted,
                   density=True, label="prediction unchanged")
        right.hist(confidence[changed], bins=24, alpha=0.75, color=p.red,
                   density=True,
                   label=f"changed ({int(changed.sum())} samples)")
        right.axvline(float(confidence[changed].mean()), color=p.red, lw=1.4,
                      ls="--")
        right.annotate(f"mean {confidence[changed].mean():.4f}",
                       (float(confidence[changed].mean()), 0), xytext=(4, 14),
                       textcoords="offset points", fontsize=7.5, color=p.red)
    right.axvline(float(confidence.mean()), color=p.muted, lw=1.2, ls=":")
    right.set_xlabel("float model's confidence in its own prediction")
    right.set_ylabel("density")
    right.set_title(f"what {worst} changed", fontsize=10)
    right.legend(fontsize=7.5, loc="upper left")


FIGURES = [
    figure("size-and-accuracy", size_and_accuracy, size=(9.6, 3.4),
           axes=False),
    figure("latency", latency, size=(9.6, 3.4), axes=False),
    figure("disagreement", disagreement, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    info = _model()
    print("=== the model being deployed ===")
    print(f"{info['parameters']:,} parameters, {EPOCHS} epochs on MNIST, "
          f"{info['seconds']:.0f}s, validation accuracy {info['accuracy']:.4f}")

    scored = _scored()
    labels = [key for key in scored if not key.startswith("_")]
    print(f"\n=== four conversions, scored on {EVAL:,} held-out digits ===")
    print(f"{'conversion':22s} {'KB':>9} {'shrink':>8} {'accuracy':>9} "
          f"{'vs float':>9} {'agreement':>10} {'ms/sample':>10}")
    baseline_bytes = scored[labels[0]]["bytes"]
    baseline_accuracy = scored[labels[0]]["accuracy"]
    for label in labels:
        entry = scored[label]
        print(f"{label:22s} {entry['bytes'] / 1024:9,.1f} "
              f"{baseline_bytes / entry['bytes']:8.2f} "
              f"{entry['accuracy']:9.4f} "
              f"{entry['accuracy'] - baseline_accuracy:+9.4f} "
              f"{entry['agreement']:10.4f} {entry['milliseconds']:10.3f}")
    print("agreement is against the FLOAT model's own predictions, which is a")
    print("stricter check than accuracy: a conversion can keep the accuracy")
    print("while changing which samples it gets right")

    print("\n=== conversion cost ===")
    for label, entry in _conversions().items():
        print(f"{label:22s} {entry['convert_seconds']:6.1f}s to convert")
    print(f"the representative dataset for full int8 used {REPRESENTATIVE} "
          f"training images")

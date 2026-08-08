"""Figures for *Custom Models and Training Loops (TensorFlow)*.

Writing the training loop by hand is presented as a flexibility win with an
unstated cost. Both halves are measurable: whether the hand-written loop
reaches the same accuracy as `fit`, and what it costs in wall-clock when the
`tf.function` decorator is left off.

``equivalence``
    A hand-written loop against `fit` on identical data and seeds -- the check
    that the loop is correct before anything is concluded from it.

``graph-mode``
    The cost of eager execution, measured per step and per epoch, which is the
    single largest performance decision in a custom loop.

``custom-pieces``
    A custom loss and a custom metric verified against the built-in versions
    they replace, because a silently wrong metric is the usual failure here.
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
EPOCHS = 6
BATCH = 128
TIMED_STEPS = 60


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _network(keras, seed: int = 0):
    seed_everything(seed)
    return keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(10),
    ])


def _accuracy(model, images, labels) -> float:
    logits = model.predict(images, verbose=0, batch_size=512)
    return float((logits.argmax(axis=1) == labels).mean())


@functools.lru_cache(maxsize=1)
def _fit_run() -> dict:
    keras = tf().keras
    data = _data()
    model = _network(keras)
    model.compile(keras.optimizers.Adam(1e-3),
                  keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=BATCH, shuffle=False, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"curve": [float(v) for v in history.history["val_accuracy"]],
            "loss": [float(v) for v in history.history["loss"]],
            "accuracy": float(history.history["val_accuracy"][-1]),
            "seconds": time.perf_counter() - started}


def _custom_run(compiled: bool) -> dict:
    """The same training, written out step by step."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    model = _network(keras)
    optimizer = keras.optimizers.Adam(1e-3)
    loss_function = keras.losses.SparseCategoricalCrossentropy(
        from_logits=True)

    def raw_step(images, labels):
        with tensorflow.GradientTape() as tape:
            logits = model(images, training=True)
            loss = loss_function(labels, logits)
        optimizer.apply_gradients(
            zip(tape.gradient(loss, model.trainable_variables),
                model.trainable_variables))
        return loss

    # The ONLY difference between the two runs on this page.
    step = tensorflow.function(raw_step, reduce_retracing=True) if compiled \
        else raw_step

    images = data["x_train"]
    labels = data["y_train"]
    curve = []
    losses = []
    started = time.perf_counter()
    for _ in range(EPOCHS):
        epoch_loss = []
        # No shuffling, so this matches fit(shuffle=False) exactly.
        for begin in range(0, len(images) - BATCH + 1, BATCH):
            batch_loss = step(images[begin:begin + BATCH],
                              labels[begin:begin + BATCH])
            epoch_loss.append(float(batch_loss))
        losses.append(float(np.mean(epoch_loss)))
        curve.append(_accuracy(model, data["x_test"], data["y_test"]))
    return {"curve": curve, "loss": losses, "accuracy": curve[-1],
            "seconds": time.perf_counter() - started, "model": model}


@functools.lru_cache(maxsize=4)
def _custom(compiled: bool = True) -> dict:
    return _custom_run(compiled)


@functools.lru_cache(maxsize=1)
def _step_times() -> dict:
    """Per-step cost with and without tf.function, after a warm-up."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    out = {}
    for compiled in (False, True):
        model = _network(keras)
        optimizer = keras.optimizers.Adam(1e-3)
        loss_function = keras.losses.SparseCategoricalCrossentropy(
            from_logits=True)

        def raw_step(images, labels):
            with tensorflow.GradientTape() as tape:
                loss = loss_function(labels, model(images, training=True))
            optimizer.apply_gradients(
                zip(tape.gradient(loss, model.trainable_variables),
                    model.trainable_variables))
            return loss

        step = (tensorflow.function(raw_step, reduce_retracing=True)
                if compiled else raw_step)
        images = data["x_train"][:BATCH]
        labels = data["y_train"][:BATCH]
        step(images, labels)                     # warm-up / trace
        started = time.perf_counter()
        for _ in range(TIMED_STEPS):
            step(images, labels)
        elapsed = time.perf_counter() - started
        out["tf.function" if compiled else "eager"] = {
            "per_step_ms": elapsed / TIMED_STEPS * 1000.0,
            "steps_per_second": TIMED_STEPS / elapsed,
        }
    return out


@functools.lru_cache(maxsize=1)
def _custom_pieces() -> dict:
    """A hand-written loss and metric, checked against the built-ins."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    model = _custom(True)["model"]
    logits = model.predict(data["x_test"], verbose=0, batch_size=512)
    labels = data["y_test"]

    builtin_loss = float(keras.losses.SparseCategoricalCrossentropy(
        from_logits=True)(labels, logits).numpy())
    probabilities = tensorflow.nn.softmax(logits).numpy()
    picked = probabilities[np.arange(len(labels)), labels]
    manual_loss = float(-np.mean(np.log(np.clip(picked, 1e-12, None))))

    builtin_metric = keras.metrics.SparseCategoricalAccuracy()
    builtin_metric.update_state(labels, logits)
    manual_accuracy = float((logits.argmax(axis=1) == labels).mean())

    # A deliberately wrong metric: averaging per-batch accuracies when the
    # last batch is a different size.
    sizes = [512] * (len(labels) // 512) + [len(labels) % 512]
    begin = 0
    per_batch = []
    for size in sizes:
        if size == 0:
            continue
        chunk = slice(begin, begin + size)
        per_batch.append(float((logits[chunk].argmax(axis=1)
                                == labels[chunk]).mean()))
        begin += size
    naive_average = float(np.mean(per_batch))

    return {"builtin_loss": builtin_loss, "manual_loss": manual_loss,
            "builtin_accuracy": float(builtin_metric.result().numpy()),
            "manual_accuracy": manual_accuracy,
            "naive_average": naive_average,
            "batch_sizes": [size for size in sizes if size],
            "per_batch": per_batch}


def equivalence(fig, axes, p: Palette) -> None:
    fitted = _fit_run()
    custom = _custom(True)
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    left.plot(epochs, fitted["curve"], "o-", ms=6, lw=2.0, color=p.blue,
              label=f"model.fit ({fitted['accuracy']:.4f})")
    left.plot(epochs, custom["curve"], "s--", ms=5, lw=2.0, color=p.green,
              label=f"custom loop ({custom['accuracy']:.4f})")
    left.set_xlabel("epoch")
    left.set_ylabel("test accuracy")
    left.set_title("identical seeds, identical batches, no shuffling",
                   fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    differences = [abs(a - b) for a, b in zip(fitted["curve"],
                                              custom["curve"])]
    right.bar(list(epochs), differences, 0.5, color=p.amber)
    for epoch, value in zip(epochs, differences):
        right.annotate(f"{value:.4f}", (epoch, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    right.set_xlabel("epoch")
    right.set_ylabel("|fit - custom| test accuracy")
    right.set_title("the equivalence check, before trusting the loop",
                    fontsize=10)


def graph_mode(fig, axes, p: Palette) -> None:
    times = _step_times()
    fitted = _fit_run()
    eager = _custom(False)
    compiled = _custom(True)
    left, right = fig.subplots(1, 2)
    labels = list(times)
    positions = np.arange(len(labels))
    per_step = [times[label]["per_step_ms"] for label in labels]
    left.bar(positions, per_step, 0.5, color=[p.red, p.green])
    for x, value in zip(positions, per_step):
        left.annotate(f"{value:.2f} ms", (x, value), xytext=(0, 4),
                      textcoords="offset points", ha="center", fontsize=9,
                      color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels)
    left.set_ylabel(f"milliseconds per step (mean of {TIMED_STEPS})")
    left.set_ylim(0, max(per_step) * 1.35)
    left.set_title(f"one decorator, {per_step[0] / per_step[1]:.1f}x",
                   fontsize=10)

    runs = (("model.fit", fitted["seconds"], p.blue),
            ("custom, tf.function", compiled["seconds"], p.green),
            ("custom, eager", eager["seconds"], p.red))
    positions = np.arange(len(runs))
    seconds = [entry[1] for entry in runs]
    right.barh(positions, seconds, 0.5, color=[entry[2] for entry in runs])
    for y, (label, value, _) in zip(positions, runs):
        right.annotate(f"{value:.1f}s", (value, y), xytext=(6, 0),
                       textcoords="offset points", va="center", fontsize=8.5,
                       color=p.fg)
    right.set_yticks(positions)
    right.set_yticklabels([entry[0] for entry in runs], fontsize=8.5)
    right.invert_yaxis()
    right.set_xlim(0, max(seconds) * 1.3)
    right.set_xlabel(f"seconds for {EPOCHS} epochs")
    right.set_title("the same training, three ways", fontsize=10)


def custom_pieces(fig, axes, p: Palette) -> None:
    pieces = _custom_pieces()
    left, right = fig.subplots(1, 2)
    pairs = (("loss", pieces["builtin_loss"], pieces["manual_loss"]),
             ("accuracy", pieces["builtin_accuracy"],
              pieces["manual_accuracy"]))
    positions = np.arange(len(pairs))
    width = 0.38
    for index, (colour, key) in enumerate(((p.blue, 1), (p.green, 2))):
        values = [pair[key] for pair in pairs]
        left.bar(positions + (index - 0.5) * width, values, width * 0.9,
                 color=colour,
                 label="built-in" if index == 0 else "hand-written")
        for x, value in zip(positions + (index - 0.5) * width, values):
            left.annotate(f"{value:.6f}", (x, value), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=7, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([pair[0] for pair in pairs])
    left.set_title("hand-written against built-in, same predictions",
                   fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    sizes = pieces["batch_sizes"]
    right.bar(np.arange(len(sizes)), pieces["per_batch"], 0.6, color=p.amber)
    right.axhline(pieces["manual_accuracy"], color=p.green, lw=1.5, ls="--",
                  label=f"correct ({pieces['manual_accuracy']:.6f})")
    right.axhline(pieces["naive_average"], color=p.red, lw=1.5, ls=":",
                  label=f"mean of batches ({pieces['naive_average']:.6f})")
    right.set_xticks(np.arange(len(sizes)))
    right.set_xticklabels([str(size) for size in sizes], fontsize=7.5)
    right.set_xlabel("batch size")
    right.set_ylabel("accuracy within the batch")
    right.set_ylim(min(pieces["per_batch"]) - 0.02, 1.005)
    right.set_title("averaging batch means is not the mean", fontsize=10)
    right.legend(fontsize=7.5, loc="lower left")


FIGURES = [
    figure("equivalence", equivalence, size=(9.4, 3.4), axes=False),
    figure("graph-mode", graph_mode, size=(9.4, 3.4), axes=False),
    figure("custom-pieces", custom_pieces, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    fitted = _fit_run()
    compiled = _custom(True)
    eager = _custom(False)
    print(f"=== the same training three ways, {EPOCHS} epochs, "
          f"{LIMIT:,} MNIST rows ===")
    print(f"{'run':22s} {'final accuracy':>15} {'seconds':>9}")
    print(f"{'model.fit':22s} {fitted['accuracy']:15.4f} "
          f"{fitted['seconds']:9.1f}")
    print(f"{'custom, tf.function':22s} {compiled['accuracy']:15.4f} "
          f"{compiled['seconds']:9.1f}")
    print(f"{'custom, eager':22s} {eager['accuracy']:15.4f} "
          f"{eager['seconds']:9.1f}")
    difference = abs(fitted["accuracy"] - compiled["accuracy"])
    print(f"fit and the compiled custom loop differ by {difference:.4f} on the")
    print("final epoch, with the same seed, the same batches and no shuffling")

    print(f"\n=== per-epoch accuracy, fit against custom ===")
    print(f"{'epoch':>6} {'fit':>9} {'custom':>9} {'difference':>11}")
    for index, (a, b) in enumerate(zip(fitted["curve"], compiled["curve"]), 1):
        print(f"{index:6d} {a:9.4f} {b:9.4f} {abs(a - b):11.4f}")

    print(f"\n=== the cost of leaving tf.function off ===")
    times = _step_times()
    print(f"{'mode':14s} {'ms/step':>9} {'steps/s':>9}")
    for label, entry in times.items():
        print(f"{label:14s} {entry['per_step_ms']:9.2f} "
              f"{entry['steps_per_second']:9.1f}")
    ratio = (times["eager"]["per_step_ms"]
             / times["tf.function"]["per_step_ms"])
    print(f"the decorator is worth {ratio:.1f}x per step on this model")

    print(f"\n=== hand-written loss and metric, against the built-ins ===")
    pieces = _custom_pieces()
    print(f"loss:     built-in {pieces['builtin_loss']:.6f}   "
          f"hand-written {pieces['manual_loss']:.6f}   "
          f"difference {abs(pieces['builtin_loss'] - pieces['manual_loss']):.2e}")
    print(f"accuracy: built-in {pieces['builtin_accuracy']:.6f}   "
          f"hand-written {pieces['manual_accuracy']:.6f}   "
          f"difference "
          f"{abs(pieces['builtin_accuracy'] - pieces['manual_accuracy']):.2e}")
    print(f"averaging per-batch accuracies instead: "
          f"{pieces['naive_average']:.6f} "
          f"({pieces['naive_average'] - pieces['manual_accuracy']:+.6f})")
    print(f"batch sizes were {pieces['batch_sizes']} -- the short final batch")
    print("is weighted equally with the full ones, which is the bug")

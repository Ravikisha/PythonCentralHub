"""Figures for *Distributed Training with tf.distribute*.

There is no GPU on this machine, so a speed-up cannot be demonstrated. What can
be measured is everything else about data parallelism, and most of it is what
actually catches people out:

``batch-semantics``
    What a distribution strategy does to the batch size, the number of steps
    per epoch, and therefore to the effective learning rate.

``strategy-overhead``
    The cost of the strategy scaffolding itself, measured on CPU where it buys
    nothing -- the honest version of "distribution is not free".

``gradient-equivalence``
    Whether averaging gradients over N shards equals one gradient over the
    whole batch, checked numerically rather than asserted.
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
BATCH = 64
# Two is as far as the CPU emulation goes reliably here: a four-replica
# MirroredStrategy over virtual CPU devices raised an InternalError from the
# collective ops and left the process unusable for later measurements.
REPLICAS = (1, 2)
TIMED_STEPS = 30


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


@functools.lru_cache(maxsize=1)
def _virtual_devices() -> int:
    """Split the one physical CPU into several logical devices.

    This is the only way to exercise MirroredStrategy without accelerators. It
    does NOT make anything faster -- the same cores do all the work -- but the
    batching, gradient aggregation and variable mirroring are real.

    It has to happen before TensorFlow initialises its context, which is why
    the module calls it at import time: once any op has run, the configuration
    is frozen and this raises.
    """
    tensorflow = tf()
    physical = tensorflow.config.list_physical_devices("CPU")
    try:
        tensorflow.config.set_logical_device_configuration(
            physical[0],
            [tensorflow.config.LogicalDeviceConfiguration()
             for _ in range(max(REPLICAS))])
    except RuntimeError:
        pass                                   # already configured this session
    return len(tensorflow.config.list_logical_devices("CPU"))


def _devices(count: int) -> list:
    available = _virtual_devices()
    tensorflow = tf()
    logical = tensorflow.config.list_logical_devices("CPU")
    return [device.name for device in logical[:min(count, available)]]


@functools.lru_cache(maxsize=8)
def _strategy(count: int):
    """One strategy object per replica count.

    Creating a fresh MirroredStrategy for every measurement destabilised the
    process -- the second figure failed with a graph execution error that the
    first one had caused. Caching keeps exactly one per configuration.
    """
    tensorflow = tf()
    return tensorflow.distribute.MirroredStrategy(devices=_devices(count))


def _network(keras):
    seed_everything(0)
    return keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])


@functools.lru_cache(maxsize=8)
def _run(replicas: int, scale_batch: bool = True) -> dict:
    """Train under MirroredStrategy across `replicas` logical devices."""
    keras = tf().keras
    data = _data()
    strategy = _strategy(replicas)
    # The convention: the batch you pass is the GLOBAL batch, split across
    # replicas. Keeping it fixed means each replica sees fewer samples.
    global_batch = BATCH * replicas if scale_batch else BATCH

    with strategy.scope():
        model = _network(keras)
        model.compile(keras.optimizers.Adam(1e-3),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])

    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=global_batch, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    seconds = time.perf_counter() - started
    steps = int(np.ceil(len(data["x_train"]) / global_batch)) * EPOCHS
    return {"replicas": replicas,
            "global_batch": global_batch,
            "per_replica_batch": global_batch // replicas,
            "steps": steps,
            "seconds": seconds,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "curve": [float(v) for v in history.history["val_accuracy"]],
            "in_sync": int(strategy.num_replicas_in_sync)}


@functools.lru_cache(maxsize=1)
def _scaling() -> dict:
    return {count: _run(count) for count in REPLICAS}


@functools.lru_cache(maxsize=1)
def _fixed_batch() -> dict:
    """The same replica counts with the GLOBAL batch held constant."""
    return {count: _run(count, scale_batch=False) for count in REPLICAS}


@functools.lru_cache(maxsize=1)
def _overhead() -> dict:
    """Per-step cost with and without a strategy, same batch, same model."""
    keras = tf().keras
    data = _data()
    images = data["x_train"][:BATCH]
    labels = data["y_train"][:BATCH]
    out = {}

    model = _network(keras)
    model.compile(keras.optimizers.Adam(1e-3), "sparse_categorical_crossentropy")
    model.train_on_batch(images, labels)
    started = time.perf_counter()
    for _ in range(TIMED_STEPS):
        model.train_on_batch(images, labels)
    out["no strategy"] = (time.perf_counter() - started) / TIMED_STEPS * 1000.0

    for count in REPLICAS:
        strategy = _strategy(count)
        with strategy.scope():
            scoped = _network(keras)
            scoped.compile(keras.optimizers.Adam(1e-3),
                           "sparse_categorical_crossentropy")
        scoped.train_on_batch(images, labels)
        started = time.perf_counter()
        for _ in range(TIMED_STEPS):
            scoped.train_on_batch(images, labels)
        out[f"MirroredStrategy x{count}"] = (
            (time.perf_counter() - started) / TIMED_STEPS * 1000.0)
    return out


@functools.lru_cache(maxsize=1)
def _equivalence() -> dict:
    """Is the mean of per-shard gradients the gradient of the whole batch?"""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    model = _network(keras)
    loss_function = keras.losses.SparseCategoricalCrossentropy()
    images = data["x_train"][:256]
    labels = data["y_train"][:256]

    def gradient_of(x, y):
        with tensorflow.GradientTape() as tape:
            loss = loss_function(y, model(x, training=True))
        return [g.numpy() for g in tape.gradient(loss,
                                                 model.trainable_variables)]

    whole = gradient_of(images, labels)
    out = {}
    for shards in (2, 4, 8):
        size = len(images) // shards
        parts = [gradient_of(images[i * size:(i + 1) * size],
                             labels[i * size:(i + 1) * size])
                 for i in range(shards)]
        averaged = [np.mean([part[index] for part in parts], axis=0)
                    for index in range(len(whole))]
        difference = max(float(np.abs(a - b).max())
                         for a, b in zip(whole, averaged))
        scale = max(float(np.abs(a).max()) for a in whole)
        out[shards] = {"max_difference": difference,
                       "relative": difference / scale if scale else 0.0}

    # And the version that is NOT equivalent: uneven shards.
    uneven = [gradient_of(images[:200], labels[:200]),
              gradient_of(images[200:], labels[200:])]
    naive = [np.mean([part[index] for part in uneven], axis=0)
             for index in range(len(whole))]
    uneven_difference = max(float(np.abs(a - b).max())
                            for a, b in zip(whole, naive))
    return {"shards": out, "uneven": uneven_difference,
            "scale": max(float(np.abs(a).max()) for a in whole)}


def batch_semantics(fig, axes, p: Palette) -> None:
    scaled = _scaling()
    fixed = _fixed_batch()
    left, right = fig.subplots(1, 2)
    counts = list(scaled)
    positions = np.arange(len(counts))
    width = 0.38
    for index, (runs, label, colour) in enumerate((
            (scaled, "global batch scaled with replicas", p.blue),
            (fixed, "global batch held fixed", p.amber))):
        steps = [runs[count]["steps"] for count in counts]
        left.bar(positions + (index - 0.5) * width, steps, width * 0.9,
                 color=colour, label=label)
        for x, value in zip(positions + (index - 0.5) * width, steps):
            left.annotate(f"{value}", (x, value), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=7.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([f"{count} replica{'s' if count > 1 else ''}"
                          for count in counts])
    left.set_ylabel(f"gradient updates over {EPOCHS} epochs")
    left.set_title("more replicas, fewer updates -- unless you say otherwise",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="upper right")

    for runs, label, colour in ((scaled, "batch scaled", p.blue),
                                (fixed, "batch fixed", p.amber)):
        accuracies = [runs[count]["accuracy"] for count in counts]
        right.plot(counts, accuracies, "o-", ms=7, lw=2.0, color=colour,
                   label=label)
        for count, value in zip(counts, accuracies):
            right.annotate(f"{value:.4f}", (count, value), xytext=(0, 8),
                           textcoords="offset points", ha="center",
                           fontsize=7.5, color=colour)
    right.set_xticks(counts)
    right.set_xlabel("replicas in sync")
    right.set_ylabel(f"accuracy after {EPOCHS} epochs")
    right.set_title("the accuracy cost of fewer, larger steps", fontsize=10)
    right.legend(fontsize=8, loc="lower left")


def strategy_overhead(fig, axes, p: Palette) -> None:
    overhead = _overhead()
    scaled = _scaling()
    left, right = fig.subplots(1, 2)
    labels = list(overhead)
    positions = np.arange(len(labels))
    times = [overhead[label] for label in labels]
    baseline = times[0]
    colours = [p.muted] + [p.red] * (len(labels) - 1)
    left.barh(positions, times, 0.55, color=colours)
    for y, value in zip(positions, times):
        left.annotate(f"{value:.2f} ms ({value / baseline:.2f}x)", (value, y),
                      xytext=(6, 0), textcoords="offset points", va="center",
                      fontsize=8, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, max(times) * 1.5)
    left.set_xlabel(f"ms per step, identical batch of {BATCH}")
    left.set_title("the scaffolding costs something even at 1 replica",
                   fontsize=10)

    counts = list(scaled)
    seconds = [scaled[count]["seconds"] for count in counts]
    right.plot(counts, seconds, "o-", ms=7, lw=2.0, color=p.red,
               label="measured on this CPU")
    ideal = [seconds[0] / count for count in counts]
    right.plot(counts, ideal, "s--", ms=6, lw=1.8, color=p.green,
               label="what N accelerators would give")
    for count, value in zip(counts, seconds):
        right.annotate(f"{value:.1f}s", (count, value), xytext=(0, 8),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.red)
    right.set_xticks(counts)
    right.set_xlabel("replicas")
    right.set_ylabel(f"seconds for {EPOCHS} epochs")
    right.set_title("no GPUs here, so there is nothing to parallelise onto",
                    fontsize=10)
    right.legend(fontsize=8, loc="upper center")


def gradient_equivalence(fig, axes, p: Palette) -> None:
    info = _equivalence()
    shards = list(info["shards"])
    positions = np.arange(len(shards) + 1)
    values = [info["shards"][count]["max_difference"] for count in shards]
    values.append(info["uneven"])
    labels = [f"{count} equal shards" for count in shards] + ["2 UNEQUAL shards"]
    colours = [p.green] * len(shards) + [p.red]
    axes.bar(positions, values, 0.5, color=colours)
    for x, value in zip(positions, values):
        axes.annotate(f"{value:.2e}", (x, value), xytext=(0, 4),
                      textcoords="offset points", ha="center", fontsize=8,
                      color=p.fg)
    axes.set_yscale("log")
    axes.set_xticks(positions)
    axes.set_xticklabels(labels, fontsize=8, rotation=12, ha="right")
    axes.set_ylabel("largest disagreement with the whole-batch gradient")
    axes.set_title(f"averaging shard gradients (weights up to "
                   f"{info['scale']:.3f})", fontsize=10)


_virtual_devices()          # must run before any TensorFlow op in this process


FIGURES = [
    figure("batch-semantics", batch_semantics, size=(9.6, 3.4), axes=False),
    figure("strategy-overhead", strategy_overhead, size=(9.6, 3.4), axes=False),
    figure("gradient-equivalence", gradient_equivalence, size=(8.6, 3.4)),
]


if __name__ == "__main__":
    logical = _virtual_devices()
    print("=== the hardware, stated plainly ===")
    print(f"no GPU is available; the CPU has been split into {logical} logical")
    print("devices so MirroredStrategy has something to mirror ONTO. The")
    print("batching, variable mirroring and gradient aggregation are real; the")
    print("parallelism is not, because the same cores do all the work")

    print(f"\n=== what a strategy does to the batch ===")
    scaled = _scaling()
    fixed = _fixed_batch()
    print(f"{'replicas':>9} {'in sync':>8} {'global batch':>13} "
          f"{'per replica':>12} {'updates':>8} {'accuracy':>9} {'seconds':>8}")
    for count, entry in scaled.items():
        print(f"{count:9d} {entry['in_sync']:8d} {entry['global_batch']:13d} "
              f"{entry['per_replica_batch']:12d} {entry['steps']:8d} "
              f"{entry['accuracy']:9.4f} {entry['seconds']:8.1f}")
    print("\nthe same replica counts with the global batch held FIXED:")
    print(f"{'replicas':>9} {'global batch':>13} {'per replica':>12} "
          f"{'updates':>8} {'accuracy':>9}")
    for count, entry in fixed.items():
        print(f"{count:9d} {entry['global_batch']:13d} "
              f"{entry['per_replica_batch']:12d} {entry['steps']:8d} "
              f"{entry['accuracy']:9.4f}")
    print("scaling the batch with the replica count keeps each device busy but")
    print("divides the number of updates -- which is why the learning rate is")
    print("usually scaled alongside it")

    print(f"\n=== the cost of the scaffolding ===")
    for label, value in _overhead().items():
        print(f"{label:24s} {value:8.2f} ms/step")
    print("MirroredStrategy has to place variables, mirror them, and run an")
    print("all-reduce every step. On real accelerators that cost is repaid by")
    print("the parallelism; here there is none to repay it")

    info = _equivalence()
    print(f"\n=== is the averaged gradient the real gradient? ===")
    print(f"{'shards':>8} {'max difference':>16} {'relative':>11}")
    for count, entry in info["shards"].items():
        print(f"{count:8d} {entry['max_difference']:16.3e} "
              f"{entry['relative']:11.3e}")
    print(f"{'uneven':>8} {info['uneven']:16.3e} "
          f"{info['uneven'] / info['scale']:11.3e}")
    print("equal shards agree with the whole-batch gradient to floating-point")
    print("precision. UNEQUAL shards do not: averaging per-shard means weights")
    print("the small shard too heavily, which is the distributed version of")
    print("the per-batch averaging bug from the custom-training page")

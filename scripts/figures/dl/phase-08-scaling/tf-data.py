"""Figures for *Loading & Preprocessing Data with tf.data*.

Input-pipeline advice is usually a list of methods to call in a particular
order. Every item on that list is a throughput claim, and throughput is
measurable, so this module times each one instead of repeating the list.

The measurements use a deliberately slow map function. On a pipeline whose
per-sample work is trivial, every option looks identical and the page would
teach nothing.

``options``
    Samples per second for each pipeline option, added one at a time.

``batch-and-parallelism``
    Batch size and map parallelism swept separately, since they are the two
    knobs with a real cost curve.

``starvation``
    What prefetching actually fixes: the accelerator waiting on the pipeline,
    measured as time spent in the training step against time spent waiting.
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
ROWS = 4000
BATCH = 64
BATCHES = (16, 32, 64, 128, 256)
WORKERS = (1, 2, 4, 8)
WORK = 400            # inner iterations of the fake preprocessing
STEP_MS = 3.0         # how long a "training step" takes


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


def _slow_map(image, label):
    """Deliberately expensive preprocessing, so the pipeline is the bottleneck.

    Real pipelines decode JPEGs, resize, and augment. A `tf.data` page timed on
    a pipeline that only yields arrays measures nothing but memory bandwidth,
    and every option looks free.
    """
    tensorflow = tf()
    value = tensorflow.cast(image, tensorflow.float32)
    for _ in range(4):
        value = tensorflow.nn.avg_pool2d(value[None, ...], 3, 1, "SAME")[0]
    noise = tensorflow.random.stateless_normal(
        tensorflow.shape(value), seed=[1, 2]) * 0.01
    return value + noise, label


def _base(optimise: bool = True):
    """The source dataset.

    `optimise=False` switches off tf.data's automatic graph rewrites. That
    matters more than it sounds: modern tf.data parallelises a stateless `map`
    for you, so with the default settings the "add num_parallel_calls" advice
    measures almost nothing. Turning the rewrites off shows what each option is
    actually worth, and leaving them on shows what you get for free.
    """
    tensorflow = tf()
    data = _data()
    pipeline = tensorflow.data.Dataset.from_tensor_slices(
        (data["x_train"][:ROWS], data["y_train"][:ROWS]))
    if not optimise:
        options = tensorflow.data.Options()
        options.experimental_optimization.map_parallelization = False
        options.experimental_optimization.map_and_batch_fusion = False
        options.autotune.enabled = False
        pipeline = pipeline.with_options(options)
    return pipeline


def _time_pipeline(pipeline, limit: int = None) -> dict:
    """Walk the pipeline once and report samples per second."""
    started = time.perf_counter()
    rows = 0
    for images, _ in pipeline:
        rows += int(images.shape[0])
        if limit and rows >= limit:
            break
    elapsed = time.perf_counter() - started
    return {"seconds": elapsed, "rows": rows,
            "per_second": rows / elapsed if elapsed else 0.0}


@functools.lru_cache(maxsize=2)
def _option_runs(optimise: bool = True) -> dict:
    """Each option added to the one before it, so the deltas are attributable."""
    tensorflow = tf()
    autotune = tensorflow.data.AUTOTUNE
    out = {}

    def build_plain():
        return _base(optimise).map(_slow_map).batch(BATCH)

    def build_parallel():
        return (_base(optimise).map(_slow_map, num_parallel_calls=autotune)
                .batch(BATCH))

    def build_prefetch():
        return (_base(optimise).map(_slow_map, num_parallel_calls=autotune)
                .batch(BATCH).prefetch(autotune))

    def build_cached():
        return (_base(optimise).map(_slow_map, num_parallel_calls=autotune)
                .cache().batch(BATCH).prefetch(autotune))

    builders = (("map, batch", build_plain),
                ("+ parallel map", build_parallel),
                ("+ prefetch", build_prefetch),
                ("+ cache (2nd epoch)", build_cached))
    for label, builder in builders:
        pipeline = builder()
        if label.startswith("+ cache"):
            _time_pipeline(pipeline)          # first pass fills the cache
        out[label] = _time_pipeline(pipeline)
    return out


@functools.lru_cache(maxsize=1)
def _batch_runs() -> dict:
    tensorflow = tf()
    autotune = tensorflow.data.AUTOTUNE
    out = {}
    for size in BATCHES:
        pipeline = (_base().map(_slow_map, num_parallel_calls=autotune)
                    .batch(size).prefetch(autotune))
        out[size] = _time_pipeline(pipeline)
    return out


@functools.lru_cache(maxsize=1)
def _worker_runs() -> dict:
    tensorflow = tf()
    out = {}
    for workers in WORKERS:
        pipeline = (_base().map(_slow_map, num_parallel_calls=workers)
                    .batch(BATCH).prefetch(tensorflow.data.AUTOTUNE))
        out[workers] = _time_pipeline(pipeline)
    out["autotune"] = _time_pipeline(
        _base().map(_slow_map, num_parallel_calls=tensorflow.data.AUTOTUNE)
        .batch(BATCH).prefetch(tensorflow.data.AUTOTUNE))
    return out


@functools.lru_cache(maxsize=1)
def _starvation() -> dict:
    """Simulate a training step and measure how long it waits for data."""
    tensorflow = tf()
    autotune = tensorflow.data.AUTOTUNE
    out = {}
    variants = (
        ("no prefetch", lambda: _base().map(
            _slow_map, num_parallel_calls=autotune).batch(BATCH)),
        ("prefetch(AUTOTUNE)", lambda: _base().map(
            _slow_map, num_parallel_calls=autotune).batch(BATCH)
         .prefetch(autotune)),
    )
    for label, builder in variants:
        pipeline = builder()
        waiting = 0.0
        computing = 0.0
        iterator = iter(pipeline)
        batches = 0
        while True:
            start = time.perf_counter()
            try:
                next(iterator)
            except StopIteration:
                break
            waiting += time.perf_counter() - start
            start = time.perf_counter()
            # Stand-in for a training step: busy-wait, so it cannot overlap by
            # accident the way a sleep would.
            target = start + STEP_MS / 1000.0
            while time.perf_counter() < target:
                pass
            computing += time.perf_counter() - start
            batches += 1
        out[label] = {"waiting": waiting, "computing": computing,
                      "batches": batches,
                      "share": waiting / (waiting + computing)}
    return out


def options(fig, axes, p: Palette) -> None:
    manual = _option_runs(False)
    automatic = _option_runs(True)
    labels = list(manual)
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(labels))
    width = 0.38
    for index, (runs, label, color) in enumerate((
            (manual, "rewrites off", p.red),
            (automatic, "rewrites on (the default)", p.green))):
        rates = [runs[key]["per_second"] for key in labels]
        left.barh(positions + (index - 0.5) * width, rates, width * 0.9,
                  color=color, label=label)
        for y, value in zip(positions + (index - 0.5) * width, rates):
            left.annotate(f"{value:,.0f}/s", (value, y), xytext=(5, 0),
                          textcoords="offset points", va="center",
                          fontsize=7, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xscale("log")
    left.set_xlim(1000, max(automatic[key]["per_second"]
                            for key in labels) * 4)
    left.set_xlabel("samples per second (log)")
    left.set_title(f"{ROWS:,} samples, each option added to the last",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    baseline = manual[labels[0]]["per_second"]
    gains = [manual[key]["per_second"] / baseline for key in labels]
    auto_gains = [automatic[key]["per_second"] / baseline for key in labels]
    right.plot(positions, gains, "o-", ms=7, lw=2.0, color=p.red,
               label="rewrites off")
    right.plot(positions, auto_gains, "s-", ms=6, lw=2.0, color=p.green,
               label="rewrites on")
    for x, value in zip(positions, gains):
        right.annotate(f"{value:.1f}x", (x, value), xytext=(0, 8),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.red)
    right.set_xticks(positions)
    right.set_xticklabels(labels, fontsize=7.5, rotation=15, ha="right")
    right.set_yscale("log")
    right.set_ylabel("speed-up over the unoptimised pipeline")
    right.set_title("what each option is worth, and what is already free",
                    fontsize=10)
    right.legend(fontsize=8, loc="upper left")


def batch_and_parallelism(fig, axes, p: Palette) -> None:
    batches = _batch_runs()
    workers = _worker_runs()
    left, right = fig.subplots(1, 2)
    sizes = list(batches)
    rates = [batches[size]["per_second"] for size in sizes]
    left.plot(sizes, rates, "o-", ms=7, lw=2.0, color=p.blue)
    for size, value in zip(sizes, rates):
        left.annotate(f"{value:,.0f}", (size, value), xytext=(0, 9),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.blue)
    left.set_xscale("log", base=2)
    left.set_xticks(sizes)
    left.set_xticklabels([str(s) for s in sizes])
    left.minorticks_off()
    left.set_xlabel("batch size")
    left.set_ylabel("samples per second")
    left.set_title("batching amortises per-batch overhead", fontsize=10)

    numeric = [key for key in workers if key != "autotune"]
    worker_rates = [workers[key]["per_second"] for key in numeric]
    right.plot(numeric, worker_rates, "o-", ms=7, lw=2.0, color=p.green,
               label="num_parallel_calls")
    right.axhline(workers["autotune"]["per_second"], color=p.amber, lw=1.6,
                  ls="--",
                  label=f"AUTOTUNE ({workers['autotune']['per_second']:,.0f}/s)")
    for key, value in zip(numeric, worker_rates):
        right.annotate(f"{value:,.0f}", (key, value), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.green)
    right.set_xticks(numeric)
    right.set_xlabel("parallel map calls")
    right.set_ylabel("samples per second")
    right.set_title(f"this machine has {os.cpu_count()} logical cores",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def starvation(fig, axes, p: Palette) -> None:
    runs = _starvation()
    labels = list(runs)
    positions = np.arange(len(labels))
    waiting = [runs[label]["waiting"] for label in labels]
    computing = [runs[label]["computing"] for label in labels]
    axes.barh(positions, computing, 0.5, color=p.green,
              label=f"the training step ({STEP_MS:.0f} ms each)")
    axes.barh(positions, waiting, 0.5, left=computing, color=p.red,
              label="waiting for the next batch")
    for y, label in zip(positions, labels):
        entry = runs[label]
        total = entry["waiting"] + entry["computing"]
        axes.annotate(f"{total:.2f}s total, {entry['share']:.1%} waiting",
                      (total, y), xytext=(8, 0), textcoords="offset points",
                      va="center", fontsize=8.5, color=p.fg)
    axes.set_yticks(positions)
    axes.set_yticklabels(labels, fontsize=9)
    axes.invert_yaxis()
    axes.set_xlim(0, max(w + c for w, c in zip(waiting, computing)) * 1.45)
    axes.set_xlabel("seconds across one epoch")
    axes.set_title("prefetch overlaps loading with the step that consumes it",
                   fontsize=10)
    axes.legend(fontsize=8.5, loc="lower right")


FIGURES = [
    figure("options", options, size=(9.6, 3.2), axes=False),
    figure("batch-and-parallelism", batch_and_parallelism, size=(9.4, 3.4),
           axes=False),
    figure("starvation", starvation, size=(8.8, 2.8)),
]


if __name__ == "__main__":
    print(f"=== the pipeline being measured ===")
    print(f"{ROWS:,} MNIST images through a deliberately slow map: four "
          f"average-pooling passes plus noise.")
    print(f"A trivial map would make every option below look identical, which "
          f"is the usual reason these numbers are never shown.")
    print(f"this machine has {os.cpu_count()} logical cores")

    print(f"\n=== options, added one at a time ===")
    manual = _option_runs(False)
    automatic = _option_runs(True)
    baseline = manual["map, batch"]["per_second"]
    print(f"{'pipeline':22s} {'rewrites off':>14} {'speed-up':>9} "
          f"{'rewrites on':>13} {'speed-up':>9}")
    for label in manual:
        off = manual[label]["per_second"]
        on = automatic[label]["per_second"]
        print(f"{label:22s} {off:14,.0f} {off / baseline:8.2f}x "
              f"{on:13,.0f} {on / baseline:8.2f}x")
    print("the second pair of columns is the default. tf.data rewrites a")
    print("stateless map into a parallel one for you, so 'add")
    print("num_parallel_calls' measures almost nothing unless you disable")
    print("that -- which is what the first pair does")
    print("cache is timed on the SECOND pass: the first one has to do the work")
    print("before there is anything to cache, so timing that pass would report")
    print("the cost and hide the benefit")

    print(f"\n=== batch size ===")
    print(f"{'batch':>7} {'seconds':>9} {'samples/s':>11}")
    for size, entry in _batch_runs().items():
        print(f"{size:7d} {entry['seconds']:9.2f} {entry['per_second']:11,.0f}")

    print(f"\n=== map parallelism ===")
    print(f"{'workers':>9} {'seconds':>9} {'samples/s':>11}")
    for key, entry in _worker_runs().items():
        print(f"{str(key):>9} {entry['seconds']:9.2f} "
              f"{entry['per_second']:11,.0f}")

    print(f"\n=== starvation: a {STEP_MS:.0f} ms training step ===")
    print(f"{'pipeline':22s} {'waiting':>9} {'computing':>10} "
          f"{'total':>8} {'% waiting':>10}")
    for label, entry in _starvation().items():
        total = entry["waiting"] + entry["computing"]
        print(f"{label:22s} {entry['waiting']:9.2f} "
              f"{entry['computing']:10.2f} {total:8.2f} "
              f"{entry['share']:10.1%}")
    print("prefetch does not make loading faster -- it makes it happen while")
    print("the previous batch is still being trained on")

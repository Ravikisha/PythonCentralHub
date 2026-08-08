"""Figures for *Fine-Tuning and Parameter-Efficient Tuning (LoRA)*.

There is no pretrained checkpoint on this machine and nothing may be
downloaded, so the base model is pretrained here: Fashion-MNIST classes 0-4,
then adapted to classes 5-9. That is a small stand-in for the usual setting,
but the mechanism under test is exactly the same one -- a low-rank update
``W + BA`` applied to a frozen weight matrix -- and it is the mechanism, not
the scale, that the numbers are about.

``strategies``
    Accuracy against trainable parameters for five ways of adapting the base
    model, including training from scratch as the floor.

``rank-sweep``
    LoRA rank against accuracy and against parameter count, which is the whole
    knob the method exposes.

``cost``
    What each strategy costs to store per task and to train, which is the
    argument for adapters and has nothing to do with accuracy.
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

LIMIT = 20000
TARGET_ROWS = 1500
WIDTH = 256
SOURCE_EPOCHS = 12
EPOCHS = 12
RANKS = (1, 2, 4, 8, 16)
LORA_RANK = 4
SEEDS = 2


@functools.lru_cache(maxsize=1)
def _split() -> dict:
    """Fashion-MNIST cut in half by label: 0-4 to pretrain on, 5-9 to adapt."""
    data = dataset("fashion", limit=LIMIT, flat=True)
    out = {}
    for part in ("train", "test"):
        x, y = data[f"x_{part}"], data[f"y_{part}"]
        source = y < 5
        out[f"source_x_{part}"], out[f"source_y_{part}"] = x[source], y[source]
        out[f"target_x_{part}"] = x[~source]
        out[f"target_y_{part}"] = y[~source] - 5
    out["target_x_train"] = out["target_x_train"][:TARGET_ROWS]
    out["target_y_train"] = out["target_y_train"][:TARGET_ROWS]
    return out


def _lora_dense(base_layer, rank: int):
    """Wrap a frozen Dense layer with a trainable rank-`r` correction.

    The base weight W stays exactly as pretrained. What trains is B (d x r) and
    A (r x k), and the layer computes x @ (W + B A) + b. B starts at zero, so
    the wrapped layer begins life numerically identical to the frozen one.
    """
    keras = tf().keras
    tensorflow = tf()

    class LoRADense(keras.layers.Layer):
        def __init__(self, base, rank, **kwargs):
            super().__init__(**kwargs)
            self.base = base
            self.base.trainable = False
            self.rank = rank

        def build(self, shape):
            inputs = int(self.base.kernel.shape[0])
            outputs = int(self.base.kernel.shape[1])
            self.down = self.add_weight(
                shape=(inputs, self.rank), initializer="glorot_uniform",
                trainable=True, name="lora_down")
            self.up = self.add_weight(
                shape=(self.rank, outputs), initializer="zeros",
                trainable=True, name="lora_up")

        def call(self, x):
            correction = tensorflow.matmul(tensorflow.matmul(x, self.down),
                                           self.up)
            return self.base.activation(
                tensorflow.matmul(x, self.base.kernel) + self.base.bias
                + correction)

    return LoRADense(base_layer, rank)


@functools.lru_cache(maxsize=1)
def _base() -> dict:
    """Pretrain once on classes 0-4 and reuse the weights everywhere."""
    keras = tf().keras
    data = _split()
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(WIDTH, activation="relu", name="hidden_one"),
        keras.layers.Dense(WIDTH, activation="relu", name="hidden_two"),
        keras.layers.Dense(5, activation="softmax", name="head"),
    ])
    model.compile("adam", "sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    started = time.perf_counter()
    model.fit(data["source_x_train"], data["source_y_train"],
              epochs=SOURCE_EPOCHS, batch_size=128, verbose=0)
    seconds = time.perf_counter() - started
    accuracy = model.evaluate(data["source_x_test"], data["source_y_test"],
                              verbose=0)[1]
    return {"weights": [w.copy() for w in model.get_weights()],
            "accuracy": float(accuracy), "seconds": seconds,
            "parameters": int(model.count_params())}


def _assemble(strategy: str, rank: int, seed: int):
    keras = tf().keras
    base = _base()
    seed_everything(seed)
    inputs = keras.layers.Input((784,))
    one = keras.layers.Dense(WIDTH, activation="relu")
    two = keras.layers.Dense(WIDTH, activation="relu")
    one.build((None, 784))
    two.build((None, WIDTH))
    if strategy != "scratch":
        one.set_weights(base["weights"][0:2])
        two.set_weights(base["weights"][2:4])

    if strategy == "lora":
        hidden = _lora_dense(one, rank)(inputs)
        hidden = _lora_dense(two, rank)(hidden)
    else:
        if strategy in ("frozen", "last-layer"):
            one.trainable = False
            two.trainable = strategy == "last-layer"
        hidden = two(one(inputs))
    outputs = keras.layers.Dense(5, activation="softmax")(hidden)
    model = keras.Model(inputs, outputs)
    model.compile("adam", "sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model


def _run(strategy: str, rank: int = LORA_RANK) -> dict:
    data = _split()
    scores, seconds, trainable = [], [], None
    for seed in range(SEEDS):
        model = _assemble(strategy, rank, seed)
        trainable = int(sum(np.prod(w.shape)
                            for w in model.trainable_weights))
        started = time.perf_counter()
        model.fit(data["target_x_train"], data["target_y_train"],
                  epochs=EPOCHS, batch_size=128, verbose=0)
        seconds.append(time.perf_counter() - started)
        scores.append(model.evaluate(data["target_x_test"],
                                     data["target_y_test"], verbose=0)[1])
    return {"accuracy": float(np.mean(scores)),
            "spread": float(np.max(scores) - np.min(scores)),
            "trainable": trainable,
            "seconds": float(np.mean(seconds))}


STRATEGIES = (
    ("scratch", "from scratch"),
    ("frozen", "frozen features + head"),
    ("last-layer", "unfreeze last hidden"),
    ("lora", f"LoRA rank {LORA_RANK}"),
    ("full", "full fine-tune"),
)


@functools.lru_cache(maxsize=1)
def _strategies() -> dict:
    return {key: {**_run(key), "label": label} for key, label in STRATEGIES}


@functools.lru_cache(maxsize=1)
def _ranks() -> dict:
    return {rank: _run("lora", rank) for rank in RANKS}


def strategies(fig, axes, p: Palette) -> None:
    runs = _strategies()
    left, right = fig.subplots(1, 2, width_ratios=(1.0, 1.15))
    keys = [key for key, _ in STRATEGIES]
    positions = np.arange(len(keys))
    colours = (p.muted, p.amber, p.purple, p.green, p.blue)
    values = [runs[key]["accuracy"] for key in keys]
    left.barh(positions, values, color=colours, height=0.62)
    for position, key in zip(positions, keys):
        left.annotate(f"{runs[key]['accuracy']:.4f}",
                      (runs[key]["accuracy"], position), xytext=(4, 0),
                      textcoords="offset points", fontsize=7.5, color=p.fg,
                      va="center")
    left.set_yticks(positions)
    left.set_yticklabels([runs[key]["label"] for key in keys], fontsize=8)
    left.set_xlim(0, 1.12)
    left.set_xlabel("accuracy on the target classes")
    left.set_title(f"{TARGET_ROWS:,} target rows, {EPOCHS} epochs",
                   fontsize=10)
    left.invert_yaxis()

    for key, colour in zip(keys, colours):
        right.scatter(runs[key]["trainable"], runs[key]["accuracy"], s=70,
                      color=colour, zorder=3)
        right.annotate(runs[key]["label"],
                       (runs[key]["trainable"], runs[key]["accuracy"]),
                       xytext=(6, -3), textcoords="offset points",
                       fontsize=7.5, color=p.fg)
    right.set_xscale("log")
    right.set_xlabel("trainable parameters")
    right.set_ylabel("accuracy")
    right.set_title("the same accuracies against what they cost to train",
                    fontsize=10)


def rank_sweep(fig, axes, p: Palette) -> None:
    runs = _ranks()
    full = _strategies()["full"]
    frozen = _strategies()["frozen"]
    ax = fig.subplots(1, 1)
    ranks = list(RANKS)
    accuracy = [runs[rank]["accuracy"] for rank in ranks]
    ax.plot(ranks, accuracy, "o-", color=p.blue, lw=1.8, ms=6, label="LoRA")
    for rank, value in zip(ranks, accuracy):
        ax.annotate(f"{value:.4f}\n{runs[rank]['trainable']:,}p",
                    (rank, value), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=7, color=p.fg)
    ax.axhline(full["accuracy"], color=p.green, lw=1.3, ls="--",
               label=f"full fine-tune ({full['accuracy']:.4f}, "
                     f"{full['trainable']:,} trainable)")
    ax.axhline(frozen["accuracy"], color=p.amber, lw=1.3, ls=":",
               label=f"frozen features ({frozen['accuracy']:.4f})")
    ax.set_xscale("log", base=2)
    ax.set_xticks(ranks)
    ax.set_xticklabels([str(rank) for rank in ranks])
    ax.set_xlabel("LoRA rank r — the inner dimension of the B A correction")
    ax.set_ylabel("accuracy on the target classes")
    ax.set_title(f"mean of {SEEDS} seeds", fontsize=10)
    ax.legend(fontsize=7.5, loc="lower right")


def cost(fig, axes, p: Palette) -> None:
    runs = _strategies()
    left, right = fig.subplots(1, 2)
    keys = [key for key, _ in STRATEGIES]
    positions = np.arange(len(keys))
    colours = (p.muted, p.amber, p.purple, p.green, p.blue)

    # Storing 20 adapted tasks: what has to be kept per task.
    tasks = 20
    per_task = [runs[key]["trainable"] * 4 / 1024 for key in keys]
    totals = [value * tasks for value in per_task]
    left.bar(positions, totals, color=colours, width=0.6)
    for position, value in zip(positions, totals):
        left.annotate(f"{value:,.0f} KB", (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    left.set_yscale("log")
    left.set_xticks(positions)
    left.set_xticklabels([runs[key]["label"].replace(" + ", "\n+ ")
                          for key in keys], fontsize=6.5, rotation=12)
    left.set_ylabel(f"KB to store {tasks} adapted tasks (float32)")
    left.set_title("the argument for adapters is storage, not accuracy",
                   fontsize=10)

    seconds = [runs[key]["seconds"] for key in keys]
    right.bar(positions, seconds, color=colours, width=0.6)
    for position, value in zip(positions, seconds):
        right.annotate(f"{value:.1f}s", (position, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([runs[key]["label"].replace(" + ", "\n+ ")
                           for key in keys], fontsize=6.5, rotation=12)
    right.set_ylabel(f"seconds for {EPOCHS} epochs")
    right.set_title("wall clock, mean of both seeds", fontsize=10)


FIGURES = [
    figure("strategies", strategies, size=(9.2, 4.2), axes=False),
    figure("rank-sweep", rank_sweep, size=(8.4, 4.4), axes=False),
    figure("cost", cost, size=(9.2, 4.6), axes=False),
]


if __name__ == "__main__":
    base = _base()
    print("=== the base model ===")
    print(f"pretrained on classes 0-4: {base['accuracy']:.4f} in "
          f"{base['seconds']:.1f}s, {base['parameters']:,} parameters")

    runs = _strategies()
    print(f"\n=== adapting to classes 5-9, {TARGET_ROWS:,} rows ===")
    print(f"{'strategy':26s} {'accuracy':>9} {'spread':>8} {'trainable':>11} "
          f"{'share':>8} {'seconds':>9}")
    total = base["parameters"]
    for key, _ in STRATEGIES:
        run = runs[key]
        print(f"{run['label']:26s} {run['accuracy']:9.4f} "
              f"{run['spread']:8.4f} {run['trainable']:11,} "
              f"{run['trainable'] / total:8.4f} {run['seconds']:9.1f}")

    print("\n=== LoRA rank sweep ===")
    print(f"{'rank':>6} {'accuracy':>9} {'trainable':>11} {'seconds':>9}")
    for rank, run in _ranks().items():
        print(f"{rank:6d} {run['accuracy']:9.4f} {run['trainable']:11,} "
              f"{run['seconds']:9.1f}")

    full, frozen = runs["full"], runs["frozen"]
    lora = runs["lora"]
    print(f"\nLoRA rank {LORA_RANK} reaches {lora['accuracy']:.4f} against "
          f"full fine-tuning's {full['accuracy']:.4f}")
    print(f"training {lora['trainable']:,} parameters instead of "
          f"{full['trainable']:,} -- "
          f"{full['trainable'] / max(lora['trainable'], 1):.1f}x fewer")
    print(f"frozen features alone reach {frozen['accuracy']:.4f}, which is the "
          f"number LoRA has to beat to be worth its complexity")

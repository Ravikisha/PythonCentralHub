"""Figures for *Learning Rate Scheduling*.

``schedule-shapes``
    The five schedules drawn as functions of the step count, so "exponential
    decay" stops being a phrase and becomes a curve.

``lr-range-test``
    A single epoch with the rate ramped from 1e-5 to 10, recording the loss per
    batch. This is how you find a base rate without guessing.

``schedule-results``
    Every schedule trained on the same data with the same budget, and the
    accuracy each one reached.
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

LIMIT = 8000
EPOCHS = 20
BATCH = 128
BASE = 0.1
STEPS_PER_EPOCH = int(np.ceil(LIMIT / BATCH))
TOTAL_STEPS = STEPS_PER_EPOCH * EPOCHS


def constant(step: int) -> float:
    return BASE


def power_decay(step: int, decay_steps: int = STEPS_PER_EPOCH * 5) -> float:
    return BASE / (1 + step / decay_steps)


def exponential(step: int, decay: float = 0.9,
                decay_steps: int = STEPS_PER_EPOCH * 2) -> float:
    return BASE * decay ** (step / decay_steps)


def piecewise(step: int) -> float:
    epoch = step / STEPS_PER_EPOCH
    if epoch < 8:
        return BASE
    if epoch < 15:
        return BASE / 10
    return BASE / 100


def one_cycle(step: int) -> float:
    """Ramp up to the peak over 45% of training, down again, then anneal."""
    peak, start = BASE, BASE / 10
    up = int(0.45 * TOTAL_STEPS)
    down = int(0.9 * TOTAL_STEPS)
    if step < up:
        return start + (peak - start) * step / up
    if step < down:
        return peak - (peak - start) * (step - up) / (down - up)
    remaining = max(TOTAL_STEPS - down, 1)
    return start * (1 - 0.9 * min((step - down) / remaining, 1.0))


SCHEDULES = {
    "constant": constant,
    "power": power_decay,
    "exponential": exponential,
    "piecewise": piecewise,
    "1cycle": one_cycle,
}


def schedule_shapes(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    steps = np.arange(TOTAL_STEPS)
    for (name, schedule), color in zip(SCHEDULES.items(), p.cycle):
        values = [schedule(int(s)) for s in steps]
        ax.plot(steps / STEPS_PER_EPOCH, values, lw=2.0, color=color,
                label=f"{name} — ends at {values[-1]:.5f}")
    ax.set_yscale("log")
    ax.set_xlabel("epoch")
    ax.set_ylabel("learning rate (log scale)")
    ax.set_title(f"Five schedules, base rate {BASE}, {EPOCHS} epochs",
                 fontsize=10.5)
    ax.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _range_test() -> dict:
    """Ramp the rate across one pass and record the loss per batch."""
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    optimizer = keras.optimizers.SGD(1e-5)
    loss_fn = keras.losses.SparseCategoricalCrossentropy()
    tensorflow = tf()

    rates, losses = [], []
    steps = 120
    x, y = data["x_train"], data["y_train"]
    for step in range(steps):
        rate = 1e-5 * (10.0 / 1e-5) ** (step / (steps - 1))
        optimizer.learning_rate.assign(rate)
        start = (step * BATCH) % (len(x) - BATCH)
        batch_x = x[start:start + BATCH]
        batch_y = y[start:start + BATCH]
        with tensorflow.GradientTape() as tape:
            loss = loss_fn(batch_y, model(batch_x, training=True))
        optimizer.apply_gradients(
            zip(tape.gradient(loss, model.trainable_variables),
                model.trainable_variables))
        rates.append(rate)
        losses.append(float(loss.numpy()))
    return {"rates": rates, "losses": losses}


def lr_range_test(fig, axes, p: Palette) -> None:
    result = _range_test()
    ax = fig.subplots(1, 1)
    rates = np.array(result["rates"])
    losses = np.array([v if np.isfinite(v) else np.nan
                       for v in result["losses"]])
    smoothed = np.convolve(np.nan_to_num(losses, nan=np.nanmax(losses)),
                           np.ones(5) / 5, mode="same")

    ax.plot(rates, losses, lw=1.0, color=p.muted, alpha=0.6, label="per batch")
    ax.plot(rates, smoothed, lw=2.2, color=p.blue, label="5-batch average")
    best = int(np.nanargmin(smoothed))
    ax.scatter([rates[best]], [smoothed[best]], s=90, facecolors="none",
               edgecolors=p.green, lw=2.0, zorder=5)
    ax.annotate(f"minimum at lr = {rates[best]:.4f}",
                (rates[best], smoothed[best]), textcoords="offset points",
                xytext=(10, 18), fontsize=8.5, color=p.green)
    suggestion = rates[best] / 10
    ax.axvline(suggestion, color=p.amber, lw=1.6, ls="--",
               label=f"a tenth of it: {suggestion:.4f}")
    ax.set_xscale("log")
    ax.set_xlabel("learning rate (log scale)")
    ax.set_ylabel("training loss on the batch")
    ax.set_ylim(0, min(np.nanmax(losses), 6))
    ax.set_title("One pass with the rate ramped from 1e-5 to 10",
                 fontsize=10.5)
    ax.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _schedule_runs() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    out = {}
    for name, schedule in SCHEDULES.items():
        seed_everything(0)
        model = keras.Sequential([
            keras.layers.Input((784,)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(10, activation="softmax"),
        ])
        model.compile(keras.optimizers.SGD(BASE),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        step = [0]

        def by_batch(batch, logs, schedule=schedule, step=step):
            model.optimizer.learning_rate.assign(schedule(step[0]))
            step[0] += 1

        history = model.fit(
            data["x_train"], data["y_train"], epochs=EPOCHS,
            batch_size=BATCH, verbose=0,
            validation_data=(data["x_test"], data["y_test"]),
            callbacks=[keras.callbacks.LambdaCallback(on_batch_begin=by_batch)])
        out[name] = {
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "loss": [float(v) for v in history.history["loss"]],
        }
    return out


def schedule_results(fig, axes, p: Palette) -> None:
    runs = _schedule_runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for (name, run), color in zip(runs.items(), p.cycle):
        left.plot(epochs, run["val_accuracy"], lw=1.8, color=color,
                  label=f"{name} — {run['val_accuracy'][-1]:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_ylim(0.75, 0.90)
    left.set_title("validation accuracy", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    names = list(runs)
    finals = [runs[n]["val_accuracy"][-1] for n in names]
    bests = [max(runs[n]["val_accuracy"]) for n in names]
    positions = np.arange(len(names))
    right.bar(positions - 0.19, finals, 0.38, color=p.blue, label="final epoch")
    right.bar(positions + 0.19, bests, 0.38, color=p.green, label="best epoch")
    for x, value in zip(positions - 0.19, finals):
        right.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                       xytext=(0, 3), ha="center", fontsize=7, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(names, fontsize=8, rotation=15, ha="right")
    right.set_ylim(0.7, 0.93)
    right.set_ylabel("validation accuracy")
    right.set_title("final against best", fontsize=10)
    right.legend(fontsize=8, loc="lower left")


FIGURES = [
    figure("schedule-shapes", schedule_shapes, size=(8.0, 3.6), axes=False),
    figure("lr-range-test", lr_range_test, size=(7.8, 3.8), axes=False),
    figure("schedule-results", schedule_results, size=(9.4, 3.6), axes=False),
]


if __name__ == "__main__":
    print(f"steps per epoch {STEPS_PER_EPOCH}, total steps {TOTAL_STEPS}")
    print("\n=== schedule values at a few epochs ===")
    print(f"{'schedule':14s} " + " ".join(f"{e:>9}" for e in (0, 5, 10, 15, 19)))
    for name, schedule in SCHEDULES.items():
        row = [schedule(int(e * STEPS_PER_EPOCH)) for e in (0, 5, 10, 15, 19)]
        print(f"{name:14s} " + " ".join(f"{v:9.5f}" for v in row))

    print("\n=== learning rate range test ===")
    result = _range_test()
    rates, losses = np.array(result["rates"]), np.array(result["losses"])
    smoothed = np.convolve(losses, np.ones(5) / 5, mode="same")
    best = int(np.nanargmin(smoothed))
    print(f"minimum smoothed loss {smoothed[best]:.4f} at lr {rates[best]:.5f}")
    print(f"suggested base rate (a tenth of it): {rates[best] / 10:.5f}")
    for index in range(0, len(rates), 12):
        print(f"  lr {rates[index]:10.5f}  loss {losses[index]:10.4f}")
    print(f"  lr {rates[-1]:10.5f}  loss {losses[-1]:10.4f}")

    print("\n=== schedules trained ===")
    print(f"{'schedule':14s} {'final val acc':>14} {'best val acc':>13} "
          f"{'best epoch':>11} {'final train loss':>17}")
    for name, run in _schedule_runs().items():
        best_epoch = int(np.argmax(run["val_accuracy"])) + 1
        print(f"{name:14s} {run['val_accuracy'][-1]:14.4f} "
              f"{max(run['val_accuracy']):13.4f} {best_epoch:11d} "
              f"{run['loss'][-1]:17.4f}")

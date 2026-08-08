"""Figures for *Callbacks and TensorBoard*.

``batch-vs-epoch``
    A custom callback recording the loss on every batch, with the epoch averages
    Keras reports drawn on top. The epoch number hides a lot.

``callback-policies``
    Four training policies built only from callbacks, scored on the same test
    set: fixed epochs, early stopping, best-checkpoint restore, and rate
    reduction on plateau.

``plateau-trace``
    ``ReduceLROnPlateau`` in operation: the learning rate it actually chose on
    each epoch, against the validation loss that triggered each cut. The
    callback is usually described rather than shown, and the description omits
    the part that matters -- how many epochs of no progress you pay before each
    reduction, and whether the reduction then buys anything.
"""

from __future__ import annotations

import functools
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 6000
EPOCHS = 40
BATCH = 128


def _model(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(256, activation="relu"),
        keras.layers.Dense(256, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _batch_history() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)

    model = _model()
    loss_fn = keras.losses.SparseCategoricalCrossentropy()

    class RecordBatches(keras.callbacks.Callback):
        """logs['loss'] mid-epoch is a running average, not this batch's loss.

        Record both, so the difference is visible instead of assumed.
        """

        def __init__(self):
            super().__init__()
            self.running = []
            self.actual = []
            self.epoch_losses = []

        def on_train_batch_end(self, batch, logs=None):
            self.running.append(float(logs["loss"]))
            start = batch * BATCH
            rows = data["x_train"][start:start + BATCH]
            labels = data["y_train"][start:start + BATCH]
            if len(rows):
                self.actual.append(float(loss_fn(
                    labels, model(rows, training=False)).numpy()))
            else:
                self.actual.append(float("nan"))

        def on_epoch_end(self, epoch, logs=None):
            self.epoch_losses.append(float(logs["loss"]))

    recorder = RecordBatches()
    model.fit(data["x_train"], data["y_train"], epochs=10, batch_size=BATCH,
              verbose=0, callbacks=[recorder])
    return {"running": recorder.running, "actual": recorder.actual,
            "epoch": recorder.epoch_losses,
            "steps": int(np.ceil(LIMIT / BATCH))}


def batch_vs_epoch(fig, axes, p: Palette) -> None:
    info = _batch_history()
    ax = fig.subplots(1, 1)
    steps = info["steps"]
    actual = np.array(info["actual"])
    running = np.array(info["running"])
    x = np.arange(1, len(actual) + 1) / steps

    ax.plot(x, actual, lw=0.9, color=p.muted, alpha=0.85,
            label=f"the loss on each of {len(actual)} batches")
    ax.plot(x, running, lw=1.6, color=p.amber,
            label="what logs['loss'] reports: a running epoch average")
    epoch_x = np.arange(1, len(info["epoch"]) + 1)
    ax.plot(epoch_x, info["epoch"], "o", ms=7, color=p.blue,
            label="the epoch value Keras prints")
    last_epoch = actual[-steps:]
    ax.annotate(f"final epoch: batches span "
                f"{last_epoch.min():.4f} to {last_epoch.max():.4f}\n"
                f"reported average {info['epoch'][-1]:.4f}",
                (len(info["epoch"]), info["epoch"][-1]),
                textcoords="offset points", xytext=(-14, 44), ha="right",
                fontsize=8, color=p.green,
                arrowprops=dict(arrowstyle="->", color=p.green, lw=1.0))
    ax.set_xlabel("epoch")
    ax.set_ylabel("training loss")
    ax.set_yscale("log")
    ax.set_title("Three different numbers, all called 'the loss'",
                 fontsize=10.5)
    ax.legend(fontsize=8)


@functools.lru_cache(maxsize=1)
def _policies() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    fit = dict(epochs=EPOCHS, batch_size=BATCH, verbose=0,
               validation_data=(data["x_test"], data["y_test"]))
    directory = tempfile.mkdtemp(prefix="pch-callbacks-")
    checkpoint_path = os.path.join(directory, "best.keras")
    out = {}

    def run(label, callbacks, restore_from=None):
        model = _model()
        history = model.fit(data["x_train"], data["y_train"],
                            callbacks=callbacks, **fit)
        if restore_from:
            model = keras.models.load_model(restore_from)
        loss, accuracy = model.evaluate(data["x_test"], data["y_test"],
                                        verbose=0)
        out[label] = {
            "accuracy": float(accuracy),
            "loss": float(loss),
            "epochs": len(history.history["loss"]),
            "val_loss": [float(v) for v in history.history["val_loss"]],
        }

    run(f"{EPOCHS} fixed\nepochs", [])
    run("EarlyStopping\npatience 5", [keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True)])
    run("ModelCheckpoint\nsave_best_only", [keras.callbacks.ModelCheckpoint(
        checkpoint_path, monitor="val_loss", save_best_only=True)],
        restore_from=checkpoint_path)
    run("ReduceLROnPlateau\nfactor 0.5", [keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5)])
    return out


def callback_policies(fig, axes, p: Palette) -> None:
    runs = _policies()
    left, right = fig.subplots(1, 2)
    for (label, info), color in zip(runs.items(), p.cycle):
        epochs = range(1, len(info["val_loss"]) + 1)
        left.plot(epochs, info["val_loss"], lw=1.8, color=color,
                  label=label.replace("\n", " "))
    left.set_xlabel("epoch")
    left.set_ylabel("validation loss")
    left.set_title("validation loss per policy", fontsize=10)
    left.legend(fontsize=7.5)

    labels = list(runs)
    accuracies = [runs[k]["accuracy"] for k in labels]
    positions = np.arange(len(labels))
    best = max(accuracies)
    right.bar(positions, accuracies, 0.55,
              color=[p.green if abs(a - best) < 1e-9 else p.blue
                     for a in accuracies])
    for x, key in zip(positions, labels):
        info = runs[key]
        right.annotate(f"{info['accuracy']:.4f}\n{info['epochs']} epochs",
                       (x, info["accuracy"]), textcoords="offset points",
                       xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(labels, fontsize=7.5)
    right.set_ylim(0, max(accuracies) * 1.25)
    right.set_ylabel("test accuracy")
    right.set_title("test accuracy and epochs spent", fontsize=10)


@functools.lru_cache(maxsize=1)
def _plateau() -> dict:
    keras = tf().keras
    data = dataset("mnist", limit=LIMIT, flat=True)
    out = {}
    for label, callbacks in (
            ("fixed 1e-3", []),
            ("ReduceLROnPlateau", [keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.3, patience=3, min_lr=1e-6)])):
        model = _model(0)
        rates = []

        class Recorder(keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                rates.append(float(
                    keras.ops.convert_to_numpy(
                        self.model.optimizer.learning_rate)))

        history = model.fit(
            data["x_train"], data["y_train"], epochs=EPOCHS, batch_size=128,
            verbose=0, validation_data=(data["x_test"], data["y_test"]),
            callbacks=callbacks + [Recorder()])
        out[label] = {
            "val_loss": [float(v) for v in history.history["val_loss"]],
            "val_accuracy": [float(v)
                             for v in history.history["val_accuracy"]],
            "rates": rates,
            "final": float(history.history["val_accuracy"][-1]),
            "best": float(max(history.history["val_accuracy"])),
        }
    plateau = out["ReduceLROnPlateau"]["rates"]
    cuts = [index + 1 for index in range(1, len(plateau))
            if plateau[index] < plateau[index - 1] - 1e-12]
    return {"runs": out, "cuts": cuts}


def plateau_trace(fig, axes, p: Palette) -> None:
    info = _plateau()
    runs = info["runs"]
    top, bottom = fig.subplots(2, 1, height_ratios=(1.5, 1.0), sharex=True)
    epochs = np.arange(1, len(runs["fixed 1e-3"]["val_loss"]) + 1)
    top.plot(epochs, runs["fixed 1e-3"]["val_loss"], color=p.muted, lw=1.5,
             label=f"fixed 1e-3 (best {runs['fixed 1e-3']['best']:.4f})")
    top.plot(epochs, runs["ReduceLROnPlateau"]["val_loss"], color=p.blue,
             lw=1.5,
             label=f"ReduceLROnPlateau "
                   f"(best {runs['ReduceLROnPlateau']['best']:.4f})")
    for cut in info["cuts"]:
        top.axvline(cut, color=p.amber, lw=1.0, ls="--", alpha=0.8)
    top.set_ylabel("validation loss")
    top.set_title(f"MNIST, {LIMIT:,} rows, {EPOCHS} epochs — dashed lines are "
                  f"the {len(info['cuts'])} reductions", fontsize=10)
    top.legend(fontsize=8, loc="upper right")

    bottom.step(epochs, runs["ReduceLROnPlateau"]["rates"], where="post",
                color=p.blue, lw=1.8)
    bottom.axhline(1e-3, color=p.muted, lw=1.2, ls=":", label="fixed 1e-3")
    bottom.set_yscale("log")
    bottom.set_xlabel("epoch")
    bottom.set_ylabel("learning rate")
    bottom.legend(fontsize=8, loc="upper right")


FIGURES = [
    figure("batch-vs-epoch", batch_vs_epoch, size=(8.2, 3.6), axes=False),
    figure("plateau-trace", plateau_trace, size=(8.4, 4.8), axes=False),
    figure("callback-policies", callback_policies, size=(9.4, 3.6), axes=False),
]


if __name__ == "__main__":
    info = _plateau()
    print("=== ReduceLROnPlateau, factor 0.3, patience 3 ===")
    for label, run in info["runs"].items():
        print(f"{label:20s} best {run['best']:.4f}  final {run['final']:.4f}  "
              f"last lr {run['rates'][-1]:.2e}")
    print(f"reductions fired on epochs: {info['cuts']}")
    print()

    info = _batch_history()
    actual = np.array(info["actual"])
    running = np.array(info["running"])
    steps = info["steps"]
    print(f"=== {len(actual)} batches over {len(info['epoch'])} epochs "
          f"({steps} steps per epoch) ===")
    print(f"{'epoch':>6} {'printed':>9} {'batch min':>10} {'batch max':>10} "
          f"{'batch sd':>9} {'running mid-epoch':>18}")
    for index, reported in enumerate(info["epoch"]):
        window = actual[index * steps:(index + 1) * steps]
        mid = running[index * steps + steps // 2]
        print(f"{index + 1:6d} {reported:9.4f} {window.min():10.4f} "
              f"{window.max():10.4f} {window.std(ddof=1):9.4f} {mid:18.4f}")
    print("logs['loss'] inside on_train_batch_end is the running average of the")
    print("epoch so far, not the loss on the batch that just finished")

    print("\n=== callback policies ===")
    print(f"{'policy':28s} {'epochs':>7} {'test acc':>9} {'test loss':>10}")
    for label, run in _policies().items():
        print(f"{label.replace(chr(10), ' '):28s} {run['epochs']:7d} "
              f"{run['accuracy']:9.4f} {run['loss']:10.4f}")

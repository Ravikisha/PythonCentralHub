"""Figures for *Regularization & Dropout*.

``capacity-and-dropout``
    Two regularisers on the same over-parameterised network: making it smaller,
    and dropping half its units. Validation loss curves, so the turning point is
    visible rather than asserted.

``l2-weights``
    What L2 actually does to the weights — a distribution, not a score — next to
    the validation loss it buys.

``mc-dropout``
    Keeping dropout on at prediction time and sampling 100 forward passes. The
    spread across samples is a usable uncertainty signal.
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

LIMIT = 6000
EPOCHS = 30
WIDTHS = (16, 64, 512)
DROPOUTS = (0.0, 0.2, 0.5, 0.7)
PENALTIES = (0.0, 1e-5, 1e-4, 1e-3, 1e-2)


def _model(width: int = 512, dropout: float = 0.0, penalty: float = 0.0,
           seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    regulariser = keras.regularizers.l2(penalty) if penalty else None
    layers = [keras.layers.Input((784,))]
    for _ in range(2):
        layers.append(keras.layers.Dense(width, activation="relu",
                                         kernel_regularizer=regulariser))
        if dropout:
            layers.append(keras.layers.Dropout(dropout))
    layers.append(keras.layers.Dense(10, activation="softmax"))
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def _fit(model) -> dict:
    data = dataset("fashion", limit=LIMIT, flat=True)
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {key: [float(v) for v in values]
            for key, values in history.history.items()}


@functools.lru_cache(maxsize=1)
def _width_runs() -> dict:
    return {width: _fit(_model(width=width)) for width in WIDTHS}


@functools.lru_cache(maxsize=1)
def _dropout_runs() -> dict:
    return {rate: _fit(_model(dropout=rate)) for rate in DROPOUTS}


@functools.lru_cache(maxsize=1)
def _penalty_runs() -> dict:
    # Keras adds the regularisation term to the reported val_loss, so comparing
    # val_loss across penalties compares different quantities. Recompute the
    # plain cross-entropy from the predictions instead.
    data = dataset("fashion", limit=LIMIT, flat=True)
    out = {}
    for penalty in PENALTIES:
        model = _model(penalty=penalty)
        history = _fit(model)
        probabilities = model.predict(data["x_test"], verbose=0)
        rows = np.arange(len(data["y_test"]))
        pure = float(np.mean(-np.log(np.clip(
            probabilities[rows, data["y_test"]], 1e-12, None))))
        kernels = np.concatenate([w.numpy().ravel()
                                  for w in model.trainable_weights
                                  if w.numpy().ndim == 2])
        out[penalty] = {"history": history,
                        "pure_ce": pure,
                        "abs_mean": float(np.abs(kernels).mean()),
                        "abs_max": float(np.abs(kernels).max()),
                        "kernels": kernels}
    return out


@functools.lru_cache(maxsize=1)
def _mc_dropout() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=True)
    model = _model(dropout=0.5)
    model.fit(data["x_train"], data["y_train"], epochs=EPOCHS, batch_size=128,
              verbose=0)
    x_test, y_test = data["x_test"], data["y_test"]

    deterministic = model.predict(x_test, verbose=0)
    samples = np.stack([model(x_test, training=True).numpy() for _ in range(100)])
    averaged = samples.mean(axis=0)
    spread = samples.std(axis=0)[np.arange(len(y_test)),
                                averaged.argmax(axis=1)]
    correct = averaged.argmax(axis=1) == y_test
    running = [float((samples[:n].mean(axis=0).argmax(axis=1) == y_test).mean())
               for n in (1, 2, 5, 10, 25, 50, 100)]
    return {
        "deterministic_accuracy": float((deterministic.argmax(axis=1) == y_test).mean()),
        "mc_accuracy": float(correct.mean()),
        "spread_correct": spread[correct],
        "spread_wrong": spread[~correct],
        "running": running,
        "counts": (1, 2, 5, 10, 25, 50, 100),
    }


def capacity_and_dropout(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for (width, run), color in zip(_width_runs().items(), p.cycle):
        best = min(run["val_loss"])
        left.plot(epochs, run["val_loss"], lw=1.8, color=color,
                  label=f"{width} units — best {best:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation loss")
    left.set_title("regularise by using fewer parameters", fontsize=10)
    left.legend(fontsize=8)

    for (rate, run), color in zip(_dropout_runs().items(), p.cycle):
        best = min(run["val_loss"])
        right.plot(epochs, run["val_loss"], lw=1.8, color=color,
                   label=f"dropout {rate:g} — best {best:.4f}")
    right.set_xlabel("epoch")
    right.set_ylabel("validation loss")
    right.set_title("regularise by dropping units (512 wide)", fontsize=10)
    right.legend(fontsize=8)


def l2_weights(fig, axes, p: Palette) -> None:
    runs = _penalty_runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    for (penalty, info), color in zip(runs.items(), p.cycle):
        label = "none" if penalty == 0 else f"{penalty:g}"
        left.plot(epochs, info["history"]["val_accuracy"], lw=1.8, color=color,
                  label=f"L2 {label} — final {info['history']['val_accuracy'][-1]:.4f}"
                        f", CE {info['pure_ce']:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_ylim(0.7, 0.9)
    left.set_title("what the penalty buys (accuracy, not Keras' val_loss)",
                   fontsize=10)
    left.legend(fontsize=7)

    for (penalty, info), color in zip(runs.items(), p.cycle):
        if penalty not in (0.0, 1e-4, 1e-2):
            continue
        label = "none" if penalty == 0 else f"{penalty:g}"
        right.hist(info["kernels"], bins=140, range=(-0.25, 0.25),
                   histtype="step", lw=1.8, color=color, density=True,
                   label=f"L2 {label} — mean |w| {info['abs_mean']:.4f}")
    right.set_xlabel("weight value")
    right.set_ylabel("density")
    right.set_yscale("log")
    right.set_title("what the penalty does to the weights", fontsize=10)
    right.legend(fontsize=7.5)


def mc_dropout(fig, axes, p: Palette) -> None:
    info = _mc_dropout()
    left, right = fig.subplots(1, 2)

    bins = np.linspace(0, 0.35, 30)
    left.hist(info["spread_correct"], bins=bins, color=p.green, alpha=0.7,
              density=True,
              label=f"correct — mean {info['spread_correct'].mean():.4f}")
    left.hist(info["spread_wrong"], bins=bins, color=p.red, alpha=0.7,
              density=True,
              label=f"wrong — mean {info['spread_wrong'].mean():.4f}")
    left.set_xlabel("standard deviation of the winning class across 100 passes")
    left.set_ylabel("density")
    left.set_title("disagreement is higher where the model is wrong",
                   fontsize=10)
    left.legend(fontsize=8)

    right.plot(info["counts"], info["running"], "o-", ms=5, lw=2.0,
               color=p.blue, label="averaged over N stochastic passes")
    right.axhline(info["deterministic_accuracy"], color=p.amber, lw=1.8,
                  ls="--",
                  label=f"one deterministic pass — "
                        f"{info['deterministic_accuracy']:.4f}")
    right.set_xscale("log")
    right.set_xticks(list(info["counts"]))
    right.set_xticklabels([str(c) for c in info["counts"]])
    right.set_xlabel("number of stochastic forward passes")
    right.set_ylabel("test accuracy")
    right.set_title("MC dropout against ordinary prediction", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("capacity-and-dropout", capacity_and_dropout, size=(9.4, 3.6),
           axes=False),
    figure("l2-weights", l2_weights, size=(9.4, 3.6), axes=False),
    figure("mc-dropout", mc_dropout, size=(9.4, 3.6), axes=False),
]


if __name__ == "__main__":
    print(f"=== Fashion-MNIST {LIMIT} rows, 2 hidden layers, Adam 1e-3, "
          f"{EPOCHS} epochs ===")
    print("\nmodel width:")
    for width, run in _width_runs().items():
        best = int(np.argmin(run["val_loss"])) + 1
        print(f"  {width:4d} units  best val loss {min(run['val_loss']):.4f} "
              f"at epoch {best:2d}  final {run['val_loss'][-1]:.4f}  "
              f"val acc {run['val_accuracy'][-1]:.4f}")

    print("\ndropout rate (512 units):")
    for rate, run in _dropout_runs().items():
        best = int(np.argmin(run["val_loss"])) + 1
        print(f"  {rate:.1f}  best val loss {min(run['val_loss']):.4f} at epoch "
              f"{best:2d}  final {run['val_loss'][-1]:.4f}  "
              f"val acc {run['val_accuracy'][-1]:.4f}  "
              f"train acc {run['accuracy'][-1]:.4f}")

    print("\nL2 penalty (512 units) — Keras' val_loss includes the penalty")
    print("term, so the plain cross-entropy is recomputed from predictions:")
    for penalty, info in _penalty_runs().items():
        history = info["history"]
        print(f"  {penalty:g}  keras val_loss {history['val_loss'][-1]:.4f}  "
              f"pure CE {info['pure_ce']:.4f}  "
              f"val acc {history['val_accuracy'][-1]:.4f}  "
              f"mean |w| {info['abs_mean']:.4f}  max |w| {info['abs_max']:.4f}")

    print("\nMC dropout:")
    info = _mc_dropout()
    print(f"  one deterministic pass: {info['deterministic_accuracy']:.4f}")
    print(f"  100 stochastic passes averaged: {info['mc_accuracy']:.4f}")
    for count, accuracy in zip(info["counts"], info["running"]):
        print(f"    {count:3d} passes -> {accuracy:.4f}")
    print(f"  spread when correct {info['spread_correct'].mean():.4f}  "
          f"when wrong {info['spread_wrong'].mean():.4f}")

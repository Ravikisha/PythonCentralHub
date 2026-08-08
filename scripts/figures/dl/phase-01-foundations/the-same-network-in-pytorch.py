"""Figures for *The Same Network in PyTorch*.

Every other page in this module is Keras. This one builds the identical
network in both frameworks, gives them identical weights, and measures where
they agree and where they do not -- which turns "the frameworks are basically
the same" from a claim into a number.

``agreement``
    Forward outputs, loss and every gradient tensor compared between Keras and
    PyTorch on identical weights and identical input. The bars are absolute
    differences, and the interesting part is which ones are not zero.

``training-parity``
    Both frameworks training the same architecture from the same initial
    weights on the same data, for the same epochs: loss curves, final accuracy
    and wall clock.

``defaults``
    The differences that are not numerical at all -- default initialisers,
    default optimiser hyper-parameters and default reduction -- each measured
    by the gap it opens on an otherwise identical run.
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

LIMIT = 12000
EPOCHS = 8
BATCH = 128
HIDDEN = 128
SEEDS = (0, 1, 2)


def torch():
    import torch as _torch
    return _torch


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _keras_model(hidden: int = HIDDEN):
    keras = tf().keras
    return keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(hidden, activation="relu"),
        keras.layers.Dense(10),
    ])


def _torch_model(hidden: int = HIDDEN):
    nn = torch().nn
    return nn.Sequential(nn.Linear(784, hidden), nn.ReLU(),
                         nn.Linear(hidden, 10))


def _copy_into_torch(keras_model, torch_model):
    """Keras stores Dense kernels as (in, out); torch stores them as (out, in)."""
    t = torch()
    weights = keras_model.get_weights()
    with t.no_grad():
        torch_model[0].weight.copy_(t.tensor(weights[0].T))
        torch_model[0].bias.copy_(t.tensor(weights[1]))
        torch_model[2].weight.copy_(t.tensor(weights[2].T))
        torch_model[2].bias.copy_(t.tensor(weights[3]))


@functools.lru_cache(maxsize=1)
def _agreement() -> dict:
    """One forward pass, one loss and one backward pass in both frameworks."""
    t = torch()
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    x = data["x_train"][:256].astype("float32")
    y = data["y_train"][:256].astype("int64")

    seed_everything(0)
    keras_model = _keras_model()
    keras_model.build((None, 784))
    torch_model = _torch_model()
    _copy_into_torch(keras_model, torch_model)

    with tensorflow.GradientTape() as tape:
        keras_logits = keras_model(x, training=True)
        keras_loss = tensorflow.reduce_mean(
            keras.losses.sparse_categorical_crossentropy(
                y, keras_logits, from_logits=True))
    keras_grads = tape.gradient(keras_loss, keras_model.trainable_variables)

    torch_logits = torch_model(t.tensor(x))
    torch_loss = t.nn.functional.cross_entropy(torch_logits, t.tensor(y))
    torch_loss.backward()

    keras_grad_arrays = [np.asarray(g) for g in keras_grads]
    torch_grad_arrays = [
        torch_model[0].weight.grad.numpy().T,
        torch_model[0].bias.grad.numpy(),
        torch_model[2].weight.grad.numpy().T,
        torch_model[2].bias.grad.numpy(),
    ]

    rows = [
        ("forward logits", float(np.abs(
            np.asarray(keras_logits) - torch_logits.detach().numpy()).max())),
        ("loss", float(abs(float(keras_loss) - float(torch_loss)))),
        ("grad: layer 1 weight", float(np.abs(
            keras_grad_arrays[0] - torch_grad_arrays[0]).max())),
        ("grad: layer 1 bias", float(np.abs(
            keras_grad_arrays[1] - torch_grad_arrays[1]).max())),
        ("grad: layer 2 weight", float(np.abs(
            keras_grad_arrays[2] - torch_grad_arrays[2]).max())),
        ("grad: layer 2 bias", float(np.abs(
            keras_grad_arrays[3] - torch_grad_arrays[3]).max())),
    ]
    scale = float(np.abs(keras_grad_arrays[0]).max())
    return {"rows": rows, "gradient_scale": scale,
            "parameters": int(keras_model.count_params()),
            "torch_parameters": int(sum(p.numel()
                                        for p in torch_model.parameters()))}


def _accuracy(logits, labels) -> float:
    return float((np.asarray(logits).argmax(axis=1) == labels).mean())


@functools.lru_cache(maxsize=1)
def _training_parity() -> dict:
    """Train both from identical initial weights, same batches, same epochs."""
    t = torch()
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    x, y = data["x_train"].astype("float32"), data["y_train"].astype("int64")
    xt, yt = data["x_test"].astype("float32"), data["y_test"].astype("int64")

    out = {"keras": [], "torch": []}
    for seed in SEEDS:
        seed_everything(seed)
        keras_model = _keras_model()
        keras_model.build((None, 784))
        torch_model = _torch_model()
        _copy_into_torch(keras_model, torch_model)

        keras_model.compile(keras.optimizers.SGD(0.1),
                            keras.losses.SparseCategoricalCrossentropy(
                                from_logits=True),
                            metrics=["accuracy"])
        started = time.perf_counter()
        history = keras_model.fit(x, y, epochs=EPOCHS, batch_size=BATCH,
                                  shuffle=False, verbose=0)
        keras_seconds = time.perf_counter() - started
        out["keras"].append({
            "loss": [float(v) for v in history.history["loss"]],
            "accuracy": _accuracy(keras_model.predict(xt, verbose=0), yt),
            "seconds": keras_seconds})

        optimiser = t.optim.SGD(torch_model.parameters(), lr=0.1)
        losses = []
        started = time.perf_counter()
        for _ in range(EPOCHS):
            running, batches = 0.0, 0
            for index in range(0, len(x), BATCH):
                batch_x = t.tensor(x[index:index + BATCH])
                batch_y = t.tensor(y[index:index + BATCH])
                optimiser.zero_grad()
                loss = t.nn.functional.cross_entropy(
                    torch_model(batch_x), batch_y)
                loss.backward()
                optimiser.step()
                running += float(loss)
                batches += 1
            losses.append(running / batches)
        torch_seconds = time.perf_counter() - started
        with t.no_grad():
            predictions = torch_model(t.tensor(xt)).numpy()
        out["torch"].append({"loss": losses,
                             "accuracy": _accuracy(predictions, yt),
                             "seconds": torch_seconds})

    summary = {}
    for name in ("keras", "torch"):
        runs = out[name]
        summary[name] = {
            "loss": np.mean([run["loss"] for run in runs], axis=0).tolist(),
            "accuracy": float(np.mean([run["accuracy"] for run in runs])),
            "spread": float(np.max([run["accuracy"] for run in runs])
                            - np.min([run["accuracy"] for run in runs])),
            "seconds": float(np.mean([run["seconds"] for run in runs])),
        }
    summary["final_gap"] = abs(summary["keras"]["loss"][-1]
                               - summary["torch"]["loss"][-1])
    summary["accuracy_gap"] = abs(summary["keras"]["accuracy"]
                                  - summary["torch"]["accuracy"])
    return summary


@functools.lru_cache(maxsize=1)
def _defaults() -> dict:
    """Where the frameworks disagree before you have written any code."""
    t = torch()
    keras = tf().keras

    # 1. Default initialiser spread on an identical layer shape.
    seed_everything(0)
    keras_layer = keras.layers.Dense(HIDDEN)
    keras_layer.build((None, 784))
    keras_weights = np.asarray(keras_layer.get_weights()[0])
    torch_layer = t.nn.Linear(784, HIDDEN)
    torch_weights = torch_layer.weight.detach().numpy()

    # 2. Default optimiser hyper-parameters.
    keras_adam = keras.optimizers.Adam()
    torch_adam = t.optim.Adam([t.nn.Parameter(t.zeros(1))])
    torch_defaults = torch_adam.param_groups[0]

    # 3. Default bias: Keras zeros it, torch draws it from a uniform range.
    keras_bias = np.asarray(keras_layer.get_weights()[1])
    torch_bias = torch_layer.bias.detach().numpy()

    return {
        "init": {
            "Keras Dense": {"sd": float(keras_weights.std()),
                            "max": float(np.abs(keras_weights).max()),
                            "name": "glorot_uniform"},
            "torch Linear": {"sd": float(torch_weights.std()),
                             "max": float(np.abs(torch_weights).max()),
                             "name": "kaiming_uniform(a=sqrt(5))"},
        },
        "adam": {
            "learning_rate": (float(keras_adam.learning_rate),
                              float(torch_defaults["lr"])),
            "epsilon": (float(keras_adam.epsilon),
                        float(torch_defaults["eps"])),
            "beta_1": (float(keras_adam.beta_1),
                       float(torch_defaults["betas"][0])),
        },
        "bias": {"Keras": float(np.abs(keras_bias).max()),
                 "torch": float(np.abs(torch_bias).max())},
        "init_ratio": float(torch_weights.std() / keras_weights.std()),
    }


def agreement(fig, axes, p: Palette) -> None:
    info = _agreement()
    ax = fig.subplots(1, 1)
    labels = [row[0] for row in info["rows"]]
    values = [row[1] for row in info["rows"]]
    floor = 1e-12
    positions = np.arange(len(labels))
    ax.barh(positions, [max(value, floor) for value in values],
            color=p.green, height=0.6)
    for position, value in zip(positions, values):
        ax.annotate(f"{value:.2e}", (max(value, floor), position),
                    xytext=(5, 0), textcoords="offset points", fontsize=8,
                    color=p.fg, va="center")
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xscale("log")
    ax.set_xlim(floor, 1e-3)
    ax.axvline(1e-6, color=p.amber, lw=1.2, ls="--")
    ax.annotate("1e-6", (1e-6, len(positions) - 0.4), xytext=(4, 0),
                textcoords="offset points", fontsize=8, color=p.amber,
                va="center")
    ax.set_xlabel("largest absolute difference, Keras against PyTorch")
    ax.set_title(f"identical weights, identical 256-row batch — gradients "
                 f"themselves reach {info['gradient_scale']:.3f}", fontsize=10)
    ax.invert_yaxis()


def training_parity(fig, axes, p: Palette) -> None:
    info = _training_parity()
    left, right = fig.subplots(1, 2, width_ratios=(1.25, 1.0))
    epochs = np.arange(1, EPOCHS + 1)
    left.plot(epochs, info["keras"]["loss"], "o-", color=p.blue, lw=1.8, ms=5,
              label=f"Keras (final {info['keras']['loss'][-1]:.4f})")
    left.plot(epochs, info["torch"]["loss"], "o--", color=p.amber, lw=1.8,
              ms=5, label=f"PyTorch (final {info['torch']['loss'][-1]:.4f})")
    left.set_xlabel("epoch")
    left.set_ylabel("training loss")
    left.set_title(f"same initial weights, same batch order, "
                   f"{len(SEEDS)} seeds", fontsize=10)
    left.legend(fontsize=8)

    names = ["Keras", "PyTorch"]
    positions = np.arange(2)
    accuracies = [info["keras"]["accuracy"], info["torch"]["accuracy"]]
    seconds = [info["keras"]["seconds"], info["torch"]["seconds"]]
    width = 0.36
    right.bar(positions - width / 2, accuracies, width * 0.9, color=p.green,
              label="test accuracy")
    for position, value in zip(positions - width / 2, accuracies):
        right.annotate(f"{value:.4f}", (position, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_ylim(0, 1.15)
    right.set_ylabel("test accuracy")
    twin = right.twinx()
    twin.bar(positions + width / 2, seconds, width * 0.9, color=p.purple,
             label="seconds")
    for position, value in zip(positions + width / 2, seconds):
        twin.annotate(f"{value:.1f}s", (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=8,
                      color=p.fg)
    twin.set_ylabel(f"seconds for {EPOCHS} epochs")
    right.set_xticks(positions)
    right.set_xticklabels(names)
    right.set_title(f"accuracy gap {info['accuracy_gap']:.4f}", fontsize=10)


def defaults(fig, axes, p: Palette) -> None:
    info = _defaults()
    left, right = fig.subplots(1, 2)
    names = list(info["init"])
    positions = np.arange(len(names))
    sds = [info["init"][name]["sd"] for name in names]
    left.bar(positions, sds, color=(p.blue, p.amber), width=0.55)
    for position, name, value in zip(positions, names, sds):
        left.annotate(f"{value:.5f}\n{info['init'][name]['name']}",
                      (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(names, fontsize=9)
    left.set_ylabel("standard deviation of the initial weights")
    left.set_ylim(0, max(sds) * 1.35)
    left.set_title(f"784 -> {HIDDEN}, default initialiser — torch starts "
                   f"at {info['init_ratio']:.2f}x the spread", fontsize=9.5)

    keys = list(info["adam"])
    positions = np.arange(len(keys))
    keras_values = [info["adam"][key][0] for key in keys]
    torch_values = [info["adam"][key][1] for key in keys]
    width = 0.36
    right.bar(positions - width / 2, keras_values, width * 0.9, color=p.blue,
              label="Keras")
    right.bar(positions + width / 2, torch_values, width * 0.9, color=p.amber,
              label="PyTorch")
    for position, value in zip(positions - width / 2, keras_values):
        right.annotate(f"{value:g}", (position, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    for position, value in zip(positions + width / 2, torch_values):
        right.annotate(f"{value:g}", (position, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    right.set_yscale("log")
    right.set_xticks(positions)
    right.set_xticklabels(keys, fontsize=8.5)
    right.set_ylabel("default value (log scale)")
    right.set_title("Adam, straight out of the box", fontsize=9.5)
    right.legend(fontsize=8)


FIGURES = [
    figure("agreement", agreement, size=(8.6, 4.0), axes=False),
    figure("training-parity", training_parity, size=(9.4, 4.0), axes=False),
    figure("defaults", defaults, size=(9.2, 4.2), axes=False),
]


if __name__ == "__main__":
    info = _agreement()
    print("=== same weights, same batch ===")
    for label, value in info["rows"]:
        print(f"{label:24s} {value:.3e}")
    print(f"gradients themselves reach {info['gradient_scale']:.4f}")
    print(f"parameters: Keras {info['parameters']:,}, "
          f"torch {info['torch_parameters']:,}")

    parity = _training_parity()
    print(f"\n=== training parity, {EPOCHS} epochs, {len(SEEDS)} seeds ===")
    for name in ("keras", "torch"):
        run = parity[name]
        print(f"{name:8s} final loss {run['loss'][-1]:.4f}  "
              f"accuracy {run['accuracy']:.4f} (spread {run['spread']:.4f})  "
              f"{run['seconds']:.1f}s")
    print(f"final loss gap {parity['final_gap']:.6f}, "
          f"accuracy gap {parity['accuracy_gap']:.4f}")

    defaults_info = _defaults()
    print("\n=== the defaults you did not choose ===")
    for name, entry in defaults_info["init"].items():
        print(f"{name:14s} sd {entry['sd']:.5f}  max {entry['max']:.5f}  "
              f"{entry['name']}")
    print(f"torch initial weights have "
          f"{defaults_info['init_ratio']:.2f}x the spread of Keras's")
    for key, (keras_value, torch_value) in defaults_info["adam"].items():
        print(f"Adam {key:16s} Keras {keras_value:<12g} "
              f"torch {torch_value:g}")
    print(f"bias at init: Keras max {defaults_info['bias']['Keras']:.5f}, "
          f"torch max {defaults_info['bias']['torch']:.5f}")

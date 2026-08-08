"""Figures for *Building Neural Networks with Keras (Sequential and Functional)*.

``early-stopping``
    300 epochs of validation loss on the house-price data, with the best epoch
    and the epoch each EarlyStopping patience would have fired on marked. The
    picture behind "patience is a bet on how long a plateau lasts".

``training-policies``
    Test MAE for four training policies on the identical model: fixed epochs,
    two patiences, and with or without ``restore_best_weights``.

``api-equivalence``
    The same architecture built three ways -- Sequential, Functional and a
    Model subclass -- given identical weights and run on identical input. The
    figure is the difference between their outputs, which is the point: the
    APIs are a notation choice, not a modelling one. The second panel is the
    thing Sequential genuinely cannot express.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPOCHS = 300
SPLIT = 320                      # 320 train / 84 validation of the 404 rows
POLICIES = ((20, False), (20, True), (50, True))


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    (x_train, y_train), (x_test, y_test) = \
        tf().keras.datasets.boston_housing.load_data()
    mean, std = x_train.mean(axis=0), x_train.std(axis=0)
    return {"x": (x_train - mean) / std, "y": y_train,
            "x_test": (x_test - mean) / std, "y_test": y_test}


def _model():
    keras = tf().keras
    model = keras.Sequential([
        keras.layers.Input((13,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(1),
    ])
    model.compile("rmsprop", "mse", metrics=["mae"])
    return model


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    keras = tf().keras
    data = _data()
    fit = dict(epochs=EPOCHS, batch_size=16, verbose=0,
               validation_data=(data["x"][SPLIT:], data["y"][SPLIT:]))

    seed_everything(0)
    model = _model()
    history = model.fit(data["x"][:SPLIT], data["y"][:SPLIT], **fit)
    out = {
        "val_loss": [float(v) for v in history.history["val_loss"]],
        "policies": {"300 fixed\nepochs":
                     float(model.evaluate(data["x_test"], data["y_test"],
                                          verbose=0)[1])},
        "stopped": {},
    }

    for patience, restore in POLICIES:
        seed_everything(0)
        model = _model()
        stop = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience,
            restore_best_weights=restore)
        run = model.fit(data["x"][:SPLIT], data["y"][:SPLIT],
                        callbacks=[stop], **fit)
        label = f"patience {patience}\nrestore={restore}"
        out["policies"][label] = float(model.evaluate(
            data["x_test"], data["y_test"], verbose=0)[1])
        out["stopped"][(patience, restore)] = len(run.history["loss"])
    return out


def early_stopping(fig, axes, p: Palette) -> None:
    runs = _runs()
    full, zoom = fig.subplots(1, 2)
    curve = runs["val_loss"]
    epochs = np.arange(1, len(curve) + 1)
    best = int(np.argmin(curve)) + 1

    full.plot(epochs, curve, lw=1.2, color=p.blue)
    full.set_yscale("log")
    full.set_xlabel("epoch")
    full.set_ylabel("validation loss, MSE (log scale)")
    full.set_title(f"all {len(curve)} epochs", fontsize=10)
    full.axvspan(100, len(curve), color=p.amber, alpha=0.12)
    full.annotate("the region on the right", (200, max(curve) * 0.5),
                  ha="center", fontsize=8, color=p.amber)

    # Everything that matters happens in a band 0.5 MSE wide, so the second
    # panel is the same curve with the first 100 epochs cut away. On a
    # shrunken smoke run there are fewer than 100 epochs to cut, so the
    # start is clamped rather than letting the slice come back empty.
    start = min(99, max(len(curve) - 2, 0))
    zoom.plot(epochs[start:], curve[start:], lw=1.2, color=p.blue,
              label="validation loss")
    zoom.axvline(best, color=p.green, lw=1.8, ls="--",
                 label=f"best epoch {best} — loss {min(curve):.4f}")
    for (patience, restore), stopped in runs["stopped"].items():
        if not restore:
            continue
        zoom.axvline(stopped, color=p.amber if patience == 20 else p.red,
                     lw=1.6, ls=":",
                     label=f"patience {patience} stops at epoch {stopped}")
    zoom.scatter([len(curve)], [curve[-1]], s=40, color=p.fg, zorder=5)
    zoom.annotate(f"epoch {len(curve)}: {curve[-1]:.4f}",
                  (len(curve), curve[-1]), textcoords="offset points",
                  xytext=(-10, 14), ha="right", fontsize=8, color=p.fg)
    zoom.set_xlabel("epoch")
    zoom.set_ylabel("validation loss (MSE)")
    zoom.set_ylim(min(curve) - 0.15,
                  np.percentile(curve[start:], 99) + 0.2)
    zoom.set_title("epochs 100-300, where the decision is made", fontsize=10)
    zoom.legend(fontsize=7.5)


def training_policies(fig, axes, p: Palette) -> None:
    results = _runs()["policies"]
    ax = fig.subplots(1, 1)
    labels = list(results)
    values = [results[k] for k in labels]
    positions = np.arange(len(labels))
    # Two policies restore the same epoch-207 weights, so they tie exactly.
    # Colouring only argmin would hide that.
    best = min(values)
    ax.bar(positions, values, 0.55,
           color=[p.green if abs(v - best) < 1e-9 else p.blue for v in values])
    for x, value in zip(positions, values):
        ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("test MAE ($1000s)")
    ax.set_ylim(0, max(values) * 1.28)
    ax.set_title("Same model, same data — four stopping policies", fontsize=10.5)


@functools.lru_cache(maxsize=1)
def _api_equivalence() -> dict:
    """Build one architecture three ways and compare outputs bit for bit."""
    keras = tf().keras
    seed_everything(0)
    rng = np.random.default_rng(0)
    probe = rng.normal(0, 1, (256, 20)).astype("float32")

    sequential = keras.Sequential([
        keras.layers.Input((20,)),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(16, activation="relu"),
        keras.layers.Dense(1),
    ])
    weights = sequential.get_weights()

    inputs = keras.layers.Input((20,))
    hidden = keras.layers.Dense(32, activation="relu")(inputs)
    hidden = keras.layers.Dense(16, activation="relu")(hidden)
    functional = keras.Model(inputs, keras.layers.Dense(1)(hidden))
    functional.set_weights(weights)

    class Subclassed(keras.Model):
        def __init__(self):
            super().__init__()
            self.one = keras.layers.Dense(32, activation="relu")
            self.two = keras.layers.Dense(16, activation="relu")
            self.out = keras.layers.Dense(1)

        def call(self, x):
            return self.out(self.two(self.one(x)))

    subclassed = Subclassed()
    subclassed(probe[:1])
    subclassed.set_weights(weights)

    reference = sequential.predict(probe, verbose=0)
    differences = {
        "Functional": float(np.abs(
            functional.predict(probe, verbose=0) - reference).max()),
        "Subclassed": float(np.abs(
            subclassed.predict(probe, verbose=0) - reference).max()),
    }

    # The two-input model Sequential cannot express at all.
    left_input = keras.layers.Input((20,), name="numbers")
    right_input = keras.layers.Input((8,), name="flags")
    merged = keras.layers.Concatenate()([
        keras.layers.Dense(32, activation="relu")(left_input),
        keras.layers.Dense(8, activation="relu")(right_input)])
    two_headed = keras.Model([left_input, right_input], [
        keras.layers.Dense(1, name="price")(merged),
        keras.layers.Dense(3, activation="softmax", name="grade")(merged)])

    return {"differences": differences,
            "parameters": {"Sequential": int(sequential.count_params()),
                           "Functional": int(functional.count_params()),
                           "Subclassed": int(subclassed.count_params())},
            "multi_inputs": len(two_headed.inputs),
            "multi_outputs": len(two_headed.outputs),
            "multi_parameters": int(two_headed.count_params())}


def api_equivalence(fig, axes, p: Palette) -> None:
    info = _api_equivalence()
    left, right = fig.subplots(1, 2, width_ratios=(1.0, 1.1))
    names = list(info["differences"])
    positions = np.arange(len(names))
    floor = 1e-12
    values = [max(info["differences"][name], floor) for name in names]
    left.barh(positions, values, color=p.green, height=0.5)
    for position, name in zip(positions, names):
        left.annotate(f"{info['differences'][name]:.2e}",
                      (max(info["differences"][name], floor), position),
                      xytext=(5, 0), textcoords="offset points", fontsize=9,
                      color=p.fg, va="center")
    left.set_yticks(positions)
    left.set_yticklabels([f"{name}\nvs Sequential" for name in names],
                         fontsize=9)
    left.set_xscale("log")
    left.set_xlim(floor, 1e-3)
    left.set_xlabel("largest output difference over 256 inputs")
    left.set_title("identical weights, identical architecture", fontsize=10)
    left.invert_yaxis()

    counts = info["parameters"]
    labels = list(counts) + ["two-input\ntwo-output"]
    heights = list(counts.values()) + [info["multi_parameters"]]
    colours = [p.blue, p.blue, p.blue, p.amber]
    right.bar(np.arange(len(labels)), heights, color=colours, width=0.6)
    for index, value in enumerate(heights):
        right.annotate(f"{value:,}", (index, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(np.arange(len(labels)))
    right.set_xticklabels(labels, fontsize=8)
    right.set_ylabel("parameters")
    right.set_title(f"the amber model has {info['multi_inputs']} inputs and "
                    f"{info['multi_outputs']} outputs —\nno Sequential exists "
                    f"for it", fontsize=9.5)


FIGURES = [
    figure("early-stopping", early_stopping, size=(9.4, 3.6), axes=False),
    figure("api-equivalence", api_equivalence, size=(9.0, 3.8), axes=False),
    figure("training-policies", training_policies, size=(7.4, 3.6), axes=False),
]


if __name__ == "__main__":
    info = _api_equivalence()
    print("=== the three APIs, same weights ===")
    for name, difference in info["differences"].items():
        print(f"{name:12s} vs Sequential: {difference:.3e}")
    for name, count in info["parameters"].items():
        print(f"{name:12s} parameters: {count:,}")
    print(f"two-input model: {info['multi_inputs']} inputs, "
          f"{info['multi_outputs']} outputs, "
          f"{info['multi_parameters']:,} parameters\n")

    runs = _runs()
    curve = runs["val_loss"]
    print(f"best val loss {min(curve):.4f} at epoch "
          f"{int(np.argmin(curve)) + 1}; epoch {len(curve)} is {curve[-1]:.4f}")
    for (patience, restore), stopped in runs["stopped"].items():
        print(f"patience {patience:2d} restore={restore!s:5s} -> stopped after "
              f"{stopped} epochs")
    for label, mae in runs["policies"].items():
        print(f"{label.replace(chr(10), ' '):28s} test MAE {mae:.4f}")

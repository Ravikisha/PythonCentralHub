"""Figures for *Famous CNN Architectures (LeNet to ResNet)*.

``residual-depth``
    The claim that made ResNet: a plain stack and a residual stack at two
    depths, trained identically. The plain one gets worse with depth.

``architecture-families``
    Miniature versions of six architectural ideas on the same data, so the
    parameter/accuracy/time trade-offs are measured rather than quoted.

``separable-savings``
    Standard convolution against depthwise-separable convolution, counted
    exactly.
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
EPOCHS = 8
# Keras' default BN momentum of 0.99 needs ~459 batches before its moving
# statistics are trustworthy; these runs are ~376, so validation accuracy
# would be meaningless. 0.9 converges in ~44.
BN_MOMENTUM = 0.9
BATCH = 128
DEPTHS = (2, 6)


def _stem(keras, inputs):
    """Downsample immediately, so the deep stack runs at 14x14 rather than
    28x28 — a 4x saving per convolution that does not change what the depth
    comparison is testing."""
    x = keras.layers.Conv2D(32, 3, padding="same", use_bias=False)(inputs)
    x = keras.layers.BatchNormalization(momentum=BN_MOMENTUM)(x)
    x = keras.layers.Activation("relu")(x)
    return keras.layers.MaxPooling2D(2)(x)


def _plain(depth: int, seed: int = 0):
    """Two convolutions per block and no shortcut — the control condition."""
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((28, 28, 1))
    x = _stem(keras, inputs)
    for index in range(depth):
        x = keras.layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
        x = keras.layers.BatchNormalization(momentum=BN_MOMENTUM)(x)
        x = keras.layers.Activation("relu")(x)
        x = keras.layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
        x = keras.layers.BatchNormalization(momentum=BN_MOMENTUM)(x)
        x = keras.layers.Activation("relu")(x)
        if index == depth // 2:
            x = keras.layers.MaxPooling2D(2)(x)
    x = keras.layers.GlobalAveragePooling2D()(x)
    return keras.Model(inputs, keras.layers.Dense(10, activation="softmax")(x))


def _residual(depth: int, seed: int = 0):
    """The same two convolutions, plus a shortcut, with the ReLU after the add.

    Putting the ReLU before the merge and none after it is a real trap: the
    block then adds non-negative values at every depth and the activations grow
    without bound. The classic ordering is conv-BN-relu-conv-BN, add, relu.
    """
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((28, 28, 1))
    x = _stem(keras, inputs)
    for index in range(depth):
        shortcut = x
        y = keras.layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
        y = keras.layers.BatchNormalization(momentum=BN_MOMENTUM)(y)
        y = keras.layers.Activation("relu")(y)
        y = keras.layers.Conv2D(32, 3, padding="same", use_bias=False)(y)
        y = keras.layers.BatchNormalization(momentum=BN_MOMENTUM)(y)
        x = keras.layers.Add()([y, shortcut])
        x = keras.layers.Activation("relu")(x)
        if index == depth // 2:
            x = keras.layers.MaxPooling2D(2)(x)
    x = keras.layers.GlobalAveragePooling2D()(x)
    return keras.Model(inputs, keras.layers.Dense(10, activation="softmax")(x))


def _compile(model):
    keras = tf().keras
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _depth_runs() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=False)
    out = {}
    for builder, label in ((_plain, "plain"), (_residual, "residual")):
        for depth in DEPTHS:
            model = _compile(builder(depth))
            started = time.perf_counter()
            history = model.fit(data["x_train"], data["y_train"],
                                epochs=EPOCHS, batch_size=BATCH, verbose=0,
                                validation_data=(data["x_test"],
                                                 data["y_test"]))
            out[(label, depth)] = {
                "val_accuracy": [float(v)
                                 for v in history.history["val_accuracy"]],
                "loss": [float(v) for v in history.history["loss"]],
                "params": int(model.count_params()),
                "seconds": time.perf_counter() - started,
            }
    return out


def residual_depth(fig, axes, p: Palette) -> None:
    runs = _depth_runs()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    # Derived from DEPTHS so changing the depths cannot break the drawing.
    styles = {}
    for label, color in (("plain", p.red), ("residual", p.green)):
        for depth, dash in zip(DEPTHS, ("-", "--", ":", "-.")):
            styles[(label, depth)] = (color, dash)
    for key, run in runs.items():
        color, dash = styles[key]
        label = (f"{key[0]} {key[1]} blocks — "
                 f"{run['val_accuracy'][-1]:.4f}")
        left.plot(epochs, run["val_accuracy"], lw=1.8, color=color, ls=dash,
                  label=label)
        right.plot(epochs, run["loss"], lw=1.8, color=color, ls=dash)
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_title(f"Fashion-MNIST, {LIMIT:,} rows, {EPOCHS} epochs",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")
    right.set_yscale("log")
    right.set_xlabel("epoch")
    right.set_ylabel("training loss (log scale)")
    right.set_title("training loss — depth should help here", fontsize=10)


def _families() -> dict:
    keras = tf().keras

    def lenet():
        return keras.Sequential([
            keras.layers.Input((28, 28, 1)),
            keras.layers.Conv2D(6, 5, activation="relu", padding="same"),
            keras.layers.AveragePooling2D(2),
            keras.layers.Conv2D(16, 5, activation="relu"),
            keras.layers.AveragePooling2D(2),
            keras.layers.Flatten(),
            keras.layers.Dense(120, activation="relu"),
            keras.layers.Dense(84, activation="relu"),
            keras.layers.Dense(10, activation="softmax"),
        ])

    def vgg():
        layers = [keras.layers.Input((28, 28, 1))]
        for filters in (32, 64):
            layers += [keras.layers.Conv2D(filters, 3, padding="same",
                                           activation="relu"),
                       keras.layers.Conv2D(filters, 3, padding="same",
                                           activation="relu"),
                       keras.layers.MaxPooling2D(2)]
        layers += [keras.layers.Flatten(),
                   keras.layers.Dense(128, activation="relu"),
                   keras.layers.Dense(10, activation="softmax")]
        return keras.Sequential(layers)

    def inception():
        inputs = keras.layers.Input((28, 28, 1))
        x = keras.layers.Conv2D(32, 3, padding="same", activation="relu")(inputs)
        for _ in range(2):
            one = keras.layers.Conv2D(16, 1, padding="same",
                                      activation="relu")(x)
            three = keras.layers.Conv2D(16, 3, padding="same",
                                        activation="relu")(x)
            five = keras.layers.Conv2D(16, 5, padding="same",
                                       activation="relu")(x)
            pooled = keras.layers.MaxPooling2D(3, strides=1,
                                               padding="same")(x)
            pooled = keras.layers.Conv2D(16, 1, padding="same",
                                         activation="relu")(pooled)
            x = keras.layers.Concatenate()([one, three, five, pooled])
            x = keras.layers.MaxPooling2D(2)(x)
        x = keras.layers.GlobalAveragePooling2D()(x)
        return keras.Model(inputs, keras.layers.Dense(10,
                                                      activation="softmax")(x))

    def resnet():
        return _residual(2)

    def xception():
        layers = [keras.layers.Input((28, 28, 1)),
                  keras.layers.Conv2D(32, 3, padding="same",
                                      activation="relu")]
        for filters in (32, 64):
            layers += [keras.layers.SeparableConv2D(filters, 3, padding="same",
                                                    activation="relu"),
                       keras.layers.MaxPooling2D(2)]
        layers += [keras.layers.GlobalAveragePooling2D(),
                   keras.layers.Dense(10, activation="softmax")]
        return keras.Sequential(layers)

    def senet():
        inputs = keras.layers.Input((28, 28, 1))
        x = keras.layers.Conv2D(32, 3, padding="same", activation="relu")(inputs)
        for filters in (32, 64):
            x = keras.layers.Conv2D(filters, 3, padding="same",
                                    activation="relu")(x)
            squeeze = keras.layers.GlobalAveragePooling2D()(x)
            squeeze = keras.layers.Dense(filters // 4, activation="relu")(squeeze)
            squeeze = keras.layers.Dense(filters, activation="sigmoid")(squeeze)
            x = keras.layers.Multiply()([x, keras.layers.Reshape(
                (1, 1, filters))(squeeze)])
            x = keras.layers.MaxPooling2D(2)(x)
        x = keras.layers.GlobalAveragePooling2D()(x)
        return keras.Model(inputs, keras.layers.Dense(10,
                                                      activation="softmax")(x))

    return {"LeNet-ish": lenet, "VGG-ish": vgg, "Inception-ish": inception,
            "ResNet-ish": resnet, "Xception-ish": xception, "SENet-ish": senet}


@functools.lru_cache(maxsize=1)
def _family_runs() -> dict:
    data = dataset("fashion", limit=LIMIT, flat=False)
    out = {}
    for name, builder in _families().items():
        seed_everything(0)
        model = _compile(builder())
        started = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=BATCH, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[name] = {
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
        }
    return out


def architecture_families(fig, axes, p: Palette) -> None:
    runs = _family_runs()
    ax = fig.subplots(1, 1)
    for (name, run), color in zip(runs.items(), p.cycle):
        best = max(run["val_accuracy"])
        ax.scatter([run["params"]], [best], s=130, color=color, label=name)
        ax.annotate(f"{name}\n{best:.4f}, {run['seconds']:.0f}s",
                    (run["params"], best), textcoords="offset points",
                    xytext=(10, -4), fontsize=8, color=color)
    ax.set_xscale("log")
    ax.set_xlabel("parameters (log scale)")
    ax.set_ylabel("best validation accuracy")
    ax.set_title("Miniature versions of six ideas, same data and budget",
                 fontsize=10.5)


def separable_savings(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    channels = np.array([16, 32, 64, 128, 256, 512])
    kernel = 3
    standard = kernel * kernel * channels * channels + channels
    separable = (kernel * kernel * channels + channels * channels + channels)
    ax.plot(channels, standard, "o-", ms=6, lw=2.0, color=p.red,
            label="Conv2D(C, 3x3)")
    ax.plot(channels, separable, "o-", ms=6, lw=2.0, color=p.green,
            label="SeparableConv2D(C, 3x3)")
    for c, s, sep in zip(channels, standard, separable):
        ax.annotate(f"{s / sep:.1f}x", (c, sep), textcoords="offset points",
                    xytext=(4, -12), fontsize=8, color=p.green)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(list(channels))
    ax.set_xticklabels([str(c) for c in channels])
    ax.set_xlabel("channels in and out (log scale)")
    ax.set_ylabel("parameters in one layer (log scale)")
    ax.set_title("Depthwise-separable convolution, counted exactly",
                 fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("residual-depth", residual_depth, size=(9.4, 3.6), axes=False),
    figure("architecture-families", architecture_families, size=(8.6, 4.0),
           axes=False),
    figure("separable-savings", separable_savings, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    print(f"=== plain against residual, Fashion-MNIST {LIMIT} rows, {EPOCHS} epochs ===")
    print(f"{'model':22s} {'params':>10} {'final val acc':>14} {'best':>8} "
          f"{'final train loss':>17} {'seconds':>9}")
    runs = _depth_runs()
    for key, run in runs.items():
        label = f"{key[0]} {key[1]} blocks ({key[1] * 2} convs)"
        print(f"{label:22s} {run['params']:10,} {run['val_accuracy'][-1]:14.4f} "
              f"{max(run['val_accuracy']):8.4f} {run['loss'][-1]:17.4f} "
              f"{run['seconds']:9.1f}")
    for label in ("plain", "residual"):
        shallow = max(runs[(label, DEPTHS[0])]["val_accuracy"])
        deep = max(runs[(label, DEPTHS[1])]["val_accuracy"])
        print(f"{label}: going from {DEPTHS[0]} to {DEPTHS[1]} blocks changed "
              f"best accuracy by {deep - shallow:+.4f}")

    print("\n=== six architectural ideas ===")
    print(f"{'family':16s} {'params':>10} {'best val acc':>13} {'seconds':>9}")
    for name, run in _family_runs().items():
        print(f"{name:16s} {run['params']:10,} "
              f"{max(run['val_accuracy']):13.4f} {run['seconds']:9.1f}")

    print("\n=== separable against standard convolution ===")
    print(f"{'channels':>9} {'standard':>12} {'separable':>11} {'ratio':>7}")
    for c in (16, 32, 64, 128, 256, 512):
        standard = 3 * 3 * c * c + c
        separable = 3 * 3 * c + c * c + c
        print(f"{c:9d} {standard:12,} {separable:11,} {standard / separable:6.1f}x")

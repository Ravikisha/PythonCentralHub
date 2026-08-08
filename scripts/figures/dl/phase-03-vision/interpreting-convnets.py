"""Figures for *Interpreting What Convnets Learn (Grad-CAM)*.

``activation-maps``
    The first and last convolutional layers' responses to one image. Early
    filters fire on edges; late filters fire on almost nothing, sparsely.

``filter-maximisation``
    Inputs synthesised by gradient ascent to maximise single filters — what the
    filter is actually looking for, rather than what we assume.

``gradcam``
    Grad-CAM heat maps for correct and incorrect predictions, which is where the
    technique earns its keep.
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
EPOCHS = 15
CLASSES = ("t-shirt", "trouser", "pullover", "dress", "coat", "sandal",
           "shirt", "sneaker", "bag", "boot")


@functools.lru_cache(maxsize=1)
def _trained() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=False)
    seed_everything(0)
    inputs = keras.layers.Input((28, 28, 1))
    x = keras.layers.Conv2D(32, 3, padding="same", activation="relu",
                            name="conv1")(inputs)
    x = keras.layers.MaxPooling2D(2)(x)
    x = keras.layers.Conv2D(64, 3, padding="same", activation="relu",
                            name="conv2")(x)
    x = keras.layers.MaxPooling2D(2)(x)
    x = keras.layers.Conv2D(64, 3, padding="same", activation="relu",
                            name="conv3")(x)
    pooled = keras.layers.GlobalAveragePooling2D()(x)
    outputs = keras.layers.Dense(10, activation="softmax", name="head")(pooled)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    probabilities = model.predict(data["x_test"], verbose=0)
    predicted = probabilities.argmax(axis=1)
    correct = predicted == data["y_test"]
    return {"model": model, "data": data,
            "val_accuracy": float(history.history["val_accuracy"][-1]),
            "probabilities": probabilities, "predicted": predicted,
            "correct": correct}


def _activations(layer_name: str, image: np.ndarray) -> np.ndarray:
    keras = tf().keras
    info = _trained()
    probe = keras.Model(info["model"].inputs,
                        info["model"].get_layer(layer_name).output)
    return probe.predict(image[None, ...], verbose=0)[0]


def activation_maps(fig, axes, p: Palette) -> None:
    info = _trained()
    image = info["data"]["x_test"][0]
    grid = fig.subplots(2, 7)
    early = _activations("conv1", image)
    late = _activations("conv3", image)

    grid[0][0].imshow(image[..., 0], cmap="gray")
    grid[0][0].set_title(f"input — {CLASSES[info['data']['y_test'][0]]}",
                         fontsize=8)
    grid[1][0].imshow(image[..., 0], cmap="gray")
    grid[1][0].set_title("input", fontsize=8)
    order_early = np.argsort(-early.mean(axis=(0, 1)))[:6]
    order_late = np.argsort(-late.mean(axis=(0, 1)))[:6]
    for ax, channel in zip(grid[0][1:], order_early):
        ax.imshow(early[..., channel], cmap="viridis")
        ax.set_title(f"conv1 #{channel}\nmax {early[..., channel].max():.2f}",
                     fontsize=7.5)
    for ax, channel in zip(grid[1][1:], order_late):
        ax.imshow(late[..., channel], cmap="viridis")
        ax.set_title(f"conv3 #{channel}\nmax {late[..., channel].max():.2f}",
                     fontsize=7.5)
    for row in grid:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


@functools.lru_cache(maxsize=1)
def _maximised() -> dict:
    """Gradient ascent on the input to maximise one filter's mean response."""
    keras = tf().keras
    tensorflow = tf()
    info = _trained()
    out = {}
    for layer_name, channels in (("conv1", (0, 1, 2)), ("conv3", (0, 1, 2))):
        probe = keras.Model(info["model"].inputs,
                           info["model"].get_layer(layer_name).output)
        for channel in channels:
            seed_everything(channel)
            image = tensorflow.Variable(
                tensorflow.random.uniform((1, 28, 28, 1), 0.4, 0.6, seed=channel))
            for _ in range(120):
                with tensorflow.GradientTape() as tape:
                    activation = tensorflow.reduce_mean(
                        probe(image, training=False)[..., channel])
                gradient = tape.gradient(activation, image)
                gradient = gradient / (tensorflow.norm(gradient) + 1e-8)
                image.assign_add(2.0 * gradient)
                image.assign(tensorflow.clip_by_value(image, 0.0, 1.0))
            final = float(tensorflow.reduce_mean(
                probe(image, training=False)[..., channel]).numpy())
            out[(layer_name, channel)] = {"image": image.numpy()[0, :, :, 0],
                                          "response": final}
    return out


def filter_maximisation(fig, axes, p: Palette) -> None:
    result = _maximised()
    grid = fig.subplots(2, 3)
    for row, layer_name in enumerate(("conv1", "conv3")):
        for column, channel in enumerate((0, 1, 2)):
            entry = result[(layer_name, channel)]
            ax = grid[row][column]
            ax.imshow(entry["image"], cmap="gray")
            ax.set_title(f"{layer_name} filter {channel}\n"
                         f"mean response {entry['response']:.2f}", fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


def _gradcam(image: np.ndarray, class_index: int,
             layer_name: str = "conv3") -> np.ndarray:
    keras = tf().keras
    tensorflow = tf()
    info = _trained()
    probe = keras.Model(info["model"].inputs,
                        [info["model"].get_layer(layer_name).output,
                         info["model"].output])
    with tensorflow.GradientTape() as tape:
        maps, predictions = probe(image[None, ...], training=False)
        score = predictions[:, class_index]
    gradient = tape.gradient(score, maps)[0].numpy()
    weights = gradient.mean(axis=(0, 1))
    heat = np.maximum((maps[0].numpy() * weights).sum(axis=-1), 0)
    return heat / (heat.max() + 1e-8)


def gradcam(fig, axes, p: Palette) -> None:
    info = _trained()
    data = info["data"]
    right_rows = np.where(info["correct"])[0][:3]
    wrong_rows = np.where(~info["correct"])[0][:3]
    grid = fig.subplots(2, 6)
    for row, rows in enumerate((right_rows, wrong_rows)):
        for index, sample in enumerate(rows):
            image = data["x_test"][sample]
            truth = int(data["y_test"][sample])
            guess = int(info["predicted"][sample])
            heat = _gradcam(image, guess)
            confidence = float(info["probabilities"][sample, guess])
            ax_image = grid[row][index * 2]
            ax_heat = grid[row][index * 2 + 1]
            ax_image.imshow(image[..., 0], cmap="gray")
            ax_image.set_title(f"true {CLASSES[truth]}", fontsize=7.5)
            ax_heat.imshow(image[..., 0], cmap="gray")
            ax_heat.imshow(np.kron(heat, np.ones((4, 4))), cmap="jet",
                           alpha=0.5)
            ax_heat.set_title(f"said {CLASSES[guess]} ({confidence:.2f})",
                              fontsize=7.5,
                              color=p.green if row == 0 else p.red)
    for row in grid:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


FIGURES = [
    figure("activation-maps", activation_maps, size=(9.6, 3.2), axes=False),
    figure("filter-maximisation", filter_maximisation, size=(6.4, 4.4),
           axes=False),
    figure("gradcam", gradcam, size=(9.6, 3.4), axes=False),
]


if __name__ == "__main__":
    info = _trained()
    data = info["data"]
    print(f"=== trained convnet, Fashion-MNIST {LIMIT} rows, {EPOCHS} epochs ===")
    print(f"validation accuracy {info['val_accuracy']:.4f}  "
          f"parameters {info['model'].count_params():,}")

    image = data["x_test"][0]
    print(f"\n=== activation statistics for one image "
          f"({CLASSES[int(data['y_test'][0])]}) ===")
    for layer_name in ("conv1", "conv2", "conv3"):
        maps = _activations(layer_name, image)
        dead = int((maps.max(axis=(0, 1)) == 0).sum())
        print(f"{layer_name}: shape {maps.shape}  mean {maps.mean():.4f}  "
              f"max {maps.max():.4f}  zero fraction "
              f"{float((maps == 0).mean()):.4f}  silent channels {dead}"
              f" of {maps.shape[-1]}")

    print("\n=== filter maximisation (120 ascent steps) ===")
    for (layer_name, channel), entry in _maximised().items():
        picture = entry["image"]
        print(f"{layer_name} filter {channel}: response {entry['response']:8.3f}  "
              f"image std {picture.std():.4f}  "
              f"fraction at the 0/1 limits "
              f"{float(((picture <= 1e-6) | (picture >= 1 - 1e-6)).mean()):.4f}")

    print("\n=== Grad-CAM ===")
    for label, rows in (("correct", np.where(info["correct"])[0][:3]),
                        ("wrong", np.where(~info["correct"])[0][:3])):
        for sample in rows:
            heat = _gradcam(data["x_test"][sample],
                            int(info["predicted"][sample]))
            centre = float(heat[1:6, 1:6].mean())
            print(f"{label:8s} row {sample:4d}  true "
                  f"{CLASSES[int(data['y_test'][sample])]:9s} said "
                  f"{CLASSES[int(info['predicted'][sample])]:9s} "
                  f"confidence {float(info['probabilities'][sample].max()):.4f}  "
                  f"heat map {heat.shape}, centre mass {centre:.4f}")

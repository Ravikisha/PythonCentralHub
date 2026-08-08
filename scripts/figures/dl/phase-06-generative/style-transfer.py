"""Figures for *Neural Style Transfer*.

Style transfer is the clearest example of a loss doing all the work: nothing is
trained here, an image is optimised. Content loss keeps the layout, style loss
matches feature correlations (the Gram matrix), and the weight between them is a
dial with measurable ends.

As with DeepDream there are no cached pretrained weights, so features come from
a convnet trained here on Fashion-MNIST. The mechanism is unchanged; the style
vocabulary is texture and stroke rather than brushwork.

``weight-sweep``
    Content and style loss against the style weight, with the resulting images --
    both losses cannot fall together, and the trade is measurable.

``gram-matrix``
    What the style loss actually compares: feature correlation matrices, for the
    style image, the content image and the result.

``optimisation``
    Both loss terms per iteration, plus what happens if the content image is
    replaced by noise as the starting point.
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
EPOCHS = 12
SIZE = 56
STEPS = 120
LEARNING_RATE = 0.02
STYLE_WEIGHTS = (0.0, 1.0, 100.0, 10000.0)
CONTENT_LAYER = "conv3"
STYLE_LAYERS = ("conv1", "conv2", "conv3")
CONTENT_INDEX = 0        # a t-shirt
STYLE_INDEX = 8          # a bag, whose texture is the "style"


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("fashion", limit=LIMIT, flat=False)


@functools.lru_cache(maxsize=1)
def _features() -> dict:
    """A small fully convolutional network, trained here rather than downloaded."""
    keras = tf().keras
    data = _data()
    seed_everything(0)
    inputs = keras.layers.Input((None, None, 1))
    x = keras.layers.Conv2D(16, 3, padding="same", activation="relu",
                            name="conv1")(inputs)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Conv2D(32, 3, padding="same", activation="relu",
                            name="conv2")(x)
    x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.Conv2D(64, 3, padding="same", activation="relu",
                            name="conv3")(x)
    outputs = keras.layers.Dense(10, activation="softmax")(
        keras.layers.GlobalAveragePooling2D()(x))
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "seconds": time.perf_counter() - started}


@functools.lru_cache(maxsize=1)
def _extractor():
    keras = tf().keras
    model = _features()["model"]
    names = tuple(dict.fromkeys(STYLE_LAYERS + (CONTENT_LAYER,)))
    return keras.Model(model.inputs,
                       [model.get_layer(name).output for name in names]), names


def _resize(image) -> np.ndarray:
    tensorflow = tf()
    return tensorflow.image.resize(image[None, ...], (SIZE, SIZE)).numpy()


@functools.lru_cache(maxsize=1)
def _images() -> dict:
    data = _data()
    return {"content": _resize(data["x_test"][CONTENT_INDEX]),
            "style": _resize(data["x_test"][STYLE_INDEX])}


def _gram(activation):
    """Feature correlations, normalised by the number of positions.

    The Gram matrix throws away WHERE each feature fired and keeps how often
    features co-occur, which is why matching it transfers texture and not layout.
    """
    tensorflow = tf()
    shape = tensorflow.shape(activation)
    flat = tensorflow.reshape(activation, (shape[0], -1, shape[3]))
    gram = tensorflow.matmul(flat, flat, transpose_a=True)
    return gram / tensorflow.cast(shape[1] * shape[2], "float32")


def _outputs(extractor, tensor) -> list:
    """A multi-output model returns a list; a single-output one returns a tensor.

    Not `np.atleast_1d`: the outputs have different shapes, so numpy refuses to
    stack them into one array.
    """
    result = extractor(tensor)
    return list(result) if isinstance(result, (list, tuple)) else [result]


def _targets():
    tensorflow = tf()
    extractor, names = _extractor()
    images = _images()
    style_outputs = _outputs(extractor,
                             tensorflow.convert_to_tensor(images["style"]))
    content_outputs = _outputs(extractor,
                               tensorflow.convert_to_tensor(images["content"]))
    grams = {name: _gram(output)
             for name, output in zip(names, style_outputs)
             if name in STYLE_LAYERS}
    content = {name: output for name, output in zip(names, content_outputs)
               if name == CONTENT_LAYER}
    return grams, content, names


def _transfer(style_weight: float, start: str = "content",
              steps: int = None) -> dict:
    """Optimise the IMAGE, not the network."""
    tensorflow = tf()
    keras = tf().keras
    extractor, names = _extractor()
    grams, content_targets, names = _targets()
    images = _images()
    steps = STEPS if steps is None else int(steps)

    if start == "content":
        initial = images["content"].copy()
    else:
        rng = np.random.default_rng(0)
        initial = np.clip(0.5 + rng.normal(0, 0.1, images["content"].shape),
                          0, 1).astype("float32")
    variable = tensorflow.Variable(initial)
    optimizer = keras.optimizers.Adam(LEARNING_RATE)
    history = {"content": [], "style": []}
    for _ in range(steps):
        with tensorflow.GradientTape() as tape:
            named = dict(zip(names, _outputs(extractor, variable)))
            content_loss = tensorflow.add_n([
                tensorflow.reduce_mean((named[name] - target) ** 2)
                for name, target in content_targets.items()])
            style_loss = tensorflow.add_n([
                tensorflow.reduce_mean((_gram(named[name]) - target) ** 2)
                for name, target in grams.items()])
            loss = content_loss + style_weight * style_loss
        gradient = tape.gradient(loss, variable)
        optimizer.apply_gradients([(gradient, variable)])
        variable.assign(tensorflow.clip_by_value(variable, 0.0, 1.0))
        history["content"].append(float(content_loss.numpy()))
        history["style"].append(float(style_loss.numpy()))
    return {"image": variable.numpy(), "history": history,
            "content": history["content"][-1], "style": history["style"][-1]}


@functools.lru_cache(maxsize=1)
def _weight_runs() -> dict:
    return {weight: _transfer(weight) for weight in STYLE_WEIGHTS}


@functools.lru_cache(maxsize=1)
def _start_runs() -> dict:
    weight = STYLE_WEIGHTS[len(STYLE_WEIGHTS) // 2]
    return {"from the content image": _transfer(weight, "content"),
            "from noise": _transfer(weight, "noise"),
            "weight": weight}


def weight_sweep(fig, axes, p: Palette) -> None:
    runs = _weight_runs()
    images = _images()
    weights = list(runs)
    top, bottom = fig.subplots(2, 1, height_ratios=(1.0, 0.95))
    strip = [images["content"][0, :, :, 0], images["style"][0, :, :, 0]]
    strip += [runs[weight]["image"][0, :, :, 0] for weight in weights]
    top.imshow(np.concatenate(strip, axis=1), cmap="gray")
    top.set_title("content | style | " + " | ".join(f"w={w:g}"
                                                    for w in weights),
                  fontsize=9.5)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    content = [runs[weight]["content"] for weight in weights]
    style = [runs[weight]["style"] for weight in weights]
    positions = np.arange(len(weights))
    bottom.plot(positions, content, "o-", ms=6, lw=2.0, color=p.blue,
                label="content loss")
    twin = bottom.twinx()
    twin.plot(positions, style, "s--", ms=5, lw=2.0, color=p.amber,
              label="style loss")
    twin.set_yscale("log")
    twin.set_ylabel("style loss (log)")
    for x, value in zip(positions, content):
        bottom.annotate(f"{value:.4f}", (x, value), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=7.5,
                        color=p.blue)
    for x, value in zip(positions, style):
        twin.annotate(f"{value:.4f}", (x, value), xytext=(0, -14),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.amber)
    bottom.set_xticks(positions)
    bottom.set_xticklabels([f"{w:g}" for w in weights])
    bottom.set_xlabel("style weight")
    bottom.set_ylabel("content loss")
    bottom.set_title(f"{STEPS} optimisation steps per setting", fontsize=9.5)
    lines = bottom.get_lines() + twin.get_lines()
    bottom.legend(lines, [line.get_label() for line in lines], fontsize=8,
                  loc="center right")


def gram_matrix(fig, axes, p: Palette) -> None:
    tensorflow = tf()
    extractor, names = _extractor()
    images = _images()
    runs = _weight_runs()
    best = max(w for w in runs)
    sources = (("style image", images["style"]),
               ("content image", images["content"]),
               (f"result (w={best:g})", runs[best]["image"]))
    grid = fig.subplots(1, len(sources))
    layer = STYLE_LAYERS[-1]
    index = list(names).index(layer)
    reference = None
    for ax, (label, image) in zip(grid, sources):
        outputs = _outputs(extractor, tensorflow.convert_to_tensor(image))
        gram = _gram(outputs[index]).numpy()[0]
        if reference is None:
            reference = gram
        distance = float(np.mean((gram - reference) ** 2))
        ax.imshow(gram, cmap="magma")
        ax.set_title(f"{label}\n{layer} Gram, MSE vs style {distance:.4f}",
                     fontsize=8.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def optimisation(fig, axes, p: Palette) -> None:
    runs = _start_runs()
    weight = runs["weight"]
    left, right = fig.subplots(1, 2, width_ratios=(1.1, 1.0))
    for label, color in (("from the content image", p.blue), ("from noise", p.amber)):
        history = runs[label]["history"]
        steps = range(1, len(history["content"]) + 1)
        left.plot(steps, history["content"], lw=2.0, color=color,
                  label=f"{label}: content")
        left.plot(steps, history["style"], lw=1.5, ls="--", color=color,
                  label=f"{label}: style")
    left.set_yscale("log")
    left.set_xlabel("optimisation step")
    left.set_ylabel("loss (log)")
    left.set_title(f"style weight {weight:g}", fontsize=10)
    left.legend(fontsize=7, loc="upper right")

    strip = [runs[label]["image"][0, :, :, 0]
             for label in ("from the content image", "from noise")]
    right.imshow(np.concatenate(strip, axis=1), cmap="gray")
    right.set_title("started from the content image (left) or from noise "
                    "(right)", fontsize=9)
    right.set_xticks([])
    right.set_yticks([])
    right.grid(False)


FIGURES = [
    figure("weight-sweep", weight_sweep, size=(9.2, 5.0), axes=False),
    figure("gram-matrix", gram_matrix, size=(8.4, 3.2), axes=False),
    figure("optimisation", optimisation, size=(9.4, 3.6), axes=False),
]


if __name__ == "__main__":
    info = _features()
    print("=== the feature network (trained here, not downloaded) ===")
    print(f"{info['model'].count_params():,} parameters, {EPOCHS} epochs on "
          f"Fashion-MNIST, {info['seconds']:.0f}s, validation accuracy "
          f"{info['accuracy']:.4f}")
    print(f"content layer {CONTENT_LAYER}, style layers "
          f"{', '.join(STYLE_LAYERS)}")
    print("nothing is trained during transfer: the IMAGE is the variable")

    print(f"\n=== the style weight trade ({STEPS} steps each) ===")
    runs = _weight_runs()
    print(f"{'style weight':>13} {'content loss':>13} {'style loss':>12} "
          f"{'total':>12}")
    for weight, entry in runs.items():
        total = entry["content"] + weight * entry["style"]
        print(f"{weight:13g} {entry['content']:13.5f} {entry['style']:12.5f} "
              f"{total:12.5f}")
    first = runs[STYLE_WEIGHTS[0]]
    last = runs[STYLE_WEIGHTS[-1]]
    print(f"content loss rose {first['content']:.5f} -> {last['content']:.5f} "
          f"while style loss fell {first['style']:.5f} -> {last['style']:.5f}")
    print("at weight 0 the result IS the content image, so its content loss is")
    print("the floor and its style loss is whatever the content already had")

    print("\n=== where you start from ===")
    starts = _start_runs()
    print(f"{'start':24s} {'content loss':>13} {'style loss':>12}")
    for label in ("from the content image", "from noise"):
        entry = starts[label]
        print(f"{label:24s} {entry['content']:13.5f} {entry['style']:12.5f}")
    print(f"both at style weight {starts['weight']:g}; starting from the content")
    print("image is not just faster, it reaches a different solution -- the")
    print("optimisation is non-convex and the start point selects the basin")

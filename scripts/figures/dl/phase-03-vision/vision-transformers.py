"""Figures for *Vision Transformers: Images Without Convolution*.

``patch-embedding``
    An image cut into patches and flattened, which is the whole of a ViT's
    "tokenisation" — drawn on a real image.

``vit-against-cnn``
    A small ViT and a convnet with comparable parameter counts, trained on the
    same data at three dataset sizes. The crossover point is the story.

``attention-maps``
    Where the class token attends, per head, on correct and incorrect
    predictions.
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

PATCH = 7               # 28 / 7 = 4, so 16 patches
SIDE = 28 // PATCH
TOKENS = SIDE * SIDE
WIDTH = 64
HEADS = 4
BLOCKS = 2
EPOCHS = 15
SIZES = (1000, 4000)
CLASSES = ("t-shirt", "trouser", "pullover", "dress", "coat", "sandal",
           "shirt", "sneaker", "bag", "boot")


def _patchify(images: np.ndarray) -> np.ndarray:
    """(N, 28, 28, 1) -> (N, 16, 49): the only 'tokenisation' a ViT does."""
    count = len(images)
    reshaped = images.reshape(count, SIDE, PATCH, SIDE, PATCH)
    return reshaped.transpose(0, 1, 3, 2, 4).reshape(count, TOKENS,
                                                     PATCH * PATCH)


@functools.lru_cache(maxsize=1)
def _patch_demo() -> dict:
    data = dataset("fashion", limit=200, flat=False)
    image = data["x_train"][7][..., 0]
    patches = _patchify(image[None, ..., None])[0]
    return {"image": image, "patches": patches,
            "label": CLASSES[int(data["y_train"][7])]}


def patch_embedding(fig, axes, p: Palette) -> None:
    info = _patch_demo()
    left, middle, right = fig.subplots(1, 3)

    left.imshow(info["image"], cmap="gray")
    for line in range(1, SIDE):
        left.axhline(line * PATCH - 0.5, color=p.amber, lw=1.2)
        left.axvline(line * PATCH - 0.5, color=p.amber, lw=1.2)
    left.set_title(f"{info['label']}: {SIDE}x{SIDE} grid of "
                   f"{PATCH}x{PATCH} patches", fontsize=9)

    grid = info["patches"].reshape(SIDE, SIDE, PATCH, PATCH)
    canvas = np.ones((SIDE * (PATCH + 1), SIDE * (PATCH + 1))) * 0.5
    for row in range(SIDE):
        for column in range(SIDE):
            top, left_edge = row * (PATCH + 1), column * (PATCH + 1)
            canvas[top:top + PATCH, left_edge:left_edge + PATCH] = \
                grid[row, column]
    middle.imshow(canvas, cmap="gray")
    middle.set_title(f"{TOKENS} patches, separated", fontsize=9)

    right.imshow(info["patches"], aspect="auto", cmap="gray")
    right.set_title(f"flattened: {info['patches'].shape[0]} tokens x "
                    f"{info['patches'].shape[1]} values", fontsize=9)
    right.set_xlabel("pixel within the patch")
    right.set_ylabel("patch index")
    for ax in (left, middle):
        ax.set_xticks([])
        ax.set_yticks([])
    for ax in (left, middle, right):
        ax.grid(False)


def _vit(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((TOKENS, PATCH * PATCH))
    tokens = keras.layers.Dense(WIDTH, name="patch_projection")(inputs)
    positions = keras.layers.Embedding(TOKENS, WIDTH,
                                       name="position")(tf().range(TOKENS))
    x = tokens + positions
    for block in range(BLOCKS):
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(x)
        attention = keras.layers.MultiHeadAttention(
            num_heads=HEADS, key_dim=WIDTH // HEADS,
            name=f"attention{block}")(normed, normed)
        x = keras.layers.Add()([x, attention])
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(x)
        hidden = keras.layers.Dense(WIDTH * 2, activation="gelu")(normed)
        hidden = keras.layers.Dense(WIDTH)(hidden)
        x = keras.layers.Add()([x, hidden])
    x = keras.layers.LayerNormalization(epsilon=1e-6)(x)
    pooled = keras.layers.GlobalAveragePooling1D()(x)
    outputs = keras.layers.Dense(10, activation="softmax")(pooled)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def _convnet(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
        keras.layers.MaxPooling2D(2),
        keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
        keras.layers.MaxPooling2D(2),
        keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _comparison() -> dict:
    data = dataset("fashion", limit=max(SIZES), flat=False)
    patched_train = _patchify(data["x_train"])
    patched_test = _patchify(data["x_test"])
    out = {}
    for size in SIZES:
        for label in ("ViT", "convnet"):
            if label == "ViT":
                model = _vit()
                x, xt = patched_train[:size], patched_test
            else:
                model = _convnet()
                x, xt = data["x_train"][:size], data["x_test"]
            started = time.perf_counter()
            history = model.fit(x, data["y_train"][:size], epochs=EPOCHS,
                                batch_size=64, verbose=0,
                                validation_data=(xt, data["y_test"]))
            out[(label, size)] = {
                "val_accuracy": [float(v)
                                 for v in history.history["val_accuracy"]],
                "accuracy": [float(v) for v in history.history["accuracy"]],
                "params": int(model.count_params()),
                "seconds": time.perf_counter() - started,
            }
    return out


def vit_against_cnn(fig, axes, p: Palette) -> None:
    runs = _comparison()
    left, right = fig.subplots(1, 2)
    for label, color in (("ViT", p.blue), ("convnet", p.green)):
        best = [max(runs[(label, s)]["val_accuracy"]) for s in SIZES]
        left.plot(SIZES, best, "o-", ms=6, lw=2.0, color=color,
                  label=f"{label} — {runs[(label, SIZES[0])]['params']:,} params")
        for size, value in zip(SIZES, best):
            left.annotate(f"{value:.4f}", (size, value),
                          textcoords="offset points", xytext=(0, 8),
                          ha="center", fontsize=7.5, color=color)
    left.set_xscale("log")
    left.set_xticks(list(SIZES))
    left.set_xticklabels([f"{s:,}" for s in SIZES])
    left.set_xlabel("training rows")
    left.set_ylabel("best validation accuracy")
    # Titled from the measurement rather than from the expectation: the ViT
    # actually led at both sizes here, on 28x28 greyscale with 7x7 patches.
    leads = [max(runs[("ViT", s)]["val_accuracy"])
             - max(runs[("convnet", s)]["val_accuracy"]) for s in SIZES]
    if min(leads) > 0:
        title = (f"the ViT led at both sizes ({leads[0]:+.4f}, {leads[-1]:+.4f})"
                 f" — and overfits far more")
    elif max(leads) < 0:
        title = f"the convnet led at both sizes ({leads[0]:+.4f}, {leads[-1]:+.4f})"
    else:
        title = "who wins depends on how much data there is"
    left.set_title(title, fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    epochs = range(1, EPOCHS + 1)
    for label, color in (("ViT", p.blue), ("convnet", p.green)):
        run = runs[(label, SIZES[-1])]
        right.plot(epochs, run["accuracy"], lw=1.3, ls="--", color=color)
        right.plot(epochs, run["val_accuracy"], lw=2.0, color=color,
                   label=f"{label} — gap "
                         f"{run['accuracy'][-1] - run['val_accuracy'][-1]:+.4f}, "
                         f"{run['seconds']:.0f}s")
    right.set_xlabel("epoch")
    right.set_ylabel("accuracy")
    right.set_title(f"{SIZES[-1]:,} rows: dashed = train, solid = validation",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


@functools.lru_cache(maxsize=1)
def _attention() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=max(SIZES), flat=False)
    patched_train = _patchify(data["x_train"])
    patched_test = _patchify(data["x_test"])
    model = _vit()
    model.fit(patched_train[:SIZES[-1]], data["y_train"][:SIZES[-1]],
              epochs=EPOCHS, batch_size=64, verbose=0)
    probabilities = model.predict(patched_test, verbose=0)
    predicted = probabilities.argmax(axis=1)
    correct = predicted == data["y_test"]

    # Re-run the first attention layer with scores exposed.
    layer = model.get_layer("attention0")
    normed = keras.Model(model.inputs, layer.input[0])
    rows = list(np.where(correct)[0][:2]) + list(np.where(~correct)[0][:2])
    inputs = normed.predict(patched_test[rows], verbose=0)
    _, scores = layer(inputs, inputs, return_attention_scores=True)
    return {"scores": scores.numpy(), "rows": rows,
            "images": data["x_test"][rows][..., 0],
            "truth": data["y_test"][rows], "predicted": predicted[rows],
            "confidence": probabilities[rows].max(axis=1),
            "correct": correct[rows],
            "accuracy": float(correct.mean())}


def attention_maps(fig, axes, p: Palette) -> None:
    info = _attention()
    grid = fig.subplots(4, 5)
    for row, sample in enumerate(info["rows"]):
        grid[row][0].imshow(info["images"][row], cmap="gray")
        mark = "right" if info["correct"][row] else "wrong"
        grid[row][0].set_title(
            f"{CLASSES[int(info['truth'][row])]} -> "
            f"{CLASSES[int(info['predicted'][row])]} ({mark})", fontsize=7.5,
            color=p.green if info["correct"][row] else p.red)
        for head in range(HEADS):
            # Average over query tokens: where does this head look overall?
            attention = info["scores"][row, head].mean(axis=0)
            grid[row][head + 1].imshow(attention.reshape(SIDE, SIDE),
                                       cmap="magma")
            grid[row][head + 1].set_title(
                f"head {head}, max {attention.max():.3f}", fontsize=7)
    for row in grid:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


FIGURES = [
    figure("patch-embedding", patch_embedding, size=(9.4, 3.0), axes=False),
    figure("vit-against-cnn", vit_against_cnn, size=(9.4, 3.6), axes=False),
    figure("attention-maps", attention_maps, size=(8.6, 6.4), axes=False),
]


if __name__ == "__main__":
    info = _patch_demo()
    print(f"=== patching: 28x28 -> {TOKENS} tokens of {PATCH * PATCH} values ===")
    print(f"image {info['image'].shape} -> patches {info['patches'].shape}")
    print(f"a {WIDTH}-wide projection costs "
          f"{PATCH * PATCH * WIDTH + WIDTH:,} parameters")
    print(f"position embedding: {TOKENS} x {WIDTH} = {TOKENS * WIDTH:,}")
    # Patching must be lossless: every pixel appears exactly once.
    rebuilt = info["patches"].reshape(SIDE, SIDE, PATCH, PATCH) \
        .transpose(0, 2, 1, 3).reshape(28, 28)
    print(f"max |rebuilt - original| = "
          f"{np.abs(rebuilt - info['image']).max():.2e} (patching is lossless)")

    print(f"\n=== ViT against convnet, {EPOCHS} epochs each ===")
    runs = _comparison()
    print(f"{'model':9s} {'rows':>7} {'params':>9} {'best val acc':>13} "
          f"{'final train':>12} {'seconds':>9}")
    for size in SIZES:
        for label in ("ViT", "convnet"):
            run = runs[(label, size)]
            print(f"{label:9s} {size:7d} {run['params']:9,} "
                  f"{max(run['val_accuracy']):13.4f} "
                  f"{run['accuracy'][-1]:12.4f} {run['seconds']:9.1f}")
    for size in SIZES:
        convnet = max(runs[("convnet", size)]["val_accuracy"])
        vit = max(runs[("ViT", size)]["val_accuracy"])
        leader = "ViT" if vit > convnet else "convnet"
        print(f"  at {size:6d} rows {leader} leads by {abs(vit - convnet):.4f} "
              f"(ViT {vit:.4f}, convnet {convnet:.4f}); ViT train-val gap "
              f"{runs[('ViT', size)]['accuracy'][-1] - vit:+.4f}, convnet "
              f"{runs[('convnet', size)]['accuracy'][-1] - convnet:+.4f}")

    print("\n=== attention ===")
    info = _attention()
    print(f"ViT test accuracy on the full split: {info['accuracy']:.4f}")
    print(f"attention scores shape {info['scores'].shape} "
          f"(rows, heads, queries, keys)")
    for row, sample in enumerate(info["rows"]):
        per_head = info["scores"][row].mean(axis=1)
        spread = [float(h.max() - h.min()) for h in per_head]
        print(f"row {sample:4d} {CLASSES[int(info['truth'][row])]:9s} -> "
              f"{CLASSES[int(info['predicted'][row])]:9s} "
              f"conf {info['confidence'][row]:.4f}  "
              f"per-head attention spread "
              f"{[round(s, 4) for s in spread]}")
    uniform = 1.0 / TOKENS
    print(f"a head that ignored position entirely would give {uniform:.4f} "
          f"everywhere")

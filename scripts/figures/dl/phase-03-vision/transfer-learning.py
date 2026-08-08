"""Figures for *Transfer Learning Using Pre-trained Models*.

The backbone is pre-trained here rather than downloaded, and *two* source tasks
are measured, because the first attempt at this page produced a result worth
keeping: pre-training on MNIST digits and transferring to Fashion-MNIST made
every strategy **worse** than training from scratch. That is not a bug, it is
what an unrelated source task does — so the page reports both.

* ``related``   — pre-train on five Fashion-MNIST classes (the garments),
  transfer to the other five (footwear and bags). Same domain, disjoint labels.
* ``unrelated`` — pre-train on MNIST handwritten digits. Different domain.

``transfer-against-scratch``
    Four strategies at three dataset sizes on the related source. Every run uses
    the same learning rate unless the strategy is explicitly the low-rate one,
    because the first version confounded strategy with learning rate.

``unfreeze-depth``
    How many of the backbone's blocks to unfreeze, measured.

``feature-quality``
    A linear probe on frozen features from both sources against the raw pixels —
    the cleanest measure of what a backbone actually learned.
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

SIZES = (250, 1000, 4000)
EPOCHS = 12
PRETRAIN_ROWS = 12000
PRETRAIN_EPOCHS = 8
BLOCKS = 3
RATE = 1e-3
LOW_RATE = 1e-4
# Fashion-MNIST label ids. The garments are the source task, the footwear and
# bags the target: same sensor, same statistics, disjoint labels.
SOURCE_CLASSES = (0, 2, 3, 4, 6)          # t-shirt, pullover, dress, coat, shirt
TARGET_CLASSES = (1, 5, 7, 8, 9)          # trouser, sandal, sneaker, bag, boot
STRATEGIES = ("from scratch", "frozen features", "fine-tuned 1e-3",
              "fine-tuned 1e-4")


def _backbone(seed: int = 0):
    """Three conv blocks, named so they can be frozen individually."""
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((28, 28, 1))
    x = inputs
    for index, filters in enumerate((16, 32, 64)):
        x = keras.layers.Conv2D(filters, 3, padding="same", activation="relu",
                                name=f"block{index}_conv")(x)
        x = keras.layers.MaxPooling2D(2, name=f"block{index}_pool")(x)
    return keras.Model(inputs, x, name="backbone")


def _head(backbone, trainable_blocks: int, classes: int = 5,
          rate: float = RATE):
    keras = tf().keras
    for layer in backbone.layers:
        layer.trainable = False
    for index in range(BLOCKS - trainable_blocks, BLOCKS):
        for layer in backbone.layers:
            if layer.name.startswith(f"block{index}_"):
                layer.trainable = True
    x = keras.layers.GlobalAveragePooling2D()(backbone.output)
    x = keras.layers.Dense(64, activation="relu")(x)
    outputs = keras.layers.Dense(classes, activation="softmax")(x)
    model = keras.Model(backbone.input, outputs)
    model.compile(keras.optimizers.Adam(rate),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=4)
def _split(which: str) -> dict:
    """Fashion-MNIST restricted to one half of the label space, remapped to 0..4."""
    classes = SOURCE_CLASSES if which == "source" else TARGET_CLASSES
    data = dataset("fashion", limit=60000, flat=False)
    lookup = {label: index for index, label in enumerate(classes)}
    out = {}
    for part in ("train", "test"):
        x, y = data[f"x_{part}"], data[f"y_{part}"]
        keep = np.isin(y, classes)
        out[f"x_{part}"] = x[keep]
        out[f"y_{part}"] = np.array([lookup[int(v)] for v in y[keep]],
                                    dtype="int64")
    return out


@functools.lru_cache(maxsize=4)
def _pretrained(source: str = "related") -> dict:
    """Train the backbone on the source task and keep its weights."""
    keras = tf().keras
    if source == "related":
        data = _split("source")
        x, y = data["x_train"][:PRETRAIN_ROWS], data["y_train"][:PRETRAIN_ROWS]
        x_val, y_val = data["x_test"], data["y_test"]
        classes = len(SOURCE_CLASSES)
    else:
        digits = dataset("mnist", limit=PRETRAIN_ROWS, flat=False)
        x, y = digits["x_train"], digits["y_train"]
        x_val, y_val = digits["x_test"], digits["y_test"]
        classes = 10
    backbone = _backbone()
    model = _head(backbone, trainable_blocks=BLOCKS, classes=classes)
    started = time.perf_counter()
    history = model.fit(x, y, epochs=PRETRAIN_EPOCHS, batch_size=128, verbose=0,
                        validation_data=(x_val, y_val))
    return {"weights": [w.numpy() for w in backbone.weights],
            "source_accuracy": float(history.history["val_accuracy"][-1]),
            "rows": int(len(x)), "classes": classes,
            "seconds": time.perf_counter() - started,
            "params": int(backbone.count_params())}


def _transferred(source: str = "related"):
    backbone = _backbone(seed=1)          # different seed: weights get replaced
    for variable, value in zip(backbone.weights, _pretrained(source)["weights"]):
        variable.assign(value)
    return backbone


def _run(strategy: str, size: int, source: str = "related") -> dict:
    target = _split("target")
    if strategy == "from scratch":
        model = _head(_backbone(seed=2), trainable_blocks=BLOCKS)
    elif strategy == "frozen features":
        model = _head(_transferred(source), trainable_blocks=0)
    elif strategy == "fine-tuned 1e-3":
        model = _head(_transferred(source), trainable_blocks=1, rate=RATE)
    else:
        model = _head(_transferred(source), trainable_blocks=1, rate=LOW_RATE)
    started = time.perf_counter()
    history = model.fit(target["x_train"][:size], target["y_train"][:size],
                        epochs=EPOCHS, batch_size=64, verbose=0,
                        validation_data=(target["x_test"], target["y_test"]))
    return {"val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "trainable": int(sum(np.prod(w.shape)
                                 for w in model.trainable_weights)),
            "total": int(model.count_params()),
            "seconds": time.perf_counter() - started}


@functools.lru_cache(maxsize=1)
def _size_runs() -> dict:
    return {(strategy, size): _run(strategy, size)
            for size in SIZES for strategy in STRATEGIES}


@functools.lru_cache(maxsize=1)
def _source_runs() -> dict:
    """The same two strategies from a related and an unrelated source."""
    out = {}
    for source in ("related", "unrelated"):
        for strategy in ("frozen features", "fine-tuned 1e-3"):
            out[(source, strategy)] = _run(strategy, SIZES[1], source=source)
    return out


@functools.lru_cache(maxsize=1)
def _unfreeze_runs() -> dict:
    target = _split("target")
    out = {}
    for blocks in range(BLOCKS + 1):
        model = _head(_transferred("related"), trainable_blocks=blocks)
        history = model.fit(target["x_train"][:SIZES[1]],
                            target["y_train"][:SIZES[1]],
                            epochs=EPOCHS, batch_size=64, verbose=0,
                            validation_data=(target["x_test"],
                                             target["y_test"]))
        out[blocks] = {
            "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            "trainable": int(sum(np.prod(w.shape)
                                 for w in model.trainable_weights)),
        }
    return out


@functools.lru_cache(maxsize=1)
def _probe() -> dict:
    """Logistic regression on frozen features against on raw pixels."""
    from sklearn.linear_model import LogisticRegression

    keras = tf().keras
    target = _split("target")
    extractors = {}
    for source in ("related", "unrelated"):
        backbone = _transferred(source)
        extractors[source] = keras.Model(
            backbone.input,
            keras.layers.GlobalAveragePooling2D()(backbone.output))
    out = {}
    x_test = target["x_test"]
    for size in SIZES:
        labels = target["y_train"][:size]
        entry = {}
        for source, extractor in extractors.items():
            features = extractor.predict(target["x_train"][:size], verbose=0)
            features_test = extractor.predict(x_test, verbose=0)
            fitted = LogisticRegression(max_iter=400).fit(features, labels)
            entry[source] = float(fitted.score(features_test,
                                               target["y_test"]))
            entry["dimensions"] = int(features.shape[1])
        pixels = target["x_train"][:size].reshape(size, -1)
        on_pixels = LogisticRegression(max_iter=400).fit(pixels, labels)
        entry["pixels"] = float(on_pixels.score(
            x_test.reshape(len(x_test), -1), target["y_test"]))
        out[size] = entry
    return out


def transfer_against_scratch(fig, axes, p: Palette) -> None:
    runs = _size_runs()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(STRATEGIES, (p.red, p.blue, p.green, p.purple)))
    # Three of the four curves sit within 0.02 of each other, so labelling
    # every point makes the panel unreadable: label the last point only, and
    # stagger the labels vertically by strategy.
    for index, strategy in enumerate(STRATEGIES):
        best = [max(runs[(strategy, s)]["val_accuracy"]) for s in SIZES]
        left.plot(SIZES, best, "o-", ms=6, lw=2.0, color=colors[strategy],
                  label=f"{strategy} — {best[-1]:.4f}")
        left.annotate(f"{best[0]:.4f}", (SIZES[0], best[0]),
                      textcoords="offset points",
                      xytext=(8, 6 if index % 2 == 0 else -12),
                      ha="left", fontsize=7, color=colors[strategy])
    left.set_xscale("log")
    left.minorticks_off()
    left.set_xticks(list(SIZES))
    left.set_xticklabels([f"{s:,}" for s in SIZES])
    left.set_xlabel("target rows available")
    left.set_ylabel("best validation accuracy")
    left.set_title("garments -> footwear and bags, same sensor", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    epochs = range(1, EPOCHS + 1)
    for strategy in STRATEGIES:
        run = runs[(strategy, SIZES[0])]
        right.plot(epochs, run["val_accuracy"], lw=1.9,
                   color=colors[strategy],
                   label=f"{strategy} — {run['trainable']:,} trainable")
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title(f"{SIZES[0]} rows: where transfer should matter most",
                    fontsize=10)
    right.legend(fontsize=7, loc="lower right")


def unfreeze_depth(fig, axes, p: Palette) -> None:
    runs = _unfreeze_runs()
    ax = fig.subplots(1, 1)
    blocks = sorted(runs)
    best = [max(runs[b]["val_accuracy"]) for b in blocks]
    winner = max(best)
    ax.bar(blocks, best, 0.5,
           color=[p.green if abs(v - winner) < 1e-9 else p.blue for v in best])
    for b, value in zip(blocks, best):
        ax.annotate(f"{value:.4f}\n{runs[b]['trainable']:,} trainable",
                    (b, value), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=8, color=p.fg)
    ax.set_xticks(blocks)
    ax.set_xticklabels([f"{b} of {BLOCKS}" for b in blocks])
    ax.set_xlabel("backbone blocks unfrozen (from the top)")
    ax.set_ylabel("best validation accuracy")
    ax.set_ylim(0, 1.18)
    ax.set_title(f"{SIZES[1]:,} target rows — how much to unfreeze at "
                 f"{RATE:g}", fontsize=10.5)


def feature_quality(fig, axes, p: Palette) -> None:
    probe = _probe()
    sources = _source_runs()
    left, right = fig.subplots(1, 2)
    sizes = sorted(probe)
    left.plot(sizes, [probe[s]["related"] for s in sizes], "o-", ms=6, lw=2.0,
              color=p.green,
              label=f"{probe[sizes[0]]['dimensions']} features, related source")
    left.plot(sizes, [probe[s]["unrelated"] for s in sizes], "o-", ms=6, lw=2.0,
              color=p.amber, label="same, unrelated source (digits)")
    left.plot(sizes, [probe[s]["pixels"] for s in sizes], "o-", ms=6, lw=2.0,
              color=p.red, label="784 raw pixels")
    for size in sizes:
        gap = probe[size]["related"] - probe[size]["pixels"]
        left.annotate(f"{gap:+.4f}", (size, probe[size]["related"]),
                      textcoords="offset points", xytext=(0, 8), ha="center",
                      fontsize=7.5, color=p.green)
    left.set_xscale("log")
    left.set_xticks(list(sizes))
    left.set_xticklabels([f"{s:,}" for s in sizes])
    left.set_xlabel("target rows available")
    left.set_ylabel("test accuracy")
    left.set_title("a linear probe measures the features, not the classifier",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    labels = ("frozen features", "fine-tuned 1e-3")
    positions = np.arange(len(labels))
    for offset, source, color in ((-0.19, "related", p.green),
                                  (0.19, "unrelated", p.amber)):
        values = [max(sources[(source, s)]["val_accuracy"]) for s in labels]
        right.bar(positions + offset, values, 0.36, color=color,
                  label=f"{source} source")
        for x, value in zip(positions + offset, values):
            right.annotate(f"{value:.4f}", (x, value),
                           textcoords="offset points", xytext=(0, 4),
                           ha="center", fontsize=8, color=p.fg)
    scratch = max(_size_runs()[("from scratch", SIZES[1])]["val_accuracy"])
    right.axhline(scratch, color=p.red, lw=1.3, ls="--",
                  label=f"from scratch ({scratch:.4f})")
    right.set_xticks(positions)
    right.set_xticklabels(labels, fontsize=8.5)
    right.set_ylim(0, 1.12)
    right.set_ylabel("best validation accuracy")
    right.set_title(f"{SIZES[1]:,} rows: the source task decides everything",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


FIGURES = [
    figure("transfer-against-scratch", transfer_against_scratch,
           size=(9.4, 3.6), axes=False),
    figure("unfreeze-depth", unfreeze_depth, size=(7.6, 3.8), axes=False),
    figure("feature-quality", feature_quality, size=(9.6, 3.7), axes=False),
]


if __name__ == "__main__":
    source = _split("source")
    target = _split("target")
    print(f"=== the split ===")
    print(f"source classes {SOURCE_CLASSES}: {len(source['x_train']):,} train "
          f"rows; target classes {TARGET_CLASSES}: "
          f"{len(target['x_train']):,} train rows")
    for name in ("related", "unrelated"):
        info = _pretrained(name)
        print(f"{name:10s} backbone: {info['rows']:,} rows, "
              f"{info['classes']} classes, source validation accuracy "
              f"{info['source_accuracy']:.4f}, {info['params']:,} parameters, "
              f"{info['seconds']:.1f}s")

    runs = _size_runs()
    print(f"\n=== four strategies on the target task, {EPOCHS} epochs ===")
    print(f"{'rows':>7} {'strategy':17s} {'best val acc':>13} "
          f"{'trainable':>11} {'total':>9} {'seconds':>9}")
    for size in SIZES:
        for strategy in STRATEGIES:
            run = runs[(strategy, size)]
            print(f"{size:7d} {strategy:17s} "
                  f"{max(run['val_accuracy']):13.4f} {run['trainable']:11,} "
                  f"{run['total']:9,} {run['seconds']:9.1f}")
    for size in SIZES:
        scratch = max(runs[("from scratch", size)]["val_accuracy"])
        for strategy in STRATEGIES[1:]:
            value = max(runs[(strategy, size)]["val_accuracy"])
            print(f"  at {size:6d} rows: {strategy} against scratch "
                  f"{value - scratch:+.4f}")

    print(f"\n=== how much of the backbone to unfreeze ({SIZES[1]:,} rows) ===")
    print(f"{'blocks':>7} {'trainable':>11} {'best val acc':>13}")
    for blocks, run in sorted(_unfreeze_runs().items()):
        print(f"{blocks:7d} {run['trainable']:11,} "
              f"{max(run['val_accuracy']):13.4f}")

    print(f"\n=== the source task decides everything ({SIZES[1]:,} rows) ===")
    sources = _source_runs()
    print(f"{'source':10s} {'strategy':17s} {'best val acc':>13}")
    for (name, strategy), run in sources.items():
        print(f"{name:10s} {strategy:17s} {max(run['val_accuracy']):13.4f}")

    print("\n=== a linear probe on the frozen features ===")
    print(f"{'rows':>7} {'related':>9} {'unrelated':>10} {'pixels':>9} "
          f"{'related - pixels':>17}")
    for size, entry in sorted(_probe().items()):
        print(f"{size:7d} {entry['related']:9.4f} {entry['unrelated']:10.4f} "
              f"{entry['pixels']:9.4f} "
              f"{entry['related'] - entry['pixels']:+17.4f}")
    print("the features are 64 numbers against 784 pixels, and the backbone")
    print("never saw a single shoe or bag")

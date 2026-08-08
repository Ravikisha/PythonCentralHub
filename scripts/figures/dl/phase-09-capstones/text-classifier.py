"""Figures for *Capstone 2: A Text Classifier, End to End*.

The same ladder as the image capstone, applied to IMDB sentiment: a baseline
that needs no learning, then bag-of-words, then embeddings, then recurrence,
then attention. The interesting part is that on this problem the ladder does
NOT climb monotonically, and the page reports where it stops.

``ladder``
    Every model on one axis, with the parameter count and training time each
    one cost.

``length``
    Accuracy against review length, which is where the sequence models are
    supposed to earn their keep.

``errors``
    Where the best model and the simplest one disagree, and what the reviews
    they disagree on look like.
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

from _dl import imdb, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

VOCAB = 10000
MAXLEN = 200
ROWS = 6000
EPOCHS = 6
EMBEDDING = 32


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return imdb(vocab=VOCAB, maxlen=MAXLEN, limit=ROWS)


@functools.lru_cache(maxsize=1)
def _lengths() -> dict:
    """True review lengths, before padding, for the length analysis."""
    data = _data()
    return {"train": data["lengths"], "test": data["test_lengths"]}


@functools.lru_cache(maxsize=1)
def _bag_of_words() -> dict:
    """Multi-hot vectors plus a linear model -- no sequence information at all."""
    keras = tf().keras
    data = _data()

    def encode(rows):
        out = np.zeros((len(rows), VOCAB), dtype="float32")
        for index, row in enumerate(rows):
            out[index, row[row > 0]] = 1.0
        return out

    x_train = encode(data["x_train"])
    x_test = encode(data["x_test"])
    out = {}
    for label, layers in (
            ("bag of words + linear", []),
            ("bag of words + MLP", [16])):
        seed_everything(0)
        stack = [keras.layers.Input((VOCAB,))]
        for units in layers:
            stack.append(keras.layers.Dense(units, activation="relu"))
        stack.append(keras.layers.Dense(1, activation="sigmoid"))
        model = keras.Sequential(stack)
        model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                      metrics=["accuracy"])
        started = time.perf_counter()
        history = model.fit(x_train, data["y_train"], epochs=EPOCHS,
                            batch_size=128, verbose=0,
                            validation_data=(x_test, data["y_test"]))
        probabilities = model.predict(x_test, verbose=0,
                                      batch_size=512).reshape(-1)
        out[label] = {"accuracy": float(history.history["val_accuracy"][-1]),
                      "parameters": int(model.count_params()),
                      "seconds": time.perf_counter() - started,
                      "probabilities": probabilities}
    return out


def _sequence_model(kind: str) -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(0)
    inputs = keras.layers.Input((MAXLEN,))
    # mask_zero matters: without it the model spends capacity on padding.
    embedded = keras.layers.Embedding(VOCAB, EMBEDDING,
                                      mask_zero=True)(inputs)
    if kind == "pooling":
        x = keras.layers.GlobalAveragePooling1D()(embedded)
    elif kind == "lstm":
        x = keras.layers.LSTM(32)(embedded)
    elif kind == "bilstm":
        x = keras.layers.Bidirectional(keras.layers.LSTM(32))(embedded)
    else:
        attention = keras.layers.MultiHeadAttention(num_heads=2,
                                                    key_dim=EMBEDDING)
        attended = attention(embedded, embedded)
        x = keras.layers.GlobalAveragePooling1D()(
            keras.layers.Add()([embedded, attended]))
    x = keras.layers.Dense(32, activation="relu")(x)
    outputs = keras.layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    probabilities = model.predict(data["x_test"], verbose=0,
                                  batch_size=512).reshape(-1)
    return {"accuracy": float(history.history["val_accuracy"][-1]),
            "parameters": int(model.count_params()),
            "seconds": time.perf_counter() - started,
            "probabilities": probabilities}


@functools.lru_cache(maxsize=8)
def _sequence(kind: str) -> dict:
    return _sequence_model(kind)


@functools.lru_cache(maxsize=1)
def _ladder() -> dict:
    data = _data()
    majority = float(max(np.mean(data["y_test"]),
                         1 - np.mean(data["y_test"])))
    out = {"always predict one class": {"accuracy": majority,
                                        "parameters": 0, "seconds": 0.0,
                                        "probabilities": None}}
    out.update(_bag_of_words())
    for label, kind in (("embedding + pooling", "pooling"),
                        ("LSTM", "lstm"),
                        ("bidirectional LSTM", "bilstm"),
                        ("self-attention", "attention")):
        out[label] = _sequence(kind)
    return out


@functools.lru_cache(maxsize=1)
def _by_length() -> dict:
    """Accuracy split by how long the review actually was."""
    data = _data()
    lengths = _lengths()["test"]
    labels = data["y_test"]
    runs = _ladder()
    buckets = ((0, 100), (100, 200), (200, 400), (400, 10000))
    out = {}
    for label, entry in runs.items():
        if entry["probabilities"] is None:
            continue
        predicted = (entry["probabilities"] > 0.5).astype(int)
        scores = {}
        for low, high in buckets:
            mask = (lengths >= low) & (lengths < high)
            if mask.sum() < 20:
                continue
            scores[f"{low}-{high if high < 10000 else '+'}"] = {
                "accuracy": float((predicted[mask] == labels[mask]).mean()),
                "count": int(mask.sum()),
            }
        out[label] = scores
    return out


@functools.lru_cache(maxsize=1)
def _disagreement() -> dict:
    data = _data()
    runs = _ladder()
    labels = data["y_test"]
    simple = (runs["bag of words + linear"]["probabilities"] > 0.5).astype(int)
    best_label = max((label for label, entry in runs.items()
                      if entry["probabilities"] is not None),
                     key=lambda label: runs[label]["accuracy"])
    best = (runs[best_label]["probabilities"] > 0.5).astype(int)
    both_right = int(((simple == labels) & (best == labels)).sum())
    only_simple = int(((simple == labels) & (best != labels)).sum())
    only_best = int(((simple != labels) & (best == labels)).sum())
    both_wrong = int(((simple != labels) & (best != labels)).sum())
    oracle = (both_right + only_simple + only_best) / len(labels)
    return {"best_label": best_label, "both_right": both_right,
            "only_simple": only_simple, "only_best": only_best,
            "both_wrong": both_wrong, "oracle": float(oracle),
            "total": len(labels),
            "agreement": float((simple == best).mean())}


def ladder(fig, axes, p: Palette) -> None:
    runs = _ladder()
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    labels = list(runs)
    positions = np.arange(len(labels))
    accuracies = [runs[label]["accuracy"] for label in labels]
    best = max(accuracies)
    colours = [p.green if value == best else p.blue for value in accuracies]
    colours[0] = p.muted
    left.barh(positions, accuracies, 0.55, color=colours)
    previous = None
    for y, label in zip(positions, labels):
        value = runs[label]["accuracy"]
        gain = "" if previous is None else f"  ({value - previous:+.4f})"
        left.annotate(f"{value:.4f}{gain}", (value, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
        previous = value
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, 1.3)
    left.set_xlabel(f"accuracy on {len(_data()['y_test']):,} held-out reviews")
    left.set_title("the ladder does not climb all the way", fontsize=10)

    trained = [label for label in labels if runs[label]["parameters"] > 0]
    seconds = [runs[label]["seconds"] for label in trained]
    scores = [runs[label]["accuracy"] for label in trained]
    right.scatter(seconds, scores, s=90, color=p.purple)
    for label, second, score in zip(trained, seconds, scores):
        right.annotate(label, (second, score), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    right.set_xscale("log")
    right.set_xlabel(f"seconds to train {EPOCHS} epochs (log)")
    right.set_ylabel("accuracy")
    right.set_title("accuracy against what it cost", fontsize=10)


def length(fig, axes, p: Palette) -> None:
    runs = _by_length()
    shown = [label for label in ("bag of words + linear", "embedding + pooling",
                                 "LSTM", "self-attention") if label in runs]
    buckets = list(runs[shown[0]])
    positions = np.arange(len(buckets))
    width = 0.8 / len(shown)
    colours = (p.muted, p.blue, p.green, p.amber)
    for index, (label, colour) in enumerate(zip(shown, colours)):
        values = [runs[label][bucket]["accuracy"] for bucket in buckets]
        axes.bar(positions + (index - (len(shown) - 1) / 2) * width, values,
                 width * 0.9, color=colour, label=label)
    counts = [runs[shown[0]][bucket]["count"] for bucket in buckets]
    axes.set_xticks(positions)
    axes.set_xticklabels([f"{bucket} tokens\n(n={count})"
                          for bucket, count in zip(buckets, counts)],
                         fontsize=8)
    axes.set_ylim(0, 1.15)
    axes.set_ylabel("accuracy")
    axes.set_title("sequence models are supposed to win on long reviews",
                   fontsize=10)
    axes.legend(fontsize=7.5, loc="lower left", ncol=2)


def errors(fig, axes, p: Palette) -> None:
    info = _disagreement()
    left, right = fig.subplots(1, 2)
    labels = ("both right", "only the simple model",
              f"only {info['best_label']}", "both wrong")
    values = (info["both_right"], info["only_simple"], info["only_best"],
              info["both_wrong"])
    colours = (p.green, p.amber, p.blue, p.red)
    positions = np.arange(len(labels))
    left.bar(positions, values, 0.55, color=colours)
    for x, value in zip(positions, values):
        left.annotate(f"{value:,}\n({value / info['total']:.1%})", (x, value),
                      xytext=(0, 4), textcoords="offset points", ha="center",
                      fontsize=8, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=7.5, rotation=12, ha="right")
    left.set_ylim(0, max(values) * 1.3)
    left.set_ylabel(f"reviews (of {info['total']:,})")
    left.set_title("where the two models disagree", fontsize=10)

    runs = _ladder()
    simple = runs["bag of words + linear"]["accuracy"]
    best = runs[info["best_label"]]["accuracy"]
    bars = (("simple model", simple, p.amber),
            (info["best_label"], best, p.blue),
            ("pick the right one each time", info["oracle"], p.green))
    positions = np.arange(len(bars))
    right.bar(positions, [entry[1] for entry in bars], 0.5,
              color=[entry[2] for entry in bars])
    for x, entry in zip(positions, bars):
        right.annotate(f"{entry[1]:.4f}", (x, entry[1]), xytext=(0, 4),
                       textcoords="offset points", ha="center", fontsize=9,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([entry[0] for entry in bars], fontsize=7.5,
                          rotation=12, ha="right")
    right.set_ylim(0, 1.15)
    right.set_ylabel("accuracy")
    right.set_title("the two models fail on different reviews", fontsize=10)


FIGURES = [
    figure("ladder", ladder, size=(9.8, 3.6), axes=False),
    figure("length", length, size=(9.2, 3.4)),
    figure("errors", errors, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    data = _data()
    lengths = _lengths()
    print("=== the problem ===")
    print(f"IMDB sentiment, {len(data['y_train']):,} training reviews, "
          f"{len(data['y_test']):,} held out")
    print(f"vocabulary {VOCAB:,}, padded to {MAXLEN} tokens")
    print(f"true review lengths: median {int(np.median(lengths['train']))}, "
          f"mean {lengths['train'].mean():.0f}, "
          f"{(lengths['train'] > MAXLEN).mean():.1%} are truncated")

    print(f"\n=== the ladder ({EPOCHS} epochs each) ===")
    runs = _ladder()
    print(f"{'model':26s} {'parameters':>12} {'seconds':>8} {'accuracy':>9} "
          f"{'gain':>8}")
    previous = None
    for label, entry in runs.items():
        gain = "" if previous is None else f"{entry['accuracy'] - previous:+8.4f}"
        print(f"{label:26s} {entry['parameters']:12,} {entry['seconds']:8.0f} "
              f"{entry['accuracy']:9.4f} {gain:>8}")
        previous = entry["accuracy"]
    best = max((label for label in runs if runs[label]["probabilities"]
                is not None), key=lambda label: runs[label]["accuracy"])
    simple = runs["bag of words + linear"]["accuracy"]
    print(f"best: {best} at {runs[best]['accuracy']:.4f}")
    print(f"the bag-of-words linear model reached {simple:.4f} with no")
    print(f"sequence information whatsoever, in "
          f"{runs['bag of words + linear']['seconds']:.0f}s")

    print(f"\n=== accuracy by true review length ===")
    by_length = _by_length()
    buckets = list(next(iter(by_length.values())))
    print(f"{'model':26s} " + " ".join(f"{bucket:>12}" for bucket in buckets))
    for label, scores in by_length.items():
        print(f"{label:26s} "
              + " ".join(f"{scores[bucket]['accuracy']:12.4f}"
                         for bucket in buckets))
    counts = next(iter(by_length.values()))
    print("reviews per bucket: "
          + ", ".join(f"{bucket} n={counts[bucket]['count']}"
                      for bucket in buckets))
    print("if recurrence is buying anything it should show up in the last")
    print("column, where a bag of words has the most to lose")

    print(f"\n=== where the models disagree ===")
    info = _disagreement()
    print(f"simple and {info['best_label']} agree on "
          f"{info['agreement']:.4f} of reviews")
    print(f"  both right:            {info['both_right']:5,} "
          f"({info['both_right'] / info['total']:.1%})")
    print(f"  only the simple model: {info['only_simple']:5,} "
          f"({info['only_simple'] / info['total']:.1%})")
    print(f"  only {info['best_label']:19s}{info['only_best']:5,} "
          f"({info['only_best'] / info['total']:.1%})")
    print(f"  both wrong:            {info['both_wrong']:5,} "
          f"({info['both_wrong'] / info['total']:.1%})")
    print(f"picking the better model per review would give "
          f"{info['oracle']:.4f}")
    print("that oracle number is the argument for ensembling: the models fail")
    print("on different reviews, so their errors are not the same errors")

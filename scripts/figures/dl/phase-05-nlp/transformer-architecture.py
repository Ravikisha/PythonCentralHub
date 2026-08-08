"""Figures for *The Transformer Architecture*.

The encoder is assembled here from the parts measured on the attention page,
then compared against the recurrent models from Phase 4 on the same IMDB split
— so "transformers replaced RNNs" becomes a number rather than a slogan.

``block-anatomy``
    Where a transformer block's parameters actually go, and how the total
    scales with width and depth.

``against-recurrence``
    Transformer encoder, LSTM, GRU and a bag of words on one split, with
    wall-clock. The ranking is not the reading order.

``ablations``
    Remove one piece at a time — positional embeddings, the residuals, the
    feed-forward block, layer normalisation — and measure what each was worth.
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
LIMIT = 8000
EPOCHS = 6
WIDTH = 32
HEADS = 2
BLOCKS = 1
WIDTHS = (16, 32, 64, 128)
ABLATIONS = ("full block", "no positions", "no residuals", "no feed-forward",
             "no layer norm")
FAMILIES = ("bag of words", "GRU", "LSTM", "transformer")


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)


def _transformer(width: int = WIDTH, blocks: int = BLOCKS,
                 positions: bool = True, residuals: bool = True,
                 feed_forward: bool = True, normalise: bool = True,
                 seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((MAXLEN,))
    x = keras.layers.Embedding(VOCAB, width)(inputs)
    if positions:
        x = x + keras.layers.Embedding(MAXLEN, width)(tf().range(MAXLEN))
    for _ in range(blocks):
        normed = (keras.layers.LayerNormalization(epsilon=1e-6)(x)
                  if normalise else x)
        attention = keras.layers.MultiHeadAttention(
            num_heads=HEADS, key_dim=max(width // HEADS, 1))(normed, normed)
        x = keras.layers.Add()([x, attention]) if residuals else attention
        if feed_forward:
            normed = (keras.layers.LayerNormalization(epsilon=1e-6)(x)
                      if normalise else x)
            hidden = keras.layers.Dense(width * 2, activation="relu")(normed)
            hidden = keras.layers.Dense(width)(hidden)
            x = keras.layers.Add()([x, hidden]) if residuals else hidden
    pooled = keras.layers.GlobalAveragePooling1D()(x)
    model = keras.Model(inputs, keras.layers.Dense(1,
                                                   activation="sigmoid")(pooled))
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


def _recurrent(kind: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layer = (keras.layers.GRU if kind == "GRU" else keras.layers.LSTM)(WIDTH)
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, WIDTH, mask_zero=True),
        layer,
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


def _bag(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, WIDTH, mask_zero=True),
        keras.layers.GlobalAveragePooling1D(),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


def _fit(model) -> dict:
    data = _data()
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=64, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"accuracy": max(float(v) for v in history.history["val_accuracy"]),
            "curve": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started}


@functools.lru_cache(maxsize=1)
def _family_runs() -> dict:
    return {"bag of words": _fit(_bag()),
            "GRU": _fit(_recurrent("GRU")),
            "LSTM": _fit(_recurrent("LSTM")),
            "transformer": _fit(_transformer())}


@functools.lru_cache(maxsize=1)
def _ablation_runs() -> dict:
    settings = {
        "full block": {},
        "no positions": {"positions": False},
        "no residuals": {"residuals": False},
        "no feed-forward": {"feed_forward": False},
        "no layer norm": {"normalise": False},
    }
    return {label: _fit(_transformer(**kwargs))
            for label, kwargs in settings.items()}


def block_anatomy(fig, axes, p: Palette) -> None:
    keras = tf().keras
    left, right = fig.subplots(1, 2)
    width = WIDTH
    pieces = {
        "attention (Q,K,V,out)": 4 * (width * width + width),
        "feed-forward": width * width * 2 + width * 2 + width * 2 * width
                        + width,
        "layer norms (x2)": 4 * width,
        "position embedding": MAXLEN * width,
        "token embedding": VOCAB * width,
    }
    labels = list(pieces)
    values = [pieces[label] for label in labels]
    positions = np.arange(len(labels))
    left.barh(positions, values, 0.55,
              color=(p.blue, p.purple, p.amber, p.green, p.muted))
    for y, (label, value) in enumerate(zip(labels, values)):
        left.annotate(f"{value:,}", (value, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xscale("log")
    left.set_xlim(1, max(values) * 6)
    left.set_xlabel("parameters (log)")
    left.set_title(f"one block at width {width}, vocabulary {VOCAB:,}",
                   fontsize=10)

    totals, attention_share = [], []
    for candidate in WIDTHS:
        model = _transformer(width=candidate)
        total = model.count_params()
        block = 4 * (candidate ** 2 + candidate) + (
            candidate * candidate * 2 + candidate * 2
            + candidate * 2 * candidate + candidate)
        totals.append(total)
        attention_share.append(block / total)
        del model
    right.plot(WIDTHS, totals, "o-", ms=6, lw=2.0, color=p.blue,
               label="total parameters")
    right.set_xscale("log")
    right.set_yscale("log")
    right.minorticks_off()
    right.set_xticks(list(WIDTHS))
    right.set_xticklabels([str(w) for w in WIDTHS])
    right.set_xlabel("model width")
    right.set_ylabel("total parameters")
    twin = right.twinx()
    twin.plot(WIDTHS, attention_share, "o--", ms=6, lw=1.8, color=p.amber,
              label="share in the block")
    twin.set_ylabel("share of parameters inside the block")
    twin.set_ylim(0, 1)
    right.set_title("the embedding dominates until the model is wide",
                    fontsize=10)
    lines = right.get_lines() + twin.get_lines()
    right.legend(lines, [line.get_label() for line in lines], fontsize=8,
                 loc="center right")


def against_recurrence(fig, axes, p: Palette) -> None:
    runs = _family_runs()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(FAMILIES, (p.amber, p.blue, p.purple, p.green)))
    accuracy = [runs[f]["accuracy"] for f in FAMILIES]
    best = max(accuracy)
    positions = np.arange(len(FAMILIES))
    left.bar(positions, accuracy, 0.55,
             color=[p.green if abs(v - best) < 1e-12 else colors[f]
                    for f, v in zip(FAMILIES, accuracy)])
    for x, family, value in zip(positions, FAMILIES, accuracy):
        left.annotate(f"{value:.4f}\n{runs[family]['params']:,}\n"
                      f"{runs[family]['seconds']:.0f}s", (x, value),
                      textcoords="offset points", xytext=(0, 4), ha="center",
                      fontsize=7.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(FAMILIES, fontsize=8.5)
    left.set_ylim(0, 1.2)
    left.set_ylabel("best validation accuracy")
    left.set_title(f"IMDB, {LIMIT:,} reviews, {EPOCHS} epochs", fontsize=10)

    for family in FAMILIES:
        run = runs[family]
        right.plot(range(1, EPOCHS + 1), run["curve"], lw=1.9,
                   color=colors[family], label=family)
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title("attention converges in one pass over the sequence",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def ablations(fig, axes, p: Palette) -> None:
    runs = _ablation_runs()
    ax = fig.subplots(1, 1)
    full = runs["full block"]["accuracy"]
    values = [runs[label]["accuracy"] for label in ABLATIONS]
    deltas = [value - full for value in values]
    positions = np.arange(len(ABLATIONS))
    ax.bar(positions, values, 0.55,
           color=[p.green if label == "full block" else
                  (p.red if delta < -0.01 else p.blue)
                  for label, delta in zip(ABLATIONS, deltas)])
    for x, label, value, delta in zip(positions, ABLATIONS, values, deltas):
        text = f"{value:.4f}" if label == "full block" else \
            f"{value:.4f}\n{delta:+.4f}"
        ax.annotate(text, (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels([label.replace(" ", "\n") for label in ABLATIONS],
                       fontsize=8)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("best validation accuracy")
    ax.set_title(f"remove one piece at a time — {EPOCHS} epochs, "
                 f"width {WIDTH}", fontsize=10.5)


DEPTH_ROWS = 4000
DEPTH_EPOCHS = 4
DEPTHS = (1, 4)


@functools.lru_cache(maxsize=1)
def _depth_runs() -> dict:
    """Do residuals and layer norm earn their keep once the stack is deep?

    At one block every ablation *improved* the score, which is the opposite of
    the textbook claim. Residual connections and normalisation exist to keep a
    deep stack trainable, so the honest test is to repeat the ablation deeper
    rather than to explain the single-block result away.
    """
    data = _data()
    out = {}
    for blocks in DEPTHS:
        for label, kwargs in (("full", {}),
                              ("no residuals", {"residuals": False}),
                              ("no layer norm", {"normalise": False})):
            model = _transformer(blocks=blocks, **kwargs)
            history = model.fit(
                data["x_train"][:DEPTH_ROWS], data["y_train"][:DEPTH_ROWS],
                epochs=DEPTH_EPOCHS, batch_size=64, verbose=0,
                validation_data=(data["x_test"], data["y_test"]))
            out[(blocks, label)] = max(float(v) for v
                                       in history.history["val_accuracy"])
    return out


def depth_ablation(fig, axes, p: Palette) -> None:
    runs = _depth_runs()
    ax = fig.subplots(1, 1)
    labels = ("full", "no residuals", "no layer norm")
    positions = np.arange(len(labels))
    for offset, blocks, color in ((-0.19, DEPTHS[0], p.blue),
                                  (0.19, DEPTHS[1], p.green)):
        values = [runs[(blocks, label)] for label in labels]
        ax.bar(positions + offset, values, 0.36, color=color,
               label=f"{blocks} block{'s' if blocks > 1 else ''}")
        for x, value in zip(positions + offset, values):
            ax.annotate(f"{value:.4f}", (x, value),
                        textcoords="offset points", xytext=(0, 3),
                        ha="center", fontsize=7.5, color=p.fg)
    for index, label in enumerate(labels):
        shallow = runs[(DEPTHS[0], label)]
        deep = runs[(DEPTHS[1], label)]
        ax.annotate(f"{deep - shallow:+.4f}", (index, 0.05), ha="center",
                    fontsize=8.5,
                    color=p.green if deep >= shallow else p.red)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("best validation accuracy")
    ax.set_title(f"{DEPTH_ROWS:,} rows, {DEPTH_EPOCHS} epochs — what depth "
                 f"does to each ablation", fontsize=10.5)
    ax.legend(fontsize=8, loc="upper right")


FIGURES = [
    figure("block-anatomy", block_anatomy, size=(9.6, 3.6), axes=False),
    figure("depth-ablation", depth_ablation, size=(8.0, 3.8), axes=False),
    figure("against-recurrence", against_recurrence, size=(9.4, 3.6),
           axes=False),
    figure("ablations", ablations, size=(8.4, 3.8), axes=False),
]


if __name__ == "__main__":
    width = WIDTH
    print(f"=== where a block's parameters live (width {width}) ===")
    pieces = {
        "attention (Q,K,V,out)": 4 * (width * width + width),
        "feed-forward (2x expand)": width * width * 2 + width * 2
                                    + width * 2 * width + width,
        "layer norms (x2)": 4 * width,
        "position embedding": MAXLEN * width,
        "token embedding": VOCAB * width,
    }
    total = sum(pieces.values())
    for label, value in pieces.items():
        print(f"  {label:26s} {value:9,}  {value / total:7.2%}")
    print(f"  {'total':26s} {total:9,}")

    print(f"\n=== four families on one split, {EPOCHS} epochs ===")
    runs = _family_runs()
    print(f"{'family':14s} {'params':>10} {'best val acc':>13} "
          f"{'seconds':>9} {'epoch 1':>9}")
    for family in FAMILIES:
        run = runs[family]
        print(f"{family:14s} {run['params']:10,} {run['accuracy']:13.4f} "
              f"{run['seconds']:9.1f} {run['curve'][0]:9.4f}")
    baseline = runs["bag of words"]["accuracy"]
    for family in FAMILIES[1:]:
        print(f"  {family} against bag of words: "
              f"{runs[family]['accuracy'] - baseline:+.4f}")

    print(f"\n=== ablations ===")
    ablation_runs = _ablation_runs()
    full = ablation_runs["full block"]["accuracy"]
    print(f"{'setting':18s} {'params':>10} {'best val acc':>13} "
          f"{'vs full':>9}")
    for label in ABLATIONS:
        run = ablation_runs[label]
        print(f"{label:18s} {run['params']:10,} {run['accuracy']:13.4f} "
              f"{run['accuracy'] - full:+9.4f}")
    print("the pooled output is permutation-invariant without positions, so")
    print("that ablation measures how much this task needs word order at all")

    print(f"\n=== the same ablations at depth ({DEPTH_ROWS:,} rows, "
          f"{DEPTH_EPOCHS} epochs) ===")
    depth = _depth_runs()
    print(f"{'setting':16s} " + " ".join(f"{f'{b} block(s)':>12}"
                                         for b in DEPTHS)
          + f" {'deep - shallow':>15}")
    for label in ("full", "no residuals", "no layer norm"):
        row = [depth[(b, label)] for b in DEPTHS]
        print(f"{label:16s} " + " ".join(f"{v:12.4f}" for v in row)
              + f" {row[-1] - row[0]:+15.4f}")
    print("if residuals and normalisation are what make depth work, the deep")
    print("column should punish removing them harder than the shallow one")

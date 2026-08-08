"""Figures for *Padding, Masking and Variable-Length Sequences*.

``length-distribution``
    What ``pad_sequences`` actually does to a real corpus: how much of the batch
    is padding at each choice of ``maxlen``, and how much text is thrown away.

``masking-effect``
    Four combinations of pre/post padding and mask/no-mask. Three of them are
    fine and one is a silent bug, which is the point.

``pooling-with-padding``
    Why GlobalAveragePooling1D over an unmasked padded batch dilutes every
    review by its own padding, measured against the masked version.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import imdb, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

VOCAB = 10000
MAXLEN = 200
LIMIT = 5000
EPOCHS = 5
UNITS = 32
BATCH = 64
CANDIDATES = (50, 100, 200, 400, 800)
SETUPS = (("pre", False), ("pre", True), ("post", False), ("post", True))


@functools.lru_cache(maxsize=4)
def _corpus(padding: str = "pre") -> dict:
    keras = tf().keras
    data = imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)
    (x_train, y_train), (x_test, y_test) = keras.datasets.imdb.load_data(
        num_words=VOCAB)
    pad = keras.preprocessing.sequence.pad_sequences
    return {
        "x_train": pad(x_train[:LIMIT], maxlen=MAXLEN, padding=padding,
                       truncating=padding),
        "x_test": pad(x_test[:LIMIT // 2], maxlen=MAXLEN, padding=padding,
                      truncating=padding),
        "y_train": data["y_train"], "y_test": data["y_test"],
        "lengths": data["lengths"], "test_lengths": data["test_lengths"],
    }


def length_distribution(fig, axes, p: Palette) -> None:
    data = _corpus()
    lengths = data["lengths"]
    left, right = fig.subplots(1, 2)
    left.hist(lengths, bins=60, color=p.blue, alpha=0.85)
    left.axvline(MAXLEN, color=p.red, lw=1.6, ls="--")
    left.annotate(f"maxlen {MAXLEN}", (MAXLEN, left.get_ylim()[1] * 0.85),
                  xytext=(6, 0), textcoords="offset points", fontsize=8.5,
                  color=p.red)
    left.axvline(float(np.median(lengths)), color=p.green, lw=1.6)
    left.annotate(f"median {int(np.median(lengths))}",
                  (float(np.median(lengths)), left.get_ylim()[1] * 0.6),
                  xytext=(6, 0), textcoords="offset points", fontsize=8.5,
                  color=p.green)
    left.set_xlabel("tokens in the review")
    left.set_ylabel("reviews")
    left.set_title(f"IMDB review lengths ({LIMIT:,} reviews)", fontsize=10)

    padding_share, kept_share = [], []
    for candidate in CANDIDATES:
        padded = np.clip(candidate - lengths, 0, None).sum()
        padding_share.append(float(padded / (len(lengths) * candidate)))
        kept_share.append(float(np.minimum(lengths, candidate).sum()
                                / lengths.sum()))
    right.plot(CANDIDATES, padding_share, "o-", ms=6, lw=2.0, color=p.red,
               label="share of the batch that is padding")
    right.plot(CANDIDATES, kept_share, "o-", ms=6, lw=2.0, color=p.green,
               label="share of the real tokens kept")
    for candidate, a, b in zip(CANDIDATES, padding_share, kept_share):
        right.annotate(f"{a:.2f}", (candidate, a), textcoords="offset points",
                       xytext=(0, -12), ha="center", fontsize=7.5, color=p.red)
        right.annotate(f"{b:.2f}", (candidate, b), textcoords="offset points",
                       xytext=(0, 7), ha="center", fontsize=7.5, color=p.green)
    right.set_xscale("log")
    right.set_xticks(list(CANDIDATES))
    right.set_xticklabels([str(c) for c in CANDIDATES])
    right.set_xlabel("maxlen")
    right.set_ylabel("share")
    right.set_ylim(0, 1.05)
    right.set_title("every maxlen trades wasted compute against lost text",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="center right")


def _rnn(mask: bool, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, 32, mask_zero=mask),
        keras.layers.SimpleRNN(UNITS),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _masking_runs() -> dict:
    out = {}
    for padding, mask in SETUPS:
        data = _corpus(padding)
        model = _rnn(mask)
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=BATCH, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[(padding, mask)] = [float(v)
                                for v in history.history["val_accuracy"]]
    return out


def masking_effect(fig, axes, p: Palette) -> None:
    runs = _masking_runs()
    left, right = fig.subplots(1, 2)
    labels = [f"{padding}-padding\n{'mask_zero=True' if mask else 'no mask'}"
              for padding, mask in SETUPS]
    best = [max(runs[key]) for key in SETUPS]
    winner = max(best)
    colors = [p.green if abs(v - winner) < 1e-9 else
              (p.red if v == min(best) else p.blue) for v in best]
    positions = np.arange(len(SETUPS))
    left.bar(positions, best, 0.55, color=colors)
    for x, value in zip(positions, best):
        left.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=7.5)
    left.set_ylim(0, 1.0)
    left.set_ylabel("best validation accuracy")
    left.set_title(f"IMDB, {LIMIT:,} reviews, maxlen {MAXLEN}", fontsize=10)

    epochs = range(1, EPOCHS + 1)
    styles = {("pre", False): (p.blue, "-"), ("pre", True): (p.green, "-"),
              ("post", False): (p.red, "--"), ("post", True): (p.amber, "--")}
    for key in SETUPS:
        color, dash = styles[key]
        right.plot(epochs, runs[key], dash, lw=1.9, color=color,
                   label=f"{key[0]}-pad, {'masked' if key[1] else 'unmasked'}")
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title("post-padding without a mask is the one that breaks",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


@functools.lru_cache(maxsize=1)
def _pooling_runs() -> dict:
    keras = tf().keras
    out = {}
    for padding in ("pre", "post"):
        data = _corpus(padding)
        for mask in (False, True):
            seed_everything(0)
            model = keras.Sequential([
                keras.layers.Input((MAXLEN,)),
                keras.layers.Embedding(VOCAB, 32, mask_zero=mask),
                keras.layers.GlobalAveragePooling1D(),
                keras.layers.Dense(1, activation="sigmoid"),
            ])
            model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                          metrics=["accuracy"])
            history = model.fit(data["x_train"], data["y_train"],
                                epochs=EPOCHS, batch_size=BATCH, verbose=0,
                                validation_data=(data["x_test"],
                                                 data["y_test"]))
            out[(padding, mask)] = max(float(v) for v in
                                       history.history["val_accuracy"])
    return out


def pooling_with_padding(fig, axes, p: Palette) -> None:
    runs = _pooling_runs()
    data = _corpus()
    left, right = fig.subplots(1, 2)

    lengths = np.clip(data["lengths"], 1, MAXLEN)
    dilution = lengths / MAXLEN
    left.hist(dilution, bins=50, color=p.amber, alpha=0.85)
    left.axvline(float(dilution.mean()), color=p.fg, lw=1.6, ls="--")
    left.annotate(f"mean {dilution.mean():.4f}", (float(dilution.mean()), 0),
                  xytext=(6, 30), textcoords="offset points", fontsize=8.5,
                  color=p.fg)
    left.set_xlabel("weight an unmasked average gives to the real tokens")
    left.set_ylabel("reviews")
    left.set_title("a short review is scaled towards zero by its own padding",
                   fontsize=10)

    positions = np.arange(2)
    for offset, mask, color in ((-0.19, False, p.red), (0.19, True, p.green)):
        values = [runs[(padding, mask)] for padding in ("pre", "post")]
        right.bar(positions + offset, values, 0.36, color=color,
                  label="mask_zero=True" if mask else "no mask")
        for x, value in zip(positions + offset, values):
            right.annotate(f"{value:.4f}", (x, value),
                           textcoords="offset points", xytext=(0, 4),
                           ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(["pre-padding", "post-padding"])
    right.set_ylim(0, 1.0)
    right.set_ylabel("best validation accuracy")
    right.set_ylim(0, 1.05)
    right.set_title("GlobalAveragePooling1D, masked and not", fontsize=10)
    # The bars reach 0.80, so the lower corners are occupied.
    right.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("length-distribution", length_distribution, size=(9.4, 3.6),
           axes=False),
    figure("masking-effect", masking_effect, size=(9.6, 3.7), axes=False),
    figure("pooling-with-padding", pooling_with_padding, size=(9.4, 3.6),
           axes=False),
]


if __name__ == "__main__":
    keras = tf().keras
    data = _corpus()
    lengths = data["lengths"]
    print(f"=== {LIMIT:,} IMDB reviews, maxlen {MAXLEN} ===")
    print(f"length: min {lengths.min()}  median {int(np.median(lengths))}  "
          f"mean {lengths.mean():.1f}  p95 "
          f"{int(np.percentile(lengths, 95))}  max {lengths.max()}")
    print(f"{'maxlen':>7} {'padding share':>14} {'tokens kept':>12} "
          f"{'rows truncated':>15}")
    for candidate in CANDIDATES:
        padded = np.clip(candidate - lengths, 0, None).sum()
        print(f"{candidate:7d} "
              f"{float(padded / (len(lengths) * candidate)):14.4f} "
              f"{float(np.minimum(lengths, candidate).sum() / lengths.sum()):12.4f} "
              f"{float((lengths > candidate).mean()):15.4f}")

    print("\n=== what mask_zero actually produces ===")
    embedding = keras.layers.Embedding(VOCAB, 4, mask_zero=True)
    sample = np.array([[0, 0, 7, 9], [4, 5, 6, 8]])
    embedded = embedding(sample)
    mask = embedding.compute_mask(sample).numpy()
    print(f"input\n{sample}")
    print(f"mask\n{mask}")
    print(f"embedded shape {tuple(int(v) for v in embedded.shape)}  "
          f"the padded rows still have vectors: "
          f"{float(np.abs(embedded.numpy()[0, 0]).sum()):.4f} != 0")
    print("the mask travels with the tensor; it does not zero the values")

    print(f"\n=== SimpleRNN, four setups, {EPOCHS} epochs ===")
    runs = _masking_runs()
    print(f"{'padding':>8} {'mask':>6} {'best val acc':>13} {'final':>8}")
    for padding, mask in SETUPS:
        curve = runs[(padding, mask)]
        print(f"{padding:>8} {str(mask):>6} {max(curve):13.4f} {curve[-1]:8.4f}")

    print(f"\n=== GlobalAveragePooling1D, masked and not ===")
    pooling = _pooling_runs()
    print(f"{'padding':>8} {'no mask':>9} {'masked':>8} {'gain':>8}")
    for padding in ("pre", "post"):
        plain = pooling[(padding, False)]
        masked = pooling[(padding, True)]
        print(f"{padding:>8} {plain:9.4f} {masked:8.4f} {masked - plain:+8.4f}")
    dilution = np.clip(lengths, 1, MAXLEN) / MAXLEN
    print(f"mean weight an unmasked average gives the real tokens: "
          f"{float(dilution.mean()):.4f}")
    print(f"the shortest review in the sample gets {float(dilution.min()):.4f}")

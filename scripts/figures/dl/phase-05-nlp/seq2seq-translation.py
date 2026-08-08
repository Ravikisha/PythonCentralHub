"""Figures for *Sequence-to-Sequence Learning (Machine Translation)*.

Real translation corpora are large downloads, so the task here is date
normalisation: "3 mar 2019" -> "2019-03-03". It is a genuine sequence-to-
sequence problem — variable-length input, fixed grammar output, a reordering
between them — and the alignment is known, so an attention map can be checked
rather than admired.

``teacher-forcing``
    Training accuracy under teacher forcing against accuracy when the decoder
    has to consume its own output. The gap is exposure bias, measured.

``attention-effect``
    Encoder-decoder with and without attention, by input length — where the
    fixed-size bottleneck starts to hurt.

``alignment``
    The attention matrix for one example, against the alignment the task
    actually has.
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

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

ROWS = 8000
TEST_ROWS = 2000
# A bare date is far too easy: at 20 input characters both models scored a
# perfect 1.0000, so attention and exposure bias both measured exactly zero.
# The date is now buried in filler, which is what forces the model to find it
# and what makes a single fixed-size state a real bottleneck.
INPUT_LENGTH = 48
OUTPUT_LENGTH = 11          # "yyyy-mm-dd" plus the start token
EPOCHS = 12
WIDTH = 64
NOISE_WORDS = ("invoice", "ref", "paid", "due", "note", "order", "code",
               "batch", "line", "acct", "seq", "item", "no", "id")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
          "oct", "nov", "dec")
LONG_MONTHS = ("january", "february", "march", "april", "may", "june",
               "july", "august", "september", "october", "november",
               "december")
INPUT_ALPHABET = " -/0123456789abcdefghijklmnopqrstuvwxyz"
OUTPUT_ALPHABET = "\t0123456789-"
INPUT_INDEX = {character: index + 1
               for index, character in enumerate(INPUT_ALPHABET)}
OUTPUT_INDEX = {character: index
                for index, character in enumerate(OUTPUT_ALPHABET)}
OUTPUT_CHARS = list(OUTPUT_ALPHABET)


def _noise(rng) -> str:
    """A short run of filler: a word, sometimes with a number attached."""
    parts = []
    for _ in range(int(rng.integers(0, 3))):
        word = str(rng.choice(NOISE_WORDS))
        if rng.random() < 0.5:
            word = f"{word} {int(rng.integers(1, 99))}"
        parts.append(word)
    return " ".join(parts)


def _example(rng) -> tuple:
    year = int(rng.integers(1970, 2030))
    month = int(rng.integers(1, 13))
    day = int(rng.integers(1, 29))
    style = int(rng.integers(0, 4))
    if style == 0:
        date = f"{day} {MONTHS[month - 1]} {year}"
    elif style == 1:
        date = f"{LONG_MONTHS[month - 1]} {day} {year}"
    elif style == 2:
        date = f"{day:02d}/{month:02d}/{year}"
    else:
        date = f"{MONTHS[month - 1]} {day}, {year}".replace(",", "")
    before, after = _noise(rng), _noise(rng)
    text = " ".join(part for part in (before, date, after) if part)
    return text[:INPUT_LENGTH], f"{year:04d}-{month:02d}-{day:02d}"


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    rng = np.random.default_rng(0)
    sources, targets = [], []
    for _ in range(ROWS + TEST_ROWS):
        text, iso = _example(rng)
        sources.append(text)
        targets.append(iso)
    x = np.zeros((len(sources), INPUT_LENGTH), "int32")
    for row, text in enumerate(sources):
        for position, character in enumerate(text[:INPUT_LENGTH]):
            x[row, position] = INPUT_INDEX.get(character, 0)
    # Decoder input is the target shifted right behind a start token.
    decoder_input = np.zeros((len(targets), OUTPUT_LENGTH), "int32")
    decoder_target = np.zeros((len(targets), OUTPUT_LENGTH), "int32")
    for row, iso in enumerate(targets):
        sequence = [OUTPUT_INDEX["\t"]] + [OUTPUT_INDEX[c] for c in iso]
        decoder_input[row] = sequence[:OUTPUT_LENGTH]
        decoder_target[row] = (sequence[1:] + [0])[:OUTPUT_LENGTH]
    return {"x": x, "decoder_input": decoder_input,
            "decoder_target": decoder_target,
            "sources": sources, "targets": targets,
            "lengths": np.array([len(s) for s in sources])}


def _build(attention: bool, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    encoder_inputs = keras.layers.Input((INPUT_LENGTH,))
    embedded = keras.layers.Embedding(len(INPUT_ALPHABET) + 1, WIDTH,
                                      mask_zero=True)(encoder_inputs)
    encoder_sequence, state_h, state_c = keras.layers.LSTM(
        WIDTH, return_sequences=True, return_state=True,
        name="encoder_lstm")(embedded)

    decoder_inputs = keras.layers.Input((OUTPUT_LENGTH,))
    decoder_embedded = keras.layers.Embedding(len(OUTPUT_ALPHABET),
                                              WIDTH)(decoder_inputs)
    decoder_sequence = keras.layers.LSTM(WIDTH, return_sequences=True,
                                         name="decoder_lstm")(
        decoder_embedded, initial_state=[state_h, state_c])
    if attention:
        context = keras.layers.Attention()([decoder_sequence,
                                            encoder_sequence])
        merged = keras.layers.Concatenate()([decoder_sequence, context])
    else:
        merged = decoder_sequence
    outputs = keras.layers.Dense(len(OUTPUT_ALPHABET),
                                 activation="softmax")(merged)
    model = keras.Model([encoder_inputs, decoder_inputs], outputs)
    model.compile(keras.optimizers.Adam(2e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def _greedy_decode(model, x) -> np.ndarray:
    """Free-running decode: feed the model its own previous character."""
    rows = len(x)
    decoder_input = np.zeros((rows, OUTPUT_LENGTH), "int32")
    decoder_input[:, 0] = OUTPUT_INDEX["\t"]
    for position in range(OUTPUT_LENGTH - 1):
        predictions = model.predict([x, decoder_input], verbose=0)
        decoder_input[:, position + 1] = predictions[:, position].argmax(axis=-1)
    return decoder_input[:, 1:]


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    data = _corpus()
    x_train = data["x"][:ROWS]
    x_test = data["x"][ROWS:]
    out = {}
    for attention in (False, True):
        model = _build(attention)
        started = time.perf_counter()
        history = model.fit(
            [x_train, data["decoder_input"][:ROWS]],
            data["decoder_target"][:ROWS], epochs=EPOCHS, batch_size=128,
            verbose=0,
            validation_data=([x_test, data["decoder_input"][ROWS:]],
                             data["decoder_target"][ROWS:]))
        elapsed = time.perf_counter() - started
        forced = float(history.history["val_accuracy"][-1])
        decoded = _greedy_decode(model, x_test)
        truth = data["decoder_target"][ROWS:][:, :OUTPUT_LENGTH - 1]
        character = float((decoded == truth).mean())
        exact = float((decoded == truth).all(axis=1).mean())
        label = "with attention" if attention else "no attention"
        out[label] = {"forced": forced, "character": character,
                      "exact": exact, "seconds": elapsed,
                      "params": int(model.count_params()),
                      "curve": [float(v)
                                for v in history.history["val_accuracy"]],
                      "decoded": decoded, "model": model}
    out["truth"] = data["decoder_target"][ROWS:][:, :OUTPUT_LENGTH - 1]
    out["lengths"] = data["lengths"][ROWS:]
    out["sources"] = data["sources"][ROWS:]
    out["targets"] = data["targets"][ROWS:]
    return out


def teacher_forcing(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    labels = ("no attention", "with attention")
    metrics = ("forced", "character", "exact")
    names = ("teacher-forced accuracy", "free-running character accuracy",
             "free-running exact match")
    colors = (p.amber, p.blue, p.green)
    positions = np.arange(len(labels))
    width = 0.8 / len(metrics)
    for index, (metric, name, color) in enumerate(zip(metrics, names, colors)):
        offset = (index - (len(metrics) - 1) / 2) * width
        values = [runs[label][metric] for label in labels]
        left.bar(positions + offset, values, width * 0.92, color=color,
                 label=name)
        for x, value in zip(positions + offset, values):
            left.annotate(f"{value:.3f}", (x, value),
                          textcoords="offset points", xytext=(0, 3),
                          ha="center", fontsize=7, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=9)
    left.set_ylim(0, 1.18)
    left.set_ylabel("accuracy")
    left.set_title(f"{TEST_ROWS:,} held-out dates, {EPOCHS} epochs",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower left")

    for label, color in (("no attention", p.red), ("with attention", p.green)):
        run = runs[label]
        right.plot(range(1, EPOCHS + 1), run["curve"], lw=2.0, color=color,
                   label=f"{label} — {run['seconds']:.0f}s")
    right.set_xlabel("epoch")
    right.set_ylabel("teacher-forced validation accuracy")
    right.set_title("training is easier than inference", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def attention_effect(fig, axes, p: Palette) -> None:
    runs = _runs()
    ax = fig.subplots(1, 1)
    lengths = runs["lengths"]
    truth = runs["truth"]
    bins = [(0, 16), (16, 24), (24, 32), (32, 49)]
    centres = [f"{low}-{high - 1}" for low, high in bins]
    positions = np.arange(len(bins))
    for label, color, offset in (("no attention", p.red, -0.19),
                                 ("with attention", p.green, 0.19)):
        decoded = runs[label]["decoded"]
        values = []
        for low, high in bins:
            mask = (lengths >= low) & (lengths < high)
            values.append(float((decoded[mask] == truth[mask]).all(axis=1).mean())
                          if mask.sum() else 0.0)
        ax.bar(positions + offset, values, 0.36, color=color, label=label)
        for x, value in zip(positions + offset, values):
            ax.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                        xytext=(0, 3), ha="center", fontsize=7.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(centres)
    ax.set_xlabel("input length in characters")
    ax.set_ylabel("free-running exact-match rate")
    ax.set_ylim(0, 1.15)
    ax.set_title("the fixed-size bottleneck hurts most on long inputs",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")


def alignment(fig, axes, p: Palette) -> None:
    keras = tf().keras
    runs = _runs()
    data = _corpus()
    model = runs["with attention"]["model"]
    # Rebuild the attention scores by hand from the two sequence tensors.
    # The layers are named, because picking them out by index silently
    # returned the wrong tensor and produced a (11, 11) score matrix for a
    # 20-character input.
    encoder_sequence = model.get_layer("encoder_lstm").output[0]
    decoder_sequence = model.get_layer("decoder_lstm").output
    probe = keras.Model(model.inputs, [encoder_sequence, decoder_sequence])
    row = int(np.argmax(runs["lengths"] >= 13))
    x = data["x"][ROWS:][row:row + 1]
    decoder_input = data["decoder_input"][ROWS:][row:row + 1]
    encoded, decoded = probe.predict([x, decoder_input], verbose=0)
    scores = decoded[0] @ encoded[0].T
    scores = scores - scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores)
    mask = (x[0] != 0).astype("float32")
    weights = weights * mask
    weights = weights / (weights.sum(axis=-1, keepdims=True) + 1e-9)

    source = runs["sources"][row]
    target = runs["targets"][row]
    ax = fig.subplots(1, 1)
    image = ax.imshow(weights[:len(target), :len(source)], cmap="magma",
                      aspect="auto")
    ax.set_xticks(range(len(source)))
    ax.set_xticklabels(list(source), fontsize=9)
    ax.set_yticks(range(len(target)))
    ax.set_yticklabels(list(target), fontsize=9)
    ax.set_xlabel("input characters")
    ax.set_ylabel("output characters")
    ax.set_title(f"attention for {source!r} -> {target!r}", fontsize=10.5)
    ax.grid(False)
    fig.colorbar(image, ax=ax, pad=0.01, fraction=0.03)


FIGURES = [
    figure("teacher-forcing", teacher_forcing, size=(9.4, 3.6), axes=False),
    figure("attention-effect", attention_effect, size=(8.0, 3.8), axes=False),
    figure("alignment", alignment, size=(8.6, 3.8), axes=False),
]


if __name__ == "__main__":
    data = _corpus()
    print(f"=== date normalisation: {ROWS:,} train / {TEST_ROWS:,} test ===")
    for row in range(6):
        print(f"  {data['sources'][row]:>22}  ->  {data['targets'][row]}")
    print(f"input alphabet {len(INPUT_ALPHABET)} characters, output alphabet "
          f"{len(OUTPUT_ALPHABET)}")
    print(f"input length: min {data['lengths'].min()}  max "
          f"{data['lengths'].max()}  mean {data['lengths'].mean():.1f}")

    runs = _runs()
    print(f"\n=== teacher forcing against free running, {EPOCHS} epochs ===")
    print(f"{'model':16s} {'params':>9} {'teacher-forced':>15} "
          f"{'free char':>10} {'free exact':>11} {'seconds':>9}")
    for label in ("no attention", "with attention"):
        run = runs[label]
        print(f"{label:16s} {run['params']:9,} {run['forced']:15.4f} "
              f"{run['character']:10.4f} {run['exact']:11.4f} "
              f"{run['seconds']:9.1f}")
    for label in ("no attention", "with attention"):
        run = runs[label]
        print(f"  {label}: exposure bias costs "
              f"{run['forced'] - run['character']:+.4f} character accuracy")

    print("\n=== exact match by input length ===")
    lengths = runs["lengths"]
    truth = runs["truth"]
    print(f"{'length':>10} {'rows':>7} {'no attention':>14} "
          f"{'with attention':>15}")
    for low, high in ((0, 16), (16, 24), (24, 32), (32, 49)):
        mask = (lengths >= low) & (lengths < high)
        if not mask.sum():
            continue
        without = float((runs["no attention"]["decoded"][mask]
                         == truth[mask]).all(axis=1).mean())
        with_attention = float((runs["with attention"]["decoded"][mask]
                                == truth[mask]).all(axis=1).mean())
        print(f"{f'{low}-{high - 1}':>10} {int(mask.sum()):7,} "
              f"{without:14.4f} {with_attention:15.4f}")

    print("\n=== a few free-running decodes (with attention) ===")
    decoded = runs["with attention"]["decoded"]
    for row in range(6):
        text = "".join(OUTPUT_CHARS[int(index)] for index in decoded[row]
                       if index)
        flag = "ok " if text == runs["targets"][row] else "BAD"
        print(f"  {flag} {runs['sources'][row]:>22} -> {text:12s} "
              f"(want {runs['targets'][row]})")

"""Figures for *Text Generation with LSTMs*.

Almost every text-generation tutorial prints a sample at three temperatures and
asserts which one is best. This module scores them instead. The corpus is real
English, so "is this a dictionary word" is a measurable proxy for quality, and
diversity is measurable as the share of distinct n-grams. The two move in
opposite directions, which is the actual lesson of the page.

``temperature-sweep``
    Word validity and n-gram diversity against temperature, on the same
    generated text -- the trade-off with numbers on it.

``sampling-strategies``
    Greedy, temperature, top-k and nucleus sampling scored on the same axes,
    plus how often each one gets stuck in a loop.

``training-progress``
    Loss per epoch next to word validity per epoch, because loss alone does not
    say when the samples become English.
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

from _dl import seed_everything, text_corpus, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

REVIEWS = 2500
WINDOW = 40
STRIDE = 6
UNITS = 128
EPOCHS = 10
SAMPLES = 24
LENGTH = 240
# An LSTM step over a 40-character window costs about a second per batch of 256
# on this CPU, so the window count is what sets the wall-clock. 120k windows and
# 15 epochs measured out at roughly 1.75 hours; this budget lands near ten
# minutes. The model is correspondingly weak, and the page says so rather than
# implying these are the numbers a serious character model would produce.
WINDOW_CAP = 40000
TEMPERATURES = (0.2, 0.5, 0.8, 1.0, 1.5)
CHECKPOINTS = (1, 3, 6, 10)


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    info = text_corpus(reviews=REVIEWS)
    chars = info["chars"]
    return {**info,
            "index": {char: number for number, char in enumerate(chars)},
            "lookup": {number: char for number, char in enumerate(chars)}}


@functools.lru_cache(maxsize=1)
def _windows() -> dict:
    """Overlapping character windows, and the next character for each."""
    info = _corpus()
    text, index = info["text"], info["index"]
    encoded = np.array([index[char] for char in text], dtype="int32")
    window = max(8, int(WINDOW))
    starts = np.arange(0, len(encoded) - window - 1, max(1, int(STRIDE)))
    total = len(starts)
    if total > WINDOW_CAP:
        # Thin evenly rather than truncating, so the windows still span the
        # whole corpus instead of only its first few hundred reviews.
        starts = starts[np.linspace(0, total - 1, WINDOW_CAP).astype(int)]
    x = np.stack([encoded[start:start + window] for start in starts])
    y = encoded[starts + window]
    split = int(len(x) * 0.9)
    return {"x_train": x[:split], "y_train": y[:split],
            "x_val": x[split:], "y_val": y[split:],
            "chars": len(info["chars"]), "window": window,
            "available": int(total)}


@functools.lru_cache(maxsize=1)
def _model() -> dict:
    """One character-level LSTM, with a sample scored after every epoch."""
    keras = tf().keras
    windows = _windows()
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((windows["window"],)),
        keras.layers.Embedding(windows["chars"], 32),
        keras.layers.LSTM(UNITS),
        keras.layers.Dense(windows["chars"], activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy")

    started = time.perf_counter()
    progress = []
    checkpoints = {}
    for epoch in range(1, max(1, int(EPOCHS)) + 1):
        history = model.fit(windows["x_train"], windows["y_train"], epochs=1,
                            batch_size=256, verbose=0,
                            validation_data=(windows["x_val"],
                                             windows["y_val"]))
        text = _generate(model, 1, temperature=0.5, length=150, seed=1)[0]
        scored = _score(text)
        progress.append({"epoch": epoch,
                         "loss": float(history.history["loss"][0]),
                         "val_loss": float(history.history["val_loss"][0]),
                         **scored})
        if epoch in CHECKPOINTS or epoch == max(1, int(EPOCHS)):
            checkpoints[epoch] = text
    return {"model": model, "progress": progress, "checkpoints": checkpoints,
            "seconds": time.perf_counter() - started}


def _pick(probabilities, temperature=1.0, top_k=0, top_p=0.0, rng=None):
    """One sampling step for one row. temperature=0 means greedy."""
    if temperature <= 0:
        return int(np.argmax(probabilities))
    scaled = np.log(np.clip(probabilities, 1e-12, None)) / temperature
    scaled = np.exp(scaled - scaled.max())
    scaled /= scaled.sum()
    if top_k:
        keep = np.argsort(scaled)[-int(top_k):]
        mask = np.zeros_like(scaled)
        mask[keep] = scaled[keep]
        scaled = mask / mask.sum()
    if top_p:
        order = np.argsort(scaled)[::-1]
        cumulative = np.cumsum(scaled[order])
        # Always keep the first token, or a very peaked step keeps nothing.
        cut = int(np.searchsorted(cumulative, top_p)) + 1
        mask = np.zeros_like(scaled)
        mask[order[:cut]] = scaled[order[:cut]]
        scaled = mask / mask.sum()
    return int((rng or np.random).choice(len(scaled), p=scaled))


def _generate(model, count=1, temperature=1.0, length=LENGTH, top_k=0,
              top_p=0.0, seed=0) -> list:
    """Generate `count` samples together.

    One forward pass per character *for the whole batch*, not per sample: a
    single-row predict costs the same as a 40-row predict here, so generating
    samples one at a time would multiply the wall-clock by `count` for nothing.
    """
    info = _corpus()
    windows = _windows()
    rng = np.random.default_rng(seed)
    text, window = info["text"], windows["window"]
    starts = rng.integers(0, len(text) - window - 1, int(count))
    context = np.stack([
        [info["index"][char] for char in text[start:start + window]]
        for start in starts]).astype("int32")
    produced = [[] for _ in range(int(count))]
    for _ in range(int(length)):
        probabilities = model.predict(context, verbose=0).astype("float64")
        tokens = [_pick(row, temperature, top_k, top_p, rng)
                  for row in probabilities]
        for row, token in enumerate(tokens):
            produced[row].append(info["lookup"][token])
        context = np.concatenate(
            [context[:, 1:], np.array(tokens, "int32")[:, None]], axis=1)
    return ["".join(row) for row in produced]


def _score(text: str) -> dict:
    """Word validity, diversity and repetition -- all computable, none eyeballed."""
    info = _corpus()
    tokens = [token for token in text.split() if token]
    # Drop the first and last token: both are usually cut mid-word.
    inner = tokens[1:-1] if len(tokens) > 2 else tokens
    valid = [token for token in inner if token in info["words"]]
    bigrams = list(zip(inner, inner[1:]))
    longest = 0
    run = 1
    for previous, current in zip(inner, inner[1:]):
        run = run + 1 if current == previous else 1
        longest = max(longest, run)
    return {"validity": len(valid) / max(1, len(inner)),
            "distinct_words": len(set(inner)) / max(1, len(inner)),
            "distinct_bigrams": len(set(bigrams)) / max(1, len(bigrams)),
            "longest_repeat": longest,
            "words": len(inner)}


def _mean_score(temperature=1.0, top_k=0, top_p=0.0, samples=SAMPLES) -> dict:
    model = _model()["model"]
    keys = ("validity", "distinct_words", "distinct_bigrams",
            "longest_repeat", "words")
    texts = _generate(model, int(samples), temperature, LENGTH, top_k, top_p,
                      seed=4)
    scored = [_score(text) for text in texts]
    out = {key: float(np.mean([entry[key] for entry in scored]))
           for key in keys}
    out["validity_sd"] = float(np.std([entry["validity"] for entry in scored]))
    out["example"] = texts[0][:220]
    return out


@functools.lru_cache(maxsize=1)
def _temperature_runs() -> dict:
    return {temperature: _mean_score(temperature)
            for temperature in TEMPERATURES}


@functools.lru_cache(maxsize=1)
def _strategy_runs() -> dict:
    return {
        "greedy": _mean_score(0.0, samples=max(4, SAMPLES // 4)),
        "T=0.5": _mean_score(0.5),
        "T=1.0": _mean_score(1.0),
        "top-k=5, T=1.0": _mean_score(1.0, top_k=5),
        "nucleus p=0.9, T=1.0": _mean_score(1.0, top_p=0.9),
    }


@functools.lru_cache(maxsize=1)
def _real_baseline() -> dict:
    """The corpus itself, scored the same way: the ceiling for every metric."""
    info = _corpus()
    rng = np.random.default_rng(0)
    text = info["text"]
    scores = []
    for _ in range(SAMPLES):
        start = int(rng.integers(0, len(text) - LENGTH - 1))
        scores.append(_score(text[start:start + LENGTH]))
    return {key: float(np.mean([entry[key] for entry in scores]))
            for key in ("validity", "distinct_words", "distinct_bigrams",
                        "longest_repeat")}


def temperature_sweep(fig, axes, p: Palette) -> None:
    runs = _temperature_runs()
    real = _real_baseline()
    left, right = fig.subplots(1, 2)
    temperatures = list(runs)
    validity = [runs[t]["validity"] for t in temperatures]
    spread = [runs[t]["validity_sd"] for t in temperatures]
    left.errorbar(temperatures, validity, yerr=spread, fmt="o-", ms=6, lw=2.0,
                  capsize=3, color=p.green, label="share of real English words")
    left.axhline(real["validity"], color=p.muted, lw=1.2, ls="--",
                 label=f"the corpus itself ({real['validity']:.4f})")
    for temperature, value in zip(temperatures, validity):
        left.annotate(f"{value:.3f}", (temperature, value), xytext=(0, 9),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.green)
    left.set_xlabel("temperature")
    left.set_ylabel("word validity")
    left.set_ylim(0, 1.08)
    left.set_title(f"mean of {SAMPLES} samples, {LENGTH} characters each",
                   fontsize=10)
    left.legend(fontsize=8, loc="lower left")

    diversity = [runs[t]["distinct_bigrams"] for t in temperatures]
    unique_words = [runs[t]["distinct_words"] for t in temperatures]
    right.plot(temperatures, diversity, "o-", ms=6, lw=2.0, color=p.blue,
               label="distinct word bigrams")
    right.plot(temperatures, unique_words, "s-", ms=5, lw=2.0, color=p.purple,
               label="distinct words")
    right.axhline(real["distinct_bigrams"], color=p.muted, lw=1.2, ls="--",
                  label=f"corpus bigrams ({real['distinct_bigrams']:.4f})")
    for temperature, value in zip(temperatures, diversity):
        right.annotate(f"{value:.3f}", (temperature, value), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.blue)
    right.set_xlabel("temperature")
    right.set_ylabel("distinct fraction")
    right.set_ylim(0, 1.15)
    right.set_title("diversity rises exactly where validity falls", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def sampling_strategies(fig, axes, p: Palette) -> None:
    runs = _strategy_runs()
    real = _real_baseline()
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    labels = list(runs)
    positions = np.arange(len(labels))
    metrics = (("validity", "word validity", p.green),
               ("distinct_bigrams", "distinct bigrams", p.blue))
    width = 0.38
    for index, (key, name, color) in enumerate(metrics):
        offset = (index - 0.5) * width
        values = [runs[label][key] for label in labels]
        left.bar(positions + offset, values, width * 0.9, color=color,
                 label=name)
        left.axhline(real[key], color=color, lw=1.0, ls=":")
        for x, value in zip(positions + offset, values):
            left.annotate(f"{value:.3f}", (x, value), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=6.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=7.5, rotation=20, ha="right")
    left.set_ylim(0, 1.2)
    left.set_ylabel("score")
    left.set_title("dotted lines are the corpus itself", fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    repeats = [runs[label]["longest_repeat"] for label in labels]
    right.barh(positions, repeats, 0.55, color=p.amber)
    right.axvline(real["longest_repeat"], color=p.muted, lw=1.2, ls="--",
                  label=f"corpus ({real['longest_repeat']:.2f})")
    for y, value in zip(positions, repeats):
        right.annotate(f"{value:.2f}", (value, y), xytext=(6, 0),
                       textcoords="offset points", va="center", fontsize=8,
                       color=p.fg)
    right.set_yticks(positions)
    right.set_yticklabels(labels, fontsize=7.5)
    right.invert_yaxis()
    right.set_xlim(0, max(repeats + [real["longest_repeat"]]) * 1.45)
    right.set_xlabel("longest run of one repeated word")
    right.set_title("greedy decoding is where loops live", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def training_progress(fig, axes, p: Palette) -> None:
    info = _model()
    real = _real_baseline()
    progress = info["progress"]
    epochs = [entry["epoch"] for entry in progress]
    left, right = fig.subplots(1, 2)
    left.plot(epochs, [entry["loss"] for entry in progress], lw=2.0,
              color=p.blue, label="training loss")
    left.plot(epochs, [entry["val_loss"] for entry in progress], lw=2.0,
              color=p.red, label="validation loss")
    best = min(entry["val_loss"] for entry in progress)
    left.axhline(best, color=p.muted, lw=1.0, ls=":")
    left.annotate(f"best {best:.4f}", (epochs[0], best), xytext=(4, 5),
                  textcoords="offset points", fontsize=7.5, color=p.muted)
    left.set_xlabel("epoch")
    left.set_ylabel("cross-entropy per character")
    left.set_title(f"{info['seconds']:.0f}s total", fontsize=10)
    left.legend(fontsize=8)

    validity = [entry["validity"] for entry in progress]
    right.plot(epochs, validity, "o-", ms=5, lw=2.0, color=p.green,
               label="word validity of a sample at T=0.5")
    right.axhline(real["validity"], color=p.muted, lw=1.2, ls="--",
                  label=f"the corpus itself ({real['validity']:.4f})")
    right.set_xlabel("epoch")
    right.set_ylabel("word validity")
    right.set_ylim(0, 1.08)
    right.set_title("loss keeps falling after the text stops improving",
                    fontsize=10)
    right.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("temperature-sweep", temperature_sweep, size=(9.4, 3.6), axes=False),
    figure("sampling-strategies", sampling_strategies, size=(9.6, 3.7),
           axes=False),
    figure("training-progress", training_progress, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    info = _corpus()
    windows = _windows()
    print(f"=== the corpus: {info['reviews']:,} IMDB reviews decoded to text ===")
    print(f"{len(info['text']):,} characters, {len(info['chars'])} distinct, "
          f"{len(info['words']):,} dictionary words")
    print(f"{len(windows['x_train']):,} training windows of "
          f"{windows['window']} characters, stride {STRIDE} "
          f"(thinned evenly from {windows['available']:,} available)")

    model = _model()
    print(f"\n=== training, {model['model'].count_params():,} parameters, "
          f"{model['seconds']:.0f}s ===")
    print(f"{'epoch':>6} {'loss':>9} {'val loss':>9} {'validity':>9} "
          f"{'distinct bigrams':>17}")
    for entry in model["progress"]:
        print(f"{entry['epoch']:6d} {entry['loss']:9.4f} "
              f"{entry['val_loss']:9.4f} {entry['validity']:9.4f} "
              f"{entry['distinct_bigrams']:17.4f}")

    real = _real_baseline()
    print(f"\n=== the corpus scored the same way (the ceiling) ===")
    print(f"validity {real['validity']:.4f}, distinct words "
          f"{real['distinct_words']:.4f}, distinct bigrams "
          f"{real['distinct_bigrams']:.4f}, longest repeat "
          f"{real['longest_repeat']:.2f}")

    print(f"\n=== temperature, mean of {SAMPLES} samples of {LENGTH} chars ===")
    runs = _temperature_runs()
    print(f"{'T':>5} {'validity':>9} {'(sd)':>7} {'distinct words':>15} "
          f"{'distinct bigrams':>17} {'longest repeat':>15}")
    for temperature, entry in runs.items():
        print(f"{temperature:5.1f} {entry['validity']:9.4f} "
              f"{entry['validity_sd']:7.4f} {entry['distinct_words']:15.4f} "
              f"{entry['distinct_bigrams']:17.4f} "
              f"{entry['longest_repeat']:15.2f}")

    print(f"\n=== sampling strategies ===")
    strategies = _strategy_runs()
    print(f"{'strategy':22s} {'validity':>9} {'distinct words':>15} "
          f"{'distinct bigrams':>17} {'longest repeat':>15}")
    for label, entry in strategies.items():
        print(f"{label:22s} {entry['validity']:9.4f} "
              f"{entry['distinct_words']:15.4f} "
              f"{entry['distinct_bigrams']:17.4f} "
              f"{entry['longest_repeat']:15.2f}")

    print("\n=== what each strategy actually writes (220 characters) ===")
    for label, entry in strategies.items():
        print(f"\n[{label}]\n{entry['example']}")

    print("\n=== samples during training, T=0.5 ===")
    for epoch, text in _model()["checkpoints"].items():
        print(f"\n[epoch {epoch}]\n{text[:200]}")

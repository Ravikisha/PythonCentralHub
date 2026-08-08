"""Figures for *Evaluating Language Models (Perplexity and BLEU)*.

Both metrics are implemented here rather than imported, because both are
routinely misread: perplexity is compared across models with different
tokenizers, and BLEU is quoted without its brevity penalty or its n-gram order.

``perplexity-ladder``
    Uniform, unigram, bigram and a small neural model on the same held-out
    text, so "perplexity 120" has something to sit next to.

``bleu-anatomy``
    What each part of BLEU does: n-gram order, the brevity penalty, and the
    cases where a sensible translation scores zero.

``length-and-temperature``
    Sampling temperature against perplexity and output diversity — the
    trade-off every text-generation demo hides.
"""

from __future__ import annotations

import functools
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

DOCUMENTS = 4000
VOCAB = 5000
CONTEXT = 8
# At 6 epochs over 120,000 windows the neural model scored 437.56 — worse than
# a smoothed bigram and barely better than a unigram, because most of its
# 1,030,085 parameters live in the output layer and had seen very little data.
EPOCHS = 14
WIDTH = 64
TRAIN_WINDOWS = 260000
INDEX_OFFSET = 3
TEMPERATURES = (0.2, 0.5, 0.8, 1.0, 1.5)


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    """Decoded IMDB, capped to a small vocabulary, split into train and test."""
    keras = tf().keras
    (x_train, _), (x_test, _) = keras.datasets.imdb.load_data(num_words=VOCAB)
    word_index = keras.datasets.imdb.get_word_index()
    reverse = {index + INDEX_OFFSET: word for word, index in word_index.items()}
    train = [[reverse.get(t, "<oov>") for t in row] for row in x_train[:DOCUMENTS]]
    test = [[reverse.get(t, "<oov>") for t in row]
            for row in x_test[:DOCUMENTS // 4]]
    vocabulary = sorted({token for document in train for token in document})
    lookup = {word: index for index, word in enumerate(vocabulary)}
    return {"train": train, "test": test, "vocabulary": vocabulary,
            "lookup": lookup}


@functools.lru_cache(maxsize=1)
def _windows() -> dict:
    """The evaluation set, shared by every model on this page.

    The first version of this module scored the n-gram models on all 231,210
    held-out tokens and the neural model on 30,000 windows, then printed the
    two in one table. Perplexity is an average over whatever you scored, so
    that comparison was meaningless. Every model now sees the same windows.
    """
    data = _corpus()
    lookup = data["lookup"]

    def build(documents, cap):
        contexts, targets = [], []
        for document in documents:
            ids = [lookup[token] for token in document if token in lookup]
            for index in range(CONTEXT, len(ids)):
                contexts.append(ids[index - CONTEXT:index])
                targets.append(ids[index])
                if len(contexts) >= cap:
                    return np.array(contexts), np.array(targets)
        return np.array(contexts), np.array(targets)

    x_train, y_train = build(data["train"], TRAIN_WINDOWS)
    x_test, y_test = build(data["test"], 30000)
    return {"x_train": x_train, "y_train": y_train,
            "x_test": x_test, "y_test": y_test,
            "vocabulary": data["vocabulary"], "lookup": lookup}


@functools.lru_cache(maxsize=1)
def _ngram_models() -> dict:
    """Uniform, unigram and add-k bigram, scored on the shared windows."""
    data = _corpus()
    windows = _windows()
    size = len(data["vocabulary"])
    unigram = Counter()
    bigram = defaultdict(Counter)
    for document in data["train"]:
        previous = "<s>"
        for token in document:
            unigram[token] += 1
            bigram[previous][token] += 1
            previous = token
    total = sum(unigram.values())
    k = 0.1
    vocabulary = data["vocabulary"]

    def uniform_scorer(previous, token):
        return 1.0 / size

    def unigram_scorer(previous, token):
        return (unigram[token] + k) / (total + k * size)

    def bigram_scorer(previous, token):
        row = bigram.get(previous)
        if row is None:
            return unigram_scorer(previous, token)
        return (row[token] + k) / (sum(row.values()) + k * size)

    # The same (context, target) pairs the neural model is scored on: the
    # bigram only looks at the last context token.
    previous_words = [vocabulary[index] for index in windows["x_test"][:, -1]]
    target_words = [vocabulary[index] for index in windows["y_test"]]

    out = {}
    for label, scorer in (("uniform", uniform_scorer),
                          ("unigram", unigram_scorer),
                          ("bigram (add-0.1)", bigram_scorer)):
        log_probability = sum(math.log(scorer(previous, token))
                              for previous, token in zip(previous_words,
                                                         target_words))
        out[label] = {"perplexity": math.exp(-log_probability
                                             / len(target_words)),
                      "tokens": len(target_words)}
    out["vocabulary"] = size
    return out


@functools.lru_cache(maxsize=1)
def _neural_model() -> dict:
    """A small fixed-context neural language model, scored the same way."""
    keras = tf().keras
    windows = _windows()
    size = len(windows["vocabulary"])
    x_train, y_train = windows["x_train"], windows["y_train"]
    x_test, y_test = windows["x_test"], windows["y_test"]
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((CONTEXT,)),
        keras.layers.Embedding(size, WIDTH),
        keras.layers.Flatten(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(WIDTH * 2, activation="relu"),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(size, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(2e-3),
                  "sparse_categorical_crossentropy")
    history = model.fit(x_train, y_train, epochs=EPOCHS, batch_size=256,
                        verbose=0, validation_data=(x_test, y_test))
    # The *best* epoch, not the last. Most of this model's 1,030,085
    # parameters are in the output layer, so it overfits hard: reading the
    # final epoch reported perplexity 4,062 where the minimum was far lower.
    loss = float(min(history.history["val_loss"]))
    return {"perplexity": math.exp(loss), "loss": loss,
            "params": int(model.count_params()),
            "curve": [math.exp(v) for v in history.history["val_loss"]],
            "model": model, "x_test": x_test, "y_test": y_test,
            "vocabulary": windows["vocabulary"]}


def perplexity_ladder(fig, axes, p: Palette) -> None:
    ngrams = _ngram_models()
    neural = _neural_model()
    left, right = fig.subplots(1, 2)
    labels = ["uniform", "unigram", "bigram (add-0.1)", "neural"]
    values = [ngrams["uniform"]["perplexity"], ngrams["unigram"]["perplexity"],
              ngrams["bigram (add-0.1)"]["perplexity"], neural["perplexity"]]
    colors = (p.muted, p.red, p.amber, p.green)
    positions = np.arange(len(labels))
    left.bar(positions, values, 0.55, color=colors)
    for x, value in zip(positions, values):
        left.annotate(f"{value:,.1f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=8.5, color=p.fg)
    left.set_yscale("log")
    left.set_xticks(positions)
    left.set_xticklabels([label.replace(" (", "\n(") for label in labels],
                         fontsize=8.5)
    left.set_ylabel("held-out perplexity (lower is better)")
    left.set_title(f"vocabulary {ngrams['vocabulary']:,} — uniform perplexity "
                   f"is the vocabulary size", fontsize=10)

    right.plot(range(1, len(neural["curve"]) + 1), neural["curve"], "o-",
               ms=5, lw=2.0, color=p.green, label="neural")
    right.axhline(ngrams["bigram (add-0.1)"]["perplexity"], color=p.amber,
                  lw=1.3, ls="--",
                  label=f"bigram {ngrams['bigram (add-0.1)']['perplexity']:,.1f}")
    right.axhline(ngrams["unigram"]["perplexity"], color=p.red, lw=1.3,
                  ls="--", label=f"unigram {ngrams['unigram']['perplexity']:,.1f}")
    right.set_xlabel("epoch")
    right.set_ylabel("held-out perplexity")
    right.set_title(f"{neural['params']:,} parameters, "
                    f"{CONTEXT}-token context", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def _bleu(candidate, references, order=4, smooth=False):
    """BLEU for one candidate against one or more references."""
    precisions = []
    for n in range(1, order + 1):
        candidate_grams = Counter(tuple(candidate[i:i + n])
                                  for i in range(len(candidate) - n + 1))
        if not candidate_grams:
            precisions.append(0.0)
            continue
        best = Counter()
        for reference in references:
            reference_grams = Counter(tuple(reference[i:i + n])
                                      for i in range(len(reference) - n + 1))
            for gram, count in reference_grams.items():
                best[gram] = max(best[gram], count)
        clipped = sum(min(count, best[gram])
                      for gram, count in candidate_grams.items())
        total = sum(candidate_grams.values())
        if smooth:
            precisions.append((clipped + 1) / (total + 1))
        else:
            precisions.append(clipped / total)
    if min(precisions) == 0:
        geometric = 0.0
    else:
        geometric = math.exp(sum(math.log(value) for value in precisions)
                             / len(precisions))
    reference_length = min((len(r) for r in references),
                           key=lambda length: (abs(length - len(candidate)),
                                               length))
    penalty = (1.0 if len(candidate) > reference_length
               else math.exp(1 - reference_length / max(len(candidate), 1)))
    return {"bleu": penalty * geometric, "precisions": precisions,
            "penalty": penalty, "geometric": geometric}


CASES = (
    ("exact match", "the cat sat on the mat"),
    ("one word changed", "the cat sat on a mat"),
    ("reordered", "on the mat the cat sat"),
    ("shorter but correct", "the cat sat"),
    ("synonym", "the feline sat on the mat"),
    ("padded with repeats", "the cat sat on the mat mat mat"),
)
REFERENCE = "the cat sat on the mat"


def bleu_anatomy(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    reference = REFERENCE.split()
    labels = [label for label, _ in CASES]
    scores = [_bleu(text.split(), [reference])["bleu"] for _, text in CASES]
    positions = np.arange(len(labels))
    left.barh(positions, scores, 0.55,
              color=[p.green if value > 0.5 else
                     (p.amber if value > 0 else p.red) for value in scores])
    for y, (value, (label, text)) in enumerate(zip(scores, CASES)):
        left.annotate(f"{value:.4f}   {text!r}", (0.01, y), va="center",
                      fontsize=7.5, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xlim(0, 1.05)
    left.set_xlabel("BLEU-4")
    left.set_title(f"reference: {REFERENCE!r}", fontsize=9.5)

    orders = (1, 2, 3, 4)
    for label, text, color in (("one word changed", CASES[1][1], p.blue),
                               ("reordered", CASES[2][1], p.amber),
                               ("synonym", CASES[4][1], p.red)):
        values = [_bleu(text.split(), [reference], order=n)["bleu"]
                  for n in orders]
        right.plot(orders, values, "o-", ms=6, lw=2.0, color=color,
                   label=label)
    right.set_xticks(list(orders))
    right.set_xlabel("maximum n-gram order")
    right.set_ylabel("BLEU")
    right.set_title("the order changes the verdict", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


@functools.lru_cache(maxsize=1)
def _temperature() -> dict:
    """Sample from the trained model at several temperatures."""
    info = _neural_model()
    model = info["model"]
    x_test = info["x_test"]
    rng = np.random.default_rng(0)
    probabilities = model.predict(x_test[:2000], verbose=0)
    out = {}
    for temperature in TEMPERATURES:
        logits = np.log(np.clip(probabilities, 1e-9, None)) / temperature
        shifted = logits - logits.max(axis=1, keepdims=True)
        scaled = np.exp(shifted)
        scaled /= scaled.sum(axis=1, keepdims=True)
        picks = np.array([rng.choice(len(row), p=row) for row in scaled])
        distinct = len(set(picks.tolist()))
        entropy = float(-(scaled * np.log(scaled + 1e-12)).sum(axis=1).mean())
        # Perplexity of the *sampled* distribution against the true next token.
        rows = np.arange(len(picks))
        likelihood = scaled[rows, info["y_test"][:2000]]
        out[temperature] = {
            "distinct": distinct,
            "entropy": entropy,
            "perplexity": float(np.exp(-np.log(np.clip(likelihood, 1e-9,
                                                       None)).mean())),
            "top_share": float(scaled.max(axis=1).mean()),
        }
    return out


def length_and_temperature(fig, axes, p: Palette) -> None:
    runs = _temperature()
    left, right = fig.subplots(1, 2)
    temperatures = list(runs)
    distinct = [runs[t]["distinct"] for t in temperatures]
    perplexity = [runs[t]["perplexity"] for t in temperatures]
    left.plot(temperatures, distinct, "o-", ms=6, lw=2.0, color=p.blue)
    for temperature, value in zip(temperatures, distinct):
        left.annotate(f"{value:,}", (temperature, value),
                      textcoords="offset points", xytext=(0, 8), ha="center",
                      fontsize=7.5, color=p.blue)
    left.set_xlabel("sampling temperature")
    left.set_ylabel("distinct tokens produced in 2,000 samples")
    left.set_title("temperature buys variety", fontsize=10)

    right.plot(temperatures, perplexity, "o-", ms=6, lw=2.0, color=p.red)
    for temperature, value in zip(temperatures, perplexity):
        right.annotate(f"{value:,.0f}", (temperature, value),
                       textcoords="offset points", xytext=(0, 8), ha="center",
                       fontsize=7.5, color=p.red)
    right.set_yscale("log")
    right.set_xlabel("sampling temperature")
    right.set_ylabel("perplexity of the reweighted distribution")
    right.set_title("and pays for it in likelihood", fontsize=10)


FIGURES = [
    figure("perplexity-ladder", perplexity_ladder, size=(9.4, 3.5),
           axes=False),
    figure("bleu-anatomy", bleu_anatomy, size=(9.6, 3.6), axes=False),
    figure("length-and-temperature", length_and_temperature, size=(9.4, 3.5),
           axes=False),
]


if __name__ == "__main__":
    data = _corpus()
    ngrams = _ngram_models()
    print(f"=== {len(data['train']):,} train / {len(data['test']):,} test "
          f"reviews, vocabulary {ngrams['vocabulary']:,} ===")
    print("every model is scored on the same held-out windows")
    print(f"{'model':20s} {'held-out perplexity':>20} {'tokens scored':>14}")
    for label in ("uniform", "unigram", "bigram (add-0.1)"):
        entry = ngrams[label]
        print(f"{label:20s} {entry['perplexity']:20,.2f} "
              f"{entry['tokens']:14,}")
    neural = _neural_model()
    print(f"{'neural':20s} {neural['perplexity']:20,.2f} "
          f"{len(neural['y_test']):14,}")
    curve = neural["curve"]
    print(f"the neural model's best epoch is {curve.index(min(curve)) + 1} of "
          f"{len(curve)}: perplexity {min(curve):,.2f} there against "
          f"{curve[-1]:,.2f} at the end")
    print(f"the neural model has {neural['params']:,} parameters and a "
          f"{CONTEXT}-token context")
    print("uniform perplexity equals the vocabulary size: a model that has")
    print("learned nothing is 'as confused as' a fair die with that many sides")

    print("\n=== BLEU on one reference ===")
    reference = REFERENCE.split()
    print(f"reference: {REFERENCE!r}")
    print(f"{'case':22s} {'BLEU-4':>8} {'BP':>7} {'p1':>6} {'p2':>6} "
          f"{'p3':>6} {'p4':>6}")
    for label, text in CASES:
        result = _bleu(text.split(), [reference])
        precisions = " ".join(f"{value:6.3f}" for value in result["precisions"])
        print(f"{label:22s} {result['bleu']:8.4f} {result['penalty']:7.3f} "
              f"{precisions}")
    print("BLEU-4 is zero whenever any n-gram precision is zero: 'reordered'")
    print("shares every unigram and still scores 0 because no 4-gram survives,")
    print("and 'shorter but correct' has perfect precisions but only 3 tokens")

    print("\n=== the brevity penalty on its own ===")
    print(f"{'candidate length':>17} {'reference length':>17} {'BP':>8}")
    for length in (3, 4, 5, 6, 7, 12):
        penalty = 1.0 if length > 6 else math.exp(1 - 6 / length)
        print(f"{length:17d} {6:17d} {penalty:8.4f}")

    print(f"\n=== sampling temperature, 2,000 predictions ===")
    print(f"{'temperature':>12} {'distinct tokens':>16} {'mean top prob':>14} "
          f"{'entropy':>9} {'perplexity':>11}")
    for temperature, entry in _temperature().items():
        print(f"{temperature:12.1f} {entry['distinct']:16,} "
              f"{entry['top_share']:14.4f} {entry['entropy']:9.4f} "
              f"{entry['perplexity']:11,.1f}")
    print("low temperature repeats the safest token; high temperature invents.")
    print("Perplexity measures the first and cannot see the second.")

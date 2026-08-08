"""Figures for *Word Embeddings (Word2Vec, GloVe)*.

No pretrained vectors are downloaded. Embeddings are trained here two ways —
as a by-product of a supervised task, and by skip-gram style co-occurrence —
so the page can measure what each actually learns rather than showing the
famous king-queen arithmetic and moving on.

``dimension-sweep``
    Accuracy and parameter count against embedding width, including the point
    where more dimensions stop paying.

``neighbours``
    Nearest neighbours for a handful of words under both training signals,
    which is where "similar" turns out to mean different things.

``frequency-and-quality``
    Why rare words get bad vectors: neighbour quality against how often the
    word was seen.
"""

from __future__ import annotations

import functools
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import imdb, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

VOCAB = 8000
MAXLEN = 200
LIMIT = 8000
EPOCHS = 8
DIMENSIONS = (8, 16, 32, 64, 128)
SWEEP_DIMENSION = 32
WINDOW = 3
# 400,000 pairs over 8 epochs produced neighbours that were still mostly
# noise ('terrible' -> 'content', 'yes', 'write'). Word2vec is a
# large-corpus method; this is the smallest budget that produces anything
# worth reading, and the page says so rather than pretending otherwise.
SKIPGRAM_PAIRS = 1600000
SKIPGRAM_EPOCHS = 6
PROBE_WORDS = ("terrible", "great", "movie", "she", "france")
INDEX_OFFSET = 3


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    keras = tf().keras
    reviews = imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)
    word_index = keras.datasets.imdb.get_word_index()
    forward = {word: index + INDEX_OFFSET for word, index in word_index.items()
               if index + INDEX_OFFSET < VOCAB}
    reverse = {index: word for word, index in forward.items()}
    return {**reviews, "forward": forward, "reverse": reverse}


def _supervised(dimension: int, seed: int = 0) -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, dimension, mask_zero=True),
        keras.layers.GlobalAveragePooling1D(),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=64, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"accuracy": max(float(v) for v in history.history["val_accuracy"]),
            "params": int(model.count_params()),
            "vectors": model.layers[0].get_weights()[0]}


@functools.lru_cache(maxsize=1)
def _dimension_runs() -> dict:
    return {dimension: _supervised(dimension) for dimension in DIMENSIONS}


@functools.lru_cache(maxsize=1)
def _skipgram() -> dict:
    """Skip-gram with negative sampling, trained on co-occurrence alone."""
    keras = tf().keras
    data = _data()
    rng = np.random.default_rng(0)
    rows = data["x_train"]
    targets, contexts, labels = [], [], []
    counts = Counter(int(token) for row in rows for token in row if token > 2)
    tokens = np.array(list(counts))
    weights = np.array([counts[int(t)] for t in tokens], dtype="float64")
    weights = weights ** 0.75
    weights /= weights.sum()
    for row in rows:
        real = [int(t) for t in row if t > 2]
        for position, token in enumerate(real):
            low = max(0, position - WINDOW)
            high = min(len(real), position + WINDOW + 1)
            for other in range(low, high):
                if other == position:
                    continue
                targets.append(token)
                contexts.append(real[other])
                labels.append(1)
            if len(targets) >= SKIPGRAM_PAIRS // 2:
                break
        if len(targets) >= SKIPGRAM_PAIRS // 2:
            break
    negatives = len(targets)
    noise = rng.choice(tokens, size=negatives, p=weights)
    targets = np.array(targets + targets[:negatives])
    contexts = np.array(contexts + list(noise))
    labels = np.array(labels + [0] * negatives, dtype="float32")
    # The positives are all built first and the negatives appended, so
    # validation_split — which takes the *last* rows — would otherwise be 100%
    # negatives and report an accuracy that means nothing.
    order = rng.permutation(len(labels))
    targets, contexts, labels = targets[order], contexts[order], labels[order]

    seed_everything(0)
    target_input = keras.layers.Input((), dtype="int32")
    context_input = keras.layers.Input((), dtype="int32")
    embedding = keras.layers.Embedding(VOCAB, SWEEP_DIMENSION,
                                       name="target_embedding")
    context_embedding = keras.layers.Embedding(VOCAB, SWEEP_DIMENSION)
    dot = keras.layers.Dot(axes=-1)([embedding(target_input),
                                     context_embedding(context_input)])
    model = keras.Model([target_input, context_input],
                        keras.layers.Activation("sigmoid")(dot))
    model.compile(keras.optimizers.Adam(2e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    history = model.fit([targets, contexts], labels, epochs=SKIPGRAM_EPOCHS,
                        batch_size=1024, verbose=0, validation_split=0.1)
    return {"vectors": embedding.get_weights()[0],
            "pairs": int(len(targets)),
            "accuracy": max(float(v)
                            for v in history.history["val_accuracy"])}


def _neighbours(vectors, word: str, count: int = 5):
    data = _data()
    index = data["forward"].get(word)
    if index is None or index >= len(vectors):
        return []
    normed = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9)
    similarity = normed @ normed[index]
    order = np.argsort(-similarity)
    out = []
    for other in order:
        if other == index or other < INDEX_OFFSET:
            continue
        word_other = data["reverse"].get(int(other))
        if word_other is None:
            continue
        out.append((word_other, float(similarity[other])))
        if len(out) == count:
            break
    return out


def dimension_sweep(fig, axes, p: Palette) -> None:
    runs = _dimension_runs()
    left, right = fig.subplots(1, 2)
    accuracy = [runs[d]["accuracy"] for d in DIMENSIONS]
    params = [runs[d]["params"] for d in DIMENSIONS]
    left.plot(DIMENSIONS, accuracy, "o-", ms=6, lw=2.0, color=p.green)
    for dimension, value in zip(DIMENSIONS, accuracy):
        left.annotate(f"{value:.4f}", (dimension, value),
                      textcoords="offset points", xytext=(0, 8), ha="center",
                      fontsize=7.5, color=p.green)
    left.set_xscale("log")
    left.minorticks_off()
    left.set_xticks(list(DIMENSIONS))
    left.set_xticklabels([str(d) for d in DIMENSIONS])
    left.set_xlabel("embedding dimension")
    left.set_ylabel("best validation accuracy")
    left.set_title(f"IMDB, {LIMIT:,} reviews, {EPOCHS} epochs", fontsize=10)

    right.plot(DIMENSIONS, params, "o-", ms=6, lw=2.0, color=p.blue)
    for dimension, value in zip(DIMENSIONS, params):
        right.annotate(f"{value:,}", (dimension, value),
                       textcoords="offset points", xytext=(0, 8), ha="center",
                       fontsize=7.5, color=p.blue)
    right.set_xscale("log")
    right.set_yscale("log")
    right.minorticks_off()
    right.set_xticks(list(DIMENSIONS))
    right.set_xticklabels([str(d) for d in DIMENSIONS])
    right.set_xlabel("embedding dimension")
    right.set_ylabel("total parameters")
    right.set_title(f"the embedding matrix is {VOCAB:,} x d", fontsize=10)


def neighbours(fig, axes, p: Palette) -> None:
    supervised = _dimension_runs()[SWEEP_DIMENSION]["vectors"]
    skipgram = _skipgram()["vectors"]
    left, right = fig.subplots(1, 2)
    for ax, vectors, title in ((left, supervised, "trained on sentiment"),
                               (right, skipgram, "trained on co-occurrence")):
        ax.axis("off")
        ax.set_title(title, fontsize=10)
        lines = []
        for word in PROBE_WORDS:
            found = _neighbours(vectors, word)
            if not found:
                continue
            lines.append(f"{word}")
            for other, score in found:
                lines.append(f"    {score:.3f}  {other}")
            lines.append("")
        ax.text(0.0, 0.98, "\n".join(lines), va="top", ha="left", fontsize=8,
                family="monospace", color=p.fg, transform=ax.transAxes)


def frequency_and_quality(fig, axes, p: Palette) -> None:
    data = _data()
    vectors = _skipgram()["vectors"]
    counts = Counter(int(token) for row in data["x_train"] for token in row
                     if token > 2)
    ax = fig.subplots(1, 1)
    indices = np.array([index for index in counts if index < len(vectors)])
    frequencies = np.array([counts[int(index)] for index in indices])
    normed = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9)
    # Two earlier versions of this figure asserted a trend the data does not
    # have. Peak-minus-average similarity rewards randomness, and plain
    # nearest-neighbour similarity turned out to be *flat* across frequency
    # bands (0.62-0.66). What does move with frequency is how close a word sits
    # to the bulk of the vocabulary, so the figure plots both and says so.
    sample = indices[np.argsort(-frequencies)]
    sample = np.concatenate([sample[:400], sample[len(sample) // 2:
                                                  len(sample) // 2 + 400],
                             sample[-400:]])
    similarity = normed[sample] @ normed[sample].T
    np.fill_diagonal(similarity, np.nan)
    peak = np.nanmax(similarity, axis=1)
    average = np.nanmean(similarity, axis=1)
    sample_frequencies = np.array([counts[int(index)] for index in sample])
    bins = np.array([1, 3, 10, 30, 100, 300, 1000, 30000])
    centres, peaks, averages = [], [], []
    for low, high in zip(bins, bins[1:]):
        mask = (sample_frequencies >= low) & (sample_frequencies < high)
        if mask.sum() > 5:
            centres.append(float(np.sqrt(low * high)))
            peaks.append(float(peak[mask].mean()))
            averages.append(float(average[mask].mean()))
    ax.plot(centres, peaks, "o-", ms=7, lw=2.2, color=p.green,
            label="nearest neighbour")
    ax.plot(centres, averages, "o-", ms=7, lw=2.2, color=p.amber,
            label="average over the vocabulary")
    for x, value in zip(centres, peaks):
        ax.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=7, color=p.green)
    for x, value in zip(centres, averages):
        ax.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                    xytext=(0, -13), ha="center", fontsize=7, color=p.amber)
    ax.set_xscale("log")
    ax.set_xlabel("times the word appears in training")
    ax.set_ylabel("cosine similarity")
    ax.set_ylim(0, 1.0)
    ax.set_title("frequent words sit closer to everything, not closer to one "
                 "thing", fontsize=10.5)
    ax.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("dimension-sweep", dimension_sweep, size=(9.4, 3.5), axes=False),
    figure("neighbours", neighbours, size=(9.6, 4.2), axes=False),
    figure("frequency-and-quality", frequency_and_quality, size=(7.8, 3.8),
           axes=False),
]


if __name__ == "__main__":
    data = _data()
    print(f"=== IMDB, {LIMIT:,} reviews, vocabulary {VOCAB:,} ===")
    runs = _dimension_runs()
    print(f"{'dimension':>10} {'parameters':>12} {'embedding rows':>15} "
          f"{'best val acc':>13}")
    for dimension in DIMENSIONS:
        run = runs[dimension]
        print(f"{dimension:10d} {run['params']:12,} {VOCAB * dimension:15,} "
              f"{run['accuracy']:13.4f}")
    best = max(DIMENSIONS, key=lambda d: runs[d]["accuracy"])
    print(f"best dimension {best} at {runs[best]['accuracy']:.4f}; going from "
          f"8 to 128 multiplies the embedding matrix by 16 for "
          f"{runs[128]['accuracy'] - runs[8]['accuracy']:+.4f} accuracy")

    skipgram = _skipgram()
    print(f"\n=== skip-gram with negative sampling ===")
    print(f"{skipgram['pairs']:,} training pairs (half of them negatives), "
          f"{SKIPGRAM_EPOCHS} epochs, validation accuracy "
          f"{skipgram['accuracy']:.4f}")

    print("\n=== nearest neighbours by cosine similarity ===")
    for label, vectors in (("sentiment", runs[SWEEP_DIMENSION]["vectors"]),
                           ("co-occurrence", skipgram["vectors"])):
        print(f"-- trained on {label}")
        for word in PROBE_WORDS:
            found = _neighbours(vectors, word)
            if found:
                print(f"  {word:10s} " + ", ".join(f"{other} {score:.3f}"
                                                   for other, score in found))
    print("the sentiment vectors group words that predict the same label;")
    print("the co-occurrence vectors group words that appear in the same")
    print("contexts. Both are 'similar' - they are not the same relation")

    counts = Counter(int(token) for row in data["x_train"] for token in row
                     if token > 2)
    vectors = skipgram["vectors"]
    normed = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9)
    print("\n=== vector quality against word frequency ===")
    print(f"{'appears':>12} {'words':>7} {'mean top similarity':>20} "
          f"{'mean similarity':>16}")
    bins = ((1, 3), (3, 10), (10, 30), (30, 100), (100, 1000), (1000, 100000))
    for low, high in bins:
        chosen = [index for index, count in counts.items()
                  if low <= count < high and index < len(vectors)][:300]
        if len(chosen) < 10:
            continue
        block = normed[chosen] @ normed[chosen].T
        np.fill_diagonal(block, -np.inf)
        peak = block.max(axis=1)
        finite = np.where(np.isinf(block), np.nan, block)
        print(f"{f'{low}-{high}':>12} {len(chosen):7d} {peak.mean():20.4f} "
              f"{float(np.nanmean(finite)):16.4f}")
    print("the nearest-neighbour column is nearly flat: at 1.6 million pairs")
    print("even rare words find *a* close neighbour. What frequency changes is")
    print("the average column - frequent words drift towards the middle of the")
    print("space, close to everything and specific to nothing")

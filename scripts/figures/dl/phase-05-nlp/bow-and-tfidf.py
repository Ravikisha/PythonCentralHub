"""Figures for *Bag of Words (BoW) & TF-IDF*.

Everything here uses scikit-learn on the decoded IMDB reviews, so the whole
module is linear models over sparse matrices: fast, and a fair fight against
the neural models the rest of the phase trains.

``weighting-schemes``
    Raw counts, binary, TF-IDF and sublinear TF at a fixed vocabulary — the
    weighting matters more than most tutorials suggest, and not always in the
    advertised direction.

``vocabulary-sweep``
    Accuracy against vocabulary size for counts and TF-IDF, with the point
    where more words stop helping.

``sparsity-and-cost``
    What the document-term matrix actually costs: non-zeros per document,
    sparse against dense memory, and the fit time that buys.
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

from _dl import tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

DOCUMENTS = 8000
CAPS = (500, 2000, 10000, 30000)
SWEEP_CAP = 10000
INDEX_OFFSET = 3
SCHEMES = ("counts", "binary", "TF-IDF", "sublinear TF-IDF")


@functools.lru_cache(maxsize=1)
def _texts() -> dict:
    keras = tf().keras
    (x_train, y_train), (x_test, y_test) = keras.datasets.imdb.load_data()
    word_index = keras.datasets.imdb.get_word_index()
    reverse = {index + INDEX_OFFSET: word for word, index in word_index.items()}

    def decode(rows):
        return [" ".join(reverse.get(token, "oov") for token in row)
                for row in rows]

    return {"x_train": decode(x_train[:DOCUMENTS]),
            "y_train": np.asarray(y_train[:DOCUMENTS]),
            "x_test": decode(x_test[:DOCUMENTS // 2]),
            "y_test": np.asarray(y_test[:DOCUMENTS // 2])}


def _vectorizer(scheme: str, cap: int):
    from sklearn.feature_extraction.text import (CountVectorizer,
                                                 TfidfVectorizer)
    if scheme == "counts":
        return CountVectorizer(max_features=cap)
    if scheme == "binary":
        return CountVectorizer(max_features=cap, binary=True)
    if scheme == "TF-IDF":
        return TfidfVectorizer(max_features=cap, sublinear_tf=False)
    return TfidfVectorizer(max_features=cap, sublinear_tf=True)


def _fit(scheme: str, cap: int) -> dict:
    from sklearn.linear_model import LogisticRegression

    data = _texts()
    vectorizer = _vectorizer(scheme, cap)
    started = time.perf_counter()
    train = vectorizer.fit_transform(data["x_train"])
    test = vectorizer.transform(data["x_test"])
    vectorise_seconds = time.perf_counter() - started
    started = time.perf_counter()
    model = LogisticRegression(max_iter=2000).fit(train, data["y_train"])
    fit_seconds = time.perf_counter() - started
    return {"accuracy": float(model.score(test, data["y_test"])),
            "nnz": int(train.nnz), "rows": train.shape[0],
            "columns": train.shape[1],
            "vectorise_seconds": vectorise_seconds,
            "fit_seconds": fit_seconds,
            "vectorizer": vectorizer, "model": model}


@functools.lru_cache(maxsize=1)
def _scheme_runs() -> dict:
    return {scheme: _fit(scheme, SWEEP_CAP) for scheme in SCHEMES}


@functools.lru_cache(maxsize=1)
def _cap_runs() -> dict:
    return {(scheme, cap): _fit(scheme, cap)
            for scheme in ("counts", "TF-IDF") for cap in CAPS}


def weighting_schemes(fig, axes, p: Palette) -> None:
    runs = _scheme_runs()
    left, right = fig.subplots(1, 2)
    values = [runs[scheme]["accuracy"] for scheme in SCHEMES]
    best = max(values)
    positions = np.arange(len(SCHEMES))
    left.bar(positions, values, 0.55,
             color=[p.green if abs(v - best) < 1e-12 else p.blue
                    for v in values])
    for x, value in zip(positions, values):
        left.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=8.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([s.replace(" ", "\n") for s in SCHEMES], fontsize=8)
    left.set_ylim(0, 1.05)
    left.set_ylabel("test accuracy")
    left.set_title(f"IMDB, {DOCUMENTS:,} reviews, {SWEEP_CAP:,} features",
                   fontsize=10)

    # What TF-IDF does to the weight of a common word against a rare one.
    tfidf = runs["TF-IDF"]["vectorizer"]
    counts = runs["counts"]["vectorizer"]
    idf = dict(zip(tfidf.get_feature_names_out(), tfidf.idf_))
    frequencies = np.asarray(
        counts.transform(_texts()["x_train"]).sum(axis=0)).ravel()
    names = counts.get_feature_names_out()
    order = np.argsort(-frequencies)
    picks = [order[0], order[5], order[50], order[500], order[3000],
             order[len(order) - 1]]
    words = [names[index] for index in picks]
    weights = [idf.get(word, np.nan) for word in words]
    document_frequency = [frequencies[index] for index in picks]
    right.barh(np.arange(len(words)), weights, 0.55, color=p.amber)
    # Labels sit to the right of each bar: drawn inside, they were unreadable
    # against the fill.
    for y, (word, weight, frequency) in enumerate(zip(words, weights,
                                                      document_frequency)):
        right.annotate(f"{word!r}  idf {weight:.2f}  ({frequency:,} uses)",
                       (weight, y), xytext=(6, 0),
                       textcoords="offset points", va="center", fontsize=8,
                       color=p.fg)
    right.set_xlim(0, max(weights) * 1.85)
    right.set_yticks([])
    right.set_xlabel("inverse document frequency")
    right.set_title("IDF is the whole difference from raw counts", fontsize=10)


def vocabulary_sweep(fig, axes, p: Palette) -> None:
    runs = _cap_runs()
    left, right = fig.subplots(1, 2)
    for scheme, color in (("counts", p.blue), ("TF-IDF", p.green)):
        values = [runs[(scheme, cap)]["accuracy"] for cap in CAPS]
        left.plot(CAPS, values, "o-", ms=6, lw=2.0, color=color, label=scheme)
        for cap, value in zip(CAPS, values):
            left.annotate(f"{value:.4f}", (cap, value),
                          textcoords="offset points", xytext=(0, 8),
                          ha="center", fontsize=7.5, color=color)
    left.set_xscale("log")
    left.set_xticks(list(CAPS))
    left.set_xticklabels([f"{c:,}" for c in CAPS])
    left.set_xlabel("vocabulary size")
    left.set_ylabel("test accuracy")
    left.set_title("more words stop helping", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    for scheme, color in (("counts", p.blue), ("TF-IDF", p.green)):
        seconds = [runs[(scheme, cap)]["fit_seconds"] for cap in CAPS]
        right.plot(CAPS, seconds, "o-", ms=6, lw=2.0, color=color,
                   label=f"{scheme} fit")
    right.set_xscale("log")
    right.set_xticks(list(CAPS))
    right.set_xticklabels([f"{c:,}" for c in CAPS])
    right.set_xlabel("vocabulary size")
    right.set_ylabel("seconds to fit the classifier")
    right.set_title("and cost more to fit", fontsize=10)
    right.legend(fontsize=8, loc="upper left")


def sparsity_and_cost(fig, axes, p: Palette) -> None:
    runs = _cap_runs()
    left, right = fig.subplots(1, 2)
    density = []
    for cap in CAPS:
        run = runs[("counts", cap)]
        density.append(run["nnz"] / (run["rows"] * run["columns"]))
    left.plot(CAPS, density, "o-", ms=6, lw=2.0, color=p.red)
    for cap, value in zip(CAPS, density):
        left.annotate(f"{value:.4f}", (cap, value),
                      textcoords="offset points", xytext=(0, 8), ha="center",
                      fontsize=7.5, color=p.red)
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xticks(list(CAPS))
    left.set_xticklabels([f"{c:,}" for c in CAPS])
    left.set_xlabel("vocabulary size")
    left.set_ylabel("fraction of the matrix that is non-zero")
    left.set_title("the matrix gets emptier as it gets wider", fontsize=10)

    sparse_mb, dense_mb = [], []
    for cap in CAPS:
        run = runs[("counts", cap)]
        # CSR: one float64 value and one int32 index per non-zero.
        sparse_mb.append(run["nnz"] * 12 / 1e6)
        dense_mb.append(run["rows"] * run["columns"] * 8 / 1e6)
    positions = np.arange(len(CAPS))
    right.bar(positions - 0.19, dense_mb, 0.36, color=p.red, label="dense")
    right.bar(positions + 0.19, sparse_mb, 0.36, color=p.green,
              label="sparse (CSR)")
    for x, value in zip(positions - 0.19, dense_mb):
        right.annotate(f"{value:,.0f}", (x, value),
                       textcoords="offset points", xytext=(0, 3), ha="center",
                       fontsize=7.5, color=p.fg)
    for x, value in zip(positions + 0.19, sparse_mb):
        right.annotate(f"{value:,.1f}", (x, value),
                       textcoords="offset points", xytext=(0, 3), ha="center",
                       fontsize=7.5, color=p.fg)
    right.set_yscale("log")
    right.set_xticks(positions)
    right.set_xticklabels([f"{c:,}" for c in CAPS])
    right.set_xlabel("vocabulary size")
    right.set_ylabel("megabytes")
    right.set_title(f"{DOCUMENTS:,} x vocabulary, dense against sparse",
                    fontsize=10)
    right.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("weighting-schemes", weighting_schemes, size=(9.6, 3.6),
           axes=False),
    figure("vocabulary-sweep", vocabulary_sweep, size=(9.4, 3.5), axes=False),
    figure("sparsity-and-cost", sparsity_and_cost, size=(9.4, 3.5),
           axes=False),
]


if __name__ == "__main__":
    data = _texts()
    print(f"=== IMDB, {len(data['x_train']):,} train / "
          f"{len(data['x_test']):,} test reviews ===")
    print(f"label balance: {data['y_train'].mean():.4f} positive")

    runs = _scheme_runs()
    print(f"\n=== four weightings at {SWEEP_CAP:,} features ===")
    print(f"{'scheme':18s} {'accuracy':>9} {'vectorise s':>12} {'fit s':>8}")
    for scheme in SCHEMES:
        run = runs[scheme]
        print(f"{scheme:18s} {run['accuracy']:9.4f} "
              f"{run['vectorise_seconds']:12.1f} {run['fit_seconds']:8.1f}")

    tfidf = runs["TF-IDF"]["vectorizer"]
    idf = dict(zip(tfidf.get_feature_names_out(), tfidf.idf_))
    counts = runs["counts"]["vectorizer"]
    frequencies = np.asarray(
        counts.transform(data["x_train"]).sum(axis=0)).ravel()
    names = counts.get_feature_names_out()
    order = np.argsort(-frequencies)
    print("\n=== what IDF does to a word's weight ===")
    print(f"{'rank':>6} {'word':16s} {'uses':>9} {'idf':>7}")
    for rank in (0, 5, 50, 500, 3000, len(order) - 1):
        index = order[rank]
        word = names[index]
        print(f"{rank + 1:6d} {word:16s} {frequencies[index]:9,} "
              f"{idf.get(word, float('nan')):7.3f}")

    caps = _cap_runs()
    print(f"\n=== vocabulary size ===")
    print(f"{'vocabulary':>11} {'counts':>9} {'TF-IDF':>9} {'nnz/doc':>9} "
          f"{'density':>9} {'sparse MB':>10} {'dense MB':>10}")
    for cap in CAPS:
        counts_run = caps[("counts", cap)]
        tfidf_run = caps[("TF-IDF", cap)]
        density = counts_run["nnz"] / (counts_run["rows"]
                                       * counts_run["columns"])
        print(f"{cap:11,} {counts_run['accuracy']:9.4f} "
              f"{tfidf_run['accuracy']:9.4f} "
              f"{counts_run['nnz'] / counts_run['rows']:9.1f} "
              f"{density:9.4f} {counts_run['nnz'] * 12 / 1e6:10.1f} "
              f"{counts_run['rows'] * counts_run['columns'] * 8 / 1e6:10.1f}")

    model = runs["TF-IDF"]["model"]
    names = runs["TF-IDF"]["vectorizer"].get_feature_names_out()
    weights = model.coef_[0]
    order = np.argsort(weights)
    print("\n=== the ten most negative and positive features ===")
    print("  negative: " + ", ".join(f"{names[i]}" for i in order[:10]))
    print("  positive: " + ", ".join(f"{names[i]}" for i in order[-10:]))
    print("a linear model over word counts is interpretable in a way no")
    print("recurrent or attention model on this phase is")

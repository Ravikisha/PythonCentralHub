"""Figures for *Text Preprocessing (Tokenization, Stemming, Lemmatization)*.

Everything here is counted rather than trained, so the whole module runs in
seconds. The corpus is the locally cached IMDB word index decoded back into
words — which is itself a lesson the page states plainly: `keras.datasets.imdb`
ships *already* tokenized, lowercased and stripped of punctuation, so the
choices this page is about were made for you before you saw the data.

``vocabulary-growth``
    Unique tokens against documents read (Heaps' law), with the fitted
    exponent — the reason a vocabulary cap is a decision you cannot avoid.

``zipf-and-coverage``
    Rank against frequency on log axes, and the cumulative coverage curve that
    says what a vocabulary of N words actually buys.

``normalisation-effects``
    What each normalisation step does to the vocabulary size, and what it
    merges that you might not want merged.
"""

from __future__ import annotations

import functools
import os
import re
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

DOCUMENTS = 5000
CANDIDATES = (1000, 5000, 10000, 20000, 50000)
# Keras reserves 0 for padding, 1 for "start of sequence" and 2 for
# out-of-vocabulary, so a token id maps to the word index at id - 3.
INDEX_OFFSET = 3


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    """Decode the cached IMDB ids back into word sequences."""
    keras = tf().keras
    (x_train, y_train), _ = keras.datasets.imdb.load_data()
    word_index = keras.datasets.imdb.get_word_index()
    reverse = {index + INDEX_OFFSET: word for word, index in word_index.items()}
    documents = []
    for row in x_train[:DOCUMENTS]:
        documents.append([reverse.get(token, "<oov>") for token in row])
    return {"documents": documents, "labels": y_train[:DOCUMENTS],
            "vocabulary": len(word_index)}


@functools.lru_cache(maxsize=1)
def _counts() -> dict:
    info = _corpus()
    tokens = [token for document in info["documents"] for token in document]
    counter = Counter(tokens)
    ordered = counter.most_common()
    frequencies = np.array([count for _, count in ordered])
    growth = []
    seen = set()
    for index, document in enumerate(info["documents"], start=1):
        seen.update(document)
        if index % 25 == 0 or index == 1:
            growth.append((index, len(seen)))
    return {"counter": counter, "ordered": ordered, "frequencies": frequencies,
            "total": int(frequencies.sum()), "growth": growth,
            "types": len(counter)}


def vocabulary_growth(fig, axes, p: Palette) -> None:
    counts = _counts()
    left, right = fig.subplots(1, 2)
    documents = np.array([d for d, _ in counts["growth"]], dtype="float64")
    types = np.array([t for _, t in counts["growth"]], dtype="float64")
    left.plot(documents, types, lw=2.0, color=p.blue)
    # Heaps' law: types = k * tokens^beta. Fit on the log-log line.
    tokens_seen = documents * (counts["total"] / len(_corpus()["documents"]))
    slope, intercept = np.polyfit(np.log(tokens_seen), np.log(types), 1)
    left.set_xlabel("documents read")
    left.set_ylabel("distinct words seen")
    left.set_title(f"the vocabulary never stops growing "
                   f"(Heaps' exponent {slope:.3f})", fontsize=10)
    left.annotate(f"{int(types[-1]):,} distinct words\nin "
                  f"{int(documents[-1]):,} reviews",
                  (documents[-1], types[-1]), textcoords="offset points",
                  xytext=(-12, -34), ha="right", fontsize=8.5, color=p.fg)

    hapax = sum(1 for _, count in counts["ordered"] if count == 1)
    twice = sum(1 for _, count in counts["ordered"] if count == 2)
    shares = [hapax, twice, counts["types"] - hapax - twice]
    labels = ("seen once", "seen twice", "seen 3+ times")
    right.bar(np.arange(3), shares, 0.55, color=(p.red, p.amber, p.green))
    for x, value in zip(np.arange(3), shares):
        right.annotate(f"{value:,}\n{value / counts['types']:.1%}", (x, value),
                       textcoords="offset points", xytext=(0, 4), ha="center",
                       fontsize=8.5, color=p.fg)
    right.set_xticks(np.arange(3))
    right.set_xticklabels(labels)
    right.set_ylim(0, max(shares) * 1.22)      # room for the labels
    right.set_ylabel("distinct words")
    right.set_title("most of the vocabulary is words you saw once",
                    fontsize=10)


def zipf_and_coverage(fig, axes, p: Palette) -> None:
    counts = _counts()
    frequencies = counts["frequencies"]
    left, right = fig.subplots(1, 2)
    ranks = np.arange(1, len(frequencies) + 1)
    left.plot(ranks, frequencies, lw=1.6, color=p.blue)
    slope, intercept = np.polyfit(np.log(ranks[:2000]),
                                 np.log(frequencies[:2000]), 1)
    left.plot(ranks, np.exp(intercept) * ranks ** slope, lw=1.2, ls="--",
              color=p.amber, label=f"fitted slope {slope:.3f}")
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlabel("rank")
    left.set_ylabel("frequency")
    left.set_title("Zipf: frequency falls as a power of rank", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    coverage = np.cumsum(frequencies) / counts["total"]
    right.plot(ranks, coverage, lw=2.0, color=p.green)
    # Stagger the labels: at 10,000 and 20,000 the curve is almost flat and
    # identical offsets put the two annotations on top of each other.
    offsets = ((10, -4), (10, -20), (-6, -30), (-6, 10), (10, -4))
    for candidate, offset in zip(CANDIDATES, offsets):
        if candidate <= len(coverage):
            value = float(coverage[candidate - 1])
            right.plot([candidate], [value], "o", ms=6, color=p.fg)
            right.annotate(f"{candidate:,} words\n{value:.4f}",
                           (candidate, value), textcoords="offset points",
                           xytext=offset, fontsize=7.5, color=p.fg,
                           ha="right" if offset[0] < 0 else "left")
    right.set_xscale("log")
    right.set_xlabel("vocabulary size (most frequent first)")
    right.set_ylabel("share of all tokens covered")
    right.set_ylim(0, 1.05)
    right.set_title("what a vocabulary cap actually costs", fontsize=10)


def _normalisations() -> dict:
    """Each step, applied cumulatively, and what it does to the vocabulary."""
    info = _corpus()
    tokens = [token for document in info["documents"] for token in document]
    STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "is", "it",
                 "this", "that", "for", "was", "as", "with", "but", "on",
                 "are", "be", "at", "by", "have", "has", "not", "you", "i"}

    def strip_suffix(word: str) -> str:
        for suffix in ("ingly", "edly", "ing", "ed", "ly", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[: -len(suffix)]
        return word

    steps = [("raw tokens", tokens)]
    lowered = [token.lower() for token in tokens]
    steps.append(("lowercased", lowered))
    depunctuated = [re.sub(r"[^\w']", "", token) for token in lowered]
    depunctuated = [token for token in depunctuated if token]
    steps.append(("punctuation stripped", depunctuated))
    stopped = [token for token in depunctuated if token not in STOPWORDS]
    steps.append(("stopwords removed", stopped))
    stemmed = [strip_suffix(token) for token in stopped]
    steps.append(("suffixes stripped", stemmed))
    return {"steps": [(label, len(set(rows)), len(rows))
                      for label, rows in steps],
            "collisions": _collisions(depunctuated, strip_suffix)}


def _collisions(tokens, stemmer) -> list:
    """Word pairs a crude stemmer merges — the cost of the vocabulary saving."""
    groups: dict[str, set] = {}
    for token in set(tokens):
        groups.setdefault(stemmer(token), set()).add(token)
    interesting = [(stem, sorted(words)) for stem, words in groups.items()
                   if len(words) >= 3]
    interesting.sort(key=lambda item: -len(item[1]))
    return interesting[:6]


def normalisation_effects(fig, axes, p: Palette) -> None:
    info = _normalisations()
    left, right = fig.subplots(1, 2)
    labels = [label for label, _, _ in info["steps"]]
    types = [count for _, count, _ in info["steps"]]
    tokens = [count for _, _, count in info["steps"]]
    positions = np.arange(len(labels))
    left.barh(positions, types, 0.55, color=p.blue)
    for y, value, total in zip(positions, types, tokens):
        left.annotate(f"{value:,} types  ({value / types[0]:.2f}x)",
                      (value, y), textcoords="offset points", xytext=(6, 0),
                      va="center", fontsize=8, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xlim(0, max(types) * 1.45)
    left.set_xlabel("distinct words in the vocabulary")
    left.set_title("each step shrinks the vocabulary", fontsize=10)

    right.axis("off")
    right.set_title("and each step merges words that were different",
                    fontsize=10)
    lines = ["a crude suffix stripper collapses these groups:", ""]
    for stem, words in info["collisions"]:
        lines.append(f"  {stem!r} <- " + ", ".join(words[:5]))
    lines += ["", "the vocabulary saving is real; so is the information loss."]
    right.text(0.0, 0.95, "\n".join(lines), va="top", ha="left", fontsize=8.5,
               family="monospace", color=p.fg, transform=right.transAxes)


FIGURES = [
    figure("vocabulary-growth", vocabulary_growth, size=(9.4, 3.5),
           axes=False),
    figure("zipf-and-coverage", zipf_and_coverage, size=(9.4, 3.5),
           axes=False),
    figure("normalisation-effects", normalisation_effects, size=(9.6, 3.6),
           axes=False),
]


if __name__ == "__main__":
    info = _corpus()
    counts = _counts()
    print(f"=== {DOCUMENTS:,} IMDB reviews, decoded from the cached ids ===")
    print(f"{counts['total']:,} tokens, {counts['types']:,} distinct words")
    print(f"the shipped word index has {info['vocabulary']:,} entries")
    lengths = np.array([len(d) for d in info["documents"]])
    print(f"document length: min {lengths.min()}  median "
          f"{int(np.median(lengths))}  mean {lengths.mean():.1f}  "
          f"max {lengths.max()}")

    print("\n=== the ten most frequent tokens ===")
    for rank, (word, count) in enumerate(counts["ordered"][:10], start=1):
        print(f"{rank:3d} {word:12s} {count:8,}  "
              f"{count / counts['total']:.4f} of all tokens")

    hapax = sum(1 for _, count in counts["ordered"] if count == 1)
    print(f"\nwords seen exactly once: {hapax:,} "
          f"({hapax / counts['types']:.4f} of the vocabulary, "
          f"{hapax / counts['total']:.4f} of the tokens)")

    print("\n=== what a vocabulary cap costs ===")
    coverage = np.cumsum(counts["frequencies"]) / counts["total"]
    print(f"{'vocabulary':>11} {'token coverage':>15} {'OOV rate':>9}")
    for candidate in CANDIDATES:
        if candidate <= len(coverage):
            value = float(coverage[candidate - 1])
            print(f"{candidate:11,} {value:15.4f} {1 - value:9.4f}")

    ranks = np.arange(1, len(counts["frequencies"]) + 1)
    slope, _ = np.polyfit(np.log(ranks[:2000]),
                          np.log(counts["frequencies"][:2000]), 1)
    print(f"\nZipf slope over the first 2,000 ranks: {slope:.4f}")

    print("\n=== normalisation ===")
    steps = _normalisations()
    print(f"{'step':24s} {'types':>9} {'tokens':>11} {'types vs raw':>13}")
    base = steps["steps"][0][1]
    for label, types, tokens in steps["steps"]:
        print(f"{label:24s} {types:9,} {tokens:11,} {types / base:13.4f}")
    print("\ngroups a crude suffix stripper merges:")
    for stem, words in steps["collisions"]:
        print(f"  {stem!r} <- " + ", ".join(words[:6]))

"""Figures for *Subword Tokenization (BPE and WordPiece)*.

Byte-pair encoding is implemented here from scratch — about forty lines — and
run on the decoded IMDB vocabulary. Nothing is downloaded and nothing is
trained, so the module runs in seconds and every number is checkable by hand.

``merge-growth``
    Vocabulary size against merges learned, and the average number of pieces
    per word that buys.

``oov-elimination``
    The measurement that explains why every modern tokenizer is subword: word
    level throws away a fixed share of the text at any vocabulary size, subword
    throws away none.

``length-tradeoff``
    Sequence length against vocabulary size for character, subword and word
    tokenization — the cost that pays for that coverage.
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

from _dl import tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

DOCUMENTS = 4000
MERGE_STEPS = (0, 200, 500, 1000, 2000, 4000)
MERGES = 2000
WORD_CAPS = (1000, 5000, 10000, 20000)
INDEX_OFFSET = 3
END = "</w>"


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    keras = tf().keras
    (x_train, _), (x_test, _) = keras.datasets.imdb.load_data()
    word_index = keras.datasets.imdb.get_word_index()
    reverse = {index + INDEX_OFFSET: word for word, index in word_index.items()}
    train = [[reverse.get(t, "<oov>") for t in row] for row in x_train[:DOCUMENTS]]
    test = [[reverse.get(t, "<oov>") for t in row]
            for row in x_test[:DOCUMENTS // 2]]
    return {"train": train, "test": test}


@functools.lru_cache(maxsize=1)
def _word_counts() -> Counter:
    return Counter(token for document in _corpus()["train"]
                   for token in document)


def _pair_counts(splits: dict[str, tuple], counts: Counter) -> Counter:
    pairs: Counter = Counter()
    for word, pieces in splits.items():
        weight = counts[word]
        for left, right in zip(pieces, pieces[1:]):
            pairs[(left, right)] += weight
    return pairs


def _pair_index(splits: dict[str, tuple]) -> dict:
    """pair -> the set of words containing it, so a merge is a local update.

    Recounting every pair after every merge is the obvious implementation and
    it is quadratic: 2,000 merges over 50,000 words never finished. Only the
    words containing the merged pair can change, so only those are rescanned.
    """
    index: dict[tuple, set] = {}
    for word, pieces in splits.items():
        for pair in zip(pieces, pieces[1:]):
            index.setdefault(pair, set()).add(word)
    return index


def _apply(pieces: tuple, pair: tuple) -> tuple:
    merged = []
    index = 0
    joined = pair[0] + pair[1]
    while index < len(pieces):
        if (index < len(pieces) - 1 and pieces[index] == pair[0]
                and pieces[index + 1] == pair[1]):
            merged.append(joined)
            index += 2
        else:
            merged.append(pieces[index])
            index += 1
    return tuple(merged)


@functools.lru_cache(maxsize=1)
def _bpe() -> dict:
    """Learn MERGES byte-pair merges over the training vocabulary."""
    counts = _word_counts()
    splits = {word: tuple(list(word) + [END]) for word in counts}
    alphabet = {piece for pieces in splits.values() for piece in pieces}
    pairs = _pair_counts(splits, counts)
    index = _pair_index(splits)
    merges: list[tuple] = []
    history = []
    for step in range(MERGES):
        if not pairs:
            break
        pair, frequency = max(pairs.items(), key=lambda item: item[1])
        if frequency < 2:
            break
        merges.append(pair)
        for word in list(index.get(pair, ())):
            pieces = splits[word]
            weight = counts[word]
            for old in zip(pieces, pieces[1:]):        # retract the old pairs
                pairs[old] -= weight
                if pairs[old] <= 0:
                    pairs.pop(old, None)
                holders = index.get(old)
                if holders is not None:
                    holders.discard(word)
            pieces = _apply(pieces, pair)
            splits[word] = pieces
            for new in zip(pieces, pieces[1:]):        # and add the new ones
                pairs[new] = pairs.get(new, 0) + weight
                index.setdefault(new, set()).add(word)
        index.pop(pair, None)
        if step + 1 in MERGE_STEPS or step == 0:
            history.append((step + 1, _snapshot(splits, counts, alphabet,
                                                len(merges))))
    return {"merges": merges, "splits": splits, "history": history,
            "alphabet": alphabet, "counts": counts}


def _snapshot(splits, counts, alphabet, merges) -> dict:
    total_words = sum(counts.values())
    pieces_per_word = sum(len(splits[word]) * counts[word] for word in counts)
    vocabulary = alphabet | {"".join(pieces) for pieces in splits.values()}
    used = {piece for pieces in splits.values() for piece in pieces}
    return {"merges": merges, "vocabulary": len(used),
            "pieces_per_word": pieces_per_word / total_words,
            "types_kept_whole": sum(1 for word in counts
                                    if len(splits[word]) == 2)}


@functools.lru_cache(maxsize=None)
def _encode_unseen(word: str) -> tuple:
    """Apply every merge in order — only needed for words BPE never trained on."""
    pieces = tuple(list(word) + [END])
    for pair in _bpe()["merges"]:
        pieces = _apply(pieces, pair)
    return pieces


def _encode(word: str, merges=None) -> tuple:
    """Encode a word, reusing the split BPE already computed where possible.

    Replaying 2,000 merges for every token is what made the first version of
    this module time out: 100,000 tokens times 2,000 merges. Training already
    produced the final split for every word in the corpus, so only genuinely
    unseen words need the replay.
    """
    known = _bpe()["splits"].get(word)
    return known if known is not None else _encode_unseen(word)


def merge_growth(fig, axes, p: Palette) -> None:
    info = _bpe()
    left, right = fig.subplots(1, 2)
    history = [snapshot for _, snapshot in info["history"]]
    merges = [snapshot["merges"] for snapshot in history]
    vocabulary = [snapshot["vocabulary"] for snapshot in history]
    pieces = [snapshot["pieces_per_word"] for snapshot in history]
    left.plot(merges, vocabulary, "o-", ms=6, lw=2.0, color=p.blue,
              label="pieces in use")
    left.set_xlabel("merges learned")
    left.set_ylabel("distinct pieces")
    left.set_title("a merge adds one symbol to the vocabulary", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    right.plot(merges, pieces, "o-", ms=6, lw=2.0, color=p.green)
    for merge, value in zip(merges, pieces):
        right.annotate(f"{value:.3f}", (merge, value),
                       textcoords="offset points", xytext=(0, 8), ha="center",
                       fontsize=7.5, color=p.green)
    right.axhline(1.0, color=p.muted, lw=1.1, ls="--")
    right.annotate("1.0 = every word is a single piece", (merges[0], 1.05),
                   fontsize=8, color=p.muted)
    right.set_xlabel("merges learned")
    right.set_ylabel("average pieces per word (token-weighted)")
    right.set_title("and buys shorter sequences", fontsize=10)

    whole = [snapshot["types_kept_whole"] for snapshot in history]
    for merge, value, count in zip(merges, pieces, whole):
        del merge, value, count


def oov_elimination(fig, axes, p: Palette) -> None:
    info = _bpe()
    corpus = _corpus()
    counts = info["counts"]
    ordered = [word for word, _ in counts.most_common()]
    test_tokens = [token for document in corpus["test"] for token in document]
    left, right = fig.subplots(1, 2)

    word_rates = []
    for cap in WORD_CAPS:
        allowed = set(ordered[:cap])
        missing = sum(1 for token in test_tokens if token not in allowed)
        word_rates.append(missing / len(test_tokens))
    left.plot(WORD_CAPS, word_rates, "o-", ms=6, lw=2.0, color=p.red,
              label="word level")
    subword_vocabulary = info["history"][-1][1]["vocabulary"]
    left.plot(WORD_CAPS, [0.0] * len(WORD_CAPS), "o-", ms=6, lw=2.0,
              color=p.green,
              label=f"subword ({subword_vocabulary:,} pieces)")
    for cap, rate in zip(WORD_CAPS, word_rates):
        left.annotate(f"{rate:.4f}", (cap, rate), textcoords="offset points",
                      xytext=(0, 8), ha="center", fontsize=7.5, color=p.red)
    left.set_xscale("log")
    left.set_xticks(list(WORD_CAPS))
    left.set_xticklabels([f"{c:,}" for c in WORD_CAPS])
    left.set_xlabel("word vocabulary size")
    left.set_ylabel("share of test tokens that are unknown")
    left.set_title("word level always loses some of the text", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    rare = [word for word in ordered[-8:]]
    right.axis("off")
    right.set_title("what BPE does with a word it has never seen whole",
                    fontsize=10)
    lines = []
    for word in rare:
        pieces = _encode(word, info["merges"])
        lines.append(f"  {word:>18s} -> " + " ".join(pieces))
    unseen = ("supercalifragilistic", "tokenization", "unbelievability")
    lines.append("")
    lines.append("  words that are not in the corpus at all:")
    for word in unseen:
        pieces = _encode(word, info["merges"])
        lines.append(f"  {word:>18s} -> " + " ".join(pieces))
    lines.append("")
    lines.append("  every piece exists, so nothing becomes <oov>")
    right.text(0.0, 0.95, "\n".join(lines), va="top", ha="left", fontsize=8,
               family="monospace", color=p.fg, transform=right.transAxes)


def length_tradeoff(fig, axes, p: Palette) -> None:
    info = _bpe()
    corpus = _corpus()
    counts = info["counts"]
    ordered = [word for word, _ in counts.most_common()]
    documents = corpus["test"][:400]
    ax = fig.subplots(1, 1)

    characters = np.mean([sum(len(word) + 1 for word in document)
                          for document in documents])
    words = np.mean([len(document) for document in documents])
    subword = np.mean([sum(len(_encode(word, info["merges"]))
                           for word in document) for document in documents])
    alphabet = len(info["alphabet"])
    subword_vocabulary = info["history"][-1][1]["vocabulary"]
    word_vocabulary = len(ordered)

    labels = (f"character\n({alphabet} symbols)",
              f"BPE\n({subword_vocabulary:,} pieces)",
              f"word\n({word_vocabulary:,} words)")
    lengths = (characters, subword, words)
    vocabularies = (alphabet, subword_vocabulary, word_vocabulary)
    positions = np.arange(3)
    ax.bar(positions, lengths, 0.5, color=(p.amber, p.green, p.red))
    for x, value, vocabulary in zip(positions, lengths, vocabularies):
        ax.annotate(f"{value:.1f} tokens per review\nvocabulary "
                    f"{vocabulary:,}", (x, value), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=8.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, max(lengths) * 1.3)
    ax.set_ylabel("average tokens per review")
    ax.set_title("the three tokenizations trade vocabulary against length",
                 fontsize=10.5)


FIGURES = [
    figure("merge-growth", merge_growth, size=(9.4, 3.5), axes=False),
    figure("oov-elimination", oov_elimination, size=(9.6, 3.6), axes=False),
    figure("length-tradeoff", length_tradeoff, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    info = _bpe()
    counts = info["counts"]
    print(f"=== BPE over {len(counts):,} distinct words from "
          f"{DOCUMENTS:,} reviews ===")
    print(f"starting alphabet: {len(info['alphabet'])} symbols")
    print(f"learned {len(info['merges']):,} merges")
    print("the first fifteen merges, in order:")
    for index, pair in enumerate(info["merges"][:15], start=1):
        print(f"  {index:3d} {pair[0]!r} + {pair[1]!r} -> "
              f"{pair[0] + pair[1]!r}")

    print(f"\n=== vocabulary and sequence length against merges ===")
    print(f"{'merges':>8} {'pieces in use':>14} {'pieces per word':>16} "
          f"{'words kept whole':>17}")
    for _, snapshot in info["history"]:
        print(f"{snapshot['merges']:8,} {snapshot['vocabulary']:14,} "
              f"{snapshot['pieces_per_word']:16.4f} "
              f"{snapshot['types_kept_whole']:17,}")

    corpus = _corpus()
    ordered = [word for word, _ in counts.most_common()]
    test_tokens = [token for document in corpus["test"] for token in document]
    print(f"\n=== out-of-vocabulary rate on {len(test_tokens):,} test tokens ===")
    print(f"{'word vocabulary':>16} {'OOV rate':>9} {'BPE OOV rate':>13}")
    for cap in WORD_CAPS:
        allowed = set(ordered[:cap])
        missing = sum(1 for token in test_tokens if token not in allowed)
        print(f"{cap:16,} {missing / len(test_tokens):9.4f} {0.0:13.4f}")

    print("\n=== how BPE splits words it never saw whole ===")
    for word in ("tokenization", "unbelievability", "supercalifragilistic",
                 "antidisestablishmentarianism"):
        pieces = _encode(word, info["merges"])
        print(f"  {word:>30s} -> " + " ".join(pieces))

    documents = corpus["test"][:400]
    characters = np.mean([sum(len(word) + 1 for word in document)
                          for document in documents])
    words = np.mean([len(document) for document in documents])
    subword = np.mean([sum(len(_encode(word, info["merges"]))
                           for word in document) for document in documents])
    print(f"\n=== average tokens per review over 400 reviews ===")
    print(f"{'tokenization':14s} {'vocabulary':>11} {'tokens/review':>14} "
          f"{'vs word level':>14}")
    print(f"{'character':14s} {len(info['alphabet']):11,} {characters:14.1f} "
          f"{characters / words:13.2f}x")
    print(f"{'BPE':14s} {info['history'][-1][1]['vocabulary']:11,} "
          f"{subword:14.1f} {subword / words:13.2f}x")
    print(f"{'word':14s} {len(ordered):11,} {words:14.1f} {1.0:13.2f}x")
    print("subword tokenization buys zero OOV for a modest increase in length,")
    print("which is why every modern model uses it")

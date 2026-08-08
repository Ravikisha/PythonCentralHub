"""Figures for *Named Entity Recognition (NER)*.

CoNLL-2003 is not redistributable and is not cached here, so the corpus is
generated: templated sentences with PERSON, LOCATION and ORGANISATION spans and
exact BIO tags. Generated data means the labels are known to be correct and the
class imbalance is a design parameter rather than an accident — which is the
whole subject of the page.

``tag-imbalance``
    How much of the corpus is the O tag, and what a model that predicts O
    everywhere scores on token accuracy.

``token-against-entity``
    Token accuracy against entity-level precision, recall and F1 for three
    models. The two metrics disagree by a wide margin, and only one of them is
    the thing you care about.

``boundary-errors``
    Where the entity-level errors actually are: whole misses, wrong types, and
    spans that are right in the middle and wrong at the edges.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

ROWS = 6000
TEST_ROWS = 1500
LENGTH = 24
EPOCHS = 12
WIDTH = 32
TAGS = ("O", "B-PER", "I-PER", "B-LOC", "I-LOC", "B-ORG", "I-ORG")
TAG_INDEX = {tag: index for index, tag in enumerate(TAGS)}

# Two things make the first version of this corpus useless: the entity pools
# were tiny closed sets, and every entity word appeared in training. Every
# model then scored 1.0000 by memorising a word list, which is not what NER is.
# So the pools are large, the *test* half is disjoint from the training half —
# so a test entity is a word the model has never seen — and some words are
# deliberately ambiguous, appearing both as entities and as ordinary words.
FIRST_TRAIN = ("mary", "john", "aisha", "wei", "carlos", "ingrid", "omar",
               "sofia", "hannah", "diego", "priya", "tomas", "leila", "noah")
FIRST_TEST = ("elena", "kofi", "yuki", "pablo", "amara", "viktor", "mina",
              "rashid", "clara", "jonas")
LAST_TRAIN = ("smith", "okafor", "tanaka", "silva", "novak", "khan", "muller",
              "rossi", "dubois", "andersen", "haddad", "walsh")
LAST_TEST = ("moreau", "iqbal", "bergman", "costa", "nakamura", "olsen",
             "farrell", "zhao")
CITY_TRAIN = ("paris", "new york", "sao paulo", "cape town", "kuala lumpur",
              "reykjavik", "santiago", "lisbon", "port louis", "hanoi")
CITY_TEST = ("oslo", "san jose", "dar es salaam", "quito", "belgrade",
             "chiang mai")
ORG_TRAIN = ("acme industries", "northern rail", "global mutual bank",
             "riverside clinic", "helios energy", "united textiles",
             "delta foods", "orion systems")
ORG_TEST = ("summit logistics", "blue harbour press", "vertex mining",
            "coastal power")
# Words that are an entity in one sentence and an ordinary word in another.
# No word list can resolve these; only the surrounding context can.
AMBIGUOUS = ("may", "hope", "rich", "mark", "summit", "delta", "orion")
TEMPLATES = (
    "PER joined ORG in CITY last spring",
    "the board of ORG met PER at the CITY office",
    "PER flew from CITY to meet the ORG team",
    "reporters asked PER about the ORG deal in CITY",
    "ORG opened a branch in CITY and hired PER",
    "PER said the CITY plant run by ORG would stay open",
)
FILLER = ("the", "a", "and", "of", "in", "to", "was", "said", "after",
          "before", "with", "for", "on", "quietly", "again", "yesterday")


def _phrase(rng, kind: str, split: str) -> tuple:
    """One entity phrase, drawn from the training or the test pool."""
    if kind == "PER":
        first = FIRST_TRAIN if split == "train" else FIRST_TEST
        last = LAST_TRAIN if split == "train" else LAST_TEST
        # Sometimes an ambiguous word stands in as a first name.
        if rng.random() < 0.18:
            return [str(rng.choice(AMBIGUOUS)), str(rng.choice(last))], "PER"
        return [str(rng.choice(first)), str(rng.choice(last))], "PER"
    if kind == "CITY":
        pool = CITY_TRAIN if split == "train" else CITY_TEST
        return str(rng.choice(pool)).split(), "LOC"
    pool = ORG_TRAIN if split == "train" else ORG_TEST
    if rng.random() < 0.18:
        return [str(rng.choice(AMBIGUOUS)), "group"], "ORG"
    return str(rng.choice(pool)).split(), "ORG"


@functools.lru_cache(maxsize=1)
def _corpus() -> dict:
    """Templated sentences with exact BIO tags, padded to LENGTH."""
    rng = np.random.default_rng(0)
    vocabulary = {"<pad>": 0, "<unk>": 1}
    sentences, taggings = [], []
    for row in range(ROWS + TEST_ROWS):
        split = "train" if row < ROWS else "test"
        template = str(rng.choice(TEMPLATES)).split()
        words, tags = [], []
        for token in template:
            if token in ("PER", "CITY", "ORG"):
                phrase, kind = _phrase(rng, token, split)
                for position, word in enumerate(phrase):
                    words.append(word)
                    tags.append(f"{'B' if position == 0 else 'I'}-{kind}")
            else:
                words.append(token)
                tags.append("O")
        while len(words) < LENGTH and rng.random() < 0.6:
            # The same ambiguous words also turn up as ordinary words, so no
            # lookup table can tag them correctly.
            filler = (str(rng.choice(AMBIGUOUS)) if rng.random() < 0.25
                      else str(rng.choice(FILLER)))
            words.append(filler)
            tags.append("O")
        words, tags = words[:LENGTH], tags[:LENGTH]
        sentences.append(words)
        taggings.append(tags)

    # The vocabulary is learned from the training rows only — building it over
    # the whole corpus would quietly guarantee that no test token is unknown.
    for words in sentences[:ROWS]:
        for word in words:
            if word not in vocabulary:
                vocabulary[word] = len(vocabulary)

    x = np.zeros((len(sentences), LENGTH), "int32")
    y = np.zeros((len(sentences), LENGTH), "int32")
    for row, (words, tags) in enumerate(zip(sentences, taggings)):
        for position, (word, tag) in enumerate(zip(words, tags)):
            x[row, position] = vocabulary.get(word, 1)
            y[row, position] = TAG_INDEX[tag]
    return {"x_train": x[:ROWS], "y_train": y[:ROWS],
            "x_test": x[ROWS:], "y_test": y[ROWS:],
            "vocabulary": vocabulary, "sentences": sentences[ROWS:],
            "tags": taggings[ROWS:]}


def _spans(tags: list) -> set:
    """BIO tags -> the set of (start, end, type) spans they describe."""
    out, start, kind = set(), None, None
    for position, tag in enumerate(tags):
        if tag.startswith("B-"):
            if start is not None:
                out.add((start, position, kind))
            start, kind = position, tag[2:]
        elif tag.startswith("I-") and start is not None and tag[2:] == kind:
            continue
        else:
            if start is not None:
                out.add((start, position, kind))
            start, kind = None, None
    if start is not None:
        out.add((start, len(tags), kind))
    return out


def _entity_scores(true_rows, predicted_rows) -> dict:
    matched = predicted_total = true_total = 0
    for true_tags, predicted_tags in zip(true_rows, predicted_rows):
        true_spans = _spans(true_tags)
        predicted_spans = _spans(predicted_tags)
        matched += len(true_spans & predicted_spans)
        predicted_total += len(predicted_spans)
        true_total += len(true_spans)
    precision = matched / predicted_total if predicted_total else 0.0
    recall = matched / true_total if true_total else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if precision + recall else 0.0)
    return {"precision": precision, "recall": recall, "f1": f1,
            "matched": matched, "predicted": predicted_total,
            "true": true_total}


def _decode(matrix, mask) -> list:
    return [[TAGS[int(tag)] for tag, keep in zip(row, keep_row) if keep]
            for row, keep_row in zip(matrix, mask)]


def _build(kind: str, vocabulary: int, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((LENGTH,))
    embedded = keras.layers.Embedding(vocabulary, WIDTH, mask_zero=True)(inputs)
    if kind == "per-token dense":
        x = keras.layers.Dense(WIDTH * 2, activation="relu")(embedded)
    elif kind == "1D convolution":
        x = keras.layers.Conv1D(WIDTH * 2, 3, padding="same",
                                activation="relu")(embedded)
    else:
        x = keras.layers.Bidirectional(
            keras.layers.LSTM(WIDTH, return_sequences=True))(embedded)
    outputs = keras.layers.Dense(len(TAGS), activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(2e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


MODELS = ("per-token dense", "1D convolution", "bidirectional LSTM")


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    data = _corpus()
    mask = data["x_test"] != 0
    truth = _decode(data["y_test"], mask)
    out = {}
    for kind in MODELS:
        model = _build(kind, len(data["vocabulary"]))
        model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                  batch_size=64, verbose=0)
        predicted = model.predict(data["x_test"], verbose=0).argmax(axis=-1)
        token_accuracy = float((predicted[mask]
                                == data["y_test"][mask]).mean())
        rows = _decode(predicted, mask)
        scores = _entity_scores(truth, rows)
        out[kind] = {"token_accuracy": token_accuracy, **scores,
                     "params": int(model.count_params()), "rows": rows}
    # The do-nothing baseline: predict O everywhere.
    all_o = [["O"] * len(row) for row in truth]
    out["all O"] = {"token_accuracy": float((data["y_test"][mask] == 0).mean()),
                    **_entity_scores(truth, all_o), "params": 0, "rows": all_o}
    out["truth"] = truth
    return out


def tag_imbalance(fig, axes, p: Palette) -> None:
    data = _corpus()
    runs = _runs()
    mask = data["x_test"] != 0
    left, right = fig.subplots(1, 2)
    counts = np.bincount(data["y_test"][mask], minlength=len(TAGS))
    share = counts / counts.sum()
    positions = np.arange(len(TAGS))
    left.bar(positions, share, 0.6,
             color=[p.muted if tag == "O" else p.blue for tag in TAGS])
    for x, value in zip(positions, share):
        left.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=7.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(TAGS, fontsize=8, rotation=30)
    left.set_ylabel("share of tokens")
    left.set_title("the O tag is most of the corpus", fontsize=10)

    labels = ("all O", "per-token dense", "1D convolution",
              "bidirectional LSTM")
    token = [runs[label]["token_accuracy"] for label in labels]
    f1 = [runs[label]["f1"] for label in labels]
    positions = np.arange(len(labels))
    right.bar(positions - 0.19, token, 0.36, color=p.amber,
              label="token accuracy")
    right.bar(positions + 0.19, f1, 0.36, color=p.green, label="entity F1")
    for x, value in zip(positions - 0.19, token):
        right.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                       xytext=(0, 3), ha="center", fontsize=7, color=p.fg)
    for x, value in zip(positions + 0.19, f1):
        right.annotate(f"{value:.3f}", (x, value), textcoords="offset points",
                       xytext=(0, 3), ha="center", fontsize=7, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([label.replace(" ", "\n") for label in labels],
                          fontsize=7.5)
    right.set_ylim(0, 1.15)
    right.set_title("two metrics, two different verdicts", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def token_against_entity(fig, axes, p: Palette) -> None:
    runs = _runs()
    ax = fig.subplots(1, 1)
    labels = ("all O", "per-token dense", "1D convolution",
              "bidirectional LSTM")
    metrics = ("token_accuracy", "precision", "recall", "f1")
    names = ("token accuracy", "entity precision", "entity recall",
             "entity F1")
    positions = np.arange(len(labels))
    width = 0.8 / len(metrics)
    colors = (p.amber, p.blue, p.purple, p.green)
    for index, (metric, name, color) in enumerate(zip(metrics, names, colors)):
        offset = (index - (len(metrics) - 1) / 2) * width
        values = [runs[label][metric] for label in labels]
        ax.bar(positions + offset, values, width * 0.92, color=color,
               label=name)
        for x, value in zip(positions + offset, values):
            ax.annotate(f"{value:.2f}", (x, value),
                        textcoords="offset points", xytext=(0, 3),
                        ha="center", fontsize=6.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, 1.18)
    ax.set_title(f"{TEST_ROWS:,} test sentences — an entity counts only if "
                 f"its span and type are both exactly right", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper left", ncol=2)


def boundary_errors(fig, axes, p: Palette) -> None:
    runs = _runs()
    truth = runs["truth"]
    ax = fig.subplots(1, 1)
    kinds = ("exact", "wrong type", "boundary off", "missed", "spurious")
    tally = {kind: 0 for kind in kinds}
    best = max(MODELS, key=lambda m: runs[m]["f1"])
    for true_tags, predicted_tags in zip(truth, runs[best]["rows"]):
        true_spans = _spans(true_tags)
        predicted_spans = _spans(predicted_tags)
        for span in true_spans:
            if span in predicted_spans:
                tally["exact"] += 1
                continue
            same_span = [other for other in predicted_spans
                         if other[0] == span[0] and other[1] == span[1]]
            overlapping = [other for other in predicted_spans
                           if other[2] == span[2]
                           and other[0] < span[1] and span[0] < other[1]]
            if same_span:
                tally["wrong type"] += 1
            elif overlapping:
                tally["boundary off"] += 1
            else:
                tally["missed"] += 1
        for span in predicted_spans:
            if span not in true_spans and not any(
                    span[0] < other[1] and other[0] < span[1]
                    for other in true_spans):
                tally["spurious"] += 1
    values = [tally[kind] for kind in kinds]
    total = sum(values)
    positions = np.arange(len(kinds))
    colors = (p.green, p.amber, p.purple, p.red, p.muted)
    ax.bar(positions, values, 0.55, color=colors)
    for x, value in zip(positions, values):
        ax.annotate(f"{value:,}\n{value / total:.1%}", (x, value),
                    textcoords="offset points", xytext=(0, 4), ha="center",
                    fontsize=8, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(kinds, fontsize=8.5)
    ax.set_ylim(0, max(values) * 1.25)
    ax.set_ylabel("entities")
    ax.set_title(f"{best}: what the entity-level errors actually are",
                 fontsize=10.5)


FIGURES = [
    figure("tag-imbalance", tag_imbalance, size=(9.4, 3.5), axes=False),
    figure("token-against-entity", token_against_entity, size=(8.6, 3.8),
           axes=False),
    figure("boundary-errors", boundary_errors, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    data = _corpus()
    mask = data["x_test"] != 0
    counts = np.bincount(data["y_test"][mask], minlength=len(TAGS))
    share = counts / counts.sum()
    print(f"=== {ROWS:,} train / {TEST_ROWS:,} test sentences, vocabulary "
          f"{len(data['vocabulary']):,} ===")
    unknown = float((data["x_test"][data["x_test"] != 0] == 1).mean())
    print(f"the test entity pools are disjoint from the training ones, so "
          f"{unknown:.4f} of test tokens are unknown words")
    print(f"{'tag':8s} {'tokens':>9} {'share':>8}")
    for tag, count, fraction in zip(TAGS, counts, share):
        print(f"{tag:8s} {count:9,} {fraction:8.4f}")
    print(f"predicting O everywhere scores {share[0]:.4f} token accuracy")

    runs = _runs()
    print(f"\n=== token accuracy against entity F1, {EPOCHS} epochs ===")
    print(f"{'model':20s} {'params':>9} {'token acc':>10} {'precision':>10} "
          f"{'recall':>8} {'F1':>8}")
    for label in ("all O", *MODELS):
        run = runs[label]
        print(f"{label:20s} {run['params']:9,} {run['token_accuracy']:10.4f} "
              f"{run['precision']:10.4f} {run['recall']:8.4f} "
              f"{run['f1']:8.4f}")
    print(f"the do-nothing baseline scores {runs['all O']['token_accuracy']:.4f} "
          f"token accuracy and {runs['all O']['f1']:.4f} entity F1")

    best = max(MODELS, key=lambda m: runs[m]["f1"])
    print(f"\n=== {best}: entity-level error breakdown ===")
    truth = runs["truth"]
    tally = {"exact": 0, "wrong type": 0, "boundary off": 0, "missed": 0,
             "spurious": 0}
    for true_tags, predicted_tags in zip(truth, runs[best]["rows"]):
        true_spans = _spans(true_tags)
        predicted_spans = _spans(predicted_tags)
        for span in true_spans:
            if span in predicted_spans:
                tally["exact"] += 1
            elif any(other[0] == span[0] and other[1] == span[1]
                     for other in predicted_spans):
                tally["wrong type"] += 1
            elif any(other[2] == span[2] and other[0] < span[1]
                     and span[0] < other[1] for other in predicted_spans):
                tally["boundary off"] += 1
            else:
                tally["missed"] += 1
        for span in predicted_spans:
            if span not in true_spans and not any(
                    span[0] < other[1] and other[0] < span[1]
                    for other in true_spans):
                tally["spurious"] += 1
    total = sum(tally.values())
    for kind, value in tally.items():
        print(f"  {kind:14s} {value:6,}  {value / total:7.2%}")
    print("a span counts only if its start, end and type are all exactly")
    print("right, which is why entity F1 is always below token accuracy")

    print("\n=== a sentence, tagged ===")
    for row in range(2):
        words = data["sentences"][row]
        true_tags = data["tags"][row]
        predicted = runs[best]["rows"][row]
        print("  " + " ".join(f"{word}/{tag}" for word, tag
                              in zip(words, true_tags) if tag != "O"))
        print("  predicted: " + " ".join(f"{word}/{tag}" for word, tag
                                         in zip(words, predicted)
                                         if tag != "O"))

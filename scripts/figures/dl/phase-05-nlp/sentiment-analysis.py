"""Figures for *Sentiment Analysis Tutorial*.

This is the phase's bake-off: five model families on one dataset, one split and
one budget, so the comparison means something. The point of the page is not
which family wins — it is that the ranking is not the one the reading order
suggests.

``family-comparison``
    Accuracy, parameters and wall-clock for every family, against the
    bag-of-words baseline.

``data-scaling``
    The same families at three training-set sizes, because "which model is
    best" is really "best at what amount of data".

``errors``
    What the winning model actually gets wrong, and how much of that is
    reachable by any bag-of-words model.
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
EPOCHS = 8
WIDTH = 32
SIZES = (1000, 4000, 8000)
INDEX_OFFSET = 3
FAMILIES = ("TF-IDF + logistic", "average embedding", "1D convolution",
            "LSTM", "transformer block")


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    keras = tf().keras
    reviews = imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)
    word_index = keras.datasets.imdb.get_word_index()
    reverse = {index + INDEX_OFFSET: word for word, index in word_index.items()}

    def detokenise(rows):
        return [" ".join(reverse.get(int(t), "oov") for t in row if t > 2)
                for row in rows]

    return {**reviews,
            "text_train": detokenise(reviews["x_train"]),
            "text_test": detokenise(reviews["x_test"]),
            "reverse": reverse}


def _keras_model(family: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((MAXLEN,))
    embedded = keras.layers.Embedding(VOCAB, WIDTH,
                                      mask_zero=family != "transformer block")(inputs)
    if family == "average embedding":
        x = keras.layers.GlobalAveragePooling1D()(embedded)
    elif family == "1D convolution":
        x = keras.layers.Conv1D(64, 5, padding="same",
                                activation="relu")(embedded)
        x = keras.layers.GlobalMaxPooling1D()(x)
    elif family == "LSTM":
        x = keras.layers.LSTM(WIDTH)(embedded)
    else:
        positions = keras.layers.Embedding(MAXLEN, WIDTH)(tf().range(MAXLEN))
        tokens = embedded + positions
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(tokens)
        attention = keras.layers.MultiHeadAttention(
            num_heads=2, key_dim=WIDTH // 2)(normed, normed)
        merged = keras.layers.Add()([tokens, attention])
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(merged)
        hidden = keras.layers.Dense(WIDTH * 2, activation="relu")(normed)
        merged = keras.layers.Add()([merged,
                                     keras.layers.Dense(WIDTH)(hidden)])
        x = keras.layers.GlobalAveragePooling1D()(merged)
    outputs = keras.layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


def _fit(family: str, size: int) -> dict:
    data = _data()
    if family == "TF-IDF + logistic":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        started = time.perf_counter()
        vectorizer = TfidfVectorizer(max_features=VOCAB, sublinear_tf=True)
        train = vectorizer.fit_transform(data["text_train"][:size])
        test = vectorizer.transform(data["text_test"])
        model = LogisticRegression(max_iter=2000).fit(train,
                                                      data["y_train"][:size])
        elapsed = time.perf_counter() - started
        probabilities = model.predict_proba(test)[:, 1]
        return {"accuracy": float(model.score(test, data["y_test"])),
                "params": int(train.shape[1] + 1), "seconds": elapsed,
                "probabilities": probabilities}
    model = _keras_model(family)
    started = time.perf_counter()
    history = model.fit(data["x_train"][:size], data["y_train"][:size],
                        epochs=EPOCHS, batch_size=64, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    elapsed = time.perf_counter() - started
    return {"accuracy": max(float(v) for v in history.history["val_accuracy"]),
            "params": int(model.count_params()), "seconds": elapsed,
            "probabilities": model.predict(data["x_test"],
                                           verbose=0).ravel()}


@functools.lru_cache(maxsize=1)
def _full_runs() -> dict:
    return {family: _fit(family, LIMIT) for family in FAMILIES}


@functools.lru_cache(maxsize=1)
def _scaling_runs() -> dict:
    return {(family, size): _fit(family, size)
            for size in SIZES
            for family in ("TF-IDF + logistic", "average embedding", "LSTM")}


def family_comparison(fig, axes, p: Palette) -> None:
    runs = _full_runs()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(FAMILIES, (p.amber, p.blue, p.purple, p.red, p.green)))
    accuracy = [runs[f]["accuracy"] for f in FAMILIES]
    best = max(accuracy)
    positions = np.arange(len(FAMILIES))
    left.barh(positions, accuracy, 0.55,
              color=[p.green if abs(v - best) < 1e-12 else colors[f]
                     for f, v in zip(FAMILIES, accuracy)])
    for y, (family, value) in enumerate(zip(FAMILIES, accuracy)):
        left.annotate(f"{value:.4f}   {runs[family]['params']:,} params",
                      (value, y), xytext=(6, 0), textcoords="offset points",
                      va="center", fontsize=8, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(FAMILIES, fontsize=8.5)
    left.invert_yaxis()
    left.set_xlim(0, 1.28)
    left.set_xlabel("test accuracy")
    left.set_title(f"IMDB, {LIMIT:,} reviews, {EPOCHS} epochs", fontsize=10)

    seconds = [runs[f]["seconds"] for f in FAMILIES]
    right.scatter(seconds, accuracy, s=90,
                  color=[colors[f] for f in FAMILIES], zorder=3)
    for family, x, y in zip(FAMILIES, seconds, accuracy):
        right.annotate(family, (x, y), xytext=(0, 9),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=colors[family])
    baseline = runs["TF-IDF + logistic"]["accuracy"]
    right.axhline(baseline, color=p.amber, lw=1.2, ls="--")
    right.annotate(f"bag-of-words baseline {baseline:.4f}",
                   (max(seconds) * 0.98, baseline), xytext=(0, -14),
                   textcoords="offset points", ha="right", fontsize=8,
                   color=p.amber)
    right.set_xscale("log")
    right.set_xlabel("seconds to train (log)")
    right.set_ylabel("test accuracy")
    right.set_title("accuracy against cost", fontsize=10)


def data_scaling(fig, axes, p: Palette) -> None:
    runs = _scaling_runs()
    ax = fig.subplots(1, 1)
    colors = {"TF-IDF + logistic": p.amber, "average embedding": p.blue,
              "LSTM": p.red}
    for family, color in colors.items():
        values = [runs[(family, size)]["accuracy"] for size in SIZES]
        ax.plot(SIZES, values, "o-", ms=6, lw=2.0, color=color, label=family)
        for size, value in zip(SIZES, values):
            ax.annotate(f"{value:.4f}", (size, value),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=7.5, color=color)
    ax.set_xscale("log")
    ax.minorticks_off()
    ax.set_xticks(list(SIZES))
    ax.set_xticklabels([f"{s:,}" for s in SIZES])
    ax.set_xlabel("training reviews")
    ax.set_ylabel("test accuracy")
    ax.set_title("which family wins depends on how much data there is",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower right")


def errors(fig, axes, p: Palette) -> None:
    runs = _full_runs()
    data = _data()
    left, right = fig.subplots(1, 2)
    truth = data["y_test"]
    # Compare the baseline against the best *neural* family: TF-IDF happens to
    # win outright here, so comparing the overall best against the baseline
    # would compare the baseline with itself.
    best_family = max((f for f in FAMILIES if f != "TF-IDF + logistic"),
                      key=lambda f: runs[f]["accuracy"])
    baseline = runs["TF-IDF + logistic"]["probabilities"] > 0.5
    winner = runs[best_family]["probabilities"] > 0.5
    both_right = int(((baseline == truth) & (winner == truth)).sum())
    only_baseline = int(((baseline == truth) & (winner != truth)).sum())
    only_winner = int(((baseline != truth) & (winner == truth)).sum())
    both_wrong = int(((baseline != truth) & (winner != truth)).sum())
    labels = ("both right", f"only {best_family}", "only bag of words",
              "both wrong")
    values = (both_right, only_winner, only_baseline, both_wrong)
    positions = np.arange(len(labels))
    left.bar(positions, values, 0.55, color=(p.green, p.blue, p.amber, p.red))
    for x, value in zip(positions, values):
        left.annotate(f"{value:,}\n{value / len(truth):.1%}", (x, value),
                      textcoords="offset points", xytext=(0, 4), ha="center",
                      fontsize=8, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([label.replace(" ", "\n") for label in labels],
                         fontsize=8)
    left.set_ylim(0, max(values) * 1.25)
    left.set_ylabel("test reviews")
    left.set_title(f"where the two models disagree ({len(truth):,} reviews)",
                   fontsize=10)

    confidence = runs["TF-IDF + logistic"]["probabilities"]
    correct = (confidence > 0.5) == truth
    bins = np.linspace(0, 1, 11)
    centres, accuracies, counts = [], [], []
    for low, high in zip(bins, bins[1:]):
        mask = (confidence >= low) & (confidence < high)
        if mask.sum() > 5:
            centres.append((low + high) / 2)
            accuracies.append(float(correct[mask].mean()))
            counts.append(int(mask.sum()))
    right.plot([0, 1], [0, 1], lw=1.2, ls="--", color=p.muted,
               label="perfect calibration")
    right.plot(centres, [a if c > 0.5 else 1 - a
                         for a, c in zip(accuracies, centres)], "o-", ms=6,
               lw=2.0, color=p.green, label="TF-IDF + logistic")
    for x, value, count in zip(centres, accuracies, counts):
        del value
        right.annotate(f"{count}", (x, x), textcoords="offset points",
                       xytext=(0, -12), ha="center", fontsize=6.5,
                       color=p.muted)
    right.set_xlabel("predicted probability of positive")
    right.set_ylabel("observed rate of positive")
    right.set_title("is the confidence meaningful?", fontsize=10)
    right.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("family-comparison", family_comparison, size=(9.6, 3.7),
           axes=False),
    figure("data-scaling", data_scaling, size=(7.8, 3.8), axes=False),
    figure("errors", errors, size=(9.4, 3.6), axes=False),
]


if __name__ == "__main__":
    data = _data()
    runs = _full_runs()
    print(f"=== IMDB, {LIMIT:,} train / {len(data['y_test']):,} test, "
          f"vocabulary {VOCAB:,}, {MAXLEN} tokens ===")
    print(f"{'family':22s} {'parameters':>12} {'accuracy':>9} {'seconds':>9} "
          f"{'vs baseline':>12}")
    baseline = runs["TF-IDF + logistic"]["accuracy"]
    for family in FAMILIES:
        run = runs[family]
        print(f"{family:22s} {run['params']:12,} {run['accuracy']:9.4f} "
              f"{run['seconds']:9.1f} {run['accuracy'] - baseline:+12.4f}")

    print(f"\n=== against training-set size ===")
    scaling = _scaling_runs()
    print(f"{'rows':>7} " + " ".join(f"{f:>20}" for f in
                                     ("TF-IDF + logistic", "average embedding",
                                      "LSTM")))
    for size in SIZES:
        row = [scaling[(f, size)]["accuracy"] for f in
               ("TF-IDF + logistic", "average embedding", "LSTM")]
        print(f"{size:7,} " + " ".join(f"{v:20.4f}" for v in row))

    truth = data["y_test"]
    best_family = max((f for f in FAMILIES if f != "TF-IDF + logistic"),
                      key=lambda f: runs[f]["accuracy"])
    baseline_correct = (runs["TF-IDF + logistic"]["probabilities"] > 0.5) == truth
    winner_correct = (runs[best_family]["probabilities"] > 0.5) == truth
    print(f"\n=== {best_family} against the bag-of-words baseline ===")
    print(f"both right          "
          f"{int((baseline_correct & winner_correct).sum()):6,}")
    print(f"only {best_family:16s} "
          f"{int((~baseline_correct & winner_correct).sum()):6,}")
    print(f"only bag of words   "
          f"{int((baseline_correct & ~winner_correct).sum()):6,}")
    print(f"both wrong          "
          f"{int((~baseline_correct & ~winner_correct).sum()):6,}")
    print("the disagreement is the interesting part: a model that only wins by")
    print("0.01 overall may still be right about a very different 1%")

    confidence = runs["TF-IDF + logistic"]["probabilities"]
    print(f"\n=== is the confidence meaningful? (TF-IDF + logistic) ===")
    print(f"{'predicted band':>16} {'reviews':>8} {'observed positive rate':>23}")
    bins = np.linspace(0, 1, 6)
    for low, high in zip(bins, bins[1:]):
        mask = (confidence >= low) & (confidence < high)
        if mask.sum() > 5:
            print(f"{f'{low:.1f}-{high:.1f}':>16} {int(mask.sum()):8,} "
                  f"{float(truth[mask].mean()):23.4f}")
    print("a well-calibrated model's 0.8-1.0 band should be about 90% positive")

"""Shared helpers for Deep Learning figure modules.

Everything here exists so a page figure can be *measured* rather than sketched,
and so the same measurement is reproducible on a laptop CPU:

* :func:`seed_everything` pins Python, NumPy and TensorFlow randomness.
* :func:`dataset` loads a Keras dataset once per process and caches it, with a
  ``limit`` so figures stay in the seconds-not-minutes range.
* :func:`train` fits a model and returns its history as plain lists, so figure
  modules never hold a live TensorFlow object.
* :func:`repeat` runs a training function over several seeds and returns the
  mean and spread, because a single deep-learning run is a draw from a
  distribution and the figures should say so.

CPU timings on the reference machine (TF 2.21, no GPU): a 64-unit MLP over
10,000 MNIST rows for 3 epochs takes about 1.2s, and a 16-filter CNN over 6,000
rows for 2 epochs about the same. Budget figure modules accordingly — anything
that needs minutes belongs in a page's prose as a reported number, not in the
build.
"""

from __future__ import annotations

import functools
import os
import random
from typing import Callable, Iterable, Sequence

import numpy as np

# Keep TensorFlow quiet and deterministic before it is imported anywhere.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")


def tf():
    """Import TensorFlow lazily, so numpy-only figures stay fast."""
    import tensorflow as tensorflow_module

    return tensorflow_module


def seed_everything(seed: int = 0) -> None:
    """Pin every source of randomness a figure can reach."""
    random.seed(seed)
    np.random.seed(seed)
    tf().keras.utils.set_random_seed(seed)


# --------------------------------------------------------------------------- #
# Datasets — small, cached, and always returned in the same shape.
# --------------------------------------------------------------------------- #

@functools.lru_cache(maxsize=8)
def dataset(name: str = "mnist", limit: int = 10000, flat: bool = True) -> dict:
    """Return a dict with x_train / y_train / x_test / y_test, scaled to [0, 1].

    ``limit`` caps the training rows so a figure stays cheap; the test split is
    capped at a quarter of that. ``flat`` reshapes images to vectors for MLPs.
    """
    loaders = {
        "mnist": lambda: tf().keras.datasets.mnist.load_data(),
        "fashion": lambda: tf().keras.datasets.fashion_mnist.load_data(),
        "cifar10": lambda: tf().keras.datasets.cifar10.load_data(),
    }
    if name not in loaders:
        raise ValueError(f"unknown dataset {name!r}; try {sorted(loaders)}")
    (x_train, y_train), (x_test, y_test) = loaders[name]()

    x_train = np.asarray(x_train[:limit], dtype="float32") / 255.0
    y_train = np.asarray(y_train[:limit]).reshape(-1)
    x_test = np.asarray(x_test[: max(1, limit // 4)], dtype="float32") / 255.0
    y_test = np.asarray(y_test[: max(1, limit // 4)]).reshape(-1)

    if flat:
        x_train = x_train.reshape(len(x_train), -1)
        x_test = x_test.reshape(len(x_test), -1)
    elif x_train.ndim == 3:                       # grayscale needs a channel axis
        x_train = x_train[..., None]
        x_test = x_test[..., None]

    return {"x_train": x_train, "y_train": y_train,
            "x_test": x_test, "y_test": y_test,
            "classes": int(y_train.max()) + 1}


@functools.lru_cache(maxsize=8)
def imdb(vocab: int = 10000, maxlen: int = 200, limit: int = 5000,
         truncating: str = "pre") -> dict:
    """Padded IMDB reviews plus their true lengths, from the local cache.

    Token ids, not pixels, so nothing is divided by 255. ``lengths`` is kept
    because every masking question on the sequence pages is really a question
    about the difference between ``maxlen`` and the true length.
    """
    keras = tf().keras
    (x_train, y_train), (x_test, y_test) = keras.datasets.imdb.load_data(
        num_words=vocab)
    x_train, y_train = x_train[:limit], y_train[:limit]
    test_rows = max(1, limit // 2)
    x_test, y_test = x_test[:test_rows], y_test[:test_rows]
    lengths = np.array([len(row) for row in x_train])
    pad = keras.preprocessing.sequence.pad_sequences
    return {
        "x_train": pad(x_train, maxlen=maxlen, truncating=truncating),
        "y_train": np.asarray(y_train).astype("int32"),
        "x_test": pad(x_test, maxlen=maxlen, truncating=truncating),
        "y_test": np.asarray(y_test).astype("int32"),
        "lengths": lengths,
        "test_lengths": np.array([len(row) for row in x_test]),
        "vocab": vocab,
        "maxlen": maxlen,
    }


@functools.lru_cache(maxsize=4)
def text_corpus(reviews: int = 3000, vocab: int = 20000) -> dict:
    """Plain English text, rebuilt from the cached IMDB token ids.

    There is no prose file in this repo and nothing may be downloaded, so the
    character-level pages get their corpus by decoding IMDB reviews through
    Keras's word index. The result is real English with real spelling, which is
    what a character model needs; it is not punctuated the way the original
    reviews were, because the tokeniser threw that away before caching.

    Returns the joined text, the character vocabulary, and the word list — the
    word list is the honest way to score a generated sample, since "is this a
    dictionary word" beats eyeballing the output.
    """
    keras = tf().keras
    index = keras.datasets.imdb.get_word_index()
    # Keras reserves 0-2 for padding / start / unknown, so ids are offset by 3.
    words = {number + 3: word for word, number in index.items()
             if number + 3 < vocab}
    (x_train, _), _ = keras.datasets.imdb.load_data(num_words=vocab)
    lines = []
    for row in x_train[:reviews]:
        line = " ".join(words[token] for token in row if token in words)
        if line:
            lines.append(line)
    text = "\n".join(lines)
    return {"text": text,
            "chars": sorted(set(text)),
            "words": frozenset(words.values()),
            "reviews": len(lines)}


def waves(rows: int = 4000, timesteps: int = 60, horizon: int = 1,
          noise: float = 0.1, seed: int = 0,
          trend: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """A windowed univariate series with two periods, drift and noise.

    Generated rather than downloaded so the signal is known exactly: any
    forecasting error a page reports can be compared against the noise floor,
    which is the only way to tell a good model from an easy series.
    """
    rng = np.random.default_rng(seed)
    total = rows + timesteps + horizon
    time = np.arange(total, dtype="float32")
    series = (np.sin(2 * np.pi * time / 24.0)
              + 0.5 * np.sin(2 * np.pi * time / 7.0 + 0.7)
              + trend * time / total
              + rng.normal(0.0, noise, total).astype("float32"))
    windows = np.stack([series[i:i + timesteps] for i in range(rows)])
    targets = series[timesteps + horizon - 1: timesteps + horizon - 1 + rows]
    return windows[..., None].astype("float32"), targets.astype("float32")


def spiral(n_per_class: int = 200, classes: int = 3, noise: float = 0.25,
           seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """The two-dimensional spiral that no linear model can separate.

    Small, instantly available and impossible for a perceptron, which makes it
    the honest illustration for "why depth" and for decision-boundary sketches.
    """
    rng = np.random.default_rng(seed)
    xs, ys = [], []
    for label in range(classes):
        radius = np.linspace(0.05, 1.0, n_per_class)
        theta = (np.linspace(label * 2 * np.pi / classes,
                             label * 2 * np.pi / classes + 3.2, n_per_class)
                 + rng.normal(0, noise, n_per_class))
        xs.append(np.c_[radius * np.sin(theta), radius * np.cos(theta)])
        ys.append(np.full(n_per_class, label))
    return (np.concatenate(xs).astype("float32"),
            np.concatenate(ys).astype("int64"))


# --------------------------------------------------------------------------- #
# Training — always returns plain Python, never a live model.
# --------------------------------------------------------------------------- #

def mlp(units: Sequence[int], inputs: int, outputs: int, activation: str = "relu",
        dropout: float = 0.0, normalise: bool = False, seed: int = 0):
    """A plain feed-forward classifier, built the same way every time."""
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((inputs,))]
    for width in units:
        layers.append(keras.layers.Dense(width, activation=None))
        if normalise:
            layers.append(keras.layers.BatchNormalization())
        layers.append(keras.layers.Activation(activation))
        if dropout:
            layers.append(keras.layers.Dropout(dropout))
    layers.append(keras.layers.Dense(outputs, activation="softmax"))
    return keras.Sequential(layers)


def train(model, data: dict, epochs: int = 5, batch_size: int = 128,
          optimizer: str = "adam", validation: bool = True) -> dict:
    """Fit ``model`` and return its history as lists of floats."""
    model.compile(optimizer=optimizer,
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    history = model.fit(
        data["x_train"], data["y_train"],
        epochs=epochs, batch_size=batch_size, verbose=0,
        validation_data=(data["x_test"], data["y_test"]) if validation else None,
    )
    out = {key: [float(v) for v in values] for key, values in history.history.items()}
    out["params"] = int(model.count_params())
    return out


def repeat(run: Callable[[int], float], seeds: Iterable[int] = range(5)) -> dict:
    """Run ``run(seed)`` over several seeds; report mean, sd and range.

    Deep-learning numbers move with the seed. Any figure that compares two
    configurations should compare distributions, not single runs.
    """
    values = [float(run(seed)) for seed in seeds]
    array = np.asarray(values)
    return {"values": values, "mean": float(array.mean()),
            "sd": float(array.std(ddof=1)) if len(values) > 1 else 0.0,
            "min": float(array.min()), "max": float(array.max())}


# --------------------------------------------------------------------------- #
# From-scratch pieces, so pages can derive before they import.
# --------------------------------------------------------------------------- #

def softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = z - z.max(axis=axis, keepdims=True)
    exponent = np.exp(shifted)
    return exponent / exponent.sum(axis=axis, keepdims=True)


def cross_entropy(probabilities: np.ndarray, labels: np.ndarray) -> float:
    rows = np.arange(len(labels))
    return float(-np.log(np.clip(probabilities[rows, labels], 1e-12, None)).mean())


def numeric_gradient(function: Callable[[np.ndarray], float], point: np.ndarray,
                     step: float = 1e-5) -> np.ndarray:
    """Central-difference gradient — the reference every analytic gradient is checked against."""
    point = np.asarray(point, dtype="float64")
    out = np.zeros_like(point)
    for index in np.ndindex(point.shape):
        forward, backward = point.copy(), point.copy()
        forward[index] += step
        backward[index] -= step
        out[index] = (function(forward) - function(backward)) / (2 * step)
    return out

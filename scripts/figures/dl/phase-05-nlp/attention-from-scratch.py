"""Figures for *Attention from Scratch (Queries, Keys and Values)*.

Scaled dot-product attention is about six lines of NumPy, and this module
checks those six lines against `keras.layers.MultiHeadAttention` rather than
asserting they match. Everything except the one training run is arithmetic, so
the module is fast.

``scaling-and-softmax``
    Why the 1/sqrt(d_k) is there, measured: attention entropy and maximum
    weight against dimension, with and without the scale.

``masks``
    The causal mask and the padding mask as pictures, plus the number that
    matters — what fraction of the attention budget a padding mask reclaims.

``learned-attention``
    A small model trained on a task that needs one specific token, and where
    its attention actually goes.
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

DIMENSIONS = (4, 16, 64, 256)
TOKENS = 12
TRIALS = 200
# The retrieval task: a sequence of (key, value) pairs and one query token.
ROWS = 4000
LENGTH = 16
SYMBOLS = 8
EPOCHS = 30
WIDTH = 32
HEADS = 2


def softmax(z, axis=-1):
    shifted = z - z.max(axis=axis, keepdims=True)
    exponent = np.exp(shifted)
    return exponent / exponent.sum(axis=axis, keepdims=True)


def attention(query, key, value, scale=True, mask=None):
    """Scaled dot-product attention — the whole thing."""
    scores = query @ key.T
    if scale:
        scores = scores / np.sqrt(query.shape[-1])
    if mask is not None:
        scores = np.where(mask, scores, -1e9)
    weights = softmax(scores, axis=-1)
    return weights @ value, weights


@functools.lru_cache(maxsize=1)
def _scaling() -> dict:
    """How peaked the softmax gets with and without the 1/sqrt(d) scale."""
    rng = np.random.default_rng(0)
    out = {}
    for dimension in DIMENSIONS:
        for scale in (False, True):
            maxima, entropies = [], []
            for _ in range(TRIALS):
                query = rng.standard_normal((1, dimension))
                key = rng.standard_normal((TOKENS, dimension))
                _, weights = attention(query, key, key, scale=scale)
                row = weights[0]
                maxima.append(float(row.max()))
                entropies.append(float(-(row * np.log(row + 1e-12)).sum()))
            out[(dimension, scale)] = {
                "max": float(np.mean(maxima)),
                "entropy": float(np.mean(entropies)),
                "score_sd": float(np.std(
                    (rng.standard_normal((TOKENS, dimension))
                     @ rng.standard_normal(dimension))
                    / (np.sqrt(dimension) if scale else 1.0))),
            }
    return out


def scaling_and_softmax(fig, axes, p: Palette) -> None:
    runs = _scaling()
    left, right = fig.subplots(1, 2)
    uniform = 1.0 / TOKENS
    for scale, label, color in ((False, "no scaling", p.red),
                                (True, "1/sqrt(d_k)", p.green)):
        values = [runs[(d, scale)]["max"] for d in DIMENSIONS]
        left.plot(DIMENSIONS, values, "o-", ms=6, lw=2.0, color=color,
                  label=label)
        for dimension, value in zip(DIMENSIONS, values):
            left.annotate(f"{value:.3f}", (dimension, value),
                          textcoords="offset points", xytext=(0, 8),
                          ha="center", fontsize=7.5, color=color)
    left.axhline(uniform, color=p.muted, lw=1.2, ls="--")
    left.annotate(f"uniform = {uniform:.4f}", (DIMENSIONS[0], uniform + 0.03),
                  fontsize=8, color=p.muted)
    left.set_xscale("log")
    left.set_xticks(list(DIMENSIONS))
    left.set_xticklabels([str(d) for d in DIMENSIONS])
    left.set_xlabel("key dimension d_k")
    left.set_ylabel(f"mean largest attention weight ({TOKENS} tokens)")
    left.set_title("without the scale, attention collapses onto one token",
                   fontsize=10)
    left.legend(fontsize=8, loc="center right")

    for scale, label, color in ((False, "no scaling", p.red),
                                (True, "1/sqrt(d_k)", p.green)):
        values = [runs[(d, scale)]["entropy"] for d in DIMENSIONS]
        right.plot(DIMENSIONS, values, "o-", ms=6, lw=2.0, color=color,
                   label=label)
    right.axhline(np.log(TOKENS), color=p.muted, lw=1.2, ls="--")
    right.annotate(f"uniform = log {TOKENS} = {np.log(TOKENS):.3f}",
                   (DIMENSIONS[0], np.log(TOKENS) - 0.18), fontsize=8,
                   color=p.muted)
    right.set_xscale("log")
    right.set_xticks(list(DIMENSIONS))
    right.set_xticklabels([str(d) for d in DIMENSIONS])
    right.set_xlabel("key dimension d_k")
    right.set_ylabel("mean attention entropy (nats)")
    right.set_title("the same fact as entropy", fontsize=10)
    right.legend(fontsize=8, loc="lower left")


def masks(fig, axes, p: Palette) -> None:
    grid = fig.subplots(1, 3)
    size = 10
    causal = np.tril(np.ones((size, size), dtype=bool))
    lengths = np.array([10, 7, 4])
    padding = np.zeros((size, size), dtype=bool)
    padding[:, :6] = True
    both = causal & padding

    for ax, (title, mask) in zip(grid, (("causal mask", causal),
                                        ("padding mask (6 real tokens)",
                                         padding),
                                        ("both", both))):
        ax.imshow(mask.astype(float), cmap="Greens", vmin=0, vmax=1.4)
        ax.set_xlabel("key position")
        ax.set_ylabel("query position")
        ax.set_title(f"{title}\n{mask.mean():.2f} of pairs allowed",
                     fontsize=9.5)
        ax.set_xticks(range(0, size, 3))
        ax.set_yticks(range(0, size, 3))
        ax.grid(False)
    del lengths


def _rows(rows: int, seed: int):
    """A cue symbol appears once; the answer is the token *after* it.

    The same cue symbol is repeated at the last position as the query. To
    answer, a model has to match the query against the earlier cue and then
    read the position one to its right — which is exactly the two-step
    "induction head" pattern, and is why one attention layer is not enough.
    """
    generator = np.random.default_rng(seed)
    x = generator.integers(1, SYMBOLS, (rows, LENGTH))
    targets = np.zeros(rows, "int32")
    positions = np.zeros(rows, "int32")
    for row in range(rows):
        cue = int(generator.integers(0, LENGTH - 3))
        x[row, cue] = SYMBOLS                      # a symbol reserved for the cue
        targets[row] = x[row, cue + 1]
        positions[row] = cue
        x[row, -1] = SYMBOLS                       # the query, repeated at the end
    return x, targets, positions


def _build(blocks: int):
    keras = tf().keras
    seed_everything(0)
    inputs = keras.layers.Input((LENGTH,))
    embedded = keras.layers.Embedding(SYMBOLS + 1, WIDTH)(inputs)
    order = keras.layers.Embedding(LENGTH, WIDTH)(tf().range(LENGTH))
    x = embedded + order
    layers = []
    for _ in range(blocks):
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(x)
        layer = keras.layers.MultiHeadAttention(num_heads=HEADS,
                                                key_dim=WIDTH // HEADS)
        x = keras.layers.Add()([x, layer(normed, normed)])
        normed = keras.layers.LayerNormalization(epsilon=1e-6)(x)
        hidden = keras.layers.Dense(WIDTH * 2, activation="relu")(normed)
        x = keras.layers.Add()([x, keras.layers.Dense(WIDTH)(hidden)])
        layers.append(layer)
    last = keras.layers.Lambda(lambda t: t[:, -1, :])(x)
    outputs = keras.layers.Dense(SYMBOLS + 1, activation="softmax")(last)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(3e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model, layers


@functools.lru_cache(maxsize=1)
def _retrieval() -> dict:
    """One attention block against two, on the induction task."""
    keras = tf().keras
    x_train, y_train, _ = _rows(ROWS, 0)
    x_test, y_test, positions = _rows(1000, 1)
    out = {"chance": 1.0 / (SYMBOLS - 1), "uniform": 1.0 / LENGTH,
           "positions": positions[:200]}
    for blocks in (1, 2):
        model, layers = _build(blocks)
        history = model.fit(x_train, y_train, epochs=EPOCHS, batch_size=64,
                            verbose=0, validation_data=(x_test, y_test))
        out[blocks] = {
            "accuracy": max(float(v) for v in history.history["val_accuracy"]),
            "curve": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
        }
        if blocks == 2:
            feeder = keras.Model(model.inputs, layers[-1].input[0])
            hidden = feeder.predict(x_test[:200], verbose=0)
            _, scores = layers[-1](hidden, hidden,
                                   return_attention_scores=True)
            last_row = scores.numpy()[:, :, -1, :]       # (rows, heads, keys)
            wanted = positions[:200] + 1
            out["scores"] = last_row
            out["on_target"] = np.array([last_row[row, :, wanted[row]]
                                         for row in range(len(wanted))])
    return out


def learned_attention(fig, axes, p: Palette) -> None:
    info = _retrieval()
    left, right = fig.subplots(1, 2)
    for blocks, color in ((1, p.red), (2, p.green)):
        run = info[blocks]
        left.plot(range(1, len(run["curve"]) + 1), run["curve"], lw=2.0,
                  color=color,
                  label=f"{blocks} block{'s' if blocks > 1 else ''} — best "
                        f"{run['accuracy']:.4f}, {run['params']:,} params")
    left.axhline(info["chance"], color=p.muted, lw=1.2, ls="--",
                 label=f"chance {info['chance']:.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_title("match the cue, then read the next token", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    # Attention from the query position, aligned so 0 = the answer position.
    offsets = np.arange(-4, 5)
    aligned = np.zeros((info["scores"].shape[1], len(offsets)))
    for head in range(info["scores"].shape[1]):
        for index, offset in enumerate(offsets):
            values = []
            for row, position in enumerate(info["positions"]):
                target = position + 1 + offset
                if 0 <= target < LENGTH:
                    values.append(info["scores"][row, head, target])
            aligned[head, index] = float(np.mean(values))
    for head in range(aligned.shape[0]):
        right.plot(offsets, aligned[head], "o-", ms=5, lw=1.8,
                   label=f"head {head}")
    right.axhline(info["uniform"], color=p.muted, lw=1.2, ls="--",
                  label=f"uniform {info['uniform']:.4f}")
    right.axvline(0, color=p.amber, lw=1.2, ls=":")
    right.annotate("the answer", (0, aligned.max() * 0.92),
                   xytext=(6, 0), textcoords="offset points", fontsize=8.5,
                   color=p.amber)
    right.set_xlabel("offset from the answer position")
    right.set_ylabel("mean attention weight from the query")
    right.set_title("second block: where the query token looks", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


FIGURES = [
    figure("scaling-and-softmax", scaling_and_softmax, size=(9.4, 3.5),
           axes=False),
    figure("masks", masks, size=(9.6, 3.2), axes=False),
    figure("learned-attention", learned_attention, size=(9.4, 3.5),
           axes=False),
]


if __name__ == "__main__":
    keras = tf().keras
    print("=== NumPy attention against keras.layers.MultiHeadAttention ===")
    seed_everything(0)
    tokens = np.random.default_rng(0).standard_normal(
        (1, 6, 16)).astype("float32")
    layer = keras.layers.MultiHeadAttention(num_heads=1, key_dim=16)
    keras_output, keras_scores = layer(tokens, tokens,
                                       return_attention_scores=True)
    weights = {w.path.split("/")[-2]: w.numpy() for w in layer.weights}
    query_kernel = layer._query_dense.kernel.numpy()
    key_kernel = layer._key_dense.kernel.numpy()
    value_kernel = layer._value_dense.kernel.numpy()
    output_kernel = layer._output_dense.kernel.numpy()
    query_bias = layer._query_dense.bias.numpy()
    key_bias = layer._key_dense.bias.numpy()
    value_bias = layer._value_dense.bias.numpy()
    output_bias = layer._output_dense.bias.numpy()
    x = tokens[0]
    q = np.einsum("td,dhk->thk", x, query_kernel) + query_bias
    k = np.einsum("td,dhk->thk", x, key_kernel) + key_bias
    v = np.einsum("td,dhk->thk", x, value_kernel) + value_bias
    scores = np.einsum("qhk,shk->hqs", q, k) / np.sqrt(q.shape[-1])
    attention_weights = softmax(scores, axis=-1)
    context = np.einsum("hqs,shk->qhk", attention_weights, v)
    mine = np.einsum("qhk,hkd->qd", context, output_kernel) + output_bias
    print(f"output difference   {np.abs(mine - keras_output.numpy()[0]).max():.2e}")
    print(f"weights difference  "
          f"{np.abs(attention_weights - keras_scores.numpy()[0]).max():.2e}")
    del weights

    print(f"\n=== why 1/sqrt(d_k), over {TRIALS} random draws, "
          f"{TOKENS} tokens ===")
    runs = _scaling()
    print(f"{'d_k':>5} {'max weight (raw)':>17} {'max weight (scaled)':>20} "
          f"{'entropy (raw)':>14} {'entropy (scaled)':>17}")
    for dimension in DIMENSIONS:
        raw = runs[(dimension, False)]
        scaled = runs[(dimension, True)]
        print(f"{dimension:5d} {raw['max']:17.4f} {scaled['max']:20.4f} "
              f"{raw['entropy']:14.4f} {scaled['entropy']:17.4f}")
    print(f"uniform attention over {TOKENS} tokens is "
          f"{1 / TOKENS:.4f}, entropy log {TOKENS} = {np.log(TOKENS):.4f}")
    print("the dot product of two d-dimensional unit-variance vectors has")
    print("variance d, so without the scale the softmax saturates as d grows")

    print("\n=== masks ===")
    size = 10
    causal = np.tril(np.ones((size, size), dtype=bool))
    padding = np.zeros((size, size), dtype=bool)
    padding[:, :6] = True
    print(f"causal mask allows {causal.mean():.4f} of query-key pairs")
    print(f"padding mask (6 of 10 real) allows {padding.mean():.4f}")
    print(f"both together allow {(causal & padding).mean():.4f}")
    scores = np.zeros((1, size))
    masked = np.where(padding[0], scores, -1e9)
    print(f"a masked softmax puts {softmax(masked)[0][6:].sum():.2e} of its "
          f"weight on the padded positions")

    print("\n=== the induction task: match the cue, read the next token ===")
    info = _retrieval()
    print(f"chance is {info['chance']:.4f} over {SYMBOLS - 1} answers")
    print(f"{'blocks':>7} {'params':>9} {'best val accuracy':>18}")
    for blocks in (1, 2):
        run = info[blocks]
        print(f"{blocks:7d} {run['params']:9,} {run['accuracy']:18.4f}")
    print("one attention layer can match the cue OR shift by one position, not")
    print("both: the second block is what turns a match into a lookup")
    print(f"\nsecond block, attention on the answer position "
          f"(uniform would be {info['uniform']:.4f}):")
    for head in range(info["on_target"].shape[1]):
        column = info["on_target"][:, head]
        print(f"  head {head}: mean {column.mean():.4f}  "
              f"median {np.median(column):.4f}  "
              f"{float((column > 0.5).mean()):.4f} of rows above 0.5")

"""Figures for *Intro to Recurrent Neural Networks (RNN) for Sequences*.

``unrolled-state``
    One SimpleRNN cell's hidden state, unrolled over a real review, so
    "the state carries information forward" is a picture rather than a claim.

``order-matters``
    The same reviews with their word order destroyed. A bag-of-words model
    cannot tell the difference; a recurrent one can, and the gap is the whole
    reason the layer exists.

``memory-length``
    How far back a SimpleRNN can actually see, measured on the adding problem
    at four sequence lengths against a do-nothing baseline.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import imdb, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

VOCAB = 10000
MAXLEN = 200
LIMIT = 5000
EPOCHS = 5
UNITS = 32
BATCH = 64
# The adding problem: two marked values in a sequence of this length.
DISTANCES = (10, 40, 100, 200)
COPY_ROWS = 3000
# The adding problem needs a real budget: at 20 epochs and 16 units every cell
# sat at the do-nothing baseline, which measures the budget, not recurrence.
COPY_EPOCHS = 60
COPY_UNITS = 32


@functools.lru_cache(maxsize=1)
def _reviews() -> dict:
    return imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)


def _recurrent(kind: str = "rnn", units: int | None = None, seed: int = 0):
    # Read UNITS at call time, not as a default argument: a default is bound
    # when the function is defined, so smoke.py's shrunk constant would be
    # ignored and the trace model would not match the trained one.
    units = UNITS if units is None else units
    keras = tf().keras
    seed_everything(seed)
    layer = {"rnn": keras.layers.SimpleRNN,
             "lstm": keras.layers.LSTM,
             "gru": keras.layers.GRU}[kind]
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, 32),
        layer(units),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _state_trace() -> dict:
    """Run one review through the cell and keep every hidden state."""
    keras = tf().keras
    data = _reviews()
    model = _recurrent("rnn")
    model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
              batch_size=BATCH, verbose=0)
    # The trained layer only returns its final state, so rebuild the same cell
    # with return_sequences=True and copy the weights across.
    units = int(model.layers[1].units)
    tracer = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, 32),
        keras.layers.SimpleRNN(units, return_sequences=True),
    ])
    tracer.layers[0].set_weights(model.layers[0].get_weights())
    tracer.layers[1].set_weights(model.layers[1].get_weights())
    row = int(np.argmax(data["test_lengths"] < MAXLEN))
    states = tracer.predict(data["x_test"][row:row + 1], verbose=0)[0]
    padding = MAXLEN - int(data["test_lengths"][row])
    return {"states": states, "padding": max(padding, 0),
            "label": int(data["y_test"][row]), "units": units,
            "length": int(data["test_lengths"][row])}


def unrolled_state(fig, axes, p: Palette) -> None:
    trace = _state_trace()
    states = trace["states"]
    top, bottom = fig.subplots(2, 1, height_ratios=(2.0, 1.0))
    image = top.imshow(states.T, aspect="auto", cmap="RdBu_r",
                       vmin=-1, vmax=1, interpolation="nearest")
    top.set_ylabel("hidden unit")
    top.set_title(f"every hidden state of one {trace['units']}-unit SimpleRNN "
                  f"over {MAXLEN} timesteps", fontsize=10)
    top.grid(False)
    fig.colorbar(image, ax=top, pad=0.01, fraction=0.03)
    if trace["padding"]:
        top.axvline(trace["padding"], color=p.fg, lw=1.2, ls="--")
        top.annotate("padding ends", (trace["padding"], 2),
                     xytext=(6, 0), textcoords="offset points",
                     fontsize=8, color=p.fg)
    bottom.plot(np.abs(states).mean(axis=1), lw=1.8, color=p.blue)
    bottom.set_xlabel("timestep")
    bottom.set_ylabel("mean |state|")
    padding = trace["padding"]
    if padding:
        during = float(np.abs(states[:padding]).mean())
        after = float(np.abs(states[padding:]).mean())
        bottom.set_title(f"the padded steps are not idle: mean |state| "
                         f"{during:.4f} over the padding against {after:.4f} "
                         f"over the text", fontsize=9.5)
    else:
        bottom.set_title("mean |state| per timestep", fontsize=9.5)


@functools.lru_cache(maxsize=1)
def _order_runs() -> dict:
    keras = tf().keras
    data = _reviews()
    rng = np.random.default_rng(0)
    shuffled_train = np.stack([rng.permutation(row) for row in data["x_train"]])
    shuffled_test = np.stack([rng.permutation(row) for row in data["x_test"]])
    out = {}

    for label, x_train, x_test in (("in order", data["x_train"], data["x_test"]),
                                   ("shuffled", shuffled_train, shuffled_test)):
        model = _recurrent("rnn")
        history = model.fit(x_train, data["y_train"], epochs=EPOCHS,
                            batch_size=BATCH, verbose=0,
                            validation_data=(x_test, data["y_test"]))
        out[("SimpleRNN", label)] = [float(v)
                                     for v in history.history["val_accuracy"]]

        seed_everything(0)
        bag = keras.Sequential([
            keras.layers.Input((MAXLEN,)),
            keras.layers.Embedding(VOCAB, 32),
            keras.layers.GlobalAveragePooling1D(),
            keras.layers.Dense(1, activation="sigmoid"),
        ])
        bag.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                    metrics=["accuracy"])
        history = bag.fit(x_train, data["y_train"], epochs=EPOCHS,
                          batch_size=BATCH, verbose=0,
                          validation_data=(x_test, data["y_test"]))
        out[("bag of words", label)] = [float(v)
                                        for v in history.history["val_accuracy"]]
    return out


def order_matters(fig, axes, p: Palette) -> None:
    runs = _order_runs()
    ax = fig.subplots(1, 1)
    models = ("bag of words", "SimpleRNN")
    orders = ("in order", "shuffled")
    positions = np.arange(len(models))
    colors = {"in order": p.green, "shuffled": p.red}
    for offset, order in zip((-0.19, 0.19), orders):
        values = [max(runs[(m, order)]) for m in models]
        ax.bar(positions + offset, values, 0.36, color=colors[order],
               label=order)
        for x, value in zip(positions + offset, values):
            ax.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    for index, model in enumerate(models):
        best = max(runs[(model, "in order")])
        drop = best - max(runs[(model, "shuffled")])
        # Above the bars: at 0.05 the label sat inside them and was unreadable.
        ax.annotate(f"order is worth {drop:+.4f}", (index, best + 0.07),
                    ha="center", fontsize=8.5, color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("best validation accuracy")
    ax.set_title(f"IMDB, {LIMIT:,} reviews, {MAXLEN} tokens, {EPOCHS} epochs",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="upper left")


def _adding_task(length: int, rows: int = COPY_ROWS, seed: int = 0):
    """The classic adding problem: two marked values in a long sequence.

    Channel 0 carries a uniform value, channel 1 is a marker that is 1 at
    exactly two positions — one near the start, one in the second half. The
    target is the sum of the two marked values, so the network has to carry a
    number across the whole sequence *and* ignore everything else. A
    remember-one-bit task turned out to be too easy to separate the cells: a
    SimpleRNN scored 1.0000 at 120 steps, which says more about the task than
    about recurrence.
    """
    rng = np.random.default_rng(seed)
    values = rng.uniform(0.0, 1.0, (rows, length)).astype("float32")
    markers = np.zeros((rows, length), "float32")
    early = rng.integers(0, max(1, length // 10), rows)
    late = rng.integers(length // 2, length, rows)
    rows_index = np.arange(rows)
    markers[rows_index, early] = 1.0
    markers[rows_index, late] = 1.0
    targets = values[rows_index, early] + values[rows_index, late]
    return np.stack([values, markers], axis=-1), targets


@functools.lru_cache(maxsize=1)
def _memory_runs() -> dict:
    keras = tf().keras
    out = {}
    for length in DISTANCES:
        x_test, y_test = _adding_task(length, rows=1000, seed=1)
        # Predicting the mean sum (1.0) is the do-nothing baseline every model
        # on this task has to beat.
        out[("baseline", length)] = float(np.abs(y_test - 1.0).mean())
        for kind in ("rnn", "lstm"):
            x, y = _adding_task(length)
            seed_everything(0)
            layer = (keras.layers.SimpleRNN if kind == "rnn"
                     else keras.layers.LSTM)
            model = keras.Sequential([keras.layers.Input((length, 2)),
                                      layer(COPY_UNITS),
                                      keras.layers.Dense(1)])
            model.compile(keras.optimizers.Adam(3e-3), "mse", metrics=["mae"])
            history = model.fit(x, y, epochs=COPY_EPOCHS, batch_size=64,
                                verbose=0, validation_data=(x_test, y_test))
            out[(kind, length)] = min(float(v) for v in
                                      history.history["val_mae"])
    return out


def memory_length(fig, axes, p: Palette) -> None:
    runs = _memory_runs()
    ax = fig.subplots(1, 1)
    for kind, label, color in (("rnn", f"SimpleRNN({COPY_UNITS})", p.red),
                               ("lstm", f"LSTM({COPY_UNITS})", p.green)):
        values = [runs[(kind, d)] for d in DISTANCES]
        ax.plot(DISTANCES, values, "o-", ms=6, lw=2.0, color=color, label=label)
        for distance, value in zip(DISTANCES, values):
            ax.annotate(f"{value:.4f}", (distance, value),
                        textcoords="offset points", xytext=(0, 7),
                        ha="center", fontsize=7.5, color=color)
    baseline = [runs[("baseline", d)] for d in DISTANCES]
    ax.plot(DISTANCES, baseline, "--", lw=1.4, color=p.muted,
            label=f"predict the mean sum ({baseline[0]:.4f})")
    ax.set_xscale("log")
    ax.set_xticks(list(DISTANCES))
    ax.set_xticklabels([str(d) for d in DISTANCES])
    ax.set_xlabel("sequence length (the two marked values are far apart)")
    ax.set_ylabel("best validation MAE (lower is better)")
    ax.set_title(f"the adding problem — {COPY_ROWS:,} sequences, "
                 f"{COPY_EPOCHS} epochs, {COPY_UNITS} units", fontsize=10.5)
    ax.legend(fontsize=8, loc="upper left")


FIGURES = [
    figure("unrolled-state", unrolled_state, size=(9.4, 4.4), axes=False),
    figure("order-matters", order_matters, size=(7.6, 3.8), axes=False),
    figure("memory-length", memory_length, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    data = _reviews()
    lengths = data["lengths"]
    print(f"=== IMDB, {LIMIT:,} reviews, vocabulary {VOCAB:,} ===")
    print(f"true length: min {lengths.min()}  median "
          f"{int(np.median(lengths))}  mean {lengths.mean():.1f}  "
          f"max {lengths.max()}")
    print(f"padded to {MAXLEN}: {float((lengths < MAXLEN).mean()):.4f} of rows "
          f"are padded, {float((lengths > MAXLEN).mean()):.4f} are truncated")
    print(f"padding tokens as a share of all timesteps: "
          f"{float(np.clip(MAXLEN - lengths, 0, None).sum() / (LIMIT * MAXLEN)):.4f}")

    trace = _state_trace()
    states = trace["states"]
    print(f"\n=== one review through a {trace['units']}-unit SimpleRNN ===")
    print(f"true length {trace['length']}, so {trace['padding']} leading "
          f"padding steps")
    print(f"state shape {states.shape}  overall |state| mean "
          f"{float(np.abs(states).mean()):.4f}")
    if trace["padding"]:
        print(f"mean |state| during padding "
              f"{float(np.abs(states[:trace['padding']]).mean()):.4f}  "
              f"after padding "
              f"{float(np.abs(states[trace['padding']:]).mean()):.4f}")
    print(f"saturated units (|h| > 0.99) at the last step: "
          f"{int((np.abs(states[-1]) > 0.99).sum())} of {trace['units']}")

    runs = _order_runs()
    print(f"\n=== does word order matter? {EPOCHS} epochs ===")
    print(f"{'model':14s} {'in order':>10} {'shuffled':>10} {'cost of order':>14}")
    for model in ("bag of words", "SimpleRNN"):
        ordered = max(runs[(model, "in order")])
        shuffled = max(runs[(model, "shuffled")])
        print(f"{model:14s} {ordered:10.4f} {shuffled:10.4f} "
              f"{ordered - shuffled:+14.4f}")

    memory = _memory_runs()
    print(f"\n=== the adding problem, {COPY_EPOCHS} epochs, MAE ===")
    print(f"{'length':>7} {'baseline':>9} {'SimpleRNN':>10} {'LSTM':>8} "
          f"{'RNN vs baseline':>16} {'LSTM vs baseline':>17}")
    for length in DISTANCES:
        base = memory[("baseline", length)]
        rnn = memory[("rnn", length)]
        lstm = memory[("lstm", length)]
        print(f"{length:7d} {base:9.4f} {rnn:10.4f} {lstm:8.4f} "
              f"{base - rnn:+16.4f} {base - lstm:+17.4f}")
    print("the baseline predicts the mean sum of 1.0; a model no better than it")
    print("has not learned to carry a number across the sequence at all")

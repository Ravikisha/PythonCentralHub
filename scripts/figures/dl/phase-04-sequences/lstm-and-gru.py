"""Figures for *LSTM & GRU Networks*.

``gate-anatomy``
    Parameter counts and gate structure for SimpleRNN, GRU and LSTM at the same
    width — the price of the gates, in numbers.

``gate-traces``
    A trained LSTM's forget, input and output gate activations over one
    sequence, so "the gate decides what to keep" is something you can read off
    an axis.

``three-cells``
    All three cells on the same two tasks: sentiment (short-range) and the
    remember-one-bit copy task (long-range). The ordering is not the same on
    both, which is the useful part.
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
LIMIT = 5000
EPOCHS = 5
UNITS = 32
BATCH = 64
KINDS = ("SimpleRNN", "GRU", "LSTM")
COPY_DISTANCE = 80
COPY_ROWS = 3000
# 20 epochs at 16 units left every cell at the do-nothing baseline (MAE 0.33),
# which measures the budget rather than the gates. The adding problem is slow
# to crack even for an LSTM.
COPY_EPOCHS = 80
COPY_UNITS = 32
WIDTHS = (16, 32, 64, 128)


def _layer(kind: str, units: int, **kwargs):
    keras = tf().keras
    return {"SimpleRNN": keras.layers.SimpleRNN,
            "GRU": keras.layers.GRU,
            "LSTM": keras.layers.LSTM}[kind](units, **kwargs)


def gate_anatomy(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    keras = tf().keras
    features = 32
    counts = {}
    for kind in KINDS:
        row = []
        for width in WIDTHS:
            layer = _layer(kind, width)
            layer.build((None, MAXLEN, features))
            row.append(int(sum(np.prod(w.shape) for w in layer.weights)))
        counts[kind] = row
    colors = dict(zip(KINDS, (p.red, p.blue, p.green)))
    for kind in KINDS:
        left.plot(WIDTHS, counts[kind], "o-", ms=6, lw=2.0, color=colors[kind],
                  label=f"{kind} — {counts[kind][1] // counts['SimpleRNN'][1]}x "
                        f"SimpleRNN")
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xticks(list(WIDTHS))
    left.set_xticklabels([str(w) for w in WIDTHS])
    left.set_xlabel("units")
    left.set_ylabel("recurrent-layer parameters")
    left.set_title(f"same {features}-dimensional input, three cells",
                   fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    matrices = {"SimpleRNN": 1, "GRU": 3, "LSTM": 4}
    positions = np.arange(len(KINDS))
    right.bar(positions, [matrices[k] for k in KINDS], 0.5,
              color=[colors[k] for k in KINDS])
    for x, kind in zip(positions, KINDS):
        right.annotate(f"{matrices[kind]} weight "
                       f"matrix{'es' if matrices[kind] > 1 else ''}\n"
                       f"{counts[kind][1]:,} params at 32",
                       (x, matrices[kind]), textcoords="offset points",
                       xytext=(0, 5), ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(KINDS)
    right.set_ylim(0, 5.4)
    right.set_ylabel("input/recurrent matrix pairs")
    right.set_title("every gate is another full weight matrix", fontsize=10)
    del keras


@functools.lru_cache(maxsize=1)
def _reviews() -> dict:
    return imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)


@functools.lru_cache(maxsize=1)
def _gate_trace() -> dict:
    """Recompute an LSTM's gates by hand from its trained kernels.

    Keras does not expose gate activations, so the cell is re-implemented in
    NumPy from the layer's own weights: that is also the check that the
    equations on the page are the ones TensorFlow ran.
    """
    keras = tf().keras
    data = _reviews()
    seed_everything(0)
    model = keras.Sequential([
        keras.layers.Input((MAXLEN,)),
        keras.layers.Embedding(VOCAB, 32),
        keras.layers.LSTM(UNITS),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=BATCH, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    kernel, recurrent, bias = model.layers[1].get_weights()
    embed = keras.Model(model.inputs, model.layers[0].output)
    row = int(np.argmax(data["test_lengths"] < MAXLEN))
    sequence = embed.predict(data["x_test"][row:row + 1], verbose=0)[0]

    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    h = np.zeros(UNITS, "float32")
    c = np.zeros(UNITS, "float32")
    traces = {"input": [], "forget": [], "cell": [], "output": [],
              "carry": [], "hidden": []}
    for step in range(MAXLEN):
        z = sequence[step] @ kernel + h @ recurrent + bias
        i = sigmoid(z[:UNITS])
        f = sigmoid(z[UNITS:2 * UNITS])
        g = np.tanh(z[2 * UNITS:3 * UNITS])
        o = sigmoid(z[3 * UNITS:])
        c = f * c + i * g
        h = o * np.tanh(c)
        traces["input"].append(i.mean())
        traces["forget"].append(f.mean())
        traces["cell"].append(np.abs(g).mean())
        traces["output"].append(o.mean())
        traces["carry"].append(np.abs(c).mean())
        traces["hidden"].append(np.abs(h).mean())
    keras_output = float(model.predict(data["x_test"][row:row + 1],
                                       verbose=0)[0, 0])
    dense_kernel, dense_bias = model.layers[2].get_weights()
    by_hand = float(sigmoid(h @ dense_kernel + dense_bias)[0])
    return {"traces": {k: np.array(v) for k, v in traces.items()},
            "padding": int(MAXLEN - data["test_lengths"][row]),
            "keras": keras_output, "by_hand": by_hand,
            "val_accuracy": max(float(v)
                                for v in history.history["val_accuracy"])}


def gate_traces(fig, axes, p: Palette) -> None:
    info = _gate_trace()
    traces = info["traces"]
    top, bottom = fig.subplots(2, 1, sharex=True)
    for name, color in (("forget", p.green), ("input", p.blue),
                        ("output", p.purple)):
        top.plot(traces[name], lw=1.6, color=color,
                 label=f"{name} gate — mean {traces[name].mean():.3f}")
    top.set_ylabel("mean gate value")
    top.set_ylim(0, 1.05)
    top.set_title("one LSTM's gates, recomputed from its trained weights",
                  fontsize=10)
    top.legend(fontsize=8, loc="lower left", ncol=3)

    bottom.plot(traces["carry"], lw=1.8, color=p.amber,
                label="mean |carry state c|")
    bottom.plot(traces["hidden"], lw=1.6, color=p.red,
                label="mean |hidden state h|")
    bottom.set_xlabel("timestep")
    bottom.set_ylabel("magnitude")
    bottom.legend(fontsize=8, loc="upper left")
    for ax in (top, bottom):
        if info["padding"]:
            ax.axvline(info["padding"], color=p.muted, lw=1.2, ls="--")
    bottom.annotate("padding ends", (info["padding"], 0),
                    xytext=(6, 12), textcoords="offset points", fontsize=8,
                    color=p.muted)


def _adding_task(length: int, rows: int, seed: int = 0):
    """The adding problem, as on the intro page: carry a number a long way.

    Channel 0 is a uniform value, channel 1 marks two positions — one early,
    one in the second half — and the target is the sum of the two marked
    values. A remember-one-bit task is too easy to separate these cells.
    """
    rng = np.random.default_rng(seed)
    values = rng.uniform(0.0, 1.0, (rows, length)).astype("float32")
    markers = np.zeros((rows, length), "float32")
    early = rng.integers(0, max(1, length // 10), rows)
    late = rng.integers(length // 2, length, rows)
    index = np.arange(rows)
    markers[index, early] = 1.0
    markers[index, late] = 1.0
    targets = values[index, early] + values[index, late]
    return np.stack([values, markers], axis=-1), targets


@functools.lru_cache(maxsize=1)
def _task_runs() -> dict:
    keras = tf().keras
    data = _reviews()
    out = {}
    for kind in KINDS:
        seed_everything(0)
        model = keras.Sequential([
            keras.layers.Input((MAXLEN,)),
            keras.layers.Embedding(VOCAB, 32),
            _layer(kind, UNITS),
            keras.layers.Dense(1, activation="sigmoid"),
        ])
        model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                      metrics=["accuracy"])
        started = time.perf_counter()
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=BATCH, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[("sentiment", kind)] = {
            "best": max(float(v) for v in history.history["val_accuracy"]),
            "curve": [float(v) for v in history.history["val_accuracy"]],
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
        }

        x, y = _adding_task(COPY_DISTANCE, COPY_ROWS)
        x_test, y_test = _adding_task(COPY_DISTANCE, 1000, seed=1)
        seed_everything(0)
        cell = keras.Sequential([keras.layers.Input((COPY_DISTANCE, 2)),
                                 _layer(kind, COPY_UNITS),
                                 keras.layers.Dense(1)])
        cell.compile(keras.optimizers.Adam(3e-3), "mse", metrics=["mae"])
        started = time.perf_counter()
        history = cell.fit(x, y, epochs=COPY_EPOCHS, batch_size=64, verbose=0,
                           validation_data=(x_test, y_test))
        out[("adding", kind)] = {
            "best": min(float(v) for v in history.history["val_mae"]),
            "curve": [float(v) for v in history.history["val_mae"]],
            "params": int(cell.count_params()),
            "seconds": time.perf_counter() - started,
        }
    out["baseline"] = float(np.abs(_adding_task(COPY_DISTANCE, 1000,
                                               seed=1)[1] - 1.0).mean())
    return out


def three_cells(fig, axes, p: Palette) -> None:
    runs = _task_runs()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(KINDS, (p.red, p.blue, p.green)))
    positions = np.arange(len(KINDS))
    values = [runs[("sentiment", kind)]["best"] for kind in KINDS]
    left.bar(positions, values, 0.5, color=[colors[k] for k in KINDS])
    for x, value, kind in zip(positions, values, KINDS):
        left.annotate(f"{value:.4f}\n{runs[('sentiment', kind)]['params']:,} "
                      f"params\n{runs[('sentiment', kind)]['seconds']:.0f}s",
                      (x, value), textcoords="offset points", xytext=(0, 4),
                      ha="center", fontsize=7.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(KINDS)
    left.set_ylim(0, 1.18)
    left.set_ylabel("best validation accuracy")
    left.set_title(f"short-range: IMDB sentiment, {EPOCHS} epochs", fontsize=10)

    for kind in KINDS:
        run = runs[("adding", kind)]
        right.plot(range(1, len(run["curve"]) + 1), run["curve"], lw=1.9,
                   color=colors[kind],
                   label=f"{kind} — best {run['best']:.4f}, "
                         f"{run['seconds']:.0f}s")
    right.axhline(runs["baseline"], color=p.muted, lw=1.3, ls="--",
                  label=f"predict the mean sum ({runs['baseline']:.4f})")
    right.set_xlabel("epoch")
    right.set_ylabel("validation MAE (lower is better)")
    right.set_title(f"long-range: the adding problem at {COPY_DISTANCE} steps",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="upper right")


FIGURES = [
    figure("gate-anatomy", gate_anatomy, size=(9.4, 3.6), axes=False),
    figure("gate-traces", gate_traces, size=(9.4, 4.2), axes=False),
    figure("three-cells", three_cells, size=(9.4, 3.7), axes=False),
]


if __name__ == "__main__":
    features = 32
    print(f"=== parameters at {features}-dimensional input ===")
    print(f"{'units':>6} " + " ".join(f"{k:>12}" for k in KINDS))
    for width in WIDTHS:
        row = []
        for kind in KINDS:
            layer = _layer(kind, width)
            layer.build((None, MAXLEN, features))
            row.append(int(sum(np.prod(w.shape) for w in layer.weights)))
        print(f"{width:6d} " + " ".join(f"{v:12,}" for v in row))
    print("GRU is 3x a SimpleRNN and LSTM 4x, because each gate is another")
    print("input matrix, recurrent matrix and bias")

    info = _gate_trace()
    traces = info["traces"]
    print(f"\n=== an LSTM's gates over one review "
          f"(val acc {info['val_accuracy']:.4f}) ===")
    print(f"NumPy re-implementation against Keras: by hand "
          f"{info['by_hand']:.6f}  Keras {info['keras']:.6f}  difference "
          f"{abs(info['by_hand'] - info['keras']):.2e}")
    real = slice(info["padding"], MAXLEN)
    print(f"{'signal':10s} {'mean over padding':>18} {'mean over text':>15}")
    for name in ("forget", "input", "output", "carry", "hidden"):
        pad_mean = (float(traces[name][:info["padding"]].mean())
                    if info["padding"] else float("nan"))
        print(f"{name:10s} {pad_mean:18.4f} {float(traces[name][real].mean()):15.4f}")
    print(f"the forget gate sits at {float(traces['forget'].mean()):.4f} on "
          f"average, so the carry state decays by that factor per step")

    runs = _task_runs()
    print(f"\n=== three cells, two tasks ===")
    print(f"{'task':10s} {'cell':10s} {'params':>9} {'best score':>11} "
          f"{'seconds':>9}")
    for task in ("sentiment", "adding"):
        for kind in KINDS:
            run = runs[(task, kind)]
            print(f"{task:10s} {kind:10s} {run['params']:9,} "
                  f"{run['best']:11.4f} {run['seconds']:9.1f}")
    print(f"sentiment is accuracy (higher better); adding is MAE (lower "
          f"better) against a do-nothing baseline of {runs['baseline']:.4f}")

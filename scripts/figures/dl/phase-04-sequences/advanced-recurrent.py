"""Figures for *Advanced Recurrent Layers (Dropout, Stacking, Bidirectional)*.

``recurrent-dropout``
    Plain dropout against ``recurrent_dropout``, and both together. The two
    arguments do different things and only one of them is applied at every
    timestep.

``stacking-depth``
    One, two and three recurrent layers, with the ``return_sequences`` rule that
    makes stacking work at all.

``bidirectional``
    Forward, backward and both, on a task where the second half of the sequence
    decides the answer — plus the reason you cannot use it for forecasting.
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
EPOCHS = 8
UNITS = 32
BATCH = 64
DROPOUTS = ((0.0, 0.0), (0.3, 0.0), (0.0, 0.3), (0.3, 0.3))
DEPTHS = (1, 2, 3)
DIRECTIONS = ("forward", "backward", "bidirectional")


@functools.lru_cache(maxsize=1)
def _reviews() -> dict:
    return imdb(vocab=VOCAB, maxlen=MAXLEN, limit=LIMIT)


def _stack(depth: int = 1, dropout: float = 0.0,
           recurrent_dropout: float = 0.0, direction: str = "forward",
           units: int = UNITS, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    layers = [keras.layers.Input((MAXLEN,)),
              keras.layers.Embedding(VOCAB, 32, mask_zero=True)]
    for index in range(depth):
        last = index == depth - 1
        cell = keras.layers.LSTM(units, dropout=dropout,
                                 recurrent_dropout=recurrent_dropout,
                                 return_sequences=not last,
                                 go_backwards=direction == "backward")
        if direction == "bidirectional":
            cell = keras.layers.Bidirectional(
                keras.layers.LSTM(units, dropout=dropout,
                                  recurrent_dropout=recurrent_dropout,
                                  return_sequences=not last))
        layers.append(cell)
    layers.append(keras.layers.Dense(1, activation="sigmoid"))
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(1e-3), "binary_crossentropy",
                  metrics=["accuracy"])
    return model


def _run(**kwargs) -> dict:
    data = _reviews()
    model = _stack(**kwargs)
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=BATCH, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"val": [float(v) for v in history.history["val_accuracy"]],
            "train": [float(v) for v in history.history["accuracy"]],
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started}


@functools.lru_cache(maxsize=1)
def _dropout_runs() -> dict:
    return {pair: _run(dropout=pair[0], recurrent_dropout=pair[1])
            for pair in DROPOUTS}


@functools.lru_cache(maxsize=1)
def _depth_runs() -> dict:
    return {depth: _run(depth=depth) for depth in DEPTHS}


@functools.lru_cache(maxsize=1)
def _direction_runs() -> dict:
    """Bidirectional doubles the units, so also compare at matched width."""
    out = {direction: _run(direction=direction) for direction in DIRECTIONS}
    out["bidirectional (16+16)"] = _run(direction="bidirectional",
                                        units=UNITS // 2)
    return out


def recurrent_dropout(fig, axes, p: Palette) -> None:
    runs = _dropout_runs()
    left, right = fig.subplots(1, 2)
    labels = [f"dropout {a}\nrecurrent {b}" for a, b in DROPOUTS]
    best = [max(runs[pair]["val"]) for pair in DROPOUTS]
    gaps = [runs[pair]["train"][-1] - runs[pair]["val"][-1] for pair in DROPOUTS]
    winner = max(best)
    positions = np.arange(len(DROPOUTS))
    left.bar(positions - 0.19, gaps, 0.36, color=p.muted,
             label="final train − val gap")
    left.bar(positions + 0.19, best, 0.36,
             color=[p.green if abs(v - winner) < 1e-9 else p.blue
                    for v in best],
             label="best validation accuracy")
    for x, value in zip(positions + 0.19, best):
        left.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=7.5, color=p.fg)
    for x, value in zip(positions - 0.19, gaps):
        left.annotate(f"{value:+.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=7.5, color=p.muted)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=7.5)
    left.set_ylabel("accuracy")
    left.set_title(f"LSTM({UNITS}) on IMDB, {EPOCHS} epochs", fontsize=10)
    left.legend(fontsize=7.5, loc="upper left")

    epochs = range(1, EPOCHS + 1)
    colors = dict(zip(DROPOUTS, (p.muted, p.blue, p.purple, p.green)))
    for pair in DROPOUTS:
        run = runs[pair]
        right.plot(epochs, run["train"], lw=1.2, ls="--", color=colors[pair])
        right.plot(epochs, run["val"], lw=2.0, color=colors[pair],
                   label=f"{pair[0]}/{pair[1]} — {run['seconds']:.0f}s")
    right.set_xlabel("epoch")
    right.set_ylabel("accuracy")
    right.set_title("dashed = train, solid = validation", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right", title="dropout/recurrent",
                 title_fontsize=7.5)


def stacking_depth(fig, axes, p: Palette) -> None:
    runs = _depth_runs()
    left, right = fig.subplots(1, 2)
    colors = dict(zip(DEPTHS, (p.blue, p.green, p.purple)))
    for depth in DEPTHS:
        run = runs[depth]
        left.plot(range(1, EPOCHS + 1), run["val"], lw=2.0,
                  color=colors[depth],
                  label=f"{depth} layer{'s' if depth > 1 else ''} — "
                        f"{run['params']:,} params, {run['seconds']:.0f}s")
    left.set_xlabel("epoch")
    left.set_ylabel("validation accuracy")
    left.set_title("stacked LSTMs on IMDB", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    positions = np.arange(len(DEPTHS))
    best = [max(runs[d]["val"]) for d in DEPTHS]
    seconds = [runs[d]["seconds"] for d in DEPTHS]
    right.bar(positions, best, 0.5, color=[colors[d] for d in DEPTHS])
    for x, value, second in zip(positions, best, seconds):
        right.annotate(f"{value:.4f}\n{second:.0f}s", (x, value),
                       textcoords="offset points", xytext=(0, 4), ha="center",
                       fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([f"{d} layer{'s' if d > 1 else ''}" for d in DEPTHS])
    right.set_ylim(0, 1.05)
    right.set_ylabel("best validation accuracy")
    right.set_title("depth costs time; it does not always buy accuracy",
                    fontsize=10)


def bidirectional(fig, axes, p: Palette) -> None:
    runs = _direction_runs()
    left, right = fig.subplots(1, 2)
    keys = list(runs)
    colors = {"forward": p.blue, "backward": p.amber,
              "bidirectional": p.green, "bidirectional (16+16)": p.purple}
    positions = np.arange(len(keys))
    best = [max(runs[k]["val"]) for k in keys]
    left.bar(positions, best, 0.5, color=[colors[k] for k in keys])
    for x, key, value in zip(positions, keys, best):
        left.annotate(f"{value:.4f}\n{runs[key]['params']:,} params",
                      (x, value), textcoords="offset points", xytext=(0, 4),
                      ha="center", fontsize=7.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([k.replace(" (", "\n(") for k in keys], fontsize=7.5)
    left.set_ylim(0, 1.12)
    left.set_ylabel("best validation accuracy")
    left.set_title("reading the review in both directions", fontsize=10)

    for key in keys:
        right.plot(range(1, EPOCHS + 1), runs[key]["val"], lw=1.9,
                   color=colors[key],
                   label=f"{key} — {runs[key]['seconds']:.0f}s")
    right.set_xlabel("epoch")
    right.set_ylabel("validation accuracy")
    right.set_title("a backward pass is not a worse pass", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


FIGURES = [
    figure("recurrent-dropout", recurrent_dropout, size=(9.6, 3.7),
           axes=False),
    figure("stacking-depth", stacking_depth, size=(9.6, 3.7), axes=False),
    figure("bidirectional", bidirectional, size=(9.6, 3.7), axes=False),
]


if __name__ == "__main__":
    print(f"=== two dropout arguments, LSTM({UNITS}), {EPOCHS} epochs ===")
    runs = _dropout_runs()
    print(f"{'dropout':>8} {'recurrent':>10} {'best val':>9} {'final gap':>10} "
          f"{'seconds':>9}")
    for pair in DROPOUTS:
        run = runs[pair]
        print(f"{pair[0]:8.1f} {pair[1]:10.1f} {max(run['val']):9.4f} "
              f"{run['train'][-1] - run['val'][-1]:+10.4f} "
              f"{run['seconds']:9.1f}")
    plain = runs[(0.0, 0.0)]
    print(f"recurrent_dropout costs "
          f"{runs[(0.0, 0.3)]['seconds'] / plain['seconds']:.1f}x the wall-clock "
          f"of no dropout, because it disables the fused kernel")

    print(f"\n=== stacking ===")
    depths = _depth_runs()
    print(f"{'layers':>7} {'params':>9} {'best val':>9} {'seconds':>9}")
    for depth in DEPTHS:
        run = depths[depth]
        print(f"{depth:7d} {run['params']:9,} {max(run['val']):9.4f} "
              f"{run['seconds']:9.1f}")
    print("every layer but the last needs return_sequences=True, or the next")
    print("layer receives a vector where it expects a sequence")

    print(f"\n=== direction ===")
    directions = _direction_runs()
    print(f"{'setup':24s} {'params':>9} {'best val':>9} {'seconds':>9}")
    for key, run in directions.items():
        print(f"{key:24s} {run['params']:9,} {max(run['val']):9.4f} "
              f"{run['seconds']:9.1f}")
    forward = max(directions["forward"]["val"])
    both = max(directions["bidirectional"]["val"])
    matched = max(directions["bidirectional (16+16)"]["val"])
    print(f"bidirectional at double width: {both - forward:+.4f} over forward")
    print(f"bidirectional at matched width: {matched - forward:+.4f}")
    print("a forecasting model cannot use this: the backward pass reads the")
    print("future, which at prediction time does not exist yet")

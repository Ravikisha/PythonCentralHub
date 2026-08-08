"""Figures for *The Universal Workflow of Machine Learning*.

``baseline-ladder``
    Five rungs on the same dataset, from "predict the majority class" to a tuned
    network. Each rung has to beat the one below it to justify its complexity.

``overfit-then-regularise``
    Step 2 of the workflow made concrete: build something that overfits, confirm
    it overfits, then push back. Three models, one plot.

``capacity-frontier``
    Step 3 of the workflow is "scale up until you overfit", and this is that
    instruction measured. Training and validation accuracy against model size,
    with the gap between them plotted underneath -- the point at which the gap
    starts widening is the point the instruction is pointing at, and it is not
    the point of best validation accuracy.
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

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 8000
EPOCHS = 30


@functools.lru_cache(maxsize=1)
def _ladder() -> dict:
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression

    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    x, y = data["x_train"], data["y_train"]
    xt, yt = data["x_test"], data["y_test"]
    rungs = []

    start = time.perf_counter()
    dummy = DummyClassifier(strategy="most_frequent").fit(x, y)
    rungs.append(("majority\nclass", float(dummy.score(xt, yt)), 0,
                  time.perf_counter() - start))

    start = time.perf_counter()
    logistic = LogisticRegression(max_iter=300).fit(x, y)
    rungs.append(("logistic\nregression", float(logistic.score(xt, yt)),
                  int(784 * 10 + 10), time.perf_counter() - start))

    def network(units, dropout=0.0, epochs=EPOCHS, patience=None):
        seed_everything(0)
        layers = [keras.layers.Input((784,))]
        for width in units:
            layers.append(keras.layers.Dense(width, activation="relu"))
            if dropout:
                layers.append(keras.layers.Dropout(dropout))
        layers.append(keras.layers.Dense(10, activation="softmax"))
        model = keras.Sequential(layers)
        model.compile(keras.optimizers.Adam(1e-3),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        callbacks = []
        if patience:
            callbacks.append(keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=patience,
                restore_best_weights=True))
        began = time.perf_counter()
        history = model.fit(x, y, epochs=epochs, batch_size=128, verbose=0,
                            validation_data=(xt, yt), callbacks=callbacks)
        return (model, history, time.perf_counter() - began)

    model, _, seconds = network([32])
    rungs.append(("small MLP\n32 units",
                  float(model.evaluate(xt, yt, verbose=0)[1]),
                  model.count_params(), seconds))

    model, _, seconds = network([512, 512])
    rungs.append(("wide MLP\n512-512",
                  float(model.evaluate(xt, yt, verbose=0)[1]),
                  model.count_params(), seconds))

    model, _, seconds = network([512, 512], dropout=0.4, epochs=60, patience=8)
    rungs.append(("wide + dropout\n+ early stop",
                  float(model.evaluate(xt, yt, verbose=0)[1]),
                  model.count_params(), seconds))
    return {"rungs": rungs}


def baseline_ladder(fig, axes, p: Palette) -> None:
    rungs = _ladder()["rungs"]
    ax = fig.subplots(1, 1)
    labels = [r[0] for r in rungs]
    scores = [r[1] for r in rungs]
    positions = np.arange(len(labels))
    best = max(scores)
    ax.bar(positions, scores, 0.55,
           color=[p.green if abs(s - best) < 1e-9 else p.blue for s in scores])
    for x, (label, score, params, seconds) in zip(positions, rungs):
        ax.annotate(f"{score:.4f}", (x, score), textcoords="offset points",
                    xytext=(0, 16), ha="center", fontsize=9, color=p.fg)
        ax.annotate(f"{params:,} params\n{seconds:.1f}s", (x, score),
                    textcoords="offset points", xytext=(0, 3), ha="center",
                    fontsize=7, color=p.muted)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("test accuracy")
    ax.set_ylim(0, 1.08)
    ax.set_title("Each rung has to beat the one below it to be worth using",
                 fontsize=10.5)


@functools.lru_cache(maxsize=1)
def _overfit_then_regularise() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    out = {}
    recipes = {
        "too small (8 units)": ([8], 0.0),
        "overfits (512-512)": ([512, 512], 0.0),
        "regularised (dropout 0.4)": ([512, 512], 0.4),
    }
    for label, (units, dropout) in recipes.items():
        seed_everything(0)
        layers = [keras.layers.Input((784,))]
        for width in units:
            layers.append(keras.layers.Dense(width, activation="relu"))
            if dropout:
                layers.append(keras.layers.Dropout(dropout))
        layers.append(keras.layers.Dense(10, activation="softmax"))
        model = keras.Sequential(layers)
        model.compile(keras.optimizers.Adam(1e-3),
                      "sparse_categorical_crossentropy", metrics=["accuracy"])
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        out[label] = {k: [float(v) for v in vals]
                      for k, vals in history.history.items()}
    return out


def overfit_then_regularise(fig, axes, p: Palette) -> None:
    runs = _overfit_then_regularise()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)
    colors = dict(zip(runs, (p.muted, p.red, p.green)))
    for label, run in runs.items():
        left.plot(epochs, run["accuracy"], lw=1.6, ls="--", color=colors[label])
        left.plot(epochs, run["val_accuracy"], lw=2.0, color=colors[label],
                  label=f"{label} — val {run['val_accuracy'][-1]:.4f}")
        gap = run["accuracy"][-1] - run["val_accuracy"][-1]
        right.plot(epochs,
                   [t - v for t, v in zip(run["accuracy"], run["val_accuracy"])],
                   lw=2.0, color=colors[label], label=f"{label} — {gap:+.4f}")
    left.set_xlabel("epoch")
    left.set_ylabel("accuracy")
    left.set_ylim(0.6, 1.02)
    left.set_title("dashed = training, solid = validation", fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    right.axhline(0, color=p.grid, lw=1.0)
    right.set_xlabel("epoch")
    right.set_ylabel("training accuracy - validation accuracy")
    right.set_title("the generalisation gap", fontsize=10)
    right.legend(fontsize=7.5)


CAPACITIES = ((16,), (64,), (256,), (256, 256), (512, 512), (1024, 1024))


@functools.lru_cache(maxsize=1)
def _capacity() -> dict:
    keras = tf().keras
    data = dataset("fashion", limit=LIMIT, flat=True)
    rows = []
    for units in CAPACITIES:
        seed_everything(0)
        layers = [keras.layers.Input((784,))]
        for width in units:
            layers.append(keras.layers.Dense(width, activation="relu"))
        layers.append(keras.layers.Dense(10, activation="softmax"))
        model = keras.Sequential(layers)
        model.compile("adam", "sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["y_test"]))
        train = float(history.history["accuracy"][-1])
        validation = float(history.history["val_accuracy"][-1])
        rows.append({
            "label": " x ".join(str(width) for width in units),
            "parameters": int(model.count_params()),
            "train": train,
            "validation": validation,
            "best": float(max(history.history["val_accuracy"])),
            "gap": train - validation,
        })
    return {"rows": rows}


def capacity_frontier(fig, axes, p: Palette) -> None:
    rows = _capacity()["rows"]
    top, bottom = fig.subplots(2, 1, height_ratios=(1.6, 1.0), sharex=True)
    sizes = [row["parameters"] for row in rows]
    top.plot(sizes, [row["train"] for row in rows], "o-", color=p.amber,
             lw=1.8, ms=5, label="training accuracy")
    top.plot(sizes, [row["validation"] for row in rows], "o-", color=p.blue,
             lw=1.8, ms=5, label="validation accuracy")
    best = max(rows, key=lambda row: row["validation"])
    top.axvline(best["parameters"], color=p.green, lw=1.2, ls="--")
    top.annotate(f"best validation {best['validation']:.4f}",
                 (best["parameters"], best["validation"]), xytext=(6, -12),
                 textcoords="offset points", fontsize=8, color=p.green)
    top.set_xscale("log")
    top.set_ylabel("accuracy")
    top.set_title(f"Fashion-MNIST, {LIMIT:,} rows, {EPOCHS} epochs, "
                  f"no regularisation", fontsize=10)
    top.legend(fontsize=8, loc="lower right")

    gaps = [row["gap"] for row in rows]
    bottom.plot(sizes, gaps, "o-", color=p.red, lw=1.8, ms=5)
    for row in rows:
        bottom.annotate(f"{row['gap']:.3f}", (row["parameters"], row["gap"]),
                        xytext=(0, 5), textcoords="offset points",
                        ha="center", fontsize=7.5, color=p.fg)
    bottom.axhline(0, color=p.fg, lw=0.8, ls=":")
    bottom.set_xscale("log")
    bottom.set_xlabel("parameters")
    bottom.set_ylabel("train minus validation")
    bottom.set_xticks(sizes)
    bottom.set_xticklabels([row["label"] for row in rows], fontsize=7.5)


FIGURES = [
    figure("baseline-ladder", baseline_ladder, size=(8.4, 3.8), axes=False),
    figure("capacity-frontier", capacity_frontier, size=(8.4, 5.0),
           axes=False),
    figure("overfit-then-regularise", overfit_then_regularise, size=(9.4, 3.6),
           axes=False),
]


if __name__ == "__main__":
    print("=== scale up until you overfit ===")
    print(f"{'model':16s} {'parameters':>12} {'train':>9} {'validation':>11} "
          f"{'best val':>10} {'gap':>8}")
    for row in _capacity()["rows"]:
        print(f"{row['label']:16s} {row['parameters']:12,} {row['train']:9.4f} "
              f"{row['validation']:11.4f} {row['best']:10.4f} "
              f"{row['gap']:8.4f}")
    print()

    print(f"=== baseline ladder, Fashion-MNIST {LIMIT} rows ===")
    print(f"{'rung':24s} {'test acc':>9} {'params':>12} {'seconds':>9}")
    for label, score, params, seconds in _ladder()["rungs"]:
        print(f"{label.replace(chr(10), ' '):24s} {score:9.4f} {params:12,} "
              f"{seconds:9.2f}")

    print("\n=== overfit, then regularise ===")
    print(f"{'model':28s} {'train acc':>10} {'val acc':>9} {'gap':>8} "
          f"{'best val acc':>13}")
    for label, run in _overfit_then_regularise().items():
        gap = run["accuracy"][-1] - run["val_accuracy"][-1]
        print(f"{label:28s} {run['accuracy'][-1]:10.4f} "
              f"{run['val_accuracy'][-1]:9.4f} {gap:8.4f} "
              f"{max(run['val_accuracy']):13.4f}")

"""Figures for *Time Series Forecasting with RNNs*.

``series-and-windows``
    The generated series, one training window and its target, plus the noise
    floor — the number every model on the page is judged against.

``baseline-against-models``
    Naive persistence, a dense model, a 1D convolution and a GRU, all on the
    same windows. The baseline is the point: a model that cannot beat it has
    learned nothing.

``horizon-decay``
    Error against forecast horizon, which is where every optimistic
    single-step demo falls apart.
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

from _dl import seed_everything, tf, waves  # noqa: E402
from _style import Palette, figure  # noqa: E402

ROWS = 4000
TIMESTEPS = 48
NOISE = 0.12
EPOCHS = 25
BATCH = 64
HORIZONS = (1, 6, 12, 24)
MODELS = ("naive", "dense", "conv1d", "GRU")
SPLIT = 0.75


def _split(horizon: int = 1):
    """Chronological split — never a random one, or the future leaks."""
    x, y = waves(rows=ROWS, timesteps=TIMESTEPS, horizon=horizon, noise=NOISE)
    cut = int(len(x) * SPLIT)
    return x[:cut], y[:cut], x[cut:], y[cut:]


def _build(kind: str, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((TIMESTEPS, 1))
    if kind == "dense":
        x = keras.layers.Flatten()(inputs)
        x = keras.layers.Dense(32, activation="relu")(x)
    elif kind == "conv1d":
        # padding="same" so a short window cannot shrink to nothing: two valid
        # kernels of 5 plus a pooling step already need 14 timesteps.
        x = keras.layers.Conv1D(32, 5, padding="same", activation="relu")(inputs)
        x = keras.layers.MaxPooling1D(2)(x)
        x = keras.layers.Conv1D(32, 5, padding="same", activation="relu")(x)
        x = keras.layers.GlobalAveragePooling1D()(x)
    else:
        x = keras.layers.GRU(32)(inputs)
    model = keras.Model(inputs, keras.layers.Dense(1)(x))
    model.compile(keras.optimizers.Adam(1e-3), "mse", metrics=["mae"])
    return model


def _fit(kind: str, horizon: int = 1) -> dict:
    x_train, y_train, x_test, y_test = _split(horizon)
    if kind == "naive":
        predicted = x_test[:, -1, 0]
        return {"mae": float(np.abs(predicted - y_test).mean()),
                "params": 0, "seconds": 0.0,
                "history": [], "predicted": predicted}
    model = _build(kind)
    started = time.perf_counter()
    history = model.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH,
                        verbose=0, validation_data=(x_test, y_test))
    predicted = model.predict(x_test, verbose=0)[:, 0]
    return {"mae": float(np.abs(predicted - y_test).mean()),
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
            "history": [float(v) for v in history.history["val_mae"]],
            "predicted": predicted}


@functools.lru_cache(maxsize=1)
def _single_step() -> dict:
    return {kind: _fit(kind) for kind in MODELS}


@functools.lru_cache(maxsize=1)
def _horizon_runs() -> dict:
    out = {}
    for horizon in HORIZONS:
        for kind in ("naive", "GRU"):
            out[(kind, horizon)] = _fit(kind, horizon)["mae"]
    return out


def series_and_windows(fig, axes, p: Palette) -> None:
    x, y = waves(rows=ROWS, timesteps=TIMESTEPS, horizon=1, noise=NOISE)
    clean_x, clean_y = waves(rows=ROWS, timesteps=TIMESTEPS, horizon=1,
                             noise=0.0)
    left, right = fig.subplots(1, 2)
    span = 240
    series = np.concatenate([x[0, :, 0], y[:span]])
    truth = np.concatenate([clean_x[0, :, 0], clean_y[:span]])
    left.plot(truth, lw=1.6, color=p.green, label="signal without noise")
    left.plot(series, lw=1.0, color=p.blue, alpha=0.85,
              label=f"observed (noise sd {NOISE})")
    left.set_xlabel("timestep")
    left.set_ylabel("value")
    left.set_title("two periods (24 and 7 steps) plus noise", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    right.plot(range(TIMESTEPS), x[0, :, 0], "o-", ms=3, lw=1.4, color=p.blue,
               label=f"one window: {TIMESTEPS} steps in")
    right.plot([TIMESTEPS], [y[0]], "o", ms=9, color=p.amber,
               label="target: the next step")
    right.axvline(TIMESTEPS - 0.5, color=p.muted, lw=1.1, ls="--")
    naive_error = float(np.abs(x[:, -1, 0] - y).mean())
    # E|N(0, sigma)| = sigma * sqrt(2/pi): the MAE a perfect forecaster still
    # pays against a noisy target.
    noise_floor = float(NOISE * np.sqrt(2 / np.pi))
    right.annotate(f"persistence MAE {naive_error:.4f}\n"
                   f"irreducible noise MAE ~{noise_floor:.4f}",
                   (1, min(x[0, :, 0])), fontsize=8.5, color=p.fg)
    right.set_xlabel("position in the window")
    right.set_ylabel("value")
    right.set_title("what one training row looks like", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def baseline_against_models(fig, axes, p: Palette) -> None:
    runs = _single_step()
    left, right = fig.subplots(1, 2)
    colors = {"naive": p.muted, "dense": p.blue, "conv1d": p.purple,
              "GRU": p.green}
    positions = np.arange(len(MODELS))
    values = [runs[k]["mae"] for k in MODELS]
    best = min(values)
    left.bar(positions, values, 0.55,
             color=[p.green if abs(v - best) < 1e-12 else colors[k]
                    for k, v in zip(MODELS, values)])
    for x, value, kind in zip(positions, values, MODELS):
        left.annotate(f"{value:.4f}\n{runs[kind]['params']:,} params",
                      (x, value), textcoords="offset points", xytext=(0, 4),
                      ha="center", fontsize=8, color=p.fg)
    left.axhline(runs["naive"]["mae"], color=p.red, lw=1.3, ls="--")
    left.annotate("persistence baseline", (len(MODELS) - 0.55,
                                           runs["naive"]["mae"]),
                  xytext=(0, 6), textcoords="offset points", fontsize=8,
                  ha="center", color=p.red)
    floor = float(NOISE * np.sqrt(2 / np.pi))
    left.axhline(floor, color=p.amber, lw=1.2, ls=":")
    left.annotate(f"irreducible noise {floor:.4f}", (0.6, floor),
                  xytext=(0, -12), textcoords="offset points", fontsize=8,
                  ha="center", color=p.amber)
    left.set_xticks(positions)
    left.set_xticklabels(MODELS)
    left.set_ylim(0, max(values) * 1.35)
    left.set_ylabel("test MAE (lower is better)")
    left.set_title(f"one-step forecast, {ROWS:,} windows, {EPOCHS} epochs",
                   fontsize=10)

    for kind in MODELS:
        if not runs[kind]["history"]:
            continue
        right.plot(range(1, EPOCHS + 1), runs[kind]["history"], lw=1.9,
                   color=colors[kind],
                   label=f"{kind} — {runs[kind]['seconds']:.0f}s")
    right.axhline(runs["naive"]["mae"], color=p.red, lw=1.3, ls="--",
                  label=f"persistence {runs['naive']['mae']:.4f}")
    right.set_xlabel("epoch")
    right.set_ylabel("validation MAE")
    right.set_title("how long each takes to beat doing nothing", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def horizon_decay(fig, axes, p: Palette) -> None:
    runs = _horizon_runs()
    ax = fig.subplots(1, 1)
    for kind, color in (("naive", p.red), ("GRU", p.green)):
        values = [runs[(kind, h)] for h in HORIZONS]
        ax.plot(HORIZONS, values, "o-", ms=6, lw=2.0, color=color, label=kind)
        for horizon, value in zip(HORIZONS, values):
            ax.annotate(f"{value:.4f}", (horizon, value),
                        textcoords="offset points", xytext=(0, 7), ha="center",
                        fontsize=7.5, color=color)
    floor = float(NOISE * np.sqrt(2 / np.pi))
    ax.axhline(floor, color=p.amber, lw=1.2, ls=":",
               label=f"irreducible noise ({floor:.4f})")
    gains = [runs[("naive", h)] - runs[("GRU", h)] for h in HORIZONS]
    ax.annotate(f"the model's advantage over persistence: "
                f"{gains[0]:+.4f} at h=1, {gains[-1]:+.4f} at h={HORIZONS[-1]}",
                (HORIZONS[0], max(runs.values()) * 0.95), fontsize=8.5,
                color=p.fg)
    ax.set_xticks(list(HORIZONS))
    ax.set_xticklabels([str(h) for h in HORIZONS])
    ax.set_xlabel("forecast horizon (steps ahead)")
    ax.set_ylabel("test MAE")
    ax.set_title(f"the same GRU at four horizons, {TIMESTEPS}-step windows",
                 fontsize=10.5)
    # The naive curve peaks near half a period, so the lower-right corner holds
    # data; the upper right is empty.
    ax.legend(fontsize=8, loc="upper right")


FIGURES = [
    figure("series-and-windows", series_and_windows, size=(9.4, 3.5),
           axes=False),
    figure("baseline-against-models", baseline_against_models, size=(9.6, 3.7),
           axes=False),
    figure("horizon-decay", horizon_decay, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    x, y = waves(rows=ROWS, timesteps=TIMESTEPS, horizon=1, noise=NOISE)
    clean_x, clean_y = waves(rows=ROWS, timesteps=TIMESTEPS, horizon=1,
                             noise=0.0)
    print(f"=== the series: {ROWS:,} windows of {TIMESTEPS} steps ===")
    print(f"target mean {y.mean():.4f}  sd {y.std():.4f}  "
          f"range [{y.min():.3f}, {y.max():.3f}]")
    print(f"noise sd {NOISE}; a perfect model still scores MAE "
          f"{float(np.abs(y - clean_y).mean()):.4f} against the noisy target")
    print(f"persistence (predict the last observed value): MAE "
          f"{float(np.abs(x[:, -1, 0] - y).mean()):.4f}")
    print(f"predicting the training mean: MAE "
          f"{float(np.abs(y[:int(ROWS * SPLIT)].mean() - y[int(ROWS * SPLIT):]).mean()):.4f}")

    runs = _single_step()
    print(f"\n=== one-step forecast, {EPOCHS} epochs ===")
    print(f"{'model':8s} {'params':>9} {'test MAE':>9} {'vs naive':>9} "
          f"{'seconds':>9}")
    for kind in MODELS:
        run = runs[kind]
        print(f"{kind:8s} {run['params']:9,} {run['mae']:9.4f} "
              f"{runs['naive']['mae'] - run['mae']:+9.4f} "
              f"{run['seconds']:9.1f}")

    print(f"\n=== horizon sweep ===")
    horizons = _horizon_runs()
    print(f"{'horizon':>8} {'naive':>9} {'GRU':>9} {'gain':>9}")
    for horizon in HORIZONS:
        naive = horizons[("naive", horizon)]
        gru = horizons[("GRU", horizon)]
        print(f"{horizon:8d} {naive:9.4f} {gru:9.4f} {naive - gru:+9.4f}")
    print("persistence tracks the autocorrelation: worst near half a period and")
    print("better again at a full period (24 steps). A model that has learned")
    print("the period pays almost nothing for a longer horizon on a signal this")
    print("deterministic - real series lose predictability instead")
